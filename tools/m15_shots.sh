#!/usr/bin/env bash
# Stills of M15 (night 6: Anselm in his bed, Thomas's wine, the cult in
# costume, Roger at the grille, the proof in the crypt passage, the rite in
# the crypt, the Hungry Saint, Dunstan taken, fire in the granary, the demon
# with a light; and a chronicle) to art/_review/m15/, plus a contact sheet.
# Opens a 960x540 window for about a minute (headless Godot can't render).
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/art/_review/m15"
rm -f "$OUT"/[0-9][0-9]_*.png
"$GODOT" --path "$ROOT" --windowed --resolution 960x540 res://tools/godot/m15_shots.tscn 2>&1 | grep -E 'wrote|ERROR|SCRIPT|m15 shots'
cd "$OUT"
ffmpeg -y -loglevel error -pattern_type glob -i '[0-9][0-9]_*.png' -vf "scale=640:-2,tile=4x4:padding=4" -frames:v 1 _m15_sheet.png
echo "wrote $OUT/_m15_sheet.png"
