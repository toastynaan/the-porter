class_name NightPilot
extends RefCounted
## Plays the porter's part in a night for tests: uses duties when the night
## wants them, counts the brothers, walks the round past the demon, goes down
## to the crypt. Times are simulated seconds (tests run at a fixed rate).

var night: Node
var player: Player
var _tree: SceneTree
var _check: Callable


## A night that hasn't started: no bell rung, nothing done, saves to
## `save_path`, played on its own (no chapter, nothing carried).
static func fresh_night(save_path: String) -> void:
	GameState.save_path = save_path
	GameState.new_game()
	GameState.night = 3
	GameState.phase = GameState.Phase.DUSK


## main.tscn with `level` to play on its own (no title).
static func main_with(level_path: String) -> Node:
	var main: Node = load("res://game/render/main.tscn").instantiate()
	main.set(&"level", load(level_path))
	return main


## `check` is the test's func(ok: bool, what: String).
func _init(night_root: Node, check: Callable) -> void:
	night = night_root
	_tree = night_root.get_tree()
	_check = check
	player = _tree.get_first_node_in_group(&"player") as Player


func director() -> NightDirector:
	return night.get_node(^"Director") as NightDirector if is_instance_valid(night) else null


func beat() -> StringName:
	var d := director()
	return d.current.name if d and d.current else &""


## The night is over: its director has finished, or the game has moved on.
func over() -> bool:
	return director() == null or director().current == null


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


## Short waits: the beats' pacing is for play, not tests. The candle clock
## all but stops while he is awake (tests move it on with skip_to) and runs
## very fast while he dozes.
func shorten() -> void:
	var d := director()
	var settings := {^"Knocks": {&"knock_every": 1.0, &"visitor_speed": 6.0},
		^"Choir": {&"office_time": 0.5}, ^"Crypt": {&"quiet_time": 0.5}}
	for beat_path: NodePath in settings:
		var node := d.get_node_or_null(beat_path)
		if node:
			for key: StringName in settings[beat_path]:
				node.set(key, settings[beat_path][key])
	(night.get_node(^"Stalker") as Stalker).quiet_lead = 0.3
	(night.get_node(^"Clock") as NightClock).set_pace(3600.0, 0.1)
	for person in night.get_node(^"People").get_children():
		if person is VisitorNPC:
			(person as VisitorNPC).speed = 6.0


func clock() -> NightClock:
	return night.get_node(^"Clock") as NightClock


## Moves the candle clock on to `hour` (never back).
func skip_to(hour: float) -> void:
	GameState.hour = maxf(GameState.hour, hour)


## Sits on the gate bench and dozes; returns once he is dozing.
func doze() -> void:
	var bench := night.get_node(^"GateBench") as GateBench
	await until(func() -> bool: return not player.controls_locked and bench.can_doze(), 5.0)
	player.place(bench.global_position + Vector3(0.6, 0, 0), 0.0)
	bench.interact(player)
	await until(func() -> bool: return clock().dozing, 3.0)
	_check.call(clock().dozing, "he dozes on the gate bench (%s)" % NightClock.clock_text(GameState.hour))


## Waits for the night to wake him on the bench, and for his eyes to open.
func wake() -> void:
	var bench := night.get_node(^"GateBench") as GateBench
	await until(func() -> bool: return not bench.sitting, 30.0)


## The small hours and dawn, as the porter plays them: doze until Lauds,
## give Cole the gate, find the keys in the cell, sleep.
func see_out_the_night() -> void:
	await until(func() -> bool: return beat() == &"SmallHours", 20.0)
	await doze()
	await wake()
	await until(func() -> bool: return beat() == &"Dawn", 5.0)
	player.place(mark("ColeGate") + Vector3(1.2, 0, 0), deg_to_rad(90.0))
	await use("HandOver")
	player.place(mark("DawnCell"), 0.0)
	await use("KeysMoved")
	await use("Sleep")
	await until(func() -> bool: return GameState.has_flag(&"night3_done") or not is_instance_valid(night), 10.0)

## A stub night (M8): wakes, lets the night go by, and sleeps at the cot.
func play_stub() -> void:
	await until(func() -> bool: return beat() == &"Wake" and not player.controls_locked, 10.0)
	skip_to(17.25)
	await until(func() -> bool: return beat() == &"Sleep", 20.0)
	await use("Sleep")
	await until(over, 10.0)


