class_name PauseMenu
extends MenuPage
## The pause menu (docs/systems/mechanics.md, "Controls": Esc or Start opens it and
## frees the mouse): Resume, Settings, How to Play, Quit to the title.

signal chosen(what: StringName)


func build() -> void:
	heading.text = "Paused"
	add_button("Resume", func() -> void: chosen.emit(&"resume"))
	add_button("Settings", func() -> void: chosen.emit(&"settings"))
	add_button("How to Play", func() -> void: chosen.emit(&"how_to_play"))
	add_button("Quit to the Title", func() -> void: chosen.emit(&"quit_to_title"))
