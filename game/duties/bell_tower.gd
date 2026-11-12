class_name BellTower
extends Node
## The abbey bell, heard from anywhere in the abbey (design doc, "Core loop":
## the bells for supper, Matins and Lauds ring at the candle clock's marks).

const BELL := preload("res://art/sfx/sfx_bell.wav")
const STROKE_GAP := 2.2

## Where the bell hangs, for the sound.
@export var bell: Node3D

var _audio: AudioStreamPlayer3D


func _ready() -> void:
	_audio = AudioStreamPlayer3D.new()
	_audio.stream = BELL
	_audio.unit_size = 20.0
	_audio.max_distance = 200.0
	add_child(_audio)


## Rings `strokes` times, a stroke every couple of seconds.
func ring(strokes: int) -> void:
	if not AudioOut.enabled():
		return
	_audio.global_position = bell.global_position
	for i in strokes:
		_audio.play()
		await get_tree().create_timer(STROKE_GAP, false).timeout
