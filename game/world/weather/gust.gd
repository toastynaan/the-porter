class_name Gust
extends Node3D
## A scripted gust (docs/systems/mechanics.md, "The lantern": wind puts the lantern
## out only at set moments, never at random and never in a chase): a gust
## down the tower stair on night 2, the door that blows open in the fog on
## night 4, and a few like them. When the porter walks into its box on one
## of its `nights`, the wind comes once: the flame gutters for 1.5 s, and
## unless he covers it in time it goes out. A `door` named here blows open.

signal blew

const GUST := preload("res://art/sfx/sfx_gust.wav")

@export var nights: Array[int] = []
@export var size := Vector3(3, 3, 3)
## A door that blows open with it.
@export var door: Door

var blown := false


func _ready() -> void:
	add_to_group(&"gusts")


func _physics_process(_delta: float) -> void:
	if blown or not nights.has(GameState.night):
		return
	var p := get_tree().get_first_node_in_group(&"player") as Player
	if p == null or not _inside(p.global_position):
		return
	for h: Hunter in get_tree().get_nodes_in_group(&"hunters"):
		if not h.dormant and h.state == Hunter.State.CHASE:
			return
	blow(p)


func blow(p: Player) -> void:
	blown = true
	if door and not door.locked:
		door.set_open(true)
	p.lantern.gust()
	if AudioOut.enabled():
		var a := AudioStreamPlayer.new()
		a.stream = GUST
		add_child(a)
		a.play()
	blew.emit()


func _inside(point: Vector3) -> bool:
	var local := global_transform.affine_inverse() * point
	return absf(local.x) <= size.x * 0.5 and absf(local.y) <= size.y * 0.5 and absf(local.z) <= size.z * 0.5
