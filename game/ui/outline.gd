class_name Outline
## The outline on whatever `interact` would use, while the porter looks at it
## within reach (docs/mechanics.md, "Your hands"; the Interactor calls set_on()
## as its focus changes). It draws over the thing's meshes: a node's own
## `outline` list if it has one (a Duty or a hiding spot names the prop it
## stands for), the person a Talker belongs to, or else the node's own meshes.

const MATERIAL := preload("res://game/ui/outline.tres")
const PREV := &"outline_prev"


## Puts the outline on `target`, or takes it off.
static func set_on(target: Node, on: bool) -> void:
	if target == null or not is_instance_valid(target):
		return
	for mesh in meshes_of(target):
		if on:
			if not mesh.has_meta(PREV):
				mesh.set_meta(PREV, mesh.material_overlay)
			mesh.material_overlay = MATERIAL
		elif mesh.has_meta(PREV):
			mesh.material_overlay = mesh.get_meta(PREV)
			mesh.remove_meta(PREV)


## Whether `target` has the outline on now.
static func is_on(target: Node) -> bool:
	var meshes := meshes_of(target)
	return not meshes.is_empty() and meshes.all(func(m: GeometryInstance3D) -> bool: return m.material_overlay == MATERIAL)


static func meshes_of(target: Node) -> Array[GeometryInstance3D]:
	var roots: Array[Node] = []
	var named: Variant = target.get(&"outline")
	if named is Array and not (named as Array).is_empty():
		for n: Variant in named:
			if n is Node:
				roots.append(n)
	elif target is Talker:
		roots.append(target.get_parent())
	else:
		roots.append(target)
	var out: Array[GeometryInstance3D] = []
	for root in roots:
		_collect(root, out)
	return out


static func _collect(node: Node, out: Array[GeometryInstance3D]) -> void:
	if node is GeometryInstance3D and (node as GeometryInstance3D).visible:
		out.append(node)
	for c in node.get_children(true):
		if c is Light3D or c is Lantern:
			continue
		_collect(c, out)
