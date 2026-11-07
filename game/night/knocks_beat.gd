extends NightBeat
## Knocks at the gate (design doc, "Core loop": talk through the grate;
## admit to the guesthouse, refuse, or send for the prior. Night 3: "Walter
## again, with a bag that smells of the incense. A child-sized knock low on
## the gate; no one there (hallucination at Dose 50+)."). Sending for the
## prior raises Suspicion 10 (Ranulf overhears).

const KNOCK := preload("res://art/sfx/sfx_knock.wav")
const KNOCK_LOW := preload("res://art/sfx/sfx_knock_low.wav")
const PRIOR_SUSPICION := 10
const CHILD_KNOCK_DOSE := 50.0

@export var grate: Duty
@export var walter: Brother
@export var walter_room: Marker3D
## Seconds before each visitor knocks, and between knocks until answered.
@export var first_delay := 6.0
@export var knock_every := 5.0

var _audio: AudioStreamPlayer3D


func _ready() -> void:
	_audio = AudioStreamPlayer3D.new()
	_audio.unit_size = 6.0
	add_child(_audio)


func run() -> void:
	await wait(first_delay)
	await _knock_until_answered(KNOCK, 1.4)
	await say("Walter", "(Walter the pardoner, again. His bag smells of the incense.)")
	var pick := await Talk.choose(PackedStringArray(["Admit him to the guesthouse", "Turn him away", "Send for the prior"]))
	match pick:
		0:
			GameState.set_flag(&"n3_walter", &"admitted")
			walter.place(walter_room.global_transform)
			await say("", "(You let him in. He goes to the guesthouse.)")
		1:
			GameState.set_flag(&"n3_walter", &"refused")
			await say("", "(You turn him away.)")
		_:
			GameState.set_flag(&"n3_walter", &"prior")
			GameState.raise_suspicion(PRIOR_SUSPICION)
			await say("", "(You send for the prior.)")
	if GameState.dose >= CHILD_KNOCK_DOSE:
		await wait(first_delay)
		await _knock_until_answered(KNOCK_LOW, 0.4)
		GameState.set_flag(&"n3_child_knock")
		await say("", "(A small knock, low on the gate. No one there.)")
	await say("", "(The candle has burned down to the Matins mark. Ring the bell in the tower.)")


func _knock_until_answered(stream: AudioStream, height: float) -> void:
	var answered := [false]
	grate.used.connect(func(_by: Node) -> void: answered[0] = true, CONNECT_ONE_SHOT)
	grate.enabled = true
	var t := 0.0
	while not answered[0]:
		if t <= 0.0:
			t = knock_every
			if AudioOut.enabled():
				_audio.global_position = grate.global_position + Vector3(-0.6, height, 0.0)
				_audio.stream = stream
				_audio.play()
		await get_tree().physics_frame
		t -= get_physics_process_delta_time()
	grate.enabled = false
