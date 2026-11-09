extends CanvasLayer
## Autoload Talk: subtitles, choices and conversations (Look and Feel, "UI":
## plain subtitles at the bottom, the speaker's name in small caps, no
## portraits). The night's beats await say() and choose().
##
## A line in round brackets is narration: what the porter sees, hears or
## does. It shows in italics, softer, with no brackets and no name. A bracket
## in a spoken line ("Osric: (He laughs.) Leave it.") shows as a small italic
## aside over the name, and the words without it. A line said while
## another is up shows over it, and when it's over the one under it shows
## again (or the open question).
##
## Conversations: converse() plays a Conversation with someone; a beat can
## open one itself with begin() and end(). Either way they turn to him, and
## his view turns to their face and narrows for a moment, then is his again:
## he looks where he likes while they talk, standing still. The porter says
## the answer he picks (his name over it), unless it's something he does,
## written in brackets. `interact` skips to the next line, and every choice
## ends with "Walk away" ("Turn away" on the wagon). Moving walks away too
## (once he has let go of the keys he walked up with). Once he has walked
## away, say() and choose() (-1) return at once until the conversation is
## ended. interrupt() ends one at once, without the parting lines, when
## something else comes up (the carter pulling in on the road in); what it
## was saying or asking stops there and leaves the next conversation alone.
## A press of `interact` counts once (Press): holding it doesn't skip on, or
## answer.
##
## Choices: number keys, or the arrow keys and `interact`. An answer in
## brackets shows in italics, without them. Tests answer through
## `auto_choice` and shorten lines with `line_seconds`.
##
## Lines wait while the game is paused. reset() drops everything said or
## asked (back to the title, a new chapter): what was waiting returns at once.
## The subtitle size and the dark band behind them follow the Settings.

signal said(speaker: String, text: String)
signal chose(options: PackedStringArray, picked: int)
## A line's time is up, or it was cut short (id -1: every line).
signal _line_over(id: int)

const CHARS_PER_SECOND := 16.0
const MIN_SECONDS := 2.5
## The porter's own answers: he knows what he said, so they go quicker.
const OWN_MIN_SECONDS := 1.5
const TEXT_COLOR := Color("#D8C9A3")
const NARRATION_COLOR := Color(0.78, 0.75, 0.68, 0.92)
const PICK_COLOR := Color("#F0E2BC")
const DIM_COLOR := Color(0.85, 0.79, 0.64, 0.55)
const LEAVE_COLOR := Color(0.85, 0.79, 0.64, 0.35)
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

var _box: VBoxContainer
var _aside: Label
var _speaker: Label
var _text: Label
var _options: VBoxContainer
var _italic: FontVariation
var _choices := PackedStringArray()
## The question of the open choice: [speaker, text].
var _prompt := ["", ""]
var _highlight := 0
var _picked := -1
var _line_id := 0
## The "Walk away" choice's index, or -1.
var _leave_index := -1
## Goes up at every reset(); talk begun before it stops.
var _gen := 0
## Goes up at every begin(), interrupt() and reset(): a conversation whose
## number has gone stops where it is.
var _talk := 0
## Lines up now, oldest first, each [id, speaker, text, said in a talk]. The
## newest shows.
var _up: Array = []
var _backing: StyleBoxFlat


func _ready() -> void:
	layer = 3
	process_mode = Node.PROCESS_MODE_ALWAYS
	_backing = StyleBoxFlat.new()
	_backing.bg_color = Color(0.02, 0.02, 0.03, 0.72)
	_backing.set_content_margin_all(4)
	_italic = FontVariation.new()
	_italic.base_font = ThemeDB.fallback_font
	_italic.variation_transform = Transform2D(Vector2(1.0, 0.0), Vector2(0.22, 1.0), Vector2.ZERO)
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)
	_box = VBoxContainer.new()
	_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_box.alignment = BoxContainer.ALIGNMENT_END
	root.add_child(_box)
	_aside = _label(NARRATION_COLOR)
	_aside.add_theme_font_override(&"font", _italic)
	_speaker = _label(TEXT_COLOR)
	_text = _label(TEXT_COLOR)
	_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_options = VBoxContainer.new()
	_options.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_box.add_child(_aside)
	_box.add_child(_speaker)
	_box.add_child(_text)
	_box.add_child(_options)
	get_viewport().size_changed.connect(_layout)
	Settings.changed.connect(_layout)
	_layout()
	_clear()


## Drops whatever is being said or asked: lines end, a choice returns -1, a
## conversation stops, and the porter's view is let go.
func reset() -> void:
	_gen += 1
	_talk += 1
	_choices = PackedStringArray()
	_line_over.emit(-1)
	if talking:
		end()
	_clear()


