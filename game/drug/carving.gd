@tool
class_name Carving
extends Node3D
## A carved saint (Look and Feel, "Dressing rules": religious imagery is
## everywhere; when drugged, these are what move first). From Dose 50 its
## head turns to follow the porter (design doc, "Effect tiers": carvings
## that turn their heads), and back when the drug wears off, but only while
## he isn't looking at it. Faces -Z.

## Dose from which the head follows him.
@export var dose_from := 50.0
## Degrees the head can turn either way.
@export var reach := 80.0

## The head is turned toward him now.
var turned := false

@onready var head: Node3D = $Head


func _ready() -> void:
	if not Engine.is_editor_hint():
		add_to_group(&"carvings")


func _process(_delta: float) -> void:
	if Engine.is_editor_hint():
		return
	var p := get_tree().get_first_node_in_group(&"player") as Player
	if p == null:
		return
	var want := GameState.dose >= dose_from and global_position.distance_to(p.global_position) < 15.0
	if ViewCheck.on_screen(p.camera, [head.global_position]):
		return
	if want:
		var local := global_transform.affine_inverse() * p.camera.global_position
		var yaw := clampf(atan2(-local.x, -local.z), -deg_to_rad(reach), deg_to_rad(reach))
		head.rotation = Vector3(0.0, yaw, 0.0)
		turned = absf(yaw) > 0.05
	elif turned:
		head.rotation = Vector3.ZERO
		turned = false
