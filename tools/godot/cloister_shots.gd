extends Node
## Stills of the cloister and its garden through the full render pipeline,
## to art/_review/cloister/ (tools/cloister_shots.sh): night 3 (a clear
## night), from a camera of the tool's own, at dusk and after dark. For the
## look of the place: the clock stands still and nobody is spoken to. A
## still marked `lantern` has the porter standing at the camera with his
## lantern, as the place is seen in play. Taken at the window's own size.

const OUT := "res://art/_review/cloister/"
const DAY := 15.5
const DUSK := 16.6
const NIGHT := 22.0
## Each still: its name, the hour, where the camera is and what it looks at.
const SHOTS := [
	{"name": "day_north_walk", "hour": DAY, "eye": Vector3(-8.9, 1.65, -26.1), "at": Vector3(10.0, 2.1, -25.9)},
	{"name": "day_through_the_arcade", "hour": DAY, "eye": Vector3(-10.6, 1.6, -20.5), "at": Vector3(0.0, 1.6, -15.0)},
	{"name": "day_garth", "hour": DAY, "eye": Vector3(-6.3, 1.65, -10.2), "at": Vector3(4.0, 2.6, -22.0)},
	{"name": "day_low_sun", "hour": DAY, "eye": Vector3(8.9, 1.65, -25.4), "at": Vector3(9.6, 1.2, -6.0), "sun": true},
	{"name": "day_low_sun_garth", "hour": DAY, "eye": Vector3(6.4, 1.65, -21.6), "at": Vector3(-5.0, 2.2, -10.0), "sun": true},
	{"name": "north_walk", "hour": DUSK, "eye": Vector3(-8.9, 1.65, -26.1), "at": Vector3(10.0, 2.1, -25.9)},
	{"name": "west_walk", "hour": DUSK, "eye": Vector3(-10.2, 1.65, -25.0), "at": Vector3(-9.9, 2.0, -5.0)},
	{"name": "through_the_arcade", "hour": DUSK, "eye": Vector3(-10.6, 1.6, -20.5), "at": Vector3(0.0, 1.6, -15.0)},
	{"name": "tracery", "hour": DUSK, "eye": Vector3(-9.9, 1.6, -11.6), "at": Vector3(-8.0, 2.5, -9.8)},
	{"name": "vault", "hour": DUSK, "eye": Vector3(10.0, 1.65, -15.0), "at": Vector3(9.9, 4.2, -21.0)},
	{"name": "a_door", "hour": DUSK, "eye": Vector3(-9.0, 1.65, -11.6), "at": Vector3(-11.6, 1.7, -14.3)},
	{"name": "into_the_garth", "hour": DUSK, "eye": Vector3(-2.0, 1.65, -25.2), "at": Vector3(0.6, 1.0, -16.0)},
	{"name": "garth_north_east", "hour": DUSK, "eye": Vector3(-6.3, 1.65, -10.2), "at": Vector3(4.0, 2.6, -22.0)},
	{"name": "garth_south_west", "hour": DUSK, "eye": Vector3(6.4, 1.65, -21.6), "at": Vector3(-5.0, 2.2, -10.0)},
	{"name": "the_basin", "hour": DUSK, "eye": Vector3(2.9, 1.6, -13.2), "at": Vector3(0.0, 1.1, -16.0)},
	{"name": "the_beds", "hour": DUSK, "eye": Vector3(0.4, 1.65, -9.4), "at": Vector3(4.6, 0.3, -13.4)},
	{"name": "arcade_from_the_garth", "hour": DUSK, "eye": Vector3(1.5, 1.65, -17.5), "at": Vector3(-8.0, 2.6, -12.0)},
	{"name": "from_above", "hour": DUSK, "eye": Vector3(1.0, 17.0, 1.0), "at": Vector3(0.0, 0.0, -16.0)},
	{"name": "night_north_walk", "hour": NIGHT, "eye": Vector3(-8.9, 1.65, -26.1), "at": Vector3(10.0, 2.1, -25.9), "lantern": true},
	{"name": "night_through_the_arcade", "hour": NIGHT, "eye": Vector3(-10.6, 1.6, -20.5), "at": Vector3(0.0, 1.6, -15.0), "lantern": true},
	{"name": "night_garth_dark", "hour": NIGHT, "eye": Vector3(-6.3, 1.65, -10.2), "at": Vector3(4.0, 2.6, -22.0)},
	{"name": "night_garth_lantern", "hour": NIGHT, "eye": Vector3(-6.3, 1.65, -10.2), "at": Vector3(4.0, 2.6, -22.0), "lantern": true},
	{"name": "night_the_basin", "hour": NIGHT, "eye": Vector3(2.9, 1.6, -13.2), "at": Vector3(0.0, 1.1, -16.0), "lantern": true},
	{"name": "night_east_walk_dark", "hour": NIGHT, "eye": Vector3(10.0, 1.65, -25.0), "at": Vector3(9.9, 1.9, -5.0)},
	{"name": "night_vault", "hour": NIGHT, "eye": Vector3(10.0, 1.65, -15.0), "at": Vector3(9.9, 4.2, -21.0), "lantern": true},
]

var _n := 0


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	Settings.subtitle_size = 1
	Settings.less_motion = false
	Settings.fov = 70.0
	Settings.apply()
	NightPilot.fresh_night("user://cloister_shots_save.tres")
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
		pilot.player.global_position = Vector3(eye.x, 0.06, eye.z) if lit else Vector3(-33.0, 0.06, 2.0)
		pilot.player.velocity = Vector3.ZERO
		pilot.player.rotation = Vector3(0.0, cam.rotation.y, 0.0)
		# "sun": a look to weigh, not in the game: the low sun warm and casting shadows.
		var low: bool = shot.get("sun", false)
		sun.shadow_enabled = low
		sun.light_color = Color(1.0, 0.78, 0.5) if low else (night.get_node(^"Daylight").get(&"moon") as DirectionalLight3D).light_color
		night.get_node(^"Daylight").set(&"day_sun", 1.6 if low else 0.4)
		await get_tree().create_timer(1.6).timeout
		await RenderingServer.frame_post_draw
		var path := OUT + "%02d_%s.png" % [_n, String(shot["name"])]
		get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path(path))
		print("wrote ", path)
	print("cloister shots done")
	get_tree().quit()
