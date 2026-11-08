extends Node
## Stills of M8's frame through the full render pipeline, to art/_review/m8/
## (tools/m8_shots.sh): the title, settings, a chapter card, the outline and
## the duty glyph at dusk on night 3, the satchel, the pause menu, crouching
## and leaning, a death, the chronicle and chapter select.

const OUT := "res://art/_review/m8/"

var _n := 0
var _main: Node
var _flow: GameFlow


func _ready() -> void:
	GameState.save_path = "user://m8_shots_save.tres"
	Settings.path = "user://m8_shots_settings.cfg"
	Talk.line_seconds = 2.0
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	_main = load("res://game/render/main.tscn").instantiate()
	add_child(_main)
	_flow = _main.get_node(^"Game")
	_flow.card.seconds = 600.0
	await get_tree().process_frame
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	await _shot("title", 1.0)
	_flow.settings.open()
	_flow.title.close()
	await _shot("settings", 0.5)
	_flow.settings.close()

	# A chapter card, then night 3 at dusk.
	GameState.new_game()
	var night3 := _flow.chapters.index_of(&"night3")
	_flow.start_chapter(night3, false)
	await _shot("chapter_card", 1.0)
	_flow.card.call(&"_finish")
	await get_tree().create_timer(4.0).timeout
	var night: Node = _main.get(&"current_level")
	var pilot := NightPilot.new(night, func(_ok: bool, _what: String) -> void: pass)
	pilot.clock().set_pace(3600.0, 1.0)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var p := pilot.player
	p.place(Vector3(-34.0, 0.05, -10.3), deg_to_rad(-100.0))
	pilot.face(Vector3(-33.25, 0.95, -10.5))
	await _shot("outline_candle_clock", 0.8)
	p.place(Vector3(-34, 0.05, -2.6), 0.0)
	p.head.rotation.x = deg_to_rad(-8.0)
	await _shot("outline_cell_door", 0.8)
	pilot.skip_to(17.25)
	var seat := pilot.duty("SupperSeat")
	while not seat.enabled:
		await get_tree().process_frame
	p.place(seat.global_position + Vector3(0.6, 0, 3.0), 0.0)
	pilot.face(seat.glyph_point() + Vector3(0, -0.5, 0))
	await _shot("duty_glyph_supper_seat", 1.0)
	GameState.satchel.assign([&"apple", &"stone"])
	(_main.get_node(^"UI/Satchel") as SatchelView).set_showing(true)
	await _shot("satchel", 0.5)
	(_main.get_node(^"UI/Satchel") as SatchelView).set_showing(false)
	_flow.open_pause()
	await _shot("pause", 0.5)
	_flow.resume()
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE

	# Crouched behind a refectory table; leaning out of a doorway.
	p.place(Vector3(-2.0, 0.05, 1.6), 0.0)
	p.crouch_override = true
	await _shot("crouched", 1.0)
	p.crouch_override = false
	var cell_door: Door = null
	for d: Door in get_tree().get_nodes_in_group(&"doors"):
		if cell_door == null or d.global_position.distance_to(Vector3(-34, 0, -3.4)) < cell_door.global_position.distance_to(Vector3(-34, 0, -3.4)):
			cell_door = d
	cell_door.set_open(true, true)
	p.place(Vector3(-33.2, 0.05, -4.4), PI)
	p.lean_override = 1.0
	await _shot("leaning", 1.0)
	p.lean_override = 0.0

	# A death: the cord, the view on the floor.
	var flow: CaptureFlow = _main.get_node(^"CaptureFlow")
	p.place(Vector3(-30.0, 0.05, 2.0), deg_to_rad(90.0))
	flow.die(&"cord", night.get_node(^"Hunter") as Node3D)
	await _shot("death_falling", 1.15)
	await get_tree().create_timer(4.0).timeout

	# The chronicle, and chapter select.
	_main.call(&"unload_level")
	_flow.chronicle.show_ending(Endings.title(&"broken_rite"), Endings.chronicle(&"broken_rite"), Endings.last_line(&"broken_rite"))
	await _shot("chronicle", 1.0)
	_flow.chronicle.call(&"_finish")
	Settings.finished = true
	_flow.show_title()
	await _shot("title_finished", 0.5)
	_flow.title.close()
	_flow.chapter_select.open()
	await _shot("chapter_select", 0.5)
	for path in [GameState.save_path, GameState.quiet_path(), Settings.path]:
		DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
	print("m8 shots done")
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
