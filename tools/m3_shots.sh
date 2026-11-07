#!/usr/bin/env bash
# Captures M3 review stills (hiding views, the demon by Dose, staring) to
# art/_review/m3/*.png and a contact sheet, _m3_sheet.png. Opens a 960x540
# window for about 20 seconds (headless Godot can't render).
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/art/_review/m3"
"$GODOT" --path "$ROOT" --windowed --resolution 960x540 res://tools/godot/m3_shots.tscn 2>&1 | grep -E 'wrote|ERROR|SCRIPT'
cd "$OUT"
ffmpeg -y -loglevel error -i hide_oven.png -i hide_under_cot.png -i hide_altar_cloth.png -i hide_open_tomb.png \
	-i hide_under_bed_w_23.png -i hide_bone_pile.png -i demon_dose_0.png -i demon_dose_60.png -i demon_dose_90.png \
	-filter_complex "[0][1][2]hstack=3[a];[3][4][5]hstack=3[b];[6][7][8]hstack=3[c];[a][b][c]vstack=3" _m3_sheet.png
echo "wrote $OUT/_m3_sheet.png"
