#!/usr/bin/env bash
# run.sh — serve hedit over localhost (reliable autosave, strings.svg boot,
# in-place Ctrl+S saving) and open it in the browser. Ctrl+C stops the server.
cd "$(dirname "$0")"
PORT="${1:-8000}"
URL="http://localhost:$PORT/hedit.html"
( sleep 1; xdg-open "$URL" 2>/dev/null || explorer.exe "$URL" 2>/dev/null ) &
echo "hedit -> $URL   (Ctrl+C to stop)"
python3 -m http.server "$PORT"
