extends Node
## Stills of the three ranges through the full render pipeline,
## to art/_review/church/ (tools/ranges_shots.sh): night 3 (a clear
## night), from a camera of the tool's own, at dusk and after dark. For the
## look of the place: the clock stands still and nobody is spoken to. A
## still marked `lantern` has the porter standing at the camera with his
## lantern, as the place is seen in play. Taken at the window's own size.

const OUT := "res://art/_review/ranges/"
const DAY := 15.5
const DUSK := 16.6
const NIGHT := 22.0
## Each still: its name, the hour, where the camera is and what it looks at.
const SHOTS := [
	{"name": "refectory", "hour": NIGHT, "eye": Vector3(-10.5, 1.65, 0.0), "at": Vector3(12.0, 2.6, 0.0), "lantern": true},
	{"name": "refectory_lit", "hour": NIGHT, "eye": Vector3(-10.5, 1.65, 0.0), "at": Vector3(12.0, 3.0, 0.0), "fill": true},
	{"name": "refectory_roof_lit", "hour": NIGHT, "eye": Vector3(-6.0, 1.65, -2.6), "at": Vector3(4.0, 7.0, 1.5), "fill": true},
	{"name": "refectory_wall", "hour": NIGHT, "eye": Vector3(6.0, 1.65, 2.4), "at": Vector3(10.0, 2.2, -4.0), "lantern": true},
	{"name": "kitchen_lit", "hour": NIGHT, "eye": Vector3(-13.2, 1.65, 3.0), "at": Vector3(-18.0, 2.4, -3.0), "fill": true},
	{"name": "bakehouse", "hour": NIGHT, "eye": Vector3(-13.4, 1.65, 10.6), "at": Vector3(-18.5, 1.6, 7.0), "lantern": true},
	{"name": "chapter_house", "hour": NIGHT, "eye": Vector3(13.2, 1.65, -17.2), "at": Vector3(19.5, 2.0, -22.5), "lantern": true},
	{"name": "chapter_house_lit", "hour": NIGHT, "eye": Vector3(13.2, 1.65, -17.2), "at": Vector3(19.5, 2.2, -22.5), "fill": true},
	{"name": "slype", "hour": NIGHT, "eye": Vector3(12.9, 1.65, -26.0), "at": Vector3(20.0, 1.7, -26.0), "lantern": true},
	{"name": "day_stair", "hour": NIGHT, "eye": Vector3(12.8, 1.65, -12.8), "at": Vector3(18.5, 3.2, -14.2), "lantern": true},
	{"name": "day_stair_lit", "hour": NIGHT, "eye": Vector3(12.8, 1.65, -12.8), "at": Vector3(18.5, 3.2, -14.2), "fill": true},
	{"name": "warming_room_lit", "hour": NIGHT, "eye": Vector3(13.0, 1.65, -5.0), "at": Vector3(19.0, 1.8, -10.5), "fill": true},
	{"name": "undercroft", "hour": NIGHT, "eye": Vector3(16.0, 1.65, -3.0), "at": Vector3(16.0, 1.9, 12.0), "lantern": true},
	{"name": "undercroft_lit", "hour": NIGHT, "eye": Vector3(16.0, 1.65, -3.0), "at": Vector3(16.0, 2.0, 12.0), "fill": true},
	{"name": "dormitory", "hour": NIGHT, "eye": Vector3(16.0, 5.65, 10.5), "at": Vector3(16.0, 6.4, -28.0), "lantern": true},
	{"name": "dormitory_lit", "hour": NIGHT, "eye": Vector3(16.0, 5.65, 10.5), "at": Vector3(16.0, 6.8, -28.0), "fill": true},
	{"name": "dormitory_roof_lit", "hour": NIGHT, "eye": Vector3(14.0, 5.65, -4.0), "at": Vector3(18.5, 10.5, -12.0), "fill": true},
	{"name": "dormitory_north_lit", "hour": NIGHT, "eye": Vector3(16.0, 5.65, -18.0), "at": Vector3(17.0, 6.5, -28.0), "fill": true},
	{"name": "stair_head", "hour": NIGHT, "eye": Vector3(19.4, 5.65, -11.6), "at": Vector3(14.0, 3.0, -14.0), "lantern": true},
	{"name": "granary_lit", "hour": NIGHT, "eye": Vector3(-13.0, 1.65, -17.0), "at": Vector3(-18.5, 2.6, -26.0), "fill": true},
	{"name": "stores", "hour": NIGHT, "eye": Vector3(-13.0, 1.65, -11.0), "at": Vector3(-19.0, 1.6, -5.5), "lantern": true},
	{"name": "parlour", "hour": NIGHT, "eye": Vector3(-12.8, 1.65, -14.0), "at": Vector3(-20.0, 1.7, -14.0), "lantern": true},
	{"name": "from_the_garth", "hour": DAY, "eye": Vector3(-5.0, 1.65, -20.0), "at": Vector3(12.0, 6.5, -8.0), "sun": true},
	{"name": "from_the_garth_west", "hour": DAY, "eye": Vector3(5.0, 1.65, -12.0), "at": Vector3(-12.0, 5.0, -18.0), "sun": true},
	{"name": "east_side", "hour": DAY, "eye": Vector3(34.0, 6.0, -10.0), "at": Vector3(20.0, 5.5, -6.0), "sun": true},
	{"name": "south_side", "hour": DAY, "eye": Vector3(-2.0, 5.0, 20.0), "at": Vector3(-6.0, 4.5, 4.0), "sun": true},
	{"name": "from_above", "hour": DAY, "eye": Vector3(34.0, 30.0, 26.0), "at": Vector3(0.0, 4.0, -10.0), "sun": true},
]

var _n := 0


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	Settings.subtitle_size = 1
	Settings.less_motion = false
	Settings.fov = 70.0
	Settings.apply()
	NightPilot.fresh_night("user://ranges_shots_save.tres")
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
	print("ranges shots done")
	get_tree().quit()
