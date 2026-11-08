class_name Hunter
extends CharacterBody3D
## A costumed cultist hunting the porter (design doc, "Suspicion, chases and
## hiding" and its Hunter AI diagram): Patrol, Investigate, Chase, Search,
## Capture.
##
## - Patrol: walks the `patrol_route` markers in order, waiting at each
##   (a marker's "wait" meta, in seconds), humming.
## - Investigate: walks to a noise or a glimpse and looks around.
## - Chase: runs at the porter's speed while he can see him, then to where he
##   last saw (or heard) him. After about 20 s of sprinting he is winded and
##   stops to listen. Reaching the porter is a Capture.
## - Search: from Suspicion 30 (or with `always_search`), checks the 2 hiding
##   spots nearest where he last saw the porter, a spot used twice tonight
##   first. Below 30 he only looks around (design doc, "Thresholds").
##
## He freezes for a moment the first time the porter's lantern light touches
## him (design doc: "they freeze the moment lantern light touches them"). He
## carries a shuttered lantern on his back, so he shows as a dark shape
## against its glow (the doc's sober render: "a lantern behind it").
##
## He opens doors in his way and shuts the ones he opened on patrol behind
## him. A locked door stops him: he tries it and gives up (he has no keys).
## He can't follow through a squeeze. Slower on stairs.
##
## `dormant` hunters stand hidden and still until take_over(), chase() or
## alert(); stand_still() shows one where he is, waiting for his cue.

signal state_changed(state: State)
signal caught(player: Player)
signal checking(spot: HidingSpot)

enum State { PATROL, INVESTIGATE, CHASE, SEARCH, CAPTURE }

## m/s (M2 report defaults; chase = the porter's run).
const PATROL_SPEED := 1.2
const INVESTIGATE_SPEED := 1.4
const SEARCH_SPEED := 2.0
const CHASE_SPEED := 4.0
const STAIRS_FACTOR := 0.7
## Seconds of sprinting before he is winded, and how long he stops.
const SPRINT_LIMIT := 20.0
const WINDED_TIME := 4.0
## How close he must get to take hold of the porter, m.
const REACH := 1.0
## After losing sight he still knows where the porter went for this long.
const TRACK_TIME := 1.5
const LOOK_TIME := 4.0
const CHECK_TIME := 2.5
const SPOTS_TO_CHECK := 2
## Hiding spots further than this from where he lost you aren't searched, m.
const SEARCH_RADIUS := 25.0
const SEARCH_SUSPICION := 30
const PATROL_WAIT := 3.0
## Seconds he stands at a locked door, trying it and listening.
const LOCKED_WAIT := 3.0
const ACCEL := 14.0
const GRAVITY := 9.8
## Doors closer than this are his own doing; he ignores their noise.
const OWN_DOOR_RANGE := 2.5
## Seconds he stands still when the porter's light first falls on him.
const FREEZE_TIME := 0.5

## Node whose Marker3D children are the patrol, in order.
@export var patrol_route: Node3D
## The night's designed chase searches whatever the Suspicion.
@export var always_search := false
@export var dormant := false
## How he kills the porter when he takes hold of him (CaptureFlow.die):
## "cord" or "blade".
@export var weapon := &"cord"
## Who is in the costume (People: "osric", "ranulf"...): his voice, and
## his face if the mask comes off.
@export var wearer := &""

## The mask came off (night 4): his face shows.
var unmasked := false

## Shown but still, senses or not, until chase() or alert().
var waiting := false

var state := State.PATROL
var last_seen := Vector3.ZERO
var sprint_time := 0.0
## Seconds left standing winded.
var winded := 0.0

var _home: Transform3D
var _start_dormant := false
var _patrol_index := 0
var _wait := 0.0
var _lost_time := 0.0
var _look_time := 0.0
var _look_yaw := 0.0
var _target := Vector3.ZERO
var _sent_target := Vector3.INF
var _spots: Array[HidingSpot] = []
var _noise_spot: HidingSpot
## The noise from _noise_spot was a person (breath, a gasp), not just the spot.
var _noise_person := false
var _checking: HidingSpot
var _check_time := 0.0
var _door_wait := 0.0
var _opened: Door
var _locked_door: Door
var _locked_time := 0.0
var _warmup := 0.5
var _freeze := 0.0
var _was_lit := false
var _player: Player

