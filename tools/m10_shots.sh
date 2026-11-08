#!/usr/bin/env bash
# Stills of M10 (one view at Dose 0, 25, 50, 75 and 100; a shape at the edge
# of view, a face in the grain, the dead in the choir, a fake death, the
# HUD's lie, the candle that lights itself, the cat, a body dropping, a face
# at the grille) to art/_review/m10/, plus a contact sheet. Opens a 960x540
# window for about half a minute (headless Godot can't render).
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/art/_review/m10"
rm -f "$OUT"/[0-9][0-9]_*.png
"$GODOT" --path "$ROOT" --windowed --resolution 960x540 res://tools/godot/m10_shots.tscn 2>&1 | grep -E 'wrote|ERROR|SCRIPT|m10 shots'
cd "$OUT"
ffmpeg -y -loglevel error -pattern_type glob -i '[0-9][0-9]_*.png' -vf "scale=640:-2,tile=4x4:padding=4" -frames:v 1 _m10_sheet.png
echo "wrote $OUT/_m10_sheet.png"
