class_name Rooks
extends MultiMeshInstance3D
## Rooks over the fields at dusk (design doc, "Animals as tells": rooks): a
## loose flock wheeling above the tree this stands at, each bird on its own
## slow circle, black against the last light. They are a shape in the sky,
## nothing more: two wings that beat (the shader), no collision, no sound of
## their own here.

@export var birds := 26
## How wide and how high they wheel, m.
@export var radius := Vector2(6.0, 30.0)
@export var height := Vector2(9.0, 24.0)
## How fast, m/s.
@export var pace := Vector2(5.0, 8.5)
@export var wingspan := 0.95

const SHADER := """shader_type spatial;
render_mode unshaded, cull_disabled;
// A rook: its wings beat about its back; each bird in its own time.
void vertex() {
	float beat = sin(TIME * (7.0 + INSTANCE_CUSTOM.x * 3.0) + INSTANCE_CUSTOM.y * 6.283);
	// It glides between beats.
	beat *= step(-0.2, sin(TIME * 0.6 + INSTANCE_CUSTOM.y * 20.0));
	VERTEX.y += abs(VERTEX.x) * (beat * 0.75 + 0.15);
}
void fragment() {
	ALBEDO = vec3(0.012, 0.012, 0.014);
}
"""

## Each bird: [radius, height, speed (radians a second), phase, tilt of its circle, wobble].
var _paths: Array = []
var _t := 0.0


func _ready() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = 1420
	var mesh := ArrayMesh.new()
	var w := wingspan * 0.5
	# A body and two wings, flat: nose at -Z.
	var verts := PackedVector3Array([
		Vector3(0, 0, -0.2), Vector3(0.05, 0, 0.16), Vector3(-0.05, 0, 0.16),
		Vector3(0.03, 0, -0.1), Vector3(w, 0, 0.02), Vector3(0.03, 0, 0.1),
		Vector3(-0.03, 0, -0.1), Vector3(-0.03, 0, 0.1), Vector3(-w, 0, 0.02)])
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = verts
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	var shader := Shader.new()
	shader.code = SHADER
	var mat := ShaderMaterial.new()
	mat.shader = shader
	mesh.surface_set_material(0, mat)
	multimesh = MultiMesh.new()
	multimesh.transform_format = MultiMesh.TRANSFORM_3D
	multimesh.use_custom_data = true
	multimesh.mesh = mesh
	multimesh.instance_count = birds
	cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	extra_cull_margin = radius.y + height.y
	for i in birds:
		var r := rng.randf_range(radius.x, radius.y)
		var speed := rng.randf_range(pace.x, pace.y) / r * (1.0 if rng.randf() < 0.8 else -1.0)
		_paths.append([r, rng.randf_range(height.x, height.y), speed, rng.randf() * TAU, rng.randf_range(-0.12, 0.12), rng.randf() * TAU])
		multimesh.set_instance_custom_data(i, Color(rng.randf(), rng.randf(), 0.0, 0.0))
	_place()


func _process(delta: float) -> void:
	_t += delta
	_place()


func _place() -> void:
	for i in _paths.size():
		var path: Array = _paths[i]
		var a: float = path[3] + _t * float(path[2])
		var r: float = float(path[0]) * (1.0 + 0.18 * sin(_t * 0.23 + float(path[5])))
		var at := Vector3(cos(a) * r, float(path[1]) + sin(a + float(path[5])) * float(path[0]) * float(path[4]) + sin(_t * 0.4 + float(path[5])) * 1.2, sin(a) * r)
		# Nose along the way it flies, banked into its turn.
		var heading := Vector3(-sin(a), 0.0, cos(a)) * signf(float(path[2]))
		var facing := Basis.looking_at(heading, Vector3.UP).rotated(heading, 0.35 * signf(float(path[2])))
		multimesh.set_instance_transform(i, Transform3D(facing, at))
