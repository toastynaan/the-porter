class_name HorseGait
extends Node3D
## Walks the cart horse (art/models/chr_horse.glb, tools/build/chr_horse.py)
## by how far it is carried: whatever moves it along (the wagon on the road
## in), its legs keep step with the ground. A walk below `trot_from` m/s, a
## trot above it. Its parts turn about their joints; the pose is set
## `steps` times a second, stepped, like the game's people (Look and Feel,
## "Characters": 15 fps). Standing, it shifts its weight now and then, and
## its tail and ears stir.

## Metres of ground for one full stride, at a walk and at a trot.
@export var walk_stride := 1.75
@export var trot_stride := 2.3
@export var trot_from := 2.3
## Poses a second.
@export var steps := 15.0
## How far the legs swing, radians, at a walk and at a trot.
@export var swing := Vector2(0.34, 0.46)

## Where it is in its stride, 0..1.
var phase := 0.0
## How fast it is being carried, m/s.
var speed := 0.0

var _last := Vector3.ZERO
var _clock := 0.0
var _idle := 0.0
var _body: Node3D
var _neck: Node3D
var _tail: Node3D
## Each leg: [upper, lower, hind, side].
var _legs: Array = []
var _body_y := 0.0


func _ready() -> void:
	_body = find_child("Body", true, false) as Node3D
	if _body == null:
		return
	_body_y = _body.position.y
	_neck = _body.find_child("Neck", true, false) as Node3D
	_tail = _body.find_child("Tail", true, false) as Node3D
	for leg: String in ["FL", "FR", "HL", "HR"]:
		var upper := _body.find_child("Leg" + leg, true, false) as Node3D
		var lower := upper.find_child("Shin" + leg, true, false) as Node3D if upper else null
		if upper and lower:
			_legs.append([upper, lower, leg.begins_with("H"), leg.ends_with("L")])
	_last = global_position


func _physics_process(delta: float) -> void:
	if _body == null or delta <= 0.0:
		return
	# How far it has gone along its own nose (a jump is not a stride).
	var moved := (global_position - _last).dot(-global_basis.z)
	_last = global_position
	if absf(moved) > 2.0:
		moved = 0.0
	speed = lerpf(speed, moved / delta, 0.2)
	var trot := speed > trot_from
	phase = fposmod(phase + moved / (trot_stride if trot else walk_stride), 1.0)
	_idle += delta
	_clock += delta
	if _clock < 1.0 / steps:
		return
	_clock = fmod(_clock, 1.0 / steps)
	_pose(trot)


func _pose(trot: bool) -> void:
	var going := clampf(absf(speed) / 0.6, 0.0, 1.0)
	var reach := (swing.y if trot else swing.x) * going
	for leg: Array in _legs:
		var hind: bool = leg[2]
		var left: bool = leg[3]
		# A walk goes round the four legs in turn; a trot moves them in diagonal pairs.
		var offset := 0.0
		if trot:
			offset = 0.0 if left != hind else 0.5
		else:
			offset = (0.0 if left else 0.5) + (0.0 if hind else 0.25)
		var t := fposmod(phase + offset, 1.0)
		# On the ground for six tenths of the stride, going back; then lifted and brought forward.
		var on_ground := 0.6
		var angle := 0.0
		var bend := 0.0
		if t < on_ground:
			angle = lerpf(reach, -reach, t / on_ground)
		else:
			var u := (t - on_ground) / (1.0 - on_ground)
			angle = lerpf(-reach, reach, smoothstep(0.0, 1.0, u))
			bend = sin(u * PI) * (0.95 if trot else 0.7) * going
		(leg[0] as Node3D).rotation.x = angle
		# The knee folds back under it; the hock folds the other way.
		(leg[1] as Node3D).rotation.x = bend if hind else -bend
	var beat := sin(phase * TAU * 2.0)
	_body.position.y = _body_y + beat * (0.022 if trot else 0.012) * going
	if _neck:
		# Its head nods with its step; standing, it hangs lower.
		_neck.rotation.x = -beat * 0.05 * going - (1.0 - going) * (0.1 + 0.03 * sin(_idle * 0.31))
	if _tail:
		_tail.rotation.z = sin(phase * TAU) * 0.1 * going + (1.0 - going) * 0.25 * maxf(sin(_idle * 0.9) - 0.7, 0.0)
		_tail.rotation.x = -0.12 * going