## Night 3 from waking to sleep, as test_night3 plays it but without its
## checks: eats, takes the remedy, admits Walter, rings Matins, counts the
## brothers, walks the round, goes down to the crypt, hides in the oven and
## holds his breath, is pulled away by Thomas, dozes to Lauds and sleeps.
## `answer` is the Array the test's Talk.auto_choice reads.
func play_night3(answer: Array) -> void:
	await until(func() -> bool: return beat() == &"Wake" and not player.controls_locked, 10.0)
	skip_to(17.5)
	await until(func() -> bool: return beat() == &"Supper", 5.0)
	player.place(mark("PorterSeat") + Vector3(0, 0, 0.6), PI)
	await use("SupperSeat")
	await until(func() -> bool: return duty("Bread").enabled, 10.0)
	duty("Bread").interact(player)
	await until(func() -> bool: return duty("RelieveCole").enabled, 20.0)
	player.place(Vector3(-36.5, 0.05, -2), deg_to_rad(90.0))
	await use("RelieveCole")
	await use("ShutGate")
	await until(func() -> bool: return not (night.get_node(^"AbbeyGate") as AbbeyGate).is_open(), 3.0)
	await use("BarGate")
	await use("Ledger")
	await until(func() -> bool: return beat() == &"Knocks", 5.0)
	await doze()
	await keep_gate(0, [], answer)
	if GameState.dose >= 50.0:
		await until(func() -> bool: return duty("Grate").enabled, 30.0)
		await wake()
		await use("Grate")
	await until(func() -> bool: return beat() == &"Bell", 60.0)
	await doze()
	await wake()
	player.place(Vector3(-24, 0.05, -30.8), 0.0)
	await use("BellRope")
	await until(func() -> bool: return beat() == &"Choir", 5.0)
	await count_brothers()
	await walk_round()
	await go_down_to_crypt()
	await until(func() -> bool: return beat() == &"Chase", 3.0)
	var oven: HidingSpot = night.get_node(^"Abbey/Navigation/SouthRange/HidingSpots/Oven")
	var hunter: Hunter = night.get_node(^"Hunter")
	player.place(oven.exit.global_position, deg_to_rad(90.0))
	player.hide_in(oven)
	var checked := []
	oven.checked.connect(func(found: bool) -> void: checked.append(found))
	await until(func() -> bool: return hunter.global_position.distance_to(oven.view.global_position) < 8.0, 60.0)
	Input.action_press(&"hold_breath")
	await until(func() -> bool: return not checked.is_empty(), 12.0)
	await until(func() -> bool: return hunter.global_position.distance_to(oven.view.global_position) > 4.0 or hunter.state == Hunter.State.PATROL, 8.0)
	Input.action_release(&"hold_breath")
	player.leave_hiding()
	await until(func() -> bool: return GameState.has_flag(&"n3_thomas_hid_you"), 10.0)
	await see_out_the_night()
	await until(over, 10.0)


## Answers the visitor's knock at the grille, looks at his `read` parts while
## the choice is open, then answers `pick` (0 admit, 1 turn away, 2 the
## prior) through `answer`, an Array the test's Talk.auto_choice reads.
## Admitting, plays the porter's part: bar, gate, gate, bar, a bed, the
## ledger. Returns the visitor.
func keep_gate(pick: int, read: Array[StringName], answer: Array) -> VisitorNPC:
	await until(func() -> bool: return duty("Grate").enabled, 120.0)
	await wake()
	player.place(Vector3(-39.0, 0.05, -2.0), deg_to_rad(90.0))
	duty("Grate").interact(player)
	var npc := _tree.get_first_node_in_group(&"callers") as VisitorNPC
	await until(func() -> bool: return Talk.is_choosing(), 5.0)
	# His view is still easing in on the visitor's face.
	await seconds(Player.TALK_TURN_TIME + 0.05)
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


## Talks to `talker`: answers each choice with the next of `picks` through
## `answer` (an Array the test's Talk.auto_choice reads); -1 walks away.
## Returns once the talk is over.
func talk(talker: Talker, picks: Array[int], answer: Array) -> void:
	talker.interact(player)
	for pick in picks:
		await until(func() -> bool: return Talk.is_choosing() or not talker.talking, 10.0)
		if not talker.talking:
			break
		if pick < 0:
			await walk_off()
		else:
			answer[0] = pick
			await until(func() -> bool: return not Talk.is_choosing(), 2.0)
			answer[0] = -1
	await until(func() -> bool: return not talker.talking, 10.0)


## Walks away from the conversation he is in: a step back.
func walk_off() -> void:
	player.use_input_override = true
	player.input_override = Vector2(0.0, -1.0)
	await until(func() -> bool: return not Talk.talking, 2.0)
	player.input_override = Vector2.ZERO
	player.use_input_override = false


## In the choir: looks at every brother in turn. Returns how many were there.
## (Brothers in line are counted together, so the office may end, and the
## brothers leave, before he has turned to each one.)
func count_brothers() -> int:
	player.place(mark("Choir") + Vector3(-5.5, 0, 0), deg_to_rad(-90.0))
	await until(func() -> bool: return GameState.has_flag(&"n3_incense"), 5.0)
	var present: Array[Brother] = []
	for b: Brother in _tree.get_nodes_in_group(&"brothers"):
		if b.visible and b.global_position.distance_to(mark("Choir")) < 10.0:
			present.append(b)
	for b in present:
		face(b.global_position + Vector3.UP * 1.6)
		await seconds(0.4)
	await until(func() -> bool: return GameState.has_flag(&"n3_headcount"), 3.0)
	return present.size()


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
