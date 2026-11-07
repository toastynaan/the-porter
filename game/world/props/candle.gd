class_name Candle
extends Node3D
## A lit candle: someone is there or was just there (Look and Feel, "Lighting
## rules"). Small range, no shadows, a slow flicker. Put it out with `lit`.
## A hunter sees anyone standing in its light (HunterSenses.is_lit).

@export var lit := true:
	set(value):
		lit = value
		if is_node_ready():
			light.visible = lit
			flame.visible = lit
@export var energy := 0.6
@export_range(0.0, 0.5) var flicker := 0.12

var _noise := FastNoiseLite.new()
var _t := randf() * 100.0

@onready var light: OmniLight3D = $Light
@onready var flame: MeshInstance3D = $Flame


func _ready() -> void:
	add_to_group(&"candles")
	_noise.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
	_noise.frequency = 1.0
	light.visible = lit
	flame.visible = lit


func _process(delta: float) -> void:
	if not lit:
		return
	_t += delta * 2.0
	var n := _noise.get_noise_1d(_t)
	light.light_energy = energy * (1.0 + flicker * n)
	flame.scale = Vector3(1.0, 1.0 + flicker * n, 1.0)
