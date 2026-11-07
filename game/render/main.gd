extends Node
## The render pipeline (Look and Feel, "Godot 4 render setup"): the 3D level
## renders into the World SubViewport, 540 lines tall, shown on the Screen
## TextureRect scaled up by a whole number with nearest filtering and the post
## shader. The UI layer draws above it at full resolution.
##
## The render keeps 540 lines and takes its width from the window's shape
## (960 on 16:9), so pixels stay square; leftover rows are letterboxed.
##
## Pick the level with a user argument: `-- --level=res://path/to/level.tscn`.

const RENDER_HEIGHT := 540

@export var level: PackedScene

var pixel_scale := 1

@onready var world: SubViewport = $World
@onready var screen: TextureRect = $Screen


func _ready() -> void:
	var tex := world.get_texture()
	screen.texture = tex
	var mat := screen.material as ShaderMaterial
	mat.set_shader_parameter(&"src_nearest", tex)
	mat.set_shader_parameter(&"src_linear", tex)
	get_viewport().size_changed.connect(_layout)
	_layout()
	var scene := level
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--level="):
			scene = load(arg.trim_prefix("--level="))
	if scene:
		world.add_child(scene.instantiate())


## Input reaches nodes inside the SubViewport only through push_input.
func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouse:
		event = event.duplicate()
		event.position = (event.position - screen.position) / pixel_scale
		event.global_position = event.position
	world.push_input(event, true)


func _layout() -> void:
	layout_for(get_viewport().get_visible_rect().size)


## Sizes the world render and the Screen for a window of `win` pixels.
func layout_for(win: Vector2) -> void:
	pixel_scale = maxi(1, floori(win.y / RENDER_HEIGHT))
	var h := mini(RENDER_HEIGHT, floori(win.y))
	world.size = Vector2i(maxi(1, floori(win.x / pixel_scale)), maxi(1, h))
	screen.size = Vector2(world.size * pixel_scale)
	screen.position = ((win - screen.size) * 0.5).floor()
