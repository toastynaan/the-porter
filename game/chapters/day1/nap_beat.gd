extends NightBeat
## The nap (docs/systems/mechanics.md, "The tour"): his shift is at night, so they
## send him to sleep in his cell. Lying on the cot fades to dusk, and night 1
## begins with its wake.

@export var cot: Duty


func run() -> void:
	await say("", "(Your cell. The cot. Your watch begins at dusk.)")
	await cot.wait_for_use()
	await sleep_through_the_day(1.0, "(You sleep, and wake to the light failing.)")
