extends Node
## The hunter in the M3 greybox (hunt_demo, the demon switched off): he sees
## the porter only by light (20 m lit, 2 m dark, a 100° view), hears running
## at 12 m but not walking at 6 m, chases and catches a lit porter, is winded
## after 20 s of sprinting, opens doors on his round, is stopped by a locked
## door, checks the hiding spots nearest where he lost you (a spot used
## twice first) and can't follow under the mill wheel.
## Run: tools/check.sh

var _fails := 0
var _player: Player
var _hunter: Hunter
var _caught := 0
## Simulated seconds (the test runs at a fixed 120 fps).
var _sim := 0.0


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	var demo: Node3D = load("res://game/dev/encounters/hunt_demo.tscn").instantiate()
	(demo.get_node(^"Stalker") as Stalker).active = false
	add_child(demo)
	_player = demo.get_node(^"Abbey/Player")
	_hunter = demo.get_node(^"Hunter")
	var route := _hunter.patrol_route
	_hunter.patrol_route = null
	_hunter.caught.connect(func(_p: Player) -> void: _caught += 1)
	GameState.suspicion = 0
	await _frames(60)

	# Sight: a lit porter at 15 m in front.
	_stage(Vector3(-10, 0.05, -10), 0.0, Vector3(-10, 0.05, -25), PI)
	await _until(func() -> bool: return _hunter.state == Hunter.State.CHASE, 2.5)
	_check(_hunter.state == Hunter.State.CHASE, "sees a lit lantern at 15 m and gives chase (%.1f s)" % _sim)

	# Covered and still at 5 m: he looks straight past.
	_stage(Vector3(-10, 0.05, -10), 0.0, Vector3(-10, 0.05, -15), PI, true)
	await _until(func() -> bool: return _hunter.state != Hunter.State.PATROL, 3.0)
	_check(_hunter.state == Hunter.State.PATROL, "doesn't see a covered lantern standing still at 5 m")
	_player.place(Vector3(-10, 0.05, -11.7), PI)
	await _until(func() -> bool: return _hunter.state == Hunter.State.CHASE, 1.5)
	_check(_hunter.state == Hunter.State.CHASE, "sees him in the dark at 1.7 m")
	Input.action_release(&"cover_lantern")

	# Behind him, lit, at 8 m: outside his view.
	_stage(Vector3(-10, 0.05, -10), PI, Vector3(-10, 0.05, -18), 0.0)
	await _until(func() -> bool: return _hunter.state != Hunter.State.PATROL, 2.0)
	_check(_hunter.state == Hunter.State.PATROL, "doesn't see a lantern behind him")

	# Hearing: walking away at 6 m behind him goes unheard, running at 10 m doesn't.
	_stage(Vector3(-10, 0.05, -10), 0.0, Vector3(-10, 0.05, -4.5), 0.0, true)
	_player.use_input_override = true
	_player.rotation.y = -PI * 0.5
	_player.input_override = Vector2(0, 1)
	await _until(func() -> bool: return _hunter.state != Hunter.State.PATROL, 1.5)
	_check(_hunter.state == Hunter.State.PATROL, "doesn't hear walking at 6 m")
	_stage(Vector3(-10, 0.05, -14), 0.0, Vector3(-10, 0.05, -4.5), 0.0, true)
	_player.use_input_override = true
	_player.rotation.y = -PI * 0.5
	_player.input_override = Vector2(0, 1)
	_player.run_override = true
	await _until(func() -> bool: return _hunter.state != Hunter.State.PATROL, 2.0)
	_player.use_input_override = false
	_check(_hunter.state == Hunter.State.INVESTIGATE, "hears running at 10 m and comes to look")
	Input.action_release(&"cover_lantern")

	# A lit porter standing still at 6 m is caught.
	_stage(Vector3(-10, 0.05, -10), 0.0, Vector3(-10, 0.05, -16), PI)
	var before := _caught
	await _until(func() -> bool: return _caught > before, 5.0)
	_check(_caught > before and _hunter.state == Hunter.State.CAPTURE, "runs him down and takes hold (%.1f s)" % _sim)

	# Winded: a long run from the crypt toward the mill race.
	_stage(Vector3(20, -4, -31), 0.0, Vector3(14, -4, -31), 0.0)
	_hunter.chase()
	await _frames(2)
	_player.place(Vector3(24.6, -1.2, 18), 0.0)
	await _until(func() -> bool: return _hunter.winded > 0.0, 25.0)
	var winded_at := _sim
	await _seconds(0.5)
	var at := _hunter.global_position
	await _seconds(3.0)
	var still := _hunter.global_position.distance_to(at)
	await _seconds(1.5)
	_check(absf(winded_at - Hunter.SPRINT_LIMIT) < 0.5, "winded after 20 s of sprinting (%.1f)" % winded_at)
	_check(still < 0.3 and _hunter.global_position.distance_to(at) > 1.0, "stops to listen, then runs on (%.2f m)" % still)

	# Doors: on his round he opens the church door and goes in.
	var church_door: Door = demo.get_node(^"Abbey/Navigation/Church/Doors/NaveS0Door_02")
	church_door.set_open(false, true)
	_hunter.patrol_route = route
	_stage(Vector3(-10, 0.05, -24.5), PI, Vector3(-30, 0.05, 0), 0.0)
	await _until(func() -> bool: return _hunter.global_position.z < -29.5, 14.0)
	_check(_hunter.global_position.z < -29.5, "opens the church door on his round and goes in (%.1f s)" % _sim)
	await _until(func() -> bool: return _hunter.global_position.z > -26.0, 15.0)
	await _seconds(2.0)
	_check(not church_door.is_open, "shuts it behind him")
	_hunter.patrol_route = null

	# Locked out of the charnel house.
	var charnel: Door = demo.get_node(^"Abbey/Navigation/GraveyardInfirmary/Doors/CharnelW0Door_01")
	charnel.set_open(false, true)
	_check(charnel.toggle_lock(), "the porter locks the charnel house")
	_stage(Vector3(27, 0.0, -18), -PI * 0.5, Vector3(36, 0.05, -20), 0.0)
	_hunter.chase()
	before = _caught
	await _seconds(10.0)
	_check(_caught == before and _hunter.global_position.x < 32.0 and _hunter.state != Hunter.State.CHASE,
		"a locked door keeps him out (at x %.1f, %s)" % [_hunter.global_position.x, Hunter.State.keys()[_hunter.state]])
	charnel.toggle_lock()

	# Search order: twice-used spots first, then the nearest two.
	var cloister := Vector3(0, 0.05, -16)
	_hunter.global_position = cloister
	var names := _hunter.search_list(cloister).map(func(s: HidingSpot) -> String: return s.name)
	_check(names == ["PillarW", "PillarE"], "checks the 2 spots nearest where he lost you %s" % [names])
	var sacks := _spot("GrainSacks")
	sacks.uses = 2
	names = _hunter.search_list(cloister).map(func(s: HidingSpot) -> String: return s.name)
	_check(names == ["GrainSacks", "PillarW"], "a spot used twice tonight first %s" % [names])
	sacks.uses = 0

	# Seen climbing into the oven: he checks it. Holding the breath, chance 0: safe.
	GameState.suspicion = 40
	var oven := _spot("Oven")
	oven.check_chance = 0.0
	var checked := []
	oven.checked.connect(func(found: bool) -> void: checked.append(found))
	await _hide_while_watched(oven)
	before = _caught
	Input.action_press(&"hold_breath")
	await _until(func() -> bool: return not checked.is_empty(), 10.0)
	_check(checked == [false], "checks the oven he saw you go into and misses you (%s)" % [checked])
	await _until(func() -> bool: return _hunter.global_position.distance_to(oven.view.global_position) > 4.0, 8.0)
	Input.action_release(&"hold_breath")
	await _seconds(2.0)
	_check(_caught == before and _player.hiding == oven, "goes on searching elsewhere; still hidden")
	_player.leave_hiding(true)

	# Same again at chance 1: dragged out.
	oven.check_chance = 1.0
	checked.clear()
	await _hide_while_watched(oven)
	Input.action_press(&"hold_breath")
	await _until(func() -> bool: return _caught > before, 10.0)
	Input.action_release(&"hold_breath")
	_check(_caught > before and _player.hiding == null, "a spot with chance 1 gives you up")

	# Under Suspicion 30 he doesn't search, but a gasp from a spot gives it away.
	GameState.suspicion = 0
	oven.check_chance = 0.0
	checked.clear()
	await _hide_while_watched(oven)
	await _until(func() -> bool: return not checked.is_empty() or _hunter.state == Hunter.State.PATROL, 12.0)
	_check(checked.is_empty(), "below Suspicion 30 he only looks around")
	before = _caught
	_hunter.global_position = oven.check_point() + Vector3(2.0, 0, 0)
	_player.breath.meter = 0.05
	Input.action_press(&"hold_breath")
	await _until(func() -> bool: return not _player.breath.holding and _sim > 0.1, 3.0)
	Input.action_release(&"hold_breath")
	await _until(func() -> bool: return _caught > before, 15.0)
	_check(_caught > before, "a gasp from the oven: he looks in, and breathing, you're found")

	# Under the mill wheel: he can't follow.
	_stage(Vector3(17.4, -1.2, 18), -PI * 0.5, Vector3(25.4, -1.2, 18), -PI * 0.5)
	_hunter.chase()
	var wheel := demo.get_node(^"Abbey/Navigation/GraveyardInfirmary/Squeezes/UnderMillWheel") as Squeeze
	wheel.interact(_player)
	before = _caught
	var closest := INF
	_sim = 0.0
	while _sim < 6.0:
		await get_tree().physics_frame
		closest = minf(closest, _hunter.global_position.distance_to(_player.global_position))
	_check(_caught == before and _hunter.global_position.x < 27.0, "can't follow under the mill wheel (closest %.1f m)" % closest)

	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


