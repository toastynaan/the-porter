class_name GateBench
extends Area3D
## The porter's bench by the gate (design doc, "Core loop" 6: you go back to
## the gate and wait; you can doze until dawn, but the night's main event
## interrupts). Sit here and doze: the candle clock runs fast and the
## screen goes dark until something needs him (NightClock.wake: a knock, the
## Matins mark, Lauds). He can doze only while the night is waiting on the
## gate (a beat with `can_doze`) and no duty is wanted.

signal dozed
signal woke

## How dark the screen goes while he dozes.
const DOZE_FADE := 0.85

@export var size := Vector3(0.6, 0.9, 1.8)

var sitting := false


func _ready() -> void:
	collision_layer = Layers.INTERACT
	collision_mask = 0
	monitoring = false
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = size
	shape.shape = box
	shape.position = Vector3(0.0, size.y * 0.5, 0.0)
	add_child(shape)


func interact(by: Node) -> void:
	var p := by as Player
	var clock := get_tree().get_first_node_in_group(&"night_clock") as NightClock
	if p == null or clock == null or sitting:
		return
	if not GameState.has_flag(&"gate_taken"):
		await Talk.say("", "(The gate is Cole's until after supper.)")
		return
	if not can_doze():
		await Talk.say("", "(Not now.)")
		return
	sitting = true
	p.controls_locked = true
	p.place(global_position + global_basis.x * 0.6, global_rotation.y)
	await Talk.say("", "(You sit by the gate, and doze.)")
	# The night may have moved on while he sat down.
	if can_doze():
		clock.doze()
		dozed.emit()
		await _fade(DOZE_FADE, 0.8)
		if clock.dozing:
			await clock.woke
		await _fade(0.0, 0.6)
	p.controls_locked = false
	sitting = false
	woke.emit()


func can_doze() -> bool:
	var director := get_tree().get_first_node_in_group(&"night_director") as NightDirector
	if director == null or director.current == null or not director.current.can_doze:
		return false
	return not get_tree().get_nodes_in_group(&"duties").any(func(d: Node) -> bool: return (d as Duty).enabled)


func _fade(alpha: float, seconds: float) -> void:
	var flow := get_tree().get_first_node_in_group(&"capture_flow") as CaptureFlow
	if flow:
		await flow.fade.fade_to(alpha, seconds)
