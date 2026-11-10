class_name CartRoll
extends Node3D
## Rolls a cart's wheels (art/models/prop_cart.glb: WheelL, WheelR) by how
## far it is carried along, and rocks its body a little over the ruts. The
## seats on it are the scene's own and don't rock.

@export var wheel_radius := 0.62
## How far the body tips over rough ground, radians, at full pace.
@export var rock := 0.012

var _last := Vector3.ZERO
var _wheels: Array[Node3D] = []
var _body: Node3D
var _along := 0.0


func _ready() -> void:
	for wheel_name: String in ["WheelL", "WheelR"]:
		var w := find_child(wheel_name, true, false) as Node3D
		if w:
			_wheels.append(w)
	_body = find_child("Cart", true, false) as Node3D
	_last = global_position


func _physics_process(_delta: float) -> void:
	var moved := (global_position - _last).dot(-global_basis.z)
	_last = global_position
	if absf(moved) > 2.0:
		return
	_along += moved
	for w in _wheels:
		w.rotation.x -= moved / wheel_radius
	if _body and not Settings.less_motion:
		var pace := clampf(absf(moved) * 60.0 / 3.0, 0.0, 1.0)
		_body.rotation.z = sin(_along * 1.9) * sin(_along * 0.53) * rock * pace
		_body.rotation.x = sin(_along * 2.7 + 1.0) * rock * 0.5 * pace
