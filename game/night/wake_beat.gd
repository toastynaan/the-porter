extends NightBeat
## Waking at dusk (design doc, "Core loop" 0: the porter sleeps through the
## day while Cole keeps the gate, and wakes in his cell in the late
## afternoon. The gate still stands open, so for a few minutes of failing
## light you can look around, talk to the brothers, or step out into the
## lane, before the supper bell). The bell rings at the candle's supper mark.

@export var wake_at: Marker3D
@export var tower: BellTower
@export var gate: AbbeyGate


func _ready() -> void:
	if not GameState.has_flag(&"gate_taken"):
		gate.stand_open()


func run() -> void:
	var p := player()
	p.controls_locked = true
	await fade_to(1.0, 0.0)
	p.place(wake_at.global_position, wake_at.global_rotation.y)
	await fade_to(0.0, 2.5)
	p.controls_locked = false
	await say("", "(You wake in your cell. The light is failing.)")
	await say("", "(Cole has the gate open. You have until the supper bell.)")
	await clock().wait_until(due)
	tower.ring(3)
	await say("", "(The supper bell.)")
