@tool
class_name Stairs
extends StaticBody3D
## A straight greybox stair: its origin is the bottom of the first step
## (front edge, centred) and it climbs `rise` over `run` toward local -Z.
## The steps are only visual; the collision is a smooth ramp under them, so
## the player and the hunters walk it like a slope.

@export var rise := 4.0:
	set(value):
		rise = value
		_rebuild()
@export var run := 6.0:
	set(value):
		run = value
		_rebuild()
@export var width := 1.2:
	set(value):
		width = value
		_rebuild()
## Target step height, m; the step count is rounded from it.
@export var step_height := 0.25:
	set(value):
		step_height = value
		_rebuild()
@export var material: Material:
	set(value):
		material = value
		_rebuild()

## Off where a model shows the stair: still walked on, not drawn.
@export var shown := true:
	set(value):
		shown = value
		_rebuild()

var _mesh: MeshInstance3D
var _collision: CollisionShape3D


func _ready() -> void:
	set_meta(&"surface", "stone")
	_rebuild()


func _rebuild() -> void:
	if not is_inside_tree():
		return
	if _mesh == null:
		_mesh = MeshInstance3D.new()
		add_child(_mesh)
		_collision = CollisionShape3D.new()
		add_child(_collision)
	var steps := maxi(1, roundi(rise / step_height))
	var depth := run / steps
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in steps:
		var h := rise * (i + 1) / steps
		var box := BoxMesh.new()
		box.size = Vector3(width, h, depth)
		st.append_from(box, 0, Transform3D(Basis.IDENTITY, Vector3(0, h * 0.5, -depth * (i + 0.5))))
	var mesh := st.commit()
	mesh.surface_set_material(0, material)
	_mesh.mesh = mesh
	_mesh.visible = shown
	var ramp := ConvexPolygonShape3D.new()
	var w := width * 0.5
	ramp.points = PackedVector3Array([
		Vector3(-w, 0, 0), Vector3(w, 0, 0),
		Vector3(-w, 0, -run), Vector3(w, 0, -run),
		Vector3(-w, rise, -run), Vector3(w, rise, -run)])
	_collision.shape = ramp