@onready var agent: NavigationAgent3D = $Agent
@onready var senses: HunterSenses = $Senses
@onready var costume: DemonCostume = $Costume


func _ready() -> void:
	add_to_group(&"hunters")
	collision_layer = Layers.CAPSULE
	collision_mask = Layers.MASK_HUNTER
	_home = global_transform
	_start_dormant = dormant
	senses.heard.connect(_on_heard)
	_set_dormant(dormant)


func _physics_process(delta: float) -> void:
	if dormant or waiting:
		return
	if _player == null or not is_instance_valid(_player):
		_player = get_tree().get_first_node_in_group(&"player") as Player
	if _warmup > 0.0:
		_warmup -= delta
		return
	var lit := _in_porter_light()
	if lit and not _was_lit:
		_freeze = FREEZE_TIME
	_was_lit = lit
	if state != State.CHASE and state != State.CAPTURE and senses.sees_player:
		_start_chase()
	elif state == State.PATROL and senses.glimpsed and senses.awareness >= 0.5:
		_investigate_at(_player.global_position, null)
	var speed := 0.0
	match state:
		State.PATROL:
			speed = _patrol(delta)
		State.INVESTIGATE:
			speed = _investigate(delta)
		State.CHASE:
			speed = _chase(delta)
		State.SEARCH:
			speed = _search(delta)
	_move(delta, speed)


## Wakes a dormant hunter at `xform` (where the demon stood) and sets him on
## the porter.
func take_over(xform: Transform3D) -> void:
	waiting = false
	_set_dormant(false)
	var map := agent.get_navigation_map()
	var at := NavigationServer3D.map_get_closest_point(map, xform.origin)
	global_transform = Transform3D(xform.basis, at)
	_warmup = 0.0
	_start_chase()


## Sets him on the porter from wherever he is (debug key, scripted beats).
func chase() -> void:
	waiting = false
	_set_dormant(false)
	_warmup = 0.0
	_start_chase()


## Sends him to look at `at` (a scripted noise, the bell).
func alert(at: Vector3) -> void:
	waiting = false
	_set_dormant(false)
	if state == State.PATROL or state == State.INVESTIGATE:
		_investigate_at(at, null)


## Shows him where he stands, still, until his cue (chase or alert).
func stand_still() -> void:
	_set_dormant(false)
	waiting = true
	velocity = Vector3.ZERO


## The mask comes off in the chase (night 4: it's Osric). It falls at his
## feet, where the porter can take it, and his own face shows.
func unmask() -> Node3D:
	if unmasked:
		return null
	unmasked = true
	costume.show_face(_face_colour())
	var mask := Pickup.new()
	mask.id = StringName("mask_" + String(wearer))
	mask.item = &"mask"
	var mesh := MeshInstance3D.new()
	var box := BoxMesh.new()
	box.size = Vector3(0.18, 0.04, 0.26)
	mesh.mesh = box
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color("#D8C9A3")
	mesh.material_override = mat
	mask.add_child(mesh)
	get_parent().add_child(mask)
	mask.global_position = global_position + global_basis.z * 0.6 + Vector3.UP * 0.02
	GameState.set_flag(StringName("unmasked_" + String(wearer)))
	return mask


func _face_colour() -> Color:
	match wearer:
		&"osric":
			return Color(0.75, 0.45, 0.38)
		&"ranulf":
			return Color(0.78, 0.74, 0.68)
	return Color(0.6, 0.48, 0.4)


## Back to where he started, patrolling (after a capture).
func reset() -> void:
	waiting = false
	global_transform = _home
	velocity = Vector3.ZERO
	sprint_time = 0.0
	winded = 0.0
	_patrol_index = 0
	_spots.clear()
	_checking = null
	_locked_door = null
	_door_wait = 0.0
	_freeze = 0.0
	_was_lit = false
	_opened = null
	_set_state(State.PATROL)
	senses.forget()
	_set_dormant(_start_dormant)
	_warmup = 0.5


