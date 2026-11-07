extends Node
## Plays night 3 with the test pilot and captures a still at each beat
## through the full render pipeline, subtitles and all, to
## art/_review/m4/ (tools/night3_shots.sh).

const OUT := "res://art/_review/m4/"

var _pilot: NightPilot
var _n := 0


func _ready() -> void:
	NightPilot.fresh_night("user://night3_shots_save.tres")
	Talk.line_seconds = 2.0
	Talk.auto_choice = func(_options: PackedStringArray) -> int: return 0
	var main: Node = load("res://game/render/main.tscn").instantiate()
	add_child(main)
	await get_tree().process_frame
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	_pilot = NightPilot.new(main.get(&"current_level"), func(ok: bool, what: String) -> void:
		if not ok:
			print("pilot: ", what))
	_pilot.shorten()
	var p := _pilot.player
	var night := _pilot.night

	await _pilot.until(func() -> bool: return _pilot.duty("Bread").enabled, 15.0)
	_pilot.face(_pilot.duty("Bread").global_position + Vector3(0.4, 0.6, -0.6))
	await _shot("supper")
	_pilot.duty("Bread").interact(p)
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Gate", 30.0)
	# The way to the gate: lit doorways through the kitchen, the lamp at the end.
	p.place(Vector3(-4, 0.05, -3.1), deg_to_rad(90.0))
	await _shot("way_to_gate", 1.0)
	p.place(Vector3(-36, 0.05, -2), deg_to_rad(90.0))
	await _pilot.use("BarGate")
	await _pilot.use("Ledger")
	GameState.snap_dose(55.0)
	await _pilot.until(func() -> bool: return _pilot.duty("Grate").enabled, 15.0)
	p.place(Vector3(-37.2, 0.05, -2), deg_to_rad(90.0))
	_pilot.duty("Grate").interact(p)
	await _shot("knock_walter", 0.6)
	# Drugged, the child-sized knock follows.
	await _pilot.use("Grate")
	await _shot("knock_no_one", 0.4)
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Bell", 30.0)
	# The way to the bell: a lamp over the tower door, seen across the court.
	p.place(Vector3(-38.5, 0.05, -25.5), 0.0)
	_pilot.face(Vector3(-28, 1.6, -30))
	await _shot("way_to_bell", 1.0)
	p.place(Vector3(-24, 0.05, -30.8), 0.0)
	_pilot.face(Vector3(-24, 1.4, -32))
	await _pilot.use("BellRope")
	await _shot("matins_bell", 0.4)
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
	_pilot.face(hunter.global_position + Vector3.UP * 1.7)
	await _shot("spotted", 0.0)
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
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Dawn", 10.0)
	await _pilot.seconds(3.0)
	_pilot.face(_pilot.duty("KeysMoved").global_position)
	await _shot("dawn_keys", 0.3)
	print("night 3 shots: rescued %s, captures %d" % [GameState.has_flag(&"n3_thomas_hid_you"), GameState.captures])
	get_tree().quit()


## The first and last appearances on the round, as he faces them.
func _on_seen(stalker: Stalker) -> void:
	if stalker.appearances == 1:
		await _shot("demon_walk_end", 0.1)
	elif stalker.final:
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
