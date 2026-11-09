class_name ChapterCard
extends MenuPage
## A chapter card (Look and Feel, "UI": a page from the chronicle, with a
## decorated initial letter): the night's heading and title, and the
## chronicle's few lines about it. It goes on when the porter presses
## `interact` (or accept, or clicks), or by itself after `seconds`.

signal done

## Seconds the card stays up if nobody presses anything (tests shorten it).
@export var seconds := 14.0

var _sub: RichTextLabel
var _initial: Label
var _body: RichTextLabel
var _hint: RichTextLabel
var _shown_at := 0.0
var _open := false


func build() -> void:
	page_width = 380.0
	page.custom_minimum_size.x = px(380.0)
	_sub = add_text("", 13.0)
	_sub.add_theme_color_override(&"default_color", Manuscript.FADED_INK)
	column.move_child(_sub, 0)
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
	_hint = add_text("", 11.0)
	_hint.add_theme_color_override(&"default_color", Manuscript.FADED_INK)


## Shows `chapter`'s card; await it.
func show_chapter(chapter: Chapter) -> void:
	_sub.text = "[center]%s[/center]" % chapter.heading.to_upper()
	heading.text = chapter.title
	var body := chapter.card.strip_edges()
	_initial.text = body.substr(0, 1)
	_body.text = body.substr(1)
	_hint.text = "[center][i]Press E to go on[/i][/center]"
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
	if not _open or _shown_at < 0.5:
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
