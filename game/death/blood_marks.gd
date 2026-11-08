class_name BloodMarks
extends Node3D
## Blood and marks that stay (docs/full-game-run.md, "Blood and marks"): every
## mark a death leaves is kept in GameState.marks and stands in the abbey on
## every night after, until the cult cleans it. Each dawn they scrub what
## would prove men did it (drag marks, boot prints in blood) and miss the
## rest (clean_at_dawn), so the abbey gets worse night by night. One node per
## night, in night_base.tscn; marks spawn under it.

const SCENES := {
	&"pool": preload("res://game/world/props/prop_blood_pool.tscn"),
	&"spray": preload("res://game/world/props/prop_blood_spray.tscn"),
	&"drag": preload("res://game/world/props/prop_drag_marks.tscn"),
	&"print": preload("res://game/world/props/prop_blood_print.tscn"),
}
## The kinds that prove men did it, which the cult scrubs at dawn.
const PROVES_MEN: Array[StringName] = [&"drag", &"print"]


func _ready() -> void:
	add_to_group(&"blood_marks")
	for m: Dictionary in GameState.marks:
		_spawn(m)


## Leaves a mark of `kind` at `xform` (kept), from the death or body `id`.
## Returns the node.
static func add(tree: SceneTree, kind: StringName, xform: Transform3D, id: StringName) -> Node3D:
	var m := {"kind": kind, "xform": xform, "night": GameState.night, "id": id, "proves_men": PROVES_MEN.has(kind)}
	GameState.marks.append(m)
	var holder := tree.get_first_node_in_group(&"blood_marks") as BloodMarks
	return holder._spawn(m) if holder else null


## A mark that isn't kept (a hallucination's): gone once the porter looks away.
static func add_fleeting(parent: Node3D, kind: StringName, xform: Transform3D) -> Node3D:
	var node := (SCENES[kind] as PackedScene).instantiate() as Node3D
	parent.add_child(node)
	node.global_transform = xform
	return node


## Removes the marks left by `id` (a body the cult moved takes its proof with it).
static func remove_for(tree: SceneTree, id: StringName, only_proof := false) -> void:
	GameState.marks = GameState.marks.filter(func(m: Dictionary) -> bool:
		return not (m.get("id") == id and (not only_proof or m.get("proves_men", false))))
	_refresh(tree)


## Dawn: the cult scrubs everything that proves men did it.
static func clean_at_dawn(tree: SceneTree) -> void:
	GameState.marks = GameState.marks.filter(func(m: Dictionary) -> bool: return not m.get("proves_men", false))
	_refresh(tree)


static func count(kind: StringName = &"") -> int:
	return GameState.marks.filter(func(m: Dictionary) -> bool: return kind == &"" or m.get("kind") == kind).size()


static func _refresh(tree: SceneTree) -> void:
	var holder := tree.get_first_node_in_group(&"blood_marks") as BloodMarks
	if holder == null:
		return
	for c in holder.get_children():
		c.queue_free()
	for m: Dictionary in GameState.marks:
		holder._spawn(m)


func _spawn(m: Dictionary) -> Node3D:
	var scene: PackedScene = SCENES.get(m.get("kind"), SCENES[&"pool"])
	var node := scene.instantiate() as Node3D
	add_child(node)
	node.global_transform = m.get("xform", Transform3D())
	return node
