extends Node
## Stills of M10's drug and dark through the full render pipeline, to
## art/_review/m10/ (tools/m10_shots.sh): one view of the cloister and a
## carved saint at Dose 0, 25, 50, 75 and 100; then each event: a shape at
## the edge of view, a face in the grain, the dead in the choir, a death
## that never happened, the HUD's one lie, the candle that lights itself,
## the cat staring, a body dropping, a face at the grille.

const OUT := "res://art/_review/m10/"

var _n := 0
var _main: Node
var _pilot: NightPilot


func _ready() -> void:
	NightPilot.fresh_night("user://m10_shots_save.tres")
	GameState.night = 5
	Talk.line_seconds = 3.0
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	_main = NightPilot.main_with("res://game/dev/encounters/death_demo.tscn")
	add_child(_main)
	await get_tree().create_timer(1.0).timeout
	GameState.hour = 22.0
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	_pilot = NightPilot.new(_main.get(&"current_level"), func(_ok: bool, _w: String) -> void: pass)
	var night := _pilot.night
	var p := _pilot.player
	var h: Hallucinations = night.get_node(^"Hallucinations")
	h.active = false
	# One view at each Dose: Matins in the choir, the brothers in their
	# places, a carved saint at the end; the dead brother in the stranger's place.
	GameState.set_flag(&"died_edwin")
	GameState.set_phase(GameState.Phase.MATINS)
	for d in [0.0, 25.0, 50.0, 75.0, 100.0]:
		GameState.snap_dose(d)
		GameState.dose_floor = d
		p.place(Vector3(8.6, 0.05, -31.4), deg_to_rad(-90.0))
		_pilot.face(p.global_position + Vector3(-10, 0, 0))
		await get_tree().create_timer(0.3).timeout
		_pilot.face(Vector3(17.0, 1.2, -33.0))
		await _shot("dose_%03d" % int(d), 1.5)
	GameState.set_phase(GameState.Phase.ROUND)
	GameState.flags.erase(&"died_edwin")
	for b: Brother in get_tree().get_nodes_in_group(&"brothers"):
		b.place(null)

	# A shape at the edge of view.
	GameState.snap_dose(60.0)
	GameState.dose_floor = 60.0
	p.place(Vector3(0.0, 0.05, -16.0), 0.0)
	if h.fire(&"edge_shape"):
		var shape := h.get_child(h.get_child_count() - 1) as Node3D
		var to := shape.global_position - p.global_position
		p.rotation.y = lerp_angle(p.rotation.y, atan2(-to.x, -to.z), 0.45)
	await _shot("edge_shape", 0.3)
	# A face in the grain.
	p.place(Vector3(-34, 0.05, -1.6), PI)
	h.fire(&"face_in_grain")
	for d: Door in get_tree().get_nodes_in_group(&"doors"):
		for c in d.get_children():
			if c is Decal:
				_pilot.face((c as Decal).global_position)
	await _shot("face_in_grain", 0.6)

	# The dead in the choir.
	GameState.snap_dose(85.0)
	GameState.dose_floor = 85.0
	GameState.set_flag(&"died_edwin")
	GameState.set_flag(&"died_choira")
	GameState.set_phase(GameState.Phase.MATINS)
	p.place(Vector3(12.0, 0.05, -32.0), deg_to_rad(-90.0))
	_pilot.face(p.global_position + Vector3(-10, 0, 0))
	await get_tree().create_timer(0.3).timeout
	_pilot.face(Vector3(14.0, 1.2, -34.6))
	await _shot("dead_in_the_choir", 1.0)
	GameState.set_phase(GameState.Phase.ROUND)

	# A death that never happened.
	p.place(Vector3(0.0, 0.05, -26.0), deg_to_rad(-90.0))
	h.fire(&"fake_death")
	await _shot("fake_death", 1.6)

	# The HUD's one lie.
	var false_door: FalseDoor = night.get_node(^"FalseDoor")
	p.place(false_door.global_position + Vector3(1.9, 0, 0.6), 0.0)
	_pilot.face(false_door.global_position + Vector3(0, 1.0, 0))
	await _shot("hud_lie_door_in_the_wall", 1.0)

	# The candle that lights itself.
	GameState.snap_dose(0.0)
	GameState.dose_floor = 0.0
	var candle: SelfLitCandle = night.get_node(^"SelfLitCandle")
	p.place(candle.global_position + Vector3(-2.2, 0.0, -0.6), 0.0)
	_pilot.face(candle.candle.global_position + Vector3.UP * 0.1)
	await _shot("candle_lights_itself", 1.6)

	# The cat stares; a body drops; a face at the grille.
	var cat: Cat = night.get_node(^"Cat")
	p.place(Vector3(-30.0, 0.05, 6.0), PI)
	cat.global_position = p.global_position + Vector3(1.2, 0, 1.8)
	await get_tree().create_timer(0.3).timeout
	cat.stare()
	_pilot.face(cat.global_position + Vector3(0, 0.2, 0))
	await _shot("cat_stares", 0.5)
	var scares: Scares = night.get_node(^"Scares")
	p.place(Vector3(-10.0, 0.05, -16.0), 0.0)
	p.head.rotation.x = deg_to_rad(5.0)
	scares.jump(&"body_drop")
	await _shot("body_drops", 0.45)
	GameState.flags.erase(&"jump_scare")
	p.place(Vector3(-37.6, 0.05, -2.0), deg_to_rad(90.0))
	scares.jump(&"face_at_grille")
	await _shot("face_at_the_grille", 0.3)
	DirAccess.remove_absolute(ProjectSettings.globalize_path(GameState.save_path))
	print("m10 shots done")
	get_tree().quit()


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
