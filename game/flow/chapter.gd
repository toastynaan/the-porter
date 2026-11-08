class_name Chapter
extends Resource
## One chapter of the game (docs/full-game-run.md, "Done when" 1): night 0,
## day 1, or one of the six nights, with the chronicle page its card shows.

@export var id := &""
## GameState.night while it plays (0 for night 0 and day 1).
@export var night := 0
## "The third night", in small capitals over the title.
@export var heading := ""
@export var title := ""
## The card's paragraph, in the chronicler's voice. Its first letter is the
## decorated initial.
@export_multiline var card := ""
@export_file("*.tscn") var scene := ""
