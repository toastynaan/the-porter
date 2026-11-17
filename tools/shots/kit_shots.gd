extends Node3D
## The people's kit as sheets (tools/shots/kit_shots.sh): every entry of
## every catalogue in tools/build/people_kit.py, as tools/build/kit_catalogue.py
## built it, in plain grey light, named, to art/_review/kit/. One still a
## sheet and a view: bodies, skins, faces, hair, headwear, wear, colours.
## The models are read straight from art/_review/kit/models/ (they are not
## the game's, and are never imported).

const OUT := "res://art/_review/kit/"
const MODELS := "res://art/_review/kit/models/"
const FONT := preload("res://art/fonts/eb_garamond/EBGaramond.ttf")
const PERSON := preload("res://game/people/person.gdshader")
const FACE := preload("res://game/people/face.gdshader")
const PERSON_MODEL := preload("res://game/people/person_model.gd")
const FACE_RIG := preload("res://game/people/face_rig.gd")
## A figure's cell and a head's, m: width, height.
const FIGURE_CELL := Vector2(1.25, 2.45)
const HEAD_CELL := Vector2(0.4, 0.5)
const CHIP := Vector2(0.3, 0.2)

var _camera: Camera3D
var _stage: Node3D


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.3, 0.3, 0.3)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.9, 0.9, 0.92)
	env.ambient_light_energy = 1.3
	env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-28.0, 152.0, 0.0)
	sun.light_energy = 1.7
	add_child(sun)
	_camera = Camera3D.new()
	_camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	add_child(_camera)
	_camera.current = true
	var only := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--only="):
			only = arg.trim_prefix("--only=")
	var text := FileAccess.get_file_as_string(MODELS + "catalogue.json")
	var sheets: Array = (JSON.parse_string(text) as Dictionary)["sheets"]
	for sheet: Dictionary in sheets:
		if only != "" and not String(sheet["name"]).contains(only):
			continue
		if sheet["kind"] == "chips":
			await _chips(sheet)
		else:
			for view: float in sheet["views"]:
				await _sheet(sheet, view)
	print("kit shots done")
	get_tree().quit()


func _sheet(sheet: Dictionary, view: float) -> void:
	var figures: bool = sheet["kind"] == "figure"
	var cell := FIGURE_CELL if figures else HEAD_CELL
	var items: Array = sheet["items"]
	var rows := int(sheet["rows"])
	var cols := ceili(items.size() / float(rows))
	_stage = Node3D.new()
	add_child(_stage)
	for i in items.size():
		var item: Dictionary = items[i]
		# +X is the picture's left (they face the camera, down -Z): the first is top left.
		var at := Vector3(-(i % cols - (cols - 1) * 0.5) * cell.x, -floorf(i / float(cols)) * cell.y, 0.0)
		var who := _figure(item) if figures else _head(item)
		_stage.add_child(who)
		who.position = at
		who.rotation.y = deg_to_rad(view)
		# Faces hold still (no blink in the still), in the mood the sheet asks.
		var rig := FaceRig.on(who)
		if rig:
			rig._still = 100.0
			if item.has("mood"):
				rig.mood(StringName(String(item["mood"])))
		_label(String(item["label"]), at + Vector3(0.0, -0.1 if figures else -0.215, 0.3), 0.075 if figures else 0.024)
	# Their clips come to rest (and a mood eases in), then every one at the
	# same moment of his idle.
	await get_tree().create_timer(1.0).timeout
	await _frames(6)
	for anim: AnimationPlayer in _stage.find_children("*", "AnimationPlayer", true, false):
		if anim.has_animation(&"idle"):
			anim.play(&"idle")
			anim.seek(0.6, true)
	if figures:
		_frame(cols, rows, cell, 2.2, 0.22)
	else:
		_frame(cols, rows, cell, 0.24, 0.27)
	await _shot("%s%s" % [sheet["name"], "" if view == 0.0 else "_%d" % int(view)])
	_stage.queue_free()
	await _frames(2)


func _chips(sheet: Dictionary) -> void:
	_stage = Node3D.new()
	add_child(_stage)
	var y := 0.0
	var widest := 1
	for group: Dictionary in sheet["groups"]:
		var items: Array = group["items"]
		_label(String(group["label"]), Vector3(1.45, y + 0.04, 0.0), 0.05)
		y -= 0.16
		var per_row := 10
		for i in items.size():
			var item: Dictionary = items[i]
			var c: Array = item["color"]
			var quad := MeshInstance3D.new()
			var mesh := QuadMesh.new()
			mesh.size = CHIP
			quad.mesh = mesh
			var mat := StandardMaterial3D.new()
			mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
			mat.albedo_color = Color(c[0], c[1], c[2])
			quad.material_override = mat
			_stage.add_child(quad)
			var at := Vector3(1.45 - (i % per_row) * (CHIP.x + 0.03), y - floorf(i / float(per_row)) * (CHIP.y + 0.1), 0.0)
			quad.position = at
			quad.rotation.y = PI
			_label(String(item["label"]), at + Vector3(0.0, -CHIP.y * 0.5 - 0.035, 0.0), 0.03)
			widest = maxi(widest, mini(items.size(), per_row))
		y -= ceilf(items.size() / float(per_row)) * (CHIP.y + 0.1) + 0.12
	_camera.size = maxf(-y + 0.3, 3.5 * 9.0 / 16.0)
	_camera.look_at_from_position(Vector3(0.0, y * 0.5 + 0.05, -5.0), Vector3(0.0, y * 0.5 + 0.05, 0.0))
	await _shot(String(sheet["name"]))
	_stage.queue_free()
	await _frames(2)


