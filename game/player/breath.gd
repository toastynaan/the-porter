class_name Breath
extends Node
## Holding the breath while `hold_breath` is held (Look and Feel, "Sound
## feel": holding your breath cuts your body's sounds). The breath meter,
## which hunger shortens, comes with hiding in M3.

signal changed(holding: bool)

var holding := false


func _process(_delta: float) -> void:
	var held := Input.is_action_pressed(&"hold_breath") and not (owner as Player).crawling
	if held != holding:
		holding = held
		changed.emit(holding)
