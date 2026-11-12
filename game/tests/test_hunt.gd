extends Node
## Hunters (docs/mechanics.md, "Being hunted", "Throwing", "The bell rope",
## "Hunters talk", "The lantern" and "Tests"), in night_base's furniture:
## - the four Suspicion bands: one hunter who doesn't search; one who does;
##   two, one waiting at the gatehouse, and doors locked (his key opens his
##   own); three, all searching;
## - from night 4 they call his name with where it comes from, sober; "a
##   voice" drugged; before night 4 they're silent; a mask that comes off
##   shows the face, and the mask is his to take;
## - a stone thrown onto stone brings a hunter 8 m off to look; onto grass
##   one 6 m off doesn't hear it;
## - the bell out of hours breaks the chase off and costs +10; who comes
##   follows trust and Suspicion (a friend walks him to his cell, the prior
##   questions him, a cultist takes him);
## - a scripted gust gutters the flame and puts it out unless covered; it
##   relights at a candle; no gust in a chase.
## Run: tools/check.sh

const TEST_SAVE := "user://test_hunt_save.tres"

var _fails := 0
var _main: Node
var _pilot: NightPilot
var _pick := 0


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	NightPilot.fresh_night(TEST_SAVE)
	GameState.night = 4
	Talk.line_seconds = 0.05
	Talk.auto_choice = func(_o: PackedStringArray) -> int: return _pick
	_main = NightPilot.main_with("res://game/dev/encounters/death_demo.tscn")
	add_child(_main)
	_pilot = NightPilot.new(_main.get(&"current_level"), _check)
	await _pilot.frames(5)
	var night := _pilot.night
	var p := _pilot.player
	for b: Brother in get_tree().get_nodes_in_group(&"brothers"):
		b.place(null)
	(night.get_node(^"Hallucinations") as Hallucinations).active = false
	GameState.hour = 22.0

	# The bands.
	var hunt: Hunt = night.get_node(^"Hunt")
	_check(Hunt.band(0) == Hunt.Band.WATCHED and Hunt.band(30) == Hunt.Band.SEARCHED and Hunt.band(60) == Hunt.Band.TWO
		and Hunt.band(85) == Hunt.Band.WHOLE, "the four bands: 0, 30, 60, 85")
	GameState.suspicion = 10
	hunt.begin()
	await _pilot.frames(3)
	_check(hunt.hunters.size() == 1 and not hunt.hunters[0].call(&"_may_search"), "0-29: one hunter on his round, who doesn't search")
	GameState.suspicion = 40
	hunt.begin()
	await _pilot.frames(3)
	_check(hunt.hunters.size() == 1 and hunt.hunters[0].call(&"_may_search"), "30-59: one who searches")
	GameState.suspicion = 70
	hunt.begin()
	await _pilot.frames(3)
	var at_gate := hunt.hunters.filter(func(x: Hunter) -> bool: return x.global_position.distance_to(hunt.gatehouse.global_position) < 1.0)
	_check(hunt.hunters.size() == 2 and at_gate.size() == 1, "60-84: two hunters, one waiting at the gatehouse")
	_check(hunt.locks.all(func(d: Door) -> bool: return d.locked) and GameState.has_flag(&"n4_doors_locked"), "and doors he used to pass are locked")
	var charnel: Door = hunt.locks[2]
	var slype: Door = hunt.locks[0]
	_check(charnel.toggle_lock(p) and not charnel.locked and not slype.toggle_lock(p), "his key opens the charnel house; the others need another way round")
	GameState.suspicion = 90
	hunt.begin()
	await _pilot.frames(3)
	_check(hunt.hunters.size() == 3 and hunt.hunters.all(func(x: Hunter) -> bool: return x.always_search), "85+: the whole cult, all searching")
	hunt.end()
	await _pilot.frames(2)
	GameState.suspicion = 0

	# Voices, from night 4.
	var h := (load("res://game/hunting/hunter.tscn") as PackedScene).instantiate() as Hunter
	h.wearer = &"osric"
	night.add_child(h)
	p.place(Vector3(-4.5, 0.05, -16.0), 0.0)
	h.global_position = p.global_position + Vector3(0, 0, 6.0)
	await _pilot.frames(2)
	var voice: HunterVoice = h.get_node(^"Voice")
	GameState.snap_dose(0.0)
	var line := voice.call_out()
	_check(line.ends_with("(behind you, Brother Osric)") and line.begins_with("\""), "night 4, sober: his name, from behind, in Osric's voice: %s" % line)
	GameState.snap_dose(60.0)
	line = voice.call_out()
	_check(line.ends_with("(behind you, a voice)"), "drugged it's only a voice: %s" % line)
	GameState.snap_dose(0.0)
	GameState.night = 3
	h.waiting = true
	h.call(&"_set_state", Hunter.State.CHASE)
	var said := Talk.history.size()
	await _pilot.seconds(12.0)
	_check(not Talk.history.slice(said).any(func(e: Array) -> bool: return String(e[1]).contains("(behind") or String(e[1]).contains("(ahead") \
		or String(e[1]).contains("to your")), "before night 4 they hunt in silence")
	GameState.night = 4
	h.reset()
	h.waiting = true
	# Unmasked.
	var mask := h.unmask()
	_check(h.unmasked and GameState.has_flag(&"unmasked_osric") and mask is Pickup, "the mask comes off: Osric's face, and the mask on the flags")
	mask.interact(p)
	_check(GameState.satchel.has(&"mask"), "and the mask is his to take")
	h.queue_free()
	await _pilot.frames(2)

	# Throwing: stone on stone, 8 m off, brings him to look; on grass, 6 m off, not.
	var listener := (load("res://game/hunting/hunter.tscn") as PackedScene).instantiate() as Hunter
	night.add_child(listener)
	await _pilot.frames(2)
	GameState.satchel.append(&"stone")
	p.place(Vector3(-4.0, 0.05, -26.0), deg_to_rad(-90.0))
	p.head.rotation.x = deg_to_rad(-20.0)
	listener.global_transform = Transform3D(Basis.IDENTITY, Vector3(8.0, 0.05, -24.0))
	listener.reset()
	listener.global_transform = Transform3D(Basis.IDENTITY, Vector3(8.0, 0.05, -24.0))
	var thrown := p.throw()
	await _pilot.until(func() -> bool: return thrown.has_landed, 3.0)
	var to_it := listener.global_position.distance_to(thrown.global_position)
	await _pilot.frames(3)
	_check(thrown.has_landed and thrown.surface == "stone" and to_it < Thrown.heard_within("stone"),
		"a stone lands on the flags %.1f m from him" % to_it)
	_check(listener.state == Hunter.State.INVESTIGATE, "and he goes to look")
	GameState.satchel.append(&"stone")
	p.place(Vector3(-4.5, 0.05, -16.0), PI)
	p.head.rotation.x = deg_to_rad(-30.0)
	thrown = p.throw()
	listener.reset()
	await _pilot.until(func() -> bool: return thrown.has_landed, 3.0)
	listener.global_transform = Transform3D(Basis.IDENTITY, thrown.global_position + Vector3(6.0, 0, 0))
	listener.call(&"_set_state", Hunter.State.PATROL)
	Earshot.make(thrown, thrown.global_position, Thrown.heard_within(thrown.surface), thrown)
	await _pilot.frames(3)
	_check(thrown.surface == "grass" and Thrown.heard_within("grass") == 4.0 and listener.state == Hunter.State.PATROL,
		"on the garth's grass, 6 m off, he doesn't hear it (%s)" % thrown.surface)
	listener.queue_free()
	await _pilot.frames(2)

	# The bell out of hours.
	var bell: OffHoursBell = night.get_node(^"OffHoursBell")
	var chaser := (load("res://game/hunting/hunter.tscn") as PackedScene).instantiate() as Hunter
	night.add_child(chaser)
	await _pilot.frames(2)
	p.place(bell.global_position + Vector3(0.6, 0, 0), 0.0)
	chaser.global_position = p.global_position + Vector3(0, 0, 8.0)
	chaser.chase()
	await _pilot.frames(2)
	GameState.suspicion = 0
	_check(OffHoursBell.who_comes() == &"edwin", "Edwin trusts him (50): Edwin would come")
	await bell.ring(p)
	_check(chaser.state == Hunter.State.PATROL and GameState.suspicion == 10, "the bell: the chase breaks off, Suspicion +10")
	_check(bell.last == &"edwin" and p.global_position.distance_to(night.get_node(^"Marks/WakeCell").global_position) < 0.5,
		"Edwin comes and walks him to his cell")
	GameState.change_trust(&"edwin", -30)
	_check(OffHoursBell.who_comes() == &"hugh", "with no friend who trusts him 40, below 60 the prior comes")
	p.place(bell.global_position + Vector3(0.6, 0, 0), 0.0)
	await bell.ring(p)
	_check(bell.last == &"hugh" and GameState.suspicion == 20, "the prior questions him")
	GameState.suspicion = 65
	_check(OffHoursBell.who_comes() == &"cultist", "at 60 or more a cultist reaches him first")
	chaser.queue_free()

	# A gust: on its night, the flame gutters and goes out unless covered.
	var gust: Gust = night.get_node(^"Gusts/TowerStair")
	GameState.night = 2
	var lantern := p.lantern
	p.place(gust.global_position - Vector3(0, 1.45, 0), 0.0)
	await _pilot.frames(3)
	_check(gust.blown and lantern.gusting > 0.0, "night 2, on the tower stair: a gust, the flame gutters")
	await _pilot.seconds(1.7)
	_check(lantern.out and not lantern.light.visible, "uncovered, it goes out")
	var candle: Candle = night.get_node(^"SupperCandle0")
	candle.set_meta(&"auto", true)
	candle.interact(p)
	await _pilot.seconds(1.8)
	_check(not lantern.out and lantern.light.visible, "held to a candle, it lights again")
	gust.blown = false
	Input.action_press(&"cover_lantern")
	gust.blow(p)
	await _pilot.seconds(1.7)
	Input.action_release(&"cover_lantern")
	_check(not lantern.out, "covered in time, it stays lit")
	p.place(Vector3(-4.5, 0.05, -16), 0.0)
	await _pilot.frames(2)
	gust.blown = false
	var hunter2 := (load("res://game/hunting/hunter.tscn") as PackedScene).instantiate() as Hunter
	night.add_child(hunter2)
	await _pilot.frames(2)
	hunter2.global_position = p.global_position + Vector3(0, 0, 10)
	hunter2.chase()
	p.place(Vector3(-4.5, 0.05, -16), 0.0)
	await _pilot.frames(2)
	p.place(gust.global_position - Vector3(0, 1.45, 0), 0.0)
	await _pilot.frames(3)
	_check(not gust.blown, "no gust in a chase")
	hunter2.queue_free()

	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	Talk.auto_choice = Callable()
	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
