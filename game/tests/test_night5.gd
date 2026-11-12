extends Node
## Night 5, the granary (design doc, Night 5; docs/mechanics.md, "Saving
## people": save Simon, not Thomas; "The payoff"), played in full twice:
## - Simon saved: the masked man lets him go, Thomas turns up "wounded"
##   anyway, and Simon says Thomas sent him to scrub the blood; the
##   sergeant waits inside the gate and lives; Matins, the abbot falling and
##   Anselm's word about the key; in the grain a pilgrim's hand, the ergot
##   and the key; the doors barred behind him and two hunters, and out down
##   the latrine chute; at dawn the prior arrests him and, with too little
##   to show, Thomas takes him into his care;
## - Thomas saved: Simon's throat is cut in front of him (fed to the rite);
##   Joan, turned away on night 2, comes back, is let in, and is the hand in
##   the grain; the sergeant left in the lane is killed; with two kinds of
##   proof in his satchel the prior believes him.
## Run: tools/check.sh

const TEST_SAVE := "user://test_night5_save.tres"

var _fails := 0
var _answer := [-1, 1]


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	Talk.line_seconds = 0.05
	Talk.auto_choice = NightPilot.gate_aware_choice(_answer)

	var pilot := await _start([])
	await pilot.play_night5(_answer, &"simon", 0)
	_check(GameState.get_flag(&"n5_saved") == &"simon" and not GameState.has_flag(&"died_simon") and GameState.has_note(&"thomas_sent_simon"),
		"he reaches Simon: the masked man goes, and Simon says Thomas sent him to scrub the blood")
	_check(GameState.get_flag(&"n5_sergeant") == &"admitted" and not GameState.has_flag(&"died_sergeant") and not GameState.souls.has(&"sergeant"),
		"let wait inside the gate, the sergeant lives")
	_check(GameState.has_flag(&"n5_anselm_key"), "at Matins, in the confusion, Anselm: the key is in the granary")
	_check(GameState.get_flag(&"n5_body5") == &"pilgrim" and GameState.has_flag(&"found_body5") and GameState.souls.has(&"body5")
		and GameState.has_note(&"ergot_rye") and GameState.keys.has(&"crypt_passage"), "in the grain a pilgrim's hand, the ergot, and the key")
	_check(GameState.has_flag(&"n5_escaped"), "barred in with two hunters, he gets out down the latrine chute")
	_check(GameState.has_flag(&"thomas_custody") and not GameState.has_flag(&"prior_believes") and GameState.has_flag(&"night5_done"),
		"at dawn the prior arrests him; with too little to show, Thomas takes him into his care")

	pilot = await _start([&"n2_joan_refused_at"])
	GameState.satchel.append_array([&"mask", &"purse"])
	await pilot.play_night5(_answer, &"thomas", 1)
	_check(GameState.get_flag(&"n5_saved") == &"thomas" and GameState.has_flag(&"died_simon") and GameState.souls.has(&"simon"),
		"he reaches Thomas: Simon's throat is cut in front of him")
	_check(GameState.get_flag(&"n5_joan") == &"admitted" and GameState.get_flag(&"n5_body5") == &"joan" and GameState.has_flag(&"died_joan"),
		"Joan, turned away before, comes back and is let in; she is the hand in the grain")
	_check(GameState.has_flag(&"died_sergeant") and GameState.souls.has(&"sergeant"), "left in the lane, the sergeant is killed")
	_check(GameState.has_flag(&"prior_believes") and not GameState.has_flag(&"thomas_custody"), "with two kinds of proof, the prior believes him")

	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	Talk.auto_choice = Callable()
	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


func _start(flags: Array[StringName]) -> NightPilot:
	for c in get_children():
		c.queue_free()
	await get_tree().process_frame
	NightPilot.fresh_night(TEST_SAVE)
	GameState.night = 5
	GameState.chapter = 6
	for f: StringName in [&"bread_warned", &"keys_copied"]:
		GameState.set_flag(f)
	for f in flags:
		GameState.set_flag(f)
	GameState.carried = true
	Talk.history.clear()
	var main := NightPilot.main_with("res://game/chapters/night5/night5.tscn")
	add_child(main)
	await get_tree().process_frame
	await get_tree().process_frame
	var pilot := NightPilot.new(main.get(&"current_level"), _check)
	pilot.shorten()
	return pilot


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
