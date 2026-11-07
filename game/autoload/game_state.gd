extends Node
## Autoload GameState: the night, its phase and clock, the hidden Dose and
## Suspicion values, story flags, and the bell saves.
##
## Dose (0-100) never steps: add_dose() eases each change in over a few
## seconds and decay runs continuously, so the look, the demon and the audio
## that follow it only ever drift (Look and Feel, "Godot 4 render setup").
## snap_dose() is for loading a save behind a fade and for tooling only.
##
## Suspicion only goes up (design doc, "Suspicion, chases and hiding").
## Captures only go up too: loading a bell never undoes one, so the second
## capture kills you even after a restart.

signal dose_changed(dose: float)
signal suspicion_changed(suspicion: int)
signal phase_changed(phase: Phase)
signal flag_changed(flag: StringName, value: Variant)
signal bell_saved(bell: StringName)
signal loaded

## The night's duties in order (design doc, "Core loop: one night").
enum Phase { SUPPER, GATE, KNOCKS, MATINS, ROUND, DAWN }

const DOSE_MAX := 100.0
## Dose lost per in-game hour (design doc: "about 10").
const DOSE_DECAY_PER_HOUR := 10.0
## Default time, in s, a dose takes to ease in. Each source passes its own.
const DOSE_EASE_TIME := 5.0

## Where the bell save lives (tests point it elsewhere).
var save_path := "user://bell_save.tres"
var night := 3
var phase := Phase.SUPPER
## In-game clock, hours since midnight of the night's start (18.5 = 18:30).
var hour := 0.0
## Real seconds per in-game hour; 0 stops the clock and the dose decay. The
## night's time scale isn't designed yet (M4).
var seconds_per_hour := 0.0
var suspicion := 0
## Decay stops here (design doc, nights 1-3: the Matins incense keeps
## everyone at Dose 50 or more, so no one sees a mask clearly). Set by the night.
var dose_floor := 0.0
## Times the player has been caught (the first wakes them, the second kills).
var captures := 0
## Keys the porter holds (design doc, "Tools": the gate, the guesthouse and
## the charnel house). Doors name the key that locks them.
var keys: Array[StringName] = [&"gate", &"guesthouse", &"charnel"]
var flags: Dictionary = {}
## The porter's ledger: who came in, in order. Each entry is
## {"name": String, "description": String, "night": int}.
var ledger: Array[Dictionary] = []
## The bell the night restarts from, or empty before the first one.
var last_bell := &""

var dose: float:
	get:
		return _dose

var _dose := 0.0


func _process(delta: float) -> void:
	if seconds_per_hour <= 0.0:
		return
	var hours := delta / seconds_per_hour
	hour += hours
	if _dose > dose_floor:
		_set_dose(maxf(_dose - DOSE_DECAY_PER_HOUR * hours, dose_floor))


## Eases `amount` of Dose in over `seconds` (negative amounts ease out).
## Overlapping calls add up.
func add_dose(amount: float, seconds := DOSE_EASE_TIME) -> void:
	var applied := [0.0]
	var step := func(v: float) -> void:
		_set_dose(_dose + v - applied[0])
		applied[0] = v
	var tween := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tween.tween_method(step, 0.0, amount, maxf(seconds, 0.01))


## Sets Dose at once. Only for loading behind a fade, tests and tools.
func snap_dose(value: float) -> void:
	_set_dose(value)


func raise_suspicion(amount: int) -> void:
	if amount <= 0:
		return
	var next := mini(suspicion + amount, 100)
	if next != suspicion:
		suspicion = next
		suspicion_changed.emit(suspicion)


func set_phase(p: Phase) -> void:
	if p != phase:
		phase = p
		phase_changed.emit(phase)


func set_flag(flag: StringName, value: Variant = true) -> void:
	if flags.get(flag) != value:
		flags[flag] = value
		flag_changed.emit(flag, value)


func get_flag(flag: StringName, default: Variant = null) -> Variant:
	return flags.get(flag, default)


func has_flag(flag: StringName) -> bool:
	return flags.has(flag)


## Writes a guest into the ledger.
func write_ledger(guest: String, description: String) -> void:
	ledger.append({"name": guest, "description": description, "night": night})


## Skipped the bread (design doc, "Sources"): a shorter breath, slower
## sprint recovery, a hand tremor on the lantern.
func is_hungry() -> bool:
	return get_flag(&"hungry", false) == true


## Saves the night at a bell. Returns false if the write failed.
func ring_bell(bell: StringName) -> bool:
	var save := SaveGame.new()
	save.bell = bell
	save.night = night
	save.phase = phase
	save.hour = hour
	save.dose = _dose
	save.suspicion = suspicion
	save.captures = captures
	save.keys = keys.duplicate()
	save.ledger = ledger.duplicate(true)
	save.flags = flags.duplicate(true)
	if ResourceSaver.save(save, save_path) != OK:
		push_error("GameState: could not write %s" % save_path)
		return false
	last_bell = bell
	bell_saved.emit(bell)
	return true


func has_bell_save() -> bool:
	return ResourceLoader.exists(save_path)


## Restores the state saved at the last bell. Returns false if there is none.
func load_last_bell() -> bool:
	if not has_bell_save():
		return false
	var save := ResourceLoader.load(save_path, "", ResourceLoader.CACHE_MODE_IGNORE) as SaveGame
	if save == null:
		push_error("GameState: %s is not a SaveGame" % save_path)
		return false
	night = save.night
	hour = save.hour
	captures = maxi(captures, save.captures)
	keys = save.keys.duplicate()
	ledger = save.ledger.duplicate(true)
	flags = save.flags.duplicate(true)
	last_bell = save.bell
	suspicion = save.suspicion
	suspicion_changed.emit(suspicion)
	phase = save.phase as Phase
	phase_changed.emit(phase)
	snap_dose(save.dose)
	loaded.emit()
	return true


func _set_dose(value: float) -> void:
	value = clampf(value, 0.0, DOSE_MAX)
	if value != _dose:
		_dose = value
		dose_changed.emit(_dose)
