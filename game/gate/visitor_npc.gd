class_name VisitorNPC
extends CharacterBody3D
## A visitor in the flesh: walks up the lane with a lantern, stands at the
## grille, follows the porter to the guesthouse, lies down in a bed, or goes
## back down the lane. Walks the navmesh at a visitor's pace; his body is a
## little slimmer than the navmesh's 0.3 m agent so paths never graze corners.
## He opens the unlocked doors in his way (a locked one stops him). While the
## porter is talking to him (Talk.talking_to) he stands still. The markers
## under Parts are what the porter looks at to read him (VisitorDetail.part);
## the box and the bag show only if his details mention them.

signal arrived

const WALK_SPEED := 1.2
const GRAVITY := 9.8
## Keeps this far behind whoever he follows.
const FOLLOW_GAP := 1.8

@export var visitor: Visitor:
	set(value):
		visitor = value
		if is_node_ready():
			_dress()
@export var speed := WALK_SPEED

## In a bed.
var lying := false

var _target := Vector3.INF
var _following: Node3D
var _door_wait := 0.0

@onready var look: CharacterLook = $Look
@onready var agent: NavigationAgent3D = $Agent
@onready var parts: Node3D = $Parts


func _ready() -> void:
	add_to_group(&"visitors")
	collision_layer = Layers.CAPSULE
	collision_mask = Layers.MASK_HUNTER
	_dress()


func _dress() -> void:
	if visitor == null:
		return
	look.look = visitor.look
	($Parts/box as Node3D).visible = visitor.has_part(&"box")
	($Parts/bag as Node3D).visible = visitor.has_part(&"bag")
	($Lantern as Node3D).visible = visitor.lantern


## Walks to `point`; await it.
func walk_to(point: Vector3) -> void:
	go_to(point)
	await arrived


## Sets off for `point`; `arrived` is emitted there.
func go_to(point: Vector3) -> void:
	_following = null
	lying = false
	_target = point
	agent.target_position = point


## Follows `who` at a few steps' distance until told otherwise.
func follow(who: Node3D) -> void:
	_following = who
	lying = false
	_target = Vector3.INF


func stop() -> void:
	_following = null
	_target = Vector3.INF
	velocity = Vector3.ZERO


## Lies down on a bed: `bed` is the bed's top centre, its long side along local Z.
func lie_down(bed: Transform3D) -> void:
	stop()
	lying = true
	global_transform = bed
	look.rotation = Vector3(-PI * 0.5, 0.0, 0.0)
	look.position = Vector3(0.0, 0.15, 0.9)
	$Shape.disabled = true


## Takes him out of the world, or puts him back at `at`.
func set_present(present: bool, at := Transform3D()) -> void:
	stop()
	visible = present
	set_physics_process(present)
	$Shape.disabled = not present or lying
	if present:
		global_transform = at


## Opens a shut door just ahead; true if he has to stop for it.
func _door_ahead(dir: Vector3) -> bool:
	var from := global_position + Vector3.UP
	for door: Door in get_tree().get_nodes_in_group(&"doors"):
		if door.is_open or door.global_position.distance_to(global_position) > 2.0:
			continue
		if door.crosses(from, from + dir * 1.0):
			if not door.locked:
				door.set_open(true)
				_door_wait = door.open_time
			return true
	return false


## Where a part of him is, for the porter's eyes.
func part_position(part: StringName) -> Vector3:
	var marker := parts.get_node_or_null(NodePath(String(part))) as Node3D
	return marker.global_position if marker else global_position + Vector3.UP * 1.2


## Where his face is, for the conversation camera.
func face_position() -> Vector3:
	return look.face_position()


func face(point: Vector3) -> void:
	var to := point - global_position
	if Vector2(to.x, to.z).length() > 0.05:
		rotation.y = atan2(-to.x, -to.z)


func _physics_process(delta: float) -> void:
	if lying:
		return
	var goal := _target
	# Talking to the porter, he stands where he is; he goes on after.
	if Talk.talking_to == self:
		goal = Vector3.INF
	elif _following:
		goal = _following.global_position
		if global_position.distance_to(goal) < FOLLOW_GAP:
			goal = Vector3.INF
	var flat := Vector3.ZERO
	if goal != Vector3.INF:
		if agent.target_position.distance_to(goal) > 0.3:
			agent.target_position = goal
		var next := agent.get_next_path_position()
		var to := next - global_position
		to.y = 0.0
		if agent.is_navigation_finished():
			if _following == null and _target != Vector3.INF:
				_target = Vector3.INF
				arrived.emit()
		elif _door_wait > 0.0:
			_door_wait -= delta
		elif to.length() > 0.02 and not _door_ahead(to.normalized()):
			flat = to.normalized() * speed
	velocity.x = flat.x
	velocity.z = flat.z
	velocity.y = 0.0 if is_on_floor() else velocity.y - GRAVITY * delta
	move_and_slide()
	if flat.length() > 0.1:
		rotation.y = lerp_angle(rotation.y, atan2(-flat.x, -flat.z), 1.0 - exp(-8.0 * delta))
