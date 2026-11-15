#!/usr/bin/env bash
# Stills inside the Cross Keys on night 0 at 20:00, the clock stopped, for
# its look: to art/_review/inn/, plus a contact sheet. Opens a 1920x1080
# window (headless Godot can't render).
#   tools/shots/inn_shots.sh          every still
#   tools/shots/inn_shots.sh loft     only stills whose name contains "loft"
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/art/_review/inn"
mkdir -p "$OUT"
if [ $# -eq 0 ]; then rm -f "$OUT"/[0-9][0-9]_*.png; fi
"$GODOT" --path "$ROOT" --windowed --resolution 1920x1080 res://tools/shots/inn_shots.tscn -- ${1:+--only=$1} 2>&1 | grep -E 'wrote|ERROR|SCRIPT|inn shots|people'
cd "$OUT"
ffmpeg -y -loglevel error -pattern_type glob -i '[0-9][0-9]_*.png' -vf "scale=640:-2,tile=3x5:padding=4" -frames:v 1 _inn_sheet.png
echo "wrote $OUT/_inn_sheet.png"
