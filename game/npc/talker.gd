class_name Talker
extends Area3D
## Someone you can talk to: look at them and press `interact` (design doc,
## "Core loop" 0: at dusk you can talk to the brothers, or to whoever is in
## the lane). Until the script is written the lines are placeholders. He
## turns to face you if he can. Only in `phases` (e.g. dusk, while there is
## time to talk). `heard_flag` records that you talked.

@export var speaker := ""
@export var lines := PackedStringArray()
@export var phases: Array[GameState.Phase] = [GameState.Phase.DUSK]
@export var heard_flag := &""

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


func interact(by: Node) -> void:
	if talking or lines.is_empty():
		return
	talking = true
	var parent := get_parent()
	if parent.has_method(&"face") and by is Node3D:
		parent.call(&"face", (by as Node3D).global_position)
	for line in lines:
		await Talk.say(speaker, line)
	if not heard_flag.is_empty():
		GameState.set_flag(heard_flag)
	talking = false


func _on_phase(phase: GameState.Phase) -> void:
	collision_layer = Layers.INTERACT if phases.has(phase) else 0
