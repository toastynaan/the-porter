class_name TitleMenu
extends MenuPage
## The title screen (the run's spec, "Menus"): New Game, Continue (with a
## bell save), Chapters (once the game is finished), How to Play, Settings,
## Quit. In debug builds, also Test a scene (SceneSelect).

signal chosen(what: StringName)

var _continue: Button
var _chapters: Button


func build() -> void:
	heading.text = "The Porter"
	heading.add_theme_font_size_override(&"font_size", px(46.0))
	var sub := add_text("[center][i]London, within the walls, 1424[/i][/center]", 13.0)
	sub.add_theme_color_override(&"default_color", Manuscript.FADED_INK)
	_continue = add_button("Continue", func() -> void: chosen.emit(&"continue"))
	add_button("New Game", func() -> void: chosen.emit(&"new_game"))
	_chapters = add_button("Chapters", func() -> void: chosen.emit(&"chapters"))
	if OS.is_debug_build():
		add_button("Test a scene", func() -> void: chosen.emit(&"test"))
	add_button("How to Play", func() -> void: chosen.emit(&"how_to_play"))
	add_button("Settings", func() -> void: chosen.emit(&"settings"))
	add_button("Quit", func() -> void: chosen.emit(&"quit"))


func refresh() -> void:
	_continue.visible = GameState.has_bell_save() and GameState.saved_chapter() >= 0
	_chapters.visible = Settings.finished


func _unhandled_input(_event: InputEvent) -> void:
	# The title has nowhere to go back to.
	pass