func _set_dormant(value: bool) -> void:
	dormant = value
	visible = not value
	$Collision.disabled = value
	senses.process_mode = Node.PROCESS_MODE_DISABLED if value else Node.PROCESS_MODE_INHERIT


func _set_state(s: State) -> void:
	if s == state:
		return
	if state == State.CHASE:
		senses.focused = false
		senses.listening = false
		winded = 0.0
	state = s
	_look_time = 0.0
	_wait = 0.0
	if s == State.CHASE:
		senses.focused = true
		sprint_time = 0.0
		_lost_time = 0.0
	state_changed.emit(state)


func _start_chase() -> void:
	_set_state(State.CHASE)
	if _player:
		last_seen = _player.global_position


func _may_search() -> bool:
	return always_search or GameState.suspicion >= SEARCH_SUSPICION


# --- States: each returns the speed to move at toward _target. ---

func _patrol(delta: float) -> float:
	var points := _patrol_points()
	if points.is_empty():
		_target = global_position
		return 0.0
	_patrol_index %= points.size()
	var p := points[_patrol_index]
	_target = p.global_position
	if _locked_door or _arrived():
		_locked_door = null
		_wait += delta
		if _wait >= float(p.get_meta(&"wait", PATROL_WAIT)):
			_wait = 0.0
			_patrol_index = (_patrol_index + 1) % points.size()
		return 0.0
	return PATROL_SPEED


func _investigate(delta: float) -> float:
	if not (_locked_door or _arrived()):
		return INVESTIGATE_SPEED
	if _locked_door:
		if _try_locked_door(delta):
			_locked_door = null
			_resume_patrol()
		return 0.0
	if _look_around(delta):
		if _noise_spot and (_noise_person or _may_search()):
			_spots = [_noise_spot]
			_noise_spot = null
			_set_state(State.SEARCH)
		else:
			_resume_patrol()
	return 0.0


func _chase(delta: float) -> float:
	if _player == null:
		return 0.0
	if senses.sees_player:
		last_seen = _player.global_position
		_lost_time = 0.0
	else:
		_lost_time += delta
		if _lost_time < TRACK_TIME:
			last_seen = _player.global_position
	_target = last_seen
	if _can_grab():
		_capture()
		return 0.0
	if winded > 0.0:
		winded -= delta
		senses.listening = winded > 0.0
		if winded <= 0.0:
			sprint_time = 0.0
		_face(last_seen, delta)
		return 0.0
	if _locked_door:
		if _try_locked_door(delta):
			_lose_track()
		return 0.0
	if _lost_time >= TRACK_TIME and _arrived():
		_lose_track()
		return 0.0
	sprint_time += delta
	if sprint_time >= SPRINT_LIMIT:
		winded = WINDED_TIME
		senses.listening = true
	return CHASE_SPEED


func _search(delta: float) -> float:
	if _checking:
		_face(_checking.view.global_position, delta)
		_check_time += delta
		if _check_time >= CHECK_TIME:
			var spot := _checking
			_checking = null
			_spots.erase(spot)
			if spot.check():
				_player.leave_hiding(true)
				_capture()
		return 0.0
	if _spots.is_empty():
		if _look_around(delta):
			_resume_patrol()
		return 0.0
	_target = _spots[0].check_point()
	if _locked_door:
		_locked_door = null
		_spots.pop_front()
		return 0.0
	if _arrived():
		_checking = _spots[0]
		_check_time = 0.0
		checking.emit(_checking)
		return 0.0
	return SEARCH_SPEED


func _capture() -> void:
	_set_state(State.CAPTURE)
	velocity = Vector3.ZERO
	caught.emit(_player)
	get_tree().call_group(&"capture_flow", &"on_captured", self, _player)


# --- Helpers ---

