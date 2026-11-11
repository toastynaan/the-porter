extends Node
## Stills of the precinct (court, graveyard, outbuildings, gardens) through the full render pipeline,
## to art/_review/church/ (tools/precinct_shots.sh): night 3 (a clear
## night), from a camera of the tool's own, at dusk and after dark. For the
## look of the place: the clock stands still and nobody is spoken to. A
## still marked `lantern` has the porter standing at the camera with his
## lantern, as the place is seen in play. Taken at the window's own size.

const OUT := "res://art/_review/precinct/"
const DAY := 15.5
const DUSK := 16.6
const NIGHT := 22.0
## Each still: its name, the hour, where the camera is and what it looks at.
const SHOTS := [
	{"name": "court_from_the_gate", "hour": DAY, "eye": Vector3(-38.6, 1.65, -2.0), "at": Vector3(-20.0, 3.0, -4.0), "sun": true},
	{"name": "court_from_the_gate_night", "hour": NIGHT, "eye": Vector3(-38.6, 1.65, -2.0), "at": Vector3(-20.0, 3.0, -4.0), "lantern": true},
	{"name": "gate_inside", "hour": DAY, "eye": Vector3(-31.0, 1.65, 1.5), "at": Vector3(-40.0, 2.2, -3.0), "sun": true},
	{"name": "cell_and_guesthouse", "hour": DAY, "eye": Vector3(-24.0, 1.65, 2.0), "at": Vector3(-33.0, 3.0, -14.0), "sun": true},
	{"name": "guesthouse_door", "hour": NIGHT, "eye": Vector3(-29.0, 1.65, -11.5), "at": Vector3(-30.0, 2.2, -16.0), "lantern": true},
	{"name": "cell_lit", "hour": NIGHT, "eye": Vector3(-33.0, 1.65, -5.2), "at": Vector3(-38.5, 2.6, -10.5), "fill": true},
	{"name": "cell", "hour": NIGHT, "eye": Vector3(-33.0, 1.65, -5.2), "at": Vector3(-38.5, 1.6, -10.5), "lantern": true},
	{"name": "guesthouse_lit", "hour": NIGHT, "eye": Vector3(-25.0, 1.65, -17.2), "at": Vector3(-35.0, 2.6, -22.0), "fill": true},
	{"name": "court_south", "hour": DAY, "eye": Vector3(-36.0, 1.65, 12.0), "at": Vector3(-24.0, 2.5, 0.0), "sun": true},
	{"name": "graveyard", "hour": DAY, "eye": Vector3(23.0, 1.65, -8.0), "at": Vector3(36.0, 2.5, -22.0), "sun": true},
	{"name": "graveyard_night", "hour": NIGHT, "eye": Vector3(23.0, 1.65, -8.0), "at": Vector3(36.0, 2.5, -22.0), "lantern": true},
	{"name": "charnel_lit", "hour": NIGHT, "eye": Vector3(33.2, 1.65, -17.2), "at": Vector3(39.0, 1.8, -22.5), "fill": true},
	{"name": "infirmary_outside", "hour": DAY, "eye": Vector3(22.0, 1.65, -9.5), "at": Vector3(31.0, 3.0, -2.0), "sun": true},
	{"name": "infirmary_lit", "hour": NIGHT, "eye": Vector3(25.0, 1.65, 3.0), "at": Vector3(35.0, 2.6, -3.0), "fill": true},
	{"name": "mill_lit", "hour": NIGHT, "eye": Vector3(25.2, 1.65, 9.2), "at": Vector3(31.0, 2.4, 15.0), "fill": true},
	{"name": "mill_and_race", "hour": DAY, "eye": Vector3(18.0, 1.65, 23.0), "at": Vector3(29.0, 2.5, 13.0), "sun": true},
	{"name": "gardens", "hour": DAY, "eye": Vector3(-2.0, 1.65, 37.0), "at": Vector3(8.0, 1.0, 24.0), "sun": true},
	{"name": "south_yard", "hour": DAY, "eye": Vector3(-8.0, 1.65, 14.5), "at": Vector3(8.0, 3.0, 4.0), "sun": true},
	{"name": "north_strip", "hour": DAY, "eye": Vector3(-30.0, 1.65, -38.0), "at": Vector3(10.0, 6.0, -37.0), "sun": true},
	{"name": "from_above", "hour": DAY, "eye": Vector3(-48.0, 36.0, 44.0), "at": Vector3(0.0, 0.0, -4.0), "sun": true},
]

var _n := 0


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	Settings.subtitle_size = 1
	Settings.less_motion = false
	Settings.fov = 70.0
	Settings.apply()
	NightPilot.fresh_night("user://precinct_shots_save.tres")
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
	fill.omni_range = 24.0
	fill.light_energy = 1.4
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
		fill.global_position = eye + Vector3(0.0, 0.8, 0.0)
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
	print("precinct shots done")
	get_tree().quit()
