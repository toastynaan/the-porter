extends Node
## Night 0 and day 1 (docs/mechanics.md, "Night 0 and day 1" and "Tests";
## docs/full-game-run.md, M12), through main.tscn from New Game to night 1's
## dusk in one run:
## - night 0: the ride in arrives at the lane (about three minutes at its own
##   pace, the body going by in the first minute, the traveller's talk); the
##   gate barred, nobody at it; the knock and Mab sending him to the Keys;
##   Agnes's room; ales blur and wear off; the curfew bell, Gib's call and the
##   squint scare once; lying down plays the cry and the window (the killing,
##   the body dragged off, his notes say how much he'd drunk); then sleep;
## - day 1: the headache after three ales, until noon; the gate open, the sand
##   by the well; the tour visits every duty and he tries each; the sand's
##   lie; the guesthouse key; Anselm's warning; the nap leads to night 1's
##   dusk. On a replay the tour can be skipped.
## Run: tools/check.sh

const TEST_SAVE := "user://test_prologue_save.tres"
const TEST_SETTINGS := "user://test_prologue_settings.cfg"

var _fails := 0
var _main: Node
var _flow: GameFlow
var _answer := [-1]


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	GameState.save_path = TEST_SAVE
	for path in [TEST_SAVE, GameState.quiet_path()]:
		DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
	Settings.path = TEST_SETTINGS
	Settings.finished = false
	Talk.line_seconds = 0.05
	Talk.auto_choice = func(_options: PackedStringArray) -> int: return _answer[0] if _answer[0] >= 0 else 0
	_main = load("res://game/render/main.tscn").instantiate()
	add_child(_main)
	_flow = _main.get_node(^"Game")
	_flow.card.seconds = 0.3
	await _frames(5)

	# Night 0: the ride.
	_button(_flow.title, "New Game").pressed.emit()
	await _until(func() -> bool: return _level() != null and _level().get_node_or_null(^"Director") != null, 10.0)
	var night := _level()
	var pilot := NightPilot.new(night, _check)
	var ride := night.get_node(^"Director/Ride")
	var length := 0.0
	var pts: Array[Vector3] = (ride as NightBeat).points(night.get_node(^"Road/RidePath"))
	for i in range(1, pts.size()):
		length += pts[i - 1].distance_to(pts[i])
	var minutes := length / float(ride.get(&"speed")) / 60.0
	_check(minutes > 2.5 and minutes < 3.5 and float(ride.get(&"meet_at")) < 60.0,
		"the ride takes about three minutes (%.1f), the body goes by in the first" % minutes)
	pilot.shorten()
	await _until(func() -> bool: return pilot.beat() == &"Ride" and pilot.player.riding != null, 5.0)
	var p := pilot.player
	_check(GameState.night == 0 and p.riding != null and GameState.has_flag(&"n0_riding"), "New Game: night 0, on the carter's wagon")
	var wagon := night.get_node(^"Wagon") as Node3D
	var cart := night.get_node(^"BodyCart") as Node3D
	var closest := INF
	var started := wagon.global_position
	var moved := 0.0
	while not GameState.has_flag(&"n0_arrived") and is_instance_valid(wagon) and is_instance_valid(cart):
		closest = minf(closest, cart.global_position.distance_to(wagon.global_position))
		moved = wagon.global_position.distance_to(started)
		await get_tree().physics_frame
	_check(closest < 4.0 and closest > 2.0 and moved > 10.0, "the wagon drives itself; the body cart passes close by on the other side of the road (%.1f m)" % closest)
	await _until(func() -> bool: return GameState.has_flag(&"talked_n0_traveller"), 10.0)
	_check(GameState.has_flag(&"talked_n0_traveller"), "the traveller talks as the body goes by")
	await _until(func() -> bool: return pilot.beat() == &"Arrive" and not Talk.talking, 60.0)
	var gate := night.get_node(^"AbbeyGate") as AbbeyGate
	_check(GameState.has_flag(&"n0_arrived") and p.riding == null and p.global_position.distance_to(pilot.mark("SetDown")) < 1.0
		and not is_instance_valid(wagon), "the carter sets him down in the lane by the gate")
	_check(not gate.is_open() and gate.bar.visible and not (night.get_node(^"People/Cole") as Node3D).visible,
		"the gate is shut and barred, and nobody keeps it")

	# The knock, and Mab.
	p.place(pilot.duty("KnockGate").global_position + Vector3(-1.2, 0.0, 0.0), deg_to_rad(-90.0))
	await pilot.use("KnockGate")
	var mab := night.get_node(^"People/Mab") as VisitorNPC
	await _until(func() -> bool: return mab.is_in_group(&"glyph_targets"), 5.0)
	_check(mab.is_in_group(&"glyph_targets"), "nobody comes; the duty flame goes to Mab")
	p.place(mab.global_position + Vector3(-1.4, 0.0, 0.0), deg_to_rad(-90.0))
	await pilot.talk(mab.get_node(^"Talker") as Talker, [2, 0, 0], _answer)
	_check(GameState.has_flag(&"n0_sent_to_inn") and GameState.satchel.has(&"mab_bread"), "Mab sends him to the Keys (and gives him bread for alms)")

	# The Keys: a room from Agnes, ales with Hob.
	await _until(func() -> bool: return pilot.beat() == &"Inn", 10.0)
	var agnes := night.get_node(^"People/Agnes") as VisitorNPC
	var hob := night.get_node(^"People/Hob") as VisitorNPC
	_check(agnes.is_in_group(&"glyph_targets") and agnes.global_position.x < -50.0 and hob.global_position.x < -50.0,
		"Agnes and Hob are inside the Keys; the flame goes to Agnes")
	p.place(agnes.global_position + Vector3(1.3, 0.0, 0.0), deg_to_rad(90.0))
	await pilot.talk(agnes.get_node(^"Talker") as Talker, [0, 1], _answer)
	_check(GameState.has_flag(&"n0_room") and absf(GameState.drink - 1.0) < 0.05, "the room at the top, and an ale (%.0f)" % GameState.drink)
	_check(DoseDriver.drink_blur() > 0.0 and DoseDriver.drunk_amount() == 0.0, "one ale: a softer focus")
	await _until(func() -> bool: return pilot.beat() == &"Window", 5.0)
	p.place(hob.global_position + Vector3(1.3, 0.0, 0.0), deg_to_rad(90.0))
	for i in 2:
		await pilot.talk(hob.get_node(^"Talker") as Talker, [2], _answer)
	_check(absf(GameState.drink - 3.0) < 0.05 and DoseDriver.drunk_amount() > 0.3, "three: the image doubles (%.2f)" % GameState.drink)
	pilot.clock().set_pace(2.0, 0.1)
	await pilot.seconds(2.2)
	pilot.clock().set_pace(3600.0, 0.1)
	_check(GameState.drink < 2.2 and GameState.drink > 1.5, "and it wears off, one an hour (%.2f)" % GameState.drink)
	await pilot.talk(hob.get_node(^"Talker") as Talker, [2], _answer)
	_check(GameState.drink > 2.8 and int(GameState.get_flag(&"drank", 0)) == 4, "another (%.2f, four ales)" % GameState.drink)

	# The curfew, Gib, the squint scare.
	p.place(Vector3(-41.2, 0.05, 9.0), PI)
	pilot.skip_to(21.0)
	var curfew := night.get_node(^"Curfew") as Curfew
	var inn_door := night.get_node(^"Abbey/Street/Houses/Inn/Door") as Door
	await _until(func() -> bool: return curfew.lane_empty(), 30.0)
	_check(curfew.has_rung and not inn_door.is_open and curfew.lane_empty() and hob.visible and agnes.visible,
		"nine: the curfew bell, the Keys shut, the lane empty; Hob and Agnes stay in (%s %s %s)" % [curfew.has_rung, inn_door.is_open, curfew.lane_empty()])
	pilot.skip_to(22.02)
	await _frames(3)
	_check(curfew.calls == [22], "ten: Gib calls the hour")
	var gib := night.get_node(^"People/Gib") as Node3D
	await _until(func() -> bool: return gib.global_position.z < -10.0 or gib.global_position.z > 40.0, 30.0)
	var scare := night.get_node(^"SquintScare") as SquintScare
	var south := scare.squint
	p.place(south.global_position + Vector3(-1.4, -1.55, 0.0), 0.0)
	await _frames(3)
	pilot.face(south.global_position)
	await pilot.seconds(0.6)
	_check(scare.figure != null and scare.seen, "alone at the south squint: a shape stands inside, seen through the slit")
	p.place(p.global_position + Vector3(-1.0, 0.0, 0.0), 0.0)
	await pilot.seconds(0.4)
	_check(scare.figure == null and GameState.has_flag(&"n0_squint_scare"), "he looks away: gone")

	# The window.
	var death := night.get_node(^"WindowKilling") as DeathScene
	p.place(pilot.duty("InnBed").global_position + Vector3(0.0, 0.0, -1.4), 0.0)
	await pilot.use("InnBed")
	await _until(func() -> bool: return death.has_played, 10.0)
	_check(death.has_played and p.global_position.distance_to(pilot.mark("TopWindow")) < 0.5,
		"lying down: the cry, and he's at the window over the abbey wall")
	_check(ViewCheck.on_screen(p.camera, [death.global_position + Vector3.UP])
		and ViewCheck.clear(p, p.camera.global_position, death.global_position + Vector3.UP), "the killing is in his view, through the window")
	await _until(func() -> bool: return pilot.beat() == &"Sleep", 120.0)
	_check(GameState.has_flag(&"moved_night0_guest") and GameState.has_note(&"window_killing_drunk")
		and GameState.get_flag(&"n0_saw_killing") == &"drunk", "the body is dragged off toward the cellar; drunk, his notes doubt it")
	await pilot.use("InnBed")
	var night_id := night.get_instance_id()
	await _until(func() -> bool: return GameState.chapter == 1 and _level_changed(night_id), 20.0)
	_check(GameState.has_flag(&"night0_done") and GameState.chapter == 1, "night 0 ends in sleep; day 1 begins")

	# Day 1.
	night = _level()
	await _until(func() -> bool: return night.get_node_or_null(^"Director") != null, 5.0)
	pilot = NightPilot.new(night, _check)
	pilot.shorten()
	p = pilot.player
	await _until(func() -> bool: return pilot.beat() == &"Morning" and not p.controls_locked, 10.0)
	_check(GameState.drink == 0.0 and GameState.has_flag(&"hangover") and DoseDriver.drink_blur() > 0.8,
		"day 1: sleep cleared the drink, but three ales or more leave a headache (%.2f, %s, %.2f)" % [GameState.drink, GameState.has_flag(&"hangover"), DoseDriver.drink_blur()])
	var hour := GameState.hour
	GameState.hour = 12.5
	_check(DoseDriver.drink_blur() == 0.0, "gone by noon")
	GameState.hour = hour
	gate = night.get_node(^"AbbeyGate") as AbbeyGate
	_check(gate.is_open() and (night.get_node(^"People/Cole") as Node3D).visible, "the gate stands open, Cole at it")
	p.place(pilot.mark("Day1Meet"), deg_to_rad(90.0))
	await _until(func() -> bool: return pilot.beat() == &"Tour", 10.0)
	_check(GameState.has_flag(&"d1_saw_sand"), "the sand by the well")
	var tour := night.get_node(^"Director/Tour")
	for path in ["BarGate", "Ledger", "", "BellRope", "RoundStops/StoresDoor", "GuestBeds/Bed0", "GuestKey"]:
		if path.is_empty():
			var candles := night.get_node(^"CandleClock") as CandleClock
			await _until(func() -> bool: return candles.is_in_group(&"glyph_targets"), 60.0)
			candles.interact(p)
		else:
			await _until(func() -> bool: return pilot.duty(path).enabled, 60.0)
			p.place(pilot.duty(path).global_position + Vector3(0.0, 0.0, 1.2), 0.0)
			await pilot.use(path)
	_check((tour.get(&"tried") as Array) == [0, 1, 2, 3, 4, 5], "the tour stops at every duty and he tries each (%s)" % [tour.get(&"tried")])
	_check(GameState.has_flag(&"d1_asked_sand") and GameState.has_note(&"sand_by_the_well"), "asked about the sand: Thomas's first lie")
	await _until(func() -> bool: return pilot.beat() == &"Nap", 30.0)
	_check(GameState.keys.has(&"guesthouse") and GameState.has_flag(&"d1_anselm_warned"), "the guesthouse key; Anselm's warning")
	await pilot.use("Sleep")
	night_id = night.get_instance_id()
	await _until(func() -> bool: return GameState.chapter == 2 and _level_changed(night_id), 20.0)
	night = _level()
	await _until(func() -> bool: return night.get_node_or_null(^"Director") != null, 5.0)
	_check(GameState.night == 1 and GameState.hour >= 16.0 and GameState.hour < 19.0 and not GameState.has_flag(&"hangover"),
		"the nap leads to night 1's dusk (%.1f)" % GameState.hour)

	# A replay: the tour can be skipped.
	Settings.finished = true
	_flow.start_chapter(1, false)
	night_id = night.get_instance_id()
	await _until(func() -> bool: return _level_changed(night_id) and _level().get_node_or_null(^"Director") != null, 10.0)
	night = _level()
	pilot = NightPilot.new(night, _check)
	await _until(func() -> bool: return pilot.beat() == &"Morning" and not pilot.player.controls_locked, 10.0)
	pilot.player.place(pilot.mark("Day1Meet"), deg_to_rad(90.0))
	_answer[0] = 1
	await _until(func() -> bool: return pilot.beat() == &"Nap", 10.0)
	_answer[0] = -1
	_check(GameState.has_flag(&"d1_tour_skipped"), "on a replay the tour can be skipped")

	for path in [TEST_SAVE, GameState.quiet_path(), TEST_SETTINGS]:
		DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
	Talk.auto_choice = Callable()
	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


func _level() -> Node:
	return _main.get(&"current_level")


func _level_changed(from_id: int) -> bool:
	return _level() != null and _level().get_instance_id() != from_id


func _button(page: MenuPage, label: String) -> Button:
	for c in page.column.get_children():
		if c is Button and (c as Button).text == label:
			return c
	push_error("no button %s" % label)
	return null


func _until(cond: Callable, limit: float) -> void:
	var t := 0.0
	while not cond.call() and t < limit:
		await get_tree().physics_frame
		t += 1.0 / Engine.physics_ticks_per_second


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
