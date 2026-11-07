extends NightBeat
## Dawn (design doc, night 3: "your keys have been moved"). The porter is back
## in his cell; his keys aren't on their hook but somewhere else, and taking
## them back ends the night.

@export var cell: Marker3D
## The keys on their hook (shown until dawn).
@export var keys_on_hook: Node3D
## The keys where they were moved to (hidden until dawn).
@export var keys_moved: Duty


func _ready() -> void:
	keys_moved.visible = false


func run() -> void:
	var p := player()
	GameState.seconds_per_hour = 0.0
	p.controls_locked = true
	await fade_to(1.0, 1.0)
	p.place(cell.global_position, cell.global_rotation.y)
	keys_on_hook.visible = false
	keys_moved.visible = true
	await fade_to(0.0, 1.5)
	p.controls_locked = false
	await say("", "(Dawn. Your keys are not on their hook.)")
	await keys_moved.wait_for_use()
	keys_moved.visible = false
	GameState.keys = [&"gate", &"guesthouse", &"charnel"]
	GameState.set_flag(&"n3_keys_moved")
	await say("", "(Your keys. Someone has moved them.)")
	GameState.set_flag(&"night3_done")
	await say("", "(End of night 3.)")
