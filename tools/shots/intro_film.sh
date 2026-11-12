#!/usr/bin/env bash
# A short film of the road in (night 0), as it plays, to art/_review/intro/:
# 1920x1080 at 30 frames a second, with the game's sound. Opens a window
# while it records (Godot's movie writer; needs ffmpeg to make the mp4).
#   tools/shots/intro_film.sh          intro.mp4: the start, three quarters of a minute
#   tools/shots/intro_film.sh gate     gate.mp4: the wall, Aldgate and the street inside, a minute
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/art/_review/intro"
NAME="intro"
PART=""
if [ "${1:-}" = "gate" ]; then NAME="gate"; PART="--part=gate"; fi
mkdir -p "$OUT"
rm -f "$OUT/$NAME.avi"
"$GODOT" --path "$ROOT" --windowed --resolution 1920x1080 --write-movie "$OUT/$NAME.avi" --fixed-fps 30 res://tools/shots/intro_film.tscn -- $PART 2>&1 | grep -E 'ERROR|SCRIPT' || true
ffmpeg -y -loglevel error -i "$OUT/$NAME.avi" -c:v libx264 -pix_fmt yuv420p -crf 23 -c:a aac "$OUT/$NAME.mp4"
rm -f "$OUT/$NAME.avi"
echo "wrote $OUT/$NAME.mp4"
