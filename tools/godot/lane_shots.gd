extends Node
## Stills of the lane outside the abbey gate through the full render
## pipeline, to art/_review/lane/ (tools/lane_shots.sh): night 1, from a
## camera of the tool's own, at dusk and after dark. For the look of the
## place: the clock stands still and nobody is spoken to. Taken at the
## window's own size.

const OUT := "res://art/_review/lane/"
## Each still: its name, the hour, where the camera is and what it looks at.
const SHOTS := [
	{"name": "from_the_gate_north", "hour": 17.3, "eye": Vector3(-43.6, 1.65, 1.5), "at": Vector3(-44.6, 3.2, 30.0)},
	{"name": "from_the_gate_south", "hour": 17.3, "eye": Vector3(-43.6, 1.65, -9.0), "at": Vector3(-44.6, 3.2, -40.0)},
	{"name": "houses_south", "hour": 17.3, "eye": Vector3(-41.2, 1.65, -18.0), "at": Vector3(-47.0, 3.6, -30.0)},
	{"name": "houses_north", "hour": 17.3, "eye": Vector3(-41.2, 1.65, 14.0), "at": Vector3(-47.0, 3.6, 27.0)},
	{"name": "a_door", "hour": 17.3, "eye": Vector3(-42.4, 1.6, -25.0), "at": Vector3(-46.6, 1.9, -29.0)},
	{"name": "north_end", "hour": 17.3, "eye": Vector3(-43.6, 1.65, 33.0), "at": Vector3(-43.4, 3.0, 50.0)},
	{"name": "north_arch", "hour": 17.3, "eye": Vector3(-43.5, 1.65, 44.5), "at": Vector3(-43.4, 2.0, 60.0)},
	{"name": "north_bend", "hour": 17.3, "eye": Vector3(-45.0, 1.65, 47.2), "at": Vector3(-71.0, 2.6, 47.0)},
	{"name": "south_end", "hour": 17.3, "eye": Vector3(-43.2, 1.65, -34.0), "at": Vector3(-43.4, 3.0, -50.0)},
	{"name": "alley", "hour": 17.3, "eye": Vector3(-44.0, 1.65, 15.2), "at": Vector3(-57.0, 1.6, 15.0)},
	{"name": "over_the_roofs", "hour": 17.3, "eye": Vector3(-33.0, 11.0, -22.0), "at": Vector3(-47.0, 3.0, 4.0)},
	{"name": "early_from_the_gate", "hour": 16.2, "eye": Vector3(-43.6, 1.65, 1.5), "at": Vector3(-44.6, 3.2, 30.0)},
	{"name": "early_south_end", "hour": 16.2, "eye": Vector3(-43.2, 1.65, -30.0), "at": Vector3(-43.6, 3.4, -50.0)},
	{"name": "night_from_the_gate", "hour": 22.0, "eye": Vector3(-43.6, 1.65, 1.5), "at": Vector3(-44.6, 3.2, 30.0)},
	{"name": "night_north_arch", "hour": 22.0, "eye": Vector3(-43.5, 1.65, 42.0), "at": Vector3(-43.4, 2.2, 60.0)},
	{"name": "night_houses_south", "hour": 22.0, "eye": Vector3(-41.2, 1.65, -8.0), "at": Vector3(-47.0, 3.6, -24.0)},
]

var _n := 0


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	Settings.subtitle_size = 1
	Settings.less_motion = false
	Settings.fov = 70.0
	Settings.apply()
	NightPilot.fresh_night("user://lane_shots_save.tres")
	GameState.night = 1
	GameState.chapter = 2
	var main := NightPilot.main_with("res://game/nights/night1.tscn")
	add_child(main)
	var night: Node = main.get(&"current_level")
	await get_tree().create_timer(1.0).timeout
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var pilot := NightPilot.new(night, func(_ok: bool, _w: String) -> void: pass)
	(night.get_node(^"Hallucinations") as Hallucinations).active = false
	pilot.clock().set_pace(1.0e9, 1.0e9)
	pilot.player.lantern.visible = false
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
		await get_tree().create_timer(1.6).timeout
		await RenderingServer.frame_post_draw
		var path := OUT + "%02d_%s.png" % [_n, String(shot["name"])]
		get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path(path))
		print("wrote ", path)
	print("lane shots done")
	get_tree().quit()
