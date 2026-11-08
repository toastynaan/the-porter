class_name Candle
extends Node3D
## A lit candle: someone is there or was just there (Look and Feel, "Lighting
## rules"). Small range, no shadows, a slow flicker. Put it out with `lit`.
## A hunter sees anyone standing in its light (HunterSenses.is_lit). While
## the porter's lantern is out, a lit candle relights it: hold E on it for
## RELIGHT_TIME s (docs/mechanics.md, "The lantern").

const RELIGHT_TIME := 1.5

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
var _area: Area3D
var _holding := false

@onready var light: OmniLight3D = $Light
@onready var flame: MeshInstance3D = $Flame


func _ready() -> void:
	add_to_group(&"candles")
	_noise.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
	_noise.frequency = 1.0
	light.visible = lit
	flame.visible = lit
	_area = Area3D.new()
	_area.collision_layer = 0
	_area.collision_mask = 0
	_area.monitoring = false
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(0.3, 0.4, 0.3)
	shape.shape = box
	shape.position = Vector3(0, 0.15, 0)
	_area.add_child(shape)
	add_child(_area)


## The porter's lantern, if it's out.
func _out_lantern() -> Lantern:
	var p := get_tree().get_first_node_in_group(&"player") as Player
	return p.lantern if p and p.lantern.out else null


## Holding E on a lit candle relights his lantern.
func interact(_by: Node) -> void:
	var lantern := _out_lantern()
	if lantern == null or not lit or _holding:
		return
	_holding = true
	var t := 0.0
	while t < RELIGHT_TIME and (Input.is_action_pressed(&"interact") or has_meta(&"auto")):
		await get_tree().physics_frame
		t += get_physics_process_delta_time()
	_holding = false
	if t >= RELIGHT_TIME:
		lantern.relight()
		Talk.say("", "(The wick takes, and you have light again.)")


func _process(delta: float) -> void:
	_area.collision_layer = Layers.INTERACT if lit and _out_lantern() != null else 0
	if not lit:
		return
	_t += delta * 2.0
	var n := _noise.get_noise_1d(_t)
	light.light_energy = energy * (1.0 + flicker * n)
	flame.scale = Vector3(1.0, 1.0 + flicker * n, 1.0)
