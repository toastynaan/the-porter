class_name ChronicleView
extends MenuPage
## The chronicle entry that closes the game (docs/log/full-game-run.md,
## "Endings"): written decades later in a plain chronicler's voice, the
## official version, which never matches what the porter saw. Its last line
## follows the thing in the crypt down the years. It goes on like a card.

signal done

@export var seconds := 40.0

var _initial: Label
var _body: RichTextLabel
var _last: RichTextLabel
var _hint: RichTextLabel
var _shown_at := 0.0
var _open := false


func build() -> void:
	page_width = 400.0
	page.custom_minimum_size.x = px(400.0)
	var row := HBoxContainer.new()
	row.add_theme_constant_override(&"separation", px(6.0))
	_initial = Manuscript.title("", px(56.0))
	_initial.add_theme_color_override(&"font_color", Manuscript.RUBRIC)
	_initial.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	row.add_child(_initial)
	_body = Manuscript.rich("", px(15.0))
	_body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(_body)
	column.add_child(row)
	_last = add_text("", 15.0)
	_hint = add_text("", 11.0)
	_hint.add_theme_color_override(&"default_color", Manuscript.FADED_INK)


## Shows the ending's chronicle; await it.
func show_ending(title_text: String, chronicle: String, last_line: String) -> void:
	heading.text = title_text
	var body := chronicle.strip_edges()
	_initial.text = body.substr(0, 1)
	_body.text = body.substr(1)
	_last.text = "[center][i]%s[/i][/center]" % last_line
	_hint.text = "[center][i]Press E[/i][/center]"
	open()
	_open = true
	_shown_at = 0.0
	await done


func _process(delta: float) -> void:
	if not _open:
		return
	_shown_at += delta
	if _shown_at >= seconds:
		_finish()


func _input(event: InputEvent) -> void:
	if not _open or _shown_at < 1.0:
		return
	if Press.fresh(event, &"interact") or Press.fresh(event, &"ui_accept"):
		get_viewport().set_input_as_handled()
		_finish()


func _finish() -> void:
	if not _open:
		return
	_open = false
	close()
	done.emit()


func _unhandled_input(_event: InputEvent) -> void:
	pass
