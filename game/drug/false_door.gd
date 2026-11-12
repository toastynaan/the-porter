class_name FalseDoor
extends Node3D
## The HUD lies once (docs/systems/mechanics.md, "The minimal HUD"): on night 5 or 6,
## only at Dose 75+, the outline shows on a door in a blank wall. The slab
## is the wall's own stone, so only its outline can be seen. Use it and it
## swings open on more stone behind it, and is gone. Only ever once.

@export var nights: Array[int] = [5, 6]
@export var dose_from := 75.0
@export var size := Vector2(0.9, 2.0)
@export var material: Material

## Its slab, for the outline (Outline reads `outline`).
var outline: Array[Node3D]:
	get:
		return [_slab]

var _slab: MeshInstance3D
var _area: Area3D
var _hinge: Node3D
var _opened := false


func _ready() -> void:
	add_to_group(&"false_doors")
	_hinge = Node3D.new()
	_hinge.position = Vector3(-size.x * 0.5, 0.0, 0.0)
	add_child(_hinge)
	_slab = MeshInstance3D.new()
	var box := BoxMesh.new()
	box.size = Vector3(size.x, size.y, 0.05)
	_slab.mesh = box
	if material:
		_slab.material_override = material
	_slab.position = Vector3(size.x * 0.5, size.y * 0.5, 0.0)
	_hinge.add_child(_slab)
	_area = Area3D.new()
	_area.collision_mask = 0
	_area.monitoring = false
	var shape := CollisionShape3D.new()
	var b := BoxShape3D.new()
	b.size = Vector3(size.x, size.y, 0.3)
	shape.shape = b
	shape.position = Vector3(0.0, size.y * 0.5, 0.1)
	_area.add_child(shape)
	add_child(_area)
	_refresh()


## The lie can be told now.
func telling() -> bool:
	return not _opened and not GameState.has_flag(&"hud_lie_told") and nights.has(GameState.night) \
		and GameState.dose >= dose_from


func _process(_delta: float) -> void:
	_refresh()


func _refresh() -> void:
	var on := telling()
	_area.collision_layer = Layers.INTERACT if on else 0
	visible = on or _opened


func interact(_by: Node) -> void:
	if not telling():
		return
	_opened = true
	GameState.set_flag(&"hud_lie_told")
	var swing := create_tween()
	swing.tween_property(_hinge, ^"rotation:y", deg_to_rad(-100.0), 1.2).set_trans(Tween.TRANS_SINE)
	await Talk.say("", "(It swings open on stone. There was never a door here.)")
	await swing.finished
	queue_free()
