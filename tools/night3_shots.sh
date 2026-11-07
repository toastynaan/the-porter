#!/usr/bin/env bash
# Plays night 3 with the test pilot and captures a still at each beat to
# art/_review/m4/NN_<beat>.png, plus a contact sheet, _night3_sheet.png.
# Opens a 960x540 window for about two minutes (headless Godot can't render).
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/art/_review/m4"
rm -f "$OUT"/[0-9][0-9]_*.png
"$GODOT" --path "$ROOT" --windowed --resolution 960x540 res://tools/godot/night3_shots.tscn 2>&1 | grep -E 'wrote|ERROR|SCRIPT|pilot:|night 3 shots'
cd "$OUT"
ffmpeg -y -loglevel error -pattern_type glob -i '[0-9][0-9]_*.png' -vf "scale=640:-2,tile=3x4:padding=4" -frames:v 1 _night3_sheet.png
echo "wrote $OUT/_night3_sheet.png"
