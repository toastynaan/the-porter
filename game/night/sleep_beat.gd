extends NightBeat
## Going to sleep at dawn (design doc, "Core loop" 7: Cole takes the gate
## and you go to your cell to sleep). Lie down on the cot and sleep through
## the day: Dose falls over the day but not to zero (`sleep_keeps`), and the
## night is over.

@export var sleep: Duty
@export var lines := PackedStringArray(["(Go to your cell and sleep.)"])
@export var asleep_line := "(You sleep through the day.)"
## Of the night's Dose, the part still in him when he wakes.
@export var sleep_keeps := 0.5


func run() -> void:
	for line in lines:
		await say("", line)
	await sleep.wait_for_use()
	await sleep_through_the_day(sleep_keeps, asleep_line)