## Lost the porter: search where he was, or just look around there.
func _lose_track() -> void:
	_locked_door = null
	var heard_spot := _noise_spot
	_noise_spot = null
	if _may_search():
		_spots = search_list(last_seen)
	else:
		_spots.clear()
	if heard_spot and (_noise_person or _may_search()):
		_spots.erase(heard_spot)
		_spots.push_front(heard_spot)
	# In the snow he follows the porter's freshest prints near where he lost him.
	var snow := get_tree().get_first_node_in_group(&"footprints") as Footprints
	if snow and Footprints.active(get_tree()):
		var trail := snow.freshest(&"porter", last_seen, 12.0)
		if trail != Vector3.INF and trail.distance_to(last_seen) > 1.0:
			_spots.clear()
			_investigate_at(trail, null)
			return
	if _spots.is_empty():
		_investigate_at(last_seen, null)
	else:
		_set_state(State.SEARCH)


func _investigate_at(at: Vector3, spot: HidingSpot, person := false) -> void:
	_target = at
	_noise_spot = spot
	_noise_person = person
	_locked_door = null
	_set_state(State.INVESTIGATE)
	_look_time = 0.0


func _resume_patrol() -> void:
	var points := _patrol_points()
	var best := INF
	for i in points.size():
		var d := global_position.distance_to(points[i].global_position)
		if d < best:
			best = d
			_patrol_index = i
	_set_state(State.PATROL)


## The hiding spots he would check after losing the porter at `at`: those
## within SEARCH_RADIUS he can reach, a spot used twice tonight first, then
## the nearest, SPOTS_TO_CHECK of them.
func search_list(at: Vector3) -> Array[HidingSpot]:
	var scored: Array = []
	for spot: HidingSpot in get_tree().get_nodes_in_group(&"hiding_spots"):
		var offset := spot.check_point() - at
		var d := Vector3(offset.x, offset.y * 3.0, offset.z).length()
		if d <= SEARCH_RADIUS and _reachable(spot.check_point()):
			scored.append([0 if spot.uses >= 2 else 1, d, spot])
	scored.sort_custom(func(a: Array, b: Array) -> bool: return a[0] < b[0] or (a[0] == b[0] and a[1] < b[1]))
	var out: Array[HidingSpot] = []
	for s in scored.slice(0, SPOTS_TO_CHECK):
		out.append(s[2])
	return out


## Whether he can walk to `to`: a path ends there and no locked door is on it.
func _reachable(to: Vector3) -> bool:
	var map := agent.get_navigation_map()
	var path := NavigationServer3D.map_get_path(map, global_position, to, true)
	if path.is_empty() or path[-1].distance_to(to) > 1.0:
		return false
	for door: Door in get_tree().get_nodes_in_group(&"doors"):
		if door.locked:
			for i in range(1, path.size()):
				if door.crosses(path[i - 1] + Vector3.UP, path[i] + Vector3.UP):
					return false
	return true


## The porter's lantern light reaches his chest.
func _in_porter_light() -> bool:
	if _player == null:
		return false
	var light := _player.lantern.light
	var chest := global_position + Vector3.UP * 1.2
	return light.global_position.distance_to(chest) < light.omni_range \
		and ViewCheck.clear(self, light.global_position, chest)


func _can_grab() -> bool:
	if _player.hiding:
		return false
	var to := _player.global_position - global_position
	return Vector2(to.x, to.z).length() < REACH and absf(to.y) < 1.2 \
		and ViewCheck.clear(self, senses.global_position, _player.camera.global_position)


## At a locked door: tries it, waits listening. True once he gives up.
func _try_locked_door(delta: float) -> bool:
	if _locked_time == 0.0:
		_locked_door.rattle()
	_locked_time += delta
	senses.listening = true
	if _locked_time >= LOCKED_WAIT:
		_locked_time = 0.0
		senses.listening = false
		return true
	return false


## Turns slowly left and right; true when he has looked long enough.
func _look_around(delta: float) -> bool:
	if _look_time == 0.0:
		_look_yaw = rotation.y
	_look_time += delta
	rotation.y = _look_yaw + 1.2 * sin(_look_time * TAU / LOOK_TIME)
	return _look_time >= LOOK_TIME


