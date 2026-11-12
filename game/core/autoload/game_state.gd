extends Node
## Autoload GameState: the chapter and night, its phase and clock, the hidden
## Dose and Suspicion values, story flags, everything the porter carries from
## night to night, and the saves.
##
## Dose (0-100) never steps: add_dose() eases each change in over a few
## seconds and decay runs continuously, so the look, the demon and the audio
## that follow it only ever drift (Look and Feel, "Godot 4 render setup").
## snap_dose() is for loading a save behind a fade and for tooling only.
##
## Suspicion rises fast and falls slowly: raise_suspicion() ignores
## decreases, and only lower_suspicion() takes any off (a clean night,
## docs/systems/mechanics.md). Captures only go up: loading a save never undoes one.
##
## Saves (docs/log/full-game-run.md, "Saves" and "Quiet saves"): one slot at every
## bell, which Continue loads, and a quiet save just before every designed
## chase and set piece, which only death goes back to. A bell clears the quiet
## save, so death always goes back to whichever came last. Each is a snapshot()
## of this state.
##
## Carry-over: everything here goes on into the next night except the flags in
## NIGHT_FLAGS, which begin_chapter() clears (Dose halves over the day's
## sleep, in the dawn beat).

signal dose_changed(dose: float)
signal suspicion_changed(suspicion: int)
signal phase_changed(phase: Phase)
signal flag_changed(flag: StringName, value: Variant)
signal bell_saved(bell: StringName)
signal loaded
## The rite was fed a soul (docs/log/full-game-run.md, "The rite").
signal fed(id: StringName)
## The porter wrote a note in his ledger.
signal noted(id: StringName)

## The night's parts (design doc, "Core loop: one night"). In the night's
## order: DUSK, SUPPER, GATE, KNOCKS, MATINS, ROUND, SMALL_HOURS, DAWN. (DUSK
## and SMALL_HOURS come last in the list so saved values keep their meaning.)
enum Phase { SUPPER, GATE, KNOCKS, MATINS, ROUND, DAWN, DUSK, SMALL_HOURS }

const DOSE_MAX := 100.0
## Dose lost per in-game hour (design doc: "about 10").
const DOSE_DECAY_PER_HOUR := 10.0
## Default time, in s, a dose takes to ease in. Each source passes its own.
const DOSE_EASE_TIME := 5.0
const DRINK_MAX := 5.0
const DRINK_LOST_PER_HOUR := 1.0
## The porter's keys at the start of the game (design doc, "Tools": the
## gate, the guesthouse and the charnel house).
const START_KEYS: Array[StringName] = [&"gate", &"guesthouse", &"charnel"]
## Flags that last one night only; begin_chapter() clears them.
const NIGHT_FLAGS: Array[StringName] = [&"night_started", &"gate_taken", &"gate_barred", &"matins_late",
	&"hungry", &"woke_in_infirmary", &"jump_scare"]

## Where the bell save lives (tests point it elsewhere). The quiet save sits
## beside it (quiet_path()).
var save_path := "user://bell_save.tres"
## Index in the chapter list (GameFlow), or -1 for a level played on its own.
var chapter := -1
var night := 3
## This night follows the last one in a playthrough (New Game, Continue), so
## the night's director doesn't set up the state a night played on its own
## starts with (NightDirector.start_dose and start_flags).
var carried := false
var phase := Phase.DUSK
## In-game clock, hours since midnight of the day the night starts (18.5 =
## 18:30; the small hours run on past 24, so 30.0 is 06:00 next morning).
var hour := 0.0
## Real seconds per in-game hour; 0 stops the clock and the dose decay. Set
## by the night's clock (NightClock).
var seconds_per_hour := 0.0
var suspicion := 0
## Decay stops here (design doc, nights 1-3: the Matins incense keeps
## everyone at Dose 50 or more, so no one sees a mask clearly). Set by the night.
var dose_floor := 0.0
## Times the porter has been caught (only the first, on night 1 or 2, is
## not death: docs/systems/mechanics.md, "Captures").
var captures := 0
## Keys the porter holds. Doors name the key that locks them.
var keys: Array[StringName] = START_KEYS.duplicate()
var flags: Dictionary = {}
## The porter's ledger: who came in, in order. Each entry is
## {"name": String, "description": String, "night": int}.
var ledger: Array[Dictionary] = []
## The ledger's second page, in his own hand: {"text": String, "night": int}.
var notes: Array[Dictionary] = []
## What he carries in his satchel besides the keys (item ids, Items).
var satchel: Array[StringName] = []
## What each person thinks of him, -100 to 100 (docs/systems/mechanics.md, "Trust").
var trust: Dictionary = {}
## Ales drunk tonight (docs/systems/mechanics.md, "Drinking": +1 an ale, to 5; he
## loses 1 an hour; sleep clears it). Drink blurs his sight, like Dose.
var drink := 0.0
## Souls the rite has been fed in the six nights (docs/log/full-game-run.md,
## "The rite"): `count` of them, the ones in `souls` by name (a night played
## on its own starts with a count and no names).
var count := 0
var souls: Array[StringName] = []
## Blood and marks left in the abbey, until the cult cleans them
## (BloodMarks): {"kind", "xform", "night", "proves_men", "id"}.
var marks: Array[Dictionary] = []
## The bell (or quiet save) the state in memory was saved at, or empty
## before the first one. The night picks up there after a load.
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
	if drink > 0.0:
		drink = maxf(drink - DRINK_LOST_PER_HOUR * hours, 0.0)
	if _dose > dose_floor:
		_set_dose(maxf(_dose - DOSE_DECAY_PER_HOUR * hours, dose_floor))


