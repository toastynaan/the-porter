class_name AbbeyGate
extends Node
## The abbey gate as the night uses it: two grille leaves and the bar
## (design doc, "Core loop": open by day with Cole at it; after supper the
## porter shuts and bars it, and lifts the bar only to let someone in). The
## bar sits on the door layer: it blocks the porter but stays out of the
## navmesh, so the gateway is walkable when the gate is open.

@export var leaves: Array[Door] = []
## The bar (a prop scene): its colliders go on the door layer while it's down.
@export var bar: Node3D


## Open by day: unbarred, unlocked, both leaves open, at once.
func stand_open() -> void:
	show_bar(false)
	for leaf in leaves:
		leaf.locked = false
		leaf.set_open(true, true)


## Opens or shuts both leaves (shut, they lock); await it.
func swing(open: bool) -> void:
	for leaf in leaves:
		leaf.locked = not open
		leaf.set_open(open)
	await get_tree().create_timer(leaves[0].open_time + 0.1, false, true).timeout


func show_bar(down: bool) -> void:
	bar.visible = down
	for body in bar.find_children("*", "CollisionObject3D", true, false):
		(body as CollisionObject3D).collision_layer = Layers.DOOR if down else 0


func is_open() -> bool:
	return leaves.any(func(leaf: Door) -> bool: return leaf.is_open)
