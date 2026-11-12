extends Node
## The drug and the dark (design doc, "Effect tiers"; docs/mechanics.md, "The
## drug, and food", "The minimal HUD"; M10's "each tier's events fire, fakes
## leave nothing"), in night_base's furniture (death_demo.tscn):
## - the tiers: clear below 25; whispers, steps behind and his name at 25+;
##   a shape at the edge of view and a face in the grain at 50+; hooves that
##   stop short and a death that never happened at 75+; none at Dose 0;
## - each visual event leaves nothing once he looks; a fake death leaves no
##   body, no blood and no soul;
## - carvings turn their heads only unseen, from 50; the dead stand in the
##   choir at Matins from 75; the flame bends toward the demon from 25; the
##   walls breathe from 75; reverb grows from 25;
## - Dose never touches his body: same walk, same look;
## - the HUD lies once, only on night 5 or 6 at 75+;
## - on night 5 a crypt candle lights itself when he looks at it.
## Run: tools/check.sh

const TEST_SAVE := "user://test_drug_save.tres"

var _fails := 0
var _main: Node
var _pilot: NightPilot
var _h: Hallucinations


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	NightPilot.fresh_night(TEST_SAVE)
	GameState.night = 5
	Talk.line_seconds = 0.05
	_main = NightPilot.main_with("res://game/dev/encounters/death_demo.tscn")
	add_child(_main)
	_pilot = NightPilot.new(_main.get(&"current_level"), _check)
	await _pilot.frames(5)
	var night := _pilot.night
	var p := _pilot.player
	_h = night.get_node(^"Hallucinations")
	for b: Brother in get_tree().get_nodes_in_group(&"brothers"):
		b.place(null)

	# The tiers.
	_check(Hallucinations.tier(10.0) == Hallucinations.Tier.CLEAR and Hallucinations.allowed(10.0).is_empty(), "below 25: clear")
	_check(Hallucinations.allowed(30.0) == [&"whisper", &"steps_behind", &"name"], "25+: his ears")
	_check(Hallucinations.allowed(60.0).has(&"edge_shape") and Hallucinations.allowed(60.0).has(&"face_in_grain")
		and not Hallucinations.allowed(60.0).has(&"fake_death"), "50+: his eyes too")
	_check(Hallucinations.allowed(80.0).size() == 7, "75+: and lies")

	# They fire on their own when drugged, never sober.
	p.place(Vector3(-2.0, 0.05, -26.0), deg_to_rad(-90.0))
	GameState.snap_dose(0.0)
	_h.set(&"_timer", 0.05)
	await _pilot.seconds(1.0)
	_check(_h.history.is_empty(), "at Dose 0 nothing fires")
	GameState.snap_dose(30.0)
	GameState.dose_floor = 30.0
	_h.set(&"_timer", 0.05)
	await _pilot.seconds(0.5)
	_check(_h.history.size() == 1 and _h.history[0][0] in Hallucinations.allowed(30.0), "at Dose 30 one of his ears' events fires (%s)" % [_h.history])

	# His name; in Edwin's voice once Edwin is dead.
	_h.fire(&"name")
	await _pilot.frames(2)
	_check(_said("(Someone calls your name.)"), "his name called")
	GameState.set_flag(&"died_edwin")
	_h.fire(&"name")
	await _pilot.frames(2)
	_check(_said("(Edwin's voice, calling your name.)"), "in Edwin's voice, once Edwin is dead")
	GameState.flags.erase(&"died_edwin")

	# A shape at the edge of view, gone when he looks.
	GameState.snap_dose(60.0)
	GameState.dose_floor = 60.0
	p.place(Vector3(0.0, 0.05, -16.0), 0.0)
	var shaped := _h.fire(&"edge_shape")
	var shape := _h.get_child(_h.get_child_count() - 1) as Node3D if shaped else null
	_check(shaped and shape is CharacterLook and absf(ViewCheck.off_centre(p.camera, shape.global_position + Vector3.UP * 1.5) - 48.0) < 15.0,
		"50+: a shape at the edge of his view")
	if shape:
		_pilot.face(shape.global_position + Vector3.UP * 1.5)
	await _pilot.seconds(0.3)
	_check(not is_instance_valid(shape) or shape.is_queued_for_deletion(), "he looks: it's gone")

	# A face in the grain of a door, gone when he stares at it.
	p.place(Vector3(-34, 0.05, -1.6), PI)
	var faced := _h.fire(&"face_in_grain")
	var decals := _decals()
	_check(faced and decals.size() == 1, "a face in the grain of the door behind him")
	_pilot.face(decals[0].global_position if not decals.is_empty() else Vector3.ZERO)
	await _pilot.seconds(1.8)
	_check(_decals().is_empty(), "he stares at it: it's only grain")

	# A death that never happened.
	GameState.snap_dose(80.0)
	GameState.dose_floor = 80.0
	var count := GameState.count
	var marks := GameState.marks.size()
	p.place(Vector3(0.0, 0.05, -26.0), deg_to_rad(-90.0))
	_check(_h.fire(&"fake_death"), "75+: a death in front of him")
	await _pilot.seconds(2.5)
	var deaths := _h.get_children().filter(func(c: Node) -> bool: return c is DeathScene)
	var fake: DeathScene = deaths[-1] if not deaths.is_empty() else null
	_check(fake != null and fake.fake and fake.body != null, "a body on the flags")
	_pilot.face(p.global_position + Vector3(-10, 0, 0))
	await _pilot.seconds(1.6)
	_check(fake.body == null and GameState.count == count and GameState.marks.size() == marks,
		"he looks away and back: no body, no blood, no soul")
	_check(_h.fire(&"fake_rush") and _h.fire(&"whisper") and _h.fire(&"steps_behind"), "hooves that stop short, a whisper, steps")

	# Carvings turn their heads only unseen.
	var carving: Carving = night.get_node(^"Carvings/Choir")
	GameState.dose_floor = 0.0
	GameState.snap_dose(20.0)
	p.place(carving.global_position + Vector3(1.5, 0, 2.3), 0.0)
	_pilot.face(carving.head.global_position)
	await _pilot.frames(3)
	_check(not carving.turned, "below 50 the saint looks ahead")
	GameState.snap_dose(60.0)
	await _pilot.frames(3)
	_check(not carving.turned, "at 60, watched, it doesn't move")
	_pilot.face(p.global_position + Vector3(10, 0, 0))
	await _pilot.frames(3)
	_pilot.face(carving.head.global_position)
	await _pilot.frames(2)
	_check(carving.turned, "he looks away and back: its head has turned to him")

	# The dead stand in the choir at Matins from 75.
	var dead: DeadInChoir = night.get_node(^"DeadInChoir")
	GameState.set_flag(&"died_edwin")
	GameState.set_phase(GameState.Phase.MATINS)
	p.place(Vector3(13, 0.05, -40.0), PI)
	GameState.snap_dose(60.0)
	await _pilot.frames(3)
	_check(dead.standing() == 0, "at 60 the choir has only the living")
	GameState.snap_dose(80.0)
	await _pilot.frames(3)
	_check(dead.standing() == 1, "at 80 dead Edwin stands in his place")
	GameState.snap_dose(40.0)
	await _pilot.frames(3)
	_check(dead.standing() == 0, "and leaves nothing as the Dose falls")
	GameState.set_phase(GameState.Phase.DUSK)
	GameState.flags.erase(&"died_edwin")

	# The flame bends toward the demon; the walls breathe; reverb.
	var costume := (load("res://game/demon/demon_costume.tscn") as PackedScene).instantiate() as DemonCostume
	night.add_child(costume)
	p.place(Vector3(-2.0, 0.05, -16.0), 0.0)
	costume.global_position = p.global_position + Vector3(3.0, 0, 0)
	GameState.snap_dose(0.0)
	await _pilot.seconds(1.5)
	var lantern := p.lantern
	_check(lantern.bent.length() < 0.02, "sober the flame stands straight")
	GameState.snap_dose(60.0)
	await _pilot.seconds(1.5)
	_check(lantern.bent.length() > 0.3, "drugged it bends toward the demon (%.2f)" % lantern.bent.length())
	costume.queue_free()
	var mat := (_main.get_node(^"Screen") as CanvasItem).material as ShaderMaterial
	GameState.snap_dose(50.0)
	await _pilot.frames(2)
	_check(float(mat.get_shader_parameter(&"breathe")) == 0.0, "at 50 the walls are still")
	GameState.snap_dose(95.0)
	await _pilot.frames(2)
	_check(float(mat.get_shader_parameter(&"breathe")) > 0.004, "at 95 the walls breathe")
	_check(_reverb_wet() > 0.3, "and everything rings (reverb %.2f)" % _reverb_wet())

	# His body is his own at any Dose.
	p.place(Vector3(-30, 0.05, 8), PI)
	Input.action_press(&"move_forward")
	await _pilot.seconds(2.0)
	Input.action_release(&"move_forward")
	var speed := Vector2(p.velocity.x, p.velocity.z).length()
	_check(absf(speed - Player.WALK_SPEED) < 0.05, "at Dose 95 he still walks at 1.4 m/s (%.2f)" % speed)
	_check(p.call(&"_turn", Vector2(100, 40)) == Vector2(100, 40), "and his look turns the same (Dose only in his senses)")

	# The HUD lies once: night 5 or 6, Dose 75+.
	var false_door: FalseDoor = night.get_node(^"FalseDoor")
	GameState.dose_floor = 0.0
	GameState.snap_dose(60.0)
	_check(not false_door.telling(), "at 60 the wall is blank")
	GameState.night = 4
	GameState.snap_dose(80.0)
	_check(not false_door.telling(), "on night 4, even at 80, the wall is blank")
	GameState.night = 5
	_check(false_door.telling(), "on night 5 at 80 there's a door in the wall")
	p.place(false_door.global_position + false_door.global_basis.z * -1.2 + Vector3(0, 0, 0), 0.0)
	_pilot.face(false_door.global_position + Vector3.UP * 1.2)
	await _pilot.frames(4)
	var interactor: Interactor = p.get_node(^"Head/LookBack/Camera/Interactor")
	_check(interactor.focused == false_door and Outline.is_on(false_door), "with the outline on it, in reach")
	false_door.interact(p)
	await _pilot.seconds(1.6)
	_check(GameState.has_flag(&"hud_lie_told") and not is_instance_valid(false_door), "it opens on stone, and is gone")

	# Night 5: a candle in the crypt lights itself.
	var candle: SelfLitCandle = night.get_node(^"SelfLitCandle")
	GameState.snap_dose(0.0)
	p.place(candle.global_position + Vector3(-2.5, 0.0, -0.5), 0.0)
	_check(not candle.candle.lit, "a cold candle in the crypt")
	_pilot.face(candle.candle.global_position + Vector3.UP * 0.1)
	await _pilot.seconds(1.3)
	_check(candle.candle.lit and GameState.has_flag(&"candle_lit_itself"), "he looks at it, sober, and it lights itself")

	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


func _decals() -> Array[Node]:
	var out: Array[Node] = []
	for d: Door in get_tree().get_nodes_in_group(&"doors"):
		for c in d.get_children():
			if c is Decal and not c.is_queued_for_deletion():
				out.append(c)
	return out


func _reverb_wet() -> float:
	for i in AudioServer.get_bus_effect_count(0):
		var e := AudioServer.get_bus_effect(0, i) as AudioEffectReverb
		if e:
			return e.wet
	return 0.0


func _said(text: String) -> bool:
	return Talk.history.any(func(h: Array) -> bool: return h[1] == text)


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
