class_name Drips
extends GPUParticles3D
## Water coming off an eave or a parapet after rain: a line of heavy drops
## along this node's x axis, `length` metres long, falling straight down.
## They are the rain's own drops (rain_fall.gdshader, rain_drop.gdshader),
## slower and fatter, and like it they splash where the night's Weather
## says the ground or a roof is. Put the node just clear of the edge the
## water leaves: a drop born under cover is put out.

const RAIN_FALL := preload("res://game/world/weather/rain_fall.gdshader")
const RAIN_DROP := preload("res://game/world/weather/rain_drop.gdshader")

## How long the dripping edge is, m, how far the drops fall, m, and how many drops a metre are in the air.
@export var length := 6.0
@export var drop := 9.0
@export var per_metre := 5.0
@export var speed := 7.5


func _ready() -> void:
	var fall := ShaderMaterial.new()
	fall.shader = RAIN_FALL
	fall.set_shader_parameter(&"extents", Vector3(length * 0.5, 0.05, 0.06))
	fall.set_shader_parameter(&"speed", speed)
	fall.set_shader_parameter(&"wind", Vector3.ZERO)
	fall.set_shader_parameter(&"gust", 0.0)
	var look := ShaderMaterial.new()
	look.shader = RAIN_DROP
	look.set_shader_parameter(&"fall", Vector3.DOWN)
	look.set_shader_parameter(&"streak", 0.3)
	look.set_shader_parameter(&"width", 0.02)
	look.set_shader_parameter(&"alpha", 0.5)
	var quad := QuadMesh.new()
	quad.material = look
	amount = maxi(int(length * per_metre), 1)
	lifetime = drop / speed
	preprocess = lifetime
	randomness = 1.0
	local_coords = false
	process_material = fall
	draw_pass_1 = quad
	cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	collision_base_size = 0.02
	visibility_aabb = AABB(Vector3(-length * 0.5 - 1.0, -drop - 1.0, -1.5), Vector3(length + 2.0, drop + 2.0, 3.0))
