class_name Figure
extends Node3D
## Someone who stays where a beat puts them (the traveller and the carter on
## the wagon): their Look (a CharacterLook) and, for a Talker, a face to look
## at and a way to turn to him.

@onready var look := get_node_or_null(^"Look") as CharacterLook


func face_position() -> Vector3:
	return look.face_position() if look else global_position + Vector3.UP * 1.6


func face(point: Vector3) -> void:
	var to := point - global_position
	if Vector2(to.x, to.z).length() > 0.05:
		global_rotation.y = atan2(-to.x, -to.z)
