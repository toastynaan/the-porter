class_name LedgerView
extends Control
## The porter's ledger, held up with `ledger` (Look and Feel, "UI": who came
## in is shown by the ledger, written in a manuscript hand on parchment; the
## ledger and the candle clock say what is due). An object he carries, not a
## HUD, with two pages (docs/mechanics.md, "The ledger's notes"): tonight's
## guests as he wrote them and tonight's duties, the done ones struck
## through; then his notes, oldest first, a night to a section. `ledger`
## turns to the notes, and again puts it away. The night goes on while he
## reads.

const PARCHMENT := Color("#CDBB93")
const INK := Color("#2B1D12")
const FADED_INK := Color(0.17, 0.11, 0.07, 0.55)
const TITLE_FONT := preload("res://art/fonts/unifraktur_maguntia/UnifrakturMaguntia-Book.ttf")
const BOOK_FONT := preload("res://art/fonts/eb_garamond/EBGaramond.ttf")

var showing := false
## 0: guests and duties; 1: notes.
var page := 0

var _page: PanelContainer
var _title: Label
var _body: RichTextLabel


func _ready() -> void:
	add_to_group(&"ledger_view")
	add_to_group(&"held_books")
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_page = PanelContainer.new()
	_page.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var paper := StyleBoxFlat.new()
	paper.bg_color = PARCHMENT
	paper.border_color = Color("#8A7552")
	paper.set_border_width_all(3)
	paper.set_content_margin_all(28)
	_page.add_theme_stylebox_override(&"panel", paper)
	add_child(_page)
	var column := VBoxContainer.new()
	column.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_page.add_child(column)
	_title = Label.new()
	_title.text = "The Ledger"
	_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_title.add_theme_font_override(&"font", TITLE_FONT)
	_title.add_theme_color_override(&"font_color", INK)
	column.add_child(_title)
	_body = RichTextLabel.new()
	_body.bbcode_enabled = true
	_body.fit_content = true
	_body.scroll_active = false
	_body.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_body.add_theme_font_override(&"normal_font", BOOK_FONT)
	_body.add_theme_font_override(&"italics_font", BOOK_FONT)
	_body.add_theme_color_override(&"default_color", INK)
	column.add_child(_body)
	visible = false
	get_viewport().size_changed.connect(_layout)
	_layout()


func _unhandled_input(event: InputEvent) -> void:
	if Press.fresh(event, &"ledger") and not get_tree().paused:
		if showing and page == 0:
			turn_to(1)
		else:
			set_showing(not showing)
		get_viewport().set_input_as_handled()


func set_showing(value: bool) -> void:
	showing = value
	visible = value
	page = 0
	if value:
		for book: Node in get_tree().get_nodes_in_group(&"held_books"):
			if book != self and book.get(&"showing") == true:
				book.call(&"set_showing", false)
		refresh()


func turn_to(p: int) -> void:
	page = p
	refresh()


## Rewrites the page from the ledger and the night's duties, or his notes.
func refresh() -> void:
	if page == 1:
		_title.text = "Notes"
		_body.text = notes_text()
		return
	_title.text = "The Ledger"
	var text := "[center][i]Guests[/i][/center]\n"
	var guests := GameState.ledger.filter(func(e: Dictionary) -> bool: return e.get("night", 0) == GameState.night)
	if guests.is_empty():
		text += "[color=#%s]None written tonight.[/color]\n" % FADED_INK.to_html()
	for e: Dictionary in guests:
		var line := String(e["name"])
		if not String(e["description"]).is_empty():
			line += ": " + String(e["description"])
		text += line + ".\n"
	var director := get_tree().get_first_node_in_group(&"night_director") as NightDirector
	if director:
		text += "\n[center][i]Duties[/i][/center]\n"
		for d: Array in director.duties():
			text += ("[s][color=#%s]%s[/color][/s]" % [FADED_INK.to_html(), d[0]]) if d[1] else String(d[0])
			text += "\n"
	text += "\n[center][color=#%s][i]L: the notes[/i][/color][/center]" % FADED_INK.to_html()
	_body.text = text


## The notes page: his notes, oldest first, under each night.
static func notes_text() -> String:
	if GameState.notes.is_empty():
		return "[color=#%s]Nothing written yet.[/color]" % FADED_INK.to_html()
	var text := ""
	var night := -1
	for n: Dictionary in GameState.notes:
		if int(n.get("night", 0)) != night:
			night = int(n.get("night", 0))
			text += "[center][i]%s[/i][/center]\n" % ("The first evening" if night == 0 else "Night %d" % night)
		text += String(n.get("text", "")) + "\n"
	return text


func _layout() -> void:
	var win := get_viewport().get_visible_rect().size
	var u := win.y / 540.0
	_page.size = Vector2(minf(win.x * 0.5, 360.0 * u), 0.0)
	_page.position = Vector2((win.x - _page.size.x) * 0.5, win.y * 0.12)
	_title.add_theme_font_size_override(&"font_size", roundi(30.0 * u))
	_body.add_theme_font_size_override(&"normal_font_size", roundi(15.0 * u))
	_body.add_theme_font_size_override(&"italics_font_size", roundi(16.0 * u))
