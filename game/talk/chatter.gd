class_name Chatter
extends Node3D
## People talking among themselves (your ask, 2026-11-12): at the Keys,
## Jankin telling Walter what he saw on the wall. When the porter comes within
## `radius` while they're about, they turn to each other and say the lines
## of `talk`'s `start` point, each in their own voice and face, once a night
## (the flag overheard_<id>). He hears it as he would: walk off and it stops.
## Pressing E on one of them talks to them as usual, and their own talk can
## pick up what he overheard ([if overheard_<id>]).
##
## The conversation is a .talk file like any other; only its `start` point is
## said, and the speakers are named in its lines ("Jankin {drunk}: ...").

@export var talk: Conversation
## Who is talking: they face each other while they do.
@export var people: Array[Node3D] = []
## How near he must come to hear them, m, and how far off it stops.
@export var radius := 4.5
@export var lose_at := 7.0
## If above 0, they talk only while every one of them is this near the
## Chatter, m: for people who walk (Margery passing Kit in the lane). Anyone
## walking (a LaneWalker) stands still while they talk.
@export var together := 0.0
## When they're at it (as Talker.phases).
@export var phases: Array[GameState.Phase] = [GameState.Phase.DUSK]

var _since := 0.0
var _playing := false


func _physics_process(delta: float) -> void:
	_since += delta
	if _since < 0.3 or _playing or talk == null or not phases.has(GameState.phase):
		return
	_since = 0.0
	if GameState.has_flag(_flag()) or not Talk.quiet():
		return
	var p := get_tree().get_first_node_in_group(&"player") as Player
	if p == null or p.busy() or p.global_position.distance_to(global_position) > radius:
		return
	if people.any(func(who: Node3D) -> bool: return who == null or not who.is_visible_in_tree()):
		return
	if together > 0.0 and people.any(func(who: Node3D) -> bool:
			return who.global_position.distance_to(global_position) > together):
		return
	_play.call(p)


## The flag set once he has heard them.
func _flag() -> StringName:
	return StringName("overheard_" + String(talk.id))


func _play(p: Player) -> void:
	_playing = true
	GameState.set_flag(_flag())
	_hold(true)
	# They turn to each other.
	for i in people.size():
		var other := people[(i + 1) % people.size()]
		if people[i].has_method(&"face") and other != people[i]:
			people[i].call(&"face", other.global_position)
	var point := talk.point(talk.start(false))
	if point:
		for l in point.lines:
			if Talk.talking or p.global_position.distance_to(global_position) > lose_at:
				break
			await Talk.say(l.speaker, l.text)
	_hold(false)
	_playing = false


func _hold(on: bool) -> void:
	for who in people:
		if is_instance_valid(who):
			for c in who.get_children():
				if c is LaneWalker:
					(c as LaneWalker).held = on
