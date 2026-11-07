class_name Stalker
extends Node3D
## The demon in its Glimpses and Stalking phases (design doc, "The demon:
## Slenderman first, men later"): a tall horned figure that is only ever
## still. It never animates in view and only moves while the porter is
## looking away; it can't move at all while his lantern light touches it.
## The rooks, rats and the cat go quiet first (the "room_tone" group).
##
## It stands at "stalk_point" markers. Glimpses: somewhere in `first_range`,
## gone when you look away and back. Stalking: each appearance at most
## `closer` times the last distance; when that would be under
## `final_distance` it appears right behind you instead (with full silence),
## and the moment you turn your back on that one and are out of your own
## lantern's light, `hunter` takes over and the chase begins.
##
## On its own it waits while any hunter is awake nearby or busy, so the two
## are never seen together, and `rearm` starts the sequence again once a
## chase is over. A `scripted` stalker only appears when a night's beat calls
## appear_from() or appear_behind() (night 3's round), and appear_ahead()
## puts it in a doorway the porter is running for.

signal appeared(at: Vector3)
signal vanished
signal handed_over

enum Phase { GLIMPSES, STALKING }
enum Step { WAIT, QUIET, SHOWN }

@export var phase := Phase.STALKING
@export var active := true
## Seconds between appearances.
@export var interval := Vector2(20.0, 40.0)
## The animals go quiet this long before it appears, s.
@export var quiet_lead := 5.0
## Distance of the first appearance and of every glimpse, m.
@export var first_range := Vector2(14.0, 35.0)
## Each stalking appearance is at most this times the last one's distance.
@export var closer := 0.7
@export var final_distance := 6.0
## How far behind the porter the last appearance stands, m.
@export var behind_distance := 3.5
## Seconds it waits to be seen before it goes anyway.
@export var linger := 40.0
## Seconds after you turn your back on the last appearance before it comes.
@export var turn_grace := 0.4
@export var hunter: Hunter
## Starts again after the hunter's chase ends.
@export var rearm := true
## Appears only when a beat asks (appear_from, appear_behind, appear_ahead).
@export var scripted := false

var step := Step.WAIT
var appearances := 0
var last_distance := 0.0
## Seen during this appearance.
var seen := false
var final := false

var _timer := 0.0
var _point := Vector3.ZERO
var _script_points: Array[Vector3] = []
var _script_behind := false
var _seen_time := 0.0
var _away_time := 0.0
var _shown_time := 0.0
var _player: Player

@onready var figure: DemonCostume = $Figure
@onready var _shape: CollisionShape3D = $Body/Shape


func _ready() -> void:
	add_to_group(&"stalkers")
	($Body as StaticBody3D).collision_layer = Layers.CAPSULE
	($Body as StaticBody3D).collision_mask = 0
	_hide()
	_timer = randf_range(interval.x, interval.y) * 0.5
	if scripted:
		active = false
	if hunter and rearm:
		hunter.state_changed.connect(_on_hunter_state)


func _physics_process(delta: float) -> void:
	if not active:
		return
	if _player == null or not is_instance_valid(_player):
		_player = get_tree().get_first_node_in_group(&"player") as Player
		if _player == null:
			return
	match step:
		Step.WAIT:
			_timer -= delta
			if _timer <= 0.0:
				_timer = 2.0
				if (scripted or _threats_clear()) and _pick():
					step = Step.QUIET
					_timer = quiet_lead
					_set_quiet(true)
		Step.QUIET:
			_timer -= delta
			if _timer <= 0.0:
				if _can_place(_point) or _pick():
					_show_at(_point)
				else:
					_timer = 0.5
		Step.SHOWN:
			_watch(delta)


## Shows it now if it can (a debug key, scripted beats).
func appear_now() -> void:
	active = true
	if step != Step.SHOWN and _player and _pick():
		_set_quiet(true)
		_show_at(_point)


## Appears, after the animals go quiet, at the first of `points` that is out
## of view and in plain sight once he turns.
func appear_from(points: Array[Vector3]) -> void:
	_script_points = points
	_script_behind = false
	_begin_scripted()


## Appears right behind him, in full silence: the last appearance.
func appear_behind() -> void:
	_script_points = []
	_script_behind = true
	_begin_scripted()


## Stands at `at` now if he can't see it there (behind a shut door or round
## a corner): ahead of him while he runs.
func appear_ahead(at: Vector3) -> bool:
	if _player == null:
		_player = get_tree().get_first_node_in_group(&"player") as Player
	if _player == null or step == Step.SHOWN:
		return false
	if ViewCheck.on_screen(_player.camera, _points_at(at)):
		return false
	active = true
	final = false
	_show_at(at)
	return true


func _begin_scripted() -> void:
	active = true
	if step == Step.SHOWN:
		_hide()
	step = Step.WAIT
	_timer = 0.0


## Back to the start of the sequence (after a capture).
func reset() -> void:
	_hide()
	step = Step.WAIT
	final = false
	last_distance = 0.0
	appearances = 0
	active = not scripted
	_timer = randf_range(interval.x, interval.y)
	_set_quiet(false)


