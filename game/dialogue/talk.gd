extends CanvasLayer
## Autoload Talk: subtitles, choices and conversations (Look and Feel, "UI":
## plain subtitles at the bottom, the speaker's name in small caps, no
## portraits). The night's beats await say() and choose(). TalkView draws it.
##
## Lines. A line in round brackets is narration: what the porter sees, hears
## or does. It shows in italics, softer, with no brackets and no name. A
## bracket in a spoken line ("Osric: (He laughs.) Leave it.") shows as an
## aside beside the name, and the words without it. A line said while another
## is up shows in its place; the older one's time runs on underneath, and if
## it has less than BLINK seconds left when the newer one is over it just
## ends, so nothing comes back for a blink.
##
## Two places. While he's talking to someone or being asked something, the
## main place keeps the talk's own line (line(), and what converse() and
## ask() say) or the question; anything else said meanwhile (a thing he
## notices, a bell, a voice in the dark: say()) shows small above it, as
## something heard, and never takes the question's place. Otherwise say()'s
## lines have the main place.
##
## Conversations. converse() plays a Conversation with someone; a beat can
## open one itself with begin() and end(). Either way they turn to him and
## stand still, and his view turns to their face and narrows for a moment,
## then is his again: he looks where he likes while they talk, standing
## still. A point's last line comes up together with its answers. The porter
## says the answer he picks (his name over it), unless it's something he
## does, written in brackets. `interact` skips to the next line, and every
## choice ends with "Walk away" ("Turn away" on the wagon). Moving walks away
## too (once he has let go of the keys he walked up with). Once he has walked
## away, say() and choose() (-1) return at once until the conversation is
## ended. interrupt() ends one at once, without the parting lines, when
## something else comes up (the carter pulling in on the road in); what it
## was saying or asking stops there and leaves the next conversation alone.
## If whoever he's talking to goes (taken out of the world, or more than
## GONE metres off), the talk is cut short the same way.
##
## Choices: number keys, or the arrow keys (or the wheel) and `interact`. An
## answer in brackets is something he does: it shows in italics, without
## them. `interact` answers nothing for CHOICE_DELAY seconds after a choice
## comes up, so the press that skipped the last line doesn't answer for him
## (a number key answers at once). A press
## counts once (Press): holding a key doesn't skip on, or answer. One
## question is open at a time: a second choose() waits for the first. A beat
## that asks with no line of its own keeps the line just said up over the
## answers. Tests answer through `auto_choice` and shorten lines with
## `line_seconds`.
##
## Lines wait while the game is paused. reset() drops everything said or
## asked (back to the title, a new chapter): what was waiting returns at once.

signal said(speaker: String, text: String)
signal chose(options: PackedStringArray, picked: int)
## A line's time is up, or it was cut short (id -1: every line).
signal _line_over(id: int)

const CHARS_PER_SECOND := 16.0
const MIN_SECONDS := 2.5
## The porter's own answers: he knows what he said, so they go quicker.
const OWN_MIN_SECONDS := 1.5
## A line uncovered with less than this left to run ends instead.
const BLINK := 0.6
## Seconds a choice is up before `interact` answers it.
const CHOICE_DELAY := 0.3
## A beat's choice with no line of its own keeps the line that ended within
## this many milliseconds up over it.
const PROMPT_LINGER := 300
## Metres from whoever he's talking to at which the talk is over.
const GONE := 6.0
## The last choice in a conversation; on the wagon he can't walk.
const WALK_AWAY := "Walk away"
const TURN_AWAY := "Turn away"
## The porter's name over the answers he says.
const PORTER := "Alric"

## Answers choices instead of the keys: func(options: PackedStringArray) -> int,
## asked every frame until it returns 0 or more.
var auto_choice: Callable
## Seconds every line stays up; below 0 the reading time is used.
var line_seconds := -1.0
## Everything said, in order: [speaker, text].
var history: Array = []
## A conversation is open (begin() to end()).
var talking := false
## He walked away from the open conversation.
var left := false
## Who he's talking to in the open conversation: they stand still for it.
var talking_to: Node3D
## What draws it all.
var view: TalkView

var _choices := PackedStringArray()
## The question of the open choice: [speaker, text].
var _prompt := ["", ""]
var _highlight := 0
var _picked := -1
## Seconds the open choice has been up.
var _choice_age := 0.0
var _line_id := 0
## The "Walk away" choice's index, or -1.
var _leave_index := -1
## Goes up at every reset(); talk begun before it stops.
var _gen := 0
## Goes up at every begin(), interrupt() and reset(): a conversation whose
## number has gone stops where it is.
var _talk := 0
## Lines up now, oldest first, each [id, speaker, text, the open talk's own
## line, seconds left]. The time of each runs; the newest of the talk's own
## shows in the main place, and the newest of the rest above it (or in the
## main place, with no talk or question open).
var _up: Array = []
## The line that ended last, and when (ticks, ms).
var _ended := ["", ""]
var _ended_at := -100000


