class_name Tankard
extends Area3D
## An ale on a table at the Cross Keys (your ask, 2026-11-12): look at it
## and press `interact` to drink it (docs/places/prologue.md, "Drinking":
## each ale blurs the night a little more, GameState.have_a_drink). Then it's
## empty, until the next night. Its `Ale` child (the ale in the cup) goes
## when it's drunk.

## What he notices as he drinks.
@export var line := "(You drink. Thin, sour ale, warm going down.)"
## The box his view finds, m, standing on the origin.
@export var size := Vector3(0.18, 0.2, 0.18)

var full := true


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


func interact(_by: Node) -> void:
	if not full:
		return
	full = false
	collision_layer = 0
	var ale := get_node_or_null(^"Ale") as Node3D
	if ale:
		ale.visible = false
	GameState.have_a_drink()
	Talk.say("", line)
