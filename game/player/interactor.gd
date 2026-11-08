class_name Interactor
extends RayCast3D
## What the porter can reach: the first thing along the view within REACH
## whose node, or an ancestor, has interact(by). What is in reach gets the
## thin pale outline (Outline); `interact` uses it, and `lock` turns a key in
## it (toggle_lock(by)) when it has a lock.

signal focus_changed(target: Node)

const REACH := 2.0

var focused: Node

@onready var _player: Player = owner


func _ready() -> void:
	add_to_group(&"interactor")
	target_position = Vector3(0.0, 0.0, -REACH)
	collision_mask = Layers.WORLD | Layers.DOOR | Layers.INTERACT
	collide_with_areas = true
	add_exception(_player)


func _physics_process(_delta: float) -> void:
	var target: Node = null
	if is_colliding() and not _player.busy():
		target = _interactable(get_collider() as Node)
	if target != focused:
		Outline.set_on(focused, false)
		focused = target
		Outline.set_on(focused, true)
		focus_changed.emit(focused)


func _exit_tree() -> void:
	Outline.set_on(focused, false)


func _unhandled_input(event: InputEvent) -> void:
	# A click that only recaptures the mouse doesn't count.
	var click := event is InputEventMouseButton
	if event.is_action_pressed(&"interact") and focused and (not click or Input.mouse_mode == Input.MOUSE_MODE_CAPTURED):
		focused.interact(_player)
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed(&"lock") and focused and focused.has_method(&"toggle_lock"):
		focused.toggle_lock(_player)
		get_viewport().set_input_as_handled()


func _interactable(node: Node) -> Node:
	while node:
		if node.has_method(&"interact"):
			return node
		node = node.get_parent()
	return null
