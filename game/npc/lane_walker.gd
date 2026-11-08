class_name LaneWalker
extends Node
## Walks its parent (a VisitorNPC) to and fro between `points` while there
## is light, and stops to talk (a Talker sibling). At `leave_hour` he goes
## off to `leave` and is gone: passers-by in the lane at dusk (design doc,
## "Core loop" 0: step out into the lane and talk to whoever is there).

@export var points: Array[Marker3D] = []
@export var leave: Marker3D
@export var leave_hour := 17.5

var _i := 0
var _leaving := false
var _paused := false

@onready var _npc := get_parent() as VisitorNPC
@onready var _talker := _npc.get_node_or_null(^"Talker") as Talker


func _ready() -> void:
	_npc.arrived.connect(_on_arrived)
	_walk.call_deferred()


func _process(_delta: float) -> void:
	if not _leaving and GameState.hour >= leave_hour:
		_leaving = true
		_walk()
	var talking := _talker != null and _talker.talking
	if talking != _paused:
		_paused = talking
		if talking:
			_npc.stop()
		else:
			_walk()


func _walk() -> void:
	if _paused:
		return
	if _leaving:
		_npc.go_to(leave.global_position)
	elif not points.is_empty():
		_npc.go_to(points[_i].global_position)


func _on_arrived() -> void:
	if _leaving:
		_npc.queue_free()
		return
	_i = (_i + 1) % points.size()
	_walk()
