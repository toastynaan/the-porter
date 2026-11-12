extends NightBeat
## Lauds and dawn (design doc, "Core loop" 7: Cole comes to take the gate
## and you go to your cell to sleep; night 3: "your keys have been moved.
## They've been copied"). Cole walks to the gate and the porter gives it to
## him; Cole opens it for the day. With `keys_moved` (night 3), in the cell
## the keys aren't on their hook but on the cot, with wax in their teeth:
## from night 4 a locked guesthouse keeps no one safe (Saving). Before he
## sleeps he decides whom to tell about any body he found tonight and
## hasn't told anyone of (Report). Then he lies down and sleeps through the
## day. Dose falls over the day but not to zero (`sleep_keeps`).

@export var gate: AbbeyGate
@export var cole: VisitorNPC
## Where Cole comes from, out of sight, and where he keeps the gate.
@export var cole_off: Marker3D
@export var cole_gate: Marker3D
@export var hand_over: Duty
## The middle of the cell; the keys' absence is noticed within `cell_radius`.
@export var cell: Marker3D
@export var cell_radius := 3.0
## The keys on their hook (shown until dawn).
@export var keys_on_hook: Node3D
## The keys where they were moved to (hidden until dawn).
@export var keys_moved: Duty
## The cot: lie down and sleep.
@export var sleep: Duty
## Of the night's Dose, the part still in him when he wakes at dusk.
@export var sleep_keeps := 0.5
@export var cole_lines := PackedStringArray(["Cole {blank}: (Takes the gate without a word, and opens it for the day.)"])
@export var keys_lines := PackedStringArray(["(Your keys. Someone has moved them.)"])
@export var sleep_line := "(You sleep through the day.)"
## Night 4: someone has been in his cell. Said as he comes into it; the
## candle clock is found snapped.
@export var cell_lines := PackedStringArray()
@export var candle_clock: Node3D


func _ready() -> void:
	if keys_moved:
		keys_moved.visible = false


func run() -> void:
	var p := player()
	cole.set_present(true, cole_off.global_transform)
	cole.go_to(cole_gate.global_position)
	await say("", "(Cole comes for the gate.)")
	await hand_over.wait_for_use()
	arrived()
	cole.stop()
	cole.global_transform = cole_gate.global_transform
	await say_lines(cole_lines)
	gate.show_bar(false)
	await gate.swing(true)
	if keys_moved:
		await _keys(p)
	else:
		await say("", "(Go to your cell and sleep.)")
		if not cell_lines.is_empty():
			await until(func() -> bool: return p.global_position.distance_to(cell.global_position) < cell_radius)
			if candle_clock:
				candle_clock.rotation = Vector3(0.0, 0.0, deg_to_rad(80.0))
			await say_lines(cell_lines)
			GameState.set_flag(GameState.tonight("cell_violated"))
	for id in Report.unreported():
		await Report.ask(id, Report.name_of(id))
	await sleep.wait_for_use()
	await sleep_through_the_day(sleep_keeps, sleep_line)


## His keys aren't on their hook: on the cot, with wax in their teeth.
func _keys(p: Player) -> void:
	keys_on_hook.visible = false
	keys_moved.visible = true
	# Wanted from now, so the way to the cell is lit.
	var found := [false]
	keys_moved.used.connect(func(_by: Node) -> void: found[0] = true, CONNECT_ONE_SHOT)
	keys_moved.enabled = true
	await say("", "(Go to your cell and sleep.)")
	await until(func() -> bool: return found[0] or p.global_position.distance_to(cell.global_position) < cell_radius)
	await say("", "(Your keys are not on their hook.)")
	await until(func() -> bool: return found[0])
	keys_moved.enabled = false
	keys_moved.visible = false
	GameState.keys = [&"gate", &"guesthouse", &"charnel"]
	GameState.set_flag(GameState.tonight("keys_moved"))
	GameState.set_flag(&"keys_copied")
	GameState.note(&"keys_moved")
	await say_lines(keys_lines)
