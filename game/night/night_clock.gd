class_name NightClock
extends Node
## The candle clock (design doc, "Core loop": a candle in your cell burns
## through the night; its marks are the duties). Time runs slowly in real
## time, and much faster while the porter dozes at the gate; anything that
## needs him (a knock, a duty coming due, the night's event) calls wake().
## Beats await wait_until() for their marks. The candle doesn't burn past the
## mark of a beat the night hasn't reached (`cap`, set by the director), so
## a long round can't bring on Lauds and the morning in the middle of a chase.

signal woke

## Where a fresh night starts: the porter wakes in the late afternoon.
@export var start_hour := 16.0
## Real seconds per in-game hour, awake and dozing.
@export var seconds_per_hour := 240.0
@export var doze_seconds_per_hour := 2.0

var dozing := false
## The clock stops here until the director moves it on.
var cap := INF


func _ready() -> void:
	add_to_group(&"night_clock")
	if GameState.last_bell.is_empty():
		GameState.hour = start_hour
	GameState.seconds_per_hour = seconds_per_hour


func _process(_delta: float) -> void:
	if GameState.hour > cap:
		GameState.hour = cap


## Resumes time at waking pace (tests and tools change the pace).
func set_pace(awake: float, asleep: float) -> void:
	seconds_per_hour = awake
	doze_seconds_per_hour = asleep
	GameState.seconds_per_hour = asleep if dozing else awake


func wait_until(hour: float) -> void:
	while GameState.hour < hour:
		await get_tree().process_frame


func doze() -> void:
	dozing = true
	GameState.seconds_per_hour = doze_seconds_per_hour


## Something needs the porter: stop dozing.
func wake() -> void:
	if dozing:
		dozing = false
		GameState.seconds_per_hour = seconds_per_hour
		woke.emit()


## "16:45" for an hour (wrapping past midnight).
static func clock_text(hour: float) -> String:
	var h := fposmod(hour, 24.0)
	return "%02d:%02d" % [floori(h), floori(fposmod(h, 1.0) * 60.0)]
