class_name Brazier
extends Node3D
## A watch fire in an iron basket (the model is tools/build/prop_brazier.py):
## its light is never still, and it throws the shadows of whoever stands by
## it up the walls.

## The light's strength, and how much of it the flames' unsteadiness takes.
@export var energy := 3.2
@export_range(0.0, 1.0) var flicker := 0.35
## Its own ironwork throws no shadow (a basket's bars so near the flame
## would stripe the whole wall).
@export var bare := false

var _noise := FastNoiseLite.new()
var _t := randf() * 100.0
var _rest := Vector3.ZERO

@onready var light: OmniLight3D = $Light


func _ready() -> void:
	_noise.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
	_noise.frequency = 1.0
	_rest = light.position
	if bare:
		for mesh: Node in find_children("*", "MeshInstance3D", true, false):
			(mesh as MeshInstance3D).cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF


func _process(delta: float) -> void:
	_t += delta
	var n := 0.5 + 0.5 * _noise.get_noise_1d(_t * 3.4)
	var quick := 0.5 + 0.5 * _noise.get_noise_1d(_t * 11.0 + 40.0)
	light.light_energy = energy * (1.0 - flicker * (0.7 * n + 0.3 * quick))
	# The flame leans about, and the shadows with it.
	light.position = _rest + Vector3(_noise.get_noise_1d(_t * 2.1 + 9.0), 0.0, _noise.get_noise_1d(_t * 2.1 + 70.0)) * 0.07
