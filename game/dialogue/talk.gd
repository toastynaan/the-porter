extends CanvasLayer
## Autoload Talk: subtitles and choices (Look and Feel, "UI": plain subtitles
## at the bottom, the speaker's name in small caps, no portraits). The night's
## beats await say() and choose(). Until the script is written, lines are
## placeholders that describe the beat in brackets, in the design doc's words.
##
## Choices: number keys, or the arrow keys and `interact`. Tests answer through
## `auto_choice` and shorten lines with `line_seconds`.

signal said(speaker: String, text: String)
signal chose(options: PackedStringArray, picked: int)

const CHARS_PER_SECOND := 16.0
const MIN_SECONDS := 2.5
const TEXT_COLOR := Color("#D8C9A3")
const PICK_COLOR := Color("#F0E2BC")
const DIM_COLOR := Color(0.85, 0.79, 0.64, 0.55)

## Answers choices instead of the keys: func(options: PackedStringArray) -> int.
var auto_choice: Callable
## Seconds every line stays up; below 0 the reading time is used.
var line_seconds := -1.0
## Everything said, in order: [speaker, text].
var history: Array = []

var _box: VBoxContainer
var _speaker: Label
var _text: Label
var _options: VBoxContainer
var _choices := PackedStringArray()
var _highlight := 0
var _picked := -1
var _line_id := 0


func _ready() -> void:
	layer = 3
	process_mode = Node.PROCESS_MODE_ALWAYS
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
	_layout()
	_clear()


## Shows a line for `seconds` (or its reading time); await it.
func say(speaker: String, text: String, seconds := -1.0) -> void:
	history.append([speaker, text])
	said.emit(speaker, text)
	_line_id += 1
	var id := _line_id
	_show_line(speaker, text)
	var t := seconds
	if t <= 0.0:
		t = line_seconds if line_seconds >= 0.0 else maxf(MIN_SECONDS, text.length() / CHARS_PER_SECOND)
	await get_tree().create_timer(t, true).timeout
	if id == _line_id:
		_clear()


## Offers `options` under an optional line; returns the index picked.
func choose(options: PackedStringArray, speaker := "", text := "") -> int:
	_line_id += 1
	_show_line(speaker, text)
	_choices = options
	_highlight = 0
	_picked = -1
	_draw_options()
	if auto_choice.is_valid():
		await get_tree().process_frame
		_picked = auto_choice.call(options)
	while _picked < 0:
		await get_tree().process_frame
	var picked := _picked
	history.append(["", "> " + options[picked]])
	chose.emit(options, picked)
	_choices = PackedStringArray()
	_clear()
	return picked


func is_choosing() -> bool:
	return not _choices.is_empty()


func _input(event: InputEvent) -> void:
	if _choices.is_empty():
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
		var l := _label(PICK_COLOR if i == _highlight else DIM_COLOR)
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
	return l


## Sized from the window height, like the interact dot.
func _font_size(factor: float) -> int:
	return maxi(10, roundi(get_viewport().get_visible_rect().size.y / 540.0 * 15.0 * factor))


func _layout() -> void:
	var win := get_viewport().get_visible_rect().size
	_box.position = Vector2(win.x * 0.15, 0.0)
	_box.size = Vector2(win.x * 0.7, win.y * 0.93)
	# Small caps: the name in capitals, smaller than the line.
	_speaker.add_theme_font_size_override(&"font_size", _font_size(0.75))
	_text.add_theme_font_size_override(&"font_size", _font_size(1.0))
	_draw_options()
