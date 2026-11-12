class_name HungrySaint
extends Node3D
## The Hungry Saint, on night 6 only (design doc, "The Hungry Saint";
## docs/systems/mechanics.md, "Night 6"). The one thing in the game that isn't men
## and the drug. It moves in view, slowly. Doors, locks and darkness don't
## stop it, and it goes through the hidden passages: it always knows roughly
## where the porter is and walks toward him, finding its way again every
## REPATH seconds. Its touch is death. Silence comes before it (the animals
## and the wind stop within SILENCE m) and his lantern dims within DIM m.
## Its strength is the rite's count (Rite):
## - 8 or fewer: a shadow that can't leave the crypt (`home`, `home_radius`);
## - 9: it walks the abbey at 0.9 m/s;
## - 10 or 11: at 1.2 m/s, and it kills any cultist it meets.

signal touched

const FIGURE := preload("res://game/characters/chr_saint.tscn")
const SILENCE := 25.0
const DIM := 8.0
const TOUCH := 1.1
const REPATH := 2.5
const KILL := 1.6

@export var home: Marker3D
@export var home_radius := 10.0
## Set by the count when it wakes (awake()); a test may set them.
var speed := 0.0
var walks := false
var kills := false
var awake := false

var _path := PackedVector3Array()
var _repath := 0.0
var _quiet := false
var _dimmed: Lantern
var _lantern_energy := 0.0


func _ready() -> void:
	add_to_group(&"saint")
	var look := CharacterLook.new()
	look.look = FIGURE
	add_child(look)
	visible = false
	set_physics_process(false)


## It comes: its strength from the count so far.
func wake() -> void:
	var count := GameState.count
	walks = count >= 9
	kills = count >= 10
	speed = 1.2 if kills else (0.9 if walks else 0.7)
	if home:
		global_transform = home.global_transform
	visible = true
	awake = true
	set_physics_process(true)


## Gone (dawn, an ending).
func sleep() -> void:
	awake = false
	visible = false
	set_physics_process(false)
	_set_quiet(false)
	_dim(false)


func _physics_process(delta: float) -> void:
	var p := get_tree().get_first_node_in_group(&"player") as Player
	if p == null:
		return
	var target := p.global_position
	if not walks and home and target.distance_to(home.global_position) > home_radius:
		target = home.global_position
	_repath -= delta
	if _repath <= 0.0 or _path.is_empty():
		_repath = REPATH
		_path = NavigationServer3D.map_get_path(get_world_3d().navigation_map, global_position, target, true)
	_step(delta)
	var d := global_position.distance_to(p.global_position)
	_set_quiet(d < SILENCE)
	_dim(d < DIM)
	# Hiding doesn't help: it knows where he is.
	if d < TOUCH:
		touched.emit()
		set_physics_process(false)
		var flow := get_tree().get_first_node_in_group(&"capture_flow") as CaptureFlow
		if flow:
			flow.die(&"saint", self)
	if kills:
		for h: Hunter in get_tree().get_nodes_in_group(&"hunters"):
			if is_instance_valid(h) and h.global_position.distance_to(global_position) < KILL:
				if h.wearer != &"":
					GameState.set_flag(StringName("died_" + String(h.wearer)))
				h.queue_free()


## Along its path, at its pace; it turns to where it goes.
func _step(delta: float) -> void:
	var left := speed * delta
	while left > 0.0 and not _path.is_empty():
		var to := _path[0] - global_position
		var flat := Vector2(to.x, to.z).length()
		if flat < 0.05:
			_path.remove_at(0)
			continue
		var step := minf(left, flat)
		global_position += to.normalized() * step
		rotation.y = atan2(-to.x, -to.z)
		left -= step


func _set_quiet(on: bool) -> void:
	if on == _quiet:
		return
	_quiet = on
	get_tree().call_group(&"room_tone", &"set_quiet", on)


func _dim(on: bool) -> void:
	if on and _dimmed == null:
		var p := get_tree().get_first_node_in_group(&"player") as Player
		for n in (p.find_children("*", "", true, false) if p else []):
			if n is Lantern:
				_dimmed = n as Lantern
				break
		if _dimmed:
			_lantern_energy = _dimmed.energy
			_dimmed.energy = _lantern_energy * 0.35
	elif not on and _dimmed:
		if is_instance_valid(_dimmed):
			_dimmed.energy = _lantern_energy
		_dimmed = null
