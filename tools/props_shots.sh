#!/usr/bin/env bash
# Stills of the abbey's props where they stand (night 3, at dusk and after
# dark), to art/_review/props_GROUP/, plus a contact sheet. GROUP names a
# list of stills, tools/godot/props_shots_GROUP.gd. Opens a 1920x1080 window
# (headless Godot can't render).
#   tools/props_shots.sh court          every still of the group
#   tools/props_shots.sh court cell     only stills whose name contains "cell"
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GROUP="${1:?usage: tools/props_shots.sh GROUP [filter]}"
OUT="$ROOT/art/_review/props_$GROUP"
mkdir -p "$OUT"
if [ $# -eq 1 ]; then rm -f "$OUT"/[0-9][0-9]_*.png; fi
"$GODOT" --path "$ROOT" --windowed --resolution 1920x1080 res://tools/godot/props_shots.tscn -- --group="$GROUP" ${2:+--only=$2} 2>&1 | grep -E 'wrote|ERROR|SCRIPT|props shots'
cd "$OUT"
ffmpeg -y -loglevel error -pattern_type glob -i '[0-9][0-9]_*.png' -vf "scale=640:-2,tile=6x6:padding=4" -frames:v 1 _sheet.png
echo "wrote $OUT/_sheet.png"
