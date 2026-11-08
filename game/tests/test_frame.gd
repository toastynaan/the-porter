extends Node
## The frame's quiet parts on night 3 (docs/mechanics.md, "The minimal HUD",
## "Your hands", "Settings" and "Tests"): the outline is on what E would use
## only while it is in reach; the duty glyph marks only the current duty,
## within 10 m and in view, never while talking, hiding or in a chase, and
## not at all with guidance off; the satchel shows what he carries and the
## ledger and satchel are never up together; the settings apply at once;
## the candle runs at 3 minutes an hour, 2 with the faster clock.
## Run: tools/check.sh

const TEST_SAVE := "user://test_frame_save.tres"

var _fails := 0
var _pilot: NightPilot


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	NightPilot.fresh_night(TEST_SAVE)
	Talk.line_seconds = 0.05
	var main := NightPilot.main_with("res://game/nights/night3.tscn")
	add_child(main)
	_pilot = NightPilot.new(main.get(&"current_level"), _check)
	_pilot.shorten()
	await _pilot.frames(5)
	var p := _pilot.player
	var night := _pilot.night
	var glyph: DutyGlyph = main.get_node(^"UI/DutyGlyph")
	var interactor: Interactor = p.get_node(^"Head/LookBack/Camera/Interactor")
	await _pilot.until(func() -> bool: return not p.controls_locked, 5.0)

	# The clock's pace.
	var clock := _pilot.clock()
	var fresh := NightClock.new()
	_check(is_equal_approx(fresh.seconds_per_hour, 180.0), "the candle runs 3 minutes an in-game hour")
	fresh.free()
	Settings.fast_clock = true
	_check(is_equal_approx(clock.awake_pace(), clock.seconds_per_hour * 2.0 / 3.0), "2 minutes with the faster clock")
	Settings.fast_clock = false

	# The outline, only within reach.
	var candle: CandleClock = night.get_node(^"CandleClock")
	p.place(Vector3(-34.1, 0.05, -10.5), deg_to_rad(-90.0))
	_pilot.face(Vector3(-33.25, 1.05, -10.5))
	await _pilot.frames(3)
	_check(interactor.focused == candle and Outline.is_on(candle), "the candle clock in reach has the outline")
	p.place(Vector3(-37.0, 0.05, -10.5), deg_to_rad(-90.0))
	_pilot.face(Vector3(-33.25, 1.05, -10.5))
	await _pilot.frames(3)
	_check(interactor.focused == null and not Outline.is_on(candle), "out of reach, it has none")

	# The glyph: no duty, no glyph.
	await _pilot.frames(3)
	_check(glyph.target == null, "at dusk no duty is wanted, and no glyph shows")
	_pilot.skip_to(17.25)
	await _pilot.until(func() -> bool: return _pilot.duty("SupperSeat").enabled, 5.0)
	var seat := _pilot.duty("SupperSeat")
	p.place(seat.global_position + Vector3(0, 0, 4.0), 0.0)
	_pilot.face(seat.glyph_point())
	await _pilot.frames(3)
	_check(glyph.target == seat, "the current duty, 4 m off: the glyph is over it")
	_check(not _pilot.duty("Bread").is_in_group(&"glyph_targets"), "a duty not yet wanted is never marked")
	p.place(seat.global_position + Vector3(0, 0, 12.0), 0.0)
	_pilot.face(seat.glyph_point())
	await _pilot.frames(3)
	_check(glyph.target == null, "12 m off, beyond 10 m: no glyph")
	p.place(seat.global_position + Vector3(0, 0, 4.0), 0.0)
	_pilot.face(seat.glyph_point() + Vector3(0, 0, 8.0))
	await _pilot.frames(3)
	_check(glyph.target == null, "looking away from it: no glyph")
	_pilot.face(seat.glyph_point())
	Settings.guidance = false
	await _pilot.frames(3)
	_check(glyph.target == null, "guidance off: no glyph")
	Settings.guidance = true
	var hunter: Hunter = night.get_node(^"Hunter")
	hunter.chase()
	await _pilot.frames(3)
	_check(glyph.target == null, "in a chase: no glyph")
	hunter.reset()
	await _pilot.frames(3)
	_check(glyph.target == seat, "the chase over, it is back")
	var osric := night.get_node(^"Brothers/Osric") as Node3D
	Talk.begin(osric)
	await _pilot.frames(3)
	_check(glyph.target == null, "talking: no glyph")
	Talk.end()
	var spot: HidingSpot = night.get_node(^"Abbey/Navigation/OuterCourt/HidingSpots/UnderCot")
	if spot:
		p.hide_in(spot)
		await _pilot.seconds(1.0)
		_check(glyph.target == null, "hiding: no glyph")
		p.leave_hiding(true)

	# The satchel; the ledger and the satchel are never up together.
	GameState.satchel.assign([&"apple"])
	var satchel: SatchelView = main.get_node(^"UI/Satchel")
	var ledger: LedgerView = main.get_node(^"UI/Ledger")
	_press(&"satchel")
	await _pilot.frames(2)
	var text := SatchelView.page_text()
	_check(satchel.showing and text.contains("A windfall apple") and text.contains("Keys") and text.contains("the guesthouse"),
		"I holds up the satchel: the keys and the apple")
	_press(&"ledger")
	await _pilot.frames(2)
	_check(ledger.showing and not satchel.showing, "the ledger takes its place")
	_press(&"ledger")
	await _pilot.frames(2)
	_check(not ledger.showing and not satchel.showing, "and goes down again")

	# Settings apply at once.
	Settings.set_value(&"fov", 85.0)
	await _pilot.frames(3)
	_check(absf(p.camera.fov - 85.0) < 0.5, "field of view 85° (%.1f)" % p.camera.fov)
	Settings.set_value(&"fov", 70.0)
	Settings.set_value(&"volume", 0.0)
	_check(AudioServer.is_bus_mute(AudioServer.get_bus_index(&"Master")), "volume 0 mutes the game")
	Settings.set_value(&"volume", 0.8)
	Settings.set_value(&"subtitle_size", 2)
	var big := Settings.subtitle_scale()
	Settings.set_value(&"subtitle_size", 0)
	var small := Settings.subtitle_scale()
	Settings.set_value(&"subtitle_size", 1)
	_check(big > 1.0 and small < 1.0 and Settings.changed.is_connected(Talk._layout),
		"subtitle sizes, and the subtitles follow the setting (%.1f, %.1f)" % [big, small])

	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


func _press(action: StringName) -> void:
	var e := InputEventAction.new()
	e.action = action
	e.pressed = true
	Input.parse_input_event(e)


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
