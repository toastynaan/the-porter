extends Node
## The game's frame (docs/full-game-run.md, M8 and "Done when" 1), through
## main.tscn from the title screen: New Game plays night 0, day 1 and nights
## 1 to 6 in order, each opened by its chapter card (night 0 to night 5 are
## played in full; night 6, a stub, wakes and sleeps), with Dose halved by each day's sleep
## and the rest carried over, and the night's own flags cleared. Night 6
## ends in the chronicle, then the title, where chapter select is open and
## there is nothing left to continue. Chapter select starts a night with its
## typical state. Pause stops the night. Death goes back to the latest save,
## quiet or bell; Continue picks up at the last bell.
## Run: tools/check.sh

const TEST_SAVE := "user://test_flow_save.tres"
const TEST_SETTINGS := "user://test_flow_settings.cfg"

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
	Talk.auto_choice = NightPilot.gate_aware_choice(_answer)
	_main = load("res://game/render/main.tscn").instantiate()
	add_child(_main)
	_flow = _main.get_node(^"Game")
	_flow.card.seconds = 0.3
	_flow.chronicle.seconds = 0.5
	await _frames(5)
	var chapters := _flow.chapters.chapters

	# The title.
	_check(_flow.mode == GameFlow.Mode.TITLE and _flow.title.visible and _main.get(&"current_level") == null,
		"the game opens on the title screen")
	_check(not _button(_flow.title, "Continue").visible and not _button(_flow.title, "Chapters").visible
		and _button(_flow.title, "New Game").visible and _button(_flow.title, "Settings").visible,
		"no save, not finished: New Game but no Continue, no Chapters")

	# New Game: every chapter in order, each with its card.
	_button(_flow.title, "New Game").pressed.emit()
	var order: Array[StringName] = []
	var dose_before := 0.0
	for i in chapters.size():
		await _until(func() -> bool: return _flow.card.visible or _main.get(&"current_level") != null, 5.0)
		var carded := _flow.card.visible and _flow.card.heading.text == chapters[i].title
		await _until(func() -> bool: return _main.get(&"current_level") != null and _director() != null, 5.0)
		_check(carded and GameState.chapter == i and GameState.night == chapters[i].night and GameState.carried,
			"%s: its card, then the night (chapter %d, night %d)" % [chapters[i].title, GameState.chapter, GameState.night])
		order.append(chapters[i].id)
		var pilot := NightPilot.new(_main.get(&"current_level"), _check)
		pilot.shorten()
		await _frames(3)
		if i == 0:
			_check(GameState.last_bell == &"start" and GameState.has_bell_save(), "each night saves at its start bell")
			GameState.raise_suspicion(12)
			GameState.set_flag(&"carried_flag")
			GameState.set_flag(&"gate_taken")
		if i == 2:
			# Night 0 and day 1 were clean nights: 5 off at each dawn.
			_check(GameState.suspicion == 2 and GameState.has_flag(&"n0_clean") and GameState.has_flag(&"carried_flag")
				and not GameState.has_flag(&"gate_taken"),
				"Suspicion carries over, less 5 for each clean night; story flags carry, the night's own don't (%d)" % GameState.suspicion)
		if chapters[i].id == &"night3":
			GameState.snap_dose(40.0)
			dose_before = -1.0
			await pilot.play_night3(_answer)
			_check(GameState.has_flag(&"night3_done") and GameState.has_flag(&"n3_thomas_hid_you"), "night 3, played in full in order")
			_check(GameState.count == 4 and GameState.souls == [&"merchant", &"lane_death", &"bell_brother", &"crypt_pilgrim"],
				"by night 3's dawn the rite has the merchant, the lane death, Bede and the crypt pilgrim (%s)" % [GameState.souls])
		elif chapters[i].id == &"night0":
			await pilot.play_night0(_answer)
		elif chapters[i].id == &"day1":
			await pilot.play_day1()
		elif chapters[i].id == &"night1":
			await pilot.play_night1(_answer)
			_check(GameState.has_flag(&"died_merchant") and GameState.has_flag(&"bread_warned"), "night 1, played in full in order")
			dose_before = -1.0
		elif chapters[i].id == &"night2":
			await pilot.play_night2(_answer)
			_check(GameState.has_flag(&"found_bell_brother") and GameState.has_flag(&"n2_roger"), "night 2, played in full in order")
			dose_before = -1.0
		elif chapters[i].id == &"night4":
			await pilot.play_night4(_answer)
			_check(GameState.has_flag(&"found_edwin") and GameState.has_note(&"osric_mask"), "night 4, played in full in order")
			dose_before = -1.0
		elif chapters[i].id == &"night5":
			await pilot.play_night5(_answer)
			_check(GameState.get_flag(&"n5_saved") == &"simon" and GameState.has_flag(&"n5_escaped"), "night 5, played in full in order")
			_check(GameState.count == 7, "by night 5's dawn the rite has seven souls (%s)" % [GameState.souls])
			dose_before = -1.0
		else:
			# A stub: the night doesn't change his Dose before he sleeps.
			await pilot.play_stub()
			dose_before = pilot.dose_at_sleep
		if dose_before > 0.0:
			_check(absf(GameState.dose - dose_before * 0.5) < 0.5, "a day's sleep halves Dose (%.1f to %.1f)" % [dose_before, GameState.dose])
		dose_before = GameState.dose
		_check(GameState.has_flag(StringName("night%d_done" % chapters[i].night)), "%s ends in sleep" % chapters[i].title)
	_check(order.size() == 8 and order[0] == &"night0" and order[1] == &"day1" and order[-1] == &"night6", "in order: %s" % [order])

	# The ending: the chronicle, then the title, with chapter select open.
	await _until(func() -> bool: return _flow.chronicle.visible, 5.0)
	_check(_flow.chronicle.visible and _flow.chronicle.heading.text == Endings.title(Endings.DEFAULT),
		"night 6 ends in the chronicle (%s)" % _flow.chronicle.heading.text)
	await _until(func() -> bool: return _flow.mode == GameFlow.Mode.TITLE, 5.0)
	_check(_flow.title.visible and Settings.finished and _button(_flow.title, "Chapters").visible
		and not _button(_flow.title, "Continue").visible, "back at the title: finished, Chapters open, nothing to continue")

	# Chapter select: night 5 with a typical state.
	_button(_flow.title, "Chapters").pressed.emit()
	_check(_flow.chapter_select.visible, "the chapter list")
	var night5 := _flow.chapters.index_of(&"night5")
	_flow.chapter_select.picked.emit(night5)
	await _until(func() -> bool: return _director() != null and _director().current != null, 5.0)
	var director := _director()
	_check(GameState.chapter == night5 and not GameState.carried and absf(GameState.dose - director.start_dose) < 0.5,
		"chapter select starts night 5 with its typical state (Dose %.1f)" % GameState.dose)

	# Pause: the night stops.
	await _frames(5)
	var hour := GameState.hour
	_flow.open_pause()
	_check(get_tree().paused and _flow.pause.visible, "Esc pauses: the pause menu")
	await get_tree().create_timer(0.5, true).timeout
	_check(is_equal_approx(GameState.hour, hour), "while paused the candle doesn't burn")
	_flow.resume()
	_check(not get_tree().paused and not _flow.pause.visible, "Resume")

	# Death: back to the latest save, quiet or bell. (Night 5 saves quietly
	# itself as the dilemma begins; the test's own quiet save comes after.)
	await _until(func() -> bool: return _director().current != null and _director().current.name == &"Dilemma", 10.0)
	await _frames(3)
	var capture: CaptureFlow = _main.get_node(^"CaptureFlow")
	GameState.snap_dose(44.0)
	GameState.quiet_save(&"start")
	GameState.snap_dose(5.0)
	var level := _level_id()
	await capture.die(&"blade")
	await _until(func() -> bool: return _level_id() != level and not capture.busy, 10.0)
	_check(_level_id() != level and absf(GameState.dose - 44.0) < 0.5 and _director().beats_run[0] == &"Wake",
		"death goes back to the quiet save (Dose %.1f)" % GameState.dose)

	# Continue: the last bell's chapter, from that bell.
	GameState.snap_dose(9.0)
	GameState.ring_bell(&"start")
	_flow.show_title()
	await _frames(3)
	_check(_button(_flow.title, "Continue").visible and _main.get(&"current_level") == null, "quit to the title: Continue is offered")
	GameState.snap_dose(70.0)
	_button(_flow.title, "Continue").pressed.emit()
	await _until(func() -> bool: return _director() != null and _director().current != null, 5.0)
	_check(GameState.chapter == night5 and absf(GameState.dose - 9.0) < 0.5 and _director().beats_run[0] == &"Wake",
		"Continue picks up at the last bell (chapter %d, Dose %.1f)" % [GameState.chapter, GameState.dose])

	for path in [TEST_SAVE, GameState.quiet_path(), TEST_SETTINGS]:
		DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
	Talk.auto_choice = Callable()
	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


func _director() -> NightDirector:
	var level: Node = _main.get(&"current_level")
	return level.get_node_or_null(^"Director") as NightDirector if level else null


func _level_id() -> int:
	var level: Node = _main.get(&"current_level")
	return level.get_instance_id() if level else 0


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
		await get_tree().physics_frame


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
