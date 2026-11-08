@tool
class_name BrotherFigure
extends Node3D
## Greybox stand-in for a brother (Look and Feel, "Characters": every brother
## wears the same black habit, and is told apart by build, face, prop and
## sound). A habit, a hood and a face, scaled by build from the character
## table. Built here so it can be regenerated. Each character's scene in
## game/characters/ holds one, so the model replaces it there. Faces -Z.

enum Build { AVERAGE, TALL_THIN, SHORT_HEAVY, SMALL_FRAIL, LEAN, GANGLY, HUNCHED, BIG }

## Height and width multipliers per build, on the 1.75 m reference figure.
## Greybox reads of the character table's words, not measurements.
const BUILDS := {
	Build.AVERAGE: Vector2(1.0, 1.0),
	Build.TALL_THIN: Vector2(1.06, 0.88),
	Build.SHORT_HEAVY: Vector2(0.92, 1.25),
	Build.SMALL_FRAIL: Vector2(0.92, 0.92),
	Build.LEAN: Vector2(1.02, 0.9),
	Build.GANGLY: Vector2(1.04, 0.86),
	Build.HUNCHED: Vector2(0.86, 1.0),
	Build.BIG: Vector2(1.04, 1.3),
}
const HEIGHT := 1.75

@export var build := Build.AVERAGE:
	set(value):
		build = value
		_rebuild()
## Hood pulled forward over the face: a stranger in a habit.
@export var hood_up := false:
	set(value):
		hood_up = value
		_rebuild()
@export var face_color := Color("#B89A80"):
	set(value):
		face_color = value
		_rebuild()
## Brown work tunic instead of the habit (Cole and Dunstan).
@export var tunic := false:
	set(value):
		tunic = value
		_rebuild()
## A cloak of this colour instead of the habit, when its alpha is above 0
## (Walter: the only saturated colour on any character).
@export var cloth_color := Color(0, 0, 0, 0):
	set(value):
		cloth_color = value
		_rebuild()

var _parts: Node3D


func _ready() -> void:
	_rebuild()


func _rebuild() -> void:
	if not is_inside_tree():
		return
	if _parts:
		_parts.queue_free()
	_parts = Node3D.new()
	add_child(_parts)
	var k: Vector2 = BUILDS[build]
	_parts.scale = Vector3(k.y, k.x, k.y)
	var cloth_col := Color("#4A3828") if tunic else Color("#1E1B19")
	if cloth_color.a > 0.0:
		cloth_col = Color(cloth_color, 1.0)
	var cloth := _mat(cloth_col)
	_add(_cylinder(0.27, 0.2, 1.45, cloth), Vector3(0, 0.725, 0))
	_add(_cylinder(0.2, 0.1, 0.12, cloth), Vector3(0, 1.5, 0))
	_add(_sphere(0.14, 0.32, cloth), Vector3(0, 1.62, 0.02))
	var face := _mat(Color(0.03, 0.03, 0.03) if hood_up else face_color)
	_add(_box(Vector3(0.14, 0.18, 0.04), face), Vector3(0, 1.6, -0.115 if not hood_up else -0.06))
	if hood_up:
		_add(_cylinder(0.16, 0.16, 0.1, cloth), Vector3(0, 1.66, -0.1), Vector3(PI * 0.5, 0, 0))


func _add(mesh: Mesh, at: Vector3, euler := Vector3.ZERO) -> void:
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.position = at
	mi.rotation = euler
	_parts.add_child(mi)


func _mat(color: Color) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.roughness = 0.95
	return m


func _cylinder(bottom: float, top: float, height: float, mat: Material) -> CylinderMesh:
	var c := CylinderMesh.new()
	c.bottom_radius = bottom
	c.top_radius = top
	c.height = height
	c.radial_segments = 8
	c.rings = 1
	c.material = mat
	return c


func _sphere(radius: float, height: float, mat: Material) -> SphereMesh:
	var s := SphereMesh.new()
	s.radius = radius
	s.height = height
	s.radial_segments = 8
	s.rings = 4
	s.material = mat
	return s


func _box(box_size: Vector3, mat: Material) -> BoxMesh:
	var b := BoxMesh.new()
	b.size = box_size
	b.material = mat
	return b
