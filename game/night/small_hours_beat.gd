extends NightBeat
## The small hours (design doc, "Core loop" 6: with the round done, you go
## back to the gate and wait. You can doze until dawn, but each night's main
## event interrupts the wait). On night 3 the main event was the crypt and
## the chase, so the wait is quiet. The Lauds bell rings at the candle's
## mark and wakes him.

@export var bench: GateBench
@export var tower: BellTower
@export var gate_lamp: Candle


func run() -> void:
	gate_lamp.lit = true
	var way := Wayfinding.show_way(self, bench.global_position)
	await say("", "(Back to the gate. Keep watch until Lauds; you can doze on the bench.)")
	await clock().wait_until(due)
	Wayfinding.put_out(way)
	gate_lamp.lit = false
	clock().wake()
	tower.ring(3)
	await say("", "(The bell for Lauds. Grey light.)")
