@tool
class_name Duty
extends Area3D
## Something the night asks the porter to use: the gate bar, the grate, the
## bell rope, the bread, a door to check on the round. Look at it and press
## `interact` while it is `enabled` and it emits `used`; the beat that
## enabled it awaits that. Disabled, the view ray passes through it. The box
## (`size`) stands on the origin.
##
## The world shows the way: while it is wanted its `lamp` burns (put out
## again after unless `keep_lit`), and the doors on the way to it from the
## porter stand open with a lamp over each (Wayfinding). The almost-no HUD
## adds two quiet marks (docs/mechanics.md, "The minimal HUD"): the outline
## on `outline` (the prop it stands for) while he looks at it in reach, and
## the faint duty glyph over it while it is wanted (group "glyph_targets").

signal used(by: Node)

@export var enabled := false:
	set(value):
		var was := enabled
		enabled = value
		collision_layer = Layers.INTERACT if value else 0
		if value != was and is_inside_tree() and not Engine.is_editor_hint():
			_show_way(value)
@export var size := Vector3(0.6, 0.6, 0.6):
	set(value):
		size = value
		_build()
## Lit while the duty is wanted, so the porter can find it.
@export var lamp: Candle
## The lamp stays lit once the duty is done (a lamp he checks is burning).
@export var keep_lit := false
## Lights the way to it when it becomes wanted.
@export var open_way := true
## What the outline goes on: the prop the duty stands for (its own meshes if empty).
@export var outline: Array[Node3D] = []
## Height of the duty glyph over the origin, m (below 0: just over the box).
@export var glyph_height := -1.0

var _way: Array[Node3D] = []

var _shape: CollisionShape3D


func _ready() -> void:
	if not Engine.is_editor_hint():
		add_to_group(&"duties")
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


func _show_way(wanted: bool) -> void:
	if wanted:
		add_to_group(&"glyph_targets")
	else:
		remove_from_group(&"glyph_targets")
	if lamp:
		lamp.lit = wanted or keep_lit
	Wayfinding.put_out(_way)
	if wanted and open_way:
		_way = Wayfinding.show_way(self, global_position)


## Where the duty glyph floats.
func glyph_point() -> Vector3:
	return global_position + Vector3.UP * (glyph_height if glyph_height >= 0.0 else size.y + 0.15)


func interact(by: Node) -> void:
	if enabled:
		used.emit(by)


## Enables it and waits until the porter uses it, then disables it again.
func wait_for_use() -> void:
	enabled = true
	await used
	enabled = false
