extends Node
## Night 6's rules (docs/mechanics.md, "Night 6" and "Tests"), in night6.tscn:
## - the Saint: its speed by the count; it goes through a locked door; the
##   animals fall silent near it; walking, it takes Dunstan, Cole and Osric
##   as he comes near each; at full strength it kills a cultist it meets; its
##   touch is death;
## - the rite: freeing the victim (E held at his cords for 3 s) stops it;
## - the Demon: nobody comes for him sober;
## - fire: in the smoke he chokes and collapses after 6 s unless he holds his
##   breath; a flame kills.
## Run: tools/check.sh

const TEST_SAVE := "user://test_night6_save.tres"

var _fails := 0
var _pilot: NightPilot
var _died: Array[StringName] = []


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	Talk.line_seconds = 0.05
	Talk.auto_choice = func(_o: PackedStringArray) -> int: return 1

	# The Saint.
	await _start()
	var night := _pilot.night
	var p := _pilot.player
	var saint := night.get_node(^"Saint") as HungrySaint
	for count in [8, 9, 10]:
		GameState.count = count
		saint.wake()
		_check(saint.walks == (count >= 9) and saint.kills == (count >= 10) and is_equal_approx(saint.speed, [0.7, 0.9, 1.2][count - 8]),
			"%d souls: %s" % [count, ["a shadow in the crypt", "it walks at 0.9 m/s", "it walks at 1.2 m/s and kills cultists"][count - 8]])
	GameState.count = 10
	saint.wake()
	var door: Door = null
	for d: Door in get_tree().get_nodes_in_group(&"doors"):
		if d.key == &"guesthouse":
			door = d
	door.set_open(false, true)
	door.locked = true
	saint.global_position = Vector3(-30.0, 0.05, -20.0)
	p.place(Vector3(-30.0, 0.05, -9.0), PI)
	await _pilot.seconds(6.0)
	_check(saint.global_position.z > -15.5 and door.locked, "it walks out through the guesthouse's locked door (%.1f)" % saint.global_position.z)
	var quiet := get_tree().get_nodes_in_group(&"room_tone").filter(func(n: Node) -> bool: return n is Animals)
	_check(not quiet.is_empty() and quiet.all(func(n: Node) -> bool: return n.get(&"quiet") == true), "silence before it: the animals stop")
	for who in ["Dunstan", "Cole", "Osric"]:
		var death := night.get_node(NodePath("SaintDeaths/" + who)) as DeathScene
		saint.global_position = death.global_position + Vector3(0, 0, -30.0)
		p.place(death.global_position + Vector3(0, 0, 6.0), 0.0)
		await _pilot.until(func() -> bool: return death.has_played, 5.0)
		await _pilot.seconds(2.0)
		_check(GameState.has_flag(StringName("died_" + who.to_lower())) and not GameState.souls.has(StringName(who.to_lower())),
			"walking, it takes %s as he comes near (fed to nothing)" % who)
	saint.global_position = Vector3(-30.0, 0.05, -12.0)
	var hunter := (load("res://game/hunter/hunter.tscn") as PackedScene).instantiate() as Hunter
	hunter.wearer = &"ranulf"
	hunter.dormant = true
	night.add_child(hunter)
	hunter.global_position = saint.global_position + Vector3(0.6, 0, 0)
	await _pilot.seconds(0.3)
	_check(not is_instance_valid(hunter) and GameState.has_flag(&"died_ranulf"), "at full strength it kills a cultist it meets")
	var touched := [false]
	saint.touched.connect(func() -> void: touched[0] = true)
	p.place(saint.global_position + Vector3(0, 0, 0.8), PI)
	await _pilot.seconds(0.3)
	_check(touched[0] and _died.has(&"saint"), "its touch is death")

	# The rite: freeing the victim.
	await _start()
	night = _pilot.night
	p = _pilot.player
	(night.get_node(^"Saint") as HungrySaint).set_physics_process(false)
	_pilot.skip_to(23.0)
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Rite" and (night.get_node(^"Victim") as Node3D).visible, 10.0)
	(night.get_node(^"Saint") as HungrySaint).sleep()
	var victim := night.get_node(^"Victim") as Node3D
	p.place(victim.global_position + Vector3(-1.0, -0.25, 0), deg_to_rad(-90.0))
	Input.action_press(&"interact")
	await _pilot.until(func() -> bool: return GameState.has_flag(&"rite_stopped"), 6.0)
	Input.action_release(&"interact")
	_check(GameState.get_flag(&"rite_stopped") == &"freed" and not victim.visible, "E held at the cords for 3 s: the victim runs, and the rite is stopped")

	# Sober, no demon comes.
	await _start()
	night = _pilot.night
	GameState.snap_dose(30.0)
	_pilot.skip_to(22.7)
	await _pilot.seconds(3.0)
	_check(not (night.get_node(^"Demon") as DemonChoice).done and not night.get_children().any(func(n: Node) -> bool: return n is VisitorNPC and (n as VisitorNPC).visitor and (n as VisitorNPC).visitor.speaker == "Hugh"),
		"at Dose 30, nobody comes for him with a light")

	# Fire: smoke and flames.
	await _start()
	night = _pilot.night
	p = _pilot.player
	var fire := night.get_node(^"FireGranary") as Fire
	fire.light()
	p.place(fire.global_position + Vector3(2.4, 0, -1.2), 0.0)
	Input.action_press(&"hold_breath")
	await _pilot.seconds(7.0)
	Input.action_release(&"hold_breath")
	_check(_died.is_empty(), "in the smoke, holding his breath, he doesn't choke")
	await _pilot.seconds(6.5)
	_check(_died.has(&"smoke"), "breathing the smoke for 6 s, he collapses: death")
	await _start()
	night = _pilot.night
	fire = night.get_node(^"FireGranary") as Fire
	fire.light()
	_pilot.player.place(fire.global_position + Vector3(0.3, 0, 0), 0.0)
	await _pilot.seconds(0.3)
	_check(_died.has(&"fire"), "into the flames: death")

	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	Talk.auto_choice = Callable()
	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


