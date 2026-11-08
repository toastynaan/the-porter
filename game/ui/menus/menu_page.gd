class_name MenuPage
extends Control
## A page of the menus (the run's spec, "Menus"; Look and Feel, "UI": the
## manuscript style): a parchment page in the middle of the screen with a
## blackletter title and a column of buttons or text. Works with the mouse,
## the keyboard and the gamepad (the ui_ actions); `ui_cancel` goes back.
## Runs while the game is paused.

signal back

const PAGE_SOUND := preload("res://art/sfx/sfx_page.wav")

## Behind the page: the night itself (the title) or the game, dimmed (pause).
@export var backdrop := Color(Manuscript.NIGHT, 0.82)
## The page's width in 540-line units.
@export var page_width := 300.0

var page: PanelContainer
var column: VBoxContainer
var heading: Label

var _sound: AudioStreamPlayer


func _init() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	visible = false


func _ready() -> void:
	var u := Manuscript.unit(self)
	var shade := ColorRect.new()
	shade.color = backdrop
	shade.set_anchors_preset(Control.PRESET_FULL_RECT)
	shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(shade)
	var centre := CenterContainer.new()
	centre.set_anchors_preset(Control.PRESET_FULL_RECT)
	centre.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(centre)
	page = PanelContainer.new()
	page.add_theme_stylebox_override(&"panel", Manuscript.page_style(24.0 * u))
	page.custom_minimum_size = Vector2(page_width * u, 0.0)
	centre.add_child(page)
	column = VBoxContainer.new()
	column.add_theme_constant_override(&"separation", roundi(6.0 * u))
	page.add_child(column)
	heading = Manuscript.title("", roundi(30.0 * u))
	column.add_child(heading)
	_sound = AudioStreamPlayer.new()
	_sound.stream = PAGE_SOUND
	add_child(_sound)
	build()


## Fills the column (pages override this).
func build() -> void:
	pass


## A text size in 540-line units, scaled to the window.
func px(units: float) -> int:
	return roundi(units * Manuscript.unit(self))


func add_button(label: String, on_press: Callable) -> Button:
	var b := Manuscript.button(label, px(17.0))
	b.pressed.connect(func() -> void:
		_page_turn()
		on_press.call())
	column.add_child(b)
	return b


func add_text(body: String, font_size := 14.0) -> RichTextLabel:
	var r := Manuscript.rich(body, px(font_size))
	column.add_child(r)
	return r


func open() -> void:
	visible = true
	refresh()
	_page_turn()
	focus_first.call_deferred()


func close() -> void:
	visible = false


## Updates what the page shows each time it opens (pages override this).
func refresh() -> void:
	pass


func focus_first() -> void:
	for c in column.get_children():
		if c is Control and (c as Control).focus_mode == Control.FOCUS_ALL and (c as Control).visible:
			(c as Control).grab_focus()
			return


func _page_turn() -> void:
	if AudioOut.enabled():
		_sound.play()


func _unhandled_input(event: InputEvent) -> void:
	if visible and event.is_action_pressed(&"ui_cancel"):
		get_viewport().set_input_as_handled()
		back.emit()
