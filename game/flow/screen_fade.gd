class_name ScreenFade
extends ColorRect
## A black fade over everything, for captures and restarts.


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	color = Color(0, 0, 0, 0)


## Fades to `alpha` (1 = black) over `seconds`; await it.
func fade_to(alpha: float, seconds: float) -> void:
	var tween := create_tween()
	tween.tween_property(self, ^"color:a", alpha, maxf(seconds, 0.01))
	await tween.finished
