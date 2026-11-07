extends Node
## Night 3 start to finish in the greybox, through main.tscn: the porter's
## actions are scripted (NightPilot) and every beat must come in the design
## doc's order with its effects: supper (bread eaten, remedy taken), the gate
## barred, Walter admitted and the child-sized knock at Dose 50+, the Matins
## bell saved, the headcount under the incense, the round with the demon
## closer each time and finally behind him, the crypt light and being
## spotted, the oven and the jaw, the hunter's search, Thomas, and dawn with
## the keys moved.
## Run: tools/check.sh

const TEST_SAVE := "user://test_night3_save.tres"
const ORDER: Array[StringName] = [&"Supper", &"Gate", &"Knocks", &"Bell", &"Choir", &"Round", &"Crypt", &"Chase", &"Dawn"]

var _fails := 0
var _choices: Array[int] = []
var _pilot: NightPilot


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	NightPilot.fresh_night(TEST_SAVE)
	Talk.line_seconds = 0.05
	Talk.auto_choice = func(_options: PackedStringArray) -> int: return _choices.pop_front() if not _choices.is_empty() else 0
	var main: Node = load("res://game/render/main.tscn").instantiate()
	add_child(main)
	_pilot = NightPilot.new(main.get(&"current_level"), _check)
	_pilot.shorten()
	await _pilot.frames(5)
	var p := _pilot.player
	var night := _pilot.night

	# Supper: eat the bread, take the remedy.
	_choices = [0, 0]
	await _pilot.until(func() -> bool: return _pilot.duty("Bread").enabled, 10.0)
	_check(_pilot.beat() == &"Supper" and GameState.phase == GameState.Phase.SUPPER, "night 3 opens at supper")
	_check(p.use_input_override, "seated: he can look but not walk")
	_pilot.duty("Bread").interact(p)
	await _pilot.until(func() -> bool: return _pilot.beat() != &"Supper", 10.0)
	_check(GameState.get_flag(&"n3_ate_bread") == true and GameState.get_flag(&"n3_took_remedy") == true,
		"ate the bread and took Thomas's remedy")
	_check(_said("(The bread tastes bitter.)") and _said("(Offers a remedy for your headaches.)"), "the doc's supper lines")

	# No HUD: the way to the gate is lit, its doors open, from his seat.
	await _pilot.until(func() -> bool: return _pilot.duty("BarGate").enabled, 5.0)
	var gate_lamp: Candle = night.get_node(^"Lamps/GateLamp")
	var refectory_door: Door = night.get_node(^"Abbey/Navigation/SouthRange/Doors/RefectoryW0Door_00")
	var kitchen_door: Door = night.get_node(^"Abbey/Navigation/SouthRange/Doors/KitchenW0Door_00")
	_check(gate_lamp.lit and refectory_door.is_open and kitchen_door.is_open,
		"a lamp burns at the gate, and the doors between supper and the gate stand open")
	_check(_lamp_over(refectory_door) and _lamp_over(kitchen_door), "a lamp hangs over each of those doorways")

	# The gate: he walks out to it (the brothers leave supper once he has gone).
	p.place(Vector3(-36, 0.05, -2), deg_to_rad(90.0))
	await _pilot.use("BarGate")
	await _pilot.use("Ledger")
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Knocks", 5.0)
	_check(GameState.has_flag(&"gate_barred") and GameState.has_flag(&"n3_ledger"), "gate barred and the ledger written")

	# Knocks: Walter (admitted); then, drugged, the child-sized knock.
	GameState.snap_dose(60.0)
	_choices = [0]
	await _pilot.use("Grate")
	await _pilot.until(func() -> bool: return GameState.has_flag(&"n3_walter"), 5.0)
	var walter: Brother = night.get_node(^"Brothers/Walter")
	_check(GameState.get_flag(&"n3_walter") == &"admitted" and walter.visible
		and walter.global_position.distance_to(_pilot.mark("WalterRoom")) < 0.5, "Walter is admitted to the guesthouse")
	await _pilot.use("Grate")
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Bell", 5.0)
	_check(GameState.has_flag(&"n3_child_knock"), "at Dose 50+, a small knock low on the gate, no one there")

	# The Matins bell saves the night. A lamp in the tower; the gate's is out.
	await _pilot.until(func() -> bool: return _pilot.duty("BellRope").enabled, 10.0)
	var tower_lamp: Candle = night.get_node(^"Lamps/TowerLamp")
	var tower_door: Door = night.get_node(^"Abbey/Navigation/Church/Doors/TowerW0Door_01")
	_check(tower_lamp.lit and tower_door.is_open and _lamp_over(tower_door) and not gate_lamp.lit,
		"the bell is due: a lamp in the tower and over its open door; the gate lamp is out")
	_check(not _lamp_over(refectory_door), "the lamps on the way to the gate are gone")
	await _pilot.use("BellRope")
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Choir", 5.0)
	_check(GameState.last_bell == &"matins" and GameState.has_bell_save(), "the Matins bell is rung and saved")

	# The choir: the incense, and every brother counted.
	GameState.snap_dose(0.0)
	var counted := await _pilot.count_brothers()
	_check(GameState.has_flag(&"n3_headcount") and counted == 8, "counts the brothers in the choir (%d)" % counted)
	await _pilot.seconds(8.0)
	_check(GameState.dose >= 49.9 and GameState.dose_floor == 50.0, "the incense takes Dose to 50 and holds it there (%.1f)" % GameState.dose)
	var stranger: DualRender = night.get_node(^"Brothers/Stranger/Look")
	_pilot.face(p.global_position + Vector3(0, 0, 10))
	await _pilot.seconds(0.5)
	_check(stranger.drugged, "drugged, the dead brother stands in the stranger's place")

	# The round: the demon closer each time, then behind him.
	var stalker: Stalker = night.get_node(^"Stalker")
	var distances := await _pilot.walk_round()
	_check(distances.size() == 3 and distances[1] < distances[0] and distances[2] < 4.5 and stalker.final,
		"end of the walk, the doorway, then behind him in the choir %s" % [distances.map(func(d: float) -> String: return "%.1f" % d)])

	# The crypt light; going down, he is seen.
	var hunter: Hunter = night.get_node(^"Hunter")
	var suspicion := GameState.suspicion
	await _pilot.go_down_to_crypt()
	_check(hunter.state == Hunter.State.CHASE and GameState.suspicion == suspicion + 10,
		"a light in the crypt; investigating, he is spotted (Suspicion +10)")

	# The chase: into the oven; the jaw; held breath while he checks it.
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Chase", 3.0)
	var oven: HidingSpot = night.get_node(^"Abbey/Navigation/SouthRange/HidingSpots/Oven")
	p.place(oven.exit.global_position, deg_to_rad(90.0))
	p.hide_in(oven)
	await _pilot.until(func() -> bool: return GameState.has_flag(&"n3_body3"), 4.0)
	_check(GameState.has_flag(&"n3_body3") and _said("(Your hand closes on something in the ash. A jaw.)"), "in the oven, a jaw in the ash (body 3)")
	var checked := []
	oven.checked.connect(func(found: bool) -> void: checked.append(found))
	await _pilot.until(func() -> bool: return hunter.global_position.distance_to(oven.view.global_position) < 8.0, 60.0)
	Input.action_press(&"hold_breath")
	await _pilot.until(func() -> bool: return not checked.is_empty(), 12.0)
	var gone := func() -> bool:
		return hunter.global_position.distance_to(oven.view.global_position) > 4.0 or hunter.state == Hunter.State.PATROL
	await _pilot.until(gone, 8.0)
	Input.action_release(&"hold_breath")
	_check(checked == [false] and GameState.captures == 0, "he checks the oven and misses him (%s)" % [checked])
	p.leave_hiding()
	await _pilot.until(func() -> bool: return GameState.has_flag(&"n3_thomas_hid_you"), 10.0)
	var thomas: Brother = night.get_node(^"Brothers/Thomas")
	_check(GameState.has_flag(&"n3_thomas_hid_you") and GameState.captures == 0
		and p.global_position.distance_to(_pilot.mark("RescuePorter")) < 0.5 and thomas.visible,
		"climbing out, nearly caught: Thomas pulls him into the infirmary")

	# Dawn: the keys have been moved.
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Dawn", 5.0)
	await _pilot.use("KeysMoved")
	await _pilot.until(func() -> bool: return GameState.has_flag(&"night3_done"), 5.0)
	_check(GameState.has_flag(&"n3_keys_moved") and p.global_position.distance_to(_pilot.mark("DawnCell")) < 6.0,
		"at dawn his keys are not where he left them")
	await _pilot.until(func() -> bool: return _pilot.director().current == null, 3.0)
	_check(_pilot.director().beats_run == ORDER, "every beat, in order: %s" % [_pilot.director().beats_run])

	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	Talk.auto_choice = Callable()
	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


func _lamp_over(door: Door) -> bool:
	return door.get_children().any(func(c: Node) -> bool: return c is Candle and not c.is_queued_for_deletion())


func _said(text: String) -> bool:
	return Talk.history.any(func(h: Array) -> bool: return h[1] == text)


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
