extends NightBeat
## The Matins bell (design doc, "Core loop": at midnight ring the bell, go
## to the choir). The night saves here: a death sends you back to this bell.

const BELL := preload("res://art/sfx/sfx_bell.wav")
const STROKES := 3
const STROKE_GAP := 2.2

@export var rope: Duty
## Where the bell hangs, for the sound.
@export var bell_at: Node3D

var _audio: AudioStreamPlayer3D


func _ready() -> void:
	_audio = AudioStreamPlayer3D.new()
	_audio.stream = BELL
	_audio.unit_size = 20.0
	_audio.max_distance = 200.0
	add_child(_audio)


func run() -> void:
	await rope.wait_for_use()
	GameState.hour = 24.0
	GameState.ring_bell(&"matins")
	_ring.call()
	await say("", "(Matins. The brothers gather in the choir.)")


func _ring() -> void:
	if not AudioOut.enabled():
		return
	_audio.global_position = bell_at.global_position
	for i in STROKES:
		_audio.play()
		await get_tree().create_timer(STROKE_GAP).timeout