func _watch(delta: float) -> void:
	_shown_time += delta
	var on_screen := ViewCheck.on_screen(_player.camera, _points())
	if on_screen:
		_seen_time += delta
		_away_time = 0.0
		if _seen_time >= 0.25:
			seen = true
	else:
		_away_time += delta
	if _lit():
		return
	if final:
		if seen and _away_time >= turn_grace:
			_hand_over()
		return
	if (seen and _away_time >= 0.4) or (_shown_time >= linger and not on_screen):
		_vanish()


func _hand_over() -> void:
	var xform := global_transform
	_hide()
	active = false
	step = Step.WAIT
	_set_quiet(false)
	if hunter:
		hunter.take_over(xform)
	handed_over.emit()


func _show_at(p: Vector3) -> void:
	global_position = p
	var to := _player.global_position - p
	rotation = Vector3(0.0, atan2(-to.x, -to.z), 0.0)
	visible = true
	_shape.disabled = false
	step = Step.SHOWN
	seen = false
	_seen_time = 0.0
	_away_time = 0.0
	_shown_time = 0.0
	appearances += 1
	last_distance = Vector2(to.x, to.z).length()
	appeared.emit(p)


func _vanish() -> void:
	_hide()
	step = Step.WAIT
	_timer = randf_range(interval.x, interval.y)
	if scripted:
		active = false
	vanished.emit()
	get_tree().create_timer(quiet_lead).timeout.connect(func() -> void:
		if step == Step.WAIT:
			_set_quiet(false))


func _hide() -> void:
	visible = false
	if _shape:
		_shape.disabled = true


## Chooses where to appear next; false if nowhere fits now.
func _pick() -> bool:
	if scripted:
		return _pick_scripted()
	var lo := first_range.x
	var hi := first_range.y
	final = false
	if phase == Phase.STALKING and last_distance > 0.0:
		hi = last_distance * closer
		lo = hi * 0.5
		if hi < final_distance:
			final = true
			return _pick_behind()
	var best: Array[Vector3] = []
	for marker: Node3D in get_tree().get_nodes_in_group(&"stalk_point"):
		var p := marker.global_position
		var d := Vector2(p.x - _player.global_position.x, p.z - _player.global_position.z).length()
		if d >= lo and d <= hi and _can_place(p):
			best.append(p)
	if best.is_empty():
		return false
	# Furthest first, so it closes in by steps; a little chance among the top three.
	var from := _player.global_position
	best.sort_custom(func(a: Vector3, b: Vector3) -> bool: return a.distance_to(from) > b.distance_to(from))
	_point = best[randi() % mini(3, best.size())]
	return true


func _pick_scripted() -> bool:
	final = _script_behind
	if _script_behind:
		return _pick_behind()
	for p in _script_points:
		if _can_place(p):
			_point = p
			return true
	return false


## A spot on the navmesh right behind where the porter is looking.
func _pick_behind() -> bool:
	var back := _player.camera.global_basis.z
	back = Vector3(back.x, 0.0, back.z).normalized()
	var map := get_world_3d().navigation_map
	for angle in [0.0, 0.5, -0.5, 1.0, -1.0]:
		var want := _player.global_position + back.rotated(Vector3.UP, angle) * behind_distance
		var p := NavigationServer3D.map_get_closest_point(map, want)
		if p.distance_to(want) < 0.8 and absf(p.y - _player.global_position.y) < 0.6 and _can_place(p):
			_point = p
			return true
	return false


## Off screen now and in plain sight once he turns. It may arrive in the
## lantern's light (he isn't looking); it can't leave it.
func _can_place(p: Vector3) -> bool:
	var points := _points_at(p)
	if ViewCheck.on_screen(_player.camera, points):
		return false
	return ViewCheck.clear(self, _player.camera.global_position, points[0])


func _points() -> Array[Vector3]:
	return _points_at(global_position)


## Head, chest and hem.
func _points_at(p: Vector3) -> Array[Vector3]:
	return [p + Vector3.UP * 1.7, p + Vector3.UP * 1.1, p + Vector3.UP * 0.2]


func _lit() -> bool:
	return _lit_at(global_position + Vector3.UP * 1.1)


func _lit_at(p: Vector3) -> bool:
	var light := _player.lantern.light
	return light.global_position.distance_to(p) < light.omni_range \
		and ViewCheck.clear(self, light.global_position, p)


## No awake hunter is busy, nearby or in view: never two at once.
func _threats_clear() -> bool:
	for h: Hunter in get_tree().get_nodes_in_group(&"hunters"):
		if h.dormant:
			continue
		if h.state != Hunter.State.PATROL or h.global_position.distance_to(_player.global_position) < 25.0:
			return false
		if ViewCheck.on_screen(_player.camera, [h.global_position + Vector3.UP * 1.5]):
			return false
	return true


func _set_quiet(on: bool) -> void:
	get_tree().call_group(&"room_tone", &"set_quiet", on, on and final)


func _on_hunter_state(s: Hunter.State) -> void:
	if not active and s == Hunter.State.PATROL:
		reset()
