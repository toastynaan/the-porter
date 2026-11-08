extends Node
## Plays night 3 from dusk to dawn with the test pilot and captures a still
## at each beat through the full render pipeline, subtitles and all, to
## art/_review/m6/ (tools/night3_shots.sh). The candle clock is moved on by
## hand for the dusk shots so the light is right in each.

const OUT := "res://art/_review/m6/"

var _pilot: NightPilot
var _n := 0
## The gate's answer while its choice is open (-1: not yet); other choices answer 0.
var _answer := -1
var _auto := true


func _ready() -> void:
	NightPilot.fresh_night("user://night3_shots_save.tres")
	Talk.line_seconds = 2.0
	Talk.auto_choice = func(_options: PackedStringArray) -> int: return _answer if _answer >= 0 else (0 if _auto else -1)
	var main: Node = load("res://game/render/main.tscn").instantiate()
	add_child(main)
	await get_tree().process_frame
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	_pilot = NightPilot.new(main.get(&"current_level"), func(ok: bool, what: String) -> void:
		if not ok:
			print("pilot: ", what))
	_pilot.shorten()
	_pilot.clock().set_pace(3600.0, 1.0)
	var p := _pilot.player
	var night := _pilot.night
	for walker in ["Carter", "Woman"]:
		(night.get_node(NodePath("People/" + walker)) as VisitorNPC).speed = 1.0

	# Dusk: the cell, the candle clock, a brother, the open gate, the lane.
	await _pilot.until(func() -> bool: return not p.controls_locked, 6.0)
	_pilot.face(Vector3(-33.25, 1.0, -10.5))
	await _shot("wake_cell", 1.0)
	p.place(Vector3(-34.1, 0.05, -10.5), deg_to_rad(-90.0))
	_pilot.face(Vector3(-33.25, 1.05, -10.5))
	(night.get_node(^"CandleClock") as CandleClock).interact(p)
	await _shot("candle_clock", 0.4)
	_pilot.skip_to(16.2)
	p.place(Vector3(-7.8, 0.05, -15.6), deg_to_rad(90.0))
	_pilot.face((night.get_node(^"Brothers/Edwin") as Node3D).global_position + Vector3.UP * 1.5)
	(night.get_node(^"Brothers/Edwin/Talker") as Talker).interact(p)
	await _said("(Placeholder: Edwin, the novice. Your friend, the one you talk to.)")
	await _shot("edwin_at_dusk", 0.3)
	_pilot.skip_to(16.4)
	p.place(Vector3(-32.0, 0.05, 1.5), deg_to_rad(90.0))
	_pilot.face(Vector3(-40.0, 1.4, -1.6))
	await _shot("gate_open_cole", 0.6)
	_pilot.skip_to(16.8)
	p.place(Vector3(-44.6, 0.05, 6.5), 0.0)
	p.head.rotation.x = deg_to_rad(2.0)
	await _shot("lane_at_dusk", 0.6)
	var mab := night.get_node(^"People/Mab") as Node3D
	p.place(Vector3(-43.6, 0.05, 2.4), 0.0)
	_pilot.face(mab.global_position + Vector3.UP * 1.3)
	(night.get_node(^"People/Mab/Talker") as Talker).interact(p)
	await _said("(Placeholder: Mab, a leper. She begs at the gate every night.)")
	await _shot("mab", 0.3)

	# The supper bell; supper; taking the gate from Cole.
	_pilot.skip_to(17.25)
	p.place(Vector3(-32.0, 0.05, 1.5), deg_to_rad(90.0))
	_pilot.face(Vector3(-40.0, 1.4, -1.6))
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Supper", 10.0)
	await _shot("supper_bell", 0.3)
	_pilot.skip_to(17.5)
	p.place(_pilot.mark("PorterSeat") + Vector3(0, 0, 0.6), PI)
	await _pilot.use("SupperSeat")
	await _pilot.until(func() -> bool: return _pilot.duty("Bread").enabled, 15.0)
	_pilot.face(_pilot.duty("Bread").global_position + Vector3(0.4, 0.6, -0.6))
	await _shot("supper")
	_pilot.duty("Bread").interact(p)
	await _pilot.until(func() -> bool: return _pilot.duty("RelieveCole").enabled, 40.0)
	var cole := night.get_node(^"People/Cole") as Node3D
	p.place(Vector3(-36.2, 0.05, -0.8), deg_to_rad(90.0))
	_pilot.face(cole.global_position + Vector3.UP * 1.5)
	await _shot("relieve_cole", 0.3)
	await _pilot.use("RelieveCole")
	p.place(Vector3(-37.2, 0.05, -2), deg_to_rad(90.0))
	await _pilot.use("ShutGate")
	await _pilot.use("BarGate")
	await _shot("gate_barred", 1.2)
	p.place(Vector3(-33.2, 0.05, -9.6), PI)
	await _pilot.use("Ledger")

	# The knocks, waited out dozing on the bench.
	GameState.snap_dose(55.0)
	GameState.dose_floor = 55.0
	await _pilot.doze()
	await _shot("bench_doze", 0.5)
	await _keep_gate(p)
	await _pilot.doze()
	await _pilot.until(func() -> bool: return _pilot.duty("Grate").enabled, 20.0)
	await _pilot.wake()
	p.place(Vector3(-39.2, 0.05, -2.4), deg_to_rad(90.0))
	await _pilot.use("Grate")
	await _shot("knock_no_one", 0.4)
	GameState.dose_floor = 0.0

	# Matins: woken at the mark; the bell, the choir, the round, the crypt, the chase.
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Bell", 30.0)
	await _pilot.doze()
	await _pilot.wake()
	p.place(Vector3(-24, 0.05, -30.8), 0.0)
	_pilot.face(Vector3(-24, 1.4, -32))
	await _pilot.use("BellRope")
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Choir", 10.0)
	await _pilot.count_brothers()
	await _pilot.seconds(6.0)
	p.place(_pilot.mark("Choir") + Vector3(-5.5, 0, 0), deg_to_rad(-90.0))
	p.head.rotation.x = deg_to_rad(4.0)
	await _shot("choir_headcount", 0.3)
	await _pilot.walk_round(_on_seen)
	await _pilot.until(func() -> bool: return (night.get_node(^"CryptLight") as Node3D).visible, 10.0)
	p.place(Vector3(19.5, 0.05, -33.0), deg_to_rad(-90.0))
	p.head.rotation.x = deg_to_rad(-38.0)
	await _shot("crypt_light", 1.0)
	await _pilot.go_down_to_crypt()
	var hunter: Hunter = night.get_node(^"Hunter")
	var oven: HidingSpot = night.get_node(^"Abbey/Navigation/SouthRange/HidingSpots/Oven")
	p.place(oven.exit.global_position, deg_to_rad(90.0))
	p.hide_in(oven)
	await _pilot.until(func() -> bool: return GameState.has_flag(&"n3_body3"), 5.0)
	p.head.rotation.x = deg_to_rad(-30.0)
	await _shot("oven_jaw", 0.2)
	p.head.rotation.x = deg_to_rad(-8.0)
	await _pilot.until(func() -> bool: return hunter.global_position.distance_to(oven.view.global_position) < 8.0, 60.0)
	Input.action_press(&"hold_breath")
	var checked := [false]
	oven.checked.connect(func(_found: bool) -> void: checked[0] = true)
	await _pilot.until(func() -> bool: return checked[0], 12.0)
	var gone := func() -> bool:
		return hunter.global_position.distance_to(oven.view.global_position) > 4.0 or hunter.state == Hunter.State.PATROL
	await _pilot.until(gone, 8.0)
	Input.action_release(&"hold_breath")
	p.leave_hiding()
	await _pilot.until(func() -> bool: return GameState.has_flag(&"n3_thomas_hid_you"), 15.0)
	await _pilot.seconds(1.2)
	_pilot.face((night.get_node(^"Brothers/Thomas") as Node3D).global_position + Vector3.UP * 1.5)
	await _shot("thomas", 0.3)

	# The small hours at the gate; Lauds; Cole takes the gate; the keys; sleep.
	await _pilot.until(func() -> bool: return _pilot.beat() == &"SmallHours", 15.0)
	p.place(Vector3(-33.0, 0.05, 0.5), deg_to_rad(90.0))
	_pilot.face(Vector3(-40.0, 1.4, -1.6))
	await _shot("small_hours", 1.0)
	await _pilot.doze()
	await _pilot.wake()
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Dawn", 10.0)
	_pilot.skip_to(30.4)
	p.place(Vector3(-37.8, 0.05, 1.8), deg_to_rad(-90.0))
	_pilot.face(cole.global_position + Vector3.UP * 1.5)
	await _shot("lauds_cole", 1.5)
	p.place(_pilot.mark("ColeGate") + Vector3(1.2, 0, 0), deg_to_rad(90.0))
	await _pilot.use("HandOver")
	_pilot.skip_to(30.7)
	await _pilot.until(func() -> bool: return (night.get_node(^"AbbeyGate") as AbbeyGate).is_open(), 5.0)
	p.place(Vector3(-34.0, 0.05, 0.5), deg_to_rad(90.0))
	_pilot.face(Vector3(-40.0, 1.4, -1.6))
	await _shot("gate_open_for_day", 0.6)
	p.place(_pilot.mark("DawnCell"), deg_to_rad(-120.0))
	_pilot.face(_pilot.duty("KeysMoved").global_position)
	await _said("(Your keys are not on their hook.)")
	await _shot("dawn_keys", 0.3)
	await _pilot.use("KeysMoved")
	await _pilot.use("Sleep")
	await _shot("sleep", 3.0)
	print("night 3 shots: rescued %s, captures %d, done %s" % [GameState.has_flag(&"n3_thomas_hid_you"), GameState.captures, GameState.has_flag(&"night3_done")])
	get_tree().quit()


