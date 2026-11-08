extends Node
## Getting caught, through the whole game (main.tscn with the hunt demo;
## docs/mechanics.md, "Being hunted"): a level rings the "start" bell. On
## night 1 the first capture wakes you in the infirmary with +40 Dose, the
## satchel emptied but the keys kept, and the hunter back on his round; the
## second kills you and restarts the night from the bell, Dose and all, at
## the bell's spawn; a restart never undoes a capture, so the next one kills
## too. On night 3 the first capture kills. A quiet save after the bell is
## where death goes back to, until the next bell clears it.
## Run: tools/check.sh

const TEST_SAVE := "user://test_capture_save.tres"

var _fails := 0
var _main: Node
var _flow: CaptureFlow
var _sim := 0.0


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	GameState.save_path = TEST_SAVE
	GameState.new_game()
	GameState.night = 1
	GameState.satchel.assign([&"apple", &"mask"])
	GameState.snap_dose(10.0)
	_main = load("res://game/render/main.tscn").instantiate()
	_main.level = load("res://game/encounters/hunt_demo.tscn")
	add_child(_main)
	_flow = _main.get_node(^"CaptureFlow")
	_quiet_demon()
	await _frames(60)
	_check(GameState.last_bell == &"start" and GameState.has_bell_save(), "the level rings the start bell")
	var first_level := _level_id()

	# First capture: the infirmary.
	var woke := [false]
	_flow.woke.connect(func() -> void: woke[0] = true)
	await _caught_in_the_cloister()
	_check(_player().controls_locked, "caught: his body is taken")
	await _until(func() -> bool: return woke[0], 12.0)
	_check(woke[0] and GameState.captures == 1, "the first capture isn't death (%d)" % GameState.captures)
	var bed := get_tree().get_first_node_in_group(&"wake_point") as Node3D
	_check(_player().global_position.distance_to(bed.global_position) < 0.5, "wakes in the infirmary")
	_check(not _player().controls_locked and is_equal_approx(_player().head.position.y, Player.EYE_HEIGHT),
		"gets up and can move again")
	await _seconds(4.0)
	_check(GameState.dose > 49.0, "with a fresh dose in him (%.1f, was 10)" % GameState.dose)
	_check(GameState.get_flag(&"woke_in_infirmary") == true, "the night remembers it")
	_check(GameState.satchel.is_empty() and GameState.keys.size() == 3, "the cult took the satchel, but not the keys")
	var hunter := _hunter()
	_check(hunter.state == Hunter.State.PATROL and hunter.global_position.distance_to(_player().global_position) > 15.0,
		"the hunter is back on his round, far off")
	_check(_level_id() == first_level, "same night, no restart")

	# Second capture: death, back to the start bell.
	var died := [false]
	_flow.died.connect(func() -> void: died[0] = true)
	await _caught_in_the_cloister()
	await _until(func() -> bool: return _level_id() != first_level and not _flow.busy, 15.0)
	_check(died[0] and _level_id() != first_level, "the second capture kills; the night restarts")
	_quiet_demon()
	await _frames(10)
	var spawn: Node3D = null
	for s: Node3D in get_tree().get_nodes_in_group(&"bell_spawn"):
		if s.name == "start":
			spawn = s
	_check(spawn != null and _player().global_position.distance_to(spawn.global_position) < 0.3, "back at the start bell")
	_check(absf(GameState.dose - 10.0) < 0.5, "Dose as it was at the bell (%.1f)" % GameState.dose)
	_check(GameState.captures == 2, "the restart keeps both captures (%d)" % GameState.captures)

	# And the next capture kills again.
	var level := _level_id()
	await _caught_in_the_cloister()
	await _until(func() -> bool: return _level_id() != level and not _flow.busy, 15.0)
	_check(_level_id() != level and GameState.captures == 3, "every capture after that kills")

	# Night 3: the first capture kills.
	GameState.night = 3
	GameState.captures = 0
	_check(not CaptureFlow.forgiving(), "from night 3 no capture is forgiving")
	level = _level_id()
	var woke_before: bool = woke[0]
	woke[0] = false
	await _caught_in_the_cloister()
	await _until(func() -> bool: return _level_id() != level and not _flow.busy, 15.0)
	_check(_level_id() != level and not woke[0] and woke_before, "on night 3 the first capture kills")

	# A quiet save after the bell: death goes back to it, until a bell.
	_quiet_demon()
	await _frames(10)
	GameState.snap_dose(33.0)
	_check(GameState.quiet_save(&"start") and GameState.has_quiet_save(), "a quiet save")
	level = _level_id()
	await _caught_in_the_cloister()
	await _until(func() -> bool: return _level_id() != level and not _flow.busy, 15.0)
	_check(absf(GameState.dose - 33.0) < 0.5, "death goes back to the quiet save, not the bell (Dose %.1f)" % GameState.dose)
	GameState.ring_bell(&"start")
	_check(not GameState.has_quiet_save(), "the next bell clears it")

	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


## Puts the hunter 4 m from a lit porter in the cloister and waits for the catch.
func _caught_in_the_cloister() -> void:
	var hunter := _hunter()
	_player().place(Vector3(-10, 0.05, -20), 0.0)
	hunter.reset()
	hunter.global_transform = Transform3D(Basis.IDENTITY, Vector3(-10, 0.05, -16))
	hunter.chase()
	await _until(func() -> bool: return _flow.busy, 5.0)


func _quiet_demon() -> void:
	for s: Stalker in get_tree().get_nodes_in_group(&"stalkers"):
		s.queue_free()


## Which level instance is loaded (the old one is freed on a restart).
func _level_id() -> int:
	var level: Node = _main.current_level
	return level.get_instance_id()


func _player() -> Player:
	return get_tree().get_first_node_in_group(&"player") as Player


func _hunter() -> Hunter:
	return get_tree().get_first_node_in_group(&"hunters") as Hunter


func _physics_process(delta: float) -> void:
	_sim += delta


func _until(cond: Callable, limit: float) -> void:
	_sim = 0.0
	while not cond.call() and _sim < limit:
		await get_tree().physics_frame


func _frames(n: int) -> void:
	for i in n:
		await get_tree().physics_frame


func _seconds(s: float) -> void:
	await get_tree().create_timer(s, true, true).timeout


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
