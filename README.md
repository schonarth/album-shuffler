# 🎵 Album Shuffler

Plays your YouTube Music library album-by-album — each album start-to-finish, but albums chosen in random order. Generates a YouTube Music playlist you can play straight through.

## Quick Start

```bash
# 1. Clone / download this folder, then:
cd album-shuffler

# 2. Run setup (installs deps + authenticates with Google)
bash setup.sh

# 3. Start the server
python3 server.py

# 4. Open your browser
open http://localhost:5000
```

## How to use

1. **Artists panel** (left, top) — browse or search your library's artists. Click to filter albums by that artist. Multiple artists can be selected.
2. **Albums panel** (left, bottom) — all matching albums shown as cards with cover art. Click any album to toggle selection. Use the album search box to narrow further.
3. **Playlist panel** (right) — name your playlist, configure overwrite behavior, hit **SHUFFLE & CREATE**.
4. The app shuffles your selected albums, fetches all tracks in album order, and creates (or overwrites) the playlist in your YouTube Music account.
5. Click **OPEN IN YT MUSIC** to play it immediately.

## Settings

| Setting | Description |
|---|---|
| **Overwrite existing** | If a playlist with the same name exists, replace it instead of creating a duplicate |
| **Confirm before overwrite** | Show a confirmation dialog before replacing |

## Requirements

- Python 3.8+
- A YouTube Music account with saved albums
- Packages: `ytmusicapi`, `flask`, `flask-cors`

## Authentication

Authentication uses OAuth and is stored in `oauth.json` in the project folder. This file contains your Google credentials — **do not share it**. It is listed in `.gitignore` by default.

To re-authenticate: delete `oauth.json` and run `ytmusicapi oauth`.

## Notes

- **First load is slow** — the app fetches your full library (up to 500 albums) on startup.
- **Playlist generation** fetches track lists for each selected album individually; with many albums this may take 10–30 seconds.
- The server must be running while you use the UI. Stop it with `Ctrl+C`.
