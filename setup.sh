#!/usr/bin/env bash
# Album Shuffler — one-time setup
# Usage: bash setup.sh [--skip-prompts]
set -e

SKIP_PROMPTS=0
for arg in "$@"; do [[ "$arg" == "--skip-prompts" ]] && SKIP_PROMPTS=1; done

pause() {
  if [[ $SKIP_PROMPTS -eq 0 ]]; then read -rp "$1"; fi
}

echo ""
echo "🎵 Album Shuffler Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
  echo "❌ Python 3 not found. Install it from https://python.org"
  exit 1
fi

echo "✅ Python: $(python3 --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies…"
pip3 install ytmusicapi flask flask-cors --quiet
echo "✅ Dependencies installed"
echo ""

echo "🔐 Authentication"
echo ""
echo "   Album Shuffler needs access to your YouTube Music account."
echo "   This copies your browser session — no Google Cloud setup needed."
echo ""

echo "   ┌─ Step 1 of 2 ────────────────────────────────────────────────────┐"
echo "   │  Copy request headers from YouTube Music                          │"
echo "   │                                                                   │"
echo "   │  1. Open https://music.youtube.com in your browser (signed in)    │"
echo "   │  2. Open DevTools:  Cmd+Option+I  (Mac)  or  F12  (Windows)       │"
echo "   │  3. Go to the Network tab and reload the page (Cmd+R / F5)        │"
echo "   │  4. In the filter box, type: youtubei/v1                          │"
echo "   │  5. Click any request in the list (e.g. browse)                   │"
echo "   │  6. In the right panel, click the Headers tab                     │"
echo "   │     Firefox: click Raw to show all headers including Cookie       │"
echo "   │     Chrome:  scroll to Request Headers                            │"
echo "   │  7. Select all the raw header text and copy it                    │"
echo "   └───────────────────────────────────────────────────────────────────┘"
echo ""
pause "   Press Enter when you have the headers copied… "
echo ""

echo "   ┌─ Step 2 of 2 ────────────────────────────────────────────────────┐"
echo "   │  Authenticate                                                      │"
echo "   └───────────────────────────────────────────────────────────────────┘"
echo ""

# Read headers from clipboard (macOS) or headers.txt fallback
_auth_err=$(mktemp)
if command -v pbpaste &>/dev/null; then
  echo "   Reading headers from clipboard…"
  echo ""
  _headers_tmp=$(mktemp)
  pbpaste | python3 -c "
import sys
text = sys.stdin.read().replace('\r\n', '\n').replace('\r', '\n')
lines = [l for l in text.split('\n') if l.strip()]

# Strip the decoded proto block injected by Chrome for x-client-data.
# It starts with a standalone 'Decoded:' line and ends with '}'.
cleaned = []
in_decoded = False
for line in lines:
    if line.strip() == 'Decoded:':
        in_decoded = True
        continue
    if in_decoded:
        if line.strip() == '}':
            in_decoded = False
        continue
    cleaned.append(line)
lines = cleaned

# Chrome DevTools copies HTTP/2 requests in alternating name/value lines:
#   :authority\nmusic.youtube.com\n:method\nPOST\naccept\n*/*\n...
# Detect this by the presence of HTTP/2 pseudo-headers near the top.
is_alternating = any(
    l.strip() in (':authority', ':method', ':path', ':scheme')
    for l in lines[:10]
)

if is_alternating:
    result = []
    i = 0
    while i < len(lines) - 1:
        name = lines[i].strip()
        value = lines[i + 1].strip()
        i += 2
        if not name.startswith(':'):  # skip HTTP/2 pseudo-headers
            result.append(f'{name}: {value}')
    print('\n'.join(result))
else:
    # Standard 'name: value' — strip HTTP request line if present
    if lines and lines[0].split(' ')[-1].startswith('HTTP/'):
        lines = lines[1:]
    print('\n'.join(lines))
" > "$_headers_tmp"

  ytmusicapi browser --file browser.json < "$_headers_tmp" 2>"$_auth_err"
  _rc=$?
  rm -f "$_headers_tmp"
  if [ $_rc -ne 0 ]; then
    _err=$(cat "$_auth_err"); rm -f "$_auth_err"
    echo "❌ Authentication failed."
    echo ""
    echo "   $_err"
    echo ""
    echo "   Make sure you copied the Request Headers from a youtubei/v1"
    echo "   request and that you are signed in to YouTube Music."
    exit 1
  fi
else
  echo "   No clipboard tool found. Paste your headers into headers.txt"
  echo "   in this folder, then press Enter."
  echo ""
  pause "   Press Enter when headers.txt is ready… "
  if [ ! -f "headers.txt" ]; then
    echo "❌ headers.txt not found."
    exit 1
  fi
  ytmusicapi browser --file browser.json < headers.txt 2>"$_auth_err" || {
    _err=$(cat "$_auth_err"); rm -f "$_auth_err"
    echo "❌ Authentication failed."
    echo ""
    echo "   $_err"
    exit 1
  }
  rm -f headers.txt
fi
rm -f "$_auth_err"

echo "🚀 Setup complete! Run the app with:"
echo ""
echo "   python3 server.py"
echo ""
echo "   Then open: http://localhost:5000"
echo ""
