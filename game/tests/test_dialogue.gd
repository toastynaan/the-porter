extends Node
## Conversations (Talk.converse, Conversation, Talker), in the greybox abbey:
## - The script: points, lines, up to three answers, "again" and "leave",
##   [if], [set] and [suspicion] tags, and the errors a bad script reports.
##   Every conversation under game/dialogue/ reads without errors.
## - Talking: they turn to him and his view turns to their face, narrowed,
##   for a moment; then it widens and he can look anywhere (looking away lets
##   go sooner); their lines, then the last one stays up over three answers
##   and "Walk away"; he says the answer he picks, unless it's in brackets
##   (something he does); answers set flags and Suspicion, and asked
##   questions drop off.
## - Showing lines: narration (in brackets) in italics without its brackets
##   or a name; an aside it opens with over the name; a line said over a talk
##   gives the talk's line back when it's over.
## - Walking away by moving: the talk ends, his view comes back, they call
##   after him. The next talk starts at "again". `interact` skips a line.
## - Keys held down (from the playtest): `interact` held skips one line, and
##   doesn't open the talk again as it closes; the move key he walked up
##   with doesn't walk him away. Cut short (Talk.interrupt), a talk's choice
##   goes and it leaves the next talk alone.
## Run: tools/check.sh

const SCRIPT := """# A test talk.
== start [set met]
Osric: (First line.)
Osric: (The question.)
-> topics

== again
Osric: (Again.)
-> topics

== topics
* [if not asked_a] Ask A. -> a
* [if door=open] Ask B. -> b
* (Do C.) -> c

== a [set asked_a] [suspicion 5]
Osric: (Answer A.)
-> topics

== b
Osric: (Answer B.)
-> topics

== c
Osric: (Answer C.)
-> end

== leave
Osric: (Calls after you.)
"""

const BAD := """Nobody: (A line before any point.)
== start
* One -> nowhere
* Two -> end
* Three -> end
* Four [maybe] -> end
* No arrow
"""

