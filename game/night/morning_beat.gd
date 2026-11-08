extends NightBeat
## Day 1's morning (design doc, "Day 1: Morning"): grey daylight. He wakes in
## his room at the top of the Cross Keys; downstairs Agnes says he'd had too
## much, if he had. Across the lane Cole has opened the abbey gate, and the
## ground by the well has been sanded over. Thomas and Anselm wait for him
## just inside.

@export var wake_at: Marker3D
@export var gate: AbbeyGate
@export var cole: VisitorNPC
@export var cole_gate: Marker3D
@export var agnes: Node3D
## Where Thomas and Anselm wait for him, inside the gate.
@export var meet: Marker3D
@export var sand: Node3D


func _ready() -> void:
	gate.stand_open()


func run() -> void:
	var p := player()
	p.controls_locked = true
	await fade_to(1.0, 0.0)
	p.place(wake_at.global_position, wake_at.global_rotation.y)
	await fade_to(0.0, 2.0)
	p.controls_locked = false
	cole.set_present(true, cole_gate.global_transform)
	if GameState.has_flag(&"hangover"):
		await say("", "(Grey light. Your head is splitting.)")
		agnes.add_to_group(&"glyph_targets")
		await say("Agnes", "(From the stair.) You had more than was good for you last night, brother. Water's in the jug.")
		agnes.remove_from_group(&"glyph_targets")
	else:
		await say("", "(Grey light through the shutter. The Keys is quiet below.)")
	await say("", "(Across the lane the abbey gate stands open.)")
	await until(func() -> bool: return p.global_position.distance_to(meet.global_position) < 5.0)
	arrived()
	await say("", "(The ground by the well has been sanded over. Fresh sand, raked smooth.)")
	GameState.set_flag(&"d1_saw_sand")
