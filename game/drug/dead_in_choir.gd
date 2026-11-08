class_name DeadInChoir
extends Node3D
## The dead stand in the choir (design doc, "Effect tiers", 75+: dead
## brothers standing in the choir). At Matins, from Dose 75, every brother
## who has died (died_<name>) stands at his place in the choir again, the
## way he looked. They come and go only while the porter isn't looking at
## their places, and leave nothing.

## Where each brother stands at Matins (Places/Matins: markers by name).
@export var places: Node3D
## The brothers (their looks).
@export var brothers: Node3D
@export var dose_from := 75.0

var _figures := {}


func _ready() -> void:
	add_to_group(&"dead_in_choir")


func _process(_delta: float) -> void:
	var p := get_tree().get_first_node_in_group(&"player") as Player
	if p == null or places == null or brothers == null:
		return
	var want := GameState.phase == GameState.Phase.MATINS and GameState.dose >= dose_from
	for b in brothers.get_children():
		var brother := b as Brother
		if brother == null or not brother.is_dead():
			continue
		var marker := places.get_node_or_null(NodePath(String(brother.name))) as Node3D
		if marker == null:
			continue
		var showing := _figures.has(brother.name)
		if want == showing or ViewCheck.on_screen(p.camera, [marker.global_position + Vector3.UP * 1.5, marker.global_position + Vector3.UP * 0.8]):
			continue
		if want and brother.look:
			var fig := CharacterLook.new()
			fig.look = brother.look.look
			fig.add_to_group(&"uncanny")
			add_child(fig)
			fig.global_transform = marker.global_transform
			_figures[brother.name] = fig
		elif not want:
			(_figures[brother.name] as Node3D).queue_free()
			_figures.erase(brother.name)


## How many of the dead stand in the choir now.
func standing() -> int:
	return _figures.size()
