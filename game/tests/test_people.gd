extends Node
## The abbey's people (docs/mechanics.md, "People", "Routines", "Trust",
## "Warnings", "Companions", "Lies", "Saving people", "Reading the hidden
## numbers", "Time and duties" and "Tests"), in night 3:
## - routines walk by the hour, in view: Osric to the granary door at nine,
##   locking it, then off to bed out of sight; Thomas to the infirmary, his
##   window lit;
## - greetings follow trust (warm, plain, cold), lines gated on trust 30;
##   answers and gifts move it;
## - from Suspicion 30 the talk stops when he comes near, and someone watches
##   him at supper; at 85 the brothers won't speak to him at all;
## - a warning: a guest's costs nothing unheard; overheard by Ranulf, +15; a
##   brother who doesn't trust him tells Thomas, +15; a warned guest lives;
## - the rules for saving people, and the lane's talk the next dusk;
## - a companion follows, waits, hides when he hides, and is gone if caught;
##   someone who distrusts him won't come;
## - a lie at the gate, noticed, goes in his notes;
## - lateness: noticed at 15 minutes (+5), fetched at 45 (Cole walks to him).
## Run: tools/check.sh

const TEST_SAVE := "user://test_people_save.tres"
const GREETING := """== start
Thomas: Brother.
-> topics

== start_warm
Thomas: Alric! Sit with me a moment.
-> topics

== start_cold
Thomas: (He looks past you.)
-> topics

== topics
* [if trust 30] Ask what he's noticed. -> more
* Leave him. -> end

== more
Thomas: The prior walks the cloister at night. I don't know why. [set heard_more]
"""

