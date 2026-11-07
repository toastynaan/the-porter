extends Control
## The only thing drawn over the world (Look and Feel, "UI"): a small dot in
## the centre that becomes a hand when something usable is in reach. Drawn at
## full resolution, sized from the window height.

const DOT_COLOR := Color(0.85, 0.82, 0.75, 0.45)
const HAND_COLOR := Color(0.85, 0.82, 0.75, 0.8)

var _focused := false
var _shown := false


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func _process(_delta: float) -> void:
	var interactor := get_tree().get_first_node_in_group(&"interactor") as Interactor
	var shown := interactor != null
	var focused := shown and interactor.focused != null
	if shown != _shown or focused != _focused:
		_shown = shown
		_focused = focused
		queue_redraw()


func _draw() -> void:
	if not _shown:
		return
	var c := (size * 0.5).floor()
	var u := maxf(1.0, size.y / 540.0)
	if not _focused:
		draw_circle(c, 1.5 * u, DOT_COLOR)
		return
	# An open hand: palm, four fingers and a thumb.
	draw_rect(Rect2(c + Vector2(-3.5, -1.0) * u, Vector2(7.0, 6.0) * u), HAND_COLOR)
	for i in 4:
		draw_rect(Rect2(c + Vector2(-3.5 + i * 1.9, -6.0 + absf(i - 1.5) * 0.8) * u, Vector2(1.4, 5.5) * u), HAND_COLOR)
	draw_line(c + Vector2(-3.5, 2.0) * u, c + Vector2(-6.0, -0.5) * u, HAND_COLOR, 1.4 * u)
