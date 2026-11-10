extends Node
## Stills of talking, through the full render pipeline and by the real keys,
## to art/_review/talk/ (tools/talk_shots.sh): Brother Thomas at dusk on
## night 3 (narration, a line, the answers, the arrows moving, the porter's
## own line, a line with an aside), Walter at the grille (his greeting with
## the question under it, the three things to do with him under his answer, a
## thing noticed above them), something heard over a choice, a beat's choice
## under the line just said, and the Settings' large size with the dark
## band; and two strips of frames, of the answers coming up under a line and
## of the porter answering. Each is taken at the window's own size, so the
## type is as the player sees it.

const OUT := "res://art/_review/talk/"

var _n := 0
var _main: Node
var _pilot: NightPilot


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	# The game's defaults, whatever the player has set.
	Settings.subtitle_size = 1
	Settings.subtitle_backing = false
	Settings.apply()
	await _thomas()
	await _walter()
	print("talk shots done")
	get_tree().quit()


func _thomas() -> void:
	var night := await _load([])
	var p := _pilot.player
	await _pilot.until(func() -> bool: return _pilot.beat() == &"Wake" and not p.controls_locked, 10.0)
	var thomas := night.get_node(^"Brothers/Thomas") as Brother
	await _wait(0.5)
	_stand_by(p, thomas)
	# The night's waking lines first: a talk begun under them shows them above it.
	await _pilot.until(func() -> bool: return Talk.quiet(), 30.0)
	(thomas.get_node(^"Talker") as Talker).interact(p)
	await _shot("narration_as_the_talk_opens", 0.9)
	await _tap(KEY_E)
	await _shot("a_line", 0.5)
	_press(KEY_E, true)
	await _strip("strip_the_answers_come_up_under_the_line")
	_press(KEY_E, false)
	await _skip_to_the_answers()
	await _shot("the_answers", 0.9)
	await _tap(KEY_DOWN)
	await _shot("the_arrows_move_the_answer", 0.2)
	await _tap(KEY_UP)
	_press(KEY_E, true)
	await _strip("strip_he_answers")
	_press(KEY_E, false)
	await _shot("the_porter_says_his_answer", 0.2)
	await _tap(KEY_E)
	await _shot("the_reply", 0.4)
	await _tap(KEY_E)
	await _shot("narration_in_a_talk", 0.4)
	await _skip_to_the_answers()
	await _shot("the_answers_again_one_asked", 0.9)
	Talk.say("", "(The supper bell, across the court.)", 3.0)
	await _shot("something_heard_over_the_answers", 0.5)
	# The large size, and the dark band behind it.
	Settings.subtitle_size = 2
	Settings.subtitle_backing = true
	Settings.apply()
	await _shot("large_with_the_dark_band", 0.4)
	Settings.subtitle_size = 1
	Settings.subtitle_backing = false
	Settings.apply()
	await _wait(2.5)
	await _tap(KEY_3)
	await _shot("walked_away_he_calls_after", 0.5)
	await _pilot.until(func() -> bool: return Talk.quiet(), 10.0)
	Talk.say("Thomas", "(Quietly, so only you hear.) Not his physic. Not that one. Trust me.", 2.0)
	await _shot("a_line_with_an_aside", 0.5)
	await _pilot.until(func() -> bool: return Talk.quiet(), 10.0)
	# A beat's choice: the line just said stays up over it.
	Talk.auto_choice = func(_o: PackedStringArray) -> int: return -1
	var ask := func() -> void:
		await Talk.say("Ranulf", "A little of this in your ale, and you'll sleep.", 1.0)
		await Talk.choose(PackedStringArray(["(Take Brother Ranulf's remedy.)", "(Refuse it.)"]))
	ask.call()
	await _shot("a_beats_choice_under_the_line_just_said", 1.9)
	Talk.reset()
	Talk.auto_choice = Callable()


func _walter() -> void:
	await _load([&"Knocks"])
	GameState.phase = GameState.Phase.KNOCKS
	var p := _pilot.player
	_pilot.shorten()
	await _pilot.frames(30)
	_pilot.skip_to(20.0)
	await _pilot.until(func() -> bool: return _pilot.duty("Grate").enabled, 60.0)
	p.place(Vector3(-39.0, 0.05, -2.0), deg_to_rad(90.0))
	await _wait(0.3)
	_pilot.duty("Grate").interact(p)
	await _shot("at_the_grille_his_greeting_and_the_question", 1.6)
	await _wait(2.5)
	await _tap(KEY_1)
	await _shot("he_asks_it", 0.3)
	await _tap(KEY_E)
	await _shot("the_answer", 0.4)
	await _skip_to_the_answers()
	await _shot("what_to_do_with_him_under_his_answer", 0.9)
	var walter := get_tree().get_first_node_in_group(&"callers") as VisitorNPC
	_pilot.face(walter.part_position(&"box"))
	await _shot("a_thing_noticed_above_the_choice", 0.8)
	await _wait(2.5)
	await _tap(KEY_4)
	await _wait(0.5)
	Talk.reset()


