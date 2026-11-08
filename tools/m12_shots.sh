#!/usr/bin/env bash
# Stills of M12 (night 0: the ride in, the body cart, Aldgate, the lane at
# dusk, the barred gate and Mab, the Cross Keys, drink, the room at the top,
# the curfew and Gib, peeking through a squint, the squint scare, the window;
# day 1: the morning, the sand, the tour, the nap) to art/_review/m12/, plus a
# contact sheet. Opens a 960x540 window for about two minutes (headless Godot
# can't render).
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/art/_review/m12"
rm -f "$OUT"/[0-9][0-9]_*.png
"$GODOT" --path "$ROOT" --windowed --resolution 960x540 res://tools/godot/m12_shots.tscn 2>&1 | grep -E 'wrote|ERROR|SCRIPT|m12 shots'
cd "$OUT"
ffmpeg -y -loglevel error -pattern_type glob -i '[0-9][0-9]_*.png' -vf "scale=640:-2,tile=4x5:padding=4" -frames:v 1 _m12_sheet.png
echo "wrote $OUT/_m12_sheet.png"
