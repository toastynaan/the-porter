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
## Sitting (the traveller and the carter on the wagon): a real model shows
## its seated body (PersonModel.seated); a placeholder stands as it was.
@export var seated := false:
	set(value):
		seated = value
		if _body and &"seated" in _body:
			_body.set(&"seated", seated)

var _body: Node3D

## How far a head turns to look, radians (about 75°).
const AIM_YAW := 1.3


func _ready() -> void:
	_dress()


## Where his face is: what the conversation camera looks at.
func face_position() -> Vector3:
	var face: Node3D = null
	if _body and _body.has_method(&"face_marker"):
		face = _body.call(&"face_marker") as Node3D
	elif _body:
		face = _body.get_node_or_null(^"Face") as Node3D
	return face.global_position if face else global_position + Vector3.UP * 1.6


## Turns his head (not his body) to look at `point`, as far as a neck turns:
## a seated man looking round at the porter. look_ahead() turns it back.
func aim_head(point: Vector3) -> void:
	var rig := FaceRig.on(_body) if _body else null
	if rig == null:
		return
	var to := global_basis.inverse() * (point - face_position())
	var yaw := clampf(atan2(-to.x, -to.z), -AIM_YAW, AIM_YAW)
	var pitch := clampf(atan2(to.y, Vector2(to.x, to.z).length()), -0.5, 0.35)
	rig.aim_at = Vector2(yaw, pitch)


func look_ahead() -> void:
	var rig := FaceRig.on(_body) if _body else null
	if rig:
		rig.aim_at = Vector2.ZERO


## A part of the character scene by its path (the warden's Lantern), or null.
func part(path: NodePath) -> Node3D:
	return _body.get_node_or_null(path) as Node3D if _body else null


func _dress() -> void:
	if not is_inside_tree():
		return
	if _body:
		remove_child(_body)
		_body.queue_free()
		_body = null
	if look:
		_body = look.instantiate() as Node3D
		if seated and &"seated" in _body:
			_body.set(&"seated", true)
		add_child(_body, false, Node.INTERNAL_MODE_FRONT)
