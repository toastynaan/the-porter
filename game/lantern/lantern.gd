class_name Lantern
extends Node3D
## The porter's horn lantern, the game's main light (Look and Feel, "Lighting
## rules"): warm, about 5 m of useful reach, a slow flicker, shadows on.
## Covering it with the cloak drops the reach to about 1 m and hides the
## flame. Guttering in wind and at high Dose comes with the player (M2).

const REACH := 5.0
const COVERED_REACH := 1.0

## Light energy before the flicker.
@export var energy := 1.0
## Depth of the slow flicker, as a fraction of the energy.
@export_range(0.0, 0.5) var flicker := 0.08
## How fast the flicker wanders.
@export var flicker_speed := 1.5
## Seconds to cover or uncover.
@export var cover_time := 0.35
## Holds the flicker still (review renders).
@export var freeze_flicker := false

var covered := false:
	set = set_covered

var _noise := FastNoiseLite.new()
var _t := 0.0
var _reach_tween: Tween

@onready var light: OmniLight3D = $Light
@onready var flame: MeshInstance3D = $Flame
@onready var body: Node3D = $Body


func _ready() -> void:
	_noise.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
	_noise.frequency = 1.0
	light.omni_range = COVERED_REACH if covered else REACH
	flame.visible = not covered


func _process(delta: float) -> void:
	if not freeze_flicker:
		_t += delta * flicker_speed
	var n := _noise.get_noise_1d(_t)
	light.light_energy = energy * (1.0 + flicker * n)
	flame.scale = Vector3.ONE * (1.0 + 0.5 * flicker * n)


func set_covered(value: bool) -> void:
	covered = value
	if not is_node_ready():
		return
	if _reach_tween:
		_reach_tween.kill()
	_reach_tween = create_tween()
	_reach_tween.tween_property(light, ^"omni_range", COVERED_REACH if covered else REACH, cover_time)
	flame.visible = not covered


## Shows or hides the lantern's own meshes; the light stays.
func set_meshes_visible(value: bool) -> void:
	body.visible = value
	flame.visible = value and not covered
