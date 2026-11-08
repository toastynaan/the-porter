class_name SatchelView
extends Control
## The porter's satchel, held up with `satchel` like the ledger
## (docs/mechanics.md, "Your hands"): what he carries, a line for each, in
## his hands rather than on a grid. Keys, evidence, clean food and the thing
## he holds to throw. The night goes on while he looks.

var showing := false

var _page: PanelContainer
var _title: Label
var _body: RichTextLabel


func _ready() -> void:
	add_to_group(&"held_books")
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_page = PanelContainer.new()
	_page.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_page.add_theme_stylebox_override(&"panel", Manuscript.page_style())
	add_child(_page)
	var column := VBoxContainer.new()
	column.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_page.add_child(column)
	_title = Manuscript.title("The Satchel", 30)
	column.add_child(_title)
	_body = Manuscript.rich("", 15)
	column.add_child(_body)
	visible = false
	get_viewport().size_changed.connect(_layout)
	_layout()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"satchel") and not get_tree().paused:
		set_showing(not showing)
		get_viewport().set_input_as_handled()


func set_showing(value: bool) -> void:
	showing = value
	visible = value
	if value:
		for book: Node in get_tree().get_nodes_in_group(&"held_books"):
			if book != self and book.get(&"showing") == true:
				book.call(&"set_showing", false)
		refresh()


## Rewrites the page from what he carries.
func refresh() -> void:
	_body.text = page_text()


static func page_text() -> String:
	var text := ""
	if GameState.keys.is_empty():
		text += "[i]No keys.[/i]\n"
	else:
		var names := PackedStringArray()
		for k in GameState.keys:
			names.append(Items.KEY_NAMES.get(k, String(k)))
		text += "[b]Keys[/b], for %s.\n" % _join(names)
	for id in GameState.satchel:
		text += "[b]%s.[/b] %s\n" % [Items.display_name(id), Items.line(id)]
	if GameState.satchel.is_empty():
		text += "[color=#%s]Nothing else.[/color]\n" % Manuscript.FADED_INK.to_html()
	return text


static func _join(names: PackedStringArray) -> String:
	if names.size() <= 1:
		return "".join(names)
	return ", ".join(names.slice(0, names.size() - 1)) + " and " + names[-1]


func _layout() -> void:
	var u := Manuscript.unit(self)
	_page.size = Vector2(minf(get_viewport_rect().size.x * 0.5, 360.0 * u), 0.0)
	_page.position = Vector2((get_viewport_rect().size.x - _page.size.x) * 0.5, get_viewport_rect().size.y * 0.12)
	_title.add_theme_font_size_override(&"font_size", roundi(30.0 * u))
	for f in [&"normal_font_size", &"italics_font_size", &"bold_font_size"]:
		_body.add_theme_font_size_override(f, roundi(15.0 * u))
