extends Node
## Night 1, the new porter (design doc, Night 1; docs/mechanics.md, "Saving
## people"), played in full twice:
## - the merchant let in and the guesthouse left unlocked: Bede's warning at
##   supper, the merchant and Walter at the gate, the first Matins with all
##   present and the incense, one glimpse on the round, the knock with no one
##   there, and at Lauds the merchant in the fishpond (found, his death fed
##   to the rite, Thomas's "drowned drunk", whom to tell);
## - let in and locked in: he lives, and leaves at first light cursing.
## Run: tools/check.sh

const TEST_SAVE := "user://test_night1_save.tres"

var _fails := 0
var _answer := [-1]


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	Talk.line_seconds = 0.05
	Talk.auto_choice = NightPilot.gate_aware_choice(_answer)

	# Unlocked: the merchant dies.
	var pilot := await _start()
	var night := pilot.night
	await pilot.play_night1(_answer, 0, false, 0)
	_check(GameState.has_flag(&"bread_warned") and GameState.has_note(&"bread_warning")
		and _said("Bede", "Something is wrong with it"), "at supper, after he has eaten, Bede warns him about the bread")
	_check(GameState.get_flag(&"n1_merchant") == &"admitted" and GameState.get_flag(&"n1_walter") == &"admitted"
		and GameState.ledger.size() == 2, "the merchant and Walter at the gate, let in and written down")
	_check(GameState.has_flag(&"n1_incense") and _said("", "All present"), "the first Matins: all present, the incense")
	_check(_said("", "horns at the far end of the walk"), "on the round, one glimpse at the end of the walk")
	_check(GameState.has_flag(&"n1_knock_no_one") and GameState.has_note(&"knock_no_one"), "the knock after midnight, with no one there")
	_check(GameState.has_flag(&"died_merchant") and GameState.souls.has(&"merchant") and not GameState.has_flag(&"n1_guesthouse_locked"),
		"left unlocked, the cult takes the merchant in the night (fed to the rite)")
	_check(GameState.has_flag(&"found_merchant") and GameState.has_note(&"merchant_rope") and _said("Thomas", "drowned drunk"),
		"at Lauds, the merchant face down in the fishpond; Thomas: drowned drunk")
	_check(GameState.get_flag(&"reported_merchant") == &"thomas", "he chooses whom to tell")
	_check(GameState.has_flag(&"night1_done") and is_instance_valid(night) == false or GameState.has_flag(&"night1_done"), "night 1 ends in sleep")

	# Locked in: he lives.
	pilot = await _start()
	await pilot.play_night1(_answer, 0, true, 1)
	_check(GameState.has_flag(&"n1_guesthouse_locked") and GameState.has_flag(&"n1_merchant_safe") and not GameState.has_flag(&"died_merchant")
		and not GameState.souls.has(&"merchant"), "locked in, the merchant lives")
	_check(_said("Merchant", "Like a sheep"), "and leaves at first light, cursing the porter for it")
	_check(GameState.get_flag(&"n1_walter") == &"refused" and GameState.get_flag(&"n1_walter_fate") == &"cross_keys",
		"Walter turned away before the curfew bell goes to the Cross Keys")

	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	Talk.auto_choice = Callable()
	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


## Night 1 on its own, as after day 1.
func _start() -> NightPilot:
	for c in get_children():
		c.queue_free()
	await get_tree().process_frame
	NightPilot.fresh_night(TEST_SAVE)
	GameState.night = 1
	GameState.chapter = 2
	# Carried on from the night before: the night's own start state isn't applied.
	GameState.carried = true
	Talk.history.clear()
	var main := NightPilot.main_with("res://game/chapters/night1/night1.tscn")
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
