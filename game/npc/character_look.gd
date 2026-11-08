@tool
class_name CharacterLook
extends Node3D
## How someone looks: an instance of their character scene
## (game/characters/chr_<name>.tscn), which holds the stand-in figure, the
## one prop they're known by, and a Face marker (Look and Feel, "Characters":
## build, face, one prop, one sound). Brothers, visitors and passers-by all
## wear one, so a character's model is swapped in one place for every night.
## Faces -Z.

@export var look: PackedScene:
	set(value):
		look = value
		_dress()

var _body: Node3D


func _ready() -> void:
	_dress()


## Where his face is: what the conversation camera looks at.
func face_position() -> Vector3:
	var face := _body.get_node_or_null(^"Face") as Node3D if _body else null
	return face.global_position if face else global_position + Vector3.UP * 1.6


func _dress() -> void:
	if not is_inside_tree():
		return
	if _body:
		remove_child(_body)
		_body.queue_free()
		_body = null
	if look:
		_body = look.instantiate() as Node3D
		add_child(_body, false, Node.INTERNAL_MODE_FRONT)
