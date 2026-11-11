#!/usr/bin/env bash
# Stills of the church (night 3, at dusk and after
# dark), for its look: to art/_review/church/, plus a contact sheet. Opens a
# 1920x1080 window (headless Godot can't render).
#   tools/church_shots.sh          every still
#   tools/church_shots.sh arch     only stills whose name contains "arch"
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/art/_review/church"
mkdir -p "$OUT"
if [ $# -eq 0 ]; then rm -f "$OUT"/[0-9][0-9]_*.png; fi
"$GODOT" --path "$ROOT" --windowed --resolution 1920x1080 res://tools/godot/church_shots.tscn -- ${1:+--only=$1} 2>&1 | grep -E 'wrote|ERROR|SCRIPT|church shots'
cd "$OUT"
ffmpeg -y -loglevel error -pattern_type glob -i '[0-9][0-9]_*.png' -vf "scale=640:-2,tile=9x8:padding=4" -frames:v 1 _church_sheet.png
echo "wrote $OUT/_church_sheet.png"