func _face(at: Vector3, delta: float) -> void:
	var to := at - global_position
	if Vector2(to.x, to.z).length() > 0.1:
		rotation.y = lerp_angle(rotation.y, atan2(-to.x, -to.z), 1.0 - exp(-8.0 * delta))


func _arrived() -> bool:
	_sync_target()
	agent.get_next_path_position()
	return agent.is_navigation_finished()


func _sync_target() -> void:
	if _target.distance_to(_sent_target) > 0.3:
		_sent_target = _target
		agent.target_position = _target


func _patrol_points() -> Array[Node3D]:
	var out: Array[Node3D] = []
	if patrol_route:
		for child in patrol_route.get_children():
			if child is Marker3D:
				out.append(child)
	return out


func _move(delta: float, speed: float) -> void:
	_sync_target()
	var flat := Vector3.ZERO
	if _freeze > 0.0:
		_freeze -= delta
	elif _door_wait > 0.0:
		_door_wait -= delta
	elif speed > 0.0 and not agent.is_navigation_finished():
		var next := agent.get_next_path_position()
		var to := next - global_position
		to.y = 0.0
		if to.length() > 0.05:
			var dir := to.normalized()
			if not _handle_door(dir):
				if is_on_floor() and get_floor_normal().y < cos(deg_to_rad(12.0)):
					speed *= STAIRS_FACTOR
				flat = dir * speed
	var vel := Vector3(velocity.x, 0.0, velocity.z).move_toward(flat, ACCEL * delta)
	velocity.x = vel.x
	velocity.z = vel.z
	velocity.y = 0.0 if is_on_floor() else velocity.y - GRAVITY * delta
	move_and_slide()
	if flat.length() > 0.1:
		rotation.y = lerp_angle(rotation.y, atan2(-flat.x, -flat.z), 1.0 - exp(-10.0 * delta))
	_shut_behind()
	_duck()


## Opens a shut door ahead; a locked one stops him. True if he must stop.
func _handle_door(dir: Vector3) -> bool:
	var from := global_position + Vector3.UP
	var ahead := from + dir * 1.2
	for door: Door in get_tree().get_nodes_in_group(&"doors"):
		if door.is_open or door.global_position.distance_to(global_position) > 2.0:
			continue
		if not door.crosses(from, ahead):
			continue
		if door.locked:
			if _locked_door != door:
				_locked_door = door
				_locked_time = 0.0
			return true
		door.set_open(true)
		_door_wait = door.open_time
		if state == State.PATROL:
			_opened = door
		return true
	return false


func _shut_behind() -> void:
	if _opened and state == State.PATROL and _opened.global_position.distance_to(global_position) > 2.0:
		_opened.set_open(false)
		_opened = null


## The headdress is taller than a doorway: he stoops under lintels.
func _duck() -> void:
	var near := 0.0
	for door: Door in get_tree().get_nodes_in_group(&"doors"):
		var d := door.global_position.distance_to(global_position)
		if d < 1.6:
			near = maxf(near, 1.0 - d / 1.6)
	var k := smoothstep(0.0, 0.5, near)
	costume.position.y = lerpf(costume.position.y, -0.35 * k, 0.2)
	costume.rotation.x = lerpf(costume.rotation.x, -0.35 * k, 0.2)


## A breath or a gasp from inside a hiding spot gives that spot away, at
## any Suspicion; a spot creaking only makes it worth a look.
func _on_heard(at: Vector3, source: Node) -> void:
	if source is Door and (source as Door).global_position.distance_to(global_position) < OWN_DOOR_RANGE:
		return
	var person := _player != null and source == _player
	var spot := source as HidingSpot
	if person and _player.hiding:
		spot = _player.hiding
	match state:
		State.CHASE:
			if spot:
				_noise_spot = spot
				_noise_person = person
			elif person:
				last_seen = at
				_lost_time = minf(_lost_time, TRACK_TIME * 0.5)
		State.SEARCH:
			if spot:
				if spot != _checking and not _spots.has(spot):
					_spots.push_front(spot)
			elif person and _checking == null:
				_investigate_at(at, null)
		State.PATROL, State.INVESTIGATE:
			_investigate_at(at, spot, person)
