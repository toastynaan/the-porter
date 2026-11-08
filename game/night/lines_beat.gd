extends NightBeat
## Lines at a mark on the candle (night 4: the supper hour with no supper
## bell, the refectory locked for the fast; night 5: the sergeant's lantern
## out in the lane at dawn, `only_if` he died). Waits until `due`, says
## `lines`, and sets `flag` (tonight's) if given.

@export var lines := PackedStringArray()
@export var flag := &""
## Said only if this flag is set (empty: always).
@export var only_if := &""


func run() -> void:
	if only_if != &"" and not GameState.has_flag(only_if):
		return
	if due >= 0.0:
		await clock().wait_until(due)
	await say_lines(lines)
	if flag != &"":
		GameState.set_flag(GameState.tonight(String(flag)))
