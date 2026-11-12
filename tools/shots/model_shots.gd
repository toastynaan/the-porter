extends Node3D
## A look at built models on their own, in plain grey daylight, from two
## sides, to art/_review/models/<name>.png (tools/shots/model_shots.sh): for
## checking a build script's shapes before the model goes into a scene.
## Names (art/models/<name>.glb) come after "--" on the command line.

const OUT := "res://art/_review/models/"


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.62, 0.65, 0.7)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.7, 0.74, 0.8)
	env.ambient_light_energy = 0.7
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-38.0, 40.0, 0.0)
	sun.light_energy = 1.1
	sun.shadow_enabled = true
	add_child(sun)
	var ground := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(200.0, 200.0)
	var grey := StandardMaterial3D.new()
	grey.albedo_color = Color(0.36, 0.36, 0.35)
	plane.material = grey
	ground.mesh = plane
	add_child(ground)
	var camera := Camera3D.new()
	camera.fov = 40.0
	add_child(camera)
	camera.current = true
	for model_name in OS.get_cmdline_user_args():
		var scene := load("res://art/models/%s.glb" % model_name) as PackedScene
		if scene == null:
			print("no model called ", model_name)
			continue
		var model := scene.instantiate() as Node3D
		add_child(model)
		var box := AABB()
		var first := true
		for m: Node in model.find_children("*", "MeshInstance3D", true, false):
			var b := (m as MeshInstance3D).global_transform * (m as MeshInstance3D).get_aabb()
			box = b if first else box.merge(b)
			first = false
		var centre := box.get_center()
		var reach := maxf(box.size.length() * 0.5, 0.5)
		var views: Array[Image] = []
		for yaw: float in [35.0, 215.0]:
			var dir := Vector3(sin(deg_to_rad(yaw)), 0.32, cos(deg_to_rad(yaw))).normalized()
			camera.global_position = centre + dir * reach / tan(deg_to_rad(camera.fov * 0.5)) * 1.15
			camera.look_at(centre)
			await get_tree().create_timer(0.4).timeout
			await RenderingServer.frame_post_draw
			views.append(get_viewport().get_texture().get_image())
		var w := views[0].get_width()
		var h := views[0].get_height()
		var sheet := Image.create(w * 2, h, false, views[0].get_format())
		sheet.blit_rect(views[0], Rect2i(0, 0, w, h), Vector2i(0, 0))
		sheet.blit_rect(views[1], Rect2i(0, 0, w, h), Vector2i(w, 0))
		sheet.save_png(ProjectSettings.globalize_path(OUT + model_name + ".png"))
		print("wrote ", OUT + model_name + ".png  ", box.size)
		model.queue_free()
		await get_tree().process_frame
	get_tree().quit()
