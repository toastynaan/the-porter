extends Node
## Stills of the road in (night 0) through the full render pipeline, to
## art/_review/intro/ (tools/intro_shots.sh): the wagon is put at set places
## along the road at set hours, and the porter looks where each still says.
## No cues, no talk: this is for the look of the place. Taken at the window's
## own size.

const OUT := "res://art/_review/intro/"
## Each still: its name, metres along the road, the hour, and where he
## looks: a point in the world, or a direction from his eyes if `dir`.
const SHOTS := [
	{"name": "back_down_the_road", "along": 25.0, "hour": 16.5, "dir": Vector3(-1.0, 0.02, 0.05)},
	{"name": "ahead_past_the_carter", "along": 25.0, "hour": 16.5, "dir": Vector3(1.0, 0.0, -0.45)},
	{"name": "the_white_chapel_coming", "along": 28.0, "hour": 16.54, "at": Vector3(-186.0, 4.5, 64.0)},
	{"name": "the_white_chapel", "along": 46.0, "hour": 16.6, "at": Vector3(-185.0, 4.0, 64.0)},
	{"name": "the_chapel_behind", "along": 68.0, "hour": 16.72, "at": Vector3(-186.0, 3.5, 62.0)},
	{"name": "the_fields_north", "along": 58.0, "hour": 16.66, "dir": Vector3(-0.3, 0.0, -1.0)},
	{"name": "rooks_over_the_oak", "along": 72.0, "hour": 16.75, "at": Vector3(-151.0, 13.0, 27.5)},
	{"name": "back_from_the_wall", "along": 96.0, "hour": 16.88, "dir": Vector3(-1.0, 0.03, -0.12)},
	{"name": "the_wall_ahead", "along": 88.0, "hour": 16.84, "dir": Vector3(1.0, 0.06, -0.3)},
	# From outside the wagon: a camera of the tool's own, `cam` metres from the wagon.
	{"name": "the_wagon_from_the_verge", "along": 42.0, "hour": 16.6, "cam": Vector3(4.5, 1.5, -5.0), "at": Vector3(0.0, 1.1, -1.4)},
	{"name": "the_wagon_from_behind", "along": 42.0, "hour": 16.6, "cam": Vector3(-1.5, 1.9, 5.5), "at": Vector3(0.0, 1.2, -1.0)},
	{"name": "the_road_from_above", "along": 52.0, "hour": 16.55, "cam": Vector3(-14.0, 16.0, 30.0), "at": Vector3(2.0, 0.0, -16.0)},
	# The wall and Aldgate. `eye` is a camera of the tool's own at a place in the world.
	{"name": "the_city_ahead", "along": 62.0, "hour": 16.7, "dir": Vector3(1.0, 0.07, -0.12)},
	{"name": "aldgate_coming", "along": 97.0, "hour": 16.88, "dir": Vector3(1.0, 0.16, -0.08)},
	{"name": "aldgate_at_the_stop", "along": 110.5, "hour": 16.92, "dir": Vector3(1.0, 0.42, -0.2)},
	{"name": "the_warden_side", "along": 110.5, "hour": 16.92, "dir": Vector3(0.8, 0.12, -1.0)},
	{"name": "the_ditch", "along": 104.0, "hour": 16.9, "dir": Vector3(0.45, -0.12, 1.0)},
	{"name": "under_the_arch", "along": 119.5, "hour": 16.95, "dir": Vector3(-1.0, 0.08, 0.02)},
	{"name": "aldgate_behind", "along": 131.0, "hour": 16.98, "dir": Vector3(-1.0, 0.3, 0.0)},
	{"name": "the_street_in", "along": 127.0, "hour": 16.98, "dir": Vector3(1.0, 0.12, 0.0)},
	{"name": "the_street_behind", "along": 152.0, "hour": 17.05, "dir": Vector3(-1.0, 0.14, 0.0)},
	{"name": "aldgate_from_the_verge", "along": 100.0, "hour": 16.88, "eye": Vector3(-141.0, 1.7, 38.5), "at": Vector3(-118.0, 7.5, 47.0)},
	{"name": "the_wall_northward", "along": 100.0, "hour": 16.88, "eye": Vector3(-137.0, 2.0, 60.0), "at": Vector3(-119.0, 6.0, 10.0)},
	{"name": "aldgate_from_the_fields", "along": 60.0, "hour": 16.75, "eye": Vector3(-178.0, 2.2, 30.0), "at": Vector3(-118.0, 9.0, 47.0)},
	{"name": "aldgate_from_inside", "along": 140.0, "hour": 17.0, "eye": Vector3(-104.0, 1.7, 47.6), "at": Vector3(-118.0, 6.0, 47.0)},
]