## Shows a line for `seconds` (or its reading time); await it.
func say(speaker: String, text: String, seconds := -1.0) -> void:
	if talking and left:
		return
	history.append([speaker, text])
	said.emit(speaker, text)
	_line_id += 1
	var id := _line_id
	_up.append([id, speaker, text, talking])
	_show_line(speaker, text)
	var t := seconds
	if t <= 0.0:
		t = line_seconds if line_seconds >= 0.0 else maxf(MIN_SECONDS, text.length() / CHARS_PER_SECOND)
	get_tree().create_timer(t, false).timeout.connect(func() -> void: _line_over.emit(id))
	while true:
		var over: int = await _line_over
		if over == id or over == -1:
			break
	for i in _up.size():
		if _up[i][0] == id:
			_up.remove_at(i)
			break
	_show_newest()


## Offers `options` under an optional line; returns the index picked. In a
## conversation "Walk away" comes last, and walking away returns -1.
func choose(options: PackedStringArray, speaker := "", text := "") -> int:
	if talking and left:
		return -1
	var gen := _gen
	var mine := _talk if talking else -1
	var shown := options.duplicate()
	_leave_index = -1
	if talking:
		_leave_index = shown.size()
		var p := _player()
		shown.append(TURN_AWAY if p and p.riding else WALK_AWAY)
	_prompt = [speaker, text]
	_choices = shown
	_highlight = 0
	_picked = -1
	_show_newest()
	_draw_options()
	while _picked < 0 and not (talking and left):
		await get_tree().process_frame
		if gen != _gen or (mine >= 0 and _talk != mine):
			return -1
		if auto_choice.is_valid() and _picked < 0 and not get_tree().paused:
			_picked = auto_choice.call(shown)
	var picked := _picked
	_choices = PackedStringArray()
	_clear_options()
	_show_newest()
	if talking and (left or picked == _leave_index):
		history.append(["", "> " + shown[-1]])
		chose.emit(shown, shown.size() - 1)
		_walk_away()
		return -1
	history.append(["", "> " + options[picked]])
	chose.emit(options, picked)
	return picked


## Plays `conversation` with `with` (anyone with face() and face_position(),
## like a Brother or a VisitorNPC); await it. Each point's lines are said in
## turn, and the last one stays up while he chooses; he says the answer he
## picks, and they go on.
func converse(conversation: Conversation, with: Node3D) -> void:
	if not begin(with):
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
		for line in point.lines:
			await say(line.speaker, line.text)
			if _talk != mine:
				return
			last = line
		var answers := conversation.offered(point)
		if left or answers.is_empty():
			at = point.go()
			continue
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
			await say(PORTER, answers[pick].text, own_seconds(answers[pick].text))
			if _talk != mine:
				return
		at = answers[pick].to
	var walked := left
	end()
	if walked and conversation.has_point(Conversation.LEAVE):
		_say_all(conversation.point(Conversation.LEAVE).lines)


## Opens a conversation with `with`: they turn to him, and his view turns to
## their face for a moment. False if he can't talk now (hiding, stumbling,
## already talking).
func begin(with: Node3D) -> bool:
	var p := _player()
	if talking or p == null or p.busy():
		return false
	if with.has_method(&"face"):
		with.call(&"face", p.global_position)
	var at: Vector3 = with.call(&"face_position") if with.has_method(&"face_position") \
			else with.global_position + Vector3.UP * 1.6
	talking = true
	left = false
	_talk += 1
	p.start_talk(at)
	if not p.walked_away.is_connected(_walk_away):
		p.walked_away.connect(_walk_away)
	return true


## Cuts the open conversation short, with no parting lines: its line and
## its choice go, and it's closed now, so a beat can open another at once.
func interrupt() -> void:
	if not talking:
		return
	_talk += 1
	_choices = PackedStringArray()
	_clear_options()
	_end_talk_lines()
	end()


## Closes the conversation; his view comes back.
func end() -> void:
	if not talking:
		return
	talking = false
	left = false
	var p := _player()
	if p:
		p.end_talk()
		if p.walked_away.is_connected(_walk_away):
			p.walked_away.disconnect(_walk_away)


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


func _walk_away() -> void:
	if not talking or left:
		return
	left = true
	_end_talk_lines()
	var p := _player()
	if p:
		p.end_talk()


## Ends the lines said since the conversation opened; lines from before it
## (a voice in the dark) stay up.
func _end_talk_lines() -> void:
	for entry: Array in _up.duplicate():
		if entry[3]:
			_line_over.emit(entry[0])


func _say_all(lines: Array[Conversation.Line]) -> void:
	for line in lines:
		await say(line.speaker, line.text)


