class_name ChapterList
extends Resource
## The chapters in order (game/flow/chapters.tres): New Game plays them from
## the first; chapter select, once the game is finished, starts any of them.

@export var chapters: Array[Chapter] = []


func index_of(id: StringName) -> int:
	for i in chapters.size():
		if chapters[i].id == id:
			return i
	return -1
