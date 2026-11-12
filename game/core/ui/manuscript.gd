class_name Manuscript
## The manuscript style every page and menu shares (Look and Feel, "UI":
## parchment, blackletter only for titles, a readable book face for the rest).

const PARCHMENT := Color("#CDBB93")
const PARCHMENT_EDGE := Color("#8A7552")
const INK := Color("#2B1D12")
const FADED_INK := Color(0.17, 0.11, 0.07, 0.55)
## Old blood: the decorated initial on the chronicle's pages.
const RUBRIC := Color("#5A1A14")
const NIGHT := Color("#0B0C10")
const TITLE_FONT := preload("res://art/fonts/unifraktur_maguntia/UnifrakturMaguntia-Book.ttf")
const BOOK_FONT := preload("res://art/fonts/eb_garamond/EBGaramond.ttf")


## Window-height units: 1 at 540 lines.
static func unit(node: CanvasItem) -> float:
	return maxf(node.get_viewport_rect().size.y / 540.0, 0.5)


static func page_style(margin := 28.0) -> StyleBoxFlat:
	var paper := StyleBoxFlat.new()
	paper.bg_color = PARCHMENT
	paper.border_color = PARCHMENT_EDGE
	paper.set_border_width_all(3)
	paper.set_content_margin_all(margin)
	return paper


static func title(label: String, size: int) -> Label:
	var l := Label.new()
	l.text = label
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.add_theme_font_override(&"font", TITLE_FONT)
	l.add_theme_font_size_override(&"font_size", size)
	l.add_theme_color_override(&"font_color", INK)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


static func rich(body: String, size: int, color := INK) -> RichTextLabel:
	var r := RichTextLabel.new()
	r.bbcode_enabled = true
	r.fit_content = true
	r.scroll_active = false
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	r.focus_mode = Control.FOCUS_NONE
	for f in [&"normal_font", &"italics_font", &"bold_font"]:
		r.add_theme_font_override(f, BOOK_FONT)
	for f in [&"normal_font_size", &"italics_font_size", &"bold_font_size"]:
		r.add_theme_font_size_override(f, size)
	r.add_theme_color_override(&"default_color", color)
	r.text = body
	return r


## A menu button: ink on parchment, darker when it has focus.
static func button(label: String, size: int) -> Button:
	var b := Button.new()
	b.text = label
	b.flat = true
	b.focus_mode = Control.FOCUS_ALL
	b.alignment = HORIZONTAL_ALIGNMENT_CENTER
	b.add_theme_font_override(&"font", BOOK_FONT)
	b.add_theme_font_size_override(&"font_size", size)
	b.add_theme_color_override(&"font_color", FADED_INK)
	b.add_theme_color_override(&"font_hover_color", INK)
	b.add_theme_color_override(&"font_focus_color", INK)
	b.add_theme_color_override(&"font_pressed_color", RUBRIC)
	var focus := StyleBoxFlat.new()
	focus.bg_color = Color(PARCHMENT_EDGE, 0.25)
	focus.set_content_margin_all(2)
	b.add_theme_stylebox_override(&"focus", focus)
	b.add_theme_stylebox_override(&"hover", focus)
	return b
