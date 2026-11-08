class_name Brother
extends Node3D
## A brother (or anyone else) the night places by phase: on each phase change
## he goes to the Marker3D named after him under `places`/<Phase name>
## (e.g. Places/Supper/Thomas). He only moves there while the porter isn't
## looking at him or where he is going, so nobody appears or vanishes in
## view. Beats move him directly with place().
##
## Where a phase has no place for him, he keeps his `Routine` (a child of
## that name): he walks from stop to stop by the hour, in view, lights his
## window, locks his door, goes to bed. With no routine he's out of the
## world for that phase.

@export var places: Node3D

const WALK := 1.2

## The routine stop he is at or walking to.
var stop: Marker3D
## Walking his routine now.
var walking := false

var _moving := false
var _routine_on := false
var _path := PackedVector3Array()
var _lit: Candle
## Where he is going: a Transform3D, or null for out of the world.
var _target: Variant = null

## How he looks (a DualRender may stand in instead).
@onready var look := get_node_or_null(^"Look") as CharacterLook
@onready var routine := get_node_or_null(^"Routine") as Routine
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
	_routine_on = false
	walking = false
	_set_place(xform)


## Where his face is, for the conversation camera.
func face_position() -> Vector3:
	return look.face_position() if look else global_position + Vector3.UP * 1.6


## Turns him to face `point`.
func face(point: Vector3) -> void:
	var to := point - global_position
	rotation.y = atan2(-to.x, -to.z)


func _process(delta: float) -> void:
	if _routine_on:
		_keep_routine(delta)
		return
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


## Dead (died_<name>, from a DeathScene on this night or one before): out of
## the world for good.
func is_dead() -> bool:
	return GameState.has_flag(StringName("died_" + String(name).to_lower()))


func _on_phase(phase: GameState.Phase) -> void:
	# A level on its way out still hears the new night's phases.
	if not is_inside_tree():
		return
	var marker: Node3D = null
	if places:
		var group := places.get_node_or_null(NodePath(GameState.Phase.keys()[phase].capitalize()))
		if group:
			marker = group.get_node_or_null(NodePath(name))
	_target = null
	if marker and not is_dead():
		_target = marker.global_transform
	_routine_on = marker == null and routine != null and not is_dead()
	if _routine_on:
		stop = null
		return
	_moving = true


## His routine: the stop for the hour; walk there in view; at it, his light
## on and his door locked; an "away" stop, out of sight once unseen.
func _keep_routine(delta: float) -> void:
	var want := routine.stop_for(GameState.hour)
	if want == null:
		return
	if want != stop:
		_leave_stop()
		stop = want
		if not visible:
			# Out of the world (asleep): he comes out where he went in, unseen.
			var camera := get_viewport().get_camera_3d()
			if camera and _seen(camera, global_position):
				stop = null
				return
			_set_place(global_transform)
		var map := get_world_3d().navigation_map
		_path = NavigationServer3D.map_get_path(map, global_position, stop.global_position, true)
		walking = true
	if walking:
		_walk(delta)
		return
	if bool(stop.get_meta(&"away", false)) and visible:
		var camera := get_viewport().get_camera_3d()
		if camera == null or not _seen(camera, global_position):
			_set_place(null)


func _walk(delta: float) -> void:
	var step := WALK * delta
	while step > 0.0 and not _path.is_empty():
		var to := _path[0] - global_position
		if to.length() <= step:
			global_position = _path[0]
			step -= to.length()
			_path.remove_at(0)
		else:
			global_position += to.normalized() * step
			if Vector2(to.x, to.z).length() > 0.01:
				rotation.y = atan2(-to.x, -to.z)
			step = 0.0
	if _path.is_empty():
		walking = false
		global_rotation.y = stop.global_rotation.y
		_arrive()


func _arrive() -> void:
	var light := stop.get_node_or_null(stop.get_meta(&"light", NodePath(""))) as Candle if stop.has_meta(&"light") else null
	if light:
		light.lit = true
		_lit = light
	var door := stop.get_node_or_null(stop.get_meta(&"lock", NodePath(""))) as Door if stop.has_meta(&"lock") else null
	if door:
		if door.is_open:
			door.set_open(false, true)
		door.locked = true


func _leave_stop() -> void:
	if _lit:
		_lit.lit = false
		_lit = null


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
