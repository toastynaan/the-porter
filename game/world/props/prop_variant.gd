@tool
class_name PropVariant
extends Node3D
## Shows one of its children and hides the rest, picked by where it stands,
## so a row of one prop (beds, tables, graves) isn't a row of one thing.
## The same place always gets the same child.

## The child to show, or -1 to pick by place.
@export var pick := -1:
	set(value):
		pick = value
		_show()
## How likely each child is, in order (empty: all alike).
@export var weights := PackedFloat32Array():
	set(value):
		weights = value
		_show()


func _ready() -> void:
	_show()


func _show() -> void:
	if not is_inside_tree() or get_child_count() == 0:
		return
	var which := clampi(pick, -1, get_child_count() - 1)
	if which < 0:
		var p := global_position
		var h := absi((roundi(p.x * 10.0) * 73856093) ^ (roundi(p.y * 10.0) * 19349663) ^ (roundi(p.z * 10.0) * 83492791))
		var total := 0.0
		for i in get_child_count():
			total += weights[i] if i < weights.size() else 1.0
		var at := float(h % 10007) / 10007.0 * total
		which = get_child_count() - 1
		for i in get_child_count():
			at -= weights[i] if i < weights.size() else 1.0
			if at < 0.0:
				which = i
				break
	for i in get_child_count():
		(get_child(i) as Node3D).visible = i == which
