class_name Companion
extends Node
## Someone who goes with the porter (docs/systems/mechanics.md, "Companions"): a guest
## to his bed, Mab or Joan on night 6, Simon on nights 5-6 if he saved him.
## A child of their VisitorNPC. Asked to follow ([follow] in a talk), they
## keep a few steps behind and open doors; told to wait ([wait], or a quick
## E), they stay. When he hides, they hide too: in the nearest free hiding
## spot within HIDE_RADIUS, or crouched in the shadow where they stand. A
## hunter who gets his hands on one (CATCH_REACH, not hidden) takes them:
## they're gone, and may be one of the night's deaths. Someone who
## distrusts him (trust below 0) won't follow.

signal caught

const HIDE_RADIUS := 6.0
const CATCH_REACH := 1.2
const WILLING := 0

## Their People id.
@export var who := &""

var recruited := false
var following := false
var hidden_in: HidingSpot
var crouched := false
var is_caught := false

@onready var npc: VisitorNPC = get_parent() as VisitorNPC


func _ready() -> void:
	add_to_group(&"companions")
	_hook.call_deferred()


func _hook() -> void:
	if not is_inside_tree():
		return
	var p := get_tree().get_first_node_in_group(&"player") as Player
	if p:
		p.hid.connect(_on_hid)
		p.unhid.connect(_on_unhid)


## Follow him, or wait here. Returns whether they will.
func set_following(on: bool) -> bool:
	if is_caught:
		return false
	if on and GameState.trust_of(who) < WILLING:
		Talk.say(People.display_name(who), "No. I'll go my own way.")
		return false
	recruited = true
	following = on
	var p := get_tree().get_first_node_in_group(&"player") as Player
	if on and p:
		npc.follow(p)
		Talk.say(People.display_name(who), "I'm with you.")
	else:
		npc.stop()
		Talk.say(People.display_name(who), "I'll wait.")
	return true


func _on_hid(spot: HidingSpot) -> void:
	if not following or is_caught:
		return
	var best: HidingSpot = null
	for s: HidingSpot in get_tree().get_nodes_in_group(&"hiding_spots"):
		var d := s.global_position.distance_to(npc.global_position)
		if s != spot and s.occupant == null and d < HIDE_RADIUS and (best == null or d < best.global_position.distance_to(npc.global_position)):
			best = s
	npc.stop()
	if best:
		hidden_in = best
		npc.set_present(false)
		npc.global_position = best.exit.global_position
	else:
		crouched = true
		npc.look.scale = Vector3(1.0, 0.55, 1.0)


func _on_unhid(_spot: HidingSpot) -> void:
	if is_caught:
		return
	if hidden_in:
		npc.set_present(true, Transform3D(Basis.IDENTITY, hidden_in.exit.global_position))
		hidden_in = null
	crouched = false
	npc.look.scale = Vector3.ONE
	if following:
		npc.follow(get_tree().get_first_node_in_group(&"player") as Player)


func _physics_process(_delta: float) -> void:
	if is_caught or hidden_in or not npc.visible:
		return
	for h: Hunter in get_tree().get_nodes_in_group(&"hunters"):
		if h.dormant or h.state == Hunter.State.PATROL:
			continue
		if h.global_position.distance_to(npc.global_position) < CATCH_REACH:
			take()
			return


## A hunter has them: gone, and dead.
func take() -> void:
	is_caught = true
	following = false
	npc.set_present(false)
	GameState.set_flag(StringName("caught_" + String(who)))
	GameState.set_flag(StringName("died_" + String(who)))
	caught.emit()
