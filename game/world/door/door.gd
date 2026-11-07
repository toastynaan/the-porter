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
## A door with a `key` can be locked and unlocked (`lock` action) by whoever
## holds that key (GameState.keys), from either side, while it is shut.
## Opening, shutting and rattling are loud (Earshot.DOOR).
##
## The leaf is on the DOOR physics layer, which the navmesh bake leaves out,
## so a doorway is always open to navigation. Hunters open doors themselves
## and are stopped by locked ones (crosses() tells them a path goes through).
## The leaf's body is itself the hinge: an AnimatableBody3D only carries its
## collision along when its own transform changes, not its parent's.

signal toggled(open: bool)

const OPEN_SOUND := preload("res://art/sfx/sfx_door_open.wav")
const CLOSE_SOUND := preload("res://art/sfx/sfx_door_close.wav")
const LOCKED_SOUND := preload("res://art/sfx/sfx_door_locked.wav")
const KEY_SOUND := preload("res://art/sfx/sfx_key_turn.wav")
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
## The key that locks and unlocks it (GameState.keys), or empty for none.
@export var key := &""
@export var start_open := false
## Oak by default; hidden doors take the material of the wall around them.
@export var material: Material:
	set(value):
		material = value
		_build()
## An iron grille you can see through (the street gate) instead of a solid
## leaf. It blocks and locks the same.
@export var grille := false:
	set(value):
		grille = value
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
	if grille:
		_mesh.mesh = _grille_mesh(box.size)
	else:
		_mesh.mesh = box
	var bs := BoxShape3D.new()
	bs.size = box.size
	_shape.shape = bs
	var hole := BoxShape3D.new()
	hole.size = Vector3(size.x, size.y, 0.8)
	_opening.shape = hole
	_opening.position = Vector3(0, size.y * 0.5, 0)


## Vertical bars with spiked tops between three rails, filling `leaf`.
func _grille_mesh(leaf: Vector3) -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var bar := BoxMesh.new()
	var bars := maxi(2, floori(leaf.x / 0.14))
	for i in bars + 1:
		var x := -leaf.x * 0.5 + leaf.x * i / bars
		bar.size = Vector3(0.035, leaf.y, 0.035)
		st.append_from(bar, 0, Transform3D(Basis.IDENTITY, Vector3(x, 0, 0)))
		bar.size = Vector3(0.05, 0.12, 0.05)
		st.append_from(bar, 0, Transform3D(Basis(Vector3.FORWARD, PI * 0.25), Vector3(x, leaf.y * 0.5 + 0.06, 0)))
	for y in [-0.42, 0.0, 0.42]:
		bar.size = Vector3(leaf.x, 0.05, 0.045)
		st.append_from(bar, 0, Transform3D(Basis.IDENTITY, Vector3(0, leaf.y * y, 0)))
	st.set_material(preload("res://game/world/materials/iron.tres"))
	return st.commit()


func interact(_by: Node) -> void:
	if locked:
		rattle()
		return
	set_open(not is_open)


## Locks or unlocks it with its key, if the porter holds that key and the
## door is shut. Returns whether the key turned.
func toggle_lock(_by: Node = null) -> bool:
	if key.is_empty() or is_open or not GameState.keys.has(key):
		return false
	locked = not locked
	_play(KEY_SOUND)
	Earshot.make(self, global_position + Vector3.UP, Earshot.KEY, self)
	return true


## Someone tries a locked door.
func rattle() -> void:
	_play(LOCKED_SOUND)
	Earshot.make(self, global_position + Vector3.UP, Earshot.DOOR, self)


## True if the segment from `a` to `b` passes through this doorway.
func crosses(a: Vector3, b: Vector3) -> bool:
	var inv := global_transform.affine_inverse()
	var la := inv * a
	var lb := inv * b
	if signf(la.z) == signf(lb.z) or is_equal_approx(la.z, lb.z):
		return false
	var hit := la.lerp(lb, la.z / (la.z - lb.z))
	return absf(hit.x) <= size.x * 0.5 + 0.2 and hit.y > -1.0 and hit.y < size.y + 0.5


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
		Earshot.make(self, global_position + Vector3.UP, Earshot.DOOR, self)
	toggled.emit(open)


func _play(stream: AudioStream) -> void:
	if not AudioOut.enabled():
		return
	_audio.stream = stream
	_audio.play()
