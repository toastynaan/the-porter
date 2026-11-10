class_name TalkView
extends Control
## What Talk shows (Look and Feel, "UI": plain subtitles at the bottom, the
## speaker's name in small caps, no portraits; up to three numbered answers,
## then "Walk away"). One column at the bottom of the screen, in the book
## face the menus use:
##
##              The supper bell, across the court.
##
##                THOMAS  Quietly, so only you hear.
##           Not his physic. Not that one. Trust me.
##
##              | 1  What is it?
##                2  Why not?
##                3  Walk away
##
## - Something heard while he's talking or being asked something (a bell, a
##   thing he notices), small and soft at the top, so it never takes the
##   question's place.
## - The name in small capitals, lantern-coloured (the porter's own, paler),
##   with the line's aside beside it in italics.
## - The line, centred. Narration (what he sees, hears or does) is in italics,
##   softer, with no name.
## - The answers in a block under it, left-aligned and numbered. The one the
##   arrows are on is brighter, with a thin flame-coloured bar; what he does
##   (rather than says) is in italics; walking away is dimmer.
## A soft dark gradient lies under it all so it reads over a lit wall; the
## Settings' dark band draws a solid one instead. Lines and answers fade in
## and out. The one thing that moves is a line already up when its answers
## come up under it: it rises to make room, not jumps (it does jump with the
## Settings' less motion). Sizes follow the window height and the subtitle
## size setting.

const FONT := preload("res://art/fonts/eb_garamond/EBGaramond.ttf")
## Solid colours, dimmer rather than more see-through, so a quiet line
## reads the same over a dark wall and a lit one.
const TEXT := Color("#D8C9A3")
const BRIGHT := Color("#F4E8C6")
const NARRATION := Color("#C2BBA6")
## Lantern, for whoever speaks; the porter's own name is paler.
const NAME := Color("#D29A57")
const OWN_NAME := Color("#A0957A")
const ASIDE := Color("#A8A18E")
const HEARD := Color("#B0A994")
const IDLE := Color("#A59B80")
const LEAVE := Color("#7C7461")
const NUMBER := Color("#7C7461")
const MARK := Color("#E0A458")
const SHADE := Color(0.016, 0.018, 0.027)
## Sizes in window-height units (1 at 540 lines), before the subtitle size.
const LINE_SIZE := 19.0
const NAME_SIZE := 11.5
const ASIDE_SIZE := 14.0
const HEARD_SIZE := 14.5
const OPTION_SIZE := 17.0
## The column: this much of the window's width, at most this wide; and how
## far down the window its bottom edge is.
const COLUMN := 0.62
const COLUMN_MAX := 620.0
const BOTTOM := 0.935
## Seconds: everything coming and going, a new line, each answer after the last.
const FADE_IN := 0.16
const FADE_OUT := 0.22
const OPTION_STEP := 0.04
## Seconds the question takes to rise as its answers come up under it.
const RISE := 0.24

## What is shown now, as a test reads it: who speaks, the aside, the words,
## whether it's narration.
var speaker := ""
var aside := ""
var words := ""
var narrated := false
## What's shown above it as heard meanwhile ("" for nothing).
var heard := ""

