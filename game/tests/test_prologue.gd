extends Node
## Night 0 and day 1 (docs/mechanics.md, "Night 0 and day 1" and "Tests";
## docs/full-game-run.md, M12), through main.tscn from New Game to night 1's
## dusk in one run:
## - night 0: the ride in arrives at the lane (about two minutes at its own
##   pace; the traveller turning to him as they set off, breaking off with
##   "Whoa. Look at that." as the body cart comes by the pulled-in wagon, and
##   the traveller on the body; paused, it waits; at Aldgate the traveller
##   breaks off to greet the warden, who walks up, holds his lantern to the
##   porter's face and walks back to his place; the wagon
##   waits at the gate for a talk to end, the carter's word, and it drives
##   off); the
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

	# Night 0: the ride, at its own pace.
	_button(_flow.title, "New Game").pressed.emit()
	await _until(func() -> bool: return _level() != null and _level().get_node_or_null(^"Director") != null, 10.0)
	var night := _level()
	var pilot := NightPilot.new(night, _check)
	var ride := night.get_node(^"Director/Ride")
	var accel: float = ride.get(&"accel")
	pilot.shorten()
	ride.set(&"pace_scale", 1.0)
	ride.set(&"accel", accel)
	await _until(func() -> bool: return pilot.beat() == &"Ride" and pilot.player.riding != null, 5.0)
	var p := pilot.player
	_check(GameState.night == 0 and p.riding != null and GameState.has_flag(&"n0_riding"), "New Game: night 0, on the carter's wagon")
	var fade := _main.get_node(^"UI/Fade") as ScreenFade
	_check(fade.color.a > 0.8 and not _flow.card.visible, "the card has gone into the dark, and the night opens on black (%.2f)" % fade.color.a)
	var wagon := night.get_node(^"Wagon") as Node3D
	var cart := night.get_node(^"BodyCart") as Node3D
	var talker := (ride.get(&"traveller") as Node3D).get_node(^"Talker") as Talker
	var answer_with := Talk.auto_choice
	# The traveller turns to him as they set off; he is still thinking of an
	# answer when the carter pulls in.
	Talk.auto_choice = func(_o: PackedStringArray) -> int: return -1
	var quiet := 0.0
	while not Talk.is_choosing() and quiet < 30.0:
		await get_tree().physics_frame
		quiet += get_physics_process_delta_time()
	_check(Talk.talking and GameState.has_flag(&"talked_n0_traveller_road") and not GameState.has_flag(&"talked_n0_traveller")
		and Talk.history.has(["Traveller", "Evening, brother. Bound for the city, are you?"]),
		"the traveller turns to him on the road, and asks him something")
	_check(quiet > 5.0 and fade.color.a < 0.05, "after a few quiet seconds of the road (%.1f s), the night come up out of black (%.2f)" % [quiet, fade.color.a])
	var said_before := Talk.history.size()
	var closest := INF
	var elapsed := 0.0
	var still := 0.0
	var stops: Array[Vector3] = []
	var last := wagon.global_position
	var paused_ok := false
	var hooked := false
	var hooked_at := 0.0
	var watched := -1.0
	var parted := false
	var held_talk := false
	var waited_at_gate := false
	var walked := [false]
	var leave_option := [""]
	var dark_from := Vector3.ZERO
	var warden := night.get_node(^"RoadFolk/Warden") as Node3D
	var warden_x := warden.global_position.x
	var warden_home := warden.global_position
	var warden_lantern := (warden.get_node(^"Look") as CharacterLook).part(^"Lantern")
	var warden_near := INF
	var lantern_near := INF
	var lantern_seen := -1.0
	var warden_back := false
	var gate_talk := false
	var gate_talk_open := false
	var bodies := cart.get_node(^"Bed/Bodies").get_child_count()
	var bed := wagon.get_node(^"Bed") as Node3D
	var jolt := 0.0
	var sway := 0.0
	var view_sway := 0.0
	const GREETING := ["Traveller", "Evening, warden. God keep the gate."]
	const LANTERN_LINE := ["", "(He holds his lantern up to your face, and looks at you a long moment.)"]
	var abbey := night.get_node(^"Abbey") as Node3D
	var lane_hidden := not abbey.visible
	var moving_into_dark := 0.0
	var last_step := 0.0
	var dark_jump := 0.0
	while not GameState.has_flag(&"n0_arrived") and elapsed < 300.0:
		await get_tree().physics_frame
		elapsed += get_physics_process_delta_time()
		if not is_instance_valid(cart):
			break
		closest = minf(closest, cart.global_position.distance_to(wagon.global_position))
		var at := wagon.global_position
		if at.distance_to(last) > 20.0:
			# The road between the bridge and the lane isn't ridden: it passes in the dark.
			dark_from = last
			dark_jump = fade.color.a
			moving_into_dark = last_step
		else:
			last_step = at.distance_to(last)
		still = still + get_physics_process_delta_time() if at.distance_to(last) < 0.0001 else 0.0
		last = at
		if still >= 0.5 and (stops.is_empty() or stops[-1].distance_to(at) > 1.0):
			stops.append(at)
		if not hooked and GameState.has_flag(&"talked_n0_traveller"):
			hooked = true
			hooked_at = elapsed
			parted = Talk.history.slice(said_before).any(func(l: Array) -> bool: return l[1] == "Suit yourself, brother.") \
				or not Talk.history.slice(said_before).any(func(l: Array) -> bool: return l == ["Traveller", "Whoa. Look at that."])
		if hooked and watched < 0.0 and elapsed - hooked_at > 1.2:
			# A moment into it his eyes are on what lies on the cart, not on the traveller.
			watched = ViewCheck.off_centre(p.camera, (cart.get_node(^"Bed/Bodies") as Node3D).global_position)
			Talk.auto_choice = answer_with
		if hooked and not paused_ok and at.x > -150.0 and at.x < -140.0:
			# Paused: the wagon, the cart and the clock wait.
			var hour_then := GameState.hour
			_flow.open_pause()
			await _frames(60)
			paused_ok = get_tree().paused and wagon.global_position.is_equal_approx(at) and GameState.hour == hour_then
			_flow.resume()
			last = wagon.global_position
		if paused_ok and not gate_talk and at.x > -132.0 and at.x < -125.0 and not Talk.talking:
			# He turns to the traveller again on the way up to Aldgate, and is
			# still talking when the wagon stops there.
			gate_talk = true
			Talk.auto_choice = func(_o: PackedStringArray) -> int: return -1
			talker.interact(p)
		if gate_talk and not Talk.history.has(GREETING):
			gate_talk_open = Talk.talking and Talk.is_choosing()
		elif gate_talk and Talk.auto_choice != answer_with and not held_talk:
			Talk.auto_choice = answer_with
			# Lines at a readable pace while the warden looks him over, so his view has time to turn.
			Talk.line_seconds = 0.6
		if Talk.line_seconds > 0.1 and GameState.has_flag(&"n0_past_aldgate"):
			Talk.line_seconds = 0.05
		if is_instance_valid(warden):
			warden_near = minf(warden_near, Vector2(warden.global_position.x - p.camera.global_position.x,
				warden.global_position.z - p.camera.global_position.z).length())
			lantern_near = minf(lantern_near, warden_lantern.global_position.distance_to(p.camera.global_position))
			if Talk.talking_to == warden:
				# Talking with the lantern up, his view goes to the warden's face.
				var off := ViewCheck.off_centre(p.camera, (warden as Figure).face_position())
				lantern_seen = off if lantern_seen < 0.0 else minf(lantern_seen, off)
			if at.x > -110.0 and not warden_back and not Talk.talking:
				warden_back = warden.global_position.distance_to(warden_home) < 0.05
		if last_step > 0.02 and at.distance_to(last) < 1.0:
			# Rolling: the bed jolts and sways over the road, and his view with it.
			jolt = maxf(jolt, absf(bed.position.y))
			sway = maxf(sway, absf(rad_to_deg(bed.rotation.z)))
			view_sway = maxf(view_sway, absf(rad_to_deg(p.look_back_pivot.rotation.z)))
		if hooked and not held_talk and at.x > -46.0 and at.z < 30.0 and not Talk.talking:
			# In the lane he turns to the traveller again, and is still talking
			# when the wagon stops.
			held_talk = true
			Talk.auto_choice = func(_o: PackedStringArray) -> int: return -1
			talker.interact(p)
		if held_talk and not walked[0] and still > 1.0 and at.z < 6.0:
			waited_at_gate = p.riding != null and Talk.talking and not GameState.has_flag(&"n0_arrived")
			Talk.auto_choice = func(o: PackedStringArray) -> int:
				if walked[0]:
					return 0
				walked[0] = true
				leave_option[0] = o[-1]
				return o.size() - 1
	var pulled_in := stops.any(func(s: Vector3) -> bool: return absf(s.x - pilot.mark("PullOver").x) < 1.5)
	# Nothing left over from the road comes between the Whoa and the cart.
	var whoa := Talk.history.find(["Traveller", "Whoa. Look at that."])
	var hook_at := Talk.history.find(["", "(The cart creaks by close enough to touch. Shapes lie under sacking on its bed, three side by side and one across them.)"])
	_check(whoa >= 0 and hook_at == whoa + 1, "after the traveller's Whoa the next thing said is the cart going by (%s)" % [Talk.history.slice(whoa, hook_at + 1)])
	_check(bodies == 4, "the cart carries four bodies under sacking (%d)" % bodies)
	_check(jolt > 0.01 and jolt < 0.12 and sway > 0.3 and sway < 5.0 and view_sway > 0.2,
		"rolling, the wagon's bed jolts (%.1f cm) and sways (%.1f°) over the road, and his view sways with it (%.1f°)" % [jolt * 100.0, sway, view_sway])
	_check(hooked and not parted and pulled_in and closest < 4.0 and closest > 2.0,
		"the carter pulls in for the body cart (stopped at %s); as it comes the traveller breaks off his talk with a Whoa, it passes close by on his side (%.1f m), and he talks about it" % [str(stops), closest])
	_check(watched >= 0.0 and watched < 8.0, "as the cart goes by his view goes to the body on it and follows it (%.1f° off)" % watched)
	_check(paused_ok, "paused, the wagon and the clock wait")
	var at_gate := stops.any(func(s: Vector3) -> bool: return absf(s.x - warden_x) < 1.5)
	var warden_spoke := Talk.history.any(func(l: Array) -> bool: return l[0] == "Warden")
	_check(at_gate and warden_spoke, "the wagon stops at Aldgate, and the warden looks them over")
	var greeted := Talk.history.find(GREETING)
	_check(gate_talk_open and greeted >= 0 and not Talk.history.slice(greeted - 3, greeted).any(func(l: Array) -> bool: return l[1].begins_with("Suit yourself")),
		"talking as the wagon stops at Aldgate, the traveller breaks off (no parting line) and greets the warden")
	_check(warden_near < 1.6 and lantern_near < 1.0 and lantern_seen >= 0.0 and lantern_seen < 8.0 and warden_back,
		"the warden walks up to him (%.2f m), holds his lantern up to his face (%.2f m, his view on the warden's face %.1f° off), and walks back to his place" % [warden_near, lantern_near, lantern_seen])
	_check(GameState.has_flag(&"talked_n0_warden") and Talk.history.has(LANTERN_LINE) and GameState.has_flag(&"n0_warden_porter") and GameState.has_flag(&"n0_past_aldgate"),
		"with the lantern up the warden talks to him (he says he's the new porter), and the wagon goes on through")
	var cues_said := Talk.history.filter(func(l: Array) -> bool: return l[0] == "Carter" or l[0] == "Traveller").size()
	_check(elapsed > 60.0 and elapsed < 150.0 and cues_said >= 8,
		"the ride takes a minute or two (%.0f s), with something said along the way (%d lines)" % [elapsed, cues_said])
	_check(dark_jump > 0.95 and absf(dark_from.x + 72.0) < 7.0 and absf(dark_from.z - 47.0) < 2.5 and moving_into_dark > 0.005 and fade.color.a < 0.05,
		"over the bridge the night goes dark with the wagon still rolling (%.2f, from %s, %.3f m a tick), and has come up again in the lane (%.2f)" % [dark_jump, str(dark_from), moving_into_dark, fade.color.a])
	_check(lane_hidden and abbey.visible and night.get_node_or_null(^"Road") == null and night.get_node_or_null(^"RoadFolk") == null,
		"the abbey and the lane aren't shown on the road, and in the lane the road and its people are gone")
	_check(waited_at_gate and leave_option[0] == Talk.TURN_AWAY, "at the gate the wagon waits until he's done talking (he turns away: %s)" % leave_option[0])
	await _until(func() -> bool: return GameState.has_flag(&"talked_n0_carter") and not Talk.talking, 30.0)
	Talk.auto_choice = answer_with
	var gate := night.get_node(^"AbbeyGate") as AbbeyGate
	_check(GameState.has_flag(&"n0_arrived") and GameState.has_flag(&"talked_n0_carter") and p.riding == null
		and p.global_position.distance_to(pilot.mark("SetDown")) < 1.0, "the carter sets him down in the lane by the gate, and has a word")
	var last_z := wagon.global_position.z if is_instance_valid(wagon) else INF
	while is_instance_valid(wagon):
		last_z = wagon.global_position.z
		await get_tree().physics_frame
	_check(last_z < -30.0, "and drives off down the lane (%.0f)" % last_z)
	await _until(func() -> bool: return pilot.beat() == &"Arrive" and not Talk.talking, 10.0)
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
