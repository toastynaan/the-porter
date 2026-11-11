extends Node3D
## Stills of props standing alone on a floor in the dark, lit as the porter's
## lantern would light them, to art/_review/props/ (tools/prop_studio.sh).
## For judging a prop's model: each is seen from its front (-Z, where one
## stands at it) and, with "--back", from behind. A second still with
## "--fill" adds a plain lamp the game doesn't have, to check the geometry.
##   -- --props=bed,bench     only these (names without "prop_")
##   -- --fill                the plain lamp as well as the lantern
##   -- --back                from behind

const OUT := "res://art/_review/props/"
## Props this tool leaves out when none are named: trees, the road's, decals.
const SKIP := ["tree_", "field_", "blood_", "drag_", "sand_", "lantern_hung", "cresset", "brazier", "gibbet"]


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	var names: PackedStringArray = []
	var fill_too := false
	var back := false
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--props="):
			names = arg.trim_prefix("--props=").split(",", false)
		elif arg == "--fill":
			fill_too = true
		elif arg == "--back":
			back = true
	if names.is_empty():
		for file in DirAccess.get_files_at("res://game/world/props/"):
			if file.begins_with("prop_") and file.ends_with(".tscn"):
				var n := file.trim_prefix("prop_").trim_suffix(".tscn")
				if not SKIP.any(func(s: String) -> bool: return n.begins_with(s)):
					names.append(n)
	var world := WorldEnvironment.new()
	world.environment = (load("res://game/render/env_night.tres") as Environment).duplicate()
	world.environment.volumetric_fog_enabled = false
	add_child(world)
	var ground := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(30, 30)
	plane.material = load("res://game/world/materials/real/flags_worn.tres")
	ground.mesh = plane
	add_child(ground)
	var cam := Camera3D.new()
	cam.fov = 50.0
	add_child(cam)
	cam.current = true
	var lantern := OmniLight3D.new()
	lantern.light_color = Color(0.878, 0.643, 0.345)
	lantern.light_energy = 1.8
	lantern.omni_range = 5.0
	lantern.omni_attenuation = 0.8
	lantern.shadow_enabled = true
	add_child(lantern)
	var fill := OmniLight3D.new()
	fill.omni_range = 20.0
	fill.light_energy = 1.4
	fill.light_color = Color(1.0, 0.9, 0.75)
	fill.shadow_enabled = true
	add_child(fill)
	for n in names:
		var path := "res://game/world/props/prop_%s.tscn" % n
		if n == "door":
			path = "res://game/world/door/door.tscn"
		elif n == "candle" or n == "lamp":
			path = "res://game/world/props/%s.tscn" % n
		if not ResourceLoader.exists(path):
			print("ERROR no scene for ", n)
			continue
		var prop := (load(path) as PackedScene).instantiate() as Node3D
		add_child(prop)
		if prop is Candle:
			(prop as Candle).lit = false
		await get_tree().process_frame
		await get_tree().process_frame
		var box := _bounds(prop)
		var centre := box.get_center()
		var reach := maxf(box.size.length() * 0.5, 0.12)
		var dist := reach / tan(deg_to_rad(cam.fov * 0.5)) * 0.92
		var way := Vector3(-0.8, 0.0, 0.62 if back else -0.62).normalized()
		# From standing height, as he would come on it, unless it is small: then closer and lower.
		var eye := centre + way * dist
		eye.y = clampf(centre.y + dist * 0.5, 0.25, maxf(1.6, centre.y + 0.4))
		cam.global_position = eye
		cam.look_at(centre)
		# The lantern is in his hand: never nearer the thing than his arm lets it be.
		var hand := centre + way * maxf(dist, 1.1)
		hand.y = clampf(eye.y - 0.25, 0.9, 1.4)
		lantern.global_position = hand + cam.global_transform.basis.x * 0.3
		fill.global_position = eye + Vector3(0, 1.0, 0)
		# A prop that shows one of several models by where it stands: a still of each.
		var variant := prop.get_node_or_null(^"Model") as PropVariant
		for pick in (variant.get_child_count() if variant else 1):
			if variant:
				variant.pick = pick
			for lit in ([false, true] if fill_too else [false]):
				fill.visible = lit
				await get_tree().create_timer(0.35).timeout
				await RenderingServer.frame_post_draw
				var file := OUT + "%s%s%s%s.png" % [n, "_%d" % pick if variant else "", "_back" if back else "", "_fill" if lit else ""]
				get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path(file))
				print("wrote ", file)
		prop.queue_free()
		await get_tree().process_frame
	print("prop studio done")
	get_tree().quit()


func _bounds(root: Node3D) -> AABB:
	var box := AABB()
	var first := true
	for node in root.find_children("*", "VisualInstance3D", true, false):
		var v := node as VisualInstance3D
		if not v.is_visible_in_tree() or v is Light3D:
			continue
		var b := v.global_transform * v.get_aabb()
		box = b if first else box.merge(b)
		first = false
	return box
