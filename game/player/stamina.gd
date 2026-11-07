class_name Stamina
extends Node
## How long the porter can run (M2 report defaults): 25 s from full to empty,
## 15 s to refill when not running, half as fast again when hungry (Look and
## Feel, "Hunger": slower to get back to full sprint). Run it dry and he can't
## run again until it is back to RECOVERED. Nothing shows it but his breathing.

const RUN_TIME := 25.0
const REFILL_TIME := 15.0
## Refill time multiplier when hungry (50% slower).
const HUNGRY_FACTOR := 1.5
## Fraction it must refill to before he can run again once empty.
const RECOVERED := 0.3

## Tests and tools: running never tires.
@export var tireless := false

## 0..1.
var value := 1.0
var exhausted := false


func can_run() -> bool:
	return tireless or not exhausted


func update(running: bool, delta: float) -> void:
	if tireless:
		value = 1.0
		return
	if running:
		value = maxf(value - delta / RUN_TIME, 0.0)
		if value == 0.0:
			exhausted = true
	else:
		var refill := REFILL_TIME * (HUNGRY_FACTOR if GameState.is_hungry() else 1.0)
		value = minf(value + delta / refill, 1.0)
		if exhausted and value >= RECOVERED:
			exhausted = false
