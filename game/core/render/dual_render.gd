class_name DualRender
extends Node3D
## Shows an object as it really is or as the drugged porter sees it (design
## doc, "Same event, two renders"): child "Real" below `threshold` Dose,
## child "Drugged" at or above it. It only swaps while out of the porter's
## view, so he never sees one turn into the other.

@export var threshold := 50.0

## True while the drugged version is showing.
var drugged := false

@onready var real: Node3D = $Real
@onready var drugged_node: Node3D = $Drugged


func _ready() -> void:
	_apply(GameState.dose >= threshold)


func _process(_delta: float) -> void:
	var want := GameState.dose >= threshold
	if want == drugged:
		return
	var camera := get_viewport().get_camera_3d()
	if camera and ViewCheck.on_screen(camera, [global_position + Vector3.UP * 1.6, global_position + Vector3.UP * 0.8]):
		return
	_apply(want)


func _apply(value: bool) -> void:
	drugged = value
	real.visible = not value
	drugged_node.visible = value
