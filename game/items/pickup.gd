class_name Pickup
extends Node3D
## Something lying about that the porter can take (docs/mechanics.md, "Your
## hands"): a windfall apple under the orchard trees, a stone to throw. Look
## at it and press `interact`. Clean food eaten now if he's hungry (hunger
## ends for the night, no Dose), else it goes in his satchel; something to
## throw goes in his hand (one at a time). Taken, it's gone for the night
## (picked_<id>).

const BITE := preload("res://art/sfx/sfx_bite.wav")

@export var id := &""
## What it is (Items).
@export var item := &"apple"
@export var size := Vector3(0.3, 0.25, 0.3)

var _area: Area3D


func _ready() -> void:
	add_to_group(&"pickups")
	if GameState.has_flag(_flag()):
		visible = false
	_area = Area3D.new()
	_area.collision_layer = Layers.INTERACT if visible else 0
	_area.collision_mask = 0
	_area.monitoring = false
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = size
	shape.shape = box
	shape.position = Vector3(0.0, size.y * 0.5, 0.0)
	_area.add_child(shape)
	add_child(_area)


func _flag() -> StringName:
	return GameState.tonight("picked_" + String(id))


## Here to take tonight.
func available() -> bool:
	return visible and not GameState.has_flag(_flag())


func interact(_by: Node) -> void:
	if not available():
		return
	GameState.set_flag(_flag())
	visible = false
	_area.collision_layer = 0
	if Items.kind(item) == &"food" and GameState.is_hungry():
		eat(item, self)
	elif Items.kind(item) == &"throwable":
		# One in his hand at a time: the old one is dropped for this.
		var old := Player.held()
		if old != &"":
			GameState.satchel.erase(old)
		GameState.satchel.append(item)
		Talk.say("", "(%s, in your hand.)" % Items.display_name(item))
	elif not GameState.satchel.has(item):
		GameState.satchel.append(item)
		Talk.say("", "(%s, in your satchel.)" % Items.display_name(item))


## Eats `item` now: clean food ends his hunger for the night.
static func eat(what: StringName, from: Node) -> void:
	GameState.satchel.erase(what)
	GameState.eat_clean()
	if AudioOut.enabled() and from.is_inside_tree():
		var a := AudioStreamPlayer.new()
		a.stream = BITE
		from.get_tree().root.add_child(a)
		a.play()
		a.finished.connect(a.queue_free)
	Talk.say("", "(You eat %s. Nothing the abbey baked.)" % Items.display_name(what).to_lower())
