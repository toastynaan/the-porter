extends Node
## Plays one scripted chase in the greybox for review (tools/chase_capture.sh
## records it with Movie Maker). At Dose 60 the porter walks up the west
## cloister walk, runs from the hunter through the refectory and kitchen,
## looks back from the bakehouse door, and makes for the oven. Two takes
## (`-- --take=<name>`):
##   caught  the hunter stands in the dark with his back turned; he hears the
##           porter, turns into the lantern light, and the porter bolts. The
##           hunter is on him at the bakehouse door: he wakes in the infirmary.
##   escape  the hunter sees the lantern from 17 m down the walk. The porter
##           reaches the oven, holds his breath while the hunter checks it,
##           and he moves on (the oven's chance is forced to 0; 30% in play).
## Night 3's designed chase searches whatever the Suspicion. The doors on the
## route are left open; the demon is off.

## take: [porter start, hunter position, hunter yaw, bolt when the hunter
## starts to turn (else once he gives chase)]
const TAKES := {
	"caught": [Vector3(-10, 0.05, -11), Vector3(-10, 0.05, -21), 0.0, true],
	"escape": [Vector3(-10, 0.05, -7), Vector3(-10, 0.05, -26), PI, false],
}
## The run: round the cloister walk, through the refectory and the kitchen.
const ROUTE: Array[Vector3] = [Vector3(-10, 0.05, -5.5), Vector3(-2, 0.05, -5.0), Vector3(-2, 0.05, -3.0),
	Vector3(-9, 0.05, -3.0), Vector3(-11.3, 0.05, -2.0), Vector3(-13.2, 0.05, -1.6), Vector3(-17.6, 0.05, 0.5),
	Vector3(-18, 0.05, 3.2), Vector3(-18, 0.05, 4.8), Vector3(-16.5, 0.05, 6.2)]
const DOSE := 60.0
const TURN_RATE := 8.0
## How far ahead on the path the porter steers for, m.
const LOOKAHEAD := 1.4

var _player: Player
var _hunter: Hunter
var _map: RID


func _ready() -> void:
	var take: Array = TAKES["caught"]
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--take="):
			take = TAKES[arg.trim_prefix("--take=")]
	var main: Node = load("res://game/render/main.tscn").instantiate()
	add_child(main)
	await get_tree().physics_frame
	for s: Stalker in get_tree().get_nodes_in_group(&"stalkers"):
		s.queue_free()
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	_player = get_tree().get_first_node_in_group(&"player")
	_hunter = get_tree().get_first_node_in_group(&"hunters")
	_map = _player.get_world_3d().navigation_map
	for door: Door in get_tree().get_nodes_in_group(&"doors"):
		if door.name in ["RefectoryN0Door_02", "RefectoryW0Door_00", "KitchenS0Door_00"]:
			door.set_open(true, true)
	GameState.snap_dose(DOSE)
	_player.place(take[0], 0.0)
	_player.head.rotation.x = deg_to_rad(-3.0)
	var route := _hunter.patrol_route
	_hunter.patrol_route = null
	_hunter.always_search = true
	_hunter.global_transform = Transform3D(Basis(Vector3.UP, take[2]), take[1])
	var oven := _spot("Oven")
	oven.check_chance = 0.0
	for i in 20:
		await get_tree().physics_frame

	# Walk up the walk until he is seen, and a moment more.
	_player.use_input_override = true
	_player.input_override = Vector2(0, 1)
	var bolt_early: bool = take[3]
	if bolt_early:
		await _until(func() -> bool: return _hunter.state != Hunter.State.PATROL, 12.0)
	else:
		await _until(func() -> bool: return _hunter.state == Hunter.State.CHASE, 12.0)
	_hunter.patrol_route = route
	# Turn and run for the oven, looking back once in the refectory.
	_player.input_override = Vector2.ZERO
	await _turn_to(PI, 0.25)
	_look_back_at(Vector3(-18, 0.05, 2.6), 1.3)
	_player.run_override = true
	var run := ROUTE.duplicate()
	run.append(oven.exit.global_position)
	await _run_along(run)
	_player.run_override = false
	_player.input_override = Vector2.ZERO
	await _turn_to(deg_to_rad(90.0), 0.3)
	_player.hide_in(oven)
	await _seconds(0.8)
	# Hold the breath while he is close; let it go once he has gone.
	await _until(func() -> bool: return _hunter.global_position.distance_to(oven.view.global_position) < 7.0, 10.0)
	Input.action_press(&"hold_breath")
	var gone := func() -> bool:
		return _hunter.state == Hunter.State.PATROL or _hunter.global_position.distance_to(oven.view.global_position) > 7.0
	await _until(gone, 11.0)
	await _seconds(1.0)
	Input.action_release(&"hold_breath")
	await _seconds(5.0)
	print("CHASE DONE: hunter %s, caught %d" % [Hunter.State.keys()[_hunter.state], GameState.captures])
	get_tree().quit()


