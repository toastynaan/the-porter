#!/usr/bin/env bash
# Stills of M11 (rain, fog and snow; two hunters and a locked door at
# Suspicion 60; Osric unmasked; a thrown stone; the bell's friend; a gust;
# Osric's and Thomas's routines; the talk stopping) to art/_review/m11/, plus a contact sheet. Opens a 960x540
# window for about half a minute (headless Godot can't render).
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/art/_review/m11"
rm -f "$OUT"/[0-9][0-9]_*.png
"$GODOT" --path "$ROOT" --windowed --resolution 960x540 res://tools/godot/m11_shots.tscn 2>&1 | grep -E 'wrote|ERROR|SCRIPT|m11 shots'
cd "$OUT"
ffmpeg -y -loglevel error -pattern_type glob -i '[0-9][0-9]_*.png' -vf "scale=640:-2,tile=4x4:padding=4" -frames:v 1 _m11_sheet.png
echo "wrote $OUT/_m11_sheet.png"
