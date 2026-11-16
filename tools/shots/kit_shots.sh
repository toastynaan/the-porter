#!/usr/bin/env bash
# The people's kit as sheets, to art/_review/kit/: every body, skin, face,
# hair cut and colour, beard, headwear and garment in
# tools/build/people_kit.py, named, in plain grey light, and the colours as
# chips. Builds the catalogue's models first (tools/build/kit_catalogue.py,
# about two minutes), then opens a 1920x1080 window (headless Godot can't
# render).
#   tools/shots/kit_shots.sh            build, then every sheet
#   tools/shots/kit_shots.sh faces      build, then only sheets whose name contains "faces"
#   NOBUILD=1 tools/shots/kit_shots.sh  render what was built last time
set -eu
BLENDER="${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}"
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
if [ -z "${NOBUILD:-}" ]; then
	"$BLENDER" -b --factory-startup --python "$ROOT/tools/build/kit_catalogue.py" 2>&1 | grep -E "^built the|Error|Traceback|^  File" || true
fi
"$GODOT" --path "$ROOT" --windowed --resolution 1920x1080 res://tools/shots/kit_shots.tscn -- ${1:+--only=$1} 2>&1 | grep -E 'wrote|ERROR|SCRIPT|kit shots'
