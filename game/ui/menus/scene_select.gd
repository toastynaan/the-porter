class_name SceneSelect
extends MenuPage
## For testing, in debug builds only (the title's "Test a scene"): start any
## chapter at any of its beats, without playing what comes before. The beats
## are read from the chapter's scene (its Director's children), so a new beat
## is listed as soon as it exists.
##
## The beats before the one picked are not played: each is asked to leave
## things as it would have (NightBeat.skipped). Few do more than nothing, so
## what earlier beats would have set up may be missing; night 0's are done
## properly (set down in the lane, sent to the inn, given the room).

signal picked(index: int, beat: StringName)

@export var chapters: ChapterList

var _rows: Array[Control] = []


func _init() -> void:
	super()
	page_width = 480.0


func build() -> void:
	_list_chapters()


func refresh() -> void:
	_list_chapters()


func _clear(title: String) -> void:
	heading.text = title
	for r in _rows:
		r.queue_free()
	_rows.clear()


func _row(label: String, on_press: Callable, font_size := 13.0) -> void:
	var b := add_button(label, on_press)
	b.add_theme_font_size_override(&"font_size", px(font_size))
	_rows.append(b)


func _list_chapters() -> void:
	_clear("Test a scene")
	for i in chapters.chapters.size():
		var c := chapters.chapters[i]
		var index := i
		_row("%s: %s" % [c.heading.capitalize(), c.title], func() -> void: _list_beats(index), 15.0)
	_row("Back", func() -> void: back.emit(), 15.0)
	focus_first.call_deferred()


func _list_beats(index: int) -> void:
	var c := chapters.chapters[index]
	_clear(c.title)
	# Two columns: a night has up to seventeen beats.
	var grid := GridContainer.new()
	grid.columns = 2
	grid.add_theme_constant_override(&"h_separation", px(14.0))
	grid.add_theme_constant_override(&"v_separation", px(2.0))
	column.add_child(grid)
	_rows.append(grid)
	for beat: Array in beats_of(c.scene):
		var beat_name: StringName = beat[0]
		var label := String(beat_name) if String(beat[1]).is_empty() else "%s  ·  %s" % [beat_name, beat[1]]
		var b := Manuscript.button(label, px(11.0))
		b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		b.clip_text = true
		b.custom_minimum_size.x = px(215.0)
		b.tooltip_text = label
		b.pressed.connect(func() -> void: picked.emit(index, beat_name))
		grid.add_child(b)
	_row("Chapters", _list_chapters, 14.0)
	focus_first.call_deferred()


## A chapter's beats in order, each [name, duty], read from its scene file
## without making the scene.
static func beats_of(scene_path: String) -> Array:
	var out := []
	var packed := load(scene_path) as PackedScene
	if packed == null:
		return out
	var state := packed.get_state()
	for n in state.get_node_count():
		if String(state.get_node_path(n, true)).trim_prefix("./") != "Director":
			continue
		var duty := ""
		for p in state.get_node_property_count(n):
			if state.get_node_property_name(n, p) == &"duty":
				duty = String(state.get_node_property_value(n, p))
		out.append([state.get_node_name(n), duty])
	return out
