extends Node
## Getting caught on night 3 (main.tscn and night3.tscn). Starting from the
## Matins bell, the night picks up in the choir. Caught in the first chase,
## the porter wakes in the infirmary with Thomas over him and his keys gone,
## and the night goes on to dawn, where he finds them moved. Caught again,
## the night goes back to Matins, Dose and all, and the captures stay.
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
	GameState.set_flag(&"gate_barred")
	GameState.set_flag(&"n3_ate_bread")
	GameState.snap_dose(MATINS_DOSE)
	GameState.set_phase(GameState.Phase.MATINS)
	GameState.ring_bell(&"matins")
	Talk.line_seconds = 0.05
	Talk.auto_choice = func(_options: PackedStringArray) -> int: return 0
	_main = load("res://game/render/main.tscn").instantiate()
	add_child(_main)
	await _start_pilot()
	var p := _pilot.player
	_check(_pilot.director().beats_run == [&"Choir"], "a night saved at Matins picks up in the choir")
	_check(p.global_position.distance_to(_spawn()) < 0.5, "the porter is at the Matins spawn")
	var bar: Node3D = _pilot.night.get_node(^"Abbey/Navigation/OuterCourt/Props/GateBar")
	_check(bar.visible, "the gate is still barred")

	# Caught in the first chase: the infirmary, Thomas, the keys gone.
	await _to_the_chase()
	await _pilot.until(func() -> bool: return GameState.captures == 1, 10.0)
	_check(GameState.captures == 1 and GameState.keys.is_empty(), "caught: the first capture takes his keys")
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Dawn", 20.0)
	var thomas: Brother = _pilot.night.get_node(^"Brothers/Thomas")
	_check(GameState.has_flag(&"n3_caught") and GameState.has_flag(&"woke_in_infirmary") and thomas.visible,
		"he wakes in the infirmary with Thomas over him, and the night goes on")
	await _pilot.use("KeysMoved")
	await _pilot.until(func() -> bool: return GameState.has_flag(&"night3_done"), 5.0)
	_check(GameState.keys.size() == 3, "at dawn he finds his keys, moved")

	# The night again from Matins; caught a second time, it starts over there.
	GameState.load_last_bell()
	_main.call(&"reload_level")
	await _start_pilot()
	_check(_pilot.director().beats_run == [&"Choir"] and GameState.captures == 1, "back at Matins with one capture")
	await _to_the_chase()
	var level := _level_id()
	var flow: CaptureFlow = _main.get_node(^"CaptureFlow")
	await _pilot.until(func() -> bool: return _level_id() != level and not flow.busy, 30.0)
	_check(_level_id() != level and GameState.captures == 2, "the second capture kills; the night goes back to its bell")
	await _start_pilot()
	_check(_pilot.director().beats_run == [&"Choir"] and _pilot.player.global_position.distance_to(_spawn()) < 0.5,
		"in the choir again, from the Matins bell")
	_check(absf(GameState.dose - MATINS_DOSE) < 0.5 and not GameState.has_flag(&"n3_caught"),
		"with the night as it was at the bell (Dose %.1f)" % GameState.dose)

	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	Talk.auto_choice = Callable()
	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


func _start_pilot() -> void:
	_pilot = NightPilot.new(_main.get(&"current_level"), _check)
	_pilot.shorten()
	await _pilot.frames(5)


## Through Matins and the round, down to the crypt, and stands in the light.
func _to_the_chase() -> void:
	await _pilot.count_brothers()
	await _pilot.walk_round()
	await _pilot.go_down_to_crypt()


func _spawn() -> Vector3:
	return _pilot.mark("matins")


func _level_id() -> int:
	var level: Node = _main.get(&"current_level")
	return level.get_instance_id()


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
