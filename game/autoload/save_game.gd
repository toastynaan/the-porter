class_name SaveGame
extends Resource
## What GameState writes at each bell and quiet save: the point the night
## picks up from, and a snapshot of the whole state (GameState.snapshot()).
## Saved as a .tres in user:// (design doc, "Systems to build in Godot").

## The bell or quiet save it was written at (a night beat's `bell`).
@export var bell: StringName
@export var state: Dictionary = {}
