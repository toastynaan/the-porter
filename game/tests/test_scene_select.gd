extends Node
## Starting a chapter at one of its beats, for testing (SceneSelect, the
## title's "Test a scene" in debug builds; docs/log/full-game-run.md, "Tools"):
## - the page lists every chapter, and a chapter's beats as its scene has them;
## - night 0 from Arrive: no ride. He stands in the lane by the barred gate,
##   the road and the wagon are gone, the abbey is shown, and the knock is
##   the duty;
## - night 0 from Window: Mab and Agnes are behind him (their flags are set);
## - night 1 from a later beat: that beat runs, with the clock at the hour
##   the skipped beats were due.
## Run: tools/check.sh

const TEST_SAVE := "user://test_scene_select_save.tres"
const TEST_SETTINGS := "user://test_scene_select_settings.cfg"

var _fails := 0
var _main: Node
var _flow: GameFlow


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	GameState.save_path = TEST_SAVE
	for path in [TEST_SAVE, GameState.quiet_path()]:
		DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
	Settings.path = TEST_SETTINGS
	Settings.finished = false
	Talk.line_seconds = 0.05
	Talk.auto_choice = func(_options: PackedStringArray) -> int: return 0
	_main = load("res://game/core/render/main.tscn").instantiate()
	add_child(_main)
	_flow = _main.get_node(^"Game")
	await _frames(5)

	var page := _flow.scene_select
	_button(_flow.title, "Test a scene").pressed.emit()
	await _frames(3)
	var chapters := page.column.get_children().filter(func(c: Node) -> bool: return c is Button and not c.is_queued_for_deletion())
	_check(page.visible and chapters.size() == _flow.chapters.chapters.size() + 1, "the title's Test a scene lists every chapter (%d)" % (chapters.size() - 1))
	var beats := SceneSelect.beats_of("res://game/chapters/night0/night0.tscn")
	_check(beats.map(func(b: Array) -> StringName: return b[0]) == [&"Ride", &"Arrive", &"Inn", &"Window", &"Sleep"] and beats[1][1] == "Knock at the abbey gate",
		"a chapter's beats are read from its scene, with their duties (%s)" % [beats])

	# Night 0, from being set down.
	page.picked.emit(0, &"Arrive")
	await _until(func() -> bool: return _beat() == &"Arrive", 10.0)
	await _frames(10)
	var night := _level()
	var p := get_tree().get_first_node_in_group(&"player") as Player
	var set_down := (night.get_node(^"Marks/SetDown") as Node3D).global_position
	var gate := night.get_node(^"AbbeyGate") as AbbeyGate
	_check(_beat() == &"Arrive" and p.riding == null and p.global_position.distance_to(set_down) < 1.0 and GameState.has_flag(&"n0_arrived"),
		"night 0 from Arrive: no ride, he stands in the lane where the carter sets him down")
	_check(night.get_node_or_null(^"Road") == null and night.get_node_or_null(^"Wagon") == null and (night.get_node(^"Abbey") as Node3D).visible
		and not gate.is_open() and GameState.hour > 16.9, "the road and the wagon are gone, the abbey is there, the gate is barred, the hour has moved on (%.2f)" % GameState.hour)
	var fade := _main.get_node(^"UI/Fade") as ScreenFade
	await _until(func() -> bool: return fade.color.a < 0.05, 6.0)
	_check(fade.color.a < 0.05, "and the night comes up out of black")

	# Night 0, from the window.
	page.picked.emit(0, &"Window")
	await _until(func() -> bool: return _beat() == &"Window", 10.0)
	_check(_beat() == &"Window" and GameState.has_flag(&"n0_sent_to_inn") and GameState.has_flag(&"n0_room") and GameState.has_flag(&"n0_arrived"),
		"night 0 from Window: Mab has sent him on and Agnes has given him the room")

	# A later night, from a later beat.
	var n1 := _flow.chapters.index_of(&"night1")
	page.picked.emit(n1, &"Round")
	await _until(func() -> bool: return _beat() == &"Round", 10.0)
	var director := _level().get_node(^"Director") as NightDirector
	var due := 0.0
	for c in director.get_children():
		if c.name == &"Round":
			break
		due = maxf(due, (c as NightBeat).due)
	_check(_beat() == &"Round" and GameState.night == 1 and GameState.hour >= due - 0.01 and GameState.start_beat.is_empty(),
		"night 1 from Round: that beat runs, the clock at the hour the beats before it were due (%.2f, due %.2f)" % [GameState.hour, due])

	for path in [TEST_SAVE, GameState.quiet_path(), TEST_SETTINGS]:
		DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(1 if _fails > 0 else 0)


func _level() -> Node:
	return _main.get(&"current_level")


func _beat() -> StringName:
	var level := _level()
	var director := level.get_node_or_null(^"Director") as NightDirector if level else null
	return director.current.name if director and director.current else &""


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