## Night 6 on its own: Anselm found, the wine refused, the hunt called back.
func _start() -> void:
	for c in get_children():
		c.queue_free()
	await get_tree().process_frame
	_died.clear()
	NightPilot.fresh_night(TEST_SAVE)
	GameState.night = 6
	GameState.chapter = 7
	for f: StringName in [&"bread_warned", &"keys_copied", &"thomas_custody"]:
		GameState.set_flag(f)
	GameState.count = 7
	GameState.carried = true
	var main := NightPilot.main_with("res://game/nights/night6.tscn")
	add_child(main)
	await get_tree().process_frame
	await get_tree().process_frame
	_pilot = NightPilot.new(main.get(&"current_level"), _check)
	_pilot.shorten()
	var flow := get_tree().get_first_node_in_group(&"capture_flow") as CaptureFlow
	# Dying is what some of this tests: note each death as it starts.
	flow.dying.connect(func(cause: StringName) -> void: _died.append(cause))
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Anselm" and not _pilot.player.controls_locked, 15.0)
	var anselm := _pilot.night.get_node(^"Bodies/Anselm") as Node3D
	_pilot.player.place(Vector3(27.6, 0.05, 2.4), deg_to_rad(-90.0))
	_pilot.face(anselm.global_position + Vector3.UP * 0.6)
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Wine", 10.0)
	var thomas := _pilot.night.get_node(^"Brothers/Thomas") as Node3D
	await _pilot.frames(2)
	_pilot.player.place(thomas.global_position + Vector3(-1.5, 0, 0), deg_to_rad(-90.0))
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Knock", 20.0)
	(_pilot.night.get_node(^"Hunt") as Hunt).end()


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
