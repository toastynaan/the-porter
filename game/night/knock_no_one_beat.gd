extends NightBeat
## The knock with no one there (design doc, night 1: a final knock after
## midnight with no one there; Mab saw nobody; it happens even at Dose 0, and
## nothing ever explains it). One of the three things with no human
## explanation before night 6. At `knock_hour` someone knocks at the gate,
## and knocks until the porter comes to the grille; there's no one in the
## lane, either way. It goes in his notes.

const KNOCK := preload("res://art/sfx/sfx_knock.wav")

@export var knock_hour := 26.0
@export var grate: Duty
@export var knock_every := 5.0

var _audio: AudioStreamPlayer3D


func _ready() -> void:
	_audio = AudioStreamPlayer3D.new()
	_audio.unit_size = 6.0
	add_child(_audio)


func run() -> void:
	await clock().wait_until(knock_hour)
	var answered := [false]
	grate.used.connect(func(_by: Node) -> void: answered[0] = true, CONNECT_ONE_SHOT)
	grate.enabled = true
	clock().wake()
	var t := 0.0
	while not answered[0]:
		if t <= 0.0:
			t = knock_every
			if AudioOut.enabled():
				_audio.global_position = grate.global_position + Vector3(-0.6, 1.4, 0.0)
				_audio.stream = KNOCK
				_audio.play()
		await get_tree().physics_frame
		t -= get_physics_process_delta_time()
	grate.enabled = false
	GameState.set_flag(GameState.tonight("knock_no_one"))
	GameState.note(&"knock_no_one")
	await say("", "(No one. The lane is empty both ways, and the lanterns are steady.)")
