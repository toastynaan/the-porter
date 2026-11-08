class_name FoundBody
extends Node3D
## A body to find (docs/full-game-run.md, "Found bodies", "Moving bodies";
## docs/mechanics.md, "Investigation": look at a body for a moment to find
## it, and a note is written). The node is where it lies. It's a ragdoll
## body lying dead (Corpse), or `figure`, a posed figure (hanging, sitting).
##
## Found: found_<id> is set, the porter says `line`, and `clue` goes in his
## notes. A body that `moves` (it would prove a man did it) is taken away
## by the cult once he leaves it to fetch someone: when he is `leave_range`
## off and can't see it, it's gone, with the marks that prove men did it,
## and coming back he finds the place empty (`moved_clue`). Near a body is
## somewhere he shouldn't be seen (group "restricted", place near_<id>).

signal found
signal moved

const BODY := preload("res://game/characters/chr_body.tscn")
## Finding it: looking within this many degrees of it, from this near, this long.
const FIND_ANGLE := 14.0

@export var id := &""
@export var appearance := {"skin": Color(0.78, 0.66, 0.55), "shirt": Color("#1E1B19"),
	"pants": Color("#1E1B19"), "height": 1.0, "width": 1.0}
## A posed figure instead of a ragdoll (a character scene: hanging, sitting).
@export var figure: PackedScene
## What the porter says when he finds it.
@export var line := ""
@export var clue := &""
@export var moves := false
@export var moved_clue := &""
## Its death feeds the rite (one that happened out of sight).
@export var feeds := false
## In the world from the start; a beat can show it later (show_body).
@export var shown := true
## Off for a body found but not seen (down the well, under the floor).
@export var body_visible := true
@export var look_time := 0.6
@export var find_range := 5.0
@export var leave_range := 20.0
## Being seen within this many metres of it counts (docs/mechanics.md).
@export var near_radius := 4.0

var is_found := false
var is_moved := false
var body: Node3D

var _dwell := 0.0
var _away := 0.0
var _told_gone := false

## For SeenWatch: the place he shouldn't be seen, and its words for the remark.
var place: StringName:
	get:
		return StringName("near_" + String(id))
var where: String:
	get:
		return "by a body"


func _ready() -> void:
	add_to_group(&"found_bodies")
	add_to_group(&"restricted")
	is_found = GameState.has_flag(found_flag())
	is_moved = GameState.has_flag(StringName("moved_" + String(id)))
	_told_gone = is_moved and moved_clue != &"" and GameState.has_note(moved_clue)
	if feeds and shown:
		GameState.feed_rite(id)
	if shown and not is_moved:
		_spawn.call_deferred()


func found_flag() -> StringName:
	return StringName("found_" + String(id))


## Puts the body here now (a beat that brings it into the world later).
func show_body() -> void:
	if not is_inside_tree():
		return
	shown = true
	if feeds:
		GameState.feed_rite(id)
	if body == null and not is_moved:
		_spawn()


func contains(point: Vector3) -> bool:
	return body != null and point.distance_to(_centre()) < near_radius


func active() -> bool:
	return body != null


func _spawn() -> void:
	if not is_inside_tree():
		return
	if not body_visible:
		body = Node3D.new()
		add_child(body)
		return
	if figure:
		var look := CharacterLook.new()
		look.look = figure
		add_child(look)
		body = look
	else:
		var c := BODY.instantiate() as Corpse
		c.appearance = appearance
		add_child(c)
		c.lie_dead.call_deferred()
		body = c


func _centre() -> Vector3:
	if body is Corpse:
		return (body as Corpse).centre()
	return global_position + Vector3.UP * 0.6


func _physics_process(delta: float) -> void:
	var p := get_tree().get_first_node_in_group(&"player") as Player
	if p == null:
		return
	var camera := p.camera
	if body and not is_found:
		var at := _centre()
		var looking := camera.global_position.distance_to(at) < find_range \
			and ViewCheck.off_centre(camera, at) < FIND_ANGLE and ViewCheck.on_screen(camera, [at])
		_dwell = _dwell + delta if looking else 0.0
		if _dwell >= look_time:
			find()
	elif body and moves and is_found and not is_moved:
		var far := p.global_position.distance_to(global_position) > leave_range \
			and not ViewCheck.on_screen(camera, [_centre()])
		_away = _away + delta if far else 0.0
		if _away > 1.0:
			move_away()
	elif is_moved and not _told_gone and p.global_position.distance_to(global_position) < find_range:
		_told_gone = true
		Talk.say("", "(It's gone. There's nothing here now.)")
		if moved_clue != &"":
			GameState.note(moved_clue)


## He finds it: the flag, his line, the note.
func find() -> void:
	if is_found:
		return
	is_found = true
	GameState.set_flag(found_flag())
	if clue != &"":
		GameState.note(clue)
	if not line.is_empty():
		Talk.say("", line)
	found.emit()


## The cult takes it away, and the marks that would prove men did it.
func move_away() -> void:
	is_moved = true
	GameState.set_flag(StringName("moved_" + String(id)))
	BloodMarks.remove_for(get_tree(), id, true)
	if body:
		body.queue_free()
		body = null
	moved.emit()