var _fails := 0
var _pilot: NightPilot
var _pick := [0]


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	NightPilot.fresh_night(TEST_SAVE)
	Talk.line_seconds = 0.05
	Talk.auto_choice = func(_o: PackedStringArray) -> int: return _pick[0]
	var main := NightPilot.main_with("res://game/chapters/night3/night3.tscn")
	add_child(main)
	_pilot = NightPilot.new(main.get(&"current_level"), _check)
	_pilot.shorten()
	await _pilot.frames(5)
	var night := _pilot.night
	var p := _pilot.player
	(night.get_node(^"Hallucinations") as Hallucinations).active = false
	await _pilot.until(func() -> bool: return not p.controls_locked, 5.0)

	# Greetings follow trust.
	var talk := Conversation.new()
	talk.id = &"test_greeting"
	talk.text = GREETING
	_check(talk.errors().is_empty(), "the greeting script reads (%s)" % [talk.errors()])
	_check(talk.start(false, &"thomas") == "start_warm", "Thomas trusts him (40): a warm greeting")
	GameState.trust[&"thomas"] = 10
	_check(talk.start(false, &"thomas") == "start", "at 10, plain")
	GameState.trust[&"thomas"] = -20
	_check(talk.start(false, &"thomas") == "start_cold", "below 0, cold")
	Conversation.partner = &"thomas"
	GameState.trust[&"thomas"] = 25
	var topics := talk.point("topics")
	_check(talk.offered(topics).size() == 1, "below 30 he tells him nothing more")
	GameState.trust[&"thomas"] = 35
	_check(talk.offered(topics).size() == 2, "at 30 and over, he tells him more")
	Conversation.apply(PackedStringArray(["trust thomas 5"]))
	_check(GameState.trust_of(&"thomas") == 40, "an answer moves trust (+5)")

	# The talk stops at Suspicion 30.
	var murmur: Murmur = night.get_node(^"Murmur")
	p.place(murmur.global_position + Vector3(5.0, -1.45, 0.0), deg_to_rad(90.0))
	await _pilot.frames(3)
	_check(murmur.talking, "two brothers talk low on the south walk")
	GameState.suspicion = 30
	await _pilot.frames(3)
	_check(not murmur.talking, "at Suspicion 30 they fall silent when he comes")
	var choir_a: Brother = night.get_node(^"Brothers/ChoirA")
	var to := p.global_position - choir_a.global_position
	_check(absf(wrapf(choir_a.rotation.y - atan2(-to.x, -to.z), -PI, PI)) < 0.2, "and look at him")
	GameState.suspicion = 85
	var talker: Talker = night.get_node(^"Brothers/Edwin/Talker")
	var said := Talk.history.size()
	talker.interact(p)
	await _pilot.frames(3)
	_check(not Talk.talking and Talk.history.slice(said).any(func(h: Array) -> bool: return String(h[1]).contains("turns away")),
		"at 85 the brothers won't speak to him")
	GameState.suspicion = 0

	# Warnings.
	var ranulf: Brother = night.get_node(^"Brothers/Ranulf")
	ranulf.place(null)
	GameState.suspicion = 0
	Warnings.give(&"merchant")
	_check(Warnings.warned(&"merchant") and GameState.suspicion == 0, "a guest warned, unheard: it costs nothing")
	ranulf.place(Transform3D(Basis.IDENTITY, p.global_position + Vector3(3.0, 0, 0)))
	Warnings.give(&"pilgrim")
	_check(GameState.suspicion == Warnings.OVERHEARD, "with Ranulf in earshot: +15")
	ranulf.place(null)
	GameState.suspicion = 0
	GameState.trust[&"choira"] = 10
	Warnings.give(&"choira")
	_check(GameState.suspicion == Warnings.OVERHEARD, "a brother who doesn't trust him takes it to Thomas: +15")

	# The rules for saving people.
	GameState.night = 2
	_check(Saving.guest_safe(&"guest", true) and not Saving.guest_safe(&"guest", false), "nights 1-3: locked in, a guest lives")
	GameState.night = 4
	_check(not Saving.guest_safe(&"guest", true), "night 4: the lock no longer helps")
	var keep := GameState.suspicion
	Warnings.give(&"merchant")
	GameState.suspicion = keep
	_check(Saving.guest_safe(&"merchant", false), "a guest warned to bar the door lives")
	GameState.night = 3
	_check(Saving.turned_away_fate(20.5) == &"cross_keys" and Saving.turned_away_fate(21.2) == &"lane",
		"turned away before the curfew bell, to the Cross Keys; after it, the lane")
	GameState.set_flag(&"died_merchant")
	var rumours := Rumours.tonight()
	_check(rumours.any(func(r: Array) -> bool: return r[0] == &"hob" and String(r[1]).contains("lock his guests")),
		"the next dusk Hob says what would have saved the merchant")
	GameState.flags.erase(&"died_merchant")

	# Lies at the gate.
	var v := Visitor.new()
	v.id = &"sailor"
	v.ledger_name = "A sailor"
	var d := VisitorDetail.new()
	d.part = &"hands"
	d.line = "(His hands are soft and clean.)"
	d.lie = "no tar on a sailor's hands"
	var knocks := _pilot.director().get_node(^"Knocks")
	await knocks.call(&"_notice", v, d)
	_check(GameState.has_note(&"lie_sailor_hands") and Talk.history.any(func(h: Array) -> bool: return String(h[1]) == "(Something doesn't fit: no tar on a sailor's hands.)"),
		"something doesn't fit: it goes in his notes")

	# A companion.
	var mab: VisitorNPC = night.get_node(^"People/Mab")
	var companion := Companion.new()
	companion.name = "Companion"
	companion.who = &"mab"
	mab.add_child(companion)
	await _pilot.frames(2)
	GameState.trust[&"mab"] = -10
	_check(not companion.set_following(true), "Mab, who distrusts him, won't come")
	GameState.trust[&"mab"] = 10
	p.place(Vector3(-36.0, 0.05, 2.0), deg_to_rad(90.0))
	_check(companion.set_following(true), "Mab follows him")
	p.place(Vector3(-30.0, 0.05, 2.0), deg_to_rad(90.0))
	await _pilot.seconds(5.0)
	_check(mab.global_position.distance_to(p.global_position) < 2.6, "a few steps behind (%.1f m)" % mab.global_position.distance_to(p.global_position))
	var woodpile: HidingSpot = night.get_node(^"Abbey/Navigation/OuterCourt/HidingSpots/Woodpile")
	p.place(woodpile.exit.global_position, 0.0)
	await _pilot.seconds(2.0)
	p.hide_in(woodpile)
	await _pilot.frames(3)
	_check(companion.hidden_in != null or companion.crouched, "he hides: she hides too (%s)" % ("a spot" if companion.hidden_in else "crouched"))
	p.leave_hiding(true)
	await _pilot.frames(3)
	_check(companion.hidden_in == null and not companion.crouched and mab.visible, "he comes out: so does she")
	companion.set_following(false)
	await _pilot.seconds(0.5)
	var where := mab.global_position
	p.place(Vector3(-24.0, 0.05, 8.0), 0.0)
	await _pilot.seconds(2.0)
	_check(mab.global_position.distance_to(where) < 0.2, "told to wait, she waits")
	var hunter: Hunter = night.get_node(^"Hunter")
	hunter.global_position = mab.global_position + Vector3(0.6, 0, 0)
	hunter.call(&"_set_dormant", false)
	hunter.call(&"_set_state", Hunter.State.SEARCH)
	hunter.waiting = true
	await _pilot.frames(3)
	_check(companion.is_caught and not mab.visible and GameState.has_flag(&"died_mab"), "a hunter gets his hands on her: she's gone")
	hunter.reset()

	# Lateness at supper: noticed at 15 minutes, fetched by Cole at 45.
	GameState.suspicion = 0
	_pilot.skip_to(17.25)
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Supper", 5.0)
	p.place(Vector3(-30.0, 0.05, 6.0), 0.0)
	_pilot.skip_to(17.55)
	await _pilot.frames(3)
	_check(GameState.get_flag(&"n3_late_supper") == &"noticed" and GameState.suspicion == 5, "15 minutes late: noticed, +5")
	_pilot.skip_to(18.05)
	await _pilot.until(func() -> bool: return GameState.has_flag(&"n3_fetched_by_cole"), 20.0)
	var cole := get_tree().get_nodes_in_group(&"fetchers")
	_check(GameState.get_flag(&"n3_late_supper") == &"fetched" and GameState.has_flag(&"n3_fetched_by_cole") and not cole.is_empty()
		and (cole[0] as Node3D).global_position.distance_to(p.global_position) < 3.0, "45 minutes late: Cole walks over to fetch him")

	# Routines, by the hour, in view.
	var osric: Brother = night.get_node(^"Brothers/Osric")
	var granary_door: Door = night.get_node(^"Abbey/Navigation/Cellar/Doors/WestE0Door_01")
	GameState.set_phase(GameState.Phase.KNOCKS)
	GameState.hour = 21.0
	p.place(Vector3(-6.0, 0.05, -20.0), deg_to_rad(90.0))
	await _pilot.frames(3)
	var start := osric.global_position
	await _pilot.seconds(3.0)
	_check(osric.visible and osric.walking and osric.global_position.distance_to(start) > 2.0, "nine o'clock: Osric walks to the granary door, in view")
	await _pilot.until(func() -> bool: return not osric.walking, 60.0)
	_check(osric.global_position.distance_to(Vector3(-11, 0.05, -22)) < 0.6 and granary_door.locked, "and locks it")
	var thomas: Brother = night.get_node(^"Brothers/Thomas")
	await _pilot.until(func() -> bool: return not thomas.walking, 90.0)
	_check((night.get_node(^"RoutineLights/Infirmary") as Candle).lit, "Thomas at his herbs in the infirmary: his window lit")
	GameState.hour = 21.6
	p.place(Vector3(-30.0, 0.05, 6.0), 0.0)
	await _pilot.until(func() -> bool: return not osric.visible, 60.0)
	_check(not osric.visible, "then off to bed, out of sight")

	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	Talk.auto_choice = Callable()
	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
