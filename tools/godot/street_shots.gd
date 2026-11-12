extends Node
## Review renders of the street outside the west gate (tools/street_shots.sh):
## a plan of the abbey and the lane, then views through the game's render
## pipeline from a free camera, to art/_review/street/.

const OUT := "res://art/_review/street/"
## name: [camera position, point looked at]
const VIEWS := {
	"lane_to_gate": [Vector3(-44.6, 1.6, 7.5), Vector3(-40.6, 2.3, -2.0)],
	"lane_north": [Vector3(-43.2, 1.6, 22.0), Vector3(-43.8, 2.4, 46.0)],
	"lane_south": [Vector3(-43.2, 1.6, -16.0), Vector3(-43.8, 2.4, -46.0)],
	"through_the_gate": [Vector3(-36.5, 1.6, -2.0), Vector3(-48.0, 2.0, -2.0)],
	"over_the_wall": [Vector3(-24.0, 13.5, -31.0), Vector3(-62.0, 3.0, -4.0)],
}


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	await _plan()
	var main: Node = load("res://game/core/render/main.tscn").instantiate()
	main.set(&"level", load("res://game/world/abbey/abbey.tscn"))
	add_child(main)
	await get_tree().process_frame
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var world: SubViewport = main.get_node(^"World")
	var player: Player = get_tree().get_first_node_in_group(&"player")
	player.process_mode = Node.PROCESS_MODE_DISABLED
	player.lantern.visible = false
	var cam := Camera3D.new()
	cam.fov = 70.0
	cam.near = 0.05
	world.add_child(cam)
	cam.current = true
	GameState.snap_dose(0.0)
	for view_name: String in VIEWS:
		var v: Array = VIEWS[view_name]
		cam.look_at_from_position(v[0], v[1], Vector3.UP)
		await get_tree().create_timer(1.2).timeout
		await RenderingServer.frame_post_draw
		_save(get_viewport().get_texture().get_image(), view_name)
	get_tree().quit()


## Flat-lit plan from above, roofs off, the lane and the city around.
func _plan() -> void:
	var abbey: Node3D = load("res://game/world/abbey/abbey.tscn").instantiate()
	add_child(abbey)
	abbey.get_node(^"Player").queue_free()
	for node in abbey.find_children("*Roof*", "", true, false):
		(node as Node3D).visible = false
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.1, 0.1, 0.1)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color.WHITE
	env.ambient_light_energy = 0.6
	(abbey.get_node(^"WorldEnvironment") as WorldEnvironment).environment = env
	var moon: DirectionalLight3D = abbey.get_node(^"Moon")
	moon.light_color = Color.WHITE
	moon.light_energy = 0.9
	moon.basis = Basis.looking_at(Vector3(0.3, -1.0, -0.4).normalized())
	var cam := Camera3D.new()
	cam.projection = Camera3D.PROJECTION_ORTHOGONAL
	cam.size = 125.0
	cam.far = 300.0
	add_child(cam)
	cam.look_at_from_position(Vector3(-25, 120, 0), Vector3(-25, 0, 0), Vector3.FORWARD)
	cam.current = true
	for i in 30:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	_save(get_viewport().get_texture().get_image(), "plan")
	abbey.queue_free()
	cam.queue_free()
	await get_tree().process_frame


func _save(img: Image, shot_name: String) -> void:
	var s := floori(img.get_height() / 540.0)
	if s > 1:
		img.resize(roundi(img.get_width() / float(s)), roundi(img.get_height() / float(s)), Image.INTERPOLATE_NEAREST)
	var path := OUT + shot_name + ".png"
	img.save_png(ProjectSettings.globalize_path(path))
	print("wrote ", path)
