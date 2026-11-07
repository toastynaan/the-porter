@tool
class_name Door
extends Node3D
## A heavy door on a hinge. The node sits at the doorway's bottom centre in
## the wall's plane, local X along the wall; the leaf hangs on the wall's
## +Z face (`leaf_offset` from the centre plane) and swings to that side
## (turn the node 180 degrees for the other side). Open, it folds back
## nearly flat against the wall, so it never blocks a path along the wall;
## looking at the doorway from either side reaches it to close it. Doors are heavy: opening takes `open_time` (Look and Feel,
## "Camera and player feel"). A locked door rattles. An open door is a
## draught: the lantern gutters near it.
##
## The leaf is on the DOOR physics layer, which the navmesh bake leaves out,
## so a doorway is always open to navigation; hunters open doors (M3). The
## leaf's body is itself the hinge: an AnimatableBody3D only carries its
## collision along when its own transform changes, not its parent's.

signal toggled(open: bool)

const OPEN_SOUND := preload("res://art/sfx/sfx_door_open.wav")
const CLOSE_SOUND := preload("res://art/sfx/sfx_door_close.wav")
const LOCKED_SOUND := preload("res://art/sfx/sfx_door_locked.wav")
const LEAF_THICKNESS := 0.08

@export var size := Vector2(0.9, 2.0):
	set(value):
		size = value
		_build()
@export var hinge_right := false:
	set(value):
		hinge_right = value
		_build()
## Distance of the hinge from the wall's centre plane, toward +Z: the face
## of a 0.8 m wall plus half the leaf.
@export var leaf_offset := 0.44:
	set(value):
		leaf_offset = value
		_build()
@export var open_angle := 170.0
@export var open_time := 0.6
@export var locked := false
@export var start_open := false
## Oak by default; hidden doors take the material of the wall around them.
@export var material: Material:
	set(value):
		material = value
		_build()

var is_open := false

var _leaf: AnimatableBody3D
var _mesh: MeshInstance3D
var _shape: CollisionShape3D
var _opening: CollisionShape3D
var _audio: AudioStreamPlayer3D
var _tween: Tween


func _ready() -> void:
	add_to_group(&"doors")
	_build()
	if start_open:
		set_open(true, true)


func _build() -> void:
	if not is_inside_tree():
		return
	if _leaf == null:
		_leaf = AnimatableBody3D.new()
		_leaf.collision_layer = Layers.DOOR
		_leaf.collision_mask = 0
		# Move straight to the new transform: with physics sync the body
		# lags the node and misses the hinge offset.
		_leaf.sync_to_physics = false
		add_child(_leaf)
		_mesh = MeshInstance3D.new()
		_leaf.add_child(_mesh)
		_shape = CollisionShape3D.new()
		_leaf.add_child(_shape)
		var area := Area3D.new()
		area.collision_layer = Layers.INTERACT
		area.collision_mask = 0
		area.monitoring = false
		add_child(area)
		_opening = CollisionShape3D.new()
		area.add_child(_opening)
		_audio = AudioStreamPlayer3D.new()
		_audio.position = Vector3(0, 1.2, leaf_offset)
		add_child(_audio)
	var side := 1.0 if hinge_right else -1.0
	_leaf.position = Vector3(side * size.x * 0.5, 0, leaf_offset)
	_mesh.position = Vector3(-side * size.x * 0.5, size.y * 0.5, 0)
	_shape.position = _mesh.position
	var box := BoxMesh.new()
	box.size = Vector3(size.x - 0.02, size.y - 0.02, LEAF_THICKNESS)
	box.material = material if material else preload("res://game/world/materials/oak.tres")
	_mesh.mesh = box
	var bs := BoxShape3D.new()
	bs.size = box.size
	_shape.shape = bs
	var hole := BoxShape3D.new()
	hole.size = Vector3(size.x, size.y, 0.8)
	_opening.shape = hole
	_opening.position = Vector3(0, size.y * 0.5, 0)


func interact(_by: Node) -> void:
	if locked:
		_play(LOCKED_SOUND)
		return
	set_open(not is_open)


func set_open(open: bool, instant := false) -> void:
	is_open = open
	var target := deg_to_rad(open_angle if open else 0.0) * (1.0 if hinge_right else -1.0)
	if _tween:
		_tween.kill()
	if instant:
		_leaf.rotation.y = target
	else:
		_tween = create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		_tween.tween_property(_leaf, ^"rotation:y", target, open_time)
		_play(OPEN_SOUND if open else CLOSE_SOUND)
	toggled.emit(open)


func _play(stream: AudioStream) -> void:
	if not AudioOut.enabled():
		return
	_audio.stream = stream
	_audio.play()
