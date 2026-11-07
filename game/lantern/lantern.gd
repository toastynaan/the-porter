class_name Lantern
extends Node3D
## The porter's horn lantern, the game's main light (Look and Feel, "Lighting
## rules"): warm, about 5 m of useful reach, a slow flicker, shadows on.
## Covering it with the cloak drops the reach to about 1 m and hides the
## flame. It gutters in a draught (an open door nearby) and at high Dose:
## the flame flutters and the light dips.

const REACH := 5.0
const COVERED_REACH := 1.0
## An open door within this many metres makes a draught.
const DRAUGHT_RANGE := 2.5
## Dose where the flame starts guttering on its own, and where it is worst.
const GUTTER_DOSE := Vector2(75.0, 100.0)

## Light energy before the flicker.
@export var energy := 1.8
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
## 0..1, how hard the flame is guttering now.
var gutter := 0.0

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
	var target := maxf(_draught(), smoothstep(GUTTER_DOSE.x, GUTTER_DOSE.y, GameState.dose))
	gutter = move_toward(gutter, target, delta * 1.5)
	var n := _noise.get_noise_1d(_t)
	# Guttering: fast flutter that only ever dips the light.
	var flutter := absf(_noise.get_noise_1d(_t * 9.0 + 50.0)) * 2.0 * gutter
	light.light_energy = energy * (1.0 + flicker * n) * (1.0 - 0.6 * minf(flutter, 1.0))
	flame.scale = Vector3(1.0 - 0.3 * flutter, 1.0 + 0.5 * flicker * n - 0.4 * flutter, 1.0)


func set_covered(value: bool) -> void:
	covered = value
	if not is_node_ready():
		return
	if _reach_tween:
		_reach_tween.kill()
	_reach_tween = create_tween()
	_reach_tween.tween_property(light, ^"omni_range", COVERED_REACH if covered else REACH, cover_time)
	flame.visible = not covered and body.visible


## Shows or hides the lantern's own meshes; the light stays.
func set_meshes_visible(value: bool) -> void:
	body.visible = value
	flame.visible = value and not covered


## 0..1 draught from the nearest open door.
func _draught() -> float:
	var wind := 0.0
	for door in get_tree().get_nodes_in_group(&"doors"):
		if door.is_open:
			var d := global_position.distance_to((door as Node3D).global_position + Vector3.UP)
			wind = maxf(wind, 1.0 - d / DRAUGHT_RANGE)
	return wind
