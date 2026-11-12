class_name Weather
extends Node3D
## The night's weather (docs/log/full-game-run.md, "Weather"; design doc,
## "Weather changes the space"), set on each night's scene:
## - RAIN (nights 1-2): halves what the hunter hears, and what the porter
##   hears of him (hearing_factor; the hunters' sounds carry half as far).
## - FOG (night 4): cuts sight to a few metres for both (FOG_SIGHT), but a
##   lit lantern is a glowing ball anyone can see from LANTERN_GLOW off.
## - SNOW (night 6): footprints, which he and the hunters can follow
##   (Footprints).
## Rain and snow fall around the porter; the fog thickens the volumetric fog.
##
## Rain is GPU particles (rain_fall.gdshader moves the drops,
## rain_drop.gdshader draws them): a slab of drops born over the camera,
## falling on the wind onto a height field of whatever is under the sky
## there, so it stops at roofs and arches and splashes where it lands.

enum Kind { CLEAR, RAIN, FOG, SNOW }

const RAIN_LOOP := preload("res://art/sfx/amb_rain_loop.wav")
const RAIN_HEARING := 0.5
## Sight in the fog, m, either way; and how far off an uncovered lantern
## shows as a glow there.
const FOG_SIGHT := 4.0
const LANTERN_GLOW := 14.0
const FOG_DENSITY := 0.22
const RAIN_FALL := preload("res://game/world/weather/rain_fall.gdshader")
const RAIN_DROP := preload("res://game/world/weather/rain_drop.gdshader")
## Drops in the air at once, the slab they are born in (half its size, m),
## how far over the camera it hangs, how fast they fall and the wind, m/s.
const RAIN_DROPS := 16000
const RAIN_SLAB := Vector3(16.0, 0.5, 16.0)
const RAIN_ABOVE := 12.0
const RAIN_SPEED := 11.5
const RAIN_WIND := Vector3(1.6, 0.0, 0.5)
## The height field the rain lands on: its size about the camera, m.
const RAIN_COVER := Vector3(38.0, 48.0, 38.0)

@export var kind := Kind.CLEAR
@export var world_environment: WorldEnvironment
## The weather clears at this hour (night 0: rain at dusk, then clear); -1 never.
@export var clears_at := -1.0

var _fall: GeometryInstance3D
var _cover: GPUParticlesCollisionHeightField3D
var _rain: AudioStreamPlayer


func _ready() -> void:
	add_to_group(&"weather")
	match kind:
		Kind.RAIN:
			_fall = _rain_fall()
			_rain = AudioStreamPlayer.new()
			_rain.stream = AudioOut.looped(RAIN_LOOP)
			_rain.volume_db = -12.0
			add_child(_rain)
			if AudioOut.enabled():
				_rain.play()
		Kind.SNOW:
			_fall = _particles(Color(0.85, 0.87, 0.9, 0.8), Vector2(0.03, 0.03), 1.0, 900)
		Kind.FOG:
			_thicken.call_deferred()


static func now(tree: SceneTree) -> Kind:
	var w := tree.get_first_node_in_group(&"weather") as Weather
	return w.kind if w else Kind.CLEAR


## What hunters hear (and what he hears of them), as a share of clear air.
static func hearing_factor(tree: SceneTree) -> float:
	return RAIN_HEARING if now(tree) == Kind.RAIN else 1.0


## How far anyone sees, given how far they'd see in clear air.
static func sight(tree: SceneTree, clear_range: float) -> float:
	return minf(clear_range, FOG_SIGHT) if now(tree) == Kind.FOG else clear_range


func _thicken() -> void:
	if not is_inside_tree():
		return
	if world_environment and world_environment.environment:
		var env := world_environment.environment
		env.volumetric_fog_enabled = true
		env.volumetric_fog_density = FOG_DENSITY


func _rain_fall() -> GPUParticles3D:
	var fall := ShaderMaterial.new()
	fall.shader = RAIN_FALL
	fall.set_shader_parameter(&"extents", RAIN_SLAB)
	fall.set_shader_parameter(&"speed", RAIN_SPEED)
	fall.set_shader_parameter(&"wind", RAIN_WIND)
	var drop := ShaderMaterial.new()
	drop.shader = RAIN_DROP
	drop.set_shader_parameter(&"fall", RAIN_WIND + Vector3.DOWN * RAIN_SPEED)
	var quad := QuadMesh.new()
	quad.material = drop
	var p := GPUParticles3D.new()
	p.amount = RAIN_DROPS
	# Long enough to fall from the slab to well under the camera.
	p.lifetime = (RAIN_ABOVE + 5.0) / RAIN_SPEED
	p.preprocess = p.lifetime
	p.local_coords = false
	p.process_material = fall
	p.draw_pass_1 = quad
	p.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	p.collision_base_size = 0.02
	var reach := RAIN_SLAB.x + 6.0
	p.visibility_aabb = AABB(Vector3(-reach, -RAIN_ABOVE - 8.0, -reach), Vector3(reach * 2.0, RAIN_ABOVE + 10.0, reach * 2.0))
	add_child(p)
	_cover = GPUParticlesCollisionHeightField3D.new()
	_cover.size = RAIN_COVER
	_cover.resolution = GPUParticlesCollisionHeightField3D.RESOLUTION_512
	_cover.update_mode = GPUParticlesCollisionHeightField3D.UPDATE_MODE_WHEN_MOVED
	add_child(_cover)
	return p


func _particles(color: Color, size: Vector2, speed: float, amount: int) -> CPUParticles3D:
	var p := CPUParticles3D.new()
	p.amount = amount
	p.lifetime = 2.0 if speed > 3.0 else 9.0
	p.emission_shape = CPUParticles3D.EMISSION_SHAPE_BOX
	p.emission_box_extents = Vector3(14.0, 0.5, 14.0)
	p.direction = Vector3(0.05, -1.0, 0.0)
	p.spread = 4.0 if speed > 3.0 else 25.0
	p.gravity = Vector3.ZERO
	p.initial_velocity_min = speed * 0.9
	p.initial_velocity_max = speed * 1.1
	var quad := QuadMesh.new()
	quad.size = size
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.albedo_color = color
	mat.billboard_mode = BaseMaterial3D.BILLBOARD_FIXED_Y if speed > 3.0 else BaseMaterial3D.BILLBOARD_PARTICLES
	quad.material = mat
	p.mesh = quad
	p.local_coords = false
	add_child(p)
	return p


func _process(_delta: float) -> void:
	if clears_at >= 0.0 and kind != Kind.CLEAR and GameState.hour >= clears_at:
		kind = Kind.CLEAR
		if _fall:
			_fall.set(&"emitting", false)
		if _rain:
			_rain.stop()
	if _fall:
		var camera := get_viewport().get_camera_3d()
		if camera:
			_fall.global_position = camera.global_position + Vector3.UP * (RAIN_ABOVE if _cover else 8.0)
			if _cover:
				_cover.global_position = camera.global_position
