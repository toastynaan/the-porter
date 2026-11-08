extends Node
## Night 2, the bell (design doc, Night 2; docs/full-game-run.md, "Witnessed
## deaths"; docs/mechanics.md, "Saving people"), played in full three times:
## - after the merchant died: Thomas's word about the prior at supper (he
##   missed him at dusk); Joan, Roger (asking after the merchant) and the
##   sailor at the gate; the sailor turned away after the curfew bell dies
##   in the lane, seen through the grille, and Gib's call stops; the heavy
##   rope and Bede hanging (a sailor's knot); the count one short; at dawn
##   the abbot's demon and the prior's question;
## - the sailor let in: Jankin, put out of the Keys, is the one killed; on
##   the round the sailor's bed is empty and his page torn from the ledger;
## - the sailor let in and Hob asked to keep Jankin in: no one dies in the
##   lane. Roger doesn't come when the merchant lived.
## Run: tools/check.sh

const TEST_SAVE := "user://test_night2_save.tres"

var _fails := 0
var _answer := [-1]


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	Talk.line_seconds = 0.05
	Talk.auto_choice = NightPilot.gate_aware_choice(_answer)

	# The sailor turned away after the bell.
	var pilot := await _start([&"died_merchant"])
	var lane_played := [false]
	(pilot.night.get_node(^"LaneDeath") as DeathScene).played.connect(func() -> void: lane_played[0] = true)
	await pilot.play_night2(_answer, 0, 1, 1)
	_check(_said("Thomas", "the prior about the house at night") and GameState.has_flag(&"n2_supper_aside"),
		"missed at dusk, Thomas tells him at supper he has seen the prior about at night")
	_check(GameState.get_flag(&"n2_joan") == &"admitted" and GameState.get_flag(&"n2_roger") == &"refused"
		and GameState.get_flag(&"n2_sailor") == &"refused" and GameState.get_flag(&"n2_sailor_fate") == &"lane",
		"Joan let in; Roger, asking after the merchant, and the sailor turned away after the bell")
	_check(GameState.has_flag(&"died_lane_death") and GameState.has_flag(&"died_sailor") and GameState.has_flag(&"lane_death_was_turned_away")
		and GameState.souls.has(&"lane_death") and lane_played[0],
		"turned away after the bell, the sailor is killed in the lane under the lantern (fed to the rite)")
	_check(GameState.has_flag(&"n2_watch_silent") and _said("", "Gib's call. It doesn't come"), "Gib's call doesn't come")
	_check(GameState.has_flag(&"found_bell_brother") and GameState.souls.has(&"bell_brother") and GameState.has_note(&"sailor_knot")
		and _said("", "Brother Bede, turning slowly"), "the rope is heavy: Bede drops past him, hanged with a sailor's knot")
	_check(_said("", "One short"), "the count is one short")
	_check(_said("", "Every bed as you left it") and not GameState.has_flag(&"n2_empty_bed"), "the guesthouse as he left it")
	_check(_said("Godric", "A demon has come into this house") and GameState.has_flag(&"n2_told_hugh"),
		"at dawn the abbot declares the demon, and the prior asks where he was")
	_check(GameState.get_flag(&"reported_bell_brother") == &"thomas" and GameState.has_flag(&"night2_done"), "whom to tell; night 2 ends in sleep")

	# The sailor let in: Jankin dies; an empty bed and a torn page.
	pilot = await _start([])
	await pilot.play_night2(_answer, 0, 0)
	_check(not GameState.has_flag(&"n2_roger"), "the merchant lived: Roger doesn't come")
	_check(GameState.has_flag(&"died_jankin") and GameState.has_flag(&"died_lane_death") and not GameState.has_flag(&"lane_death_was_turned_away"),
		"no one turned away after the bell: Jankin, put out of the Keys, is the one killed")
	_check(GameState.has_flag(&"n2_empty_bed") and GameState.has_note(&"ledger_torn")
		and not GameState.ledger.any(func(e: Dictionary) -> bool: return String(e["name"]).contains("Cobb") or String(e["name"]).to_lower().contains("sailor")),
		"on the round the sailor's bed is empty, and his page is torn from the ledger")

	# Hob kept Jankin in: no one dies in the lane.
	pilot = await _start([&"n2_jankin_kept_in"])
	await pilot.play_night2(_answer, 1, 0)
	_check(GameState.has_flag(&"n2_lane_quiet") and not GameState.has_flag(&"died_lane_death") and not GameState.souls.has(&"lane_death")
		and not GameState.has_flag(&"died_jankin"), "Hob kept Jankin in, and no one was turned away after the bell: no one dies in the lane")
	_check(GameState.get_flag(&"n2_joan_fate") == &"cross_keys", "Joan turned away before the bell goes to the Cross Keys")

	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	Talk.auto_choice = Callable()
	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


## Night 2 on its own, after night 1, with `flags`.
func _start(flags: Array[StringName]) -> NightPilot:
	for c in get_children():
		c.queue_free()
	await get_tree().process_frame
	NightPilot.fresh_night(TEST_SAVE)
	GameState.night = 2
	GameState.chapter = 3
	GameState.set_flag(&"bread_warned")
	for f in flags:
		GameState.set_flag(f)
	# Carried on from the night before: the night's own start state isn't applied.
	GameState.carried = true
	Talk.history.clear()
	var main := NightPilot.main_with("res://game/nights/night2.tscn")
	add_child(main)
	await get_tree().process_frame
	await get_tree().process_frame
	var pilot := NightPilot.new(main.get(&"current_level"), _check)
	pilot.shorten()
	return pilot


func _said(who: String, words: String) -> bool:
	return Talk.history.any(func(h: Array) -> bool: return h[0] == who and String(h[1]).contains(words))


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
