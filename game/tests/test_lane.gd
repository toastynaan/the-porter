extends Node
## The lane and the squints (docs/mechanics.md, "The lane at dusk", "Peeking",
## "The squint scare", "Drinking" and "Tests"), in night_base's furniture:
## - the lane's dusk talk reads the flags: what happened the night before is
##   what they talk about (Hob on night 2: the merchant dead in the fishpond,
##   or alive and cursing the porter who locked him in);
## - the curfew bell at nine empties the lane (its people go home), shuts the
##   Cross Keys and the windows go dark through the next hour; then Gib calls
##   the hour on the hour, until something silences him;
## - E at a squint puts his eye to the bars from either side, the view held
##   within 25°; a hunter can't see him through it except up close with a
##   light;
## - the squint scare: night 0, after curfew, alone by the south squint; a
##   shape stands inside, and is gone once he has looked away; only once,
##   and never before the bell;
## - drink: +1 an ale to 5, a softer focus, a double image from 3, a drift,
##   1 lost an hour, cleared by sleep, and a headache the morning after 3.
## Run: tools/check.sh

const TEST_SAVE := "user://test_lane_save.tres"

var _fails := 0
var _pilot: NightPilot


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	NightPilot.fresh_night(TEST_SAVE)
	GameState.night = 0
	Talk.line_seconds = 0.05
	var main := NightPilot.main_with("res://game/encounters/death_demo.tscn")
	add_child(main)
	_pilot = NightPilot.new(main.get(&"current_level"), _check)
	await _pilot.frames(5)
	var night := _pilot.night
	var p := _pilot.player
	(night.get_node(^"Hallucinations") as Hallucinations).active = false
	for b: Brother in get_tree().get_nodes_in_group(&"brothers"):
		b.place(null)
	var curfew: Curfew = night.get_node(^"Curfew")
	var inn_door: Door = night.get_node(^"Abbey/Street/Houses/Inn/Door")

	# The dusk talk reads the flags.
	var hob: VisitorNPC = night.get_node(^"People/Hob")
	var hob_talk := (hob.get_node(^"Talker") as Talker).conversation
	_check(hob_talk != null and hob_talk.id == &"lane_hob", "Hob talks at dusk (%s)" % [hob_talk.id if hob_talk else &""])
	Talk.auto_choice = func(o: PackedStringArray) -> int: return o.size() - 1
	GameState.night = 2
	GameState.set_flag(&"died_merchant")
	p.place(hob.global_position + Vector3(1.3, 0.0, 0.0), deg_to_rad(90.0))
	await Talk.converse(hob_talk, hob)
	_check(_said("Hob", "fishpond") and not _said("Hob", "like a sheep"), "night 2, the merchant dead: Hob has heard he was in the fishpond")
	for f: StringName in [&"died_merchant", hob_talk.talked_flag(), &"lane_hob_2", &"drank"]:
		GameState.flags.erase(f)
	GameState.drink = 0.0
	Talk.history.clear()
	GameState.set_flag(&"n1_merchant", &"admitted")
	GameState.set_flag(&"n1_guesthouse_locked")
	await Talk.converse(hob_talk, hob)
	_check(_said("Hob", "like a sheep") and not _said("Hob", "fishpond"), "locked in and alive: Hob has heard him cursing the porter")
	Talk.auto_choice = Callable()
	GameState.night = 0
	GameState.drink = 0.0

	# Drink.
	GameState.hour = 18.0
	_check(DoseDriver.drink_blur() == 0.0 and DoseDriver.drunk_amount() == 0.0, "sober: a clear eye")
	GameState.have_a_drink()
	_check(DoseDriver.drink_blur() > 0.5 and DoseDriver.drunk_amount() == 0.0, "an ale: a softer focus, no double image")
	GameState.have_a_drink()
	GameState.have_a_drink()
	_check(DoseDriver.drunk_amount() > 0.3, "three: the double image")
	for i in 4:
		GameState.have_a_drink()
	_check(GameState.drink == 5.0, "five at most (%.0f)" % GameState.drink)
	var mat := (main.get_node(^"Screen") as CanvasItem).material as ShaderMaterial
	await _pilot.frames(2)
	_check(float(mat.get_shader_parameter(&"drunk")) > 0.9 and float(mat.get_shader_parameter(&"palette_shift")) == 0.0,
		"drunk, the image doubles, with no drugged colour")
	await _pilot.frames(2)
	_check(absf(p.look_back_pivot.rotation.z) > 0.0, "and his view drifts")
	GameState.seconds_per_hour = 1.0
	await _pilot.seconds(2.0)
	GameState.seconds_per_hour = 0.0
	_check(absf(GameState.drink - 3.0) < 0.1, "he loses one an hour (%.2f)" % GameState.drink)
	GameState.hour = 18.0

	# The squint: peeking from inside, the cell's.
	var cell: Squint = night.get_node(^"Squints/Cell")
	p.place(cell.global_position + Vector3(1.2, -1.55, 0.0), deg_to_rad(90.0))
	cell.interact(p)
	await _pilot.seconds(1.0)
	_check(p.peeking == cell and p.camera.global_position.distance_to(cell.global_position) < 0.6,
		"E at the cell's squint: his eye to the bars")
	var yaw := p.rotation.y
	p.call(&"_look", Vector2(1.5, 0.0))
	_check(absf(rad_to_deg(wrapf(p.rotation.y - yaw, -PI, PI))) <= Squint.PEEK_LOOK + 0.5, "he can look about only 25°")
	_check(-p.camera.global_basis.z.x < -0.9, "looking out into the lane")
	var hunter := (load("res://game/hunter/hunter.tscn") as PackedScene).instantiate() as Hunter
	hunter.dormant = true
	night.add_child(hunter)
	await _pilot.frames(2)
	hunter.global_transform = Transform3D(Basis(Vector3.UP, deg_to_rad(-90.0)), cell.global_position + Vector3(-6.0, -1.55, 0.0))
	_check(not hunter.senses.can_see(p), "a hunter in the lane 6 m off can't see him at the squint")
	hunter.global_transform = Transform3D(Basis(Vector3.UP, deg_to_rad(-90.0)), cell.global_position + Vector3(-2.0, -1.55, 0.0))
	_check(hunter.senses.can_see(p), "up close, with his light, he can")
	hunter.queue_free()
	p.stop_peeking()
	await _pilot.seconds(1.0)
	_check(p.peeking == null and not p.busy(), "E again: he steps back")

	# Before the bell, nothing at the south squint.
	var scare: SquintScare = night.get_node_or_null(^"SquintScare")
	var south: Squint = night.get_node(^"Squints/CourtSouth")
	if scare == null:
		scare = SquintScare.new()
		scare.squint = south
		var stand := Marker3D.new()
		night.add_child(stand)
		stand.global_transform = Transform3D(Basis(Vector3.UP, deg_to_rad(90.0)), south.global_position + Vector3(2.6, -1.55, 0.0))
		scare.stand = stand
		night.add_child(scare)
	var gib: VisitorNPC = night.get_node(^"People/Gib")
	gib.set_present(false)
	for n: Node in get_tree().get_nodes_in_group(&"lane_people"):
		(n as Node3D).visible = false
	GameState.hour = 20.0
	await _pass_squint(p, south)
	_check(scare.figure == null and not GameState.has_flag(&"n0_squint_scare"), "before the curfew bell: nothing at the squint")

	# The curfew bell.
	for n: Node in get_tree().get_nodes_in_group(&"lane_people"):
		(n as Node3D).visible = true
	gib.set_present(true, Transform3D(Basis.IDENTITY, Vector3(-43.4, 0.05, 20.0)))
	var kit: VisitorNPC = night.get_node(^"People/Kit")
	var lit_before := _lit_houses(night)
	GameState.hour = 21.0
	await _pilot.frames(3)
	_check(curfew.has_rung and GameState.has_flag(&"n0_curfew"), "nine: the curfew bell")
	_check(not inn_door.is_open, "the Cross Keys shuts")
	await _pilot.until(func() -> bool: return not kit.visible, 30.0)
	_check(not kit.visible and curfew.lane_empty(), "the lane empties: its people go home")
	GameState.hour = 21.5
	await _pilot.frames(3)
	var half := _lit_houses(night)
	GameState.hour = 22.05
	await _pilot.frames(3)
	_check(lit_before > 0 and half < lit_before and _lit_houses(night) == 0, "windows go dark one by one (%d, %d, %d)" % [lit_before, half, _lit_houses(night)])
	_check(curfew.calls == [22] and Talk.history.any(func(h: Array) -> bool: return h[0] == "Gib" and String(h[1]).contains("Ten of the clock")),
		"ten: Gib calls the hour from the lane")
	curfew.silence()
	GameState.hour = 23.05
	await _pilot.frames(3)
	_check(curfew.calls == [22], "silenced, his calls stop")

	# The squint scare: after the bell, alone, once.
	await _pass_squint(p, south)
	_check(scare.figure != null and scare.seen, "after the bell, alone at the south squint: a shape stands inside")
	p.place(p.global_position + Vector3(-1.0, 0, 0), deg_to_rad(0.0))
	await _pilot.seconds(0.4)
	_check(scare.figure == null and GameState.has_flag(&"n0_squint_scare"), "he looks away: it's gone")
	await _pass_squint(p, south)
	_check(scare.figure == null, "and it never comes again")

	# Sleep clears the drink; three or more and he wakes with a headache.
	GameState.drink = 3.0
	var beat := NightBeat.new()
	night.add_child(beat)
	await beat.sleep_through_the_day(0.5, "")
	_check(GameState.drink == 0.0 and GameState.has_flag(&"hangover"), "sleep clears the drink; three or more, a headache")
	GameState.hour = 9.0
	_check(DoseDriver.drink_blur() > 0.8, "the morning after: a headache blur")
	GameState.hour = 12.5
	_check(DoseDriver.drink_blur() == 0.0, "gone by noon")

	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


func _said(who: String, words: String) -> bool:
	return Talk.history.any(func(h: Array) -> bool: return h[0] == who and String(h[1]).contains(words))


## Walks up the lane past the squint outside, then looks into it.
func _pass_squint(p: Player, squint: Squint) -> void:
	p.place(squint.global_position + Vector3(-1.4, -1.55, 0.0), 0.0)
	await _pilot.frames(3)
	_pilot.face(squint.global_position)
	await _pilot.seconds(0.6)


func _lit_houses(night: Node) -> int:
	return night.get_node(^"Abbey/Street/Houses").get_children().filter(func(h: Node) -> bool:
		return h is TimberHouse and not (h as TimberHouse).lit_windows.is_empty()).size()


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
