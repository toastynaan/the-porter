class_name Brother
extends Node3D
## A brother (or anyone else) the night places by phase: on each phase change
## he goes to the Marker3D named after him under `places`/<Phase name>
## (e.g. Places/Supper/Thomas), or out of the world if there is none. He only
## moves while the porter isn't looking at him or where he is going, so
## nobody appears or vanishes in view. Beats move him directly with place().

@export var places: Node3D

var _moving := false
## Where he is going: a Transform3D, or null for out of the world.
var _target: Variant = null

## How he looks (a DualRender may stand in instead).
@onready var look := get_node_or_null(^"Look") as CharacterLook
@onready var _shape: CollisionShape3D = $Body/Shape


func _ready() -> void:
	add_to_group(&"brothers")
	($Body as StaticBody3D).collision_layer = Layers.CAPSULE
	($Body as StaticBody3D).collision_mask = 0
	GameState.phase_changed.connect(_on_phase)
	_on_phase(GameState.phase)
	_set_place(_target)
	_moving = false


## Puts him at `xform` now (or null: out of the world), watched or not.
func place(xform: Variant) -> void:
	_moving = false
	_set_place(xform)


## Where his face is, for the conversation camera.
func face_position() -> Vector3:
	return look.face_position() if look else global_position + Vector3.UP * 1.6


## Turns him to face `point`.
func face(point: Vector3) -> void:
	var to := point - global_position
	rotation.y = atan2(-to.x, -to.z)


func _process(_delta: float) -> void:
	if not _moving:
		return
	var camera := get_viewport().get_camera_3d()
	if camera:
		if visible and _seen(camera, global_position):
			return
		if _target is Transform3D and _seen(camera, (_target as Transform3D).origin):
			return
	_moving = false
	_set_place(_target)


func _on_phase(phase: GameState.Phase) -> void:
	var marker: Node3D = null
	if places:
		var group := places.get_node_or_null(NodePath(GameState.Phase.keys()[phase].capitalize()))
		if group:
			marker = group.get_node_or_null(NodePath(name))
	_target = null
	if marker:
		_target = marker.global_transform
	_moving = true


func _set_place(xform: Variant) -> void:
	if xform is Transform3D:
		global_transform = xform
		visible = true
		_shape.disabled = false
	else:
		visible = false
		_shape.disabled = true


func _seen(camera: Camera3D, at: Vector3) -> bool:
	return ViewCheck.on_screen(camera, [at + Vector3.UP * 1.6, at + Vector3.UP * 0.8])
