extends Node
## Night 4, Edwin (design doc, Night 4; docs/full-game-run.md, "Witnessed
## deaths", the chase rule "two hunters; one is Osric"), played in full twice:
## - the pilgrim let in and not warned: no supper (the fast), Edwin's
##   whisper and Thomas on Simon at dusk, Mab let in, Edwin missing at
##   Matins, Wulfric killed a few steps ahead in the fog and the prior
##   kneeling by him with blood on his sleeve, the guest killed in the
##   guesthouse (the lock no longer helps), Edwin in the charnel house, two
##   hunters at once and Osric's face under the mask, Simon scrubbing blood,
##   and at dawn someone has been in his cell;
## - warned at his bed to bar the door from inside: the guest lives.
## Run: tools/check.sh

const TEST_SAVE := "user://test_night4_save.tres"

var _fails := 0
var _answer := [-1, 1]


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	Talk.line_seconds = 0.05
	Talk.auto_choice = NightPilot.gate_aware_choice(_answer)

	var pilot := await _start()
	await pilot.play_night4(_answer, 0)
	_check(GameState.has_flag(&"n4_edwin_whisper") and GameState.has_flag(&"n4_thomas_simon") and GameState.has_flag(&"n4_fast"),
		"dusk: Edwin's whisper, Thomas on Simon, and no supper (the fast)")
	_check(GameState.get_flag(&"n4_mab") == &"admitted" and GameState.get_flag(&"n4_guest") == &"admitted", "Mab let in, and the pilgrim")
	_check(GameState.has_flag(&"died_edwin") and GameState.has_note(&"edwin_missing"), "Edwin missing at Matins")
	_check(GameState.has_flag(&"died_fog_brother") and GameState.has_flag(&"died_choira") and GameState.souls.has(&"fog_brother")
		and GameState.has_note(&"prior_sleeve"), "in the fog, Wulfric killed a few steps ahead; the prior kneels by him, blood on his sleeve")
	_check(GameState.has_flag(&"died_night4_guest") and GameState.souls.has(&"night4_guest") and not Saving.guest_safe(&"night4_guest", true),
		"the guest he let in is killed in the guesthouse: his lock no longer helps")
	_check(GameState.has_flag(&"found_edwin") and GameState.has_note(&"edwin_comb") and GameState.souls.has(&"edwin"),
		"Edwin, laid out in the charnel house")
	_check(GameState.has_note(&"two_demons") and GameState.has_note(&"osric_mask"), "two hunters at once; one loses his mask: Osric")
	_check(GameState.has_note(&"simon_blood") and GameState.has_flag(&"n4_simon_scrubbing"), "Simon on his knees, scrubbing blood")
	_check(GameState.has_flag(&"n4_cell_violated") and GameState.has_flag(&"night4_done"), "at dawn someone has been in his cell; he sleeps")

	_answer[1] = 0
	pilot = await _start()
	await pilot.play_night4(_answer, 0)
	_check(GameState.has_flag(&"n4_warned_night4_guest") and not GameState.has_flag(&"died_night4_guest")
		and not GameState.souls.has(&"night4_guest"), "warned to bar his door from inside, the guest lives")

	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	Talk.auto_choice = Callable()
	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


func _start() -> NightPilot:
	for c in get_children():
		c.queue_free()
	await get_tree().process_frame
	NightPilot.fresh_night(TEST_SAVE)
	GameState.night = 4
	GameState.chapter = 5
	for f: StringName in [&"bread_warned", &"keys_copied"]:
		GameState.set_flag(f)
	GameState.carried = true
	Talk.history.clear()
	var main := NightPilot.main_with("res://game/chapters/night4/night4.tscn")
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
