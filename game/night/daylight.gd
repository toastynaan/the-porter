class_name Daylight
extends Node
## The light of the hour: failing daylight at dusk fading into night, and
## grey morning at dawn (design doc, "Core loop": waking at dusk, sleeping at
## dawn). Day is overcast, flat and grey with no strong shadows (Look and
## Feel, "Lighting rules" 6), so daylight raises the sky and the ambient
## light in the night's own moonlight colour, with a soft, shadowless light
## from the low sun's side. The sky itself (game/render/sky.gdshader) is
## told how much day is left and where the sun went down: flat at night,
## overcast by day, a strip of dying light at dusk. The lane's lanterns are
## lit once it is dark (London's order of 1415).

## Hours over which dusk turns to night, and night to morning.
@export var dusk := Vector2(16.0, 17.5)
@export var dawn := Vector2(30.0, 31.0)
@export var world_environment: WorldEnvironment
@export var moon: DirectionalLight3D
## Lit when it gets dark (Candle children).
@export var street_lanterns: Node3D
## Full daylight: sky brightness, ambient light, and the soft sun.
@export var day_sky := 0.8
@export var day_ambient := 0.8
@export var day_sun := 0.4

## 1 in daylight, 0 at night.
var light := 0.0

var _env: Environment
var _night_sky := 0.0
var _night_ambient := 0.0
var _moon_energy := 0.0
var _sun: DirectionalLight3D
var _sky: ShaderMaterial
var _lanterns_lit := true


func _ready() -> void:
	_env = world_environment.environment.duplicate()
	world_environment.environment = _env
	_night_sky = _env.background_energy_multiplier
	_night_ambient = _env.ambient_light_energy
	_moon_energy = moon.light_energy
	if _env.sky:
		_sky = _env.sky.sky_material as ShaderMaterial
	_sun = DirectionalLight3D.new()
	_sun.light_color = moon.light_color
	_sun.shadow_enabled = false
	add_child(_sun)
	_apply()


func _process(_delta: float) -> void:
	_apply()


func _apply() -> void:
	var h := GameState.hour
	light = clampf(1.0 - smoothstep(dusk.x, dusk.y, h) + smoothstep(dawn.x, dawn.y, h), 0.0, 1.0)
	_env.background_energy_multiplier = lerpf(_night_sky, day_sky, light)
	_env.ambient_light_energy = lerpf(_night_ambient, day_ambient, light)
	moon.light_energy = _moon_energy * (1.0 - light)
	_sun.light_energy = day_sun * light
	_sun.visible = light > 0.01
	# Low in the west at dusk, in the east at dawn.
	var toward := Vector3(1.0, -0.3, -0.2) if h < 24.0 else Vector3(-1.0, -0.3, 0.2)
	_sun.basis = Basis.looking_at(toward.normalized())
	# The sky (game/render/sky.gdshader): its cloud and its strip of last light.
	if _sky:
		_sky.set_shader_parameter(&"light", light)
		_sky.set_shader_parameter(&"glow_dir", -toward)
	var dark := light < 0.5
	if street_lanterns and dark != _lanterns_lit:
		_lanterns_lit = dark
		for c in street_lanterns.get_children():
			if c is Candle:
				(c as Candle).lit = dark