var _fails := 0
var _offered: Array[PackedStringArray] = []
var _answer := -1
var _player: Player


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	GameState.flags = {}
	GameState.suspicion = 0
	Talk.line_seconds = 0.3
	Talk.auto_choice = func(options: PackedStringArray) -> int:
		if _offered.is_empty() or _offered[-1] != options:
			_offered.append(options)
		return _answer

	# The script.
	var c := Conversation.new()
	c.id = &"test"
	c.text = SCRIPT
	_check(c.errors().is_empty(), "a good script reads without errors %s" % [c.errors()])
	_check(c.start(false) == "start" and c.start(true) == "again" and c.has_point("leave"),
		"it starts at the first point, or at \"again\" once he has talked to them")
	var start := c.point("start")
	_check(start.lines.size() == 2 and start.lines[0].speaker == "Osric" and start.lines[0].text == "(First line.)"
		and start.next == "topics" and start.tags == PackedStringArray(["set met"]),
		"lines are \"Name: line\", and a point can carry tags and go on with ->")
	var topics := c.point("topics")
	_check(topics.answers.size() == 3 and topics.answers[1].text == "Ask B." and topics.answers[1].to == "b"
		and topics.answers[1].tags == PackedStringArray(["if door=open"]), "an answer has its text, tags and where it leads")
	var bad := Conversation.new()
	bad.text = BAD
	var errors := " / ".join(bad.errors())
	_check(errors.contains("under a point") and errors.contains("no point called nowhere") and errors.contains("5 answers")
		and errors.contains("unknown tag [maybe]") and errors.contains("needs ->"),
		"a bad script says what is wrong: %s" % errors)
	var files := _conversations("res://game/dialogue")
	var broken := files.filter(func(path: String) -> bool: return not (load(path) as Conversation).errors().is_empty())
	_check(files.size() >= 13 and broken.is_empty(), "every conversation in game/dialogue reads without errors (%d; broken: %s)" % [files.size(), broken])

	# Someone to talk to, in the outer court; the porter has his back to him.
	var abbey: Node3D = load("res://game/world/abbey/abbey.tscn").instantiate()
	add_child(abbey)
	_player = abbey.get_node(^"Player")
	var osric: Brother = load("res://game/npc/brother.tscn").instantiate()
	(osric.get_node(^"Look") as CharacterLook).look = load("res://game/characters/chr_osric.tscn")
	var talker := Talker.new()
	talker.name = &"Talker"
	talker.conversation = c
	talker.phases = [GameState.phase]
	osric.add_child(talker)
	abbey.add_child(osric)
	osric.place(Transform3D(Basis.IDENTITY, Vector3(-30, 0.05, 5.5)))
	await _seconds(0.5)
	_player.place(Vector3(-30, 0.05, 8.0), PI)
	GameState.set_flag(&"door", &"shut")
	await _seconds(0.3)

	# The way a line shows.
	var view := Talk.view
	_check(Talk.aside("(He laughs.) Leave it.") == ["He laughs.", "Leave it."] and Talk.narration("(He (still) waits.)") == "He (still) waits."
		and Talk.aside("Inside our wall? (He laughs.) At night?") == ["He laughs.", "Inside our wall? At night?"]
		and Talk.narration("Osric: no brackets") == "" and Talk.narration("(He laughs.) Leave it.") == ""
		and Talk.aside("An open (bracket") == ["", "An open (bracket"],
		"a line in brackets is narration; a bracket in a spoken line is an aside")
	Talk.say("Osric", "(He looks up.)", 0.5)
	await get_tree().process_frame
	_check(view.words == "He looks up." and view.narrated and view.speaker.is_empty(),
		"narration shows in italics, with no brackets and no name (%s)" % view.words)
	await _seconds(0.6)
	Talk.say("Osric", "(He laughs.) Leave it.", 0.5)
	await get_tree().process_frame
	_check(view.aside == "He laughs." and view.speaker == "Osric" and view.words == "Leave it." and not view.narrated,
		"a spoken line's aside shows beside the name")
	await _seconds(0.6)

	# Talking: they turn to him, his view turns to their face for a moment.
	talker.interact(_player)
	await _seconds(Player.TALK_TURN_TIME + 0.1)
	var face := osric.face_position()
	_check(_player.talking and Talk.talking and absf(_player.zoom - Player.TALK_ZOOM) < 0.5
		and absf(_player.camera.fov - (70.0 - Player.TALK_ZOOM)) < 0.6,
		"his view narrows by %d° (fov %.1f)" % [Player.TALK_ZOOM, _player.camera.fov])
	_check(ViewCheck.off_centre(_player.camera, face) < 3.0, "and turns to Osric's face (%.1f° off)" % ViewCheck.off_centre(_player.camera, face))
	var to_porter := _player.global_position - osric.global_position
	_check((-osric.global_basis.z).angle_to(Vector3(to_porter.x, 0, to_porter.z)) < 0.1, "Osric turns to face him")
	await _seconds(Player.TALK_HOLD + Player.TALK_TURN_TIME + 0.1)
	_check(Talk.talking and _player.zoom < 0.01, "a moment later his view widens again, and the talk goes on (zoom %.1f)" % _player.zoom)
	_player._look(Vector2(PI * 0.8, 0.0))
	var off := ViewCheck.off_centre(_player.camera, face)
	_check(Talk.talking and off > 120.0, "he can look anywhere while Osric talks (%.0f° off)" % off)
	_player._look(Vector2(-PI * 0.8, 0.0))
	await _choice()
	_check(_said("(First line.)") and Talk._prompt == ["Osric", "(The question.)"] and GameState.has_flag(&"met") and GameState.has_flag(&"talked_test"),
		"Osric says his lines; the last stays up over the choice")
	_check(_offered[-1] == PackedStringArray(["Ask A.", "(Do C.)", Talk.WALK_AWAY]),
		"three answers at most, those whose [if] holds, then Walk away: %s" % [_offered[-1]])
	var shown := view.option_texts()
	_check(shown == PackedStringArray(["Ask A.", "Do C.", Talk.WALK_AWAY]) and not view.option_done(0) and view.option_done(1) and view.option_done(2),
		"an answer in brackets shows in italics, without them, and so does walking away: %s" % [shown])

	# An answer: he says it, its tags, its reply, and it drops off.
	var suspicion := GameState.suspicion
	_answer = 0
	await _until(func() -> bool: return _said("(Answer A.)"), 3.0)
	_answer = -1
	var asked := Talk.history.find(["Alric", "Ask A."])
	_check(asked >= 0 and asked < Talk.history.find(["Osric", "(Answer A.)"]), "he says the answer he picks, and Osric answers it")
	await _choice()
	_check(GameState.has_flag(&"asked_a") and GameState.suspicion == suspicion + 5, "the answer sets its flag and raises Suspicion")
	_check(_offered[-1] == PackedStringArray(["(Do C.)", Talk.WALK_AWAY]), "asked, it isn't offered again: %s" % [_offered[-1]])

	# Walking away: a move key.
	Input.action_press(&"move_back")
	await _seconds(0.1)
	_check(not _player.talking and not Talk.talking and not Talk.is_choosing(), "a move key walks him away from the talk")
	await _seconds(0.3)
	_check(_flat_speed() > 0.5 and _said("(Calls after you.)"), "he walks off, and Osric calls after him")
	Input.action_release(&"move_back")
	await _seconds(Player.TALK_TURN_TIME + 0.2)
	_check(_player.zoom < 0.01 and absf(_player.camera.fov - 70.0) < 0.1, "his view widens again")

	# Again: the "again" point; a flag now offers B; Walk away as a choice.
	GameState.set_flag(&"door", &"open")
	var leaves := _count_said("(Calls after you.)")
	talker.interact(_player)
	await _choice()
	_check(_said("(Again.)") and _offered[-1] == PackedStringArray(["Ask B.", "(Do C.)", Talk.WALK_AWAY]),
		"talked to before, it starts at \"again\"; [if door=open] now holds: %s" % [_offered[-1]])
	_answer = 2
	await _until(func() -> bool: return not talker.talking, 3.0)
	_answer = -1
	_check(not Talk.talking and _count_said("(Calls after you.)") == leaves + 1 and Talk.history[-2] == ["", "> " + Talk.WALK_AWAY],
		"choosing Walk away ends it the same way")

	# An answer that ends the talk: no call after him.
	await _seconds(0.5)
	leaves = _count_said("(Calls after you.)")
	talker.interact(_player)
	await _choice()
	_answer = 1
	await _until(func() -> bool: return not talker.talking, 3.0)
	_answer = -1
	await _seconds(0.5)
	_check(_said("(Answer C.)") and not _player.talking and _count_said("(Calls after you.)") == leaves,
		"an answer that leads to end closes the talk; nobody calls after him")
	_check(not _said("(Do C.)") and not Talk.history.has(["Alric", "Do C."]), "an answer in brackets is done, not said")

	# Looking away while his view is on Osric lets it go at once.
	talker.conversation = c
	_player.place(Vector3(-30, 0.05, 8.0), PI)
	await _seconds(0.2)
	talker.interact(_player)
	await _seconds(Player.TALK_TURN_TIME + 0.1)
	Input.action_press(&"look_right")
	await _seconds(0.1)
	Input.action_release(&"look_right")
	await _seconds(Player.TALK_TURN_TIME + 0.05)
	_check(Talk.talking and _player.zoom < 0.01, "looking away lets his view off Osric's face before its time (zoom %.1f)" % _player.zoom)
	await _choice()
	_answer = 2
	await _until(func() -> bool: return not talker.talking, 3.0)
	_answer = -1
	await _seconds(0.5)

	# `interact` skips a line in a talk; held down, it counts once. A held key
	# repeats, and in the editor's game window the repeats come as presses.
	Talk.line_seconds = -1.0
	var skip_c := Conversation.new()
	skip_c.text = "== start\nOsric: A long first line, long enough to take a few seconds to read.\nOsric: Second, and long enough to take a few seconds to read.\nOsric: Third.\n-> end\n"
	talker.conversation = skip_c
	talker.interact(_player)
	await _seconds(0.3)
	# Something said over his line (a pickup) gives it back when it's over.
	Talk.say("", "(Picked up.)", 0.3)
	await get_tree().process_frame
	_check(view.heard == "Picked up." and view.words.begins_with("A long first"),
		"something said meanwhile shows above the talk's line, not in its place (%s / %s)" % [view.heard, view.words])
	await _seconds(0.4)
	_check(view.heard.is_empty() and view.words.begins_with("A long first"), "and goes when it's over (%s)" % view.heard)
	_action(&"interact", true)
	await _seconds(0.2)
	_check(view.words.begins_with("Second"), "interact skips to the next line (%s)" % view.words)
	for i in 8:
		_action(&"interact", true)
		await _seconds(0.05)
	_check(Talk.talking and view.words.begins_with("Second"), "held down, it skips no further (%s)" % view.words)
	_action(&"interact", false)
	await _seconds(0.1)
	_action(&"interact", true)
	await _seconds(0.1)
	_check(view.words == "Third.", "let go and pressed again, it skips on (%s)" % view.words)
	_action(&"interact", false)
	await _until(func() -> bool: return not talker.talking, 5.0)

	# Pressed on Osric and held: the talk opens once, plays its line, and
	# doesn't open again as it closes.
	var short_c := Conversation.new()
	short_c.text = "== start\nOsric: (Only line.)\n-> end\n"
	talker.conversation = short_c
	_player.place(Vector3(-30, 0.05, 7.0), 0.0)
	var interactor: Interactor = _player.get_node(^"Head/LookBack/Camera/Interactor")
	await _until(func() -> bool: return interactor.focused == talker, 2.0)
	var said := _count_said("(Only line.)")
	_action(&"interact", true)
	await _seconds(0.1)
	_check(Talk.talking and _count_said("(Only line.)") == said + 1, "interact on Osric opens the talk")
	for i in 80:
		_action(&"interact", true)
		await _seconds(0.05)
	_check(not Talk.talking and _count_said("(Only line.)") == said + 1,
		"held down through his line and after, it neither skips it nor opens the talk again (%d times)" % (_count_said("(Only line.)") - said))
	_action(&"interact", false)

	# Walked up with a move key held: that key doesn't walk him away; let go
	# and pressed again, it does.
	talker.conversation = c
	Input.action_press(&"move_left")
	talker.interact(_player)
	await _seconds(0.4)
	_check(Talk.talking and _player.talking, "the move key he walked up with doesn't walk him away")
	Input.action_release(&"move_left")
	await _seconds(0.1)
	Input.action_press(&"move_left")
	await _seconds(0.1)
	_check(not Talk.talking and not _player.talking, "let go and pressed again, it does")
	Input.action_release(&"move_left")
	await _seconds(0.5)

	# Cut short (as the body cart does on the road in): its choice goes,
	# nobody calls after him, and the talk opened next is left alone.
	_player.place(Vector3(-30, 0.05, 7.5), PI)
	await _seconds(0.3)
	talker.interact(_player)
	await _choice()
	leaves = _count_said("(Calls after you.)")
	Talk.interrupt()
	var next_c := Conversation.new()
	next_c.text = "== start\nOsric: (Something else.)\nOsric: (And more.)\n-> end\n"
	Talk.converse(next_c, osric)
	await _seconds(0.2)
	_check(Talk.talking and not talker.talking and view.words == "Something else."
		and not Talk.is_choosing() and view.option_texts().is_empty(),
		"cut short, its choice goes and the next talk opens at once (%s)" % view.words)
	await _until(func() -> bool: return not Talk.talking, 8.0)
	_check(_said("(And more.)") and _count_said("(Calls after you.)") == leaves,
		"the next talk plays out, and nobody calls after him from the first")

	await _answering(talker)
	await _lines_and_questions(osric)
	await _standing_still(abbey, osric)

	Talk.auto_choice = Callable()
	Talk.line_seconds = -1.0
	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


