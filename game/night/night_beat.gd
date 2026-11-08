class_name NightBeat
extends Node
## One beat of a night (design doc, "Night-by-night script"). The director
## sets the beat's `phase` and awaits run(). A beat with a `bell` is where the
## night picks up again after a death or a Continue sends it back to that
## save; with `quiet` the director saves quietly there as the beat starts.

@export var phase := GameState.Phase.SUPPER
@export var bell := &""
## Saves quietly as the beat starts (before a designed chase or set piece).
@export var quiet := false
## Lateness counts for this duty from `due` until arrived() (docs/mechanics.md,
## "Lateness"): 15 minutes late is noticed, 45 brings someone to fetch him.
@export var watch_late := false
## Who comes to fetch him: "prior", or "cole" (at dusk).
@export var fetcher := &"prior"

## The porter has come to this duty (lateness stops counting).
var is_arrived := false


func arrived() -> void:
	is_arrived = true
## The duty as the porter's ledger lists it (empty: not a duty, an event).
@export var duty := ""
## When it is due by the candle clock, in hours (-1: no set time).
@export var due := -1.0
## The porter may doze on the gate bench while this beat waits.
@export var can_doze := false


## Does the beat; returns when it is over. Beats override this.
func run() -> void:
	await get_tree().process_frame


func player() -> Player:
	return get_tree().get_first_node_in_group(&"player") as Player


func clock() -> NightClock:
	return get_tree().get_first_node_in_group(&"night_clock") as NightClock


func say(speaker: String, text: String) -> void:
	await Talk.say(speaker, text)


## Fades the screen if the game's capture flow (and its fade) is there.
func fade_to(alpha: float, seconds: float) -> void:
	var flow := get_tree().get_first_node_in_group(&"capture_flow") as CaptureFlow
	if flow:
		await flow.fade.fade_to(alpha, seconds)


## Lies down and sleeps through the day: the screen goes dark, the clock
## stops, and of the night's Dose only `keeps` is left (docs/full-game-run.md,
## "Six nights": Dose halved by a day's sleep); the cult scrubs the marks that
## prove men did it. Sets night<N>_done.
func sleep_through_the_day(keeps: float, line: String) -> void:
	var p := player()
	p.controls_locked = true
	await fade_to(1.0, 2.0)
	GameState.seconds_per_hour = 0.0
	GameState.dose_floor = 0.0
	GameState.snap_dose(GameState.dose * keeps)
	# While he sleeps the cult scrubs what would prove men did it.
	BloodMarks.clean_at_dawn(get_tree())
	Lateness.clean_night()
	GameState.set_flag(StringName("night%d_done" % GameState.night))
	if not line.is_empty():
		await say("", line)


func until(condition: Callable) -> void:
	while not condition.call():
		await get_tree().physics_frame


func wait(seconds: float) -> void:
	await get_tree().create_timer(seconds, false, true).timeout


## The Marker3D children of `holder`, as positions.
func points(holder: Node) -> Array[Vector3]:
	var out: Array[Vector3] = []
	for c in holder.get_children():
		if c is Marker3D:
			out.append((c as Marker3D).global_position)
	return out
