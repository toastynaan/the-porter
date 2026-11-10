class_name NightPilot
extends RefCounted
## Plays the porter's part in a night for tests: uses duties when the night
## wants them, counts the brothers, walks the round past the demon, goes down
## to the crypt. Times are simulated seconds (tests run at a fixed rate).

const GateVisits := preload("res://game/night/gate_visits_beat.gd")
## The grille's answers, as the porter is offered them.
const GATE_ADMIT: String = GateVisits.ADMIT
const GATE_DONT_ASK: String = GateVisits.DONT_ASK
const GATE_LEAVE_TO_SLEEP: String = GateVisits.LEAVE_TO_SLEEP

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
## His Dose as he lay down to sleep (play_stub).
var dose_at_sleep := -1.0


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
	var settings := {^"Knocks": {&"knock_every": 1.0, &"visitor_speed": 6.0}, ^"Ride": {&"pace_scale": 8.0, &"accel": 60.0},
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
	var from := GameState.hour
	bench.interact(player)
	# Dozing, or dozed already: a fast clock can reach the next mark first.
	await until(func() -> bool: return clock().dozing or GameState.hour > from + 0.25, 3.0)
	_check.call(clock().dozing or GameState.hour > from + 0.25, "he dozes on the gate bench (%s)" % NightClock.clock_text(GameState.hour))


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
	dose_at_sleep = GameState.dose
	await use("Sleep")
	await until(over, 10.0)


## Night 0 from the wagon to sleep: rides in, knocks at the barred gate, is
## sent across by Mab, takes the room from Agnes (and an ale, if `answer`
## picks it), lies down, sees the killing from the window and sleeps.
## `answer` is the Array the test's Talk.auto_choice reads.
func play_night0(answer: Array) -> void:
	await until(func() -> bool: return beat() == &"Arrive" and not Talk.talking, 400.0)
	player.place(duty("KnockGate").global_position + Vector3(-1.2, 0.0, 0.0), deg_to_rad(-90.0))
	await use("KnockGate")
	var mab := night.get_node(^"People/Mab") as VisitorNPC
	player.place(mab.global_position + Vector3(-1.4, 0.0, 0.0), deg_to_rad(-90.0))
	await talk(mab.get_node(^"Talker") as Talker, [0, 0, 0], answer)
	await until(func() -> bool: return beat() == &"Inn", 10.0)
	var agnes := night.get_node(^"People/Agnes") as VisitorNPC
	player.place(agnes.global_position + Vector3(1.3, 0.0, 0.0), deg_to_rad(90.0))
	await talk(agnes.get_node(^"Talker") as Talker, [0, 0, 0], answer)
	await until(func() -> bool: return beat() == &"Window", 10.0)
	player.place(duty("InnBed").global_position + Vector3(0.0, 0.0, -1.4), 0.0)
	await use("InnBed")
	await until(func() -> bool: return beat() == &"Sleep", 120.0)
	await use("InnBed")
	await until(over, 20.0)


## Day 1 from waking at the Keys to the nap: crosses the lane, follows Thomas
## and Anselm and tries each duty, takes the guesthouse key, sleeps in his cell.
func play_day1() -> void:
	await until(func() -> bool: return beat() == &"Morning" and not player.controls_locked, 10.0)
	player.place(mark("Day1Meet"), deg_to_rad(90.0))
	await until(func() -> bool: return beat() == &"Tour", 10.0)
	for path in ["BarGate", "Ledger", "", "BellRope", "RoundStops/StoresDoor", "GuestBeds/Bed0", "GuestKey"]:
		if path.is_empty():
			var candles := night.get_node(^"CandleClock") as CandleClock
			await until(func() -> bool: return candles.is_in_group(&"glyph_targets"), 60.0)
			candles.interact(player)
		else:
			await until(func() -> bool: return duty(path).enabled, 60.0)
			player.place(duty(path).global_position + Vector3(0.0, 0.0, 1.2), 0.0)
			await use(path)
	await until(func() -> bool: return beat() == &"Nap", 30.0)
	await use("Sleep")
	await until(over, 20.0)


## A night's opening as the porter plays it: wakes, goes in at the supper
## bell, eats the bread (the test's `answer` picks, where there's a choice),
## takes the gate from Cole, shuts and bars it, opens the ledger.
func to_the_gate(from_wake := true) -> void:
	if from_wake:
		await until(func() -> bool: return beat() == &"Wake" and not player.controls_locked, 10.0)
	skip_to(17.25)
	await until(func() -> bool: return beat() == &"Supper", 5.0)
	player.place(mark("PorterSeat") + Vector3(0, 0, 0.6), PI)
	await use("SupperSeat")
	await until(func() -> bool: return duty("Bread").enabled, 10.0)
	duty("Bread").interact(player)
	await until(func() -> bool: return duty("RelieveCole").enabled, 30.0)
	player.place(Vector3(-36.5, 0.05, -2), deg_to_rad(90.0))
	await use("RelieveCole")
	await use("ShutGate")
	await until(func() -> bool: return not (night.get_node(^"AbbeyGate") as AbbeyGate).is_open(), 3.0)
	await use("BarGate")
	await use("Ledger")
	await until(func() -> bool: return beat() == &"Knocks", 5.0)


## Locks the guesthouse door, as the porter does with his key.
func lock_guesthouse() -> void:
	for d: Door in _tree.get_nodes_in_group(&"doors"):
		if d.key == &"guesthouse":
			d.set_open(false, true)
			d.locked = true


## Rings Matins, counts the brothers and walks the round (with the night's
## number of appearances).
func matins_and_round(appearances: int) -> void:
	await until(func() -> bool: return beat() == &"Bell", 120.0)
	if clock().dozing:
		await wake()
	elif not duty("BellRope").enabled and GameState.hour < 23.5:
		await doze()
		await wake()
	await until(func() -> bool: return duty("BellRope").enabled, 60.0)
	player.place(Vector3(-24, 0.05, -30.8), 0.0)
	await use("BellRope")
	await until(func() -> bool: return beat() == &"Choir", 10.0)
	await count_brothers()
	await walk_round(Callable(), appearances)


## Dozes to Lauds, gives Cole the gate, answers whom to tell of any body
## (the test's `answer`), and sleeps.
func dawn_and_sleep() -> void:
	await until(func() -> bool: return beat() == &"SmallHours", 60.0)
	await doze()
	await wake()
	await until(func() -> bool: return beat() == &"Dawn", 60.0)
	player.place(mark("ColeGate") + Vector3(1.2, 0, 0), deg_to_rad(90.0))
	await use("HandOver")
	player.place(mark("DawnCell"), 0.0)
	await use("Sleep")
	await until(over, 15.0)


## Night 1 from waking to sleep: admits the merchant (or `merchant` 1 turns
## him away, 2 sends for the prior) and Walter, locks the guesthouse if
## `lock`, rings Matins, walks the round, answers the knock with no one
## there, and at Lauds goes to the fishpond if the merchant died.
func play_night1(answer: Array, merchant := 0, lock := false, walter := 0) -> void:
	await to_the_gate()
	await doze()
	await keep_gate(merchant, [], answer, "GuestBeds/Bed2")
	if lock:
		lock_guesthouse()
	await doze()
	await keep_gate(walter, [], answer, "GuestBeds/Bed3")
	await matins_and_round(1)
	await doze()
	await until(func() -> bool: return duty("Grate").enabled, 120.0)
	await wake()
	player.place(Vector3(-39.0, 0.05, -2.0), deg_to_rad(90.0))
	await use("Grate")
	await until(func() -> bool: return beat() == &"SmallHours", 10.0)
	await doze()
	await wake()
	await until(func() -> bool: return beat() == &"Pond" or beat() == &"Dawn", 30.0)
	if GameState.has_flag(&"died_merchant"):
		var body := night.get_node(^"Bodies/Pond") as FoundBody
		await until(func() -> bool: return body.active(), 5.0)
		player.place(body.global_position + Vector3(-2.5, 0, 0), deg_to_rad(-90.0))
		face((body.body as Corpse).centre() if body.body is Corpse else body.global_position)
		await until(func() -> bool: return body.is_found, 5.0)
	await until(func() -> bool: return beat() == &"Dawn", 30.0)
	player.place(mark("ColeGate") + Vector3(1.2, 0, 0), deg_to_rad(90.0))
	await use("HandOver")
	player.place(mark("DawnCell"), 0.0)
	await use("Sleep")
	await until(over, 15.0)


## Night 2 from waking to sleep: Joan, Roger (if he comes) and the sailor
## (`joan`, `roger`, `sailor`: 0 admit, 1 turn away, 2 the prior); the lane
## death at the grille if there is one; the heavy rope and Bede; the count;
## the round and the guesthouse; Lauds, the abbot and the prior; sleep.
func play_night2(answer: Array, joan := 0, sailor := 0, roger := 0) -> void:
	await to_the_gate()
	await doze()
	await keep_gate(joan, [], answer, "GuestBeds/Bed2")
	if GameState.has_flag(&"died_merchant"):
		await doze()
		await keep_gate(roger, [], answer, "GuestBeds/Bed3")
	await doze()
	await keep_gate(sailor, [], answer, "GuestBeds/Bed4")
	await until(func() -> bool: return beat() == &"Lane" or beat() == &"Bell", 30.0)
	if beat() == &"Lane":
		if (night.get_node(^"GateBench") as GateBench).can_doze() and not duty("Grate").enabled:
			await doze()
		await until(func() -> bool: return duty("Grate").enabled or beat() != &"Lane", 120.0)
		if duty("Grate").enabled:
			await wake()
			player.place(Vector3(-39.0, 0.05, -2.0), deg_to_rad(90.0))
			await use("Grate")
	await matins_and_round(2)
	await until(func() -> bool: return beat() == &"Guesthouse", 30.0)
	player.place(duty("GuesthouseCheck").global_position + Vector3(0, 0, 1.5), 0.0)
	await use("GuesthouseCheck")
	await until(func() -> bool: return beat() == &"SmallHours", 30.0)
	await doze()
	await wake()
	await until(func() -> bool: return beat() == &"DawnScene", 30.0)
	var godric := night.get_node(^"Brothers/Godric") as Node3D
	await frames(2)
	player.place(godric.global_position + Vector3(-1.5, 0, 0), deg_to_rad(-90.0))
	await until(func() -> bool: return beat() == &"Dawn", 60.0)
	player.place(mark("ColeGate") + Vector3(1.2, 0, 0), deg_to_rad(90.0))
	await use("HandOver")
	player.place(mark("DawnCell"), 0.0)
	await use("Sleep")
	await until(over, 15.0)


## A Talk.auto_choice for tests that play whole nights: at the grille it
## waits for `answer` (keep_gate sets it), anything else takes `answer` if
## set, or the first choice.
static func gate_aware_choice(answer: Array) -> Callable:
	return func(options: PackedStringArray) -> int:
		if options.has(GATE_ADMIT):
			return answer[0]
		# Warning a guest at his bed: answer[1] if the test gives one (1: no).
		if options.has(GATE_LEAVE_TO_SLEEP):
			return answer[1] if answer.size() > 1 else 0
		return answer[0] if answer[0] >= 0 else 0


## Takes the gate from Cole after supper (or with no supper): relieve, shut,
## bar, the ledger.
func take_gate() -> void:
	await until(func() -> bool: return duty("RelieveCole").enabled, 30.0)
	player.place(Vector3(-36.5, 0.05, -2), deg_to_rad(90.0))
	await use("RelieveCole")
	await use("ShutGate")
	await until(func() -> bool: return not (night.get_node(^"AbbeyGate") as AbbeyGate).is_open(), 3.0)
	await use("BarGate")
	await use("Ledger")
	await until(func() -> bool: return beat() == &"Knocks", 5.0)


## Goes within `radius` of `node` (a marker, a body) and faces it.
func go_to(node: Node3D, radius := 1.5) -> void:
	var at := node.global_position
	player.place(at + Vector3(radius, 0, 0), deg_to_rad(90.0))
	face(at + Vector3.UP * 1.0)


## Gives Cole the gate and sleeps (answers whom to tell through the test's
## auto choice).
func hand_over_and_sleep() -> void:
	await until(func() -> bool: return beat() == &"Dawn", 60.0)
	player.place(mark("ColeGate") + Vector3(1.2, 0, 0), deg_to_rad(90.0))
	await use("HandOver")
	player.place(mark("DawnCell"), 0.0)
	await use("Sleep")
	await until(over, 15.0)


## Night 4 from waking to sleep: Edwin's whisper and Thomas at dusk, no
## supper, the gate; Mab let in, the pilgrim (`guest`: 0 admit, 1 turn away;
## warned at his bed if the test's answer[1] is 0); Matins without Edwin; the
## round's stops; the death in the fog and the prior; the guesthouse; Edwin
## in the charnel house; the two hunters (he lets Osric come close, sees his
## face, and gets away); Simon scrubbing; Lauds; his cell; sleep.
func play_night4(answer: Array, guest := 0) -> void:
	await until(func() -> bool: return beat() == &"Edwin" and not player.controls_locked, 15.0)
	go_to(mark_node("EdwinDusk"))
	await until(func() -> bool: return beat() == &"Thomas", 15.0)
	go_to(mark_node("ThomasDusk"))
	await until(func() -> bool: return beat() == &"Fast", 15.0)
	skip_to(17.25)
	await until(func() -> bool: return beat() == &"Gate", 10.0)
	await take_gate()
	await doze()
	await keep_gate(0, [], answer, "GuestBeds/Bed2")
	await doze()
	await keep_gate(guest, [], answer, "GuestBeds/Bed3")
	await matins_and_round(0)
	await until(func() -> bool: return beat() == &"Fog", 30.0)
	player.place(mark("FogSpot") + Vector3(-6.0, 0, 0), deg_to_rad(-90.0))
	await until(func() -> bool: return (night.get_node(^"FogDeath") as DeathScene).has_played, 10.0)
	go_to(night.get_node(^"FogDeath") as Node3D, 2.0)
	await until(func() -> bool: return beat() != &"Fog", 30.0)
	if beat() == &"Guest":
		player.place(mark("GuestDoor") + Vector3(0, 0, 2.0), PI)
		await until(func() -> bool: return beat() != &"Guest", 30.0)
	await until(func() -> bool: return beat() == &"Charnel", 10.0)
	var edwin := night.get_node(^"Bodies/Edwin") as FoundBody
	await until(func() -> bool: return edwin.active(), 5.0)
	player.place(edwin.global_position + Vector3(-2.5, 0, 0), deg_to_rad(-90.0))
	face((edwin.body as Corpse).centre() if edwin.body is Corpse else edwin.global_position)
	await until(func() -> bool: return beat() == &"Hunters", 15.0)
	await frames(3)
	var two := director().get_node(^"Hunters")
	var hunters: Array = two.get(&"hunters")
	if hunters.size() == 2:
		# Both of them at once: stand back from the two so both are in view.
		var a := (hunters[0] as Hunter).global_position
		var b := (hunters[1] as Hunter).global_position
		var mid := (a + b) * 0.5
		var side := (b - a).cross(Vector3.UP).normalized()
		player.place(mid + side * 8.0, 0.0)
		face(mid + Vector3.UP * 1.5)
		await until(func() -> bool: return GameState.has_note(&"two_demons"), 2.0)
		(hunters[1] as Hunter).queue_free()
		var osric := hunters[0] as Hunter
		await until(func() -> bool: return osric.global_position.distance_to(player.global_position) < 6.5, 4.0)
		face(osric.global_position + Vector3.UP * 1.6)
		await until(func() -> bool: return GameState.has_note(&"osric_mask"), 2.0)
	# He gets away (the chase itself is test_hunt's): they lose him.
	player.place(mark("DawnCell"), 0.0)
	for h: Variant in hunters:
		if is_instance_valid(h):
			(h as Node).queue_free()
	await until(func() -> bool: return beat() == &"Simon", 90.0)
	go_to(mark_node("SimonScrubbing"), 2.0)
	await until(func() -> bool: return beat() == &"SmallHours", 15.0)
	await doze()
	await wake()
	await hand_over_and_sleep()


## Night 5 from waking to sleep: the cry and the chapter house (`save`:
## &"thomas" or &"simon"); supper, the gate; Joan if she comes, the sergeant
## (`sergeant`: 0 let him wait inside, 1 leave him in the lane); Matins and
## Anselm; the granary, the grain, the lock-in and out by the latrine chute;
## Lauds and the prior's arrest; sleep.
func play_night5(answer: Array, save := &"simon", sergeant := 0) -> void:
	await until(func() -> bool: return beat() == &"Dilemma" and not player.controls_locked, 15.0)
	player.place(mark("ThomasUp") + Vector3(-3.0, 0, 0), deg_to_rad(-90.0))
	var reach := duty("ReachSimon" if save == &"simon" else "ReachThomas")
	await until(func() -> bool: return reach.enabled, 10.0)
	reach.interact(player)
	await until(func() -> bool: return beat() != &"Dilemma", 30.0)
	await to_the_gate(false)
	if GameState.has_flag(&"n2_joan_refused_at"):
		await doze()
		await keep_gate(0, [], answer, "GuestBeds/Bed2")
	await doze()
	await keep_gate(sergeant, [], answer, "GuestBeds/Bed4")
	await until(func() -> bool: return beat() == &"Bell", 120.0)
	await matins_and_round_no_round()
	await until(func() -> bool: return beat() == &"Anselm", 30.0)
	go_to(mark_node("AnselmChoir"), 1.5)
	await until(func() -> bool: return beat() == &"Granary", 15.0)
	player.place(duty("Grain").global_position + Vector3(0, 0, 1.4), 0.0)
	await use("Grain")
	await until(func() -> bool: return GameState.keys.has(&"crypt_passage"), 10.0)
	var chute := night.get_node(^"Abbey/Navigation/Dormitory/Squeezes/LatrineChute")
	player.place((chute.get_node(^"P0") as Node3D).global_position + Vector3(0, 0, 0.6), PI)
	chute.call(&"interact", player)
	await until(func() -> bool: return beat() != &"Granary", 30.0)
	await until(func() -> bool: return beat() == &"SmallHours", 15.0)
	await doze()
	await wake()
	await until(func() -> bool: return beat() == &"Arrest", 30.0)
	var hugh := night.get_node(^"Brothers/Hugh") as Node3D
	await frames(2)
	player.place(hugh.global_position + Vector3(-1.5, 0, 0), deg_to_rad(-90.0))
	await hand_over_and_sleep()


## Night 6 from dusk to the Broken Rite: finds Anselm, refuses the wine
## (answer[0] is set for it), lets the hunt go by (the hunters are test_hunt's),
## goes down at the rite and takes the book, and holds out to dawn.
func play_night6(answer: Array) -> void:
	await until(func() -> bool: return beat() == &"Anselm" and not player.controls_locked, 15.0)
	var anselm := night.get_node(^"Bodies/Anselm") as Node3D
	player.place(Vector3(27.6, 0.05, 2.4), deg_to_rad(-90.0))
	face(anselm.global_position + Vector3.UP * 0.6)
	await until(func() -> bool: return beat() == &"Wine", 10.0)
	answer[0] = 1
	var thomas := night.get_node(^"Brothers/Thomas") as Node3D
	await frames(2)
	player.place(thomas.global_position + Vector3(-1.5, 0, 0), deg_to_rad(-90.0))
	await until(func() -> bool: return beat() == &"Knock", 20.0)
	answer[0] = -1
	(night.get_node(^"Hunt") as Hunt).end()
	skip_to(23.0)
	await until(func() -> bool: return beat() == &"Rite", 10.0)
	await seconds(0.5)
	(night.get_node(^"Saint") as HungrySaint).sleep()
	(night.get_node(^"Proof/Book") as Pickup).interact(player)
	await until(func() -> bool: return GameState.has_flag(&"rite_stopped"), 5.0)
	skip_to(30.0)
	await until(over, 15.0)


## Rings Matins and counts the brothers (no round after: night 5 goes on to
## the granary).
func matins_and_round_no_round() -> void:
	if clock().dozing:
		await wake()
	elif not duty("BellRope").enabled and GameState.hour < 23.5:
		await doze()
		await wake()
	await until(func() -> bool: return duty("BellRope").enabled, 60.0)
	player.place(Vector3(-24, 0.05, -30.8), 0.0)
	await use("BellRope")
	await until(func() -> bool: return beat() == &"Choir", 10.0)
	await count_brothers()


func mark_node(mark_name: String) -> Node3D:
	return night.get_node(NodePath("Marks/" + mark_name)) as Node3D


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
func keep_gate(pick: int, read: Array[StringName], answer: Array, bed := "GuestBeds/Bed2") -> VisitorNPC:
	await until(func() -> bool: return duty("Grate").enabled, 120.0)
	await wake()
	player.place(Vector3(-39.0, 0.05, -2.0), deg_to_rad(90.0))
	duty("Grate").interact(player)
	# The one at the grille, not a guest already in bed.
	var npc: VisitorNPC = null
	for n in _tree.get_nodes_in_group(&"callers"):
		if not (n as VisitorNPC).lying and (n as VisitorNPC).visible:
			npc = n
	await until(func() -> bool: return Talk.is_choosing(), 5.0)
	# A visitor with a question: ask him nothing, on to the three choices
	# (they come up in the same talk, under his greeting).
	if Talk.offered().has(GATE_DONT_ASK):
		answer[0] = 1
		await until(func() -> bool: return not Talk.offered().has(GATE_DONT_ASK), 2.0)
		answer[0] = -1
		await until(func() -> bool: return Talk.offered().has(GATE_ADMIT), 5.0)
	# His view eases in on the visitor's face, and rests there long enough
	# to read it.
	await seconds(Player.TALK_TURN_TIME + 0.5)
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
		player.place(Vector3(duty(bed).global_position.x, 0.05, -19.0), 0.0)
		face(duty(bed).global_position)
		await use(bed)
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
	await until(func() -> bool: return GameState.has_flag(GameState.tonight("incense")), 5.0)
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
func walk_round(on_seen := Callable(), appearances := 3) -> Array[float]:
	await until(func() -> bool: return beat() == &"Round", 15.0)
	var stalker: Stalker = night.get_node(^"Stalker")
	var stands := {"StoresDoor": Vector3(-10.2, 0.05, -6), "ChapterDoor": Vector3(10.2, 0.05, -18),
		"SanctuaryLamp": Vector3(25.0, 0.05, -32.6)}
	var distances: Array[float] = []
	for stop: String in stands:
		player.place(stands[stop], 0.0)
		face(duty("RoundStops/" + stop).global_position + Vector3.UP * 0.2)
		await use("RoundStops/" + stop)
		if distances.size() >= appearances:
			distances.append(0.0)
			continue
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
	return distances.slice(0, appearances)


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
