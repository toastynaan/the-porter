class_name SelfLitCandle
extends Node3D
## One of the three things nothing explains (design doc, "The Hungry Saint"):
## on night 5 a candle in the crypt lights itself in front of the porter,
## with no one there, at any Dose. It lights once he has looked at it from
## close for a moment.

signal lit

@export var id := &"candle_lit_itself"
@export var look_time := 1.0
@export var reach := 5.0
## Only on these nights (empty: every night).
@export var nights: Array[int] = [5]

var _dwell := 0.0

@onready var candle: Candle = $Candle


func _ready() -> void:
	candle.lit = GameState.has_flag(id)


func _physics_process(delta: float) -> void:
	if candle.lit or (not nights.is_empty() and not nights.has(GameState.night)):
		return
	var p := get_tree().get_first_node_in_group(&"player") as Player
	if p == null:
		return
	var at := candle.global_position + Vector3.UP * 0.1
	var looking := p.camera.global_position.distance_to(at) < reach and ViewCheck.off_centre(p.camera, at) < 12.0 \
		and ViewCheck.on_screen(p.camera, [at])
	_dwell = _dwell + delta if looking else 0.0
	if _dwell >= look_time:
		candle.lit = true
		GameState.set_flag(id)
		lit.emit()
