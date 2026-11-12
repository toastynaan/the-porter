#!/usr/bin/env bash
# Night 0's last scene, the killing seen from the window, as a film:
# art/_review/night0/window.mp4 (1280x720, 30 fps). Opens a window while it records.
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/art/_review/night0"
mkdir -p "$OUT"
rm -f "$OUT/window.avi"
"$GODOT" --path "$ROOT" --windowed --resolution 1280x720 --write-movie "$OUT/window.avi" --fixed-fps 30 res://tools/shots/window_film.tscn 2>&1 | grep -E 'ERROR|SCRIPT' || true
ffmpeg -y -loglevel error -i "$OUT/window.avi" -c:v libx264 -pix_fmt yuv420p -crf 23 -an "$OUT/window.mp4"
rm -f "$OUT/window.avi"
echo "wrote $OUT/window.mp4"