## Walter at the grille (he knocked while the porter dozed), let in, and the
## ledger page with him and the night's duties at their times.
func _keep_gate(p: Player) -> void:
	_auto = false
	await _pilot.until(func() -> bool: return _pilot.duty("Grate").enabled, 30.0)
	await _pilot.wake()
	var walter := get_tree().get_first_node_in_group(&"callers") as VisitorNPC
	walter.speed = VisitorNPC.WALK_SPEED * 2.0
	p.place(Vector3(-39.2, 0.05, -2.4), deg_to_rad(90.0))
	_pilot.duty("Grate").interact(p)
	await _pilot.until(func() -> bool: return Talk.is_choosing(), 5.0)
	for part in [&"box", &"bag", &"face"]:
		_pilot.face(walter.part_position(part))
		await _pilot.seconds(0.6)
	await _shot("walter_at_the_grille", 0.1)
	_answer = 0
	await _pilot.frames(3)
	_answer = -1
	_auto = true
	await _pilot.use("BarGate")
	await _pilot.use("OpenGate")
	await _pilot.use("ShutGate")
	await _pilot.use("BarGate")
	p.place(Vector3(-30.0, 0.05, -19.0), 0.0)
	_pilot.face(_pilot.duty("GuestBeds/Bed2").global_position)
	await _pilot.use("GuestBeds/Bed2")
	await _pilot.until(func() -> bool: return walter.lying, 30.0)
	await _pilot.until(func() -> bool: return _pilot.duty("Ledger").enabled, 20.0)
	p.place(Vector3(-33.2, 0.05, -9.6), PI)
	await _pilot.use("Ledger")
	var ledger_view := get_tree().get_first_node_in_group(&"ledger_view") as LedgerView
	ledger_view.set_showing(true)
	await _shot("ledger_page", 0.3)
	ledger_view.set_showing(false)


## Waits until `line` has been said (lines queue behind each other).
func _said(line: String) -> void:
	await _pilot.until(func() -> bool: return Talk.history.any(func(h: Array) -> bool: return h[1] == line), 15.0)


## The last appearance on the round, right behind him, as he faces it.
func _on_seen(stalker: Stalker) -> void:
	if stalker.final:
		await _shot("demon_behind", 0.1)


func _shot(shot_name: String, settle := 0.5) -> void:
	await get_tree().create_timer(settle).timeout
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	var s := floori(img.get_height() / 540.0)
	if s > 1:
		img.resize(roundi(img.get_width() / float(s)), roundi(img.get_height() / float(s)), Image.INTERPOLATE_NEAREST)
	_n += 1
	var path := OUT + "%02d_%s.png" % [_n, shot_name]
	img.save_png(ProjectSettings.globalize_path(path))
	print("wrote ", path)
