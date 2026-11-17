#!/usr/bin/env bash
# People side by side, named, in plain grey light, from in front and turned,
# to art/_review/people/<sheet>.png: the character scenes as the game has
# them. Opens a 1920x1080 window (headless Godot can't render).
#   tools/shots/people_shots.sh lane hob,agnes,kit,gib     a sheet "lane" of those
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
"$GODOT" --path "$ROOT" --windowed --resolution 1920x1080 res://tools/shots/people_shots.tscn -- --as="$1" "$2" 2>&1 | grep -E 'wrote|ERROR|SCRIPT|people shots'
