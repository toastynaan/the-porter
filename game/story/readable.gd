class_name Readable
extends Node3D
## Something to read (the cult's book on night 3, a letter): look at it and
## press `interact`. The porter holds up the page (PageView) and, if it's
## something to `take`, it goes in his satchel as `item`. Reading it writes
## `clue` in his notes and sets read_<id>.

signal read

@export var id := &""
@export var title := ""
@export_multiline var text := ""
## Taken into the satchel (and gone from here) as this item, if set.
@export var item := &""
@export var clue := &""
@export var size := Vector3(0.4, 0.15, 0.4)

var _area: Area3D


func _ready() -> void:
	add_to_group(&"readables")
	if not item.is_empty() and GameState.satchel.has(item):
		visible = false
	_area = Area3D.new()
	_area.collision_layer = Layers.INTERACT if visible else 0
	_area.collision_mask = 0
	_area.monitoring = false
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = size
	shape.shape = box
	shape.position = Vector3(0, size.y * 0.5, 0)
	_area.add_child(shape)
	add_child(_area)


func interact(_by: Node) -> void:
	var view := get_tree().get_first_node_in_group(&"page_view") as PageView
	if view:
		view.show_page(title, text)
	GameState.set_flag(StringName("read_" + String(id)))
	if clue != &"":
		GameState.note(clue)
	if not item.is_empty() and not GameState.satchel.has(item):
		GameState.satchel.append(item)
		visible = false
		_area.collision_layer = 0
	read.emit()
