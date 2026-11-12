extends Node
## A short film of the start of the road in (night 0), as it plays: the
## wagon setting off, the porter looking back down the road, round to the
## white chapel as it passes, and forward over the horse to the wall
## (tools/intro_film.sh, which runs this under Godot's movie writer). For
## seeing what stills can't: the rain, the horse's step, the wheels, the
## rooks, the light going.

## Seconds in, and where he looks then (a direction from his eyes); between
## them his view eases from one to the next.
const LOOKS := [
	[0.0, Vector3(-1.0, 0.03, 0.06)],
	[9.0, Vector3(-1.0, 0.02, -0.1)],
	[14.0, Vector3(-0.3, 0.08, 1.0)],
	[19.0, Vector3(0.3, 0.05, 1.0)],
	[23.0, Vector3(-1.0, 0.03, 0.25)],
	[44.0, Vector3(-1.0, 0.03, 0.2)],
]
const LENGTH := 44.0
## The same for the second film (`-- --part=gate`): the wall coming, the
## stop at Aldgate, through the arch looking back, and the street inside.
const GATE_LOOKS := [
	[0.0, Vector3(1.0, 0.08, -0.1)],
	[9.0, Vector3(1.0, 0.24, -0.12)],
	[15.0, Vector3(1.0, 0.5, 0.05)],
	[21.0, Vector3(0.45, 0.4, 1.0)],
	[27.0, Vector3(1.0, 0.12, -0.05)],
	[33.0, Vector3(-1.0, 0.08, 0.02)],
	[41.0, Vector3(-1.0, 0.26, 0.0)],
	[47.0, Vector3(0.5, 0.22, -1.0)],
	[52.0, Vector3(1.0, 0.1, 0.0)],
	[58.0, Vector3(1.0, 0.1, 0.0)],
]
const GATE_LENGTH := 58.0
## Where along the road the second film starts, and the hour then.
const GATE_FROM := 84.0
const GATE_HOUR := 16.84

var _p: Player
var _t := 0.0
var _looks: Array = LOOKS
var _length := LENGTH
var _gate := false
var _ride: Node


func _ready() -> void:
	Settings.subtitle_size = 1
	Settings.subtitle_backing = false
	Settings.less_motion = false
	Settings.fov = 70.0
	Settings.apply()
	NightPilot.fresh_night("user://intro_film_save.tres")
	GameState.night = 0
	GameState.chapter = 0
	var main := NightPilot.main_with("res://game/chapters/night0/night0.tscn")
	add_child(main)
	var night: Node = main.get(&"current_level")
	if OS.get_cmdline_user_args().has("--part=gate"):
		_gate = true
		_looks = GATE_LOOKS
		_length = GATE_LENGTH
		_ride = night.get_node(^"Director/Ride")
		_ride.set(&"traveller_talk", null)
	(night.get_node(^"Hallucinations") as Hallucinations).active = false
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	_p = get_tree().get_first_node_in_group(&"player") as Player
	# He turns away from the traveller's hello, and hears him out about the cart.
	Talk.auto_choice = func(options: PackedStringArray) -> int:
		return options.size() - 1 if not GameState.has_flag(&"talked_n0_traveller") else -1


func _process(delta: float) -> void:
	if _p == null or _p.riding == null:
		return
	if _gate and _ride:
		# Set down near the wall, the cart with the body long gone by.
		_ride.set(&"_hook_done", true)
		_ride.set(&"_along", GATE_FROM)
		var cart := _ride.get(&"body_cart") as Node3D
		if cart:
			cart.visible = false
		GameState.hour = GATE_HOUR
		_ride = null
	_t += delta
	if _t >= _length:
		get_tree().quit()
	# While someone talks to him his view is the game's own (its glance, and
	# the cart it follows as it goes by).
	if Talk.talking:
		return
	var dir: Vector3 = _looks[-1][1]
	for i in _looks.size() - 1:
		if _t >= float(_looks[i][0]) and _t < float(_looks[i + 1][0]):
			var k := smoothstep(0.0, 1.0, (_t - float(_looks[i][0])) / (float(_looks[i + 1][0]) - float(_looks[i][0])))
			dir = (_looks[i][1] as Vector3).slerp(_looks[i + 1][1] as Vector3, k)
	_p.rotation.y = atan2(-dir.x, -dir.z)
	_p.head.rotation.x = atan2(dir.y, Vector2(dir.x, dir.z).length())
