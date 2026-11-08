#!/usr/bin/env bash
# Headless project check:
#   1. imports the project,
#   2. loads every script, scene and resource (tools/godot/load_all.gd),
#   3. runs every game/tests/test_*.tscn.
# GDScript warnings count as errors for the length of the check (an
# override.cfg from tools/godot/warnings_override.gd). Fails on any error or
# warning in the output, a test that doesn't print "RESULT: PASS", or a run
# that takes longer than TIMEOUT seconds.
#   tools/check.sh            everything
#   tools/check.sh ragdoll    only tests whose name contains "ragdoll"
# Set GODOT to use another binary.
set -u
GODOT="${GODOT:-/Applications/Godot_4_8.app/Contents/MacOS/Godot}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# Seconds a test may take (test_flow plays six whole nights).
TIMEOUT=900
LOG="$(mktemp -d)"
trap 'rm -rf "$LOG" "$ROOT/override.cfg"' EXIT
fail=0

# Lines that mean something went wrong.
BAD='SCRIPT ERROR|^ERROR|^WARNING|Parse Error|USER ERROR|USER WARNING'

# run <log name> <godot args...>: runs Godot headless with a time limit.
run() {
	local name="$1"
	shift
	"$GODOT" --headless --path "$ROOT" "$@" >"$LOG/$name.txt" 2>&1 &
	local pid=$!
	(sleep "$TIMEOUT" && kill "$pid" 2>/dev/null && echo "TIMEOUT after ${TIMEOUT}s" >>"$LOG/$name.txt") 2>/dev/null &
	local watchdog=$!
	wait "$pid"
	local code=$?
	# Its sleep too, or it outlives us and later kills whatever has that pid.
	pkill -P "$watchdog" 2>/dev/null
	kill "$watchdog" 2>/dev/null
	wait "$watchdog" 2>/dev/null
	return $code
}

# report <log name> <exit code> <needs RESULT: PASS (1/0)>
report() {
	local name="$1" code="$2" needs_pass="$3"
	if [ "$code" -ne 0 ] || grep -E "$BAD|TIMEOUT" "$LOG/$name.txt" >/dev/null \
		|| { [ "$needs_pass" = 1 ] && ! grep -q "RESULT: PASS" "$LOG/$name.txt"; }; then
		echo "FAIL $name (exit $code)"
		grep -E -A1 "$BAD|TIMEOUT|  FAIL|RESULT" "$LOG/$name.txt" | head -40
		fail=1
	else
		local n
		n=$(grep -c '  ok ' "$LOG/$name.txt")
		if [ "$n" -gt 0 ]; then echo "ok   $name ($n checks)"; else echo "ok   $name"; fi
	fi
}

rm -f "$ROOT/override.cfg"
run import --import
report import $? 0

run override --script res://tools/godot/warnings_override.gd
sed -n '/^--- override.cfg/,$p' "$LOG/override.txt" | tail -n +2 >"$ROOT/override.cfg"
if ! grep -q 'gdscript/warnings/unused_variable=2' "$ROOT/override.cfg"; then
	echo "FAIL could not write override.cfg"
	exit 1
fi

if [ $# -eq 0 ]; then
	run load_all res://tools/godot/load_all.tscn
	report load_all $? 1
fi

for scene in "$ROOT"/game/tests/test_*.tscn; do
	name="$(basename "$scene" .tscn)"
	if [ $# -gt 0 ] && [[ "$name" != *"$1"* ]]; then
		continue
	fi
	run "$name" --fixed-fps 120 "res://game/tests/$name.tscn"
	report "$name" $? 1
done
exit $fail
