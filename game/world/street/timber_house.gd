@tool
class_name TimberHouse
extends Node3D
## A house in the lane outside the gate (Look and Feel, "The lane outside the
## gate": lit windows show who is awake). The windows named in `lit_windows`
## glow and the rest are dark. Each house type is its own scene in
## game/world/street/, so its placeholder parts can be swapped for a model.

const LIT := preload("res://game/world/materials/window_lit.tres")

@export var lit_windows := PackedStringArray():
	set(value):
		lit_windows = value
		_light()
## What a lit pane is made of (left empty: the plain glow).
@export var lit_material: Material:
	set(value):
		lit_material = value
		_light()


func _ready() -> void:
	_light()


func _light() -> void:
	if not is_inside_tree():
		return
	# The panes are the house's own children, or inside its model.
	for child in find_children("*", "MeshInstance3D", true, false):
		var pane := child as MeshInstance3D
		if pane.name.begins_with("Window") or pane.name.begins_with("Door"):
			pane.material_override = (lit_material if lit_material else LIT) if lit_windows.has(pane.name) else null
