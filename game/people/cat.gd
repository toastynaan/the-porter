class_name Cat
extends CharacterBody3D
## The abbey cat (docs/log/full-game-run.md, "The cat"; design doc, "Animals as
## tells"): it follows the porter on his rounds, a few steps off; now and
## then it stops and stares into a dark corner, and sometimes a man is
## standing there (the nearest hunter within `stare_range`, waiting or not);
## and it runs before the demon: when the animals go quiet (the "room_tone"
## group), it hisses and bolts away from him and is gone until it's over.

enum Mode { FOLLOW, STARE, FLEE, GONE }

const HISS := preload("res://art/sfx/sfx_cat_hiss.wav")
const MEOW := preload("res://art/sfx/sfx_cat_0.wav")
const WALK := 1.6
const TROT := 3.6
## It keeps this far from him, m.
const GAP := Vector2(1.8, 3.2)
const STARE_TIME := 4.0
const FLEE_DISTANCE := 14.0

## Follows from this hour (the night's hours); before it, it keeps to itself.
@export var from_hour := 0.0
## Seconds between stares.
@export var stare_every := Vector2(35.0, 70.0)
@export var stare_range := 10.0

var mode := Mode.FOLLOW
## What it stares at, while it stares.
var staring_at := Vector3.ZERO

var _stare_timer := 30.0
var _mode_time := 0.0
var _audio: AudioStreamPlayer3D
var _rng := RandomNumberGenerator.new()

@onready var agent: NavigationAgent3D = $Agent


func _ready() -> void:
	add_to_group(&"cat")
	add_to_group(&"room_tone")
	collision_layer = 0
	collision_mask = Layers.WORLD
	_audio = AudioStreamPlayer3D.new()
	_audio.unit_size = 3.0
	add_child(_audio)
	_stare_timer = _rng.randf_range(stare_every.x, stare_every.y)


## The animals go quiet before the demon: the cat runs.
func set_quiet(on: bool, _full := false) -> void:
	if on and mode != Mode.FLEE and mode != Mode.GONE:
		_flee()
	elif not on and mode == Mode.GONE:
		_set_mode(Mode.FOLLOW)
		visible = true


func _physics_process(delta: float) -> void:
	var p := get_tree().get_first_node_in_group(&"player") as Player
	if p == null:
		return
	_mode_time += delta
	var target := Vector3.INF
	var speed := WALK
	match mode:
		Mode.FOLLOW:
			if GameState.hour < from_hour:
				return
			var d := global_position.distance_to(p.global_position)
			if d > GAP.y:
				target = p.global_position
				speed = TROT if d > 8.0 else WALK
			_stare_timer -= delta
			if _stare_timer <= 0.0:
				_stare_timer = _rng.randf_range(stare_every.x, stare_every.y)
				stare()
		Mode.STARE:
			_face(staring_at)
			if _mode_time > STARE_TIME:
				_set_mode(Mode.FOLLOW)
		Mode.FLEE:
			target = agent.target_position
			speed = TROT
			if agent.is_navigation_finished() or _mode_time > 6.0:
				visible = false
				_set_mode(Mode.GONE)
		Mode.GONE:
			return
	var flat := Vector3.ZERO
	if target != Vector3.INF:
		if agent.target_position.distance_to(target) > 0.5:
			agent.target_position = target
		var next := agent.get_next_path_position()
		var to := next - global_position
		to.y = 0.0
		if to.length() > 0.05 and not agent.is_navigation_finished():
			flat = to.normalized() * speed
	velocity.x = flat.x
	velocity.z = flat.z
	velocity.y = 0.0 if is_on_floor() else velocity.y - 9.8 * delta
	move_and_slide()
	if flat.length() > 0.1:
		rotation.y = lerp_angle(rotation.y, atan2(-flat.x, -flat.z), 1.0 - exp(-8.0 * delta))


## Stops and stares into the dark: at a man standing there if one is near,
## or at nothing.
func stare() -> void:
	var nearest: Node3D = null
	for h: Hunter in get_tree().get_nodes_in_group(&"hunters"):
		var d := h.global_position.distance_to(global_position)
		if d < stare_range and (nearest == null or d < nearest.global_position.distance_to(global_position)):
			nearest = h
	if nearest:
		staring_at = nearest.global_position
	else:
		var a := _rng.randf_range(-PI, PI)
		staring_at = global_position + Vector3(sin(a), 0.0, cos(a)) * 4.0
	_set_mode(Mode.STARE)
	if AudioOut.enabled():
		_audio.stream = MEOW
		_audio.play()


func _flee() -> void:
	var p := get_tree().get_first_node_in_group(&"player") as Player
	var away := (global_position - p.global_position) if p else Vector3.FORWARD
	away.y = 0.0
	if away.length() < 0.1:
		away = Vector3.FORWARD
	var map := get_world_3d().navigation_map
	agent.target_position = NavigationServer3D.map_get_closest_point(map, global_position + away.normalized() * FLEE_DISTANCE)
	_set_mode(Mode.FLEE)
	if AudioOut.enabled():
		_audio.stream = HISS
		_audio.play()


func _set_mode(m: Mode) -> void:
	mode = m
	_mode_time = 0.0


func _face(at: Vector3) -> void:
	var to := at - global_position
	if Vector2(to.x, to.z).length() > 0.05:
		rotation.y = atan2(-to.x, -to.z)
