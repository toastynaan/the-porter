class_name Animals
extends Node3D
## The living part of the room tone (Look and Feel, "Sound feel": rats, the
## rooks, the abbey cat): a call from somewhere around the listener every few
## seconds, rooks outdoors and rats under a roof. They go quiet before the
## demon appears (set_quiet, the "room_tone" group). Placeholder sounds.

signal called(kind: StringName)

const ROOKS: Array[AudioStream] = [preload("res://art/sfx/sfx_rook_0.wav"),
	preload("res://art/sfx/sfx_rook_1.wav"), preload("res://art/sfx/sfx_rook_2.wav")]
const RATS: Array[AudioStream] = [preload("res://art/sfx/sfx_rat_0.wav"),
	preload("res://art/sfx/sfx_rat_1.wav"), preload("res://art/sfx/sfx_rat_2.wav")]
const CAT := preload("res://art/sfx/sfx_cat_0.wav")
## Seconds between calls.
const GAP := Vector2(2.5, 7.0)
## How far from the listener a call comes from, m.
const RANGE := Vector2(5.0, 18.0)
const CAT_CHANCE := 0.08
const ROOF_CHECK := 30.0

var quiet := false

var _timer := 3.0
var _pool: Array[AudioStreamPlayer3D] = []
var _next := 0


func _ready() -> void:
	add_to_group(&"room_tone")
	for i in 3:
		var p := AudioStreamPlayer3D.new()
		p.unit_size = 6.0
		add_child(p)
		_pool.append(p)


## Stops every call now and until set_quiet(false).
func set_quiet(on: bool, _full := false) -> void:
	quiet = on
	if on:
		for p in _pool:
			p.stop()
	else:
		_timer = randf_range(GAP.x, GAP.y)


func _process(delta: float) -> void:
	if quiet:
		return
	_timer -= delta
	if _timer > 0.0:
		return
	_timer = randf_range(GAP.x, GAP.y)
	var camera := get_viewport().get_camera_3d()
	if camera:
		_call(camera)


func _call(camera: Camera3D) -> void:
	var from := camera.global_position
	var query := PhysicsRayQueryParameters3D.create(from, from + Vector3.UP * ROOF_CHECK, Layers.WORLD)
	var indoors := not camera.get_world_3d().direct_space_state.intersect_ray(query).is_empty()
	var kind := &"cat" if randf() < CAT_CHANCE else (&"rat" if indoors else &"rook")
	called.emit(kind)
	if not AudioOut.enabled():
		return
	var p := _pool[_next]
	_next = (_next + 1) % _pool.size()
	var dir := Vector3.FORWARD.rotated(Vector3.UP, randf() * TAU)
	var at := from + dir * randf_range(RANGE.x, RANGE.y)
	at.y = from.y + (randf_range(6.0, 10.0) if kind == &"rook" else -1.4)
	p.global_position = at
	match kind:
		&"rook":
			p.stream = ROOKS.pick_random()
			p.volume_db = -10.0
		&"rat":
			p.stream = RATS.pick_random()
			p.volume_db = -16.0
		_:
			p.stream = CAT
			p.volume_db = -12.0
	p.play()
