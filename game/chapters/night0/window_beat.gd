extends NightBeat
## The window (design doc, "Night 0"; docs/systems/mechanics.md, "Sleeping"): he
## goes to the bed in his room at the top of the Cross Keys (it's outlined
## when he looks at it); instead of lying down he goes to the window, looks
## out at the abbey over the lane and says to himself what it is to him (your
## design, 2026-11-12). Then a cry, and his view closes in on the court over
## the abbey wall: a figure in a
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
## His thoughts at the window, before the cry ("Alric: ..." is said to himself).
@export var thoughts := PackedStringArray([
	"(You go to the window instead. Over the lane, the abbey's wall, and its roofs black against the rain.)",
	"Alric: So that's my new home.",
	"Alric: A gate, a bell, a candle to tell the hours by. Tomorrow it's mine to keep.",
])
## How long he takes to cross to the window, seconds.
@export var walk_time := 1.6
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
	if p.seat:
		p.stand_up()
	var forward := -window.global_basis.z
	await _cross_to(p, window.global_position + forward * lean_in, window.global_rotation.y)
	await say_lines(thoughts)
	await say("", "(Outside, a cry, and it stops short.)")
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
	p.controls_locked = false
	await death.play()
	await wait(1.2)
	await death.drag_to(drag_to.global_position, 1.0, true)
	var drunk := DoseDriver.drunk_amount() > 0.0
	GameState.note(&"window_killing_drunk" if drunk else &"window_killing")
	GameState.set_flag(&"n0_saw_killing", &"drunk" if drunk else &"sober")
	await say("", "(Gone, toward the cellar. The court is empty again. Nobody comes.)")
	p.stop_looking()
	gaze.queue_free()


## He crosses the room to the window: a short walk, his view turning to it,
## not a cut.
func _cross_to(p: Player, to: Vector3, yaw: float) -> void:
	var from := p.global_position
	var from_yaw := p.rotation.y
	var from_pitch := p.head.rotation.x
	var t := 0.0
	while t < 1.0:
		t = minf(t + PlayTime.physics(self) / maxf(walk_time, 0.01), 1.0)
		var k := smoothstep(0.0, 1.0, t)
		p.global_position = from.lerp(to, k)
		p.velocity = Vector3.ZERO
		p.rotation.y = lerp_angle(from_yaw, yaw, k)
		p.head.rotation.x = lerp_angle(from_pitch, deg_to_rad(-12.0), k)
		await PlayTime.physics_frame(self)


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