## A dressed figure, as a character scene has it: Model on its skeleton,
## Head (a FaceRig) with the head model, Face.
func _figure(item: Dictionary) -> Node3D:
	var atlas := _atlas(String(item["id"]))
	var root := Node3D.new()
	root.set_script(PERSON_MODEL)
	var model := _glb(String(item["id"]) + ".glb")
	model.name = "Model"
	root.add_child(model)
	var neck: Array = item["neck"]
	var head := Node3D.new()
	head.name = "Head"
	head.set_script(FACE_RIG)
	head.position = Vector3(neck[0], neck[1], neck[2])
	root.add_child(head)
	var head_model := _glb(String(item["id"]) + "_head.glb")
	head_model.name = "Model"
	head.add_child(head_model)
	var face := Marker3D.new()
	face.name = "Face"
	root.add_child(face)
	_dress(root, atlas, item["look"])
	return root


func _head(item: Dictionary) -> Node3D:
	var atlas := _atlas(String(item["id"]))
	var root := Node3D.new()
	var head := Node3D.new()
	head.name = "Head"
	head.set_script(FACE_RIG)
	# The head's own origin is the neck: bring the face to the cell's middle.
	head.position = Vector3(0.0, -0.2, 0.0)
	root.add_child(head)
	var head_model := _glb(String(item["id"]) + "_head.glb")
	head.add_child(head_model)
	_dress(root, atlas, item["look"])
	return root


func _glb(file: String) -> Node3D:
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	var err := doc.append_from_file(ProjectSettings.globalize_path(MODELS + file), state)
	if err != OK:
		push_error("kit shots: can't read %s" % file)
		return Node3D.new()
	return doc.generate_scene(state) as Node3D


func _atlas(id: String) -> ImageTexture:
	var img := Image.load_from_file(ProjectSettings.globalize_path(MODELS + id + ".png"))
	img.generate_mipmaps()
	return ImageTexture.create_from_image(img)


## The game's materials on a model read from a file: by each surface's
## material name (chr_<name>, chr_<name>_face).
func _dress(root: Node, atlas: Texture2D, look: Dictionary) -> void:
	var body := ShaderMaterial.new()
	body.shader = PERSON
	body.set_shader_parameter(&"atlas", atlas)
	var face := ShaderMaterial.new()
	face.shader = FACE
	face.set_shader_parameter(&"atlas", atlas)
	for k: String in look:
		var v: Variant = look[k]
		if v is Array:
			var a := v as Array
			if a.size() == 2:
				face.set_shader_parameter(k, Vector2(a[0], a[1]))
			else:
				face.set_shader_parameter(k, Color(a[0], a[1], a[2]))
		else:
			face.set_shader_parameter(k, float(v))
	for mi: MeshInstance3D in root.find_children("*", "MeshInstance3D", true, false):
		for s in mi.mesh.get_surface_count():
			var mat := mi.mesh.surface_get_material(s)
			var is_face := mat != null and String(mat.resource_name).ends_with("_face")
			mi.set_surface_override_material(s, face if is_face else body)


func _label(text: String, at: Vector3, size: float) -> void:
	var l := Label3D.new()
	l.text = text
	l.font = FONT
	l.font_size = 64
	l.pixel_size = size / 64.0
	l.modulate = Color(0.92, 0.9, 0.84)
	l.outline_size = 8
	l.outline_modulate = Color(0.0, 0.0, 0.0, 0.6)
	l.shaded = false
	l.no_depth_test = true
	l.rotation.y = PI
	_stage.add_child(l)
	l.position = at


## The camera square on the whole grid, from in front (they face -Z):
## `top` m above the first row's origin to `below` m under the last row's.
func _frame(cols: int, rows: int, cell: Vector2, top: float, below: float) -> void:
	var height := (rows - 1) * cell.y + top + below
	var width := cols * cell.x
	var middle := Vector3(0.0, top - height * 0.5, 0.0)
	_camera.size = maxf(height, (width + 0.1) * 9.0 / 16.0)
	_camera.look_at_from_position(middle + Vector3(0.0, 0.0, -8.0), middle)


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _shot(shot_name: String) -> void:
	await _frames(3)
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(OUT + "%s.png" % shot_name)
	print("wrote %s%s.png" % [OUT, shot_name])