## Answering by the keys: a point's last line comes up with its answers at
## once; the choice takes no key for a moment; the arrows move the answer;
## `interact` skips a line said over the open choice before it answers.
func _answering(talker: Talker) -> void:
	var view := Talk.view
	Talk.auto_choice = Callable()
	Talk.line_seconds = -1.0
	_player.place(Vector3(-30, 0.05, 7.5), PI)
	await _seconds(0.3)
	var ask_c := Conversation.new()
	ask_c.id = &"test_ask"
	ask_c.text = "== start\nOsric: A first line, long enough to take a few seconds to read.\nOsric: And a question?\n* Yes. -> yes\n* No. -> end\n\n== yes\nOsric: (He nods.)\n-> end\n"
	talker.conversation = ask_c
	talker.interact(_player)
	await _seconds(0.3)
	await _tap(&"interact")
	_check(Talk.is_choosing() and view.words == "And a question?" and _said("And a question?")
		and view.option_texts() == PackedStringArray(["Yes.", "No.", Talk.WALK_AWAY]),
		"a point's last line comes up with its answers, not before them (%s)" % view.words)
	await _tap(&"interact")
	_check(Talk.is_choosing(), "a press as the answers come up answers nothing")
	await _seconds(Talk.CHOICE_DELAY)
	await _tap(&"ui_down")
	var down := Talk.highlighted()
	await _tap(&"ui_up")
	await _tap(&"ui_up")
	_check(down == 1 and Talk.highlighted() == 2, "the arrows move the answer, and wrap round (%d, %d)" % [down, Talk.highlighted()])
	await _tap(&"ui_down")
	Talk.say("Gib", "(From the lane.) Ten of the clock.", 5.0)
	await _seconds(0.1)
	_check(view.heard == "GIB  (From the lane.) Ten of the clock." and view.words == "And a question?" and Talk.is_choosing(),
		"something said over an open choice shows above it; the question keeps its place (%s)" % view.heard)
	await _tap(&"interact")
	_check(not Talk.is_choosing() and Talk.history.has(["Alric", "Yes."]) and view.speaker == "Alric" and view.words == "Yes.",
		"interact answers, and he says it (%s)" % view.words)
	await _until(func() -> bool: return not talker.talking, 8.0)
	_check(_said("(He nods.)") and not Talk.talking, "and the talk goes on from the answer")
	await _seconds(0.3)
	# A number key is meant: it answers as soon as the answers are up.
	talker.interact(_player)
	await _seconds(0.3)
	await _tap(&"interact")
	var key := InputEventKey.new()
	key.keycode = KEY_2
	key.physical_keycode = KEY_2
	key.pressed = true
	Input.parse_input_event(key)
	await _seconds(0.1)
	_check(not Talk.is_choosing() and Talk.history.has(["Alric", "No."]), "a number key answers at once")
	key = key.duplicate()
	key.pressed = false
	Input.parse_input_event(key)
	await _until(func() -> bool: return not talker.talking, 8.0)
	await _seconds(0.3)


