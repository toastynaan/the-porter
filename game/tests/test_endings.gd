extends Node
## Night 6 and the seven endings (design doc, "Endings"; docs/full-game-run.md,
## "Endings", checked in order; docs/mechanics.md, "Night 6"): each reached by
## its own scripted route from night 6's dusk:
## - the New Faith: he drinks Thomas's wine and is caught;
## - the Demon: at Dose 75+ "the demon" corners him with a light and he strikes;
## - the Rising: the rite finishes at Matins with the count at 9;
## - the Fire: he burns the granary and the crypt with the book on its stand,
##   and leaves by the mill race;
## - the Gate: two kinds of proof, and he opens the gate for Roger;
## - the Witness: he lets Joan in and goes out by the mill race with her;
## - the Broken Rite: he takes the book from the crypt and holds out to dawn.
## Each is played through the game's own flow (night 6 started as the last
## chapter), and ends in its own chronicle. Also: Anselm found dead in his
## bed; the wine's Dose; refusing it; the Saint's strength by the count; the
## fire catching and spreading; Roger and Joan at the gate.
## Run: tools/check.sh

const TEST_SAVE := "user://test_endings_save.tres"

var _fails := 0
var _answer := [-1]
var _pilot: NightPilot
var _main: Node
var _flow: GameFlow


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	Talk.line_seconds = 0.05
	Talk.auto_choice = func(_o: PackedStringArray) -> int: return _answer[0] if _answer[0] >= 0 else 0

	# The New Faith: the wine, then caught.
	await _start([], 0)
	_check(GameState.has_flag(&"found_anselm") and GameState.souls.has(&"anselm") and GameState.has_note(&"anselm_henbane"),
		"Anselm dead in his bed, his mouth full of henbane (body 6, fed to the rite)")
	await _pilot.until(func() -> bool: return GameState.dose >= 39.0, 30.0)
	_check(GameState.has_flag(&"drank_wine") and GameState.dose >= 39.0, "Thomas's wine: Dose +40 (%.0f)" % GameState.dose)
	var flow := _pilot.night.get_tree().get_first_node_in_group(&"capture_flow") as CaptureFlow
	var hunter := (load("res://game/hunter/hunter.tscn") as PackedScene).instantiate() as Hunter
	hunter.dormant = true
	_pilot.night.add_child(hunter)
	flow.on_captured(hunter, _pilot.player)
	await _ended()
	_check(GameState.get_flag(&"ending") == &"new_faith", "caught after the wine: the New Faith (%s)" % GameState.get_flag(&"ending", &""))

	# The Demon: drugged, the demon corners him, and he strikes.
	await _start([], 1)
	_check(GameState.has_flag(&"refused_wine") and GameState.suspicion >= 20, "refused to his face: Suspicion +20")
	GameState.snap_dose(80.0)
	var demon := _pilot.night.get_node(^"Demon") as DemonChoice
	_pilot.player.place(demon.from.global_position + Vector3(2.8, 0, 0), deg_to_rad(90.0))
	_answer[0] = 0
	_pilot.skip_to(22.6)
	await _ended()
	_answer[0] = -1
	_check(GameState.get_flag(&"ending") == &"demon" and GameState.has_flag(&"struck_the_demon"), "at Dose 75+, he strikes the demon: the Demon (%s, Dose %.0f, %s)" % [GameState.get_flag(&"ending", &""), GameState.dose, NightClock.clock_text(GameState.hour)])

	# The Rising: the rite finishes with the count at 9.
	await _start([], 1)
	GameState.count = 8
	_pilot.skip_to(23.0)
	await _pilot.seconds(0.5)
	var saint := _pilot.night.get_node(^"Saint") as HungrySaint
	_check(saint.awake and not saint.walks, "with 8 souls the Saint is a shadow that can't leave the crypt")
	_pilot.skip_to(24.05)
	await _ended()
	_check(GameState.get_flag(&"ending") == &"rising" and GameState.has_flag(&"rite_done") and GameState.count == 9, "the rite finishes at Matins with 9: the Rising")

	# The Fire: the granary and the crypt, with the book; out by the race.
	await _start([], 1)
	var granary := _pilot.night.get_node(^"FireGranary") as Fire
	var crypt := _pilot.night.get_node(^"FireCrypt") as Fire
	_pilot.player.place(granary.global_position + Vector3(0, 0, 1.2), 0.0)
	_pilot.face(granary.global_position)
	await _pilot.until(func() -> bool: return granary.burning, 4.0)
	_check(granary.burning, "his lantern held to the sacks for 2 s: the granary catches")
	_pilot.player.place(Vector3(10, 0.05, -14), 0.0)
	await _pilot.seconds(2.5)
	_check(granary.flames.size() >= 3, "the fire spreads along its path, about 1 m/s (%d flames)" % granary.flames.size())
	crypt.light()
	_check(GameState.has_flag(&"book_burned"), "the crypt burns, and the book on its stand with it")
	_pilot.player.place(_pilot.mark("RaceExit"), 0.0)
	await _ended()
	_check(GameState.get_flag(&"ending") == &"fire", "burned with the book, he gets out: the Fire")

	# The Gate: proof, and the gate opened for Roger.
	await _start([&"died_merchant"], 1)
	GameState.satchel.append_array([&"mask", &"purse"])
	_pilot.skip_to(20.0)
	await _pilot.seconds(0.5)
	_check(GameState.get_flag(&"n6_knock") == &"roger", "the merchant died: Roger knocks")
	_pilot.player.place(Vector3(-39.0, 0.05, -2.0), deg_to_rad(90.0))
	_answer[0] = 0
	await _pilot.use("Grate")
	await _ended()
	_answer[0] = -1
	_check(GameState.get_flag(&"ending") == &"gate", "with two kinds of proof he opens the gate for Roger: the Gate")

	# The Witness: Joan let in, out by the race with her.
	await _start([], 1)
	GameState.set_flag(&"n2_joan", &"admitted")
	_pilot.skip_to(20.0)
	await _pilot.seconds(0.5)
	_check(GameState.get_flag(&"n6_knock") == &"joan", "Joan alive: Joan knocks")
	_pilot.player.place(Vector3(-39.0, 0.05, -2.0), deg_to_rad(90.0))
	_answer[0] = 0
	await _pilot.use("Grate")
	await _pilot.until(func() -> bool: return GameState.has_flag(&"n6_gate_opened"), 10.0)
	_answer[0] = -1
	await _pilot.seconds(3.0)
	_pilot.player.place(_pilot.mark("RaceExit"), 0.0)
	await _ended()
	_check(GameState.get_flag(&"ending") == &"witness", "out by the race with Joan at his heels: the Witness (%s)" % GameState.get_flag(&"ending", &""))

	# The Broken Rite: the book taken; held out to dawn. And the Saint.
	await _start([], 1)
	GameState.count = 9
	_pilot.skip_to(23.0)
	await _pilot.seconds(0.5)
	saint = _pilot.night.get_node(^"Saint") as HungrySaint
	_check(saint.awake and saint.walks and is_equal_approx(saint.speed, 0.9), "with 9 souls the Saint walks the abbey at 0.9 m/s")
	saint.sleep()
	var book := _pilot.night.get_node(^"Proof/Book") as Pickup
	book.interact(_pilot.player)
	await _pilot.until(func() -> bool: return GameState.has_flag(&"rite_stopped"), 3.0)
	_check(GameState.get_flag(&"rite_stopped") == &"book" and GameState.satchel.has(&"book"), "he takes the book from the crypt: the rite is stopped")
	_pilot.skip_to(24.1)
	await _pilot.seconds(0.3)
	_check(not GameState.has_flag(&"rite_done") and GameState.count == 9, "Matins passes and the last soul isn't given")
	_pilot.skip_to(30.0)
	await _ended()
	_check(GameState.get_flag(&"ending") == &"broken_rite", "he holds out to dawn: the Broken Rite (%s, %s)" % [GameState.get_flag(&"ending", &""), NightClock.clock_text(GameState.hour)])

	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	Talk.auto_choice = Callable()
	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


