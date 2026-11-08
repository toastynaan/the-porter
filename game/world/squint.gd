class_name Squint
extends Node3D
## A squint: a small barred window in the abbey wall along the lane (design
## doc, "Setting": three, one from the porter's cell and two from the outer
## court). The node sits in the slit, -Z toward the lane. From either side,
## E puts his eye to the bars (Player.peek): the view held, within PEEK_LOOK
## degrees of straight through; E steps back. He can't be seen through it
## except up close, with a light (HunterSenses).

## Degrees he can look about through it, either way (docs/mechanics.md, "Peeking").
const PEEK_LOOK := 25.0
## How far from the slit his eye is.
const EYE_OFF := 0.12

## For the night's scare and its tests: which squint this is.
@export var id := &""

var _area: Area3D


func _ready() -> void:
	add_to_group(&"squints")
	_area = Area3D.new()
	_area.collision_layer = Layers.INTERACT
	_area.collision_mask = 0
	_area.monitoring = false
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(0.5, 0.7, 1.6)
	shape.shape = box
	_area.add_child(shape)
	add_child(_area)


## True if `point` is on the lane's side.
func outside(point: Vector3) -> bool:
	return (global_transform.affine_inverse() * point).z < 0.0


## Where his eye goes to look through from the side `point` is on.
func eye_for(point: Vector3) -> Transform3D:
	var out := outside(point)
	var at := global_transform * Vector3(0.0, 0.0, -EYE_OFF if out else EYE_OFF)
	# Looking through: from the lane into the court is +Z, from the court out is -Z.
	var look := global_basis.z if out else -global_basis.z
	return Transform3D(Basis.looking_at(look, Vector3.UP), at)


func interact(by: Node) -> void:
	var p := by as Player
	if p:
		p.peek(self)
