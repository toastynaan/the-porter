extends Node
## Bodies and what follows them (docs/full-game-run.md, "Found bodies",
## "Moving bodies", "Reporting", "Hidden bodies"; docs/mechanics.md,
## "Investigation", "Being seen", "The payoff"), in death_demo.tscn:
## looking at a body finds it and writes a note; the cult moves a body that
## proves men did it once he leaves it, with its proof, and coming back he
## finds the place empty; whom he tells changes what follows (Thomas: +5 at
## the next dusk; the prior: +10 now and he suspects him; no one: nothing,
## or +15 if a brother saw him there); a brother who sees him somewhere he
## shouldn't be costs +10 once per place per night, and comes up at dawn;
## the prior believes him with two kinds of proof or six clues; the cult's
## book page goes in the satchel and the notes; the hidden bodies are found
## by doing the thing that finds them, only from their night.
## Run: tools/check.sh

const TEST_SAVE := "user://test_bodies_save.tres"

var _fails := 0
var _pilot: NightPilot
var _offered: Array[PackedStringArray] = []
var _pick := 0


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	NightPilot.fresh_night(TEST_SAVE)
	GameState.night = 4
	Talk.line_seconds = 0.05
	Talk.auto_choice = func(options: PackedStringArray) -> int:
		_offered.append(options)
		return _pick
	var main := NightPilot.main_with("res://game/encounters/death_demo.tscn")
	add_child(main)
	_pilot = NightPilot.new(main.get(&"current_level"), _check)
	await _pilot.frames(5)
	var night := _pilot.night
	var p := _pilot.player
	# The brothers stay out of this, but for the one placed to see him.
	for b: Brother in get_tree().get_nodes_in_group(&"brothers"):
		b.place(null)

	# Finding: look at the body for a moment.
	var pond: FoundBody = night.get_node(^"Bodies/Pond")
	BloodMarks.add(get_tree(), &"drag", Transform3D(Basis.IDENTITY, pond.global_position + Vector3(1, 0, -2)), &"demo_pond")
	BloodMarks.add(get_tree(), &"pool", Transform3D(Basis.IDENTITY, pond.global_position + Vector3(0, 0, -0.6)), &"demo_pond")
	await _pilot.seconds(1.0)
	p.place(pond.global_position + Vector3(0, 0, -3.0), PI)
	_pilot.face(pond.body.call(&"centre") as Vector3)
	await _pilot.seconds(1.0)
	_check(pond.is_found and GameState.has_flag(&"found_demo_pond") and GameState.has_note(&"merchant_rope"),
		"looking at the body finds it, and he notes the rope marks")
	_check(Talk.history.any(func(h: Array) -> bool: return String(h[1]).contains("Rope marks")), "he says what he sees")

	# Moving: he leaves to fetch someone; it's gone, with its drag marks.
	p.place(pond.global_position + Vector3(-28, 0, 0), PI * 0.5)
	await _pilot.seconds(1.6)
	_check(pond.is_moved and pond.body == null and GameState.has_flag(&"moved_demo_pond"), "he leaves it: the cult moves the body")
	_check(BloodMarks.count(&"drag") == 0 and BloodMarks.count(&"pool") == 1, "and its drag marks with it; the pool is missed")
	p.place(pond.global_position + Vector3(0, 0, -3.0), PI)
	await _pilot.seconds(0.5)
	_check(GameState.has_note(&"merchant_moved"), "coming back, it's gone, and he writes that down")

	# Reporting.
	GameState.suspicion = 0
	_pick = 0
	var to: StringName = await Report.ask(&"demo_pond", "the merchant in the pond")
	_check(to == &"thomas" and GameState.get_flag(&"reported_demo_pond") == &"thomas" and GameState.suspicion == 0
		and _offered[-1][0] == "Tell Brother Thomas about the merchant in the pond", "told Thomas: safe now")
	Report.at_dusk()
	_check(GameState.suspicion == Report.THOMAS_LATER, "dangerous later: +5 at the next dusk (%d)" % GameState.suspicion)
	Report.at_dusk()
	_check(GameState.suspicion == Report.THOMAS_LATER, "only once")
	GameState.suspicion = 0
	Report.apply(&"body_b", &"prior")
	_check(GameState.suspicion == 10 and GameState.has_flag(&"hugh_suspects"), "told the prior: +10 now, and he suspects him")
	GameState.suspicion = 0
	Report.apply(&"body_c", &"none")
	_check(GameState.suspicion == 0, "told no one, unseen: nothing")
	GameState.set_flag(SeenWatch.flag(&"near_body_d"), &"Osric")
	Report.apply(&"body_d", &"none")
	_check(GameState.suspicion == 15, "told no one, but seen by it: +15")

	# Being seen in the crypt by the prior.
	GameState.suspicion = 0
	var hugh: Brother = night.get_node(^"Brothers/Hugh")
	p.place(Vector3(20.0, -3.95, -32.0), deg_to_rad(90.0))
	hugh.place(Transform3D(Basis(Vector3.UP, deg_to_rad(-90.0)), Vector3(14.0, -3.95, -32.0)))
	await _pilot.seconds(0.6)
	_check(GameState.suspicion == 10 and GameState.get_flag(&"n4_seen_crypt") == &"Hugh", "the prior sees him in the crypt: +10")
	await _pilot.seconds(0.6)
	_check(GameState.suspicion == 10, "once per place per night")
	_check(Array(SeenWatch.remarks()).any(func(r: String) -> bool: return r.begins_with("Prior Hugh saw you in the crypt")),
		"it comes up at dawn: %s" % [SeenWatch.remarks()])
	# The granary counts only after Compline.
	p.place(Vector3(-16.0, 0.05, -10.0), PI)
	hugh.place(Transform3D(Basis.IDENTITY, Vector3(-16.0, 0.05, -4.0)))
	GameState.hour = 18.0
	await _pilot.seconds(0.6)
	_check(GameState.suspicion == 10, "in the stores before Compline: nothing")
	GameState.hour = 21.0
	await _pilot.seconds(0.6)
	_check(GameState.suspicion == 20 and GameState.has_flag(&"n4_seen_granary"), "after Compline: +10")
	hugh.place(null)

	# The prior's judgement.
	GameState.satchel.assign([&"mask"])
	for clue: StringName in [&"merchant_rope", &"merchant_moved", &"bread_warning", &"sailor_knot"]:
		GameState.note(clue)
	_check(not PriorJudgement.believes(), "one kind of proof and %d clues: not enough" % Clues.written())
	GameState.satchel.append(&"hoof_soles")
	_check(not PriorJudgement.believes(), "two costume pieces are one kind: still not")
	GameState.satchel.append(&"purse")
	_check(PriorJudgement.believes(), "a costume and a purse: two kinds, he believes him")
	GameState.satchel.clear()
	GameState.note(&"ledger_torn")
	_check(Clues.written() == 5 and not PriorJudgement.believes(), "five clues: not enough")
	GameState.note(&"oven_badge")
	_check(PriorJudgement.believes(), "six clues: he believes him")

	# The cult's book.
	var page: Readable = night.get_node(^"BookPage")
	page.interact(p)
	await _pilot.frames(2)
	var view: PageView = main.get_node(^"UI/Page")
	_check(view.showing and GameState.satchel.has(&"book_page") and GameState.has_note(&"crypt_book") and not page.visible,
		"the book's page: he reads it and takes it")
	view.set_showing(false)

	# Hidden bodies, from their nights.
	var well: HiddenBody = night.get_node(^"HiddenBodies/Well")
	var chapter: HiddenBody = night.get_node(^"HiddenBodies/ChapterFlag")
	_check(well.available() and not chapter.available(), "on night 4 the well's body is there, the chapter house's not yet")
	(night.get_node(^"Well") as Well).interact(p)
	await _pilot.until(func() -> bool: return well.is_found, 4.0)
	_check(well.is_found and GameState.has_note(&"well_badge"), "drawing water: the bucket comes up heavy")
	var dose := GameState.dose
	(night.get_node(^"Well") as Well).interact(p)
	await _pilot.seconds(3.5)
	_check(GameState.dose > dose + 4.5, "after that it's water to drink, and from night 4 the cult doses it (+5)")
	var culvert: HiddenBody = night.get_node(^"HiddenBodies/RaceCulvert")
	p.place(Vector3(31.4, -1.15, 18.0), deg_to_rad(-90.0))
	await _pilot.until(func() -> bool: return culvert.is_found, 3.0)
	_check(culvert.is_found and culvert.body is Corpse and GameState.has_note(&"race_badge"), "wading the culvert, he finds a body")

	# The count adds up: six always come, five can be stopped.
	GameState.count = 0
	GameState.souls.clear()
	for id in Rite.always():
		GameState.feed_rite(id)
	_check(Rite.always().size() == 6 and Rite.stoppable().size() == 5 and GameState.count == 6,
		"six deaths always come, five can be stopped")
	var saved_three := Rite.stoppable().slice(0, 2)
	for id in saved_three:
		GameState.feed_rite(id)
	_check(GameState.count == 8 and Rite.strength(GameState.count) == Rite.Strength.SHADOW,
		"save three of the five: 8, the Saint a shadow in the crypt")
	GameState.feed_rite(Rite.stoppable()[2])
	_check(Rite.strength(GameState.count) == Rite.Strength.WALKS, "9: it walks")
	for id in Rite.stoppable():
		GameState.feed_rite(id)
	GameState.feed_rite(Rite.always()[0])
	_check(GameState.count == 11 and Rite.strength(GameState.count) == Rite.Strength.HUNTS,
		"save none: 11, it hunts (a soul fed twice counts once)")
	_check(Rite.last_victim() == &"simon", "Simon alive: he is the last victim")
	GameState.set_flag(&"died_simon")
	_check(Rite.last_victim() == &"pilgrim", "Simon dead: a pilgrim")

	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	Talk.auto_choice = Callable()
	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
