class_name SquintScare
extends Node3D
## The squint scare (docs/mechanics.md, "The squint scare"): night 0 only,
## once. If he walks the lane alone after the curfew bell and passes the
## south squint, a shape stands perfectly still just inside it: too tall, too
## thin, no horns. It's gone once he has seen it (a clear line through the
## slit) and looked away; if he walks on without seeing it, it can come again.
## One of the three things
## nothing explains before night 6 (it's the Saint). The animals go quiet
## while it's there.

const SAINT := preload("res://game/characters/chr_saint.tscn")
## How near the squint, outside, he must pass; how near nobody else may be.
const NEAR := 3.0
const ALONE := 12.0

@export var squint: Squint
## Where it stands, just inside the wall.
@export var stand: Marker3D
@export var night := 0

var figure: Node3D
var seen := false
var done := false


func _process(_delta: float) -> void:
	if done or GameState.night != night or GameState.hour < Curfew.HOUR or GameState.has_flag(&"n0_squint_scare"):
		return
	var p := get_tree().get_first_node_in_group(&"player") as Player
	if p == null:
		return
	var slit := squint.global_position
	var near := squint.outside(p.global_position) and p.global_position.distance_to(slit) < NEAR + 1.6
	if figure == null:
		if near and _alone(p) and not ViewCheck.on_screen(p.camera, [stand.global_position + Vector3.UP * 1.8]):
			figure = SAINT.instantiate() as Node3D
			add_child(figure)
			figure.global_transform = stand.global_transform
			get_tree().call_group(&"room_tone", &"set_quiet", true)
		return
	var head := figure.global_position + Vector3.UP * 1.9
	var looking := p.camera.global_position.distance_to(slit) < NEAR + 0.5 and ViewCheck.off_centre(p.camera, slit) < 15.0 \
			and ViewCheck.clear(p, p.camera.global_position, head)
	if looking:
		seen = true
	elif not seen and p.global_position.distance_to(slit) > 8.0:
		# He walked on without seeing it: it can come again.
		_remove()
	elif seen and (ViewCheck.off_centre(p.camera, slit) > 35.0 or p.camera.global_position.distance_to(slit) > 4.0):
		_remove()
		done = true
		GameState.set_flag(&"n0_squint_scare")


func _remove() -> void:
	figure.queue_free()
	figure = null
	get_tree().call_group(&"room_tone", &"set_quiet", false)


func _alone(p: Player) -> bool:
	for n: Node in get_tree().get_nodes_in_group(&"lane_people"):
		var npc := n as Node3D
		if npc.visible and npc.global_position.distance_to(p.global_position) < ALONE:
			return false
	return true
