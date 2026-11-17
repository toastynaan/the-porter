extends Node
## Night 0 out of order (docs/places/prologue.md, "Night 0, the Cross Keys"):
## the gate, Mab and Agnes can be come to in any order, and the bed is his as
## soon as Agnes has given him the room. Each route starts where the carter
## sets him down (SceneSelect's start at `Arrive`):
## - Mab before the knock: she has called to him, and opens with "No use
##   knocking, brother" ("I could have told you" is for after a knock); she
##   sends him to the Keys, the knock is no longer wanted, and the flame goes
##   to Agnes;
## - telling Agnes the gate is shut: she says she has the one bed, and it is
##   his without asking again;
## - no knock, no Mab and no bed asked for (an ale from Agnes): at eight the
##   gate's beat ends, the bell strikes and he thinks of Agnes;
## - straight to Agnes, with no knock and no word from Mab: she gives him the
##   room, the knock is no longer wanted, and the bed starts the window.
## And leaving the night while the window plays (as he crosses to it, and
## during the killing) stops its loops with no script error.
## Run: tools/check.sh

const TEST_SAVE := "user://test_night0_routes_save.tres"
const TEST_SETTINGS := "user://test_night0_routes_settings.cfg"

var _fails := 0
var _main: Node
var _flow: GameFlow
var _answer := [-1]


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	GameState.save_path = TEST_SAVE
	for path in [TEST_SAVE, GameState.quiet_path()]:
		DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
	Settings.path = TEST_SETTINGS
	Settings.finished = false
	Talk.line_seconds = 0.05
	# Only what the route picks: until then the question waits.
	Talk.auto_choice = func(_options: PackedStringArray) -> int: return _answer[0]
	_main = load("res://game/core/render/main.tscn").instantiate()
	add_child(_main)
	_flow = _main.get_node(^"Game")
	await _frames(5)

	# Mab before the knock.
	var pilot := await _set_down()
	var p := pilot.player
	var night := pilot.night
	var knock := pilot.duty("KnockGate")
	var inn_bed := pilot.duty("InnBed")
	await _until(func() -> bool: return knock.enabled, 5.0)
	_check(knock.enabled and not inn_bed.enabled, "set down in the lane: the knock is wanted, the bed isn't his")
	var mab := night.get_node(^"People/Mab") as VisitorNPC
	p.place(mab.global_position + Vector3(-1.3, 0.0, 0.0), deg_to_rad(-90.0))
	# She calls for alms as he comes near.
	await _until(func() -> bool: return GameState.has_flag(&"hailed_n0_mab") and Talk.quiet(), 5.0)
	_check(_said("Mab", "Alms, brother."), "Mab calls to him as he comes near the gate")
	await pilot.talk(mab.get_node(^"Talker") as Talker, [-1], _answer)
	_check(GameState.has_flag(&"n0_sent_to_inn") and _said("Mab", "No use knocking, brother.") and not _said("Mab", "I could have told you."),
		"Mab, before any knock: no use knocking, he'll have to stay at the Keys (not \"I could have told you\")")
	var agnes := night.get_node(^"People/Agnes") as VisitorNPC
	await _until(func() -> bool: return pilot.beat() == &"Inn" and agnes.is_in_group(&"glyph_targets"), 5.0)
	_check(pilot.beat() == &"Inn" and not knock.enabled and agnes.is_in_group(&"glyph_targets"),
		"the knock is no longer wanted, and the flame goes to Agnes (%s)" % pilot.beat())

	# Agnes, told the gate is shut.
	p.place(agnes.global_position + Vector3(1.3, 0.0, 0.0), deg_to_rad(90.0))
	await _frames(3)
	await pilot.talk(agnes.get_node(^"Talker") as Talker, [1, 1], _answer)
	_check(_said("Agnes", "So it's a bed you want, and I've the one.") and GameState.has_flag(&"n0_room"),
		"told the gate is shut, Agnes says she has the one bed, and it is his")
	await _until(func() -> bool: return pilot.beat() == &"Window", 5.0)
	_check(pilot.beat() == &"Window" and inn_bed.enabled, "and his bed is wanted (%s)" % pilot.beat())

	# No knock, no Mab, no bed asked for: at eight the bell comes all the same.
	pilot = await _set_down()
	p = pilot.player
	night = pilot.night
	knock = pilot.duty("KnockGate")
	await _until(func() -> bool: return knock.enabled, 5.0)
	agnes = night.get_node(^"People/Agnes") as VisitorNPC
	p.place(agnes.global_position + Vector3(1.3, 0.0, 0.0), deg_to_rad(90.0))
	await _frames(3)
	await pilot.talk(agnes.get_node(^"Talker") as Talker, [2], _answer)
	_check(pilot.beat() == &"Arrive" and not GameState.has_flag(&"n0_room") and GameState.drink > 0.5,
		"an ale from Agnes and no bed asked for: the knock is still what's wanted (%s)" % pilot.beat())
	pilot.skip_to(20.5)
	var eight := func() -> bool: return _said("", "(A bell somewhere in the city strikes eight.")
	await _until(func() -> bool: return eight.call() and Talk.quiet(), 15.0)
	_check(is_equal_approx(GameState.hour, 20.0) and pilot.beat() == &"Inn" and not knock.enabled and agnes.is_in_group(&"glyph_targets"),
		"at eight the gate is behind him: the knock is no longer wanted, the flame goes to Agnes (%s, %.2f)" % [pilot.beat(), GameState.hour])
	_check(eight.call() and not _said("", "(Warm light and noise across the lane."),
		"the bell strikes eight and he thinks of Agnes; nothing tells him the Keys is across the lane")

	# Straight to Agnes: no knock, no Mab.
	pilot = await _set_down()
	p = pilot.player
	night = pilot.night
	knock = pilot.duty("KnockGate")
	inn_bed = pilot.duty("InnBed")
	await _until(func() -> bool: return knock.enabled, 5.0)
	agnes = night.get_node(^"People/Agnes") as VisitorNPC
	p.place(agnes.global_position + Vector3(1.3, 0.0, 0.0), deg_to_rad(90.0))
	await _frames(3)
	await pilot.talk(agnes.get_node(^"Talker") as Talker, [0, 1], _answer)
	_check(GameState.has_flag(&"n0_room") and _said("Agnes", "There's the room at the top."), "Agnes, before any knock: she gives him the room at the top")
	await _until(func() -> bool: return pilot.beat() == &"Window", 5.0)
	_check(pilot.beat() == &"Window" and inn_bed.enabled and not knock.enabled,
		"the night goes on to his bed: it is wanted, and the knock no longer (%s)" % pilot.beat())
	_check(not _said("", "(Warm light and noise across the lane."), "he is in the Keys already: nothing tells him it's across the lane")
	var interactor := get_tree().get_first_node_in_group(&"interactor") as Interactor
	p.place(inn_bed.global_position + Vector3(0.0, 0.0, -1.4), 0.0)
	await _frames(3)
	pilot.face(inn_bed.global_position + Vector3(0.0, 0.5, 0.0))
	await _frames(3)
	_check(interactor.focused == inn_bed, "up in his room, he looks at the bed")
	if interactor.focused:
		interactor.focused.interact(p)
	await _frames(3)
	_check(GameState.has_flag(&"n0_lay_down") and not _said("", "Nobody has let it to you yet"),
		"using it starts the window; nothing says the bed isn't his")

	# Leaving the night while the window plays (back to the title, another
	# scene): its loops stop with it, with no script error (check.sh fails on one).
	var window_night := night.get_instance_id()
	await pilot.seconds(0.4)
	_check(p.controls_locked and pilot.beat() == &"Window", "he is crossing to the window")
	await _set_down()
	await pilot.seconds(1.0)
	_check(not is_instance_id_valid(window_night) and _beat() == &"Arrive", "left mid-walk, that night is gone and the next begins (%s)" % _beat())
	await _until(func() -> bool: return _said("", "(The gate is shut and barred."), 5.0)
	_flow.start_at(0, &"Window")
	await _until(func() -> bool: return _beat() == &"Window", 10.0)
	pilot = NightPilot.new(_level(), _check)
	pilot.shorten()
	var death := pilot.night.get_node(^"WindowKilling") as DeathScene
	await pilot.use("InnBed")
	await _until(func() -> bool: return is_instance_valid(death.killer), 20.0)
	await pilot.seconds(0.5)
	_check(is_instance_valid(death.killer), "from the window, his view follows the killer in the court")
	window_night = pilot.night.get_instance_id()
	await _set_down()
	await pilot.seconds(1.0)
	_check(not is_instance_id_valid(window_night) and _beat() == &"Arrive", "left during the killing, that night is gone too (%s)" % _beat())

	Talk.auto_choice = Callable()
	for path in [TEST_SAVE, GameState.quiet_path(), TEST_SETTINGS]:
		DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(1 if _fails > 0 else 0)


## Night 0 from where the carter sets him down, nothing said yet.
func _set_down() -> NightPilot:
	_flow.start_at(0, &"Arrive")
	await _frames(3)
	await _until(func() -> bool: return _beat() == &"Arrive", 10.0)
	await _frames(10)
	Talk.history.clear()
	var pilot := NightPilot.new(_level(), _check)
	pilot.shorten()
	return pilot


func _said(speaker: String, start: String) -> bool:
	return Talk.history.any(func(l: Array) -> bool: return l[0] == speaker and String(l[1]).contains(start))


func _level() -> Node:
	return _main.get(&"current_level")


func _beat() -> StringName:
	var level := _level()
	var director := level.get_node_or_null(^"Director") as NightDirector if level else null
	return director.current.name if director and director.current else &""


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
