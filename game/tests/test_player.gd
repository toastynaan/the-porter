extends Node
## Player checks in the greybox abbey, driven through the input actions:
## walk 1.4 m/s and run 4 m/s with footsteps and head bob; covering the
## lantern (5 m to 1 m); looking back; opening a door by looking at it (and
## the draught guttering the lantern); high Dose guttering it; holding the
## breath; crawling under the mill wheel and dropping down the latrine chute.
## Run: tools/check.sh

var _fails := 0
var _player: Player
var _abbey: Node3D


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	_abbey = load("res://game/world/abbey/abbey.tscn").instantiate()
	add_child(_abbey)
	_player = _abbey.get_node(^"Player")
	var lantern: Lantern = _player.get_node(^"Head/LanternHand/Pivot/Lantern")
	await _seconds(0.5)
	GameState.snap_dose(0.0)

	# Walk and run in the outer court.
	_place(Vector3(-30, 0.05, 8), PI)
	var steps := []
	_player.stepped.connect(func(surface: String, running: bool) -> void: steps.append([surface, running]))
	var low := 9.0
	Input.action_press(&"move_forward")
	for i in 240:
		await get_tree().physics_frame
		low = minf(low, _player.head.position.y)
	_check(absf(_flat_speed() - 1.4) < 0.05, "walks at 1.4 m/s (%.2f)" % _flat_speed())
	_check(steps.size() >= 3 and steps[0][0] == "mud", "two footsteps a second on mud while walking (%d, %s)" % [steps.size(), steps[0] if steps.size() else "none"])
	_check(low < 1.59, "head bobs (lowest %.3f m)" % low)
	Input.action_press(&"run")
	await _seconds(1.5)
	_check(absf(_flat_speed() - 4.0) < 0.1 and _player.running, "runs at 4 m/s (%.2f)" % _flat_speed())
	Input.action_release(&"run")
	Input.action_release(&"move_forward")
	await _seconds(0.6)
	_check(_flat_speed() < 0.05, "stops")

	# Cover the lantern, look back.
	Input.action_press(&"cover_lantern")
	await _seconds(0.6)
	_check(is_equal_approx(lantern.light.omni_range, Lantern.COVERED_REACH) and not lantern.flame.visible, "covered lantern reaches 1 m")
	Input.action_release(&"cover_lantern")
	await _seconds(0.6)
	_check(is_equal_approx(lantern.light.omni_range, Lantern.REACH), "uncovered lantern reaches 5 m")
	Input.action_press(&"look_back")
	await _seconds(0.5)
	_check(absf(rad_to_deg(_player.look_back_pivot.rotation.y) - Player.LOOK_BACK_ANGLE) < 1.0, "looks back over the shoulder")
	Input.action_release(&"look_back")
	await _seconds(0.5)
	_check(absf(_player.look_back_pivot.rotation.y) < 0.01, "looks ahead again")
	Input.action_press(&"hold_breath")
	await _seconds(0.1)
	_check((_player.get_node(^"Breath") as Breath).holding, "holds breath")
	Input.action_release(&"hold_breath")

	# Look at the porter's cell door from outside and open it.
	_place(Vector3(-34, 0.05, -2.6), 0.0)
	await _seconds(0.3)
	var interactor: Interactor = _player.get_node(^"Head/LookBack/Camera/Interactor")
	var door := interactor.focused as Door
	_check(door != null, "the cell door is in reach")
	if door:
		_press(&"interact")
		await _seconds(1.0)
		_check(door.is_open, "interact opens it")
		await _seconds(1.5)
		_check(lantern.gutter > 0.2, "the open door's draught gutters the lantern (%.2f)" % lantern.gutter)
		_press(&"interact")
		await _seconds(2.0)
		_check(not door.is_open and lantern.gutter < 0.05, "closes again; the flame steadies")
	GameState.snap_dose(90.0)
	await _seconds(1.5)
	_check(lantern.gutter > 0.5, "Dose 90 gutters the lantern (%.2f)" % lantern.gutter)
	GameState.snap_dose(0.0)

	# Crawl under the mill wheel, both ways.
	var wheel: Squeeze = _abbey.get_node(^"Navigation/GraveyardInfirmary/Squeezes/UnderMillWheel")
	_place(Vector3(25.0, -1.15, 18), -PI / 2.0)
	await _seconds(0.3)
	wheel.interact(_player)
	await _seconds(wheel.crawl_time + 1.2)
	_check(_player.global_position.distance_to(Vector3(30.6, -1.2, 18)) < 0.3 and not _player.crawling, "crawls under the mill wheel")
	wheel.interact(_player)
	await _seconds(wheel.crawl_time + 1.2)
	_check(_player.global_position.distance_to(Vector3(25.4, -1.2, 18)) < 0.3, "and back")

	# Drop down the latrine chute into the race.
	var chute: Squeeze = _abbey.get_node(^"Navigation/Dormitory/Squeezes/LatrineChute")
	_place(Vector3(16, 4.05, 17.3), PI)
	await _seconds(0.3)
	chute.interact(_player)
	await _seconds(chute.crawl_time + 1.5)
	_check(absf(_player.global_position.y + 1.2) < 0.1 and _player.is_on_floor(), "drops down the latrine chute into the race (y %.2f)" % _player.global_position.y)

	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


func _place(pos: Vector3, yaw: float) -> void:
	_player.global_position = pos
	_player.rotation = Vector3(0, yaw, 0)
	_player.head.rotation = Vector3.ZERO
	_player.velocity = Vector3.ZERO


func _flat_speed() -> float:
	return Vector2(_player.velocity.x, _player.velocity.z).length()


## A tap: pressed and let go (a press counts once until it's let go, Press).
func _press(action: StringName) -> void:
	var e := InputEventAction.new()
	e.action = action
	e.pressed = true
	Input.parse_input_event(e)
	var up := InputEventAction.new()
	up.action = action
	Input.parse_input_event(up)


func _seconds(s: float) -> void:
	await get_tree().create_timer(s).timeout


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
