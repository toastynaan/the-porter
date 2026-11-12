extends Node
## Night 0's last scene as the player sees it (tools/shots/window_film.sh):
## from the Window beat, he lies down; the cry; at the window the killing by
## the well and the body dragged off toward the cellar; then the court
## empty. Run under Godot's movie writer, so the drag can be watched to the
## end: the body should go out of sight, not vanish in view.

const LENGTH := 48.0

var _t := 0.0
var _flow: GameFlow


func _ready() -> void:
	Settings.subtitle_size = 1
	Settings.less_motion = false
	Settings.apply()
	var main: Node = load("res://game/core/render/main.tscn").instantiate()
	add_child(main)
	_flow = main.get_node(^"Game") as GameFlow
	await get_tree().process_frame
	_flow.title.close()
	await _flow.start_at(0, &"Window")
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	# He lies down at once.
	await get_tree().create_timer(1.0).timeout
	GameState.set_flag(&"n0_lay_down")


func _process(delta: float) -> void:
	_t += delta
	if _t >= LENGTH:
		get_tree().quit()
