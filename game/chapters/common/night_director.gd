class_name NightDirector
extends Node
## Runs one night: its NightBeat children, in order (design doc, "Core loop:
## one night"). After a death or a Continue the night starts again at the
## beat whose `bell` the save was made at. A beat marked `quiet` saves
## quietly as it starts (docs/systems/mechanics.md, "Quiet saves": just before every
## designed chase and set piece). `beats_run` records what ran, for tests.
##
## A night played on its own (the slice, tests, chapter select) starts as if
## the nights before it had happened: the start_ exports set that up. A
## night that follows the last one in a playthrough (GameState.carried)
## starts with what the porter brought from it.

signal beat_started(beat: StringName)
signal finished

@export var night := 3
## Dose when the night starts fresh: what the nights before left after a
## day's sleep.
@export var start_dose := 0.0
## Flags the nights before would have set (night 3: warned about the bread).
@export var start_flags: Array[StringName] = []
@export var start_suspicion := 0
## The rite's count the nights before would have reached.
@export var start_count := 0
## He has the porter's lantern from the start of this chapter. Off on night 0
## (he comes to London without one) and day 1 (Anselm gives it to him on the
## tour); once given, the flag has_lantern keeps it his.
@export var porter_lantern := true

var beats_run: Array[StringName] = []
var current: NightBeat
## The night was brought to an end early (night 6: an ending).
var ended := false


func _ready() -> void:
	add_to_group(&"night_director")
	run.call_deferred()


## Tonight's duties for the ledger: [text, done], in order, each with the
## time it is due if it has one.
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
			var text := beat.duty
			if beat.due >= 0.0:
				text = "%s  %s" % [NightClock.clock_text(beat.due), text]
			out.append([text, done])
	return out


func run() -> void:
	# Replaced before it began (a reload in the same frame).
	if not is_inside_tree():
		return
	GameState.night = night
	if not GameState.has_flag(&"night_started"):
		GameState.set_flag(&"night_started")
		if not GameState.carried:
			GameState.snap_dose(start_dose)
			GameState.suspicion = start_suspicion
			GameState.count = start_count
			for f in start_flags:
				GameState.set_flag(f)
		# What Thomas was told since the last dusk has reached the cult.
		Report.at_dusk()
	if porter_lantern:
		GameState.set_flag(&"has_lantern")
	var p := get_tree().get_first_node_in_group(&"player") as Player
	if p:
		p.lantern_hand.owned = GameState.has_flag(&"has_lantern")
	var beats: Array[NightBeat] = []
	for c in get_children():
		if c is NightBeat:
			beats.append(c)
	var from := 0
	if not GameState.last_bell.is_empty():
		for i in beats.size():
			if beats[i].bell == GameState.last_bell:
				from = i
	if not GameState.start_beat.is_empty():
		# For testing: start at that beat, the ones before it skipped.
		for i in beats.size():
			if beats[i].name == GameState.start_beat:
				from = i
		GameState.start_beat = &""
		for i in from:
			beats_run.append(beats[i].name)
			if beats[i].due >= 0.0:
				GameState.hour = maxf(GameState.hour, beats[i].due)
			beats[i].skipped()
	var clock := get_tree().get_first_node_in_group(&"night_clock") as NightClock
	for i in range(from, beats.size()):
		current = beats[i]
		if clock:
			clock.cap = _next_due(beats, i)
		GameState.set_phase(current.phase)
		if current.quiet and not current.bell.is_empty():
			GameState.quiet_save(current.bell)
		if current.watch_late and current.due >= 0.0:
			Lateness.watch.call(current, self)
		beats_run.append(current.name)
		beat_started.emit(current.name)
		await current.run()
		if ended or not is_inside_tree():
			return
	current = null
	ended = true
	finished.emit()


## Ends the night now, whatever beat is running (night 6: an ending).
func end_night() -> void:
	if ended:
		return
	ended = true
	current = null
	finished.emit()


## The earliest mark of the beats after `i` (INF if none has one).
func _next_due(beats: Array[NightBeat], i: int) -> float:
	var due := INF
	for k in range(i + 1, beats.size()):
		if beats[k].due >= 0.0:
			due = minf(due, beats[k].due)
	return due
