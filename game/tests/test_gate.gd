extends Node
## Keeping the gate on night 3 (night3.tscn with only its Knocks beat): at his
## hour Walter comes up the lane with his lantern and knocks at the grille; the porter
## reads him by looking; each choice plays out.
## - At the grille they talk: the porter's view eases in on Walter's face.
## - Admitted: bar, gate open, he comes in, gate shut and barred, he follows to
##   the bed the porter shows him, and the ledger says what the porter noticed
##   (and nothing he didn't).
## - Walked away from: Walter waits at the grille, knocking, until the porter
##   comes back. Then turned away: he goes back down the lane; nothing in the
##   ledger.
## - The prior: Suspicion +10; the prior takes him to a bed; he is written in.
## And the ledger, held up, shows him and the night's duty.
## Run: tools/check.sh

const TEST_SAVE := "user://test_gate_save.tres"

var _fails := 0
var _answer := [-1]


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	Talk.line_seconds = 0.05
	Talk.auto_choice = func(_options: PackedStringArray) -> int: return _answer[0]

	# Admitted, having noticed his box and his bag (not his face).
	var pilot := await _night()
	var night := pilot.night
	var lane_start := pilot.mark("LaneStart")
	var seen_walking := [false]
	var npc_ready := func() -> bool: return get_tree().get_first_node_in_group(&"callers") != null
	await pilot.until(npc_ready, 5.0)
	var walter := get_tree().get_first_node_in_group(&"callers") as VisitorNPC
	_check(walter.global_position.distance_to(lane_start) < 1.0 and walter.get_node(^"Lantern").visible,
		"Walter starts down the lane with his lantern")
	await pilot.until(func() -> bool:
		seen_walking[0] = seen_walking[0] or walter.velocity.length() > 1.0
		return pilot.duty("Grate").enabled, 30.0)
	_check(seen_walking[0] and walter.global_position.distance_to(pilot.mark("Porch")) < 0.7,
		"he walks up the lane and knocks at the grille, under the porch lantern")
	var said_before := Talk.history.size()
	var came_in := [false]
	var watch := func() -> void: came_in[0] = came_in[0] or walter.global_position.x > -39.0
	get_tree().physics_frame.connect(watch)
	await pilot.keep_gate(0, [&"box", &"bag"], _answer)
	get_tree().physics_frame.disconnect(watch)
	var asides := Talk.history.slice(said_before).map(func(h: Array) -> String: return h[1])
	_check(asides.has("(Oily, cheerful.)") and asides.has("(His box of relics rattles.)") and asides.has("(His bag smells of the incense.)")
		and not asides.has("(Plump, in a coloured cloak.)"),
		"reading him: what the porter looks at (his face as they talk, then the box and bag), he notices; not his cloak")
	var bed := pilot.duty("GuestBeds/Bed2")
	_check(came_in[0], "admitted, he walks in through the gateway")
	_check(walter.lying and walter.global_position.distance_to(bed.global_position) < 0.8,
		"he follows the porter and lies down in the bed he is shown")
	var leaves: Array = [night.get_node(^"Abbey/Navigation/OuterCourt/Doors/GateN"), night.get_node(^"Abbey/Navigation/OuterCourt/Doors/GateS")]
	var bar: Node3D = night.get_node(^"Abbey/Navigation/OuterCourt/Props/GateBar")
	_check(leaves.all(func(d: Door) -> bool: return not d.is_open and d.locked) and bar.visible, "the gate is shut and barred behind him")
	await pilot.frames(5)
	var entry: Dictionary = GameState.ledger[-1] if not GameState.ledger.is_empty() else {}
	_check(entry.get("name", "") == "Walter the pardoner" and String(entry.get("description", "")).contains("box of relics")
		and String(entry.get("description", "")).contains("incense") and not String(entry.get("description", "")).contains("plump"),
		"the ledger says what he noticed: %s" % [entry])
	_check(GameState.get_flag(&"n3_walter") == &"admitted", "the night remembers he was let in")
	var ledger_view := LedgerView.new()
	add_child(ledger_view)
	ledger_view.set_showing(true)
	var page := (ledger_view.get_child(0).get_child(0).get_child(1) as RichTextLabel).text
	_check(ledger_view.visible and page.contains("Walter the pardoner") and page.contains("Keep the gate"),
		"held up, the ledger shows him and tonight's duty")
	ledger_view.queue_free()

	# Walked away from, then turned away: back down the lane, nothing written.
	pilot = await _night()
	var porter := pilot.player
	await pilot.until(func() -> bool: return pilot.duty("Grate").enabled, 120.0)
	await pilot.wake()
	porter.place(Vector3(-39.0, 0.05, -2.0), deg_to_rad(90.0))
	pilot.duty("Grate").interact(porter)
	await pilot.until(func() -> bool: return Talk.is_choosing(), 5.0)
	await pilot.seconds(Player.TALK_TURN_TIME + 0.1)
	walter = get_tree().get_first_node_in_group(&"callers") as VisitorNPC
	_check(porter.talking and porter.zoom > Player.TALK_ZOOM - 0.5 and ViewCheck.off_centre(porter.camera, walter.face_position()) < 3.0,
		"at the grille, his view turns to Walter's face")
	await pilot.seconds(Player.TALK_HOLD + Player.TALK_TURN_TIME)
	_check(porter.talking and Talk.is_choosing() and porter.zoom < 0.01, "a moment later it's his again, and Walter waits for an answer")
	await pilot.walk_off()
	_check(not porter.talking and not Talk.talking, "he can walk away from the grille")
	await pilot.until(func() -> bool: return pilot.duty("Grate").enabled, 5.0)
	_check(pilot.duty("Grate").enabled and walter.global_position.distance_to(pilot.mark("Porch")) < 0.7 and GameState.get_flag(&"n3_walter") == null,
		"Walter waits at the grille, knocking, for him to come back")
	await pilot.keep_gate(1, [], _answer)
	var walter_id := (get_tree().get_first_node_in_group(&"callers") as Node).get_instance_id()
	await pilot.until(func() -> bool: return not is_instance_id_valid(walter_id), 30.0)
	_check(GameState.get_flag(&"n3_walter") == &"refused" and GameState.ledger.is_empty() and not is_instance_id_valid(walter_id),
		"turned away, he goes back down the lane and is gone")

	# The prior: he comes and takes Walter in himself.
	pilot = await _night()
	var suspicion := GameState.suspicion
	walter = null
	var prior_came := [false]
	get_tree().node_added.connect(func(n: Node) -> void:
		if n is VisitorNPC and (n as VisitorNPC).visitor and (n as VisitorNPC).visitor.id == &"hugh":
			prior_came[0] = true)
	await pilot.keep_gate(2, [&"face"], _answer)
	for v: VisitorNPC in get_tree().get_nodes_in_group(&"visitors"):
		if v.visitor.id == &"walter":
			walter = v
	_check(prior_came[0] and GameState.suspicion == suspicion + 10, "sending for the prior brings him to the gate (Suspicion +10)")
	_check(walter != null and walter.lying, "the prior takes Walter to a bed")
	_check(GameState.ledger.size() == 1 and String(GameState.ledger[0]["description"]).contains("oily"), "and the porter still writes him in")

	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	Talk.auto_choice = Callable()
	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


## A fresh night 3 that runs only its Knocks beat.
func _night() -> NightPilot:
	for n in get_children():
		if n.name == &"Night3":
			remove_child(n)
			n.free()
	for v in get_tree().get_nodes_in_group(&"visitors"):
		v.free()
	NightPilot.fresh_night(TEST_SAVE)
	GameState.phase = GameState.Phase.KNOCKS
	var night: Node = load("res://game/nights/night3.tscn").instantiate()
	var director := night.get_node(^"Director")
	for beat in director.get_children():
		if beat.name != &"Knocks":
			director.remove_child(beat)
			beat.free()
	add_child(night)
	var pilot := NightPilot.new(night, _check)
	pilot.shorten()
	await pilot.frames(30)
	pilot.skip_to(20.0)
	return pilot


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
