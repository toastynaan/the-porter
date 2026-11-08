class_name Talker
extends Area3D
## Someone you can talk to: look at them and press `interact` (design doc,
## "Core loop" 0: at dusk you can talk to the brothers, or to whoever is in
## the lane). The talk is a Conversation, written in its own file under
## game/dialogue/; Talk.converse() plays it, with the porter's view eased in
## on their face. They turn to face him. Only in `phases` (e.g. dusk, while
## there is time to talk).

@export var conversation: Conversation
@export var phases: Array[GameState.Phase] = [GameState.Phase.DUSK]

var talking := false


func _ready() -> void:
	collision_mask = 0
	monitoring = false
	var shape := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.4
	capsule.height = 1.8
	shape.shape = capsule
	shape.position = Vector3(0.0, 0.9, 0.0)
	add_child(shape)
	GameState.phase_changed.connect(_on_phase)
	_on_phase(GameState.phase)


func interact(_by: Node) -> void:
	if talking or conversation == null:
		return
	talking = true
	await Talk.converse(conversation, get_parent() as Node3D)
	talking = false


func _on_phase(phase: GameState.Phase) -> void:
	collision_layer = Layers.INTERACT if phases.has(phase) else 0
