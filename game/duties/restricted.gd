class_name Restricted
extends Node3D
## Somewhere the porter shouldn't be seen (docs/systems/mechanics.md, "Being seen"):
## the crypt at any time, the granary and stores after Compline, the
## dormitory floor at night. A box (`size`, centred on the node) and the
## hours it counts in. SeenWatch does the seeing.

## Names the flag: n<night>_seen_<place>.
@export var place := &""
## For the dawn remark: "in the crypt".
@export var where := ""
@export var size := Vector3(4, 3, 4)
## Counts from this hour (in the night's hours, 30 = 06:00 next morning); -1: any time.
@export var from_hour := -1.0
@export var until_hour := -1.0


func _ready() -> void:
	add_to_group(&"restricted")


func contains(point: Vector3) -> bool:
	var local := global_transform.affine_inverse() * point
	return absf(local.x) <= size.x * 0.5 and absf(local.y) <= size.y * 0.5 and absf(local.z) <= size.z * 0.5


func active() -> bool:
	var h := GameState.hour
	return (from_hour < 0.0 or h >= from_hour) and (until_hour < 0.0 or h < until_hour)
