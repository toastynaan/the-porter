class_name HiddenBody
extends FoundBody
## One of the five hidden bodies (docs/log/full-game-run.md, "Hidden bodies"):
## an earlier victim with a pilgrim's badge that matches a name torn from
## the ledger, there from `from_night` on for a porter who explores. It
## stays hidden until he does the thing that finds it at its "Reveal"
## marker: draws water at the well, wades the race past the wheel (walking
## into it), digs at the turned earth with his hands, climbs past the bell,
## lifts a loose flag (holding `interact` for `reveal_time`, or walking within
## `walk_radius`). Finding one is a risk: the nearest hunter on his rounds
## hears and comes to look (Hunter.alert).

const REVEAL := preload("res://game/death/reveal_area.gd")

@export var from_night := 1
## Found by walking into it (the race) rather than using it.
@export var by_walking := false
@export var walk_radius := 1.5
## What the porter sees as he begins (the bucket comes up heavy...).
@export var reveal_line := ""
@export var reveal_time := 1.5
## Found with its own reveal (off: something else finds it, the Well).
@export var own_reveal := true

var _reveal: Area3D
var _holding := 0.0


func _ready() -> void:
	shown = false
	super._ready()
	if is_found and not is_moved:
		show_body.call_deferred()
	if not by_walking and not is_found and own_reveal:
		_reveal = REVEAL.new()
		_reveal.collision_layer = Layers.INTERACT if available() else 0
		_reveal.collision_mask = 0
		_reveal.monitoring = false
		var shape := CollisionShape3D.new()
		var box := BoxShape3D.new()
		box.size = Vector3(1.0, 1.2, 1.0)
		shape.shape = box
		shape.position = Vector3(0, 0.6, 0)
		_reveal.add_child(shape)
		_reveal.set(&"hidden_body", self)
		add_child(_reveal)
		var marker := get_node_or_null(^"Reveal") as Node3D
		if marker:
			_reveal.global_transform = marker.global_transform


## Here tonight (it was hidden before or on this night).
func available() -> bool:
	return GameState.night >= from_night


func _physics_process(delta: float) -> void:
	if not is_found and by_walking and available():
		var p := get_tree().get_first_node_in_group(&"player") as Player
		if p and p.global_position.distance_to(_reveal_point()) < walk_radius:
			uncover()
		return
	super._physics_process(delta)


## He holds `interact` on the reveal for `reveal_time` (called each frame by
## the reveal while held); returns true once it's done.
func work(delta: float) -> bool:
	if is_found:
		return true
	if _holding == 0.0 and not reveal_line.is_empty():
		Talk.say("", reveal_line)
	_holding += delta
	if _holding >= reveal_time:
		uncover()
		return true
	return false


## Shows the body and finds it, and the nearest hunter hears.
func uncover() -> void:
	if is_found:
		return
	show_body()
	find()
	if _reveal:
		_reveal.collision_layer = 0
	var nearest: Hunter = null
	for h: Hunter in get_tree().get_nodes_in_group(&"hunters"):
		if not h.dormant and (nearest == null or h.global_position.distance_to(global_position) < nearest.global_position.distance_to(global_position)):
			nearest = h
	if nearest:
		nearest.alert(global_position)


func _reveal_point() -> Vector3:
	var marker := get_node_or_null(^"Reveal") as Node3D
	return marker.global_position if marker else global_position
