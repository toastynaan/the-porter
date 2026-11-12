class_name Talker
extends Area3D
## Someone you can talk to: look at them and press `interact` (design doc,
## "Core loop" 0: at dusk you can talk to the brothers, or to whoever is in
## the lane). The talk is a Conversation, written in its own file under
## game/chapters/<chapter>/dialogue/; Talk.converse() plays it, with the porter's view eased in
## on their face. They turn to face him. Only in `phases` (e.g. dusk, while
## there is time to talk). At Suspicion 85+ the brothers won't speak to him at
## all (docs/systems/mechanics.md, "Reading the hidden numbers"). Someone who is his
## companion (a Companion child) is told to follow or wait with a quick E
## instead.
##
## Hails (your ask, 2026-11-12: people start talks too): if the conversation
## has a `hail` point, the first time the porter comes within `hail_radius`
## while they can talk, they turn to him and say its lines ("Brother! You're
## the new porter?"), once a night (the flag hailed_<id>). Pressing E then
## talks to them as usual; the talk can ask [if hailed_<id>].

@export var conversation: Conversation
@export var phases: Array[GameState.Phase] = [GameState.Phase.DUSK]
## How near he must come for them to call out to him, m.
@export var hail_radius := 5.0

var talking := false
var _since := 0.0


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


## Suspicion from which the brothers won't speak to him.
const SILENT_SUSPICION := 85


func interact(_by: Node) -> void:
	if talking or conversation == null:
		return
	var companion := get_parent().get_node_or_null(^"Companion") as Companion
	if companion and companion.recruited:
		companion.set_following(not companion.following)
		return
	if get_parent() is Brother and GameState.suspicion >= SILENT_SUSPICION:
		Talk.say("", "(He looks through you, and turns away.)")
		return
	talking = true
	await Talk.converse(conversation, get_parent() as Node3D)
	talking = false


func _physics_process(delta: float) -> void:
	_since += delta
	if _since < 0.3:
		return
	_since = 0.0
	if collision_layer == 0 or conversation == null or talking or not conversation.has_point("hail"):
		return
	var flag := StringName("hailed_" + String(conversation.id))
	if GameState.has_flag(flag) or not Talk.quiet():
		return
	var p := get_tree().get_first_node_in_group(&"player") as Player
	var who := get_parent() as Node3D
	if p == null or who == null or not who.is_visible_in_tree() or p.busy():
		return
	var head := who.global_position + Vector3.UP * 1.6
	if p.global_position.distance_to(who.global_position) > hail_radius \
			or not ViewCheck.clear(who, head, p.camera.global_position):
		return
	GameState.set_flag(flag)
	if who.has_method(&"face"):
		who.call(&"face", p.global_position)
	_hail.call()


## Calls out to him: the hail point's lines, unless a talk begins meanwhile.
func _hail() -> void:
	for l in conversation.point("hail").lines:
		if Talk.talking:
			return
		await Talk.say(l.speaker, l.text)


func _on_phase(phase: GameState.Phase) -> void:
	collision_layer = Layers.INTERACT if phases.has(phase) else 0