## Skips the talk's lines, as the player would, until answers are offered.
func _skip_to_the_answers() -> void:
	for i in 12:
		if Talk.is_choosing():
			return
		await _tap(KEY_E)
		await _wait(0.15)


## Loads night 3 on its own in a fresh main scene, with only the beats named
## in `keep` (none named: all of them).
func _load(keep: Array[StringName]) -> Node:
	if _main:
		_main.queue_free()
		await get_tree().process_frame
	Talk.reset()
	NightPilot.fresh_night("user://talk_shots_save.tres")
	_main = NightPilot.main_with("res://game/nights/night3.tscn")
	add_child(_main)
	var night: Node = _main.get(&"current_level")
	if not keep.is_empty():
		var director := night.get_node(^"Director")
		for beat in director.get_children():
			if not keep.has(beat.name):
				director.remove_child(beat)
				beat.free()
	await get_tree().create_timer(0.8).timeout
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	_pilot = NightPilot.new(night, func(_ok: bool, _w: String) -> void: pass)
	(night.get_node(^"Hallucinations") as Hallucinations).active = false
	return night


## Puts the porter a step and a half from `who`, on a side with nothing in
## the way, his front first.
func _stand_by(p: Player, who: Node3D) -> void:
	var space := who.get_world_3d().direct_space_state
	var chest := who.global_position + Vector3.UP * 1.2
	for turn: float in [0.0, 0.6, -0.6, 1.2, -1.2, PI * 0.5, -PI * 0.5, PI]:
		var dir := (-who.global_basis.z).rotated(Vector3.UP, turn)
		var at := who.global_position + dir * 1.5
		var query := PhysicsRayQueryParameters3D.create(chest, at + Vector3.UP * 1.2, Layers.WORLD | Layers.DOOR)
		if space.intersect_ray(query).is_empty():
			p.place(at, atan2(dir.x, dir.z))
			return
	p.place(who.global_position + Vector3(1.5, 0, 0), PI * 0.5)


## Presses a key and lets go of it, as the player would.
func _tap(code: Key) -> void:
	for pressed: bool in [true, false]:
		_press(code, pressed)
		await _wait(0.08)


func _press(code: Key, pressed: bool) -> void:
	var e := InputEventKey.new()
	e.keycode = code
	e.physical_keycode = code
	e.pressed = pressed
	Input.parse_input_event(e)


## A strip of the bottom of the screen over the next frames, to see how
## something comes and goes.
func _strip(shot_name: String, count := 12) -> void:
	var frames: Array[Image] = []
	for i in count:
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		var w := img.get_width()
		var h := img.get_height()
		var part := img.get_region(Rect2i(roundi(w * 0.2), roundi(h * 0.55), roundi(w * 0.6), roundi(h * 0.45)))
		part.resize(roundi(part.get_width() * 0.5), roundi(part.get_height() * 0.5), Image.INTERPOLATE_BILINEAR)
		frames.append(part)
		await get_tree().process_frame
	var cols := 3
	var rows := ceili(count / float(cols))
	var fw := frames[0].get_width()
	var fh := frames[0].get_height()
	var sheet := Image.create(cols * fw, rows * fh, false, frames[0].get_format())
	for i in frames.size():
		sheet.blit_rect(frames[i], Rect2i(0, 0, fw, fh), Vector2i((i % cols) * fw, floori(i / float(cols)) * fh))
	var path := OUT + "%s.png" % shot_name
	sheet.save_png(ProjectSettings.globalize_path(path))
	print("wrote ", path)


func _wait(seconds: float) -> void:
	await get_tree().create_timer(seconds).timeout


func _shot(shot_name: String, settle := 0.5) -> void:
	await get_tree().create_timer(settle).timeout
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	_n += 1
	var path := OUT + "%02d_%s.png" % [_n, shot_name]
	img.save_png(ProjectSettings.globalize_path(path))
	print("wrote ", path)
