extends Node
## The incense at Matins from night 4 (docs/systems/mechanics.md, "Incense from
## night 4" and "Tests": the dose by place, holding your breath, being seen
## out of your stall), in a test night of Matins alone: in his stall he
## takes the whole +25; by the choir's west door about a third; holding his
## breath, nothing; and seen out of his stall by a brother while the office
## is sung, Suspicion +10, once.
## Run: tools/check.sh

const TEST_SAVE := "user://test_incense_save.tres"

var _fails := 0
var _main: Node
var _pilot: NightPilot


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	NightPilot.fresh_night(TEST_SAVE)
	Talk.line_seconds = 0.05
	_main = NightPilot.main_with("res://game/tests/scenes/matins_night4.tscn")
	add_child(_main)

	# In his stall: all of it.
	var stall := await _office(&"stall", false)
	_check(absf(stall - 25.0) < 1.0, "in his stall he takes the whole +25 (%.1f)" % stall)
	_check(GameState.suspicion == 0, "in his stall no one minds him")

	# By the west door: about a third, and the brothers see him out of his stall.
	var door := await _office(&"door", false)
	_check(absf(door - 25.0 / 3.0) < 1.0, "by the west door about a third (%.1f)" % door)
	_check(GameState.suspicion == 10 and GameState.has_flag(&"n4_seen_out_of_stall"),
		"seen out of his stall while the office is sung: +10 (%d)" % GameState.suspicion)

	# Holding his breath by the door: nothing.
	var held := await _office(&"door", true)
	_check(held < 0.1, "holding his breath he takes none (%.2f)" % held)
	_check(GameState.suspicion == 10, "and seen out of his stall again, it costs once a night")

	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


## Plays the office with the porter `where` (his stall or the west door),
## holding his breath or not; returns the Dose the incense gave him.
func _office(where: StringName, hold: bool) -> float:
	var keep_suspicion := GameState.suspicion
	# The same night, played again: its start state stays as it was.
	var keep_flags := {&"night_started": true}
	if GameState.has_flag(&"n4_seen_out_of_stall"):
		keep_flags[&"n4_seen_out_of_stall"] = GameState.get_flag(&"n4_seen_out_of_stall")
	GameState.flags = keep_flags
	GameState.suspicion = keep_suspicion
	GameState.snap_dose(0.0)
	GameState.last_bell = &""
	_main.call(&"reload_level")
	_pilot = NightPilot.new(_main.get(&"current_level"), _check)
	await _pilot.frames(5)
	var marks := _pilot.night.get_node(^"Marks")
	var at: Marker3D = marks.get_node(^"PorterStall" if where == &"stall" else ^"ChoirWestDoor")
	_pilot.player.place(at.global_position, deg_to_rad(-90.0))
	var choir: Node = _pilot.director().get_node(^"Choir")
	await _pilot.until(func() -> bool: return GameState.has_flag(&"n4_incense"), 5.0)
	if hold:
		Input.action_press(&"hold_breath")
	for b: Brother in get_tree().get_nodes_in_group(&"brothers"):
		if b.visible:
			_pilot.face(b.global_position + Vector3.UP * 1.6)
			await _pilot.seconds(0.4)
	await _pilot.until(func() -> bool: return _pilot.over(), 20.0)
	Input.action_release(&"hold_breath")
	return float(choir.get(&"taken"))


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