func _ready() -> void:
	layer = 3
	process_mode = Node.PROCESS_MODE_ALWAYS
	view = TalkView.new()
	add_child(view)


func _process(delta: float) -> void:
	if get_tree().paused:
		return
	if is_choosing():
		_choice_age += delta
	if talking and not left and _gone():
		interrupt()
	for entry: Array in _up.duplicate():
		entry[4] = float(entry[4]) - delta
		if float(entry[4]) <= 0.0:
			_line_over.emit(entry[0])


## Drops whatever is being said or asked: lines end, a choice returns -1, a
## conversation stops, and the porter's view is let go.
func reset() -> void:
	_gen += 1
	_talk += 1
	_choices = PackedStringArray()
	_line_over.emit(-1)
	if talking:
		end()
	_ended_at = -100000
	view.clear_options()
	_show_newest()


## Shows a line for `seconds` (or its reading time); await it. With a talk
## or a question open it's something heard meanwhile, shown small above it.
func say(speaker: String, text: String, seconds := -1.0) -> void:
	await _say(speaker, text, seconds, false)


## A line of the open conversation: what they say to him, or he to them. It
## has the main place, `interact` skips it, and it stops if he walks away.
## With no conversation open it's the same as say().
func line(speaker: String, text: String, seconds := -1.0) -> void:
	await _say(speaker, text, seconds, talking)


func _say(speaker: String, text: String, seconds: float, own: bool) -> void:
	if talking and left:
		return
	_log(speaker, text)
	_line_id += 1
	var id := _line_id
	var t := seconds
	if t <= 0.0:
		t = line_seconds if line_seconds >= 0.0 else maxf(MIN_SECONDS, text.length() / CHARS_PER_SECOND)
	_up.append([id, speaker, text, own, t])
	_show_newest()
	while true:
		var over: int = await _line_over
		if over == id or over == -1:
			break
	var newest := _newest(own)
	var covering: bool = not newest.is_empty() and newest[0] == id
	for i in _up.size():
		if _up[i][0] == id:
			_up.remove_at(i)
			break
	# The line it covered has only a blink left: it ends too.
	var under := _newest(own)
	if covering and not under.is_empty() and line_seconds < 0.0 and float(under[4]) < BLINK:
		_line_over.emit(under[0])
	_ended = [speaker, text]
	_ended_at = Time.get_ticks_msec()
	_show_newest()


## Offers `options` under an optional line; returns the index picked. In a
## conversation "Walk away" comes last, and walking away returns -1. With no
## line given, the line that has just been said stays up over the answers.
func choose(options: PackedStringArray, speaker := "", text := "") -> int:
	if talking and left:
		return -1
	var gen := _gen
	var in_talk := talking
	var mine := _talk
	# One question at a time: this one waits for any other to be answered.
	while is_choosing():
		await get_tree().process_frame
		if gen != _gen or (in_talk and (_talk != mine or left)):
			return -1
	var shown := options.duplicate()
	_leave_index = -1
	if in_talk:
		_leave_index = shown.size()
		var p := _player()
		shown.append(TURN_AWAY if p and p.riding else WALK_AWAY)
	if text.is_empty() and Time.get_ticks_msec() - _ended_at <= PROMPT_LINGER:
		_prompt = _ended.duplicate()
	else:
		_prompt = [speaker, text]
	_choices = shown
	_highlight = 0
	_picked = -1
	_choice_age = 0.0
	_show_newest()
	view.show_options(shown, _leave_index, _highlight)
	while _picked < 0 and not (in_talk and left):
		await get_tree().process_frame
		if gen != _gen or (in_talk and _talk != mine):
			return -1
		if auto_choice.is_valid() and _picked < 0 and not get_tree().paused:
			_picked = auto_choice.call(shown)
	var picked := _picked
	_choices = PackedStringArray()
	view.clear_options()
	_show_newest()
	if in_talk and (left or picked == _leave_index):
		history.append(["", "> " + shown[-1]])
		chose.emit(shown, shown.size() - 1)
		_walk_away()
		return -1
	history.append(["", "> " + options[picked]])
	chose.emit(options, picked)
	return picked


## Says `text` and offers `options` under it at once: the line stays up while
## he chooses. Returns as choose() does.
func ask(options: PackedStringArray, speaker: String, text: String) -> int:
	if talking and left:
		return -1
	_log(speaker, text)
	return await choose(options, speaker, text)


## Asks him something outside a Conversation (a beat's question): says
## `text`, if given, with `options` under it, and then he says the answer he
## picked, unless it's something he does (in brackets).
func answer(options: PackedStringArray, speaker := "", text := "") -> int:
	var pick: int
	if text.is_empty():
		pick = await choose(options)
	else:
		pick = await ask(options, speaker, text)
	if pick >= 0 and narration(options[pick]).is_empty():
		await line(PORTER, options[pick], own_seconds(options[pick]))
	return pick


