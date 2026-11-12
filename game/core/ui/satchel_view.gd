class_name SatchelView
extends Control
## The porter's satchel, held up with `satchel` like the ledger
## (docs/systems/mechanics.md, "Your hands"): what he carries, a line for each, in
## his hands rather than on a grid. Keys, evidence, clean food and the thing
## he holds to throw. Hungry, `interact` eats the clean food he carries. The
## night goes on while he looks.

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
	if Press.fresh(event, &"satchel") and not get_tree().paused:
		set_showing(not showing)
		get_viewport().set_input_as_handled()
	elif showing and Press.fresh(event, &"interact") and eat_food():
		refresh()
		get_viewport().set_input_as_handled()


## Eats the first clean food in the satchel, if he's hungry.
func eat_food() -> bool:
	if not GameState.is_hungry():
		return false
	for id in GameState.satchel:
		if Items.kind(id) == &"food":
			Pickup.eat(id, self)
			return true
	return false


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
	var hand := _lantern_hand()
	if hand and hand.owned:
		if hand.showing():
			text += "[b]The lantern[/b], in your hand. [color=#%s][i]G: put it away[/i][/color]\n" % Manuscript.FADED_INK.to_html()
		elif not hand.held:
			text += "[b]The lantern[/b], put away. [color=#%s][i]G: take it out[/i][/color]\n" % Manuscript.FADED_INK.to_html()
		else:
			text += "[b]The lantern[/b], put away while you're indoors.\n"
	for id in GameState.satchel:
		text += "[b]%s.[/b] %s\n" % [Items.display_name(id), Items.line(id)]
	if GameState.satchel.is_empty() and not (hand and hand.owned):
		text += "[color=#%s]Nothing else.[/color]\n" % Manuscript.FADED_INK.to_html()
	elif GameState.is_hungry() and GameState.satchel.any(func(i: StringName) -> bool: return Items.kind(i) == &"food"):
		text += "\n[center][color=#%s][i]E: eat[/i][/color][/center]" % Manuscript.FADED_INK.to_html()
	return text


static func _lantern_hand() -> LanternHand:
	var tree := Engine.get_main_loop() as SceneTree
	var p := tree.get_first_node_in_group(&"player") as Player if tree else null
	return p.lantern_hand if p else null


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
