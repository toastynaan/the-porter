extends CanvasLayer
## Autoload Talk: subtitles, choices and conversations (Look and Feel, "UI":
## plain subtitles at the bottom, the speaker's name in small caps, no
## portraits). The night's beats await say() and choose(). Until the script
## is written, lines are placeholders that describe the beat in brackets, in
## the design doc's words.
##
## Conversations: converse() plays a Conversation with someone; a beat can
## open one itself with begin() and end(). While one is open the porter's
## view eases in on their face and he stands still, `interact` skips to the
## next line, and every choice ends with "Walk away". Moving walks away too.
## Once he has walked away, say() and choose() (-1) return at once until the
## conversation is ended.
##
## Choices: number keys, or the arrow keys and `interact`. A line said while
## a choice is open shows over its question for a moment and then gives it
## back (the porter noticing something while he decides). Tests answer through
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
const TEXT_COLOR := Color("#D8C9A3")
const PICK_COLOR := Color("#F0E2BC")
const DIM_COLOR := Color(0.85, 0.79, 0.64, 0.55)
const LEAVE_COLOR := Color(0.85, 0.79, 0.64, 0.35)
## The last choice in a conversation.
const WALK_AWAY := "Walk away"
## How far he can look about while talking, in degrees either side of their
## face (yaw, pitch).
const TALK_CONE := Vector2(30.0, 30.0)

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
var _speaker: Label
var _text: Label
var _options: VBoxContainer
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
var _backing: StyleBoxFlat


func _ready() -> void:
	layer = 3
	process_mode = Node.PROCESS_MODE_ALWAYS
	_backing = StyleBoxFlat.new()
	_backing.bg_color = Color(0.02, 0.02, 0.03, 0.72)
	_backing.set_content_margin_all(4)
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)
	_box = VBoxContainer.new()
	_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_box.alignment = BoxContainer.ALIGNMENT_END
	root.add_child(_box)
	_speaker = _label(TEXT_COLOR)
	_text = _label(TEXT_COLOR)
	_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_options = VBoxContainer.new()
	_options.mouse_filter = Control.MOUSE_FILTER_IGNORE
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
	_choices = PackedStringArray()
	_line_over.emit(-1)
	if talking:
		end()
	_clear()


## Shows a line for `seconds` (or its reading time); await it.
func say(speaker: String, text: String, seconds := -1.0) -> void:
	if talking and left:
		return
	var gen := _gen
	history.append([speaker, text])
	said.emit(speaker, text)
	_line_id += 1
	var id := _line_id
	_show_line(speaker, text)
	var t := seconds
	if t <= 0.0:
		t = line_seconds if line_seconds >= 0.0 else maxf(MIN_SECONDS, text.length() / CHARS_PER_SECOND)
	get_tree().create_timer(t, false).timeout.connect(func() -> void: _line_over.emit(id))
	while true:
		var over: int = await _line_over
		if over == id or over == -1:
			break
	if gen != _gen:
		return
	if id == _line_id:
		if is_choosing():
			_show_line(_prompt[0], _prompt[1])
		else:
			_clear()


## Offers `options` under an optional line; returns the index picked. In a
## conversation "Walk away" comes last, and walking away returns -1.
func choose(options: PackedStringArray, speaker := "", text := "") -> int:
	if talking and left:
		return -1
	var gen := _gen
	var shown := options.duplicate()
	_leave_index = -1
	if talking:
		_leave_index = shown.size()
		shown.append(WALK_AWAY)
	_line_id += 1
	_prompt = [speaker, text]
	_show_line(speaker, text)
	_choices = shown
	_highlight = 0
	_picked = -1
	_draw_options()
	while _picked < 0 and not (talking and left):
		await get_tree().process_frame
		if gen != _gen:
			return -1
		if auto_choice.is_valid() and _picked < 0 and not get_tree().paused:
			_picked = auto_choice.call(shown)
	var picked := _picked
	_choices = PackedStringArray()
	_clear()
	if talking and (left or picked == _leave_index):
		history.append(["", "> " + WALK_AWAY])
		chose.emit(shown, shown.size() - 1)
		_walk_away()
		return -1
	history.append(["", "> " + options[picked]])
	chose.emit(options, picked)
	return picked