var _n := 0
var _main: Node
var _pilot: NightPilot


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	Settings.subtitle_size = 1
	Settings.subtitle_backing = false
	Settings.less_motion = false
	Settings.fov = 70.0
	Settings.apply()
	NightPilot.fresh_night("user://intro_shots_save.tres")
	GameState.night = 0
	GameState.chapter = 0
	_main = NightPilot.main_with("res://game/nights/night0.tscn")
	add_child(_main)
	var night: Node = _main.get(&"current_level")
	var ride := night.get_node(^"Director/Ride")
	# No cues: nothing is said, nobody starts a talk.
	ride.set(&"cues", null)
	ride.set(&"traveller_talk", null)
	await get_tree().create_timer(0.8).timeout
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	_pilot = NightPilot.new(night, func(_ok: bool, _w: String) -> void: pass)
	var p := _pilot.player
	(night.get_node(^"Hallucinations") as Hallucinations).active = false
	var clock := _pilot.clock()
	clock.set_pace(1.0e9, 1.0e9)
	await _pilot.until(func() -> bool: return p.riding != null, 5.0)
	# The ride comes up out of black.
	await get_tree().create_timer(4.5).timeout
	# The wagon stands where each still wants it.
	ride.set(&"pace_scale", 0.0001)
	ride.set(&"_hook_done", true)
	var only := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--only="):
			only = arg.trim_prefix("--only=")
	for shot: Dictionary in SHOTS:
		if only != "" and not String(shot["name"]).contains(only):
			_n += 1
			continue
		ride.set(&"_along", float(shot["along"]))
		ride.set(&"_v", 0.0)
		GameState.hour = float(shot["hour"])
		Talk.reset()
		await get_tree().create_timer(0.7).timeout
		if shot.has("eye"):
			var free := Camera3D.new()
			free.fov = 60.0
			night.add_child(free)
			free.global_position = shot["eye"]
			free.look_at(shot["at"] as Vector3)
			free.current = true
			await _shot(String(shot["name"]))
			p.camera.current = true
			free.queue_free()
			continue
		if shot.has("cam"):
			# In the wagon's own space (its front is -Z).
			var wagon := night.get_node(^"Wagon") as Node3D
			var outside := Camera3D.new()
			outside.fov = 55.0
			night.add_child(outside)
			outside.global_position = wagon.global_transform * (shot["cam"] as Vector3)
			outside.look_at(wagon.global_transform * (shot["at"] as Vector3))
			outside.current = true
			await _shot(String(shot["name"]))
			p.camera.current = true
			outside.queue_free()
			continue
		var eye := p.camera.global_position
		var at: Vector3 = eye + (shot["dir"] as Vector3) * 10.0 if shot.has("dir") else shot["at"]
		var to := at - eye
		p.rotation.y = atan2(-to.x, -to.z)
		p.head.rotation.x = atan2(to.y, Vector2(to.x, to.z).length())
		await _shot(String(shot["name"]))
	print("intro shots done")
	get_tree().quit()


func _shot(shot_name: String, settle := 1.2) -> void:
	await get_tree().create_timer(settle).timeout
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	_n += 1
	var path := OUT + "%02d_%s.png" % [_n, shot_name]
	img.save_png(ProjectSettings.globalize_path(path))
	print("wrote ", path)
