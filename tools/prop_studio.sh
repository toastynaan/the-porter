#!/usr/bin/env bash
# Stills of props standing alone, lit as the porter's lantern lights them, to
# art/_review/props/ (tools/godot/prop_studio.gd), plus a contact sheet.
# Opens a 1280x720 window (headless Godot can't render).
#   tools/prop_studio.sh                    every abbey prop
#   tools/prop_studio.sh bed,bench          only these
#   tools/prop_studio.sh bed,bench --fill   and a still under a plain lamp
#   tools/prop_studio.sh bed --back         from behind
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/art/_review/props"
mkdir -p "$OUT"
ARGS=()
for a in "$@"; do
	case "$a" in
		--*) ARGS+=("$a") ;;
		*) ARGS+=("--props=$a") ;;
	esac
done
"$GODOT" --path "$ROOT" --windowed --resolution 1280x720 res://tools/godot/prop_studio.tscn -- ${ARGS[@]+"${ARGS[@]}"} 2>&1 | grep -E 'wrote|ERROR|SCRIPT|prop studio'
cd "$OUT"
ffmpeg -y -loglevel error -pattern_type glob -i '*.png' -vf "scale=480:-2,tile=8x8:padding=4" -frames:v 1 _sheet.jpg 2>/dev/null || true
echo "wrote $OUT/_sheet.jpg"
