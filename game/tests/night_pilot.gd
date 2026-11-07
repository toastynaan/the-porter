class_name NightPilot
extends RefCounted
## Plays the porter's part in a night for tests: uses duties when the night
## wants them, counts the brothers, walks the round past the demon, goes down
## to the crypt. Times are simulated seconds (tests run at a fixed rate).

var night: Node
var player: Player
var _tree: SceneTree
var _check: Callable


## A night that hasn't started: no bell rung, nothing done, saves to `save_path`.
static func fresh_night(save_path: String) -> void:
	GameState.save_path = save_path
	GameState.last_bell = &""
	GameState.captures = 0
	GameState.suspicion = 0
	GameState.flags = {}
	GameState.keys = [&"gate", &"guesthouse", &"charnel"]
	GameState.ledger = []
	GameState.dose_floor = 0.0
	GameState.seconds_per_hour = 0.0
	GameState.snap_dose(0.0)
	GameState.phase = GameState.Phase.SUPPER


## `check` is the test's func(ok: bool, what: String).
func _init(night_root: Node, check: Callable) -> void:
	night = night_root
	_tree = night_root.get_tree()
	_check = check
	player = _tree.get_first_node_in_group(&"player") as Player


func director() -> NightDirector:
	return night.get_node(^"Director") as NightDirector


func beat() -> StringName:
	var d := director()
	return d.current.name if d.current else &""


func duty(path: String) -> Duty:
	return night.get_node(NodePath("Duties/" + path)) as Duty


func mark(mark_name: String) -> Vector3:
	return (night.get_node(NodePath("Marks/" + mark_name)) as Node3D).global_position


## Waits for the duty to be wanted, then uses it.
func use(path: String) -> void:
	var d := duty(path)
	await until(func() -> bool: return d.enabled, 15.0)
	_check.call(d.enabled, "%s is wanted" % path)
	d.interact(player)
	await frames(2)


## Short waits: the beats' pacing is for play, not tests.
func shorten() -> void:
	var d := director()
	var settings := {^"Knocks": {&"first_delay": 0.3, &"knock_every": 1.0, &"visitor_speed": 6.0},
		^"Choir": {&"office_time": 0.5}, ^"Crypt": {&"quiet_time": 0.5}}
	for beat_path: NodePath in settings:
		var node := d.get_node_or_null(beat_path)
		if node:
			for key: StringName in settings[beat_path]:
				node.set(key, settings[beat_path][key])
	(night.get_node(^"Stalker") as Stalker).quiet_lead = 0.3


## Answers the visitor's knock at the grille, looks at his `read` parts while
## the choice is open, then answers `pick` (0 admit, 1 turn away, 2 the
## prior) through `answer`, an Array the test's Talk.auto_choice reads.
## Admitting, plays the porter's part: bar, gate, gate, bar, a bed, the
## ledger. Returns the visitor.
func keep_gate(pick: int, read: Array[StringName], answer: Array) -> VisitorNPC:
	await until(func() -> bool: return duty("Grate").enabled, 120.0)
	player.place(Vector3(-39.0, 0.05, -2.0), deg_to_rad(90.0))
	duty("Grate").interact(player)
	var npc := _tree.get_first_node_in_group(&"visitors") as VisitorNPC
	await until(func() -> bool: return Talk.is_choosing(), 5.0)
	for part in read:
		face(npc.part_position(part))
		await seconds(0.6)
	answer[0] = pick
	await frames(3)
	answer[0] = -1
	if pick == 0:
		await use("BarGate")
		await use("OpenGate")
		await use("ShutGate")
		await use("BarGate")
		player.place(Vector3(-30.0, 0.05, -19.0), 0.0)
		face(duty("GuestBeds/Bed2").global_position)
		await use("GuestBeds/Bed2")
		await until(func() -> bool: return npc.lying, 20.0)
	if pick != 1:
		await until(func() -> bool: return duty("Ledger").enabled, 60.0)
		player.place(Vector3(-33.2, 0.05, -9.6), PI)
		await use("Ledger")
	return npc


## In the choir: looks at every brother in turn. Returns how many.
func count_brothers() -> int:
	player.place(mark("Choir") + Vector3(-5.5, 0, 0), deg_to_rad(-90.0))
	await until(func() -> bool: return GameState.has_flag(&"n3_incense"), 5.0)
	var counted := 0
	for b: Brother in _tree.get_nodes_in_group(&"brothers"):
		if b.visible and b.global_position.distance_to(mark("Choir")) < 10.0:
			face(b.global_position + Vector3.UP * 1.6)
			await seconds(0.4)
			counted += 1
	await until(func() -> bool: return GameState.has_flag(&"n3_headcount"), 3.0)
	return counted


## Checks the round's stops, looking at the demon each time it appears and
## turning his back on it. Returns its distances. `on_seen`, if given, is
## awaited while he faces it: func(stalker: Stalker).
func walk_round(on_seen := Callable()) -> Array[float]:
	await until(func() -> bool: return beat() == &"Round", 15.0)
	var stalker: Stalker = night.get_node(^"Stalker")
	var stands := {"StoresDoor": Vector3(-10.2, 0.05, -6), "ChapterDoor": Vector3(10.2, 0.05, -18),
		"SanctuaryLamp": Vector3(25.0, 0.05, -32.6)}
	var distances: Array[float] = []
	for stop: String in stands:
		player.place(stands[stop], 0.0)
		face(duty("RoundStops/" + stop).global_position + Vector3.UP * 0.2)
		await use("RoundStops/" + stop)
		await until(func() -> bool: return stalker.step == Stalker.Step.SHOWN, 12.0)
		_check.call(stalker.step == Stalker.Step.SHOWN, "after the %s, it appears" % stop)
		distances.append(stalker.last_distance)
		face(stalker.global_position + Vector3.UP * 1.5)
		if on_seen.is_valid():
			await on_seen.call(stalker)
		await seconds(0.5)
		if stalker.final:
			Input.action_press(&"cover_lantern")
		face(player.global_position + (player.global_position - stalker.global_position))
		await until(func() -> bool: return not stalker.visible, 4.0)
		Input.action_release(&"cover_lantern")
	return distances


## Waits for the crypt light and goes down to it.
func go_down_to_crypt() -> void:
	await until(func() -> bool: return beat() == &"Crypt", 5.0)
	await until(func() -> bool: return (night.get_node(^"CryptLight") as Node3D).visible, 5.0)
	player.place(mark("CryptFoot"), deg_to_rad(-90.0))
	var hunter: Hunter = night.get_node(^"Hunter")
	await until(func() -> bool: return hunter.state == Hunter.State.CHASE, 3.0)


func face(point: Vector3) -> void:
	var to := point - player.camera.global_position
	player.rotation.y = atan2(-to.x, -to.z)
	player.head.rotation.x = atan2(to.y, Vector2(to.x, to.z).length())


func until(cond: Callable, limit: float) -> void:
	var t := 0.0
	while not cond.call() and t < limit:
		await _tree.physics_frame
		t += 1.0 / Engine.physics_ticks_per_second


func frames(n: int) -> void:
	for i in n:
		await _tree.physics_frame


func seconds(s: float) -> void:
	await _tree.create_timer(s, true, true).timeout
