#!/usr/bin/env bash
# Stills of the crypt and the passages (night 3, at dusk and after
# dark), for its look: to art/_review/crypt/, plus a contact sheet. Opens a
# 1920x1080 window (headless Godot can't render).
#   tools/crypt_shots.sh          every still
#   tools/crypt_shots.sh arch     only stills whose name contains "arch"
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/art/_review/crypt"
mkdir -p "$OUT"
if [ $# -eq 0 ]; then rm -f "$OUT"/[0-9][0-9]_*.png; fi
"$GODOT" --path "$ROOT" --windowed --resolution 1920x1080 res://tools/godot/crypt_shots.tscn -- ${1:+--only=$1} 2>&1 | grep -E 'wrote|ERROR|SCRIPT|crypt shots'
cd "$OUT"
ffmpeg -y -loglevel error -pattern_type glob -i '[0-9][0-9]_*.png' -vf "scale=640:-2,tile=9x8:padding=4" -frames:v 1 _crypt_sheet.png
echo "wrote $OUT/_crypt_sheet.png"
