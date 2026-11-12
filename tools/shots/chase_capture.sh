#!/usr/bin/env bash
# Records the scripted chase takes in the greybox (tools/shots/chase_capture.gd)
# to art/_review/m3/chase_<take>.mp4, each with a contact sheet of frames
# (chase_<take>_sheet.png, one a second). Opens a 960x540 window for about
# half a minute a take (headless Godot can't render).
#   tools/shots/chase_capture.sh            both takes
#   tools/shots/chase_capture.sh escape     one
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/art/_review/m3"
mkdir -p "$OUT"
for take in ${1:-caught escape}; do
	"$GODOT" --path "$ROOT" --windowed --resolution 960x540 --fixed-fps 30 --write-movie "$OUT/chase_$take.avi" \
		res://tools/shots/chase_capture.tscn -- --take="$take" 2>&1 | grep -E 'CHASE|ERROR|SCRIPT' || true
	ffmpeg -y -loglevel error -i "$OUT/chase_$take.avi" -vf "scale=960:-2:flags=neighbor" -c:v libx264 -pix_fmt yuv420p \
		-crf 18 -c:a aac -b:a 160k "$OUT/chase_$take.mp4"
	ffmpeg -y -loglevel error -i "$OUT/chase_$take.mp4" -vf "fps=1,scale=480:-2,tile=5x8" -frames:v 1 "$OUT/chase_${take}_sheet.png"
	rm -f "$OUT/chase_$take.avi"
	echo "wrote $OUT/chase_$take.mp4"
done