## Hunter at `h` facing `h_yaw`, porter at `p` facing `p_yaw`; fresh state.
func _stage(h: Vector3, h_yaw: float, p: Vector3, p_yaw: float, covered := false) -> void:
	_player.use_input_override = false
	_player.run_override = false
	_player.input_override = Vector2.ZERO
	_player.place(p, p_yaw)
	_player.stamina.value = 1.0
	_player.stamina.exhausted = false
	if covered:
		Input.action_press(&"cover_lantern")
		_player.lantern.covered = true
	else:
		Input.action_release(&"cover_lantern")
	_hunter.reset()
	_hunter.global_transform = Transform3D(Basis(Vector3.UP, h_yaw), h)
	_hunter._warmup = 0.0
	_sim = 0.0


## The hunter sees the porter by the oven, the porter climbs in.
func _hide_while_watched(oven: HidingSpot) -> void:
	_stage(Vector3(-14.2, 0.05, 10.5), deg_to_rad(43.0), oven.exit.global_position, deg_to_rad(90.0))
	await _until(func() -> bool: return _hunter.state == Hunter.State.CHASE, 2.0)
	_player.hide_in(oven)
	await _seconds(0.8)


func _spot(spot_name: String) -> HidingSpot:
	for s: HidingSpot in get_tree().get_nodes_in_group(&"hiding_spots"):
		if s.name == spot_name:
			return s
	return null


func _physics_process(delta: float) -> void:
	_sim += delta


## Waits until `cond` holds or `limit` seconds pass; `_sim` counts from here.
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
