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

Authentication works by copying your browser session from YouTube Music — no Google Cloud project or API keys required. `setup.sh` walks you through it step by step.

Credentials are stored in `browser.json` in the project folder. **Do not share this file.** It is listed in `.gitignore`.

Sessions eventually expire (when your browser session does). Re-run `bash setup.sh` to refresh — it overwrites the existing credentials automatically.

> **Future improvement**: session refresh could be automated (detected on API error, re-prompted without manual intervention).

## Notes

- **First load is slow** — the app fetches your full library (up to 500 albums) on startup.
- **Playlist generation** fetches track lists for each selected album individually; with many albums this may take 10–30 seconds.
- The server must be running while you use the UI. Stop it with `Ctrl+C`.
