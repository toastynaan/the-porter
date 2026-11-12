class_name Lantern
extends Node3D
## The porter's horn lantern, the game's main light (Look and Feel, "Lighting
## rules"): warm, about 5 m of useful reach, a slow flicker, shadows on.
## Covering it with the cloak drops the reach to about 1 m and hides the
## flame. It gutters in a draught (an open door nearby), at high Dose and
## while he stares at the demon: the flame flutters and the light dips.
## Wind can put it out, but only at set moments (Gust, never in a chase):
## the flame gutters for GUST_WARNING s and, unless he covers it in time,
## goes out. Out, it's dark but for others' lights until he relights it at a
## lit candle or lamp (hold E, Candle). From Dose 25 the flame bends toward things (design doc, "Effect tiers"):
## the nearest thing that shouldn't be there (group "uncanny": the demon, a
## body, the dead in the choir) within BEND_RANGE.

const REACH := 5.0
const COVERED_REACH := 1.0
## An open door within this many metres makes a draught.
const DRAUGHT_RANGE := 2.5
## Dose where the flame starts guttering on its own, and where it is worst.
const GUTTER_DOSE := Vector2(75.0, 100.0)
## Seconds the flame gutters in a gust before it goes out.
const GUST_WARNING := 1.5
## Dose where the flame starts bending toward things, and where it bends most;
## how far it looks, m; how far it leans, radians.
const BEND_DOSE := Vector2(25.0, 60.0)
const BEND_RANGE := 9.0
const BEND_MAX := 0.6

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
## 0..1 from the stare meter.
var stare := 0.0
## How far the flame leans now (x and z, radians).
var bent := Vector3.ZERO
## Blown out: no light until relit.
var out := false
## Seconds left of a gust's guttering.
var gusting := 0.0

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
	if gusting > 0.0:
		gusting -= delta
		if gusting <= 0.0 and not covered:
			blow_out()
	var target := maxf(maxf(maxf(_draught(), stare), smoothstep(GUTTER_DOSE.x, GUTTER_DOSE.y, GameState.dose)), 1.0 if gusting > 0.0 else 0.0)
	gutter = move_toward(gutter, target, delta * 1.5)
	var n := _noise.get_noise_1d(_t)
	# Guttering: fast flutter that only ever dips the light.
	var flutter := absf(_noise.get_noise_1d(_t * 9.0 + 50.0)) * 2.0 * gutter
	light.light_energy = energy * (1.0 + flicker * n) * (1.0 - 0.6 * minf(flutter, 1.0))
	flame.scale = Vector3(1.0 - 0.3 * flutter, 1.0 + 0.5 * flicker * n - 0.4 * flutter, 1.0)
	_bend(delta)


## Leans the flame toward the nearest uncanny thing, drugged.
func _bend(delta: float) -> void:
	var k := smoothstep(BEND_DOSE.x, BEND_DOSE.y, GameState.dose)
	var lean := Vector3.ZERO
	if k > 0.0:
		var best := BEND_RANGE
		for n: Node in get_tree().get_nodes_in_group(&"uncanny"):
			var t := n as Node3D
			if t and t.is_visible_in_tree():
				var d := t.global_position.distance_to(global_position)
				if d < best:
					best = d
					lean = (t.global_position - global_position)
	var target := Vector3.ZERO
	if lean != Vector3.ZERO:
		var local := flame.get_parent_node_3d().global_basis.inverse() * lean.normalized()
		target = Vector3(-local.z, 0.0, local.x) * BEND_MAX * k
	bent = bent.lerp(target, 1.0 - exp(-3.0 * delta))
	flame.rotation = Vector3(bent.x, 0.0, -bent.z)


## A gust: the flame gutters, and goes out unless he covers it in time.
func gust() -> void:
	if out or gusting > 0.0:
		return
	gusting = GUST_WARNING


func blow_out() -> void:
	out = true
	gusting = 0.0
	light.visible = false
	flame.visible = false


func relight() -> void:
	out = false
	light.visible = true
	flame.visible = not covered and body.visible


func set_covered(value: bool) -> void:
	covered = value
	if not is_node_ready():
		return
	if _reach_tween:
		_reach_tween.kill()
	_reach_tween = create_tween()
	_reach_tween.tween_property(light, ^"omni_range", COVERED_REACH if covered else REACH, cover_time)
	flame.visible = not covered and body.visible and not out


## Shows or hides the lantern's own meshes; the light stays.
func set_meshes_visible(value: bool) -> void:
	body.visible = value
	flame.visible = value and not covered and not out


## 0..1 draught from the nearest open door.
func _draught() -> float:
	var wind := 0.0
	for door in get_tree().get_nodes_in_group(&"doors"):
		if door.is_open:
			var d := global_position.distance_to((door as Node3D).global_position + Vector3.UP)
			wind = maxf(wind, 1.0 - d / DRAUGHT_RANGE)
	return wind
