#!/usr/bin/env bash
# Album Shuffler — one-time setup
set -e

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

# Check for existing auth
if [ -f "oauth.json" ]; then
  echo "✅ Found existing oauth.json — you're already authenticated."
  echo ""
else
  echo "🔐 Google authentication required."
  echo "   This will open a browser for you to log in with your Google account."
  echo "   (The credentials are stored locally in oauth.json)"
  echo ""
  read -p "   Press Enter to start authentication…"
  ytmusicapi oauth
  echo ""
fi

echo "🚀 Setup complete! Run the app with:"
echo ""
echo "   python3 server.py"
echo ""
echo "   Then open: http://localhost:5000"
echo ""