var _scrim: TextureRect
## Holds the block; set down and eased back up as answers come up under a line.
var _lift: Control
var _rise: Tween
## Whose line is on screen (name and aside), and the whole of it, until it's
## taken down; and the frame it came up on.
var _voice := ["", ""]
var _on_screen := []
var _new_on_frame := -1
var _block: PanelContainer
var _column: VBoxContainer
var _heard: Label
var _heard_gap: Control
var _header: HBoxContainer
var _name: Label
var _aside: Label
var _line: Label
var _gap: Control
var _options: VBoxContainer
var _book: FontVariation
var _italic: FontVariation
var _caps: FontVariation
var _band: StyleBoxFlat
var _no_band: StyleBox = StyleBoxEmpty.new()
## A line, something heard, and answers, are up (what's on screen may still
## be fading out).
var _line_live := false
var _heard_live := false
var _options_live := false
var _shown := false
var _presence: Tween
var _line_fade: Tween
var _choices := PackedStringArray()
var _leave := -1
var _highlight := 0
## Each row: [mark ColorRect, number Label, text Label].
var _rows: Array = []


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	modulate.a = 0.0
	_make_fonts()
	_scrim = TextureRect.new()
	_scrim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_scrim.stretch_mode = TextureRect.STRETCH_SCALE
	_scrim.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_scrim.texture = _shade()
	add_child(_scrim)
	_band = StyleBoxFlat.new()
	_band.bg_color = Color(SHADE, 0.8)
	# Pinned to a point at the bottom, in the middle: it keeps to the size of
	# what's in it, growing upward and to both sides.
	_block = PanelContainer.new()
	_block.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_block.anchor_left = 0.5
	_block.anchor_right = 0.5
	_block.anchor_top = BOTTOM
	_block.anchor_bottom = BOTTOM
	_block.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_block.grow_vertical = Control.GROW_DIRECTION_BEGIN
	_lift = Control.new()
	_lift.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_lift)
	_lift.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_lift.add_child(_block)
	_column = VBoxContainer.new()
	_column.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_column.alignment = BoxContainer.ALIGNMENT_END
	_block.add_child(_column)
	_heard = _label(_italic, HEARD)
	_heard.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_heard.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_column.add_child(_heard)
	_heard_gap = Control.new()
	_heard_gap.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_column.add_child(_heard_gap)
	_header = HBoxContainer.new()
	_header.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_header.alignment = BoxContainer.ALIGNMENT_CENTER
	_column.add_child(_header)
	_name = _label(_caps, NAME)
	_name.size_flags_vertical = Control.SIZE_SHRINK_END
	_aside = _label(_italic, ASIDE)
	_aside.size_flags_vertical = Control.SIZE_SHRINK_END
	_header.add_child(_name)
	_header.add_child(_aside)
	_line = _label(_book, TEXT)
	_line.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_line.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_column.add_child(_line)
	_gap = Control.new()
	_gap.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_column.add_child(_gap)
	_options = VBoxContainer.new()
	_options.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_options.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	_column.add_child(_options)
	_block.item_rect_changed.connect(_place_shade)
	get_viewport().size_changed.connect(layout)
	Settings.changed.connect(layout)
	_hide_line()
	_hide_heard()
	_drop_options()
	layout()


## Shows a line: "Name" and its words, with any aside beside the name; or
## narration (a line wholly in brackets), with no name. Empty: no line.
func show_line(who: String, text: String) -> void:
	var split := Talk.aside(text)
	var told := Talk.narration(text)
	var was := [speaker, aside, words, narrated]
	narrated = not told.is_empty()
	speaker = "" if narrated else who
	aside = "" if narrated else String(split[0])
	words = told if narrated else String(split[1])
	if was == [speaker, aside, words, narrated]:
		return
	if words.is_empty() and speaker.is_empty() and aside.is_empty():
		# Gone: with answers still up it goes now, otherwise it fades with the rest.
		_line_live = false
		if _options_live or _heard_live:
			_hide_line()
		_present()
		return
	_line_live = true
	_drop_stale()
	# Still on screen from a moment ago (a line that ended as its answers
	# came up): it stays as it is.
	var now := [speaker, aside, words, narrated]
	if _on_screen == now:
		_gap.visible = _options_live
		_present()
		return
	_on_screen = now
	_new_on_frame = Engine.get_process_frames()
	_name.text = speaker.to_upper()
	_name.visible = not speaker.is_empty()
	_name.add_theme_color_override(&"font_color", OWN_NAME if speaker == Talk.PORTER else NAME)
	_aside.text = aside
	_aside.visible = not aside.is_empty()
	_header.visible = _name.visible or _aside.visible
	_line.text = words
	_line.visible = not words.is_empty()
	_line.add_theme_font_override(&"font", _italic if narrated else _book)
	_line.add_theme_color_override(&"font_color", NARRATION if narrated else TEXT)
	_gap.visible = _options_live
	if _line_fade:
		_line_fade.kill()
	# The name stays lit while the same person goes on talking.
	var same_voice: bool = _voice == [speaker, aside] and not speaker.is_empty()
	_voice = [speaker, aside]
	_line_fade = create_tween().set_parallel()
	_line.modulate.a = 0.0
	_line_fade.tween_property(_line, ^"modulate:a", 1.0, FADE_IN)
	if same_voice:
		_header.modulate.a = 1.0
	else:
		_header.modulate.a = 0.0
		_line_fade.tween_property(_header, ^"modulate:a", 1.0, FADE_IN)
	_present()


## Shows something heard meanwhile, small, above the line: narration in
## italics, or "NAME  words". Empty: nothing.
func show_heard(who: String, text: String) -> void:
	var told := Talk.narration(text)
	var now := told if not told.is_empty() else ("%s  %s" % [who.to_upper(), text] if not who.is_empty() else text)
	if now == heard:
		return
	heard = now
	_heard_live = not heard.is_empty()
	if not _heard_live:
		# With anything else still up it goes now, otherwise it fades with the rest.
		if _line_live or _options_live:
			_hide_heard()
		_present()
		return
	_drop_stale()
	_heard.text = heard
	_heard.add_theme_font_override(&"font", _italic if not told.is_empty() else _book)
	_heard.visible = true
	_heard_gap.visible = true
	_heard.modulate.a = 0.0
	_heard.create_tween().tween_property(_heard, ^"modulate:a", 1.0, FADE_IN)
	_present()