## Lines over lines, questions over questions, and a beat's own question.
func _lines_and_questions(osric: Brother) -> void:
	var view := Talk.view
	# A line said over another has its place; the older one's time runs on
	# underneath, and with only a blink left it doesn't flash back.
	Talk.say("", "(Long.)", 2.0)
	await _seconds(0.1)
	Talk.say("", "(Over it.)", 1.7)
	await _seconds(0.2)
	_check(view.words == "Over it." and view.heard.is_empty(), "with no talk open, a line said over another has its place (%s)" % view.words)
	await _seconds(1.55)
	_check(view.words.is_empty() and Talk.quiet(), "a line with only a blink left doesn't flash back (%s)" % view.words)
	Talk.say("", "(Long.)", 3.0)
	await _seconds(0.1)
	Talk.say("", "(Over it.)", 1.0)
	await _seconds(1.2)
	_check(view.words == "Long.", "one with longer left shows again (%s)" % view.words)
	await _seconds(2.0)
	# A line from before a talk is heard above it, and gone by its end.
	Talk.say("", "(Stale.)", 1.0)
	await _seconds(0.3)
	Talk.begin(osric)
	Talk.line("Osric", "Fresh.", 1.5)
	await _seconds(0.2)
	_check(view.words == "Fresh." and view.heard == "Stale.", "a line from before a talk moves above the talk's line (%s / %s)" % [view.words, view.heard])
	await _seconds(1.5)
	_check(view.words.is_empty() and view.heard.is_empty(), "and doesn't turn up after it (%s)" % view.heard)
	Talk.end()

	# One question at a time: a second waits for the first to be answered.
	var picks := []
	var first := func() -> void:
		var got := await Talk.choose(PackedStringArray(["(One.)", "(Two.)"]))
		picks.append(["first", got])
	var second := func() -> void:
		var got := await Talk.choose(PackedStringArray(["(Three.)", "(Four.)"]))
		picks.append(["second", got])
	first.call()
	second.call()
	await _seconds(0.1)
	_check(Talk.offered() == PackedStringArray(["(One.)", "(Two.)"]) and view.option_texts() == PackedStringArray(["One.", "Two."]),
		"asked two things at once, the first is up: %s" % [Talk.offered()])
	Talk.auto_choice = func(o: PackedStringArray) -> int: return 1 if o.has("(One.)") else -1
	await _seconds(0.1)
	_check(picks == [["first", 1]] and Talk.offered() == PackedStringArray(["(Three.)", "(Four.)"]),
		"answered, the second comes up: %s" % [picks])
	Talk.auto_choice = func(_o: PackedStringArray) -> int: return 0
	await _seconds(0.1)
	_check(picks == [["first", 1], ["second", 0]] and not Talk.is_choosing() and view.option_texts().is_empty(), "and is answered in its turn: %s" % [picks])

	# A beat's question: the line just said stays up over the answers, and he
	# says the answer he picks.
	_answer = -1
	Talk.auto_choice = func(_o: PackedStringArray) -> int: return _answer
	var beat := func() -> void:
		await Talk.say("Osric", "Well, porter?", 0.3)
		await Talk.answer(PackedStringArray(["I saw nothing.", "(Say nothing.)"]))
	beat.call()
	await _seconds(0.5)
	_check(Talk.is_choosing() and view.speaker == "Osric" and view.words == "Well, porter?",
		"a beat's question keeps the line just said up over its answers (%s)" % view.words)
	_answer = 0
	await _seconds(0.2)
	_answer = -1
	_check(view.speaker == "Alric" and view.words == "I saw nothing.", "and he says the answer he picks (%s: %s)" % [view.speaker, view.words])
	await _seconds(2.0)


