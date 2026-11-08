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


func _ready() -> void:
	_light()


func _light() -> void:
	if not is_inside_tree():
		return
	for child in get_children():
		var pane := child as MeshInstance3D
		if pane and (pane.name.begins_with("Window") or pane.name.begins_with("Door")):
			pane.material_override = LIT if lit_windows.has(pane.name) else null
