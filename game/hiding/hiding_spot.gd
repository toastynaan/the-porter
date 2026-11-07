@tool
class_name HidingSpot
extends Area3D
## A place to hide (design doc, "Hiding"): look at it and `interact` to climb
## in; `interact` again to climb out. Each spot has a `noise` (getting in and
## out carries noise × Earshot.SPOT m) and a `check_chance`: the chance a hunter
## who checks it finds you while you hold your breath. Breathing, he always
## finds you. Hunters check the 2 spots nearest where they last saw you, and
## a spot used twice in a night first.
##
## Children: a Marker3D "View" (the camera while hidden: position and facing,
## -Z forward), "Exit" (feet when you climb out) and optionally "Check"
## (where a hunter stands to check it; Exit if missing). The box (`size`,
## standing on the origin) is what the view ray finds; make it a little
## bigger than the prop so the ray reaches it first.

signal entered_spot(player: Player)
signal left_spot(player: Player)
signal checked(found: bool)

const HIDE_SOUND := preload("res://art/sfx/sfx_hide.wav")

## How loud getting in and out is, 0..1.
@export_range(0.0, 1.0) var noise := 0.3
## Chance a hunter checking it finds you holding your breath, 0..1.
@export_range(0.0, 1.0) var check_chance := 0.5
## How far you can look around from the view, degrees.
@export var look_yaw := 50.0
@export var look_pitch := 25.0
## Eye height above the hidden body's feet; the view marker sets the eye.
@export var eye_height := 0.4
@export var size := Vector3(1, 1, 1):
	set(value):
		size = value
		_build()

## Times used tonight.
var uses := 0
var occupant: Player

var _shape: CollisionShape3D
var _audio: AudioStreamPlayer3D

@onready var view: Marker3D = $View
@onready var exit: Marker3D = $Exit


func _ready() -> void:
	_build()
	if Engine.is_editor_hint():
		return
	add_to_group(&"hiding_spots")
	collision_layer = Layers.INTERACT
	collision_mask = 0
	monitoring = false
	_audio = AudioStreamPlayer3D.new()
	_audio.stream = HIDE_SOUND
	add_child(_audio)


func _build() -> void:
	if not is_inside_tree():
		return
	if _shape == null:
		_shape = CollisionShape3D.new()
		add_child(_shape)
	var box := BoxShape3D.new()
	box.size = size
	_shape.shape = box
	_shape.position = Vector3(0.0, size.y * 0.5, 0.0)


## Where a hunter stands to check it.
func check_point() -> Vector3:
	var marker := get_node_or_null(^"Check") as Node3D
	return (marker if marker else exit).global_position


func interact(by: Node) -> void:
	if occupant == null and by is Player:
		(by as Player).hide_in(self)


func enter(player: Player) -> void:
	occupant = player
	uses += 1
	_make_noise()
	entered_spot.emit(player)


func exit_spot(player: Player) -> void:
	occupant = null
	_make_noise()
	left_spot.emit(player)


## A hunter looks in. Returns true if he finds whoever is hiding here.
func check() -> bool:
	var found := false
	if occupant:
		found = not occupant.breath.holding or randf() < check_chance
	checked.emit(found)
	return found


func _make_noise() -> void:
	Earshot.make(self, view.global_position, noise * Earshot.SPOT, self)
	if AudioOut.enabled() and noise > 0.0:
		_audio.global_position = view.global_position
		_audio.volume_db = linear_to_db(lerpf(0.3, 1.0, noise))
		_audio.play()


func _get_configuration_warnings() -> PackedStringArray:
	var out := PackedStringArray()
	for marker in ["View", "Exit"]:
		if not has_node(NodePath(marker)):
			out.append("Needs a Marker3D child named %s." % marker)
	return out
