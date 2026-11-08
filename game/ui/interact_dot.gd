extends Control
## The centre dot (Look and Feel, "UI": a small dot in the centre; what E
## would use gets a thin, pale outline in the world instead of a cursor,
## Outline). Drawn at full resolution, sized from the window height.

const DOT_COLOR := Color(0.85, 0.82, 0.75, 0.45)

var _shown := false


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func _process(_delta: float) -> void:
	var shown := get_tree().get_first_node_in_group(&"interactor") != null
	if shown != _shown:
		_shown = shown
		queue_redraw()


func _draw() -> void:
	if not _shown:
		return
	var c := (size * 0.5).floor()
	var u := maxf(1.0, size.y / 540.0)
	draw_circle(c, 1.5 * u, DOT_COLOR)
