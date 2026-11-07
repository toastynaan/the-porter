extends Node
## Hiding and the porter's body in the greybox abbey: climbing into the oven
## by looking at it (camera low, lantern covered, noise heard), the breath
## meter (12 s, 8 s hungry, a gasp a hunter hears), a hunter's check (found
## breathing; by chance holding the breath), climbing out, look limits,
## stamina, and locking a door with the porter's keys.
## Run: tools/check.sh

var _fails := 0
var _player: Player
var _heard: Array = []
## Simulated seconds (the test runs at a fixed 120 fps).
var _sim := 0.0


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	var abbey: Node3D = load("res://game/world/abbey/abbey.tscn").instantiate()
	add_child(abbey)
	_player = abbey.get_node(^"Player")
	add_to_group(&"listeners")
	await _seconds(0.5)
	GameState.set_flag(&"hungry", false)

	# Look at the oven's mouth from the bakehouse and climb in.
	var oven := _spot("Oven")
	_player.place(Vector3(-15.6, 0.05, 8.0), deg_to_rad(90.0))
	_player.head.rotation.x = deg_to_rad(-22.0)
	await _seconds(0.3)
	var interactor: Interactor = _player.get_node(^"Head/LookBack/Camera/Interactor")
	_check(interactor.focused == oven, "the oven is in reach (%s)" % interactor.focused)
	_heard.clear()
	_press(&"interact")
	await _seconds(1.2)
	_check(_player.hiding == oven and oven.occupant == _player and oven.uses == 1, "climbs into the oven")
	_check(_player.camera.global_position.distance_to(oven.view.global_position) < 0.1,
		"the camera is at the oven's view (%.2f m off)" % _player.camera.global_position.distance_to(oven.view.global_position))
	_check(_player.lantern.covered and is_equal_approx(_player.lantern.light.omni_range, Lantern.COVERED_REACH),
		"the lantern goes under the cloak")
	_check(_heard_radius(oven) > 5.9, "getting in carries %.0f m (noise 0.6)" % _heard_radius(oven))
	_player._look(Vector2(3.0, 0.0))
	var yaw_off := rad_to_deg(absf(wrapf(_player.rotation.y - deg_to_rad(-90.0), -PI, PI)))
	_check(absf(yaw_off - oven.look_yaw) < 0.5, "look is limited to %.0f° either side (%.1f)" % [oven.look_yaw, yaw_off])
	_player._look(Vector2(-3.0, 0.0))

	# The hunter's check: breathing gives you away; holding, it's the spot's chance.
	oven.check_chance = 0.0
	_check(oven.check(), "found while breathing")
	Input.action_press(&"hold_breath")
	await _seconds(0.1)
	_check(_player.breath.holding and not oven.check(), "not found holding the breath at chance 0")
	oven.check_chance = 1.0
	_check(oven.check(), "found holding the breath at chance 1")

	# The breath meter: 12 s, then a gasp a hunter hears.
	var gasp_at := [-1.0]
	_player.breath.gasped.connect(func() -> void: gasp_at[0] = _sim)
	_heard.clear()
	await _until(func() -> bool: return gasp_at[0] >= 0.0, 14.0)
	_check(absf(gasp_at[0] - 11.9) < 0.4, "breath runs out after 12 s (%.1f)" % gasp_at[0])
	_check(_heard.any(func(h: Array) -> bool: return h[1] == Earshot.GASP), "the gasp carries %.0f m" % Earshot.GASP)
	_check(not _player.breath.holding, "he has to breathe")
	Input.action_release(&"hold_breath")
	await _seconds(6.5)
	_check(is_equal_approx(_player.breath.meter, 1.0), "the meter refills")
	GameState.set_flag(&"hungry", true)
	gasp_at[0] = -1.0
	Input.action_press(&"hold_breath")
	await _until(func() -> bool: return gasp_at[0] >= 0.0, 10.0)
	Input.action_release(&"hold_breath")
	_check(absf(gasp_at[0] - 8.0) < 0.4, "8 s when hungry (%.1f)" % gasp_at[0])
	GameState.set_flag(&"hungry", false)

	# Climb out to the exit; a second use counts.
	await _seconds(2.5)
	_press(&"interact")
	await _seconds(1.2)
	_check(_player.hiding == null and oven.occupant == null, "climbs out")
	_check(_player.global_position.distance_to(oven.exit.global_position) < 0.3, "stands at the exit")
	_check(not _player.lantern.covered, "the lantern comes out again")
	_player.hide_in(oven)
	await _seconds(1.0)
	_player.leave_hiding()
	await _seconds(1.0)
	_check(oven.uses == 2, "a second use tonight counts (%d)" % oven.uses)

	# Stamina: 25 s of running, 15 s to refill, half as fast again hungry.
	var st := _player.stamina
	st.value = 1.0
	st.exhausted = false
	var ran := 0.0
	while st.can_run() and ran < 40.0:
		st.update(true, 0.05)
		ran += 0.05
	_check(absf(ran - 25.0) < 0.1, "runs dry after 25 s (%.1f)" % ran)
	var rested := 0.0
	while not st.can_run():
		st.update(false, 0.05)
		rested += 0.05
	_check(absf(rested - 4.5) < 0.1, "can run again at 30%% after %.1f s" % rested)
	st.value = 0.0
	var full := 0.0
	while st.value < 1.0:
		st.update(false, 0.05)
		full += 0.05
	GameState.set_flag(&"hungry", true)
	st.value = 0.0
	var full_hungry := 0.0
	while st.value < 1.0:
		st.update(false, 0.05)
		full_hungry += 0.05
	GameState.set_flag(&"hungry", false)
	_check(absf(full - 15.0) < 0.1 and absf(full_hungry - 22.5) < 0.1, "refills in %.1f s, %.1f s hungry" % [full, full_hungry])
	st.value = 1.0
	st.exhausted = false

	# Keys: the porter locks the guesthouse door, a hunter-proof door.
	var door: Door = abbey.get_node(^"Navigation/OuterCourt/Doors/GuestS0Door_01")
	_player.place(Vector3(-30, 0.05, -14.6), 0.0)
	await _seconds(0.3)
	_check(interactor.focused == door, "the guesthouse door is in reach")
	_heard.clear()
	_press(&"lock")
	await _seconds(0.1)
	_check(door.locked, "R locks it with the guesthouse key")
	_check(_heard.any(func(h: Array) -> bool: return h[1] == Earshot.KEY), "the key is heard at %.0f m" % Earshot.KEY)
	_press(&"interact")
	await _seconds(1.0)
	_check(not door.is_open, "a locked door won't open")
	_check(door.toggle_lock() and not door.locked, "unlocks again")
	GameState.keys.erase(&"guesthouse")
	_check(not door.toggle_lock() and not door.locked, "no key, no lock")
	GameState.keys.append(&"guesthouse")
	door.set_open(true, true)
	_check(not door.toggle_lock(), "an open door can't be locked")
	_check(door.crosses(door.global_position + Vector3(0, 1, 2), door.global_position + Vector3(0, 1, -2))
		and not door.crosses(door.global_position + Vector3(3, 1, 2), door.global_position + Vector3(3, 1, -2)),
		"knows which paths go through the doorway")

	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


func _spot(spot_name: String) -> HidingSpot:
	for s: HidingSpot in get_tree().get_nodes_in_group(&"hiding_spots"):
		if s.name == spot_name:
			return s
	return null


func _heard_radius(source: Node) -> float:
	var r := 0.0
	for h: Array in _heard:
		if h[2] == source:
			r = maxf(r, h[1])
	return r


## Listens like a hunter: every Earshot.make() lands here.
func hear(at: Vector3, radius: float, source: Node) -> void:
	_heard.append([at, radius, source])


func _press(action: StringName) -> void:
	var e := InputEventAction.new()
	e.action = action
	e.pressed = true
	Input.parse_input_event(e)
	await get_tree().process_frame
	var r := InputEventAction.new()
	r.action = action
	r.pressed = false
	Input.parse_input_event(r)


func _physics_process(delta: float) -> void:
	_sim += delta


## Waits until `cond` holds or `limit` seconds; `_sim` counts from the start.
func _until(cond: Callable, limit: float) -> void:
	_sim = 0.0
	while not cond.call() and _sim < limit:
		await get_tree().physics_frame


func _seconds(s: float) -> void:
	await get_tree().create_timer(s).timeout


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
