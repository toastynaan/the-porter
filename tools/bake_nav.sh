#!/usr/bin/env bash
# Rebakes the abbey navmesh (game/world/abbey/abbey_nav.res) after layout edits.
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$GODOT" --headless --path "$ROOT" res://tools/godot/bake_nav.tscn 2>&1 | grep -E 'baked|ERROR|SCRIPT'