## Plays `conversation` with `with` (anyone with face() and face_position(),
## like a Brother or a VisitorNPC); await it. `watch`: what his eyes go to
## as it opens, if not their face. Each point's lines are said in
## turn; the last comes up with the answers and stays while he chooses; he
## says the answer he picks, and they go on.
func converse(conversation: Conversation, with: Node3D, watch: Node3D = null) -> void:
	if not begin(with, watch):
		return
	var mine := _talk
	var again := GameState.has_flag(conversation.talked_flag())
	GameState.set_flag(conversation.talked_flag())
	Conversation.partner = People.id_of(with)
	Conversation.partner_node = with
	var at := conversation.start(again, Conversation.partner)
	var last: Conversation.Line = null
	while not left and at != "" and at != Conversation.END:
		var point := conversation.point(at)
		if point == null:
			push_error("%s: no point called %s (%s)" % [conversation.resource_path, at, conversation.errors()])
			break
		Conversation.apply(point.tags)
		var answers := conversation.offered(point)
		# The line the answers come up under isn't waited out first.
		var asked: Conversation.Line = point.lines[-1] if not answers.is_empty() and not point.lines.is_empty() else null
		for said_line in point.lines:
			if said_line == asked:
				break
			await line(said_line.speaker, said_line.text)
			if _talk != mine:
				return
			last = said_line
		if left or answers.is_empty():
			at = point.go()
			continue
		if asked:
			_log(asked.speaker, asked.text)
			last = asked
		var texts := PackedStringArray()
		for a in answers:
			texts.append(a.text)
		var pick := await choose(texts, last.speaker if last else "", last.text if last else "")
		if _talk != mine:
			return
		if pick < 0:
			break
		Conversation.apply(answers[pick].tags)
		if narration(answers[pick].text).is_empty():
			await line(PORTER, answers[pick].text, own_seconds(answers[pick].text))
			if _talk != mine:
				return
		at = answers[pick].to
	var walked := left
	end()
	if walked and conversation.has_point(Conversation.LEAVE):
		_say_all(conversation.point(Conversation.LEAVE).lines)


## Opens a conversation with `with`: they turn to him and stand still, and
## his view turns to their face for a moment; or, with `watch`, to that
## instead, following it for a few seconds (what they are talking about: the
## cart going by). False if he can't talk now (hiding, stumbling, already
## talking).
func begin(with: Node3D, watch: Node3D = null) -> bool:
	var p := _player()
	if talking or p == null or p.busy():
		return false
	if with.has_method(&"face"):
		with.call(&"face", p.global_position)
	var at: Vector3 = with.call(&"face_position") if with.has_method(&"face_position") \
			else with.global_position + Vector3.UP * 1.6
	talking = true
	left = false
	talking_to = with
	_talk += 1
	p.start_talk(at, watch)
	if not p.walked_away.is_connected(_walk_away):
		p.walked_away.connect(_walk_away)
	_show_newest()
	return true


## Cuts the open conversation short, with no parting lines: its line and
## its choice go, and it's closed now, so a beat can open another at once.
func interrupt() -> void:
	if not talking:
		return
	_talk += 1
	_choices = PackedStringArray()
	view.clear_options()
	_end_talk_lines()
	end()
	_show_newest()


## Closes the conversation; his view comes back.
func end() -> void:
	if not talking:
		return
	talking = false
	left = false
	talking_to = null
	var p := _player()
	if p:
		p.end_talk()
		if p.walked_away.is_connected(_walk_away):
			p.walked_away.disconnect(_walk_away)
	_show_newest()


## Seconds the porter's own line `text` stays up.
func own_seconds(text: String) -> float:
	return line_seconds if line_seconds >= 0.0 else maxf(OWN_MIN_SECONDS, text.length() / CHARS_PER_SECOND)


## The words of `text` if it's narration, wholly in brackets; else "".
func narration(text: String) -> String:
	var split := aside(text)
	return split[0] if split[1].is_empty() else ""


## Splits `text` into [its brackets, the words outside them]: "Inside our
## wall? (He laughs.) At night?" is ["He laughs.", "Inside our wall? At
## night?"]. A line wholly in brackets has no words; one with none has no
## aside; one with a bracket left open is left as it is.
func aside(text: String) -> Array:
	var asides := PackedStringArray()
	var words := ""
	var depth := 0
	var from := 0
	for i in text.length():
		if text[i] == "(":
			if depth == 0:
				from = i
			depth += 1
		elif text[i] == ")" and depth > 0:
			depth -= 1
			if depth == 0:
				asides.append(text.substr(from + 1, i - from - 1).strip_edges())
		elif depth == 0:
			words += text[i]
	if depth > 0:
		return ["", text.strip_edges()]
	return [" ".join(asides), " ".join(words.split(" ", false))]


