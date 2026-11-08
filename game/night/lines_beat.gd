extends NightBeat
## Lines at a mark on the candle (night 4: the supper hour with no supper
## bell, the refectory locked for the fast; night 5: the sergeant's lantern
## out in the lane at dawn, `only_if` he died). Waits until `due`, says
## `lines`, and sets `flag` (tonight's) if given.

@export var lines := PackedStringArray()
@export var flag := &""
## Said only if this flag is set (empty: always).
@export var only_if := &""
## Said only at this Dose or more (night 6: someone remarks on his eyes).
@export var min_dose := 0.0
## An hour to wait for that isn't a mark on the candle (it doesn't hold the
## clock back the way `due` does).
@export var at_hour := -1.0


func run() -> void:
	if only_if != &"" and not GameState.has_flag(only_if):
		return
	if due >= 0.0:
		await clock().wait_until(due)
	if at_hour >= 0.0:
		await clock().wait_until(at_hour)
	if GameState.dose < min_dose:
		return
	await say_lines(lines)
	if flag != &"":
		GameState.set_flag(GameState.tonight(String(flag)))
