extends Node
## Development keys, in debug builds only: [ and ] ease Dose down or up by 25
## over 2 seconds, to try the look anywhere.

const STEP := 25.0
const EASE_TIME := 2.0


func _ready() -> void:
	if not OS.is_debug_build():
		queue_free()


func _unhandled_input(event: InputEvent) -> void:
	var key := event as InputEventKey
	if key == null or not key.pressed or key.echo:
		return
	match key.keycode:
		KEY_BRACKETLEFT:
			GameState.add_dose(-minf(STEP, GameState.dose), EASE_TIME)
		KEY_BRACKETRIGHT:
			GameState.add_dose(minf(STEP, GameState.DOSE_MAX - GameState.dose), EASE_TIME)
