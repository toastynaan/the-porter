extends Node
## Night 3 start to finish in the greybox, through main.tscn, on the candle
## clock: the porter's actions are scripted (NightPilot) and every beat must
## come in the design doc's order with its effects. Waking at dusk with the
## gate open and Cole at it (people to talk to, the lane walkable), the supper
## bell at its mark, supper (palming offered: night 3 counts the night-1
## warning), taking the gate from Cole (shut, barred, the ledger), dozing on
## the gate bench until Walter's knock and then the child-sized knock at Dose
## 50+, the Matins bell at its mark and saved, the headcount under the
## incense, the round with the demon closer each time and finally behind him,
## the crypt light and being spotted, the oven and the jaw, the hunter's
## search, Thomas, the small hours dozed through to Lauds, and dawn: Cole
## takes the gate, the keys moved, sleep.
## Run: tools/check.sh

const TEST_SAVE := "user://test_night3_save.tres"
const ORDER: Array[StringName] = [&"Wake", &"Supper", &"Gate", &"Knocks", &"Bell", &"Choir", &"Round", &"Crypt", &"Chase", &"SmallHours", &"Dawn"]

var _fails := 0
var _choices: Array[int] = []
## Every set of options offered.
var _offered: Array[PackedStringArray] = []
## The gate's answer, set by NightPilot.keep_gate while the choice is open.
var _answer := [-1]
var _pilot: NightPilot


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	NightPilot.fresh_night(TEST_SAVE)
	Talk.line_seconds = 0.05
	Talk.auto_choice = func(options: PackedStringArray) -> int:
		if _offered.is_empty() or _offered[-1] != options:
			_offered.append(options)
		if _answer[0] >= 0:
			return _answer[0]
		return _choices.pop_front() if not _choices.is_empty() else -1
	var main: Node = NightPilot.main_with("res://game/nights/night3.tscn")
	add_child(main)
	_pilot = NightPilot.new(main.get(&"current_level"), _check)
	_pilot.shorten()
	await _pilot.frames(5)
	var p := _pilot.player
	var night := _pilot.night
	var gate: AbbeyGate = night.get_node(^"AbbeyGate")
	var cole: VisitorNPC = night.get_node(^"People/Cole")
	var daylight: Daylight = night.get_node(^"Daylight")

	# Waking at dusk: the cell, failing light, the gate open with Cole at it.
	_check(_pilot.beat() == &"Wake" and GameState.phase == GameState.Phase.DUSK and absf(GameState.hour - 16.0) < 0.01,
		"night 3 opens at dusk, 16:00 by the candle")
	await _pilot.until(func() -> bool: return not p.controls_locked, 5.0)
	_check(p.global_position.distance_to(_pilot.mark("WakeCell")) < 0.5, "he wakes in his cell")
	_check(daylight.light > 0.95 and absf(GameState.dose - 30.0) < 0.5 and GameState.has_flag(&"bread_warned"),
		"in failing daylight, with what the nights before left (Dose 30, warned about the bread)")
	_check(gate.is_open() and not (night.get_node(^"Abbey/Navigation/OuterCourt/Props/GateBar") as Node3D).visible
		and cole.visible and cole.global_position.distance_to(_pilot.mark("ColeGate")) < 0.3,
		"the gate stands open, unbarred, with Cole at it")
	var map := p.get_world_3d().navigation_map
	var lane := _pilot.mark("LaneStart")
	var way := NavigationServer3D.map_get_path(map, p.global_position, lane, true)
	_check(not way.is_empty() and way[-1].distance_to(lane) < 0.5, "he can walk out through the gate into the lane")
	# Talking: Mab answers one question, then he walks away; Edwin calls after him.
	p.place(Vector3(-40.4, 0.05, 0.9), deg_to_rad(90.0))
	await _pilot.talk(night.get_node(^"People/Mab/Talker") as Talker, [0, -1], _answer)
	var edwin: Brother = night.get_node(^"Brothers/Edwin")
	p.place(edwin.global_position + Vector3(2.0, 0, 0), 0.0)
	await _pilot.talk(night.get_node(^"Brothers/Edwin/Talker") as Talker, [-1], _answer)
	await _pilot.seconds(0.2)
	_check(_said("Porter. You look worse every night. I say it kindly.")
		and _said("Everyone who goes in at that gate, and everyone who comes out. Nobody asks me.") and GameState.has_flag(&"n3_mab_saw"),
		"Mab at the gate can be talked to, and answers")
	_check(edwin.visible and edwin.global_position.distance_to((night.get_node(^"Places/Dusk/Edwin") as Node3D).global_position) < 0.1
		and _said("Alric! There you are. I looked for you at None, then I remembered you sleep all day. You lucky man.")
		and _said("I'll see you at supper! Sit by me, if they let you.") and not p.talking,
		"the brothers at their dusk places can be talked to, and walked away from")
	var walkers := night.get_node(^"People").get_children().filter(func(n: Node) -> bool: return n.has_node(^"Walk"))
	_check(walkers.size() == 2, "two passers-by in the lane (and Hob, Agnes, Kit and Gib about)")
	(night.get_node(^"GateBench") as GateBench).interact(p)
	await _pilot.seconds(0.3)
	_check(_said("(The gate is Cole's until after supper.)") and not _pilot.clock().dozing, "no dozing while the gate is Cole's")
	(night.get_node(^"CandleClock") as CandleClock).interact(p)
	await _pilot.seconds(0.3)
	_check(_said("(The candle stands at 16:00. The next mark is the supper bell.)"), "the candle clock tells the hour and the next mark")

	# The supper bell at its mark. The light has gone; the lane's lanterns are lit.
	_pilot.skip_to(17.25)
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Supper", 5.0)
	_check(_said("(The supper bell.)") and GameState.phase == GameState.Phase.SUPPER, "the supper bell at 17:15")
	var lantern := night.get_node(^"Abbey/Street/StreetLanterns").get_child(0) as Candle
	_check(daylight.light < 0.2 and lantern.lit, "the light fails into night, and the lane's lanterns are lit")
	_check(_pilot.director().duties()[0][0] == "17:15  Supper in the refectory, at the supper bell", "the ledger lists the duty at its time")
	_pilot.skip_to(17.5)
	await _pilot.until(func() -> bool:
		return night.get_node(^"People").get_children().all(func(n: Node) -> bool: return not n.has_node(^"Walk")), 30.0)
	_check(night.get_node(^"People").get_children().all(func(n: Node) -> bool: return not n.has_node(^"Walk")),
		"at nightfall the passers-by go home")

	# Supper: he goes to his place; offered the choice, he eats and takes the remedy.
	_choices = [0, 0]
	p.place(_pilot.mark("PorterSeat") + Vector3(0, 0, 0.6), PI)
	await _pilot.use("SupperSeat")
	await _pilot.until(func() -> bool: return _pilot.duty("Bread").enabled, 10.0)
	_check(p.use_input_override, "seated: he can look but not walk")
	_pilot.duty("Bread").interact(p)
	await _pilot.until(func() -> bool: return _pilot.beat() != &"Supper", 10.0)
	_check(_offered.has(PackedStringArray(["(Eat the bread.)", "(Palm the bread.)"])),
		"warned on night 1, he may palm the bread")
	_check(GameState.get_flag(&"n3_ate_bread") == true and GameState.get_flag(&"n3_took_remedy") == true,
		"ate the bread and took Ranulf's remedy")
	_check(_said("(The bread is bitter tonight. The taste stays at the back of your tongue.)") and Talk.history.any(func(h: Array) -> bool: return h[0] == "Ranulf")
		and Talk.history.any(func(h: Array) -> bool: return h[0] == "Thomas" and String(h[1]).contains("Not from him"))
		and Talk.history.any(func(h: Array) -> bool: return h[0] == "Thomas" and String(h[1]).contains("The prior has been asking about you")),
		"the bitter bread; Ranulf offers the remedy, Thomas warns him off it, and says the prior has been asking about him")

	# No HUD: the way to Cole is lit, its doors open, from his seat.
	await _pilot.until(func() -> bool: return _pilot.duty("RelieveCole").enabled, 5.0)
	var gate_lamp: Candle = night.get_node(^"Lamps/GateLamp")
	var refectory_door: Door = night.get_node(^"Abbey/Navigation/SouthRange/Doors/RefectoryW0Door_00")
	var kitchen_door: Door = night.get_node(^"Abbey/Navigation/SouthRange/Doors/KitchenW0Door_00")
	_check(gate_lamp.lit and refectory_door.is_open and kitchen_door.is_open,
		"a lamp burns at the gate, and the doors between supper and the gate stand open")
	_check(_lamp_over(refectory_door) and _lamp_over(kitchen_door), "a lamp hangs over each of those doorways")

	# Taking the gate: Cole goes; shut, barred, the ledger.
	p.place(Vector3(-36.5, 0.05, -2), deg_to_rad(90.0))
	await _pilot.use("RelieveCole")
	await _pilot.use("ShutGate")
	await _pilot.until(func() -> bool: return not gate.is_open(), 3.0)
	await _pilot.use("BarGate")
	await _pilot.use("Ledger")
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Knocks", 5.0)
	_check(GameState.has_flag(&"gate_taken") and GameState.has_flag(&"gate_barred") and GameState.has_flag(&"n3_ledger") and not gate.is_open(),
		"he takes the gate from Cole, shuts and bars it, and opens the ledger")
	await _pilot.until(func() -> bool: return not cole.visible, 20.0)
	_check(not cole.visible, "Cole goes off into the abbey")

	# Knocks: he dozes on the bench; at Walter's hour the knock wakes him.
	# Read, admitted, bedded, written in. Then, drugged, the child-sized knock.
	GameState.snap_dose(60.0)
	GameState.dose_floor = 60.0
	await _pilot.doze()
	var walter := await _pilot.keep_gate(0, [&"box", &"bag"], _answer)
	_check(GameState.hour >= 20.0 and GameState.hour < 20.5 and not _pilot.clock().dozing, "Walter's knock wakes him at 20:00 (%s)" % NightClock.clock_text(GameState.hour))
	var entry: Dictionary = GameState.ledger[-1] if not GameState.ledger.is_empty() else {}
	_check(GameState.get_flag(&"n3_walter") == &"admitted" and walter.lying and String(entry.get("description", "")).contains("incense"),
		"Walter comes up the lane, is let in, shown a bed and written in the ledger")
	await _pilot.doze()
	await _pilot.until(func() -> bool: return _pilot.duty("Grate").enabled, 10.0)
	await _pilot.wake()
	await _pilot.use("Grate")
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Bell", 5.0)
	_check(GameState.has_flag(&"n3_child_knock") and GameState.hour >= 22.0, "at Dose 50+, a small knock low on the gate at 22:00, no one there")
	GameState.dose_floor = 0.0

	# The Matins bell: dozing, he is woken at the mark. A lamp in the tower;
	# the gate's is out. Rung, the night saves.
	await _pilot.doze()
	await _pilot.wake()
	_check(GameState.hour >= 23.75 and GameState.hour < 24.0 and _pilot.duty("BellRope").enabled, "woken for the Matins mark (%s)" % NightClock.clock_text(GameState.hour))
	var tower_lamp: Candle = night.get_node(^"Lamps/TowerLamp")
	var tower_door: Door = night.get_node(^"Abbey/Navigation/Church/Doors/TowerW0Door_01")
	_check(tower_lamp.lit and tower_door.is_open and _lamp_over(tower_door) and not gate_lamp.lit,
		"the bell is due: a lamp in the tower and over its open door; the gate lamp is out")
	_check(not _lamp_over(refectory_door), "the lamps on the way to the gate are gone")
	await _pilot.use("BellRope")
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Choir", 5.0)
	_check(GameState.last_bell == &"matins" and GameState.has_bell_save() and not GameState.has_flag(&"matins_late"),
		"the Matins bell is rung on time and saved")

	# The choir: the incense, and every brother counted.
	GameState.snap_dose(0.0)
	var counted := await _pilot.count_brothers()
	_check(GameState.has_flag(&"n3_headcount") and counted == 11, "counts the eleven brothers in the choir (%d)" % counted)
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
	var crypt_death: DeathScene = night.get_node(^"CryptPilgrim")
	_check(crypt_death.has_played and GameState.has_flag(&"died_crypt_pilgrim") and GameState.souls.has(&"crypt_pilgrim")
		and crypt_death.body != null and _said("(The figure straightens, and turns, and looks straight at you.)"),
		"at the foot of the stair the figure, its back to him, kills a bound pilgrim (fed to the rite), then turns")
	_check(night.get_node(^"BookPage") is Readable, "a page of the cult's book lies by the crypt altar")

	# The chase: into the oven; the jaw; held breath while he checks it.
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Chase", 3.0)
	var oven: HidingSpot = night.get_node(^"Abbey/Navigation/SouthRange/HidingSpots/Oven")
	p.place(oven.exit.global_position, deg_to_rad(90.0))
	p.hide_in(oven)
	await _pilot.until(func() -> bool: return GameState.has_flag(&"n3_body3"), 4.0)
	_check(GameState.has_flag(&"n3_body3") and _said("(Your hand closes on something in the ash. Smooth, curved, with teeth in it. A jaw.)"), "in the oven, a jaw in the ash (body 3)")
	var checked := []
	oven.checked.connect(func(found: bool) -> void: checked.append(found))
	# He holds his breath once the hunter is at the oven, not while he is
	# still coming round the walls to it: a held breath runs out, and the gasp
	# brings the hunter back for a second look.
	await _pilot.until(func() -> bool: return hunter.global_position.distance_to(oven.view.global_position) < 4.5, 60.0)
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

	# However long the night's event takes, the candle waits at the Lauds mark.
	_pilot.skip_to(33.0)
	await _pilot.frames(2)
	_check(GameState.hour == 30.0, "the candle doesn't burn past Lauds before the small hours")

	# The small hours: back at the gate he dozes, and Lauds wakes him.
	await _pilot.until(func() -> bool: return _pilot.beat() == &"SmallHours", 5.0)
	_check(gate_lamp.lit, "the small hours: a lamp at the gate")
	await _pilot.doze()
	await _pilot.wake()
	_check(GameState.hour >= 30.0 and _said("(The Lauds bell. Grey light comes up over the court.)"), "dozing until Lauds (%s)" % NightClock.clock_text(GameState.hour))

	# Dawn: Cole takes the gate; the keys have been moved; sleep.
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Dawn", 5.0)
	_check(cole.visible, "Cole comes back for the gate")
	_pilot.skip_to(30.5)
	await _pilot.frames(2)
	_check(daylight.light > 0.3, "grey morning light")
	p.place(_pilot.mark("ColeGate") + Vector3(1.2, 0, 0), deg_to_rad(90.0))
	await _pilot.use("HandOver")
	await _pilot.until(func() -> bool: return gate.is_open(), 3.0)
	_check(gate.is_open() and not (night.get_node(^"Abbey/Navigation/OuterCourt/Props/GateBar") as Node3D).visible,
		"he gives Cole the gate, and Cole opens it for the day")
	p.place(_pilot.mark("DawnCell"), 0.0)
	await _pilot.until(func() -> bool: return _said("(Your keys are not on their hook.)"), 3.0)
	await _pilot.use("KeysMoved")
	await _pilot.until(func() -> bool: return GameState.has_flag(&"n3_keys_moved"), 3.0)
	_check(GameState.has_flag(&"n3_keys_moved") and GameState.has_flag(&"keys_copied") and GameState.has_note(&"keys_moved"),
		"in his cell, his keys are not where he left them; wax in the teeth: copied")
	var dose := GameState.dose
	await _pilot.use("Sleep")
	await _pilot.until(func() -> bool: return GameState.has_flag(&"night3_done"), 10.0)
	_check(GameState.has_flag(&"night3_done") and GameState.dose < dose and GameState.dose > 0.0,
		"he sleeps through the day; Dose falls, not to zero (%.1f to %.1f)" % [dose, GameState.dose])
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
