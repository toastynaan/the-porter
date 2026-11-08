extends Node
## Stills of M12's prologue through the full render pipeline, to
## art/_review/m12/ (tools/m12_shots.sh). Night 0: the fields from the
## wagon, the cart with the body, Aldgate, the lane at dusk, the barred gate
## and Mab, the Cross Keys' taproom, talking to Agnes, three ales, the room
## at the top, the dark lane and Gib after the curfew, the lane through the
## cell's squint, the shape in the south squint, the killing from the
## window, the body dragged off. Day 1: the morning with a headache, the
## sand by the well, the tour, the nap.

const OUT := "res://art/_review/m12/"

var _n := 0
var _main: Node
var _pilot: NightPilot


func _ready() -> void:
	NightPilot.fresh_night("user://m12_shots_save.tres")
	GameState.night = 0
	GameState.chapter = 0
	Talk.line_seconds = 3.0
	Talk.auto_choice = func(_o: PackedStringArray) -> int: return 0
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	_main = NightPilot.main_with("res://game/nights/night0.tscn")
	add_child(_main)
	await get_tree().create_timer(0.5).timeout
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	_pilot = NightPilot.new(_main.get(&"current_level"), func(_ok: bool, _w: String) -> void: pass)
	var night := _pilot.night
	var p := _pilot.player
	(night.get_node(^"Hallucinations") as Hallucinations).active = false
	var ride := night.get_node(^"Director/Ride")
	ride.set(&"speed", 7.0)
	ride.set(&"meet_at", 9.0)
	_pilot.clock().set_pace(3600.0, 0.1)

	# The ride.
	await _until(func() -> bool: return p.riding != null, 5.0)
	await get_tree().create_timer(3.0).timeout
	p.head.rotation.x = deg_to_rad(-4.0)
	await _shot("ride_fields", 0.1)
	var cart := night.get_node(^"BodyCart") as Node3D
	await _until(func() -> bool: return cart.global_position.distance_to(p.global_position) < 9.0, 15.0)
	_look_at(p, cart.global_position + Vector3.UP * 0.8)
	await _shot("ride_body_cart", 0.1)
	await _until(func() -> bool: return p.global_position.x > -128.0, 40.0)
	p.rotation.y = deg_to_rad(-90.0)
	p.head.rotation.x = deg_to_rad(6.0)
	await _shot("ride_aldgate", 0.1)
	await _until(func() -> bool: return GameState.has_flag(&"n0_arrived"), 60.0)

	# The lane at dusk; the barred gate and Mab.
	p.place(Vector3(-43.0, 0.05, 12.0), 0.0)
	p.head.rotation.x = deg_to_rad(-3.0)
	await _shot("lane_at_dusk", 1.0)
	p.place(Vector3(-44.6, 0.05, 1.6), deg_to_rad(-70.0))
	await _shot("barred_gate_and_mab", 0.5)
	await _pilot.use("KnockGate")
	var mab := night.get_node(^"People/Mab") as VisitorNPC
	await _pilot.talk(mab.get_node(^"Talker") as Talker, [0, 0, 0], [-1])
	await _until(func() -> bool: return not Talk.talking and _pilot.beat() == &"Inn", 90.0)

	# The Cross Keys.
	p.place(Vector3(-47.6, 0.05, -2.0), deg_to_rad(90.0))
	await _shot("the_cross_keys", 1.0)
	var agnes := night.get_node(^"People/Agnes") as VisitorNPC
	p.place(agnes.global_position + Vector3(1.4, 0.0, 0.3), deg_to_rad(90.0))
	Talk.auto_choice = Callable()
	(agnes.get_node(^"Talker") as Talker).interact(p)
	await _until(func() -> bool: return Talk.is_choosing(), 15.0)
	await _shot("talking_to_agnes", 1.0)
	Talk.auto_choice = func(_o: PackedStringArray) -> int: return 0
	await _until(func() -> bool: return not Talk.talking and GameState.has_flag(&"n0_room"), 60.0)
	for i in 3:
		GameState.have_a_drink()
	p.place(Vector3(-48.2, 0.05, -1.0), deg_to_rad(100.0))
	await _shot("three_ales", 1.0)
	GameState.drink = 0.0
	p.place(Vector3(-50.4, 6.05, 0.2), 0.0)
	_look_at(p, Vector3(-46.7, 6.7, 2.4))
	await _shot("the_room_at_the_top", 0.5)

	# After the bell: the dark lane, Gib; the squints.
	_pilot.skip_to(21.0)
	await get_tree().create_timer(4.0).timeout
	_pilot.skip_to(22.02)
	var gib := night.get_node(^"People/Gib") as VisitorNPC
	gib.set_present(true, Transform3D(Basis(Vector3.UP, PI), Vector3(-43.4, 0.05, 7.0)))
	gib.stop()
	p.place(Vector3(-42.6, 0.05, 1.0), PI)
	p.head.rotation.x = deg_to_rad(-2.0)
	await _shot("after_the_curfew_gib", 1.5)
	gib.set_present(false)
	var cell := night.get_node(^"Squints/Cell") as Squint
	p.place(cell.global_position + Vector3(1.2, -1.55, 0.0), deg_to_rad(90.0))
	cell.interact(p)
	await _shot("the_lane_through_the_cells_squint", 1.2)
	p.stop_peeking()
	await get_tree().create_timer(1.0).timeout
	var scare := night.get_node(^"SquintScare") as SquintScare
	p.place(scare.squint.global_position + Vector3(-1.4, -1.55, 0.0), 0.0)
	await get_tree().create_timer(0.3).timeout
	_look_at(p, scare.squint.global_position)
	await _shot("the_shape_in_the_south_squint", 0.6)
	p.place(p.global_position + Vector3(-1.0, 0.0, 0.0), 0.0)
	await get_tree().create_timer(0.4).timeout

	# The window.
	var death := night.get_node(^"WindowKilling") as DeathScene
	p.place(_pilot.duty("InnBed").global_position + Vector3(0.0, 0.0, -1.4), 0.0)
	await _pilot.use("InnBed")
	await _until(func() -> bool: return death.has_played, 15.0)
	await get_tree().create_timer(0.6).timeout
	await _shot("the_killing_from_the_window", 0.1)
	await _until(func() -> bool: return death.body == null, 30.0)
	await get_tree().create_timer(0.1).timeout
	await _until(func() -> bool: return _pilot.beat() == &"Sleep", 30.0)
	_look_at(p, night.get_node(^"Marks/DragTo").global_position)
	await _shot("gone_toward_the_cellar", 0.3)

	# Day 1.
	var night_id := night.get_instance_id()
	GameState.set_flag(&"drank", 3)
	await _pilot.use("InnBed")
	await _until(func() -> bool: return _main.get(&"current_level") != null and (_main.get(&"current_level") as Node).get_instance_id() != night_id, 20.0)
	await get_tree().create_timer(0.5).timeout
	_pilot = NightPilot.new(_main.get(&"current_level"), func(_ok: bool, _w: String) -> void: pass)
	night = _pilot.night
	p = _pilot.player
	(night.get_node(^"Hallucinations") as Hallucinations).active = false
	_pilot.clock().set_pace(3600.0, 0.1)
	for person in night.get_node(^"People").get_children():
		if person is VisitorNPC:
			(person as VisitorNPC).speed = 4.0
	await _until(func() -> bool: return _pilot.beat() == &"Morning" and not p.controls_locked, 15.0)
	p.place(night.get_node(^"Marks/Day1Wake").global_position, deg_to_rad(-90.0))
	await _shot("morning_with_a_headache", 1.0)
	p.place(Vector3(-36.0, 0.05, 2.0), deg_to_rad(-70.0))
	_look_at(p, Vector3(-28.0, 0.0, 4.0))
	await _shot("the_sand_by_the_well", 1.0)
	await _until(func() -> bool: return _pilot.beat() == &"Tour", 10.0)
	await _until(func() -> bool: return _pilot.duty("BarGate").enabled, 30.0)
	var thomas := night.get_node(^"People/TourThomas") as Node3D
	p.place(thomas.global_position + Vector3(2.6, 0.0, 1.4), 0.0)
	_look_at(p, thomas.global_position + Vector3(-0.6, 1.5, 0.0))
	await _shot("the_tour_thomas_and_anselm", 1.0)
	for path in ["BarGate", "Ledger", "", "BellRope", "RoundStops/StoresDoor", "GuestBeds/Bed0", "GuestKey"]:
		if path.is_empty():
			var candles := night.get_node(^"CandleClock") as CandleClock
			await _until(func() -> bool: return candles.is_in_group(&"glyph_targets"), 60.0)
			candles.interact(p)
		else:
			await _until(func() -> bool: return _pilot.duty(path).enabled, 60.0)
			p.place(_pilot.duty(path).global_position + Vector3(0.0, 0.0, 1.2), 0.0)
			if path == "GuestBeds/Bed0":
				_look_at(p, _pilot.duty(path).global_position)
				await _shot("the_tour_the_guesthouse", 0.6)
			_pilot.duty(path).interact(p)
			await get_tree().create_timer(0.2).timeout
	await _until(func() -> bool: return Talk.history.any(func(h: Array) -> bool: return String(h[1]).contains("Don't let them in")), 40.0)
	var anselm := night.get_node(^"People/TourAnselm") as Node3D
	p.place(anselm.global_position + Vector3(0.0, 0.0, 1.6), 0.0)
	_look_at(p, anselm.global_position + Vector3.UP * 1.5)
	await _shot("anselm_dont_let_them_in", 0.3)
	print("m12 shots done")
	get_tree().quit()


func _look_at(p: Player, at: Vector3) -> void:
	var to := at - p.camera.global_position
	p.rotation.y = atan2(-to.x, -to.z)
	p.head.rotation.x = atan2(to.y, Vector2(to.x, to.z).length())


func _until(cond: Callable, limit: float) -> void:
	var t := 0.0
	while not cond.call() and t < limit:
		await get_tree().process_frame
		t += get_process_delta_time()


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
