#!/usr/bin/env bash
# Stills of the road in (night 0), for its look: the wagon stood at set
# places along the road at set hours, to art/_review/intro/, plus a contact
# sheet. Opens a 1920x1080 window (headless Godot can't render).
#   tools/intro_shots.sh            every still
#   tools/intro_shots.sh chapel     only stills whose name contains "chapel"
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/art/_review/intro"
mkdir -p "$OUT"
if [ $# -eq 0 ]; then rm -f "$OUT"/[0-9][0-9]_*.png; fi
"$GODOT" --path "$ROOT" --windowed --resolution 1920x1080 res://tools/godot/intro_shots.tscn -- ${1:+--only=$1} 2>&1 | grep -E 'wrote|ERROR|SCRIPT|intro shots'
cd "$OUT"
ffmpeg -y -loglevel error -pattern_type glob -i '[0-9][0-9]_*.png' -vf "scale=640:-2,tile=5x6:padding=4" -frames:v 1 _intro_sheet.png
echo "wrote $OUT/_intro_sheet.png"
