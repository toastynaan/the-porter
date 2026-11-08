class_name Murmur
extends Node3D
## Brothers talking low (docs/mechanics.md, "Reading the hidden numbers": at
## Suspicion 30+ talk stops when he walks into a room). A murmur plays here
## while two or more brothers stand within RADIUS of it. From Suspicion 30,
## it stops when the porter comes within HUSH, and they turn to look at him.

const LOOP := preload("res://art/sfx/amb_murmur_loop.wav")
const RADIUS := 3.0
const HUSH := 8.0
const SUSPICION := 30

var talking := false

var _audio: AudioStreamPlayer3D


func _ready() -> void:
	add_to_group(&"murmurs")
	_audio = AudioStreamPlayer3D.new()
	_audio.stream = AudioOut.looped(LOOP)
	_audio.unit_size = 3.0
	_audio.volume_db = -8.0
	add_child(_audio)


func _process(_delta: float) -> void:
	var near: Array[Brother] = []
	for b: Brother in get_tree().get_nodes_in_group(&"brothers"):
		if b.visible and b.global_position.distance_to(global_position) < RADIUS:
			near.append(b)
	var p := get_tree().get_first_node_in_group(&"player") as Player
	var hushed := p != null and GameState.suspicion >= SUSPICION and p.global_position.distance_to(global_position) < HUSH
	var now := near.size() >= 2 and not hushed
	if hushed and near.size() >= 2 and talking:
		for b in near:
			b.face(p.global_position)
	if now != talking:
		talking = now
		if AudioOut.enabled():
			if now:
				_audio.play()
			else:
				_audio.stop()
