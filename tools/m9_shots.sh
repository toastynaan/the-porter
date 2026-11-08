#!/usr/bin/env bash
# Stills of M9 (the three styles of death, sober and drugged, a hallucination,
# the crypt candles, a found body, a hidden one, the book page and the
# ledger notes) to art/_review/m9/, plus a contact sheet. Opens a 960x540
# window for about half a minute (headless Godot can't render).
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/art/_review/m9"
rm -f "$OUT"/[0-9][0-9]_*.png
"$GODOT" --path "$ROOT" --windowed --resolution 960x540 res://tools/godot/m9_shots.tscn 2>&1 | grep -E 'wrote|ERROR|SCRIPT|m9 shots'
cd "$OUT"
ffmpeg -y -loglevel error -pattern_type glob -i '[0-9][0-9]_*.png' -vf "scale=640:-2,tile=4x4:padding=4" -frames:v 1 _m9_sheet.png
echo "wrote $OUT/_m9_sheet.png"