## Shows the answers, numbered; `leave` is the one that walks away (-1:
## none), `highlight` the one the arrows are on.
func show_options(options: PackedStringArray, leave: int, highlight: int) -> void:
	_choices = options
	_leave = leave
	_highlight = highlight
	_options_live = true
	_drop_stale()
	# A line already up rises to make room for them.
	var rising := _shown and _line_live and _new_on_frame != Engine.get_process_frames() and not Settings.less_motion
	var before := _column.get_combined_minimum_size().y
	_gap.visible = _line_live
	_build_options(true)
	_settle()
	if rising:
		_lift.position.y = _column.get_combined_minimum_size().y - before
		_rise = create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
		_rise.tween_property(_lift, ^"position:y", 0.0, RISE)
	_present()


func set_highlight(index: int) -> void:
	_highlight = index
	_paint_options()


## The answers go: now if a line is still up, otherwise fading with the rest.
func clear_options() -> void:
	_choices = PackedStringArray()
	_options_live = false
	if _line_live or _heard_live:
		_drop_options()
		_gap.visible = false
	_settle()
	_present()


## The answers as shown, without their numbers or brackets.
func option_texts() -> PackedStringArray:
	var out := PackedStringArray()
	if _options_live:
		for row: Array in _rows:
			out.append((row[2] as Label).text)
	return out


## Whether answer `index` shows as something he does (in italics).
func option_done(index: int) -> bool:
	return index == _leave or not Talk.narration(_choices[index]).is_empty()


## Sizes everything for the window and the Settings.
func layout() -> void:
	var u := _unit()
	var scale_by := Settings.subtitle_scale()
	_caps.spacing_glyph = roundi(1.6 * u * scale_by)
	_size(_name, NAME_SIZE)
	_size(_aside, ASIDE_SIZE)
	_size(_line, LINE_SIZE)
	_size(_heard, HEARD_SIZE)
	_heard_gap.custom_minimum_size.y = roundf(7.0 * u)
	_header.add_theme_constant_override(&"separation", roundi(7.0 * u))
	_column.add_theme_constant_override(&"separation", roundi(3.0 * u))
	_column.custom_minimum_size.x = minf(get_viewport_rect().size.x * COLUMN, COLUMN_MAX * u * maxf(scale_by, 1.0))
	_gap.custom_minimum_size.y = roundf(5.0 * u)
	_options.add_theme_constant_override(&"separation", roundi(2.0 * u))
	_band.set_corner_radius_all(roundi(3.0 * u))
	_band.content_margin_left = 16.0 * u
	_band.content_margin_right = 16.0 * u
	_band.content_margin_top = 10.0 * u
	_band.content_margin_bottom = 10.0 * u
	var panel: StyleBox = _no_band
	if Settings.subtitle_backing:
		panel = _band
	_block.add_theme_stylebox_override(&"panel", panel)
	_scrim.visible = not Settings.subtitle_backing
	if not _rows.is_empty():
		_build_options(false)
	_place_shade()


## The shade reaches from a little above the column to the bottom.
func _place_shade() -> void:
	var win := get_viewport_rect().size
	var top := maxf(_block.position.y - 90.0 * _unit(), 0.0)
	_scrim.position = Vector2(0.0, top)
	_scrim.size = Vector2(win.x, win.y - top)


func _build_options(animate: bool) -> void:
	_drop_options()
	_options.visible = not _choices.is_empty()
	var u := _unit()
	var size_px := _px(OPTION_SIZE)
	var widest := _column.custom_minimum_size.x - 40.0 * u
	for i in _choices.size():
		var done := Talk.narration(_choices[i])
		var row := HBoxContainer.new()
		row.mouse_filter = Control.MOUSE_FILTER_IGNORE
		row.add_theme_constant_override(&"separation", roundi(9.0 * u))
		var mark := ColorRect.new()
		mark.mouse_filter = Control.MOUSE_FILTER_IGNORE
		mark.custom_minimum_size = Vector2(maxf(roundf(1.5 * u), 1.0), 0.0)
		var number := _label(_book, NUMBER)
		number.text = str(i + 1)
		_size(number, OPTION_SIZE)
		number.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		number.custom_minimum_size.x = roundf(9.0 * u * Settings.subtitle_scale())
		var text := _label(_italic if option_done(i) else _book, IDLE)
		text.text = done if not done.is_empty() else _choices[i]
		_size(text, OPTION_SIZE)
		# A long answer wraps inside the column.
		if _book.get_string_size(text.text, HORIZONTAL_ALIGNMENT_LEFT, -1, size_px).x > widest:
			text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			text.custom_minimum_size.x = widest
		row.add_child(mark)
		row.add_child(number)
		row.add_child(text)
		if i == _leave and i > 0:
			# Walking away stands a little apart from the answers.
			var apart := Control.new()
			apart.mouse_filter = Control.MOUSE_FILTER_IGNORE
			apart.custom_minimum_size.y = roundf(3.0 * u)
			_options.add_child(apart)
		_options.add_child(row)
		_rows.append([mark, number, text])
		if animate:
			row.modulate.a = 0.0
			var t := row.create_tween()
			t.tween_interval(FADE_IN * 0.5 + OPTION_STEP * i)
			t.tween_property(row, ^"modulate:a", 1.0, FADE_IN)
	_paint_options()


