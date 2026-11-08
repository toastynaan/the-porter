#!/usr/bin/env bash
# Stills of M8's frame (title, settings, a chapter card, the outline and the
# duty glyph, the satchel, pause, crouch, lean, a death, the chronicle and
# chapter select) to art/_review/m8/, plus a contact sheet. Opens a 960x540
# window for about half a minute (headless Godot can't render).
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/art/_review/m8"
rm -f "$OUT"/[0-9][0-9]_*.png
"$GODOT" --path "$ROOT" --windowed --resolution 960x540 res://tools/godot/m8_shots.tscn 2>&1 | grep -E 'wrote|ERROR|SCRIPT|m8 shots'
cd "$OUT"
ffmpeg -y -loglevel error -pattern_type glob -i '[0-9][0-9]_*.png' -vf "scale=640:-2,tile=4x4:padding=4" -frames:v 1 _m8_sheet.png
echo "wrote $OUT/_m8_sheet.png"
