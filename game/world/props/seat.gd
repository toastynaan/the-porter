class_name Seat
extends Area3D
## Somewhere the porter can sit (your ask, 2026-11-12): a bench, a stool, a
## settle by the fire. Look at it and press `interact` to sit; his view
## comes down to a seated eye and he can look about, talk to whoever comes,
## and reach what's on the table (an ale, Tankard). A move key or
## `interact` on the seat again stands him up, in front of it.
##
## The origin is on the floor under where he sits, facing -Z (the way he
## looks when he sits down). The box (`size`) is what the view ray finds.

## Height of his eyes when seated, from the floor, m.
@export var eye_height := 1.18
## The box his view finds, m, standing on the origin.
@export var size := Vector3(0.6, 0.5, 0.6)
## How far in front of the seat he stands when he gets up, m.
@export var stand_off := 0.55
## What the outline goes on (the prop this seat is part of).
@export var outline: Array[Node3D] = []

var occupied := false


func _ready() -> void:
	collision_layer = Layers.INTERACT
	collision_mask = 0
	monitoring = false
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = size
	shape.shape = box
	shape.position = Vector3(0.0, size.y * 0.5, 0.0)
	add_child(shape)


func interact(by: Node) -> void:
	var p := by as Player
	if p == null:
		return
	if p.seat == self:
		p.stand_up()
	elif p.seat == null and not occupied:
		p.sit_on(self)


## Where he stands when he gets up.
func stand_point() -> Vector3:
	return global_position - global_basis.z * stand_off
