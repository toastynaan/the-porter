#!/usr/bin/env bash
# Renders the abbey plan view with the navmesh to art/_review/abbey/topdown.png.
# Opens a window for a few seconds (headless Godot can't render).
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
"$GODOT" --path "$ROOT" --windowed --resolution 1080x1080 res://tools/shots/topdown.tscn 2>&1 | grep -E 'wrote|ERROR|SCRIPT'
