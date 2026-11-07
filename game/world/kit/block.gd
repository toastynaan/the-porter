@tool
class_name Block
extends StaticBody3D
## A greybox solid standing on its origin (bottom centre): a box, a gable roof
## (ridge along local Z) or a cylinder (axis along local Y, size.x across),
## with matching collision. Change the size, shape or material in the
## inspector and it rebuilds. Footsteps read `surface`.

enum Shape { BOX, GABLE, CYLINDER }

@export var size := Vector3(4, 4, 0.8):
	set(value):
		size = value
		_rebuild()
@export var shape := Shape.BOX:
	set(value):
		shape = value
		_rebuild()
@export var material: Material:
	set(value):
		material = value
		_rebuild()
## What footsteps on top of it sound like.
@export_enum("stone", "wood", "mud", "grass") var surface := "stone":
	set(value):
		surface = value
		if is_inside_tree():
			set_meta(&"surface", value)
## Off for things you walk through (water, cloth).
@export var solid := true:
	set(value):
		solid = value
		_rebuild()

var _mesh: MeshInstance3D
var _collision: CollisionShape3D


func _ready() -> void:
	set_meta(&"surface", surface)
	_rebuild()


func _rebuild() -> void:
	if not is_inside_tree():
		return
	if _mesh == null:
		_mesh = MeshInstance3D.new()
		add_child(_mesh)
		_collision = CollisionShape3D.new()
		add_child(_collision)
	var mesh: PrimitiveMesh
	match shape:
		Shape.GABLE:
			var prism := PrismMesh.new()
			prism.size = size
			mesh = prism
			var hull := ConvexPolygonShape3D.new()
			var h := size * 0.5
			hull.points = PackedVector3Array([
				Vector3(-h.x, -h.y, -h.z), Vector3(h.x, -h.y, -h.z), Vector3(0, h.y, -h.z),
				Vector3(-h.x, -h.y, h.z), Vector3(h.x, -h.y, h.z), Vector3(0, h.y, h.z)])
			_collision.shape = hull
		Shape.CYLINDER:
			var cylinder := CylinderMesh.new()
			cylinder.top_radius = size.x * 0.5
			cylinder.bottom_radius = size.x * 0.5
			cylinder.height = size.y
			cylinder.radial_segments = 16
			cylinder.rings = 1
			mesh = cylinder
			var cs := CylinderShape3D.new()
			cs.radius = size.x * 0.5
			cs.height = size.y
			_collision.shape = cs
		_:
			var box := BoxMesh.new()
			box.size = size
			mesh = box
			var bs := BoxShape3D.new()
			bs.size = size
			_collision.shape = bs
	mesh.material = material
	_mesh.mesh = mesh
	_mesh.position = Vector3(0, size.y * 0.5, 0)
	_collision.position = _mesh.position
	_collision.disabled = not solid
