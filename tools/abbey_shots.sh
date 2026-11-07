#!/usr/bin/env bash
# Captures in-game views of the abbey to art/_review/abbey/view_*.png.
# Opens a 960x540 window for about 20 seconds (headless Godot can't render).
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$GODOT" --path "$ROOT" --windowed --resolution 960x540 res://tools/godot/abbey_shots.tscn 2>&1 | grep -E 'wrote|ERROR|SCRIPT'
