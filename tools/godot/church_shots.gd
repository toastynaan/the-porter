extends Node
## Stills of the church through the full render pipeline,
## to art/_review/church/ (tools/church_shots.sh): night 3 (a clear
## night), from a camera of the tool's own, at dusk and after dark. For the
## look of the place: the clock stands still and nobody is spoken to. A
## still marked `lantern` has the porter standing at the camera with his
## lantern, as the place is seen in play. Taken at the window's own size.

const OUT := "res://art/_review/church/"
const DAY := 15.5
const DUSK := 16.6
const NIGHT := 22.0
## Each still: its name, the hour, where the camera is and what it looks at.
const SHOTS := [
	# The first thirty make the contact sheet (tools/church_shots.sh tiles 6 by 5).
	{"name": "nave_east", "hour": NIGHT, "eye": Vector3(-17.0, 1.65, -32.0), "at": Vector3(28.0, 6.5, -32.0), "lantern": true},
	{"name": "nave_east_dusk", "hour": DUSK, "eye": Vector3(-17.0, 1.65, -32.0), "at": Vector3(28.0, 6.5, -32.0)},
	{"name": "nave_lit", "hour": NIGHT, "eye": Vector3(-17.0, 1.65, -32.0), "at": Vector3(28.0, 6.5, -32.0), "fill": true},
	{"name": "nave_west", "hour": NIGHT, "eye": Vector3(6.0, 1.65, -32.0), "at": Vector3(-20.0, 5.0, -32.0), "lantern": true},
	{"name": "vault", "hour": NIGHT, "eye": Vector3(-2.0, 1.65, -32.0), "at": Vector3(6.0, 16.0, -32.0), "lantern": true},
	{"name": "north_wall", "hour": NIGHT, "eye": Vector3(-6.0, 1.65, -29.4), "at": Vector3(0.0, 5.0, -36.0), "lantern": true},
	{"name": "north_wall_lit", "hour": NIGHT, "eye": Vector3(-6.0, 1.65, -29.4), "at": Vector3(2.0, 7.0, -36.0), "fill": true},
	{"name": "wall_tomb", "hour": NIGHT, "eye": Vector3(-8.2, 1.65, -33.6), "at": Vector3(-10.2, 0.9, -35.7), "lantern": true},
	{"name": "wall_tomb_lit", "hour": NIGHT, "eye": Vector3(-9.0, 1.65, -32.6), "at": Vector3(-10.2, 1.0, -35.7), "fill": true},
	{"name": "corona_crooked_lit", "hour": NIGHT, "eye": Vector3(-7.0, 1.65, -31.4), "at": Vector3(-2.0, 5.2, -32.0), "fill": true},
	{"name": "rood_and_choir", "hour": NIGHT, "eye": Vector3(1.0, 1.65, -32.0), "at": Vector3(28.0, 6.0, -32.0), "lantern": true},
	{"name": "rood_dusk", "hour": DUSK, "eye": Vector3(0.5, 1.65, -32.6), "at": Vector3(8.0, 7.4, -32.0)},
	{"name": "choir_lit", "hour": NIGHT, "eye": Vector3(9.0, 1.65, -32.0), "at": Vector3(28.0, 6.0, -32.0), "fill": true},
	{"name": "east_window", "hour": NIGHT, "eye": Vector3(18.0, 1.65, -32.0), "at": Vector3(28.0, 8.0, -32.0), "lantern": true},
	{"name": "east_niches", "hour": NIGHT, "eye": Vector3(25.3, 1.65, -33.9), "at": Vector3(27.6, 4.9, -34.8), "lantern": true},
	{"name": "east_niches_lit", "hour": NIGHT, "eye": Vector3(22.0, 1.65, -32.0), "at": Vector3(28.0, 6.0, -32.6), "fill": true},
	{"name": "altar", "hour": NIGHT, "eye": Vector3(21.5, 1.65, -31.0), "at": Vector3(27.0, 1.6, -32.2), "lantern": true},
	{"name": "night_stairs", "hour": NIGHT, "eye": Vector3(13.0, 1.65, -33.0), "at": Vector3(21.0, 3.0, -28.6), "lantern": true},
	{"name": "stair_figure", "hour": NIGHT, "eye": Vector3(19.6, 5.02, -29.0), "at": Vector3(16.6, 6.0, -28.4), "lantern": true},
	{"name": "stair_figure_landing", "hour": NIGHT, "eye": Vector3(18.1, 5.67, -29.1), "at": Vector3(16.6, 6.1, -28.5), "lantern": true},
	{"name": "upper_door_lit", "hour": NIGHT, "eye": Vector3(17.0, 5.4, -32.0), "at": Vector3(17.6, 5.2, -28.0), "fill": true},
	{"name": "crypt_stair", "hour": NIGHT, "eye": Vector3(15.5, 1.65, -32.5), "at": Vector3(22.0, 0.0, -35.0), "lantern": true},
	{"name": "tower_room_lit", "hour": NIGHT, "eye": Vector3(-21.4, 1.65, -29.4), "at": Vector3(-26.0, 6.0, -34.0), "fill": true},
	{"name": "tower_scratches", "hour": NIGHT, "eye": Vector3(-24.0, 1.65, -30.3), "at": Vector3(-24.4, 1.0, -28.4), "lantern": true},
	{"name": "tower_west_door", "hour": NIGHT, "eye": Vector3(-32.0, 1.65, -31.4), "at": Vector3(-28.4, 3.0, -30.0), "lantern": true},
	{"name": "graveyard_door", "hour": NIGHT, "eye": Vector3(26.6, 1.65, -23.6), "at": Vector3(25.6, 3.6, -28.0), "lantern": true},
	{"name": "graveyard_side", "hour": DUSK, "eye": Vector3(31.0, 1.65, -17.0), "at": Vector3(21.5, 10.0, -28.0)},
	{"name": "from_the_garth", "hour": DUSK, "eye": Vector3(4.0, 1.65, -10.5), "at": Vector3(-6.0, 9.0, -30.0)},
	{"name": "east_end", "hour": DAY, "eye": Vector3(37.5, 1.65, -34.0), "at": Vector3(28.0, 9.5, -32.0), "sun": true},
	{"name": "tower", "hour": DAY, "eye": Vector3(-38.6, 1.65, -27.0), "at": Vector3(-24.0, 15.0, -32.0), "sun": true},
	# More of the same, and ("x_") checks of the geometry from where nobody stands.
	{"name": "nave_east_dark", "hour": NIGHT, "eye": Vector3(-17.0, 1.65, -32.0), "at": Vector3(28.0, 6.5, -32.0)},
	{"name": "vault_lit", "hour": NIGHT, "eye": Vector3(-2.0, 1.65, -32.0), "at": Vector3(6.0, 16.0, -32.0), "fill": true},
	{"name": "a_window", "hour": NIGHT, "eye": Vector3(-2.0, 1.65, -30.0), "at": Vector3(-2.0, 8.5, -36.0), "fill": true},
	{"name": "blind_arcade", "hour": NIGHT, "eye": Vector3(-4.0, 1.65, -32.5), "at": Vector3(-1.0, 1.6, -36.0), "lantern": true},
	{"name": "lunette", "hour": NIGHT, "eye": Vector3(-2.0, 9.0, -30.0), "at": Vector3(-2.0, 13.5, -36.0), "fill": true},
	{"name": "tower_room", "hour": NIGHT, "eye": Vector3(-21.4, 1.65, -29.4), "at": Vector3(-26.0, 6.0, -34.0), "lantern": true},
	{"name": "tower_room_floor", "hour": NIGHT, "eye": Vector3(-21.4, 1.65, -29.4), "at": Vector3(-27.0, 0.5, -35.0), "lantern": true},
	{"name": "tower_west_door_dusk", "hour": DUSK, "eye": Vector3(-34.0, 1.65, -32.0), "at": Vector3(-28.4, 5.0, -30.0)},
	{"name": "nave_tower_door", "hour": NIGHT, "eye": Vector3(-17.5, 1.65, -30.6), "at": Vector3(-20.0, 0.6, -30.0), "lantern": true},
	{"name": "crypt_well", "hour": NIGHT, "eye": Vector3(21.5, -0.67, -34.8), "at": Vector3(19.0, 0.3, -35.7), "lantern": true},
	{"name": "graveyard_door_lit", "hour": NIGHT, "eye": Vector3(27.5, 1.65, -22.0), "at": Vector3(24.5, 5.0, -28.0), "fill": true},
	{"name": "graveyard_side_lit", "hour": DAY, "eye": Vector3(31.0, 1.65, -17.0), "at": Vector3(21.5, 10.0, -28.0), "sun": true},
	{"name": "from_the_garth_lit", "hour": DAY, "eye": Vector3(4.0, 1.65, -10.5), "at": Vector3(-6.0, 9.0, -30.0), "sun": true},
	{"name": "north_side", "hour": DAY, "eye": Vector3(33.0, 1.65, -38.6), "at": Vector3(10.0, 9.0, -36.4), "sun": true},
	{"name": "north_side_lantern", "hour": NIGHT, "eye": Vector3(-6.0, 1.65, -38.9), "at": Vector3(2.0, 3.5, -36.4), "lantern": true},
	{"name": "x_rood_lit", "hour": NIGHT, "eye": Vector3(1.0, 6.0, -31.0), "at": Vector3(8.0, 7.8, -32.0), "fill": true},
	{"name": "x_tower_slits", "hour": NIGHT, "eye": Vector3(-26.5, 1.65, -30.0), "at": Vector3(-20.0, 10.2, -33.0), "fill": true},
	{"name": "x_roof_east", "hour": DAY, "eye": Vector3(40.0, 25.0, -20.0), "at": Vector3(27.0, 18.0, -31.0), "sun": true},
	{"name": "x_roof_west", "hour": DAY, "eye": Vector3(-8.0, 27.0, -20.0), "at": Vector3(-20.0, 18.0, -32.0), "sun": true},
	{"name": "x_dorm_roof", "hour": DAY, "eye": Vector3(30.0, 14.0, -14.0), "at": Vector3(17.0, 10.5, -28.0), "sun": true},
	{"name": "x_west_roof", "hour": DAY, "eye": Vector3(-30.0, 11.0, -14.0), "at": Vector3(-17.0, 7.0, -28.0), "sun": true},
	{"name": "x_choir_south", "hour": NIGHT, "eye": Vector3(13.0, 1.65, -34.8), "at": Vector3(18.5, 8.5, -28.0), "fill": true},
	{"name": "x_dorm_gable", "hour": NIGHT, "eye": Vector3(16.0, 5.6, -20.0), "at": Vector3(16.0, 9.5, -28.0), "fill": true},
	{"name": "x_granary_gable", "hour": NIGHT, "eye": Vector3(-16.0, 1.65, -21.0), "at": Vector3(-16.0, 6.0, -28.0), "fill": true},
]

