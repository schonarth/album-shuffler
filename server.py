"""
Album Shuffler — YouTube Music Backend
Run: python server.py
Auth setup (one-time): ytmusicapi oauth  →  saves oauth.json
"""

import json
import random
import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from ytmusicapi import YTMusic

app = Flask(__name__, static_folder="static")
CORS(app)

AUTH_FILE = os.path.join(os.path.dirname(__file__), "oauth.json")

def get_ytm():
    if not os.path.exists(AUTH_FILE):
        raise FileNotFoundError(
            "oauth.json not found. Run: ytmusicapi oauth"
        )
    return YTMusic(AUTH_FILE)


# ─── Health / auth check ────────────────────────────────────────────────────

@app.route("/api/status")
def status():
    try:
        get_ytm()
        return jsonify({"ok": True, "auth": True})
    except FileNotFoundError:
        return jsonify({"ok": True, "auth": False, "message": "Run: ytmusicapi oauth"}), 200
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

        artists = {}
        for album in library_albums:
            for artist in album.get("artists", []):
                aid = artist.get("id")
                aname = artist.get("name", "").strip()
                if aid and aname and aid not in artists:
                    artists[aid] = aname

        result = sorted(
            [{"id": k, "name": v} for k, v in artists.items()],
            key=lambda x: x["name"].lower()
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Library: albums (optionally filtered by artist ids) ─────────────────────

@app.route("/api/albums")
def get_albums():
    """
    Returns library albums, optionally filtered by comma-separated artist IDs.
    Query param: ?artists=id1,id2,...
    """
    try:
        ytm = get_ytm()
        artist_filter = request.args.get("artists", "")
        artist_ids = set(artist_filter.split(",")) if artist_filter else set()

        library_albums = ytm.get_library_albums(limit=500)

        results = []
        for album in library_albums:
            album_artists = album.get("artists", [])
            album_artist_ids = {a.get("id") for a in album_artists}

            # If filtering, skip albums that don't match any selected artist
            if artist_ids and not artist_ids.intersection(album_artist_ids):
                continue

            # Thumbnail: pick the largest available
            thumbnails = album.get("thumbnails", [])
            thumb = thumbnails[-1]["url"] if thumbnails else ""

            results.append({
                "id":        album.get("browseId", album.get("playlistId", "")),
                "title":     album.get("title", "Unknown Album"),
                "artists":   [a.get("name", "") for a in album_artists],
                "year":      album.get("year", ""),
                "thumbnail": thumb,
            })

        # Sort by artist then year then title
        results.sort(key=lambda x: (
            x["artists"][0].lower() if x["artists"] else "",
            x["year"] or "0",
            x["title"].lower()
        ))
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
    return send_from_directory("static", "index.html")


if __name__ == "__main__":
    print("\n🎵 Album Shuffler starting on http://localhost:5000\n")
    if not os.path.exists(AUTH_FILE):
        print("⚠️  No oauth.json found.")
        print("   Run this first:  ytmusicapi oauth\n")
    app.run(debug=True, port=5000)