## Whoever he's talking to stands still for it and goes on after; if they
## go, or he's taken away, the talk is cut short.
func _standing_still(abbey: Node3D, osric: Brother) -> void:
	osric.place(null)
	var walker: VisitorNPC = load("res://game/gate/visitor_npc.tscn").instantiate()
	walker.name = &"Pilgrim"
	var who := Visitor.new()
	who.look = load("res://game/characters/chr_pilgrim.tscn")
	who.lantern = false
	walker.visitor = who
	abbey.add_child(walker)
	walker.global_position = Vector3(-30, 0.05, 5.5)
	var long_c := Conversation.new()
	long_c.id = &"test_long"
	long_c.text = "== start\nPilgrim: A long line, long enough to take a few seconds to read.\nPilgrim: And another just as long, to keep the talk open.\nPilgrim: And a third, as long as the others were.\n-> end\n"
	await _seconds(0.3)
	walker.go_to(Vector3(-30, 0.05, -6.0))
	await _seconds(1.0)
	_check(walker.velocity.length() > 0.5, "someone walking by (%.1f m/s)" % walker.velocity.length())
	_player.place(walker.global_position + Vector3(1.4, 0, 0), PI * 0.5)
	Talk.converse(long_c, walker)
	await _seconds(0.5)
	var stood := walker.global_position
	await _seconds(1.0)
	_check(Talk.talking and Talk.talking_to == walker and walker.global_position.distance_to(stood) < 0.05,
		"talked to, he stands still (moved %.2f m)" % walker.global_position.distance_to(stood))
	Talk.interrupt()
	await _seconds(1.0)
	_check(not Talk.talking and walker.global_position.distance_to(stood) > 0.5, "and walks on when it's over (%.2f m)" % walker.global_position.distance_to(stood))

	_player.place(walker.global_position + Vector3(1.4, 0, 0), PI * 0.5)
	Talk.converse(long_c, walker)
	await _seconds(0.5)
	walker.set_present(false)
	await _seconds(0.1)
	_check(not Talk.talking and not _player.talking and Talk.view.words.is_empty(), "if they go, the talk is cut short")

	walker.set_present(true, Transform3D(Basis.IDENTITY, Vector3(-30, 0.05, 5.5)))
	_player.place(Vector3(-28.6, 0.05, 5.5), PI * 0.5)
	await _seconds(0.3)
	Talk.converse(long_c, walker)
	await _seconds(0.5)
	var open := Talk.talking
	_player.place(Vector3(-30, 0.05, 5.5 + Talk.GONE + 2.0), 0.0)
	await _seconds(0.1)
	_check(open and not Talk.talking and not _player.talking, "and so it is if he's taken %d m away" % roundi(Talk.GONE + 2.0))
	walker.queue_free()
	await _seconds(0.3)


