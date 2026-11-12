extends NightBeat
## Waking at dusk (design doc, "Core loop" 0: the porter sleeps through the
## day while Cole keeps the gate, and wakes in his cell in the late
## afternoon. The gate still stands open, so for a few minutes of failing
## light you can look around, talk to the brothers, or step out into the
## lane, before the supper bell). The bell rings at the candle's supper mark.

@export var wake_at: Marker3D
## Night 6: in the infirmary in Thomas's care, unless the prior believed him
## (`alt_if`): then here, his cell, with `alt_lines`.
@export var alt_at: Marker3D
@export var alt_if := &""
@export var alt_lines := PackedStringArray()
@export var tower: BellTower
@export var gate: AbbeyGate
## What the porter notices as he wakes (the night's own lines).
@export var lines := PackedStringArray(["(You wake in your cell. The light is failing.)",
	"(Cole has the gate open. You have until the supper bell.)"])
## Rings the supper bell at `due` (off: the night has no supper).
@export var supper_bell := true


func _ready() -> void:
	if not GameState.has_flag(&"gate_taken"):
		gate.stand_open()


func run() -> void:
	var p := player()
	p.controls_locked = true
	await fade_to(1.0, 0.0)
	var alt := alt_at != null and alt_if != &"" and GameState.has_flag(alt_if)
	var at := alt_at if alt else wake_at
	p.place(at.global_position, at.global_rotation.y)
	await fade_to(0.0, 2.5)
	p.controls_locked = false
	await say_lines(alt_lines if alt else lines)
	if due >= 0.0:
		await clock().wait_until(due)
	if supper_bell:
		tower.ring(3)
		await say("", "(The supper bell.)")