func _player() -> Player:
	return get_tree().get_first_node_in_group(&"player") as Player


func is_choosing() -> bool:
	return not _choices.is_empty()


## Nobody's talking and no line is up: a beat can say something without
## stepping on anyone.
func quiet() -> bool:
	return not talking and _up.is_empty()


func _input(event: InputEvent) -> void:
	if get_tree().paused:
		return
	# A click that only recaptures the mouse doesn't count.
	if event is InputEventMouseButton and Input.mouse_mode != Input.MOUSE_MODE_CAPTURED:
		return
	if _choices.is_empty():
		if talking and not left and not _up.is_empty() and Press.fresh(event, &"interact"):
			_line_over.emit(_up[-1][0])
			get_viewport().set_input_as_handled()
		return
	var key := event as InputEventKey
	if key and key.keycode >= KEY_1 and key.keycode < KEY_1 + _choices.size() and Press.fresh_key(key):
		_picked = key.keycode - KEY_1
	elif event.is_action_pressed(&"ui_up"):
		_highlight = posmod(_highlight - 1, _choices.size())
		_draw_options()
	elif event.is_action_pressed(&"ui_down"):
		_highlight = posmod(_highlight + 1, _choices.size())
		_draw_options()
	elif Press.fresh(event, &"interact") or Press.fresh(event, &"ui_accept"):
		_picked = _highlight
	else:
		return
	get_viewport().set_input_as_handled()


## Shows the newest line up, or the open question, or nothing.
func _show_newest() -> void:
	if not _up.is_empty():
		_show_line(_up[-1][1], _up[-1][2])
	elif is_choosing():
		_show_line(_prompt[0], _prompt[1])
	else:
		_show_line("", "")


## A spoken line: its name in small caps and its words, with any aside it
## opens with over the name. Narration: italic and softer, with no name.
func _show_line(speaker: String, text: String) -> void:
	var split := aside(text)
	var told := narration(text)
	if not told.is_empty():
		_aside.visible = false
		_speaker.visible = false
		_text.text = told
		_text.add_theme_font_override(&"font", _italic)
		_text.add_theme_color_override(&"font_color", NARRATION_COLOR)
		_text.visible = true
		return
	_aside.text = split[0]
	_aside.visible = not split[0].is_empty()
	_speaker.text = speaker.to_upper()
	_speaker.visible = not speaker.is_empty()
	_text.text = split[1]
	_text.remove_theme_font_override(&"font")
	_text.add_theme_color_override(&"font_color", TEXT_COLOR)
	_text.visible = not split[1].is_empty()


func _draw_options() -> void:
	_clear_options()
	for i in _choices.size():
		var l := _label(PICK_COLOR if i == _highlight else (LEAVE_COLOR if i == _leave_index else DIM_COLOR))
		var done := narration(_choices[i])
		l.text = "%d.  %s" % [i + 1, done if not done.is_empty() else _choices[i]]
		if not done.is_empty():
			l.add_theme_font_override(&"font", _italic)
		l.add_theme_font_size_override(&"font_size", _font_size(1.0))
		_options.add_child(l)


func _clear_options() -> void:
	for c in _options.get_children():
		c.queue_free()


func _clear() -> void:
	_show_line("", "")
	_clear_options()


func _label(color: Color) -> Label:
	var l := Label.new()
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.add_theme_color_override(&"font_color", color)
	l.add_theme_color_override(&"font_outline_color", Color(0, 0, 0, 0.85))
	l.add_theme_constant_override(&"outline_size", 5)
	_style(l)
	return l


## The dark band behind the line, if the setting asks for it.
func _style(l: Label) -> void:
	if Settings.subtitle_backing:
		l.add_theme_stylebox_override(&"normal", _backing)
	else:
		l.remove_theme_stylebox_override(&"normal")


## Sized from the window height, like the interact dot, times the subtitle size setting.
func _font_size(factor: float) -> int:
	return maxi(10, roundi(get_viewport().get_visible_rect().size.y / 540.0 * 15.0 * factor * Settings.subtitle_scale()))


func _layout() -> void:
	var win := get_viewport().get_visible_rect().size
	_box.position = Vector2(win.x * 0.15, 0.0)
	_box.size = Vector2(win.x * 0.7, win.y * 0.93)
	# Small caps: the name in capitals, smaller than the line.
	_aside.add_theme_font_size_override(&"font_size", _font_size(0.75))
	_speaker.add_theme_font_size_override(&"font_size", _font_size(0.75))
	_text.add_theme_font_size_override(&"font_size", _font_size(1.0))
	_style(_aside)
	_style(_speaker)
	_style(_text)
	_draw_options()
