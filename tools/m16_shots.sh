#!/usr/bin/env bash
# Stills of M16, the full pass: the chronicle page each of the seven endings
# closes with, to art/_review/m16/, plus a contact sheet. Opens a 960x540
# window for a few seconds (headless Godot can't render).
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/art/_review/m16"
rm -f "$OUT"/[0-9][0-9]_*.png
"$GODOT" --path "$ROOT" --windowed --resolution 960x540 res://tools/godot/m16_shots.tscn 2>&1 | grep -E 'wrote|ERROR|SCRIPT|m16 shots'
cd "$OUT"
ffmpeg -y -loglevel error -pattern_type glob -i '[0-9][0-9]_*.png' -vf "scale=640:-2,tile=4x2:padding=4" -frames:v 1 _m16_sheet.png
echo "wrote $OUT/_m16_sheet.png"
