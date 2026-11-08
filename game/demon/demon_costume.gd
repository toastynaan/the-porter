@tool
class_name DemonCostume
extends Node3D
## Greybox stand-in for the demon (Look and Feel, "The demon's look"): a man
## of 1.75 m in a black habit whose hem hides his feet, a pale long mask with
## no mouth, wooden finger extensions, and a headdress of stag antlers on
## ram's horns that adds about 60 cm. Faces -Z. Built from primitives here so
## it can be regenerated; the rigged model replaces it in M5.
##
## It drifts with Dose, never pops (render states): from Dose 50 to 74 it
## grows about 15% taller, the eyes glow ember and the mask sinks into the
## hood; from 75 its arms and fingers stretch.
##
## `starable` costumes are in the "demon" group the stare meter watches.

const HEIGHT := 1.75
const HEADDRESS := 0.6
const EMBER := Color("#FF5A1F")
## Dose ranges for the render states. The eyes come on early in the first.
const TALL_DOSE := Vector2(50.0, 74.0)
const EYES_DOSE := Vector2(50.0, 58.0)
## Bright enough to bloom: in the dark the eyes are all you see of it.
const EYE_ENERGY := 16.0
const STRETCH_DOSE := Vector2(75.0, 100.0)
## Growth at the top of each range.
const TALL_SCALE := 0.15
## Greybox guess until the rigged model's blend shapes (M5).
const STRETCH_SCALE := 0.4

@export var starable := true
## Overrides GameState.dose when >= 0 (lookdev, tests).
@export var dose_override := -1.0

## How far into its drugged renders it is now: 0 the costume as it is,
## 1 taller with ember eyes (Dose 74); `stretch` likewise for 75-100.
var tall := 0.0
var stretch := 0.0

var _body: Node3D
var _arms: Array[Node3D] = []
var _mask_mat: StandardMaterial3D
var _eye_mat: StandardMaterial3D
var _mask_color := Color("#D8C9A3")


func _ready() -> void:
	_build()
	if starable and not Engine.is_editor_hint():
		add_to_group(&"demon")


func _process(_delta: float) -> void:
	var d := dose_override
	if d < 0.0:
		d = 0.0 if Engine.is_editor_hint() else GameState.dose
	tall = smoothstep(TALL_DOSE.x, TALL_DOSE.y, d)
	stretch = smoothstep(STRETCH_DOSE.x, STRETCH_DOSE.y, d)
	_body.scale = Vector3(1.0, 1.0 + TALL_SCALE * tall, 1.0)
	for arm in _arms:
		arm.scale = Vector3(1.0, 1.0 + STRETCH_SCALE * stretch, 1.0)
	_mask_mat.albedo_color = _mask_color.lerp(Color(0.05, 0.045, 0.05), 0.85 * tall)
	_eye_mat.emission_energy_multiplier = EYE_ENERGY * smoothstep(EYES_DOSE.x, EYES_DOSE.y, d)


## Points the stare meter and sight checks look at: head and chest.
func stare_points() -> Array[Vector3]:
	var s := _body.scale.y
	return [global_transform * Vector3(0.0, 1.62 * s, 0.0), global_transform * Vector3(0.0, 1.2 * s, 0.0)]


func _build() -> void:
	if _body:
		return
	var wool := _mat(Color("#1E1B19"), 0.95)
	var leather := _mat(Color("#2A2019"), 0.8)
	var antler := _mat(Color("#8A7A5E"), 0.7)
	var horn := _mat(Color("#6B5A3E"), 0.6)
	_mask_mat = _mat(_mask_color, 0.8)
	_eye_mat = _mat(Color.BLACK, 1.0)
	_eye_mat.emission_enabled = true
	_eye_mat.emission = EMBER
	_eye_mat.emission_energy_multiplier = 0.0
	_body = Node3D.new()
	add_child(_body)
	# Habit: a long narrow cone from the dragging hem to the shoulders.
	_part(_body, _cylinder(0.3, 0.19, 1.5, wool), Vector3(0, 0.75, 0))
	_part(_body, _cylinder(0.19, 0.12, 0.12, wool), Vector3(0, 1.56, 0))
	# Hood round the head, mask in front, eyes in the mask.
	_part(_body, _sphere(0.15, 0.36, wool), Vector3(0, 1.64, 0.01))
	_part(_body, _box(Vector3(0.13, 0.27, 0.04), _mask_mat), Vector3(0, 1.6, -0.13))
	for x in [-0.034, 0.034]:
		_part(_body, _box(Vector3(0.034, 0.016, 0.01), _eye_mat), Vector3(x, 1.65, -0.152))
	# Leather cap, ram's horns curling at the sides, antlers rising 60 cm.
	_part(_body, _cylinder(0.13, 0.15, 0.06, leather), Vector3(0, 1.79, 0.01))
	for side in [-1.0, 1.0]:
		_part(_body, _cylinder(0.035, 0.02, 0.2, horn), Vector3(side * 0.15, 1.74, 0.02), Vector3(0.6, 0, side * 1.9))
		_antler(side, antler)
	for side in [-1.0, 1.0]:
		var arm := Node3D.new()
		arm.position = Vector3(side * 0.2, 1.48, -0.02)
		_body.add_child(arm)
		_arms.append(arm)
		_part(arm, _cylinder(0.055, 0.045, 0.62, wool), Vector3(0, -0.31, 0), Vector3(0, 0, side * 0.06))
		# Gloved hand with carved finger extensions.
		_part(arm, _box(Vector3(0.07, 0.09, 0.04), leather), Vector3(side * 0.04, -0.66, 0))
		for f in 4:
			_part(arm, _box(Vector3(0.012, 0.16, 0.012), antler), Vector3(side * 0.04 + (f - 1.5) * 0.017, -0.78, 0))


## A stag antler: a main beam leaning out and back to the full height, with tines.
func _antler(side: float, mat: Material) -> void:
	var base := Vector3(side * 0.08, 1.82, 0.02)
	var tip := Vector3(side * 0.34, HEIGHT + HEADDRESS, 0.1)
	_beam(base, tip, 0.022, mat)
	for t in [0.35, 0.6, 0.85]:
		var at := base.lerp(tip, t)
		_beam(at, at + Vector3(side * 0.03, 0.13, -0.11), 0.012, mat)


func _beam(from: Vector3, to: Vector3, radius: float, mat: Material) -> void:
	var mesh := _cylinder(radius, radius * 0.6, from.distance_to(to), mat)
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	var up := (to - from).normalized()
	var side := up.cross(Vector3.FORWARD).normalized()
	mi.transform = Transform3D(Basis(side, up, side.cross(up)), (from + to) * 0.5)
	_body.add_child(mi)


func _part(parent: Node3D, mesh: Mesh, at: Vector3, euler := Vector3.ZERO) -> void:
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.position = at
	mi.rotation = euler
	parent.add_child(mi)


func _mat(color: Color, roughness: float) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.roughness = roughness
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
