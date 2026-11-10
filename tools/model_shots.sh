#!/usr/bin/env bash
# A look at built models on their own, in plain grey daylight, from two
# sides: art/_review/models/<name>.png for each name given (the models in
# art/models/, without ".glb"). With no names, every model. Opens a window.
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [ $# -eq 0 ]; then
	set -- $(cd "$ROOT/art/models" && ls *.glb | sed 's/\.glb$//')
fi
"$GODOT" --path "$ROOT" --windowed --resolution 960x720 res://tools/godot/model_shots.tscn -- "$@" 2>&1 | grep -E 'wrote|no model|ERROR|SCRIPT'
