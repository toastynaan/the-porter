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
	[6.0, Vector3(-1.0, 0.02, -0.1)],
	[9.0, Vector3(-0.2, 0.08, 1.0)],
	[14.0, Vector3(0.35, 0.05, 1.0)],
	[18.0, Vector3(1.0, 0.0, -0.35)],
	[24.0, Vector3(1.0, 0.02, -0.25)],
	[28.0, Vector3(-0.9, 0.05, 0.45)],
	[34.0, Vector3(-1.0, 0.03, 0.2)],
]
const LENGTH := 34.0

var _p: Player
var _t := 0.0


func _ready() -> void:
	Settings.subtitle_size = 1
	Settings.subtitle_backing = false
	Settings.less_motion = false
	Settings.fov = 70.0
	Settings.apply()
	NightPilot.fresh_night("user://intro_film_save.tres")
	GameState.night = 0
	GameState.chapter = 0
	var main := NightPilot.main_with("res://game/nights/night0.tscn")
	add_child(main)
	var night: Node = main.get(&"current_level")
	(night.get_node(^"Hallucinations") as Hallucinations).active = false
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	_p = get_tree().get_first_node_in_group(&"player") as Player
	# He doesn't answer the traveller: the talk closes itself and the road goes by.
	Talk.auto_choice = func(options: PackedStringArray) -> int: return options.size() - 1


func _process(delta: float) -> void:
	if _p == null or _p.riding == null:
		return
	_t += delta
	var dir: Vector3 = LOOKS[-1][1]
	for i in LOOKS.size() - 1:
		if _t >= float(LOOKS[i][0]) and _t < float(LOOKS[i + 1][0]):
			var k := smoothstep(0.0, 1.0, (_t - float(LOOKS[i][0])) / (float(LOOKS[i + 1][0]) - float(LOOKS[i][0])))
			dir = (LOOKS[i][1] as Vector3).slerp(LOOKS[i + 1][1] as Vector3, k)
	_p.rotation.y = atan2(-dir.x, -dir.z)
	_p.head.rotation.x = atan2(dir.y, Vector2(dir.x, dir.z).length())
	if _t >= LENGTH:
		get_tree().quit()
