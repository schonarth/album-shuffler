"""
Album Shuffler — YouTube Music Backend
Run: python server.py
Auth setup (one-time): bash setup.sh  →  saves browser.json
"""

import json
import random
import re
import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from ytmusicapi import YTMusic

app = Flask(__name__, static_folder="dist", static_url_path="")
CORS(app)

AUTH_FILE = os.path.join(os.path.dirname(__file__), "browser.json")

def get_ytm():
    if not os.path.exists(AUTH_FILE):
        raise FileNotFoundError("browser.json not found. Run: bash setup.sh")
    return YTMusic(AUTH_FILE)


# ─── Health / auth check ────────────────────────────────────────────────────

@app.route("/api/status")
def status():
    try:
        get_ytm()
        return jsonify({"ok": True, "auth": True})
    except FileNotFoundError:
        return jsonify({"ok": True, "auth": False, "message": "Run: bash setup.sh"}), 200
    except Exception as e:
        return jsonify({"ok": False, "auth": False, "message": str(e)}), 500


# ─── Library: all artists ────────────────────────────────────────────────────

@app.route("/api/artists")
def get_artists():
    """
    Returns all unique artists from the user's library albums.
    Cached in memory per process — refresh by restarting server.
    """
    try:
        ytm = get_ytm()
        # Fetch library albums (up to 500)
        library_albums = ytm.get_library_albums(limit=500)

        # Deduplicate by name (case-insensitive): same artist may have different
        # IDs across albums. Keep the first non-None ID seen as the canonical ID.
        artists = {}  # name_lower -> {"id": primary_id, "name": display_name}
        for album in library_albums:
            for artist in album.get("artists", []):
                aid = artist.get("id")
                aname = artist.get("name", "").strip()
                if not aname:
                    continue
                key = aname.lower()
                if key not in artists:
                    artists[key] = {"id": aid, "name": aname}
                elif artists[key]["id"] is None and aid:
                    artists[key]["id"] = aid

        result = sorted(
            [v for v in artists.values() if v["id"]],
            key=lambda x: x["name"].lower()
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Library: albums (optionally filtered by artist ids) ─────────────────────

def _thumb_urls(thumbnails):
    if not thumbnails:
        return []
    sorted_thumbs = sorted(thumbnails, key=lambda t: t.get("width", 0))
    return [t["url"] for t in sorted_thumbs]


def _sort_key(album):
    return (
        album["artists"][0].lower() if album["artists"] else "",
        album["year"] or "0",
        album["title"].lower(),
    )


@app.route("/api/albums")
def get_albums():
    """
    Returns albums, optionally filtered by comma-separated artist IDs.
    Query params:
      ?artists=id1,id2,...
      ?mode=library (default) | all
    mode=all fetches full discography for each selected artist via the artist page.
    mode=library (or no artist filter) returns saved library albums only.
    """
    try:
        ytm = get_ytm()
        artist_filter = request.args.get("artists", "")
        mode = request.args.get("mode", "library")
        artist_ids = [a for a in artist_filter.split(",") if a] if artist_filter else []

        if mode == "all" and artist_ids:
            results = []
            seen = set()
            for artist_id in artist_ids:
                try:
                    artist_data = ytm.get_artist(artist_id)
                    artist_name = artist_data.get("name", "")
                    albums_section = artist_data.get("albums", {})
                    browse_id = albums_section.get("browseId")
                    params = albums_section.get("params")
                    if browse_id and params:
                        discography = ytm.get_artist_albums(browse_id, params)
                    else:
                        discography = albums_section.get("results", [])
                    for album in discography:
                        aid = album.get("browseId", "")
                        if not aid or aid in seen:
                            continue
                        seen.add(aid)
                        results.append({
                            "id":        aid,
                            "title":     album.get("title", "Unknown Album"),
                            "artists":   [artist_name],
                            "year":      album.get("year", ""),
                            "thumbnails": _thumb_urls(album.get("thumbnails", [])),
                        })
                except Exception:
                    pass
            results.sort(key=_sort_key)
            return jsonify(results)

        # --- library mode (default) ---
        library_albums = ytm.get_library_albums(limit=500)
        artist_id_set = set(artist_ids)

        # Build name set to handle same artist with different IDs across albums
        selected_names = set()
        if artist_id_set:
            for album in library_albums:
                for artist in album.get("artists", []):
                    if artist.get("id") in artist_id_set and artist.get("name"):
                        selected_names.add(artist["name"].strip().lower())

        results = []
        for album in library_albums:
            album_artists = album.get("artists", [])
            if artist_id_set:
                ids = {a.get("id") for a in album_artists}
                names = {a.get("name", "").strip().lower() for a in album_artists}
                if not (artist_id_set.intersection(ids) or selected_names.intersection(names)):
                    continue
            results.append({
                "id":        album.get("browseId", album.get("playlistId", "")),
                "title":     album.get("title", "Unknown Album"),
                "artists":   [a.get("name", "") for a in album_artists],
                "year":      album.get("year", ""),
                "thumbnails": _thumb_urls(album.get("thumbnails", [])),
            })

        results.sort(key=_sort_key)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Create / overwrite playlist ─────────────────────────────────────────────

@app.route("/api/playlist", methods=["POST"])
def create_playlist():
    """
    Body JSON:
    {
      "name": "My Shuffled Playlist",
      "album_ids": ["browseId1", "browseId2", ...],
      "overwrite": true   // if false, always create new
    }
    Shuffles albums, fetches tracks in order, creates/overwrites playlist.
    """
    try:
        ytm = get_ytm()
        body = request.get_json()

        name      = body.get("name", "Album Shuffle").strip()
        album_ids = body.get("album_ids", [])
        overwrite = body.get("overwrite", True)

        if not album_ids:
            return jsonify({"error": "No albums selected."}), 400
        if not name:
            return jsonify({"error": "Playlist name is required."}), 400

        # Shuffle album order
        shuffled_ids = album_ids[:]
        random.shuffle(shuffled_ids)

        # Collect track IDs in album order
        track_ids = []
        album_order = []  # for UI feedback
        for album_id in shuffled_ids:
            try:
                album_data = ytm.get_album(album_id)
                title = album_data.get("title", album_id)
                tracks = album_data.get("tracks", [])
                ids = [t["videoId"] for t in tracks if t.get("videoId")]
                track_ids.extend(ids)
                album_order.append({
                    "title":  title,
                    "tracks": len(ids),
                    "artists": [a["name"] for a in album_data.get("artists", [])]
                })
            except Exception as album_err:
                # Skip unresolvable albums gracefully
                album_order.append({"title": album_id, "tracks": 0, "error": str(album_err)})

        if not track_ids:
            return jsonify({"error": "Could not retrieve any tracks from selected albums."}), 400

        playlist_id = None
        action = "created"

        # Overwrite: find existing playlist by name
        if overwrite:
            playlists = ytm.get_library_playlists(limit=500)
            for pl in playlists:
                if pl.get("title", "").strip() == name:
                    playlist_id = pl.get("playlistId")
                    break

        if playlist_id and overwrite:
            # Delete all existing items then add new ones
            existing = ytm.get_playlist(playlist_id, limit=5000)
            existing_tracks = existing.get("tracks", [])
            if existing_tracks:
                ytm.remove_playlist_items(playlist_id, existing_tracks)
            ytm.add_playlist_items(playlist_id, track_ids)
            action = "overwritten"
        else:
            # Create fresh
            playlist_id = ytm.create_playlist(
                name,
                description="Generated by Album Shuffler",
                video_ids=track_ids
            )
            action = "created"

        playlist_url = f"https://music.youtube.com/playlist?list={playlist_id}"

        return jsonify({
            "ok":          True,
            "action":      action,
            "playlist_id": playlist_id,
            "url":         playlist_url,
            "name":        name,
            "total_tracks": len(track_ids),
            "album_order": album_order,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Serve frontend ──────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("dist", "index.html")


if __name__ == "__main__":
    print("\n🎵 Album Shuffler starting on http://localhost:5001\n")
    if not os.path.exists(AUTH_FILE):
        print("⚠️  No browser.json found.")
        print("   Run this first:  bash setup.sh\n")
    app.run(debug=True, port=5001)
