class_name Squeeze
extends Area3D
## A gap only the porter fits through: under the mill wheel, down the latrine
## chute (design doc, "The hunter is a man"). Interact at either end and the
## player crawls along the child Marker3Ds in order (reversed from the far
## end). The gap is too low for the navmesh, so hunters must go round.

## Seconds the whole crawl takes.
@export var crawl_time := 2.5
## Only from the first marker (a chute you drop down).
@export var one_way := false
## Eye height while crawling, m.
@export var eye_height := 0.6


func _ready() -> void:
	collision_layer = Layers.INTERACT
	collision_mask = 0
	monitoring = false


func points() -> Array[Vector3]:
	var out: Array[Vector3] = []
	for child in get_children():
		if child is Marker3D:
			out.append((child as Marker3D).global_position)
	return out


func interact(by: Node) -> void:
	var path := points()
	if path.size() < 2 or not by.has_method(&"crawl_along"):
		return
	var from: Vector3 = (by as Node3D).global_position
	if from.distance_to(path[-1]) < from.distance_to(path[0]):
		if one_way:
			return
		path.reverse()
	by.crawl_along(path, crawl_time, eye_height)
