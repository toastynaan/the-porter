class_name Spin
extends Node3D
## Turns one node of a model about an axis, slowly and not quite evenly: a
## mill's sails in a failing wind.

## The node that turns, by its path from here, the axis it turns about (its own), and how fast, turns a minute.
@export var part := NodePath("Model/Sails")
@export var axis := Vector3(0, 0, 1)
@export var turns_a_minute := 5.0

var _t := 0.0


func _process(delta: float) -> void:
	var node := get_node_or_null(part) as Node3D
	if node == null:
		return
	_t += delta
	var gusting := 0.75 + 0.25 * sin(_t * 0.37) * sin(_t * 0.11 + 1.0)
	node.rotate_object_local(axis.normalized(), delta * turns_a_minute / 60.0 * TAU * gusting)
