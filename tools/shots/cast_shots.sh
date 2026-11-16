#!/usr/bin/env bash
# Night 0's real people (the traveller, the carter, the warden) to
# art/_review/cast_night0/: side by side, every mood and tell close up by the
# porter's lantern, the warden's lantern raised, the two on the wagon seated,
# the carter walking. Once at 1920x1080 and once at the game's 960x540
# (files ending "_game"). Names (traveller carter warden) take only those.
# Opens a window for a minute or two (headless Godot can't render).
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
for res in 1920x1080 960x540; do
	"$GODOT" --path "$ROOT" --windowed --resolution "$res" res://tools/shots/cast_shots.tscn -- "$@" 2>&1 | grep -E 'wrote|ERROR|SCRIPT|done'
done
