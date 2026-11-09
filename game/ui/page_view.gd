class_name PageView
extends Control
## A page the porter holds up to read (Readable: the cult's book, a letter),
## like the ledger: parchment, a title, the text. `interact`, the ledger or
## the satchel puts it down; so does walking off.

var showing := false

var _page: PanelContainer
var _title: Label
var _body: RichTextLabel
var _shown_for := 0.0


func _ready() -> void:
	add_to_group(&"page_view")
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
	_title = Manuscript.title("", 26)
	column.add_child(_title)
	_body = Manuscript.rich("", 15)
	column.add_child(_body)
	visible = false
	get_viewport().size_changed.connect(_layout)
	_layout()


func show_page(title_text: String, body: String) -> void:
	for book: Node in get_tree().get_nodes_in_group(&"held_books"):
		if book != self and book.get(&"showing") == true:
			book.call(&"set_showing", false)
	_title.text = title_text
	_body.text = body
	set_showing(true)


func set_showing(value: bool) -> void:
	showing = value
	visible = value
	_shown_for = 0.0


func _process(delta: float) -> void:
	if not showing:
		return
	_shown_for += delta
	var p := get_tree().get_first_node_in_group(&"player") as Player
	if p and Vector2(p.velocity.x, p.velocity.z).length() > 0.5 and _shown_for > 0.5:
		set_showing(false)


func _unhandled_input(event: InputEvent) -> void:
	if showing and _shown_for > 0.3 and (Press.fresh(event, &"interact") or Press.fresh(event, &"ledger") or Press.fresh(event, &"satchel")):
		set_showing(false)
		get_viewport().set_input_as_handled()


func _layout() -> void:
	var u := Manuscript.unit(self)
	_page.size = Vector2(minf(get_viewport_rect().size.x * 0.55, 400.0 * u), 0.0)
	_page.position = Vector2((get_viewport_rect().size.x - _page.size.x) * 0.5, get_viewport_rect().size.y * 0.12)
	_title.add_theme_font_size_override(&"font_size", roundi(26.0 * u))
	for f in [&"normal_font_size", &"italics_font_size", &"bold_font_size"]:
		_body.add_theme_font_size_override(f, roundi(15.0 * u))
