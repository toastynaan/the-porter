#!/usr/bin/env bash
# Renders the street outside the west gate: a plan and five views, to
# art/_review/street/, plus a contact sheet. Opens a window for ~20 s.
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/art/_review/street"
"$GODOT" --path "$ROOT" --windowed --resolution 960x540 res://tools/godot/street_shots.tscn 2>&1 | grep -E 'wrote|ERROR|SCRIPT'
cd "$OUT"
ffmpeg -y -loglevel error -i lane_to_gate.png -i lane_north.png -i through_the_gate.png -i over_the_wall.png \
	-filter_complex "[0][1]hstack[a];[2][3]hstack[b];[a][b]vstack" _views_sheet.png
echo "wrote $OUT/_views_sheet.png"
