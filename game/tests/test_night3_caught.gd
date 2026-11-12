extends Node
## Getting caught on night 3 (main.tscn and night3.tscn; docs/systems/mechanics.md,
## "Being hunted"). Starting from the Matins bell, the night picks up in the
## choir. Through the round, the night saves quietly just before the crypt.
## Caught in the chase, the porter dies (from night 3 the first capture
## kills) and the night goes back to that quiet save, not to the bell: the
## round stays done, Dose and all as it was at the crypt. Caught again, the
## same. Continue from the title would still start at the Matins bell.
## Run: tools/check.sh

const TEST_SAVE := "user://test_night3_caught_save.tres"
const MATINS_DOSE := 30.0

var _fails := 0
var _main: Node
var _pilot: NightPilot


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	NightPilot.fresh_night(TEST_SAVE)
	# As if the night had come as far as the Matins bell.
	GameState.set_flag(&"night_started")
	GameState.set_flag(&"gate_taken")
	GameState.set_flag(&"gate_barred")
	GameState.set_flag(&"n3_ate_bread")
	GameState.hour = 24.0
	GameState.snap_dose(MATINS_DOSE)
	GameState.set_phase(GameState.Phase.MATINS)
	GameState.ring_bell(&"matins")
	Talk.line_seconds = 0.05
	Talk.auto_choice = func(_options: PackedStringArray) -> int: return 0
	_main = NightPilot.main_with("res://game/chapters/night3/night3.tscn")
	add_child(_main)
	await _start_pilot()
	var p := _pilot.player
	_check(_pilot.director().beats_run == [&"Choir"], "a night saved at Matins picks up in the choir")
	_check(p.global_position.distance_to(_pilot.mark("matins")) < 0.5, "the porter is at the Matins spawn")
	var bar: Node3D = _pilot.night.get_node(^"Abbey/Navigation/OuterCourt/Props/GateBar")
	var gate: AbbeyGate = _pilot.night.get_node(^"AbbeyGate")
	_check(bar.visible and not gate.is_open() and absf(GameState.hour - 24.0) < 0.01, "the gate is still shut and barred, at midnight")

	# Through the round to the crypt: a quiet save just before it.
	await _pilot.count_brothers()
	await _pilot.walk_round()
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Crypt", 5.0)
	_check(GameState.has_quiet_save() and GameState.has_flag(&"n3_round"), "the night saves quietly before the crypt")
	var crypt_dose := GameState.dose

	# Caught in the chase: on night 3 the first capture kills.
	var flow: CaptureFlow = _main.get_node(^"CaptureFlow")
	var died := [0]
	flow.died.connect(func() -> void: died[0] += 1)
	var level := _level_id()
	await _pilot.go_down_to_crypt()
	await _pilot.until(func() -> bool: return _level_id() != level and not flow.busy, 30.0)
	_check(died[0] == 1 and GameState.captures == 1 and not GameState.has_flag(&"woke_in_infirmary"),
		"caught on night 3: the first capture kills, no infirmary")
	_check(flow.last_cause == &"cord", "a cord from behind (%s)" % flow.last_cause)
	await _start_pilot()
	_check(_pilot.director().beats_run == [&"Crypt"] and _pilot.player.global_position.distance_to(_pilot.mark("crypt")) < 0.5,
		"back at the quiet save before the crypt, not the Matins bell (%s)" % [_pilot.director().beats_run])
	_check(GameState.has_flag(&"n3_round") and GameState.has_flag(&"n3_headcount") and absf(GameState.dose - crypt_dose) < 1.0,
		"with the night as it was there: the round done, Dose %.1f" % GameState.dose)

	# Caught again: the same quiet save.
	level = _level_id()
	await _pilot.go_down_to_crypt()
	await _pilot.until(func() -> bool: return _level_id() != level and not flow.busy, 30.0)
	await _start_pilot()
	_check(died[0] == 2 and _pilot.director().beats_run == [&"Crypt"], "caught again: back before the crypt again")

	# Continue loads the bell, not the quiet save.
	_check(GameState.load_last_bell() and GameState.last_bell == &"matins", "Continue would start at the Matins bell")
	_main.call(&"reload_level")
	await _start_pilot()
	_check(_pilot.director().beats_run == [&"Choir"] and absf(GameState.dose - MATINS_DOSE) < 0.5,
		"in the choir, Dose as at the bell (%.1f)" % GameState.dose)

	for path in [TEST_SAVE, GameState.quiet_path()]:
		DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
	Talk.auto_choice = Callable()
	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


func _start_pilot() -> void:
	_pilot = NightPilot.new(_main.get(&"current_level"), _check)
	_pilot.shorten()
	await _pilot.frames(5)


func _level_id() -> int:
	var level: Node = _main.get(&"current_level")
	return level.get_instance_id()


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
