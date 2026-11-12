class_name DemonChoice
extends Node3D
## The Demon ending is a choice (docs/systems/mechanics.md, "Night 6"). At Dose 75+,
## from `hour`, "the demon" comes for the porter with a light: the prior,
## coming to help, though drugged he can't see it. When it corners him
## (within REACH) he can strike, the only time he can: the Demon ending; or
## run, and the night goes on. Sober, nobody comes.

signal struck

const DOSE := 75.0
const REACH := 3.0
## How he sees it: the demon (the costume renders by Dose: drugged, the demon).
const LOOK := preload("res://game/demon/demon_costume.tscn")

@export var hour := 22.5
@export var visitor: Visitor
@export var visitor_scene: PackedScene
@export var from: Marker3D
@export var demon_lines := PackedStringArray()
@export var struck_lines := PackedStringArray()
@export var ran_lines := PackedStringArray()

var done := false
var _npc: VisitorNPC


func _physics_process(_delta: float) -> void:
	if done or GameState.night != 6 or GameState.hour < hour or GameState.dose < DOSE:
		return
	var p := get_tree().get_first_node_in_group(&"player") as Player
	if p == null or p.busy():
		return
	if _npc == null:
		_npc = visitor_scene.instantiate() as VisitorNPC
		_npc.visitor = visitor
		get_parent().add_child(_npc)
		_npc.global_transform = from.global_transform
		_npc.speed = 2.6
		# Drugged, he can't see that it's the prior.
		_npc.look.visible = false
		_npc.add_child(LOOK.instantiate())
	_npc.go_to(p.global_position)
	if _npc.global_position.distance_to(p.global_position) < REACH:
		done = true
		_corner.call(p)


func _corner(p: Player) -> void:
	_npc.stop()
	_npc.face(p.global_position)
	for line in demon_lines:
		await Talk.say("", line)
	var pick := await Talk.choose(PackedStringArray(["(Strike it.)", "(Run.)"]))
	if pick == 0:
		GameState.set_flag(&"struck_the_demon")
		for line in struck_lines:
			var at := line.find(": ")
			await Talk.say(line.left(at) if at > 0 and not line.begins_with("(") else "", line.substr(at + 2) if at > 0 and not line.begins_with("(") else line)
		struck.emit()
	else:
		GameState.set_flag(&"ran_from_the_demon")
		for line in ran_lines:
			await Talk.say("", line)
		_npc.queue_free()
