class_name Sway
extends Node3D
## Something hung that never hangs quite still (the gibbet's cage): the
## part named `part`, somewhere under this node, swings a little about its
## own origin and turns slowly back and forth on its chain.

@export var part := "Cage"
## Degrees it swings, and it turns, at most.
@export var swing := 2.5
@export var turn := 14.0

var _node: Node3D
var _t := randf() * 50.0


func _ready() -> void:
	_node = find_child(part, true, false) as Node3D


func _process(delta: float) -> void:
	if _node == null:
		return
	_t += delta
	_node.rotation = Vector3(deg_to_rad(swing) * sin(_t * 0.9), deg_to_rad(turn) * sin(_t * 0.23), deg_to_rad(swing) * 0.6 * sin(_t * 0.7 + 1.3))
