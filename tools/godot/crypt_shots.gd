extends Node
## Stills of the crypt and the passages through the full render pipeline,
## to art/_review/church/ (tools/crypt_shots.sh): night 3 (a clear
## night), from a camera of the tool's own, at dusk and after dark. For the
## look of the place: the clock stands still and nobody is spoken to. A
## still marked `lantern` has the porter standing at the camera with his
## lantern, as the place is seen in play. A still marked `void` is a check
## for holes, not a look: nothing is shaded and what is not there shows
## magenta. Taken at the window's own size.

const OUT := "res://art/_review/crypt/"
const DAY := 15.5
const DUSK := 16.6
const NIGHT := 22.0
## Each still: its name, the hour, where the camera is and what it looks at.
## Where the torch brackets are: stills marked `torches` light them, to weigh it (the game doesn't).
const TORCHES := [Vector3(-14, -1.9, -31.2), Vector3(-6, -1.9, -28.8), Vector3(2, -1.9, -31.2), Vector3(10, -1.9, -28.8), Vector3(-16.8, -1.9, -26.6),
	Vector3(20, -1.85, -28.9), Vector3(20, -1.85, -33.4), Vector3(27.2, -1.85, -32.75), Vector3(27.2, -1.85, -29.55)]
const SHOTS := [
	{"name": "passage_east", "hour": NIGHT, "eye": Vector3(-15.0, -2.35, -30.0), "at": Vector3(12.0, -2.4, -30.0), "lantern": true},
	{"name": "passage_east_torches", "hour": NIGHT, "eye": Vector3(-15.0, -2.35, -30.0), "at": Vector3(12.0, -2.4, -30.0), "torches": true},
	{"name": "passage_west_torches", "hour": NIGHT, "eye": Vector3(10.0, -2.35, -30.2), "at": Vector3(-20.0, -2.4, -30.0), "torches": true},
	{"name": "passage_wall", "hour": NIGHT, "eye": Vector3(-3.0, -2.35, -29.2), "at": Vector3(1.5, -2.2, -31.6), "lantern": true},
	{"name": "passage_lit", "hour": NIGHT, "eye": Vector3(-9.0, -2.35, -30.0), "at": Vector3(12.0, -2.2, -30.0), "fill": true},
	{"name": "crypt_door", "hour": NIGHT, "eye": Vector3(7.0, -2.35, -30.0), "at": Vector3(12.0, -2.6, -30.0), "lantern": true},
	{"name": "corner", "hour": NIGHT, "eye": Vector3(-13.0, -2.35, -30.0), "at": Vector3(-19.0, -2.3, -28.5), "lantern": true},
	{"name": "corner_torches", "hour": NIGHT, "eye": Vector3(-13.0, -2.35, -30.0), "at": Vector3(-19.0, -2.3, -28.5), "torches": true},
	{"name": "hidden_stair_foot", "hour": NIGHT, "eye": Vector3(-18.0, -2.35, -30.5), "at": Vector3(-18.2, -2.6, -24.0), "lantern": true},
	{"name": "hidden_stair_foot_lit", "hour": NIGHT, "eye": Vector3(-18.0, -2.35, -30.5), "at": Vector3(-18.2, -2.6, -24.0), "fill": true},
	{"name": "hidden_stair_down", "hour": NIGHT, "eye": Vector3(-18.8, 0.9, -20.4), "at": Vector3(-18.6, -3.6, -27.0), "lantern": true},
	{"name": "crypt_in", "hour": NIGHT, "eye": Vector3(13.0, -2.35, -30.2), "at": Vector3(27.0, -2.6, -31.6), "lantern": true},
	{"name": "crypt_in_torches", "hour": NIGHT, "eye": Vector3(13.0, -2.35, -30.2), "at": Vector3(27.0, -2.6, -31.6), "torches": true},
	{"name": "crypt_in_lit", "hour": NIGHT, "eye": Vector3(13.0, -2.35, -30.2), "at": Vector3(27.0, -2.4, -31.6), "fill": true},
	{"name": "crypt_west_torches", "hour": NIGHT, "eye": Vector3(26.8, -2.35, -29.4), "at": Vector3(13.0, -2.5, -32.5), "torches": true},
	{"name": "crypt_vault", "hour": NIGHT, "eye": Vector3(18.0, -2.35, -31.0), "at": Vector3(22.5, -0.4, -31.3), "lantern": true},
	{"name": "tombs", "hour": NIGHT, "eye": Vector3(20.0, -2.35, -32.6), "at": Vector3(22.5, -3.2, -28.4), "lantern": true},
	{"name": "reliquary_niche", "hour": NIGHT, "eye": Vector3(23.0, -2.35, -31.2), "at": Vector3(28.0, -2.4, -31.2), "lantern": true},
	{"name": "stair_wall", "hour": NIGHT, "eye": Vector3(19.0, -2.35, -29.4), "at": Vector3(23.5, -2.5, -34.0), "lantern": true},
	{"name": "stair_foot", "hour": NIGHT, "eye": Vector3(26.4, -2.35, -32.2), "at": Vector3(24.6, -2.4, -35.2), "lantern": true},
	{"name": "stair_foot_lit", "hour": NIGHT, "eye": Vector3(26.4, -2.35, -32.2), "at": Vector3(24.6, -2.4, -35.2), "fill": true},
	{"name": "stair_up", "hour": NIGHT, "eye": Vector3(25.6, -2.35, -34.85), "at": Vector3(18.0, 0.6, -34.8), "lantern": true},
	{"name": "stair_down", "hour": NIGHT, "eye": Vector3(18.6, 1.2, -34.8), "at": Vector3(26.0, -3.6, -34.9), "lantern": true},
	{"name": "west_alcove", "hour": NIGHT, "eye": Vector3(15.0, -2.35, -31.5), "at": Vector3(14.0, -2.6, -35.4), "lantern": true},
	{"name": "west_end", "hour": NIGHT, "eye": Vector3(-14.2, -2.35, -30.0), "at": Vector3(-19.6, -2.3, -30.0), "lantern": true},
	{"name": "west_end_near", "hour": NIGHT, "eye": Vector3(-16.4, -2.35, -30.0), "at": Vector3(-19.6, -2.2, -30.0), "lantern": true},
	{"name": "ossuary", "hour": NIGHT, "eye": Vector3(-3.4, -2.35, -29.6), "at": Vector3(-2.0, -2.9, -31.6), "lantern": true},
	{"name": "empty_niche", "hour": NIGHT, "eye": Vector3(4.6, -2.35, -29.4), "at": Vector3(6.0, -2.8, -31.6), "lantern": true},
	{"name": "crosses", "hour": NIGHT, "eye": Vector3(-17.7, -2.35, -27.4), "at": Vector3(-17.35, -2.8, -25.0), "lantern": true},
	{"name": "stair_figure", "hour": NIGHT, "eye": Vector3(23.6, -2.08, -34.8), "at": Vector3(27.5, -2.6, -34.9), "lantern": true},
	{"name": "stair_figure_near", "hour": NIGHT, "eye": Vector3(25.4, -2.35, -34.85), "at": Vector3(27.6, -2.4, -34.9), "lantern": true},
	{"name": "tomb_effigy", "hour": NIGHT, "eye": Vector3(13.4, -2.35, -30.4), "at": Vector3(14.4, -3.4, -28.5), "lantern": true},
	{"name": "tomb_ajar", "hour": NIGHT, "eye": Vector3(20.9, -2.35, -30.0), "at": Vector3(21.9, -3.4, -28.5), "lantern": true},
	{"name": "hidden_stair_descent", "hour": NIGHT, "eye": Vector3(-18.8, -2.0, -24.5), "at": Vector3(-18.1, -2.9, -31.5), "lantern": true},
	{"name": "west_alcove_in", "hour": NIGHT, "eye": Vector3(15.6, -2.35, -34.9), "at": Vector3(12.4, -3.2, -34.9), "lantern": true},
	{"name": "soot_passage", "hour": NIGHT, "eye": Vector3(-14.6, -2.35, -29.4), "at": Vector3(-14.0, -1.6, -31.5), "lantern": true},
	{"name": "ring", "hour": NIGHT, "eye": Vector3(18.6, -2.35, -31.8), "at": Vector3(18.1, -3.0, -33.9), "lantern": true},
	{"name": "stains", "hour": NIGHT, "eye": Vector3(0.6, -2.35, -30.6), "at": Vector3(1.6, -2.7, -28.4), "lantern": true},
	{"name": "gap_hs_foot", "hour": NIGHT, "eye": Vector3(-18.8, -2.35, -26.0), "at": Vector3(-18.8, -1.0, -19.0), "void": true},
	{"name": "gap_hs_mid_up", "hour": NIGHT, "eye": Vector3(-18.8, -0.3, -22.0), "at": Vector3(-18.8, 0.9, -19.0), "void": true},
	{"name": "gap_hs_rim_n", "hour": NIGHT, "eye": Vector3(-18.8, -0.3, -22.0), "at": Vector3(-18.8, 0.0, -25.0), "void": true},
	{"name": "gap_cs_top", "hour": NIGHT, "eye": Vector3(18.4, 1.7, -34.8), "at": Vector3(24.0, -3.0, -34.8), "void": true},
	{"name": "gap_cs_rim_n", "hour": NIGHT, "eye": Vector3(21.0, -0.33, -34.6), "at": Vector3(21.6, 0.2, -35.6), "void": true},
	{"name": "gap_cs_rim_s", "hour": NIGHT, "eye": Vector3(21.0, -0.33, -35.0), "at": Vector3(21.6, 0.2, -34.1), "void": true},
	{"name": "gap_cs_arch", "hour": NIGHT, "eye": Vector3(22.5, -1.34, -34.8), "at": Vector3(24.0, -0.6, -34.8), "void": true},
	{"name": "gap_tomb", "hour": NIGHT, "eye": Vector3(13.4, -2.35, -30.4), "at": Vector3(14.4, -3.4, -28.5), "void": true},
]

