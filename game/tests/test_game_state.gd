extends Node
## GameState checks: Dose eases in without steps, stacks, caps and decays with
## the clock; Suspicion only rises; a bell save restores the night.
## Run: tools/check.sh

const TEST_SAVE := "user://test_bell_save.tres"

var _fails := 0


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	GameState.save_path = TEST_SAVE

	# One dose eases in over its time, in many small changes.
	GameState.snap_dose(0.0)
	var seen: Array[float] = []
	var on_change := func(d: float) -> void: seen.append(d)
	GameState.dose_changed.connect(on_change)
	GameState.add_dose(25.0, 1.0)
	await _seconds(1.3)
	GameState.dose_changed.disconnect(on_change)
	_check(is_equal_approx(GameState.dose, 25.0), "dose eases to 25 (%.3f)" % GameState.dose)
	var biggest := 0.0
	var prev := 0.0
	for d in seen:
		biggest = maxf(biggest, absf(d - prev))
		prev = d
	_check(seen.size() > 30 and biggest < 2.0, "no steps: %d changes, biggest %.2f" % [seen.size(), biggest])

	# Overlapping doses add up and Dose caps at 100.
	GameState.add_dose(40.0, 0.5)
	GameState.add_dose(50.0, 0.8)
	await _seconds(1.0)
	_check(GameState.dose == 100.0, "doses stack and cap at 100 (%.2f)" % GameState.dose)

	# Decay: about 10 per in-game hour while the clock runs.
	GameState.snap_dose(50.0)
	GameState.seconds_per_hour = 1.0
	await _seconds(1.0)
	GameState.seconds_per_hour = 0.0
	_check(absf(GameState.dose - 40.0) < 0.5, "decays 10 per in-game hour (%.2f)" % GameState.dose)

	# Suspicion only goes up, to 100 at most.
	GameState.raise_suspicion(15)
	GameState.raise_suspicion(-10)
	_check(GameState.suspicion == 15, "suspicion ignores decreases (%d)" % GameState.suspicion)
	GameState.raise_suspicion(200)
	_check(GameState.suspicion == 100, "suspicion caps at 100 (%d)" % GameState.suspicion)

	# A bell save restores the state it saw.
	GameState.suspicion = 20
	GameState.snap_dose(42.0)
	GameState.set_phase(GameState.Phase.MATINS)
	GameState.hour = 24.0
	GameState.captures = 1
	GameState.set_flag(&"ate_bread")
	_check(GameState.ring_bell(&"matins"), "bell writes a save")
	GameState.snap_dose(5.0)
	GameState.set_phase(GameState.Phase.ROUND)
	GameState.hour = 25.5
	GameState.captures = 2
	GameState.keys.erase(&"charnel")
	GameState.set_flag(&"ate_bread", false)
	GameState.raise_suspicion(30)
	_check(GameState.load_last_bell(), "bell save loads")
	_check(GameState.dose == 42.0 and GameState.phase == GameState.Phase.MATINS and GameState.hour == 24.0,
		"dose, phase and clock restored")
	_check(GameState.suspicion == 20 and GameState.get_flag(&"ate_bread") == true and GameState.keys.has(&"charnel"),
		"suspicion, keys and flags restored")
	_check(GameState.captures == 2, "a reload never undoes a capture (%d)" % GameState.captures)
	_check(GameState.last_bell == &"matins", "remembers the last bell")
	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))

	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


func _seconds(s: float) -> void:
	await get_tree().create_timer(s).timeout


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
