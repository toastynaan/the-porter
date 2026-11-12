class_name SaintKills
extends Node3D
## The Saint's witnessed deaths on night 6 (docs/full-game-run.md, "Witnessed
## deaths"): Dunstan in the cloister (it finds him first, then turns to the
## porter), Cole at the gate (holding it shut against him), and Osric or
## Ranulf in the choir (the candles go out one by one). Only once it walks
## (the count at 9 or more): each of `deaths` (DeathScenes, the Saint their
## killer) plays the first time the porter comes within `radius` of it after
## the Saint wakes, with its `lines`. They feed nothing.

@export var saint: HungrySaint
@export var deaths: Array[DeathScene] = []
@export var radius := 14.0
## Lines for each death, in the same order ("Name: words" or "(...)").
@export var lines: Array[PackedStringArray] = []

var played: Array[int] = []


func _physics_process(_delta: float) -> void:
	if saint == null or not saint.awake or not saint.walks:
		return
	var p := get_tree().get_first_node_in_group(&"player") as Player
	if p == null:
		return
	for i in deaths.size():
		if played.has(i) or deaths[i] == null:
			continue
		if p.global_position.distance_to(deaths[i].global_position) < radius:
			played.append(i)
			_play.call(i)


func _play(i: int) -> void:
	await deaths[i].play()
	if i < lines.size():
		for line in lines[i]:
			await Talk.say("", line)