var _n := 0


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	Settings.subtitle_size = 1
	Settings.less_motion = false
	Settings.fov = 70.0
	Settings.apply()
	NightPilot.fresh_night("user://crypt_shots_save.tres")
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
	fill.omni_range = 16.0
	fill.light_energy = 1.0
	fill.light_color = Color(1.0, 0.85, 0.65)
	fill.shadow_enabled = true
	night.add_child(fill)
	var torches: Array[OmniLight3D] = []
	for at: Vector3 in TORCHES:
		var lamp := OmniLight3D.new()
		lamp.omni_range = 7.0
		lamp.light_energy = 1.5
		lamp.light_color = Color(1.0, 0.62, 0.3)
		lamp.shadow_enabled = true
		night.add_child(lamp)
		lamp.global_position = at + Vector3(0.0, 0.5, 0.0)
		torches.append(lamp)
	# For stills marked `void`: no shading and a magenta nothing, so a hole in the model shows.
	var void_env := Environment.new()
	void_env.background_mode = Environment.BG_COLOR
	void_env.background_color = Color(1.0, 0.0, 1.0)
	void_env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	void_env.ambient_light_color = Color.WHITE
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
		fill.global_position = eye + Vector3(0.0, 0.6, 0.0)
		for lamp in torches:
			lamp.visible = shot.get("torches", false)
		var void_shot: bool = shot.get("void", false)
		cam.environment = void_env if void_shot else null
		get_viewport().debug_draw = Viewport.DEBUG_DRAW_UNSHADED if shot.get("flat", false) or void_shot else Viewport.DEBUG_DRAW_DISABLED
		var low: bool = shot.get("sun", false)
		sun.shadow_enabled = low
		sun.light_color = Color(1.0, 0.78, 0.5) if low else (night.get_node(^"Daylight").get(&"moon") as DirectionalLight3D).light_color
		night.get_node(^"Daylight").set(&"day_sun", 1.6 if low else 0.4)
		await get_tree().create_timer(1.6).timeout
		await RenderingServer.frame_post_draw
		var path := OUT + "%02d_%s.png" % [_n, String(shot["name"])]
		get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path(path))
		print("wrote ", path)
	print("crypt shots done")
	get_tree().quit()