## Everything back to the start of the game (New Game).
## For testing (SceneSelect, debug builds): the beat the next night loaded
## starts at, by its node's name. The director clears it. Never saved.
var start_beat := &""


func new_game() -> void:
	chapter = -1
	night = 0
	carried = false
	phase = Phase.DUSK
	hour = 0.0
	seconds_per_hour = 0.0
	suspicion = 0
	dose_floor = 0.0
	captures = 0
	keys = START_KEYS.duplicate()
	flags = {}
	ledger = []
	notes = []
	satchel = []
	trust = {}
	count = 0
	drink = 0.0
	souls = []
	marks = []
	last_bell = &""
	snap_dose(0.0)
	clear_quiet_save()


## A new chapter begins: the night's own flags are cleared and it starts
## from its beginning. Everything else carries over.
func begin_chapter(index: int, night_number: int) -> void:
	chapter = index
	night = night_number
	phase = Phase.DUSK
	hour = 0.0
	seconds_per_hour = 0.0
	dose_floor = 0.0
	last_bell = &""
	for f in NIGHT_FLAGS:
		flags.erase(f)
	clear_quiet_save()


## Eases `amount` of Dose in over `seconds` (negative amounts ease out).
## Overlapping calls add up.
func add_dose(amount: float, seconds := DOSE_EASE_TIME) -> void:
	var applied := [0.0]
	var step := func(v: float) -> void:
		_set_dose(_dose + v - applied[0])
		applied[0] = v
	var tween := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tween.tween_method(step, 0.0, amount, maxf(seconds, 0.01))


## Takes in `amount` of Dose now: for sources that come a breath at a
## time (the incense, frame by frame), which are already smooth.
func breathe_in(amount: float) -> void:
	_set_dose(_dose + amount)


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


## Takes Suspicion off (only a clean night does: docs/systems/mechanics.md).
func lower_suspicion(amount: int) -> void:
	var next := maxi(suspicion - maxi(amount, 0), 0)
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


## A flag for tonight: n<night>_<name> (night 3's bread is n3_ate_bread).
func tonight(name_: String) -> StringName:
	return StringName("n%d_%s" % [night, name_])


## What `who` thinks of the porter, -100 to 100 (People.START_TRUST to begin).
func trust_of(who: StringName) -> int:
	return int(trust.get(who, People.START_TRUST.get(who, 0)))


func change_trust(who: StringName, amount: int) -> void:
	trust[who] = clampi(trust_of(who) + amount, -100, 100)


## An ale: +1 drink, to 5.
func have_a_drink() -> void:
	drink = minf(drink + 1.0, DRINK_MAX)
	set_flag(&"drank", int(get_flag(&"drank", 0)) + 1)


## Eats clean food: hunger ends for the night, no Dose (docs/systems/mechanics.md,
## "The drug, and food").
func eat_clean() -> void:
	set_flag(&"hungry", false)
	set_flag(tonight("ate_clean"))


## The cult tears a guest's page from the ledger: his entries are gone.
func tear_ledger(guest: String) -> void:
	ledger.assign(ledger.filter(func(e: Dictionary) -> bool: return e.get("name", "") != guest))
	set_flag(tonight("ledger_torn"))


## Writes a guest into the ledger.
func write_ledger(guest: String, description: String) -> void:
	ledger.append({"name": guest, "description": description, "night": night})


## The porter writes a note on the ledger's second page, in his own hand
## (docs/systems/mechanics.md, "The ledger's notes"), once per `id`. A note whose id
## is in Clues counts toward what the prior needs on night 5. `text` empty:
## the clue's own text.
func note(id: StringName, text := "") -> bool:
	for n in notes:
		if n.get("id") == id:
			return false
	if text.is_empty():
		text = Clues.text(id)
	notes.append({"id": id, "text": text, "night": night})
	noted.emit(id)
	return true