## Night 6 from dusk, as the last chapter of a playthrough: Anselm found,
## the wine (`wine` 0 drinks, 1 refuses), the hunt sent out and called back
## (the hunters are test_hunt's).
func _start(flags: Array[StringName], wine: int) -> void:
	if _main:
		_main.queue_free()
		await get_tree().process_frame
	NightPilot.fresh_night(TEST_SAVE)
	for f: StringName in [&"bread_warned", &"keys_copied", &"thomas_custody"]:
		GameState.set_flag(f)
	for f in flags:
		GameState.set_flag(f)
	GameState.count = 6
	Talk.history.clear()
	_main = load("res://game/render/main.tscn").instantiate()
	add_child(_main)
	_flow = _main.get_node(^"Game")
	_flow.card.seconds = 0.2
	_flow.chronicle.seconds = 30.0
	await get_tree().process_frame
	_flow.start_chapter(_flow.chapters.index_of(&"night6"), true)
	while _main.get(&"current_level") == null or (_main.get(&"current_level") as Node).get_node_or_null(^"Director") == null:
		await get_tree().physics_frame
	_pilot = NightPilot.new(_main.get(&"current_level"), _check)
	_pilot.shorten()
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Anselm" and not _pilot.player.controls_locked, 15.0)
	var anselm := _pilot.night.get_node(^"Bodies/Anselm") as FoundBody
	_pilot.player.place(Vector3(27.6, 0.05, 2.4), deg_to_rad(-90.0))
	_pilot.face(anselm.global_position + Vector3.UP * 0.6)
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Wine", 10.0)
	_answer[0] = wine
	var thomas := _pilot.night.get_node(^"Brothers/Thomas") as Node3D
	await _pilot.frames(2)
	_pilot.player.place(thomas.global_position + Vector3(-1.5, 0, 0), deg_to_rad(-90.0))
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Hunt" or _pilot.beat() == &"Knock", 15.0)
	_answer[0] = -1
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Knock", 5.0)
	(_pilot.night.get_node(^"Hunt") as Hunt).end()


## Waits for the night's ending and its chronicle.
func _ended() -> void:
	await _pilot.until(func() -> bool: return GameState.has_flag(&"ending"), 30.0)
	var id := StringName(GameState.get_flag(&"ending", &""))
	var t := 0.0
	while not _flow.chronicle.visible and t < 10.0:
		await get_tree().physics_frame
		t += 1.0 / Engine.physics_ticks_per_second
	_check(_flow.chronicle.visible and _flow.chronicle.heading.text == Endings.title(id),
		"its chronicle: %s" % _flow.chronicle.heading.text)


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
