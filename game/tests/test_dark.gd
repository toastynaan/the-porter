extends Node
## The dark between the chases, and clean food (docs/log/full-game-run.md,
## "Scares between chases", "The cat"; docs/systems/mechanics.md, "The drug, and
## food" and "Tests": eating ends hunger), on night 3's furniture:
## - the cat follows him at night, stares into the dark (at a man, if one
##   is near), and runs before the demon when the animals go quiet;
## - steps on the floor above him under a roof, not in the open; a light
##   ahead goes out; a jump scare once a night, and again the next night;
## - windfall apples, a third of them each night; eaten hungry, an apple ends
##   his hunger; not hungry, it goes in the satchel, and the satchel feeds
##   him later; Mab gives him a heel of bread for alms.
## Run: tools/check.sh

const TEST_SAVE := "user://test_dark_save.tres"

var _fails := 0
var _pilot: NightPilot


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	NightPilot.fresh_night(TEST_SAVE)
	Talk.line_seconds = 0.05
	Talk.auto_choice = func(_o: PackedStringArray) -> int: return 2
	var main := NightPilot.main_with("res://game/chapters/night3/night3.tscn")
	add_child(main)
	_pilot = NightPilot.new(main.get(&"current_level"), _check)
	_pilot.shorten()
	await _pilot.frames(5)
	var night := _pilot.night
	var p := _pilot.player
	await _pilot.until(func() -> bool: return not p.controls_locked, 5.0)

	# The cat follows him.
	var cat: Cat = night.get_node(^"Cat")
	p.place(Vector3(-30.0, 0.05, 6.0), 0.0)
	await _pilot.until(func() -> bool: return cat.global_position.distance_to(p.global_position) < Cat.GAP.y + 0.3, 20.0)
	_check(cat.global_position.distance_to(p.global_position) < Cat.GAP.y + 0.3, "the cat comes to him and keeps a few steps off")
	# It stares into the dark, at a man if one is near.
	var hunter: Hunter = night.get_node(^"Hunter")
	hunter.stand_still()
	hunter.global_position = cat.global_position + Vector3(4.0, 0, 0)
	cat.stare()
	_check(cat.mode == Cat.Mode.STARE and cat.staring_at.distance_to(hunter.global_position) < 0.1, "it stares into the dark, at a man standing there")
	hunter.reset()
	await _pilot.seconds(4.5)
	_check(cat.mode == Cat.Mode.FOLLOW, "and comes on again")
	_check(cat.global_position.distance_to(p.global_position) > 0.5, "it never gets under his feet")
	# The animals go quiet before the demon: it runs.
	get_tree().call_group(&"room_tone", &"set_quiet", true)
	_check(cat.mode == Cat.Mode.FLEE, "the animals go quiet: the cat bolts")
	await _pilot.until(func() -> bool: return cat.mode == Cat.Mode.GONE, 8.0)
	_check(cat.mode == Cat.Mode.GONE and not cat.visible, "and is gone")
	get_tree().call_group(&"room_tone", &"set_quiet", false)
	_check(cat.mode == Cat.Mode.FOLLOW and cat.visible, "it comes back after")

	# Steps overhead, under a roof only.
	var scares: Scares = night.get_node(^"Scares")
	p.place(Vector3(16.0, 0.05, -12.0), 0.0)
	_check(scares.steps_above(), "under the dormitory: steps on the floor over his head")
	p.place(Vector3(0.0, 0.05, -16.0), 0.0)
	_check(not scares.steps_above(), "in the open garth: none")
	# A light ahead goes out.
	p.place(Vector3(0.0, 0.05, 2.5), 0.0)
	_pilot.face(Vector3(-3.0, 0.95, -1.5))
	var lit := (night.get_node(^"SupperCandle0") as Candle).lit or (night.get_node(^"SupperCandle1") as Candle).lit
	_check(lit and scares.light_out_ahead(), "a candle ahead gutters")
	await _pilot.seconds(1.0)
	_check(not (night.get_node(^"SupperCandle0") as Candle).lit or not (night.get_node(^"SupperCandle1") as Candle).lit, "and goes out")
	# A jump scare once a night.
	p.place(Vector3(-30.0, 0.05, 6.0), 0.0)
	_check(scares.jump(&"body_drop"), "a body drops in front of him")
	_check(not scares.jump(&"face_at_grille"), "but only one jump scare a night")
	GameState.begin_chapter(5, 4)
	_check(scares.jump(&"face_at_grille"), "the next night, a face at the grille")
	GameState.night = 3

	# Windfalls: a third of the apples each night.
	var windfalls: Windfalls = night.get_node(^"Windfalls")
	var shown := windfalls.get_children().filter(func(c: Node) -> bool: return c is Pickup and (c as Pickup).visible)
	_check(shown.size() == 3, "three windfall apples tonight")
	var apple: Pickup = shown[0]
	# Hungry, he eats it at once.
	GameState.set_flag(&"hungry")
	apple.interact(p)
	_check(not GameState.is_hungry() and GameState.has_flag(&"n3_ate_clean") and not apple.visible, "hungry, the apple ends his hunger")
	# Not hungry, it goes in the satchel; later the satchel feeds him.
	var second: Pickup = shown[1]
	second.interact(p)
	_check(GameState.satchel.has(&"apple"), "not hungry, it goes in his satchel")
	GameState.set_flag(&"hungry")
	var satchel: SatchelView = main.get_node(^"UI/Satchel")
	satchel.set_showing(true)
	_check(satchel.eat_food() and not GameState.is_hungry() and not GameState.satchel.has(&"apple"), "later, hungry, he eats it from the satchel")
	satchel.set_showing(false)
	# Mab's bread, for alms.
	var mab: Talker = night.get_node(^"People/Mab/Talker")
	GameState.hour = 16.5
	GameState.set_phase(GameState.Phase.DUSK)
	p.place(Vector3(-40.4, 0.05, 0.9), deg_to_rad(90.0))
	await _pilot.talk(mab, [2, -1], [-1])
	_check(GameState.satchel.has(&"mab_bread") and GameState.trust_of(&"mab") == 5, "alms for Mab: a heel of bread, and she thinks better of him")

	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	Talk.auto_choice = Callable()
	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
