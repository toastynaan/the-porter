extends Node
## Stills of the abbey's props where they stand, through the full render
## pipeline (tools/shots/props_shots.sh GROUP): night 3 (a clear night) unless the
## list names another (`NIGHT_NUMBER`), from a camera of the tool's own. GROUP names a list of stills,
## tools/godot/props_shots_<group>.gd (its `SHOTS`), and they are written to
## art/_review/props_<group>/. A still marked `lantern` has the porter
## standing at the camera with his lantern, as the thing is seen in play:
## put the eye 1.65 m above a floor he can stand on. `fill` adds a plain
## lamp the game doesn't have, to check a model; `sun` the low sun.

const DAY := 15.5
const DUSK := 16.6
const NIGHT := 22.0

var _n := 0


func _ready() -> void:
	var group := "court"
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--group="):
			group = arg.trim_prefix("--group=")
	var out := "res://art/_review/props_%s/" % group
	var list := (load("res://tools/godot/props_shots_%s.gd" % group) as Script).get_script_constant_map()
	var shots: Array = list["SHOTS"]
	# A list may ask for another night with `const NIGHT_NUMBER` (night 6 for the proofs).
	var number: int = list.get("NIGHT_NUMBER", 3)
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
	Settings.subtitle_size = 1
	Settings.less_motion = false
	Settings.fov = 70.0
	Settings.apply()
	NightPilot.fresh_night("user://props_shots_save.tres")
	GameState.night = number
	GameState.chapter = number + 1
	var main := NightPilot.main_with("res://game/chapters/night%d/night%d.tscn" % [number, number])
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
	for shot: Dictionary in shots:
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
		var path := out + "%02d_%s.png" % [_n, String(shot["name"])]
		get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path(path))
		print("wrote ", path)
	print("props shots done")
	get_tree().quit()
