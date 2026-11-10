#!/usr/bin/env bash
# Stills of talking (Brother Thomas at dusk on night 3: narration, a line,
# the answers, the arrows, the porter's own line, an aside, the large size
# with the dark band, walking away; Walter at the grille: the greeting and
# the question, the answer, what to do with him, a thing noticed; a beat's
# choice) to art/_review/talk/, plus a contact sheet, and two strips of
# frames (strip_*.png: the answers coming up, the porter answering). Driven
# by the real keys. Opens a 1920x1080 window for about a minute (headless Godot can't
# render), so the type is the size the player sees.
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/art/_review/talk"
mkdir -p "$OUT"
rm -f "$OUT"/[0-9][0-9]_*.png "$OUT"/strip_*.png
"$GODOT" --path "$ROOT" --windowed --resolution 1920x1080 res://tools/godot/talk_shots.tscn 2>&1 | grep -E 'wrote|ERROR|SCRIPT|talk shots'
cd "$OUT"
ffmpeg -y -loglevel error -pattern_type glob -i '[0-9][0-9]_*.png' -vf "crop=iw*0.7:ih*0.5:iw*0.15:ih*0.5,scale=672:-2,tile=3x6:padding=4" -frames:v 1 _talk_sheet.png
echo "wrote $OUT/_talk_sheet.png"