var _n := 0


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	Settings.subtitle_size = 1
	Settings.less_motion = false
	Settings.fov = 70.0
	Settings.apply()
	NightPilot.fresh_night("user://church_shots_save.tres")
	GameState.night = 3
	GameState.chapter = 4
	var main := NightPilot.main_with("res://game/nights/night3.tscn")
	add_child(main)
	var night: Node = main.get(&"current_level")
	await get_tree().create_timer(1.0).timeout
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var pilot := NightPilot.new(night, func(_ok: bool, _w: String) -> void: pass)
	(night.get_node(^"Hallucinations") as Hallucinations).active = false
	pilot.clock().set_pace(1.0e9, 1.0e9)
	Talk.view.visible = false
	var sun: DirectionalLight3D = night.get_node(^"Daylight").get(&"_sun")
	var ui := main.get_node_or_null(^"UI") as CanvasLayer
	if ui:
		ui.visible = false
	var cam := Camera3D.new()
	cam.fov = 65.0
	night.add_child(cam)
	cam.current = true
	var fill := OmniLight3D.new()
	fill.omni_range = 40.0
	fill.light_energy = 2.0
	fill.light_color = Color(1.0, 0.85, 0.65)
	fill.shadow_enabled = true
	night.add_child(fill)
	var only := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--only="):
			only = arg.trim_prefix("--only=")
	for shot: Dictionary in SHOTS:
		_n += 1
		if only != "" and not String(shot["name"]).contains(only):
			continue
		GameState.hour = float(shot["hour"])
		cam.global_position = shot["eye"]
		cam.look_at(shot["at"] as Vector3)
		var lit: bool = shot.get("lantern", false)
		pilot.player.lantern.visible = lit
		# With the lantern, he stands where the camera is; without, out of the way.
		var eye: Vector3 = shot["eye"]
		pilot.player.global_position = Vector3(eye.x, eye.y - 1.59, eye.z) if lit else Vector3(-33.0, 0.06, 2.0)
		pilot.player.velocity = Vector3.ZERO
		pilot.player.rotation = Vector3(0.0, cam.rotation.y, 0.0)
		# "sun": a look to weigh, not in the game: the low sun warm and casting shadows.
		# "fill": a plain lamp at the camera, to judge the stonework; not in the game.
		fill.visible = shot.get("fill", false)
		fill.global_position = eye + Vector3(0.0, 2.0, 0.0)
		get_viewport().debug_draw = Viewport.DEBUG_DRAW_UNSHADED if shot.get("flat", false) else Viewport.DEBUG_DRAW_DISABLED
		var low: bool = shot.get("sun", false)
		sun.shadow_enabled = low
		sun.light_color = Color(1.0, 0.78, 0.5) if low else (night.get_node(^"Daylight").get(&"moon") as DirectionalLight3D).light_color
		night.get_node(^"Daylight").set(&"day_sun", 1.6 if low else 0.4)
		await get_tree().create_timer(1.6).timeout
		await RenderingServer.frame_post_draw
		var path := OUT + "%02d_%s.png" % [_n, String(shot["name"])]
		get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path(path))
		print("wrote ", path)
	print("church shots done")
	get_tree().quit()
