class_name Windfalls
extends Node3D
## Windfall apples under the orchard trees (docs/mechanics.md, "The drug,
## and food": two or three a night): of its Pickup children, it puts out a
## third each night, a different third from the night before.


func _ready() -> void:
	var i := 0
	for c in get_children():
		if c is Pickup:
			(c as Pickup).visible = (i + GameState.night) % 3 == 0 and not GameState.has_flag(GameState.tonight("picked_" + String((c as Pickup).id)))
			i += 1
