class_name SaveGame
extends Resource
## What GameState writes at each bell: enough to restart the night from that
## bell. Saved as a .tres in user:// (design doc, "Systems to build in Godot").

@export var bell: StringName
@export var night := 3
@export var phase := 0
@export var hour := 0.0
@export var dose := 0.0
@export var suspicion := 0
@export var captures := 0
@export var keys: Array[StringName] = []
@export var flags: Dictionary = {}
