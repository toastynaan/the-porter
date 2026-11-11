class_name RoadCity
extends Node3D
## The city seen on the road in (night 0), on the skyline model
## (tools/build/env_city_skyline.py).
##
## The far city (St Paul's and the far towers, the model's "Far") is for
## the approach: it is put away once the wagon is deep in the street. (The
## lane and the abbey aren't shown while he is on the road, and the road is
## gone once he is in the lane: RideBeat.)

## East of this the far city isn't shown.
@export var far_until_x := -60.0

var _far: Node3D


func _ready() -> void:
	_far = find_child("Far", true, false) as Node3D


func _process(_delta: float) -> void:
	var p := get_tree().get_first_node_in_group(&"player") as Node3D
	if _far and p:
		_far.visible = p.global_position.x < far_until_x