## Presses `action` and lets go of it, as a tap of a key would.
func _tap(action: StringName) -> void:
	_action(action, true)
	await _seconds(0.05)
	_action(action, false)
	await _seconds(0.05)


## Presses (or lets go of) `action`, as a key would.
func _action(action: StringName, pressed: bool) -> void:
	var e := InputEventAction.new()
	e.action = action
	e.pressed = pressed
	Input.parse_input_event(e)


func _conversations(dir: String) -> Array[String]:
	var out: Array[String] = []
	for sub in DirAccess.get_directories_at(dir):
		out.append_array(_conversations(dir.path_join(sub)))
	for f in DirAccess.get_files_at(dir):
		if f.ends_with(".tres") and load(dir.path_join(f)) is Conversation:
			out.append(dir.path_join(f))
	return out


## Waits for a choice to open and be offered.
func _choice() -> void:
	await _until(func() -> bool: return Talk.is_choosing(), 3.0)
	await _seconds(0.05)


func _said(text: String) -> bool:
	return _count_said(text) > 0


func _count_said(text: String) -> int:
	return Talk.history.filter(func(h: Array) -> bool: return h[1] == text).size()


func _flat_speed() -> float:
	return Vector2(_player.velocity.x, _player.velocity.z).length()


func _seconds(t: float) -> void:
	await get_tree().create_timer(t).timeout


func _until(condition: Callable, timeout: float) -> void:
	var t := 0.0
	while not condition.call() and t < timeout:
		await get_tree().physics_frame
		t += get_physics_process_delta_time()


func _check(ok: bool, what: String) -> void:
	if not ok:
		_fails += 1
	print("  %s %s" % ["ok  " if ok else "FAIL", what])
