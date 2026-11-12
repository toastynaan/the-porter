#!/usr/bin/env bash
# Stills of the reworked ride in (night 0: talking to the traveller, the body
# cart going by, the warden at Aldgate and his lantern, the woman in the
# doorway, the lane, the wagon driving off) to art/_review/ride/, plus a contact sheet. Opens a
# 960x540 window for about two and a half minutes (headless Godot can't
# render).
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/art/_review/ride"
rm -f "$OUT"/[0-9][0-9]_*.png
"$GODOT" --path "$ROOT" --windowed --resolution 960x540 res://tools/shots/ride_shots.tscn 2>&1 | grep -E 'wrote|ERROR|SCRIPT|ride shots'
cd "$OUT"
ffmpeg -y -loglevel error -pattern_type glob -i '[0-9][0-9]_*.png' -vf "scale=640:-2,tile=4x2:padding=4" -frames:v 1 _ride_sheet.png
echo "wrote $OUT/_ride_sheet.png"