## Runs along navmesh paths through `points`, steering for a point a little
## ahead on the line (smooth corners, like a player); the view follows.
func _run_along(points: Array[Vector3]) -> void:
	var line := PackedVector3Array([_player.global_position])
	var from := _player.global_position
	for p in points:
		var seg := NavigationServer3D.map_get_path(_map, from, p, true)
		for k in range(1, seg.size()):
			if seg[k].distance_to(line[-1]) > 0.05:
				line.append(seg[k])
		from = p
	var i := 0
	var t := 0.0
	while t < 25.0 and not _player.controls_locked:
		var pos := _player.global_position
		# Move on to the next segment once past this one's end.
		while i < line.size() - 2 and _flat(pos - line[i + 1]).dot(_flat(line[i + 1] - line[i])) > 0.0:
			i += 1
		if _flat(line[-1] - pos).length() < 0.3:
			break
		var target := _ahead(line, i, pos, LOOKAHEAD)
		var dir := _flat(target - pos).normalized()
		var local := _player.global_basis.inverse() * dir
		_player.input_override = Vector2(local.x, -local.z)
		var dt := get_physics_process_delta_time()
		_player.rotation.y = lerp_angle(_player.rotation.y, atan2(-dir.x, -dir.z), 1.0 - exp(-TURN_RATE * dt))
		await get_tree().physics_frame
		t += dt
	_player.input_override = Vector2.ZERO


## The point `dist` along `line` past the player's place on segment `i`.
func _ahead(line: PackedVector3Array, i: int, pos: Vector3, dist: float) -> Vector3:
	var a := line[i]
	var b := line[i + 1]
	var ab := b - a
	var u := clampf((pos - a).dot(ab) / maxf(ab.length_squared(), 0.0001), 0.0, 1.0)
	var at := a + ab * u
	var left := dist
	var k := i
	while k < line.size() - 1:
		var to := line[k + 1] - at
		if to.length() >= left:
			return at + to.normalized() * left
		left -= to.length()
		at = line[k + 1]
		k += 1
	return line[-1]


func _flat(v: Vector3) -> Vector3:
	return Vector3(v.x, 0.0, v.z)


## Holds `look_back` for `seconds` once the porter comes within 1 m of `at`.
func _look_back_at(at: Vector3, seconds: float) -> void:
	await _until(func() -> bool: return _flat(_player.global_position - at).length() < 1.0, 30.0)
	Input.action_press(&"look_back")
	await _seconds(seconds)
	Input.action_release(&"look_back")


func _turn_to(yaw: float, seconds: float) -> void:
	var tween := create_tween()
	tween.tween_property(_player, ^"rotation:y", _player.rotation.y + wrapf(yaw - _player.rotation.y, -PI, PI), seconds)
	await tween.finished


func _spot(spot_name: String) -> HidingSpot:
	for s: HidingSpot in get_tree().get_nodes_in_group(&"hiding_spots"):
		if s.name == spot_name:
			return s
	return null


func _until(cond: Callable, limit: float) -> void:
	var t := 0.0
	while not cond.call() and t < limit:
		await get_tree().physics_frame
		t += get_physics_process_delta_time()


func _seconds(s: float) -> void:
	await get_tree().create_timer(s, true, true).timeout

