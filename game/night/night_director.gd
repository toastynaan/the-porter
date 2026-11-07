class_name NightDirector
extends Node
## Runs one night: its NightBeat children, in order (design doc, "Core loop:
## one night"). After a death the night starts again at the beat whose
## `bell` was the last one rung. `beats_run` records what ran, for tests.

signal beat_started(beat: StringName)
signal finished

@export var night := 3

var beats_run: Array[StringName] = []
var current: NightBeat


func _ready() -> void:
	add_to_group(&"night_director")
	run.call_deferred()


## Tonight's duties for the ledger: [text, done], in order.
func duties() -> Array:
	var out := []
	var done := true
	for c in get_children():
		var beat := c as NightBeat
		if beat == null:
			continue
		if beat == current:
			done = false
		if not beat.duty.is_empty():
			out.append([beat.duty, done])
	return out


func run() -> void:
	GameState.night = night
	var beats: Array[NightBeat] = []
	for c in get_children():
		if c is NightBeat:
			beats.append(c)
	var from := 0
	if not GameState.last_bell.is_empty():
		for i in beats.size():
			if beats[i].bell == GameState.last_bell:
				from = i
	for i in range(from, beats.size()):
		current = beats[i]
		GameState.set_phase(current.phase)
		beats_run.append(current.name)
		beat_started.emit(current.name)
		await current.run()
	current = null
	finished.emit()
