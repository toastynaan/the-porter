#!/usr/bin/env bash
# Builds the game's models from their scripts (Look and Feel, "Asset
# pipeline": every asset is built by a script).
#   tools/build.sh                 every tools/build/env_*.py, prop_*.py, chr_*.py
#   tools/build.sh prop_wagon      one of them (several names can be given)
# Each script runs in Blender and writes art/models/<name>.glb. Then Godot
# imports what changed, tools/build/link_imports.py links the models'
# materials to the game's own (game/world/materials/real/) and sets the
# textures' import, and Godot imports again.
# Textures come first, once: tools/build/tex_fetch.py.
# Set BLENDER or GODOT to use other binaries. Close the Godot editor first.
set -eu
BLENDER="${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}"
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if [ $# -eq 0 ]; then
	set -- $(cd tools/build && ls env_*.py prop_*.py chr_*.py 2>/dev/null | sed 's/\.py$//')
fi
for name in "$@"; do
	"$BLENDER" -b --factory-startup --python "tools/build/$name.py" 2>&1 | grep -E "^built|Error|Traceback|^  File|error" || true
done
"$GODOT" --headless --path "$ROOT" --import 2>&1 | grep -E "^ERROR|SCRIPT ERROR" || true
python3 tools/build/link_imports.py
"$GODOT" --headless --path "$ROOT" --import 2>&1 | grep -E "^ERROR|SCRIPT ERROR" || true
