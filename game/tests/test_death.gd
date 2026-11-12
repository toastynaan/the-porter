extends Node
## Deaths (docs/full-game-run.md, "Deaths and bodies"; M9's "each style plays
## in a test scene"), in game/dev/encounters/death_demo.tscn through main.tscn:
## an implied death sober (a man in a mask, a cry, a lantern, a body that
## falls as a ragdoll and settles, a pool of blood), a gory one drugged (the
## demon, blood up the wall), the throat sober (blood flying, a spray); the
## killer gone once the porter looks away; the rite fed a soul for each, and
## a candle lit in the crypt for each; a hallucination at Dose 80 that leaves
## nothing once he looks away and feeds nothing; bodies and blood still there
## after a reload; and the dawn scrubbing what proves men did it.
## Run: tools/check.sh

const TEST_SAVE := "user://test_death_save.tres"

var _fails := 0
var _main: Node
var _pilot: NightPilot


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	NightPilot.fresh_night(TEST_SAVE)
	GameState.night = 4
	Talk.line_seconds = 0.05
	_main = NightPilot.main_with("res://game/dev/encounters/death_demo.tscn")
	add_child(_main)
	await _start()
	var night := _pilot.night
	var candles: RiteCandles = night.get_node(^"RiteCandles")
	_check(GameState.count == 0 and candles.lit_count() == 0, "no souls yet, and no candle lit in the crypt")

	# Implied, sober.
	var implied: DeathScene = night.get_node(^"Deaths/Implied")
	GameState.snap_dose(0.0)
	_watch(implied, Vector3(5.0, 0, 0.5))
	await implied.play()
	var costume := implied.killer as DemonCostume
	_check(costume != null and costume.tall < 0.05, "implied, sober: the killer is a man in a mask")
	_check(implied.body != null and implied.body.dead, "the victim falls as a ragdoll")
	_check(GameState.has_flag(&"died_demo_implied") and GameState.count == 1 and GameState.souls.has(&"demo_implied"),
		"the death feeds the rite a soul (count %d)" % GameState.count)
	_check(BloodMarks.count(&"pool") == 1 and BloodMarks.count(&"spray") == 0, "implied: a pool of blood, nothing up the wall")
	await _pilot.seconds(4.0)
	_check(implied.body.centre().y < implied.global_position.y + 0.7, "the body comes to rest on the flags (chest %.2f m)" %
		(implied.body.centre().y - implied.global_position.y))
	_check(candles.lit_count() == 1, "a candle is lit in the crypt for it")
	_pilot.face(_pilot.player.global_position + Vector3(0, 0, 10))
	await _pilot.seconds(1.0)
	_check(implied.killer == null and implied.body != null, "the killer is gone once he looks away; the body stays")

	# Gory, drugged: the demon.
	var gory: DeathScene = night.get_node(^"Deaths/Gory")
	GameState.snap_dose(75.0)
	_watch(gory, Vector3(3.2, 0, -0.8))
	await gory.play()
	costume = gory.killer as DemonCostume
	_check(costume != null and costume.tall > 0.95, "gory, at Dose 75: the demon does it (%.2f)" % (costume.tall if costume else -1.0))
	_check(BloodMarks.count(&"spray") == 1 and BloodMarks.count(&"pool") == 2, "gory: blood up the wall, and a pool")
	_check(GameState.count == 2, "a second soul")

	# The throat, sober.
	var throat: DeathScene = night.get_node(^"Deaths/Throat")
	GameState.snap_dose(0.0)
	_watch(throat, Vector3(0, 0, 4.0))
	var sprays := BloodMarks.count(&"spray")
	await throat.play()
	var particles := throat.find_children("*", "CPUParticles3D", true, false)
	_check(not particles.is_empty() and BloodMarks.count(&"spray") == sprays + 1, "the throat: blood flying through the light")
	_check(GameState.count == 3 and candles.lit_count() == 3, "three souls, three candles")

	# A hallucination at Dose 80.
	var fake: DeathScene = night.get_node(^"Deaths/Fake")
	GameState.snap_dose(80.0)
	var marks := GameState.marks.size()
	_watch(fake, Vector3(-5.0, 0, 0))
	await fake.play()
	_check(fake.body != null and fake.killer != null, "at Dose 80 a death that looks the same")
	_check(GameState.count == 3 and not GameState.has_flag(&"died_demo_fake") and GameState.marks.size() == marks,
		"but it feeds nothing and keeps no blood")
	_pilot.face(_pilot.player.global_position - Vector3(10, 0, 0))
	await _pilot.seconds(1.6)
	var left := fake.get_children().filter(func(c: Node) -> bool: return (c is Corpse or c.is_in_group(&"placeholder") or c is DemonCostume) and not c.is_queued_for_deletion())
	_check(fake.body == null and fake.killer == null and left.is_empty() and GameState.has_flag(&"fake_seen_demo_fake"),
		"he looks away and back: nothing there, no body, no blood (%d left)" % left.size())

	# A reload keeps the bodies where they fell, and the blood.
	GameState.snap_dose(0.0)
	GameState.ring_bell(&"start")
	GameState.load_last_bell()
	_main.call(&"reload_level")
	await _start()
	night = _pilot.night
	var holder: BloodMarks = night.get_node(^"BloodMarks")
	implied = night.get_node(^"Deaths/Implied")
	await _pilot.frames(3)
	_check(holder.get_child_count() == GameState.marks.size() and GameState.marks.size() == 5,
		"after a reload the blood is where it was (%d marks)" % holder.get_child_count())
	_check(implied.has_played and implied.body != null, "and the body lies where it fell")
	_check((night.get_node(^"RiteCandles") as RiteCandles).lit_count() == 3, "and the crypt still keeps the count")

	# Dawn: the cult scrubs what proves men did it.
	BloodMarks.add(get_tree(), &"drag", Transform3D(Basis.IDENTITY, Vector3(-30, 0.05, -20)), &"demo_gory")
	BloodMarks.add(get_tree(), &"print", Transform3D(Basis.IDENTITY, Vector3(-29, 0.05, -19)), &"demo_gory")
	_check(BloodMarks.count() == 7, "drag marks and a boot print in blood")
	BloodMarks.clean_at_dawn(get_tree())
	await _pilot.frames(2)
	_check(BloodMarks.count(&"drag") == 0 and BloodMarks.count(&"print") == 0 and BloodMarks.count() == 5,
		"at dawn they're scrubbed; the pools and sprays are missed")

	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


func _start() -> void:
	_pilot = NightPilot.new(_main.get(&"current_level"), _check)
	await _pilot.frames(5)


## Stands the porter `offset` from the death, looking at it.
func _watch(death: DeathScene, offset: Vector3) -> void:
	_pilot.player.place(death.global_position + offset, 0.0)
	_pilot.face(death.global_position + Vector3.UP * 1.3)
	await _pilot.frames(2)


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
