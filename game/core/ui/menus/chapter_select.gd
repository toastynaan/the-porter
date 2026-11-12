class_name ChapterSelect
extends MenuPage
## Chapter select, once the game is finished (docs/systems/mechanics.md, "Settings
## and accessibility"): start any night, with the state a typical
## playthrough would have reached by then (each night's own start state).

signal picked(index: int)

@export var chapters: ChapterList


func build() -> void:
	heading.text = "Chapters"
	for i in chapters.chapters.size():
		var c := chapters.chapters[i]
		var index := i
		add_button("%s: %s" % [c.heading.capitalize(), c.title], func() -> void: picked.emit(index))
	add_button("Back", func() -> void: back.emit())