## Plays `conversation` with `with` (anyone with face() and face_position(),
## like a Brother or a VisitorNPC); await it. Each point's lines are said in
## turn, and the last one stays up while he chooses.
func converse(conversation: Conversation, with: Node3D) -> void:
	if not begin(with):
		return
	var gen := _gen
	var again := GameState.has_flag(conversation.talked_flag())
	GameState.set_flag(conversation.talked_flag())
	Conversation.partner = People.id_of(with)
	Conversation.partner_node = with
	var at := conversation.start(again, Conversation.partner)
	var last: Conversation.Line = null
	while not left and at != "" and at != Conversation.END and gen == _gen:
		var point := conversation.point(at)
		if point == null:
			push_error("%s: no point called %s (%s)" % [conversation.resource_path, at, conversation.errors()])
			break
		Conversation.apply(point.tags)
		for line in point.lines:
			await say(line.speaker, line.text)
			last = line
		var answers := conversation.offered(point)
		if left or answers.is_empty():
			at = point.next
			continue
		var texts := PackedStringArray()
		for a in answers:
			texts.append(a.text)
		var pick := await choose(texts, last.speaker if last else "", last.text if last else "")
		if pick < 0 or gen != _gen:
			break
		Conversation.apply(answers[pick].tags)
		at = answers[pick].to
	if gen != _gen:
		return
	var walked := left
	end()
	if walked and conversation.has_point(Conversation.LEAVE):
		_say_all(conversation.point(Conversation.LEAVE).lines)


## Opens a conversation with `with`: they turn to him and his view eases in
## on their face, held within `cone`. False if he can't talk now (hiding,
## stumbling, already talking).
func begin(with: Node3D, cone := TALK_CONE) -> bool:
	var p := _player()
	if p == null or p.busy():
		return false
	if with.has_method(&"face"):
		with.call(&"face", p.global_position)
	var at: Vector3 = with.call(&"face_position") if with.has_method(&"face_position") \
			else with.global_position + Vector3.UP * 1.6
	talking = true
	left = false
	p.start_talk(at, cone)
	if not p.walked_away.is_connected(_walk_away):
		p.walked_away.connect(_walk_away)
	return true


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


func _walk_away() -> void:
	if not talking or left:
		return
	left = true
	_line_over.emit(-1)
	_line_id += 1
	if not is_choosing():
		_clear()
	var p := _player()
	if p:
		p.end_talk()


func _say_all(lines: Array[Conversation.Line]) -> void:
	for line in lines:
		await say(line.speaker, line.text)


func _player() -> Player:
	return get_tree().get_first_node_in_group(&"player") as Player


func is_choosing() -> bool:
	return not _choices.is_empty()


func _input(event: InputEvent) -> void:
	if get_tree().paused:
		return
	if _choices.is_empty():
		if talking and not left and event.is_action_pressed(&"interact"):
			_line_over.emit(_line_id)
			get_viewport().set_input_as_handled()
		return
	var key := event as InputEventKey
	if key and key.pressed and not key.echo and key.keycode >= KEY_1 and key.keycode < KEY_1 + _choices.size():
		_picked = key.keycode - KEY_1
	elif event.is_action_pressed(&"ui_up"):
		_highlight = posmod(_highlight - 1, _choices.size())
		_draw_options()
	elif event.is_action_pressed(&"ui_down"):
		_highlight = posmod(_highlight + 1, _choices.size())
		_draw_options()
	elif event.is_action_pressed(&"interact") or event.is_action_pressed(&"ui_accept"):
		_picked = _highlight
	else:
		return
	get_viewport().set_input_as_handled()


func _show_line(speaker: String, text: String) -> void:
	_speaker.text = speaker.to_upper()
	_speaker.visible = not speaker.is_empty()
	_text.text = text
	_text.visible = not text.is_empty()


func _draw_options() -> void:
	for c in _options.get_children():
		c.queue_free()
	for i in _choices.size():
		var l := _label(PICK_COLOR if i == _highlight else (LEAVE_COLOR if i == _leave_index else DIM_COLOR))
		l.text = "%d.  %s" % [i + 1, _choices[i]]
		l.add_theme_font_size_override(&"font_size", _font_size(1.0))
		_options.add_child(l)


func _clear() -> void:
	_speaker.visible = false
	_text.visible = false
	for c in _options.get_children():
		c.queue_free()


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
	_speaker.add_theme_font_size_override(&"font_size", _font_size(0.75))
	_text.add_theme_font_size_override(&"font_size", _font_size(1.0))
	_style(_speaker)
	_style(_text)
	_draw_options()
