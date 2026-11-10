class_name RoadCity
extends Node3D
## The city seen on the road in (night 0), on the skyline model
## (tools/build/env_city_skyline.py).
##
## - The lane's own greybox stand-ins for the city (the nearer blocks of its
##   skyline, and the wall that closes the far end of its bend, which stands
##   across this road) are in the group "road_in_hides": tonight the real
##   ones are here, so those go.
## - The far city (St Paul's and the far towers, the model's "Far") is for
##   the approach. Once the wagon is near the lane it is put away, so the
##   abbey's own sky is as it is on every other night.

## East of this the far city isn't shown.
@export var far_until_x := -60.0

var _far: Node3D


func _ready() -> void:
	_far = find_child("Far", true, false) as Node3D
	for n in get_tree().get_nodes_in_group(&"road_in_hides"):
		n.queue_free()


func _process(_delta: float) -> void:
	var p := get_tree().get_first_node_in_group(&"player") as Node3D
	if _far and p:
		_far.visible = p.global_position.x < far_until_x
