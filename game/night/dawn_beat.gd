extends NightBeat
## Lauds and dawn (design doc, "Core loop" 7: Cole comes to take the gate
## and you go to your cell to sleep; night 3: "your keys have been moved").
## Cole walks to the gate and the porter gives it to him; Cole opens it for
## the day. In the cell the keys aren't on their hook but on the cot, and
## taking them back, the porter lies down and sleeps through the day. Dose
## falls over the day but not to zero (`sleep_keeps`).

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


func _ready() -> void:
	keys_moved.visible = false


func run() -> void:
	var p := player()
	cole.set_present(true, cole_off.global_transform)
	cole.go_to(cole_gate.global_position)
	await say("", "(Cole comes for the gate.)")
	await hand_over.wait_for_use()
	cole.stop()
	cole.global_transform = cole_gate.global_transform
	await say("Cole", "(Takes the gate without a word, and opens it for the day.)")
	gate.show_bar(false)
	await gate.swing(true)
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
	GameState.set_flag(&"n3_keys_moved")
	await say("", "(Your keys. Someone has moved them.)")
	await sleep.wait_for_use()
	await sleep_through_the_day(sleep_keeps, "(You sleep through the day.)")
