#!/usr/bin/env bash
# Stills of M14 (night 4: Edwin's whisper, Mab at the grille, Wulfric in the
# fog, the prior kneeling, the guest in the guesthouse, Edwin in the charnel
# house, two hunters, Osric's face, Simon scrubbing, the snapped clock;
# night 5: the chapter house, Simon's throat, the sergeant at the grille,
# Anselm at Matins, the grain, the hunter in the barred granary, the arrest)
# to art/_review/m14/, plus a contact sheet. Opens a 960x540 window for
# about a minute (headless Godot can't render).
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/art/_review/m14"
rm -f "$OUT"/[0-9][0-9]_*.png
"$GODOT" --path "$ROOT" --windowed --resolution 960x540 res://tools/godot/m14_shots.tscn 2>&1 | grep -E 'wrote|ERROR|SCRIPT|m14 shots'
cd "$OUT"
ffmpeg -y -loglevel error -pattern_type glob -i '[0-9][0-9]_*.png' -vf "scale=640:-2,tile=4x5:padding=4" -frames:v 1 _m14_sheet.png
echo "wrote $OUT/_m14_sheet.png"
