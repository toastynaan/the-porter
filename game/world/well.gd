class_name Well
extends Node3D
## The court well. Draw water and drink: clean on nights 1-3, but from night
## 4 the cult doses it too, +5 a drink (design doc, "Sources"). The first
## time he draws water from night 1, the bucket comes up heavy: the hidden
## body down the well (`hidden`).

const DOSE := 5.0
const DOSED_FROM := 4

@export var hidden: HiddenBody
@export var size := Vector3(1.6, 1.2, 1.6)

var _area: Area3D


func _ready() -> void:
	_area = Area3D.new()
	_area.collision_layer = Layers.INTERACT
	_area.collision_mask = 0
	_area.monitoring = false
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = size
	shape.shape = box
	shape.position = Vector3(0, size.y * 0.5, 0)
	_area.add_child(shape)
	add_child(_area)


func interact(_by: Node) -> void:
	if hidden and hidden.available() and not hidden.is_found:
		Talk.say("", hidden.reveal_line)
		hidden.uncover()
		return
	drink()


func drink() -> void:
	GameState.set_flag(GameState.tonight("drank_well"))
	if GameState.night >= DOSED_FROM:
		GameState.add_dose(DOSE, 3.0)
		Talk.say("", "(Cold water. There's a taste under it, faintly sweet.)")
	else:
		Talk.say("", "(Cold water. It tastes of stone.)")
