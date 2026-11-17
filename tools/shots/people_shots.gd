extends Node3D
## People side by side, named, in plain grey light, from in front and
## turned (tools/shots/people_shots.sh): the character scenes as the game
## has them (game/characters/chr_<name>.tscn), to art/_review/people/.
##   -- --as=lane hob,agnes,kit        one sheet "lane" of those three

const OUT := "res://art/_review/people/"
const FONT := preload("res://art/fonts/eb_garamond/EBGaramond.ttf")
const CELL := Vector2(1.2, 2.5)

var _camera: Camera3D


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
	var sheet := "people"
	var names := PackedStringArray()
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--as="):
			sheet = arg.trim_prefix("--as=")
		else:
			names = arg.split(",", false)
	for view: float in [0.0, 140.0]:
		await _sheet(sheet, names, view)
	print("people shots done")
	get_tree().quit()


func _sheet(sheet: String, names: PackedStringArray, view: float) -> void:
	var stage := Node3D.new()
	add_child(stage)
	var rows := 1 if names.size() <= 6 else 2
	var cols := ceili(names.size() / float(rows))
	for i in names.size():
		var path := "res://game/characters/chr_%s.tscn" % names[i]
		if not ResourceLoader.exists(path):
			push_error("people shots: no %s" % path)
			continue
		# Named as the person, so the face finds its baseline.
		var holder := Node3D.new()
		holder.name = names[i].capitalize().replace(" ", "")
		stage.add_child(holder)
		holder.position = Vector3(-(i % cols - (cols - 1) * 0.5) * CELL.x, -floorf(i / float(cols)) * CELL.y, 0.0)
		holder.rotation.y = deg_to_rad(view)
		holder.add_child((load(path) as PackedScene).instantiate())
		var rig := FaceRig.on(holder)
		if rig:
			rig._still = 100.0
		var l := Label3D.new()
		l.text = names[i].replace("_", " ")
		l.font = FONT
		l.font_size = 64
		l.pixel_size = 0.075 / 64.0
		l.modulate = Color(0.92, 0.9, 0.84)
		l.outline_size = 8
		l.outline_modulate = Color(0.0, 0.0, 0.0, 0.6)
		l.shaded = false
		l.no_depth_test = true
		l.rotation.y = PI
		stage.add_child(l)
		l.position = holder.position + Vector3(0.0, -0.1, 0.3)
	await get_tree().create_timer(1.0).timeout
	for anim: AnimationPlayer in stage.find_children("*", "AnimationPlayer", true, false):
		if anim.has_animation(&"idle"):
			anim.play(&"idle")
			anim.seek(0.6, true)
	var height := (rows - 1) * CELL.y + 2.2 + 0.22
	_camera.size = maxf(height, (cols * CELL.x + 0.1) * 9.0 / 16.0)
	var middle := Vector3(0.0, 2.2 - height * 0.5, 0.0)
	_camera.look_at_from_position(middle + Vector3(0.0, 0.0, -8.0), middle)
	for i in 4:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var file := "%s%s%s.png" % [OUT, sheet, "" if view == 0.0 else "_%d" % int(view)]
	get_viewport().get_texture().get_image().save_png(file)
	print("wrote ", file)
	stage.queue_free()
	await get_tree().process_frame
