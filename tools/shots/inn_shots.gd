extends Node
## Stills inside the Cross Keys (game/world/street/env_inn.tscn) through the
## full render pipeline, to art/_review/inn/ (tools/shots/inn_shots.sh):
## night 0 from the `Inn` beat, Hob, Agnes and the drinkers in, at 20:00
## with the clock stopped. The porter stands where each still says and
## looks at a point; both are in the inn's own space (its front faces -Z,
## the origin on the ground at the middle of its front). No talk, no
## duty marker: this is for the look of the place. A still whose name ends
## "_lamp" adds a plain lamp at his eye, which the game doesn't have (the
## upper floors are unlit), to see what is there.

const OUT := "res://art/_review/inn/"
const INN := ^"Abbey/Street/Houses/Inn"
## Each still: its name, where his feet are and what he looks at (the inn's space).
const SHOTS := [
	{"name": "door_looking_in", "feet": Vector3(0.0, 0.0, 0.75), "at": Vector3(-0.7, 0.9, 9.0)},
	{"name": "hearth_corner", "feet": Vector3(-3.5, 0.0, 6.5), "at": Vector3(-0.9, 0.3, 9.0)},
	{"name": "hearth_right", "feet": Vector3(-0.4, 0.0, 6.9), "at": Vector3(1.1, 0.5, 9.5)},
	{"name": "counter", "feet": Vector3(2.0, 0.0, 5.5), "at": Vector3(4.1, 0.85, 8.2)},
	{"name": "behind_the_bar", "feet": Vector3(2.2, 0.0, 8.3), "at": Vector3(5.2, 0.4, 8.0)},
	{"name": "stair_foot", "feet": Vector3(-4.2, 0.0, 9.4), "at": Vector3(-5.4, 0.8, 7.9)},
	{"name": "loft", "feet": Vector3(-0.4, 3.0, 5.4), "at": Vector3(3.6, 3.35, 8.6)},
	{"name": "loft_lamp", "feet": Vector3(-0.4, 3.0, 5.4), "at": Vector3(3.6, 3.35, 8.6), "lamp": true},
	{"name": "loft_front_lamp", "feet": Vector3(1.0, 3.0, 5.2), "at": Vector3(-1.2, 3.0, 1.2), "lamp": true},
	{"name": "porter_room_bed", "feet": Vector3(2.3, 6.0, 4.05), "at": Vector3(4.7, 6.35, 2.6)},
	{"name": "porter_room_window", "feet": Vector3(1.6, 6.0, 3.2), "at": Vector3(4.0, 7.0, 0.9)},
	{"name": "porter_room_back", "feet": Vector3(4.2, 6.0, 1.5), "at": Vector3(1.5, 7.0, 4.2)},
	{"name": "porter_room_bed_lamp", "feet": Vector3(2.3, 6.0, 4.05), "at": Vector3(4.7, 6.35, 2.6), "lamp": true},
	{"name": "porter_room_corner_lamp", "feet": Vector3(4.6, 6.0, 1.2), "at": Vector3(1.8, 6.6, 1.9), "lamp": true},
]

var _n := 0


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	Settings.subtitle_size = 1
	Settings.subtitle_backing = false
	Settings.less_motion = false
	Settings.guidance = false
	Settings.sky_dial = false
	Settings.fov = 70.0
	Settings.apply()
	NightPilot.fresh_night("user://inn_shots_save.tres")
	GameState.night = 0
	GameState.chapter = 0
	GameState.start_beat = &"Inn"
	GameState.hour = 20.0
	var main := NightPilot.main_with("res://game/chapters/night0/night0.tscn")
	add_child(main)
	var night: Node = main.get(&"current_level")
	await get_tree().create_timer(1.0).timeout
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var pilot := NightPilot.new(night, func(_ok: bool, _w: String) -> void: pass)
	var p := pilot.player
	(night.get_node(^"Hallucinations") as Hallucinations).active = false
	pilot.clock().set_pace(1.0e9, 1.0e9)
	GameState.hour = 20.0
	var inn := night.get_node(INN) as Node3D
	var people := PackedStringArray()
	for person in night.get_node(^"People").get_children():
		if person is Node3D:
			var at := inn.to_local((person as Node3D).global_position)
			if at.x > -6.0 and at.x < 6.0 and at.z > 0.0 and at.z < 10.0:
				people.append("%s (%.2f, %.2f, %.2f)" % [person.name, at.x, at.y, at.z])
	print("inn shots: people in the inn: ", ", ".join(people))
	var only := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--only="):
			only = arg.trim_prefix("--only=")
	for shot: Dictionary in SHOTS:
		if only != "" and not String(shot["name"]).contains(only):
			_n += 1
			continue
		var feet := inn.to_global(shot["feet"] as Vector3)
		var at := inn.to_global(shot["at"] as Vector3)
		p.place(feet, 0.0)
		Talk.reset()
		GameState.hour = 20.0
		await get_tree().create_timer(0.3).timeout
		var to := at - p.camera.global_position
		p.rotation.y = atan2(-to.x, -to.z)
		p.head.rotation.x = atan2(to.y, Vector2(to.x, to.z).length())
		var lamp: OmniLight3D = null
		if shot.get("lamp", false):
			lamp = OmniLight3D.new()
			lamp.light_color = Color(0.878, 0.643, 0.345)
			lamp.light_energy = 1.6
			lamp.omni_range = 7.0
			lamp.shadow_enabled = true
			night.add_child(lamp)
			lamp.global_position = p.camera.global_position + Vector3(0.0, -0.35, 0.0)
		await _shot(String(shot["name"]))
		if lamp:
			lamp.queue_free()
	print("inn shots done")
	get_tree().quit()


func _shot(shot_name: String, settle := 1.5) -> void:
	await get_tree().create_timer(settle).timeout
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	_n += 1
	var path := OUT + "%02d_%s.png" % [_n, shot_name]
	img.save_png(ProjectSettings.globalize_path(path))
	print("wrote ", path)
