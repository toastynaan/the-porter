@tool
class_name Duty
extends Area3D
## Something the night asks the porter to use: the gate bar, the grate, the
## bell rope, the bread, a door to check on the round. Look at it and press
## `interact` while it is `enabled` and it emits `used`; the beat that
## enabled it awaits that. Disabled, the view ray passes through it. The box
## (`size`) stands on the origin.

signal used(by: Node)

@export var enabled := false:
	set(value):
		enabled = value
		collision_layer = Layers.INTERACT if value else 0
@export var size := Vector3(0.6, 0.6, 0.6):
	set(value):
		size = value
		_build()

var _shape: CollisionShape3D


func _ready() -> void:
	collision_mask = 0
	monitoring = false
	collision_layer = Layers.INTERACT if enabled else 0
	_build()


func _build() -> void:
	if not is_inside_tree():
		return
	if _shape == null:
		_shape = CollisionShape3D.new()
		add_child(_shape)
	var box := BoxShape3D.new()
	box.size = size
	_shape.shape = box
	_shape.position = Vector3(0.0, size.y * 0.5, 0.0)


func interact(by: Node) -> void:
	if enabled:
		used.emit(by)


## Enables it and waits until the porter uses it, then disables it again.
func wait_for_use() -> void:
	enabled = true
	await used
	enabled = false