func _paint_options() -> void:
	for i in _rows.size():
		var row: Array = _rows[i]
		var on := i == _highlight
		(row[0] as ColorRect).color = Color(MARK, 0.95 if on else 0.0)
		var idle: Color = LEAVE if i == _leave else IDLE
		(row[1] as Label).add_theme_color_override(&"font_color", MARK if on else NUMBER)
		(row[2] as Label).add_theme_color_override(&"font_color", BRIGHT if on else idle)


## Fades the whole thing in while there is something to show, and out after;
## once it's out, what was on it is taken down.
func _present() -> void:
	var want := _line_live or _options_live or _heard_live
	if want == _shown:
		return
	_shown = want
	if _presence:
		_presence.kill()
	_presence = create_tween()
	_presence.tween_property(self, ^"modulate:a", 1.0 if want else 0.0, FADE_IN if want else FADE_OUT)
	if not want:
		_presence.tween_callback(_take_down)


func _take_down() -> void:
	_hide_line()
	_hide_heard()
	_drop_options()


## Takes down what has gone but was left up to fade with the rest.
func _drop_stale() -> void:
	if not _line_live:
		_hide_line()
	if not _heard_live:
		_hide_heard()
	if not _options_live:
		_drop_options()


## The block is where it belongs, with nothing easing it there.
func _settle() -> void:
	if _rise:
		_rise.kill()
	_lift.position.y = 0.0


func _hide_line() -> void:
	_header.visible = false
	_line.visible = false
	_gap.visible = false
	_voice = ["", ""]
	_on_screen = []


func _hide_heard() -> void:
	_heard.visible = false
	_heard_gap.visible = false


func _drop_options() -> void:
	_rows.clear()
	for c in _options.get_children():
		_options.remove_child(c)
		c.queue_free()
	_options.visible = false


func _make_fonts() -> void:
	var weight := TextServerManager.get_primary_interface().name_to_tag("wght")
	_book = FontVariation.new()
	_book.base_font = FONT
	_book.variation_opentype = {weight: 500}
	_italic = FontVariation.new()
	_italic.base_font = FONT
	_italic.variation_opentype = {weight: 500}
	_italic.variation_transform = Transform2D(Vector2(1.0, 0.0), Vector2(0.2, 1.0), Vector2.ZERO)
	_caps = FontVariation.new()
	_caps.base_font = FONT
	_caps.variation_opentype = {weight: 600}


## Dark at the bottom, clear at the top.
func _shade() -> GradientTexture2D:
	var g := Gradient.new()
	g.offsets = PackedFloat32Array([0.0, 0.45, 1.0])
	g.colors = PackedColorArray([Color(SHADE, 0.0), Color(SHADE, 0.4), Color(SHADE, 0.8)])
	var tex := GradientTexture2D.new()
	tex.gradient = g
	tex.width = 4
	tex.height = 128
	tex.fill_from = Vector2(0.5, 0.0)
	tex.fill_to = Vector2(0.5, 1.0)
	return tex


func _label(font: Font, color: Color) -> Label:
	var l := Label.new()
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.add_theme_font_override(&"font", font)
	l.add_theme_color_override(&"font_color", color)
	l.add_theme_color_override(&"font_outline_color", Color(0.0, 0.0, 0.0, 0.55))
	l.add_theme_color_override(&"font_shadow_color", Color(0.0, 0.0, 0.0, 0.4))
	return l


func _size(l: Label, units: float) -> void:
	var u := _unit()
	l.add_theme_font_size_override(&"font_size", _px(units))
	l.add_theme_constant_override(&"outline_size", roundi(2.0 * u))
	l.add_theme_constant_override(&"shadow_outline_size", roundi(2.0 * u))
	l.add_theme_constant_override(&"shadow_offset_x", 0)
	l.add_theme_constant_override(&"shadow_offset_y", roundi(1.0 * u))


func _px(units: float) -> int:
	return maxi(10, roundi(_unit() * units * Settings.subtitle_scale()))


func _unit() -> float:
	return maxf(get_viewport_rect().size.y / 540.0, 0.5)
