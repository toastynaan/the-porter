#!/usr/bin/env bash
# Stills of M13 (night 1: Bede's warning at supper, the merchant at the
# grille, Matins all present, the shape at the end of the walk, the knock
# with no one there, the merchant in the pond at dawn; night 2: Thomas at
# supper, the sailor at the grille, the death in the lane through the
# grille, Bede in the bell tower, the empty stall, the empty bed, the abbot
# at dawn; night 3: the crypt light, the killing, the figure turning, the
# book's page) to art/_review/m13/, plus a contact sheet. Opens a 960x540
# window for about a minute (headless Godot can't render).
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/art/_review/m13"
rm -f "$OUT"/[0-9][0-9]_*.png
"$GODOT" --path "$ROOT" --windowed --resolution 960x540 res://tools/godot/m13_shots.tscn 2>&1 | grep -E 'wrote|ERROR|SCRIPT|m13 shots'
cd "$OUT"
ffmpeg -y -loglevel error -pattern_type glob -i '[0-9][0-9]_*.png' -vf "scale=640:-2,tile=4x5:padding=4" -frames:v 1 _m13_sheet.png
echo "wrote $OUT/_m13_sheet.png"