func has_note(id: StringName) -> bool:
	return notes.any(func(n: Dictionary) -> bool: return n.get("id") == id)


## Feeds the rite the soul `id`, once: a candle lights in the crypt.
func feed_rite(id: StringName) -> void:
	if souls.has(id):
		return
	souls.append(id)
	count += 1
	set_flag(StringName("fed_" + String(id)))
	fed.emit(id)


## Skipped the bread (design doc, "Sources"): a shorter breath, slower
## sprint recovery, a hand tremor on the lantern.
func is_hungry() -> bool:
	return get_flag(&"hungry", false) == true


## Everything a save keeps.
func snapshot() -> Dictionary:
	return {
		"chapter": chapter, "night": night, "phase": phase, "hour": hour, "dose": _dose,
		"dose_floor": dose_floor, "suspicion": suspicion, "captures": captures,
		"keys": keys.duplicate(), "flags": flags.duplicate(true), "ledger": ledger.duplicate(true),
		"notes": notes.duplicate(true), "satchel": satchel.duplicate(), "trust": trust.duplicate(),
		"count": count, "souls": souls.duplicate(), "marks": marks.duplicate(true), "drink": drink,
	}


## Puts back a snapshot(). Captures never go down.
func restore(state: Dictionary) -> void:
	chapter = int(state.get("chapter", -1))
	night = int(state.get("night", night))
	hour = float(state.get("hour", 0.0))
	dose_floor = float(state.get("dose_floor", 0.0))
	captures = maxi(captures, int(state.get("captures", 0)))
	keys.assign(state.get("keys", START_KEYS))
	flags = (state.get("flags", {}) as Dictionary).duplicate(true)
	ledger.assign((state.get("ledger", []) as Array).duplicate(true))
	notes.assign((state.get("notes", []) as Array).duplicate(true))
	satchel.assign(state.get("satchel", []))
	trust = (state.get("trust", {}) as Dictionary).duplicate()
	count = int(state.get("count", 0))
	drink = float(state.get("drink", 0.0))
	souls.assign(state.get("souls", []))
	marks.assign((state.get("marks", []) as Array).duplicate(true))
	suspicion = int(state.get("suspicion", 0))
	suspicion_changed.emit(suspicion)
	phase = int(state.get("phase", Phase.DUSK)) as Phase
	phase_changed.emit(phase)
	snap_dose(float(state.get("dose", 0.0)))


## Saves the night at a bell (the one slot Continue loads), and clears the
## quiet save. Returns false if the write failed.
func ring_bell(bell: StringName) -> bool:
	if not _write(save_path, bell):
		return false
	clear_quiet_save()
	last_bell = bell
	bell_saved.emit(bell)
	return true


## Saves quietly just before a designed chase or set piece: death comes back
## here, Continue doesn't.
func quiet_save(point: StringName) -> bool:
	return _write(quiet_path(), point)


func quiet_path() -> String:
	return save_path.get_basename() + "_quiet.tres"


func has_bell_save() -> bool:
	return ResourceLoader.exists(save_path)


func has_quiet_save() -> bool:
	return ResourceLoader.exists(quiet_path())


func clear_quiet_save() -> void:
	if has_quiet_save():
		DirAccess.remove_absolute(ProjectSettings.globalize_path(quiet_path()))


## The chapter the bell save is in, or -1 if there is none.
func saved_chapter() -> int:
	var save := _read(save_path)
	return int(save.state.get("chapter", -1)) if save else -1


## Restores the state saved at the last bell (Continue). False if none.
func load_last_bell() -> bool:
	return _load(save_path)


## Restores the latest save, quiet or bell (death). False if none.
func load_resume() -> bool:
	return _load(quiet_path()) if has_quiet_save() else _load(save_path)


func _write(path: String, point: StringName) -> bool:
	var save := SaveGame.new()
	save.bell = point
	save.state = snapshot()
	if ResourceSaver.save(save, path) != OK:
		push_error("GameState: could not write %s" % path)
		return false
	return true


func _read(path: String) -> SaveGame:
	if not ResourceLoader.exists(path):
		return null
	var save := ResourceLoader.load(path, "", ResourceLoader.CACHE_MODE_IGNORE) as SaveGame
	if save == null:
		push_error("GameState: %s is not a SaveGame" % path)
	return save


func _load(path: String) -> bool:
	var save := _read(path)
	if save == null:
		return false
	restore(save.state)
	last_bell = save.bell
	loaded.emit()
	return true


func _set_dose(value: float) -> void:
	value = clampf(value, 0.0, DOSE_MAX)
	if value != _dose:
		_dose = value
		dose_changed.emit(_dose)
