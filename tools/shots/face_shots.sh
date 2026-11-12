#!/usr/bin/env bash
# The placeholder faces (docs/systems/faces.md) to art/_review/faces/: every
# mood, each tell, Anselm's blind eyes, and a face by lantern light in the
# dark. Opens a window for a few seconds (headless Godot can't render).
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
rm -f "$ROOT"/art/_review/faces/[0-9][0-9]_*.png
"$GODOT" --path "$ROOT" --windowed --resolution 1280x720 res://tools/shots/face_shots.tscn 2>&1 | grep -E 'wrote|ERROR|SCRIPT|done'
