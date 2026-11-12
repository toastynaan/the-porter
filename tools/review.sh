#!/usr/bin/env bash
# Renders the 5 lookdev review shots at Dose 0 and 75 through the full render
# pipeline, to art/_review/<asset_id>/<shot>_dose<NN>.png. Opens a 960x540
# window for about 15 seconds (headless Godot can't render).
#   tools/review.sh                                  the baseline stage (greybox wall)
#   tools/review.sh <asset_id> res://art/env/<asset_id>.glb
# Set GODOT to use another binary.
set -eu
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ID="${1:-lookdev_baseline}"
ARGS=(--review "--asset-id=$ID")
if [ $# -ge 2 ]; then
	ARGS+=("--asset=$2")
fi
"$GODOT" --path "$ROOT" --windowed --resolution 960x540 \
	-- --level=res://game/dev/lookdev/lookdev.tscn "${ARGS[@]}"
ls "$ROOT/art/_review/$ID"