func is_choosing() -> bool:
	return not _choices.is_empty()


## The answers of the open choice, "Walk away" and all; empty with none open.
func offered() -> PackedStringArray:
	return _choices


## The answer the arrows are on in the open choice.
func highlighted() -> int:
	return _highlight


## Nobody's talking and no line is up: a beat can say something without
## stepping on anyone.
func quiet() -> bool:
	return not talking and _up.is_empty()


func _log(speaker: String, text: String) -> void:
	history.append([speaker, text])
	said.emit(speaker, text)


func _walk_away() -> void:
	if not talking or left:
		return
	left = true
	_end_talk_lines()
	var p := _player()
	if p:
		p.end_talk()


## Ends the conversation's own lines; anything else that's up (a voice in
## the dark) stays up.
func _end_talk_lines() -> void:
	for entry: Array in _up.duplicate():
		if entry[3]:
			_line_over.emit(entry[0])


func _say_all(lines: Array[Conversation.Line]) -> void:
	for said_line in lines:
		await say(said_line.speaker, said_line.text)


## The newest line up that is (or isn't) the talk's own; empty with none.
func _newest(own: bool) -> Array:
	for i in range(_up.size() - 1, -1, -1):
		if bool(_up[i][3]) == own:
			return _up[i]
	return []


## Whoever he's talking to is no longer there to talk to.
func _gone() -> bool:
	if not is_instance_valid(talking_to) or not talking_to.is_inside_tree() or not talking_to.is_visible_in_tree():
		return true
	var p := _player()
	return p != null and p.riding == null and p.global_position.distance_to(talking_to.global_position) > GONE


func _player() -> Player:
	return get_tree().get_first_node_in_group(&"player") as Player


func _input(event: InputEvent) -> void:
	if get_tree().paused:
		return
	# A click that only recaptures the mouse doesn't count.
	if event is InputEventMouseButton and Input.mouse_mode != Input.MOUSE_MODE_CAPTURED:
		return
	if not is_choosing():
		# In a talk `interact` skips the line that's being said.
		var said_now := _newest(true)
		if talking and not left and not said_now.is_empty() and Press.fresh(event, &"interact"):
			_line_over.emit(said_now[0])
			get_viewport().set_input_as_handled()
		return
	var pick := -1
	var number := _number_key(event as InputEventKey)
	if number >= 0 and number < _choices.size():
		# A number is meant, whenever it's pressed.
		if Press.fresh_key(event as InputEventKey):
			_picked = number
	elif Press.fresh(event, &"ui_up") or _wheel(event, MOUSE_BUTTON_WHEEL_UP):
		_highlight = posmod(_highlight - 1, _choices.size())
		view.set_highlight(_highlight)
	elif Press.fresh(event, &"ui_down") or _wheel(event, MOUSE_BUTTON_WHEEL_DOWN):
		_highlight = posmod(_highlight + 1, _choices.size())
		view.set_highlight(_highlight)
	elif Press.fresh(event, &"interact") or Press.fresh(event, &"ui_accept"):
		pick = _highlight
	elif not (event.is_action(&"interact") or event.is_action(&"ui_accept") or event.is_action(&"ui_up") or event.is_action(&"ui_down")):
		return
	# Too soon after it came up, `interact` is spent and answers nothing.
	if pick >= 0 and _choice_age >= CHOICE_DELAY:
		_picked = pick
	get_viewport().set_input_as_handled()


## The answer a number key stands for (1 is 0), or -1.
func _number_key(key: InputEventKey) -> int:
	if key == null or not key.pressed:
		return -1
	for code: int in [int(key.keycode), int(key.physical_keycode)]:
		if code >= KEY_1 and code <= KEY_9:
			return code - KEY_1
		if code >= KEY_KP_1 and code <= KEY_KP_9:
			return code - KEY_KP_1
	return -1


func _wheel(event: InputEvent, button: MouseButton) -> bool:
	var click := event as InputEventMouseButton
	return click != null and click.pressed and click.button_index == button


## Shows what's up. With a talk or a question open: the talk's line (or the
## question) in the main place, and the newest thing said meanwhile above
## it. Otherwise the newest line in the main place.
func _show_newest() -> void:
	var own := _newest(true)
	var other := _newest(false)
	if not (talking or is_choosing()):
		if own.is_empty():
			own = other
		other = []
	if not own.is_empty():
		view.show_line(own[1], own[2])
	elif is_choosing():
		view.show_line(_prompt[0], _prompt[1])
	else:
		view.show_line("", "")
	if other.is_empty():
		view.show_heard("", "")
	else:
		view.show_heard(other[1], other[2])
