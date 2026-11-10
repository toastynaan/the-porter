#!/usr/bin/env bash
# A short film of the start of the road in (night 0), as it plays, to
# art/_review/intro/intro.mp4: about three quarters of a minute at 30 frames a second,
# 1920x1080, with the game's sound. Opens a window while it records (Godot's
# movie writer; needs ffmpeg to make the mp4).
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/art/_review/intro"
mkdir -p "$OUT"
rm -f "$OUT/intro.avi"
"$GODOT" --path "$ROOT" --windowed --resolution 1920x1080 --write-movie "$OUT/intro.avi" --fixed-fps 30 res://tools/godot/intro_film.tscn 2>&1 | grep -E 'ERROR|SCRIPT' || true
ffmpeg -y -loglevel error -i "$OUT/intro.avi" -c:v libx264 -pix_fmt yuv420p -crf 23 -c:a aac "$OUT/intro.mp4"
rm -f "$OUT/intro.avi"
echo "wrote $OUT/intro.mp4"
