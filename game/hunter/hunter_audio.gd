extends Node3D
## What the porter hears of a hunter (Look and Feel, "Sound feel"): felt
## overshoes on his rounds, barely there, and the chant hummed under his
## breath; carved hoof soles when he runs, the loudest sound in the game;
## panting when winded; rummaging when he checks a hiding spot. In the rain
## they carry half as far (Weather.hearing_factor). In the snow his steps
## leave prints (Footprints).
## (Placeholder synthesised sounds, art/sfx/.)

const HOOVES: Array[AudioStream] = [preload("res://art/sfx/sfx_hoof_0.wav"),
	preload("res://art/sfx/sfx_hoof_1.wav"), preload("res://art/sfx/sfx_hoof_2.wav")]
const FELT: Array[AudioStream] = [preload("res://art/sfx/sfx_felt_0.wav"),
	preload("res://art/sfx/sfx_felt_1.wav"), preload("res://art/sfx/sfx_felt_2.wav")]
const HUM := preload("res://art/sfx/sfx_hum_loop.wav")
const PANT := preload("res://art/sfx/sfx_pant_loop.wav")
const RUMMAGE := preload("res://art/sfx/sfx_rummage.wav")
const STRIDE_WALK := 0.8
const STRIDE_RUN := 1.5

var _steps: AudioStreamPlayer3D
var _hum: AudioStreamPlayer3D
var _pant: AudioStreamPlayer3D
var _rummage: AudioStreamPlayer3D
var _travel := 0.0

@onready var _hunter: Hunter = owner


func _ready() -> void:
	_steps = _player(null, 0.0, 4.0)
	_hum = _player(AudioOut.looped(HUM), -8.0, 3.0)
	_pant = _player(AudioOut.looped(PANT), -4.0, 3.0)
	_rummage = _player(RUMMAGE, -2.0, 4.0)
	_hunter.checking.connect(func(_spot: HidingSpot) -> void: _play(_rummage))


func _player(stream: AudioStream, db: float, unit: float) -> AudioStreamPlayer3D:
	var p := AudioStreamPlayer3D.new()
	p.stream = stream
	p.volume_db = db
	p.unit_size = unit
	add_child(p)
	return p


func _process(delta: float) -> void:
	var carry := Weather.hearing_factor(get_tree())
	for p in [_steps, _hum, _pant, _rummage]:
		(p as AudioStreamPlayer3D).max_distance = 60.0 * carry
	if not AudioOut.enabled() or _hunter.dormant:
		_stop_all()
		return
	var chasing := _hunter.state == Hunter.State.CHASE
	_loop(_hum, _hunter.state == Hunter.State.PATROL)
	_loop(_pant, _hunter.winded > 0.0)
	var speed := Vector2(_hunter.velocity.x, _hunter.velocity.z).length()
	_travel += speed * delta
	var stride := STRIDE_RUN if speed > 2.5 else STRIDE_WALK
	if _travel >= stride:
		_travel = 0.0
		var snow := get_tree().get_first_node_in_group(&"footprints") as Footprints
		if snow:
			snow.leave(_hunter.global_position, _hunter.rotation.y, &"hunter")
		_steps.stream = (HOOVES if chasing else FELT).pick_random()
		_steps.volume_db = 2.0 if chasing else -10.0
		_steps.pitch_scale = randf_range(0.92, 1.08)
		_steps.play()


func _loop(p: AudioStreamPlayer3D, on: bool) -> void:
	if on and not p.playing:
		p.play()
	elif not on and p.playing:
		p.stop()


func _play(p: AudioStreamPlayer3D) -> void:
	if AudioOut.enabled():
		p.play()


func _stop_all() -> void:
	for p: AudioStreamPlayer3D in [_hum, _pant]:
		if p.playing:
			p.stop()
