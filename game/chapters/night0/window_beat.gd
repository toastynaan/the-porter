extends NightBeat
## The window (design doc, "Night 0"; docs/systems/mechanics.md, "Sleeping"): lying
## down on the bed in his room at the top of the Cross Keys, he hears a cry;
## from the window he sees over the abbey wall into the court: a figure in a
## black habit, its back to him, kills a man by the well and drags him away
## toward the cellar. Sober, he saw a man; drunk (3 ales or more) the double
## image smears it, and his note says he'd drunk too much to be sure. This
## death is before his six nights and doesn't feed the rite. He can stay at
## the window or not; then he sleeps, and the night is over. If he's still
## up at midnight, Agnes sends him to bed (the window always happens).

@export var bed: Duty
@export var window: Marker3D
@export var death: DeathScene
## Where the killer drags the body (toward the cellar).
@export var drag_to: Marker3D
@export var midnight := 24.0
## How far forward of `window` he stands: right at the opening, so the court
## fills the view and not the shutters.
@export var lean_in := 0.45
## Degrees his view narrows as it follows the killing (talks narrow 22).
@export var narrow := 38.0


func run() -> void:
	var p := player()
	bed.enabled = true
	while not GameState.has_flag(&"n0_lay_down"):
		if GameState.hour >= midnight:
			await _sent_up(p)
			break
		await tick()
		if not bed.enabled:
			break
	bed.enabled = false
	GameState.set_flag(&"n0_lay_down")
	p.controls_locked = true
	await fade_to(0.6, 1.0)
	await say("", "(You lie down. The bed smells of other men. Then, outside, a cry, and it stops short.)")
	var forward := -window.global_basis.z
	p.place(window.global_position + forward * lean_in, window.global_rotation.y)
	# His eyes go to the court and follow what happens there; moving the
	# mouse lets go, as in a talk.
	var gaze := Node3D.new()
	add_child(gaze)
	gaze.global_position = death.global_position + Vector3.UP
	p.look_at_scene(gaze, narrow)
	var follow := func() -> void:
		while is_instance_valid(gaze):
			if is_instance_valid(death.killer):
				gaze.global_position = death.killer.global_position + Vector3.UP * 0.9
			await PlayTime.physics_frame(self)
	follow.call()
	await fade_to(0.0, 0.8)
	p.controls_locked = false
	await say("", "(From the window you can see over the abbey wall, into the court.)")
	await death.play()
	await wait(1.2)
	await death.drag_to(drag_to.global_position, 1.0, true)
	var drunk := DoseDriver.drunk_amount() > 0.0
	GameState.note(&"window_killing_drunk" if drunk else &"window_killing")
	GameState.set_flag(&"n0_saw_killing", &"drunk" if drunk else &"sober")
	await say("", "(Gone, toward the cellar. The court is empty again. Nobody comes.)")
	p.stop_looking()
	gaze.queue_free()


## Agnes sends him up to bed: midnight, and he's still about.
func _sent_up(p: Player) -> void:
	p.controls_locked = true
	await fade_to(1.0, 0.8)
	await say("Agnes {weary}", "Up you go, brother. I'll not have you sleeping on my benches.")
	p.place(bed.global_position + Vector3(0.0, 0.0, 0.0), 0.0)
	await fade_to(0.0, 0.6)
	p.controls_locked = false


func _ready() -> void:
	bed.used.connect(func(_by: Node) -> void: GameState.set_flag(&"n0_lay_down"))
