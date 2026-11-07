class_name StareMeter
extends Node
## Staring at the demon (design doc, "Rules for the Glimpses and Stalking
## phases"): looking straight at it builds a distortion over BUILD_TIME, the
## screen edges warp (the post shader's `stare`), the view narrows about 5°
## (Look and Feel, "Field of view"), the ears ring and the lantern gutters.
## Hold it full for HOLD_TIME and he loses his footing (Player.stumble).
## It fades when he looks away. Watches the "demon" group (DemonCostume).
## (M2 report defaults.)

const BUILD_TIME := 3.0
const FADE_TIME := 2.0
const HOLD_TIME := 2.0
const STUMBLE_TIME := 1.5
## Within this many degrees of the centre of view counts as staring.
const CENTRE_ANGLE := 20.0
const RANGE := 45.0
const FOV_DROP := 5.0
const RING := preload("res://art/sfx/sfx_ring_loop.wav")

## 0..1.
var value := 0.0

var _full := 0.0
var _base_fov := 70.0
var _ring: AudioStreamPlayer

@onready var _player: Player = owner


func _ready() -> void:
	# The player's own @onready references aren't set yet.
	_base_fov = (_player.get_node(^"Head/LookBack/Camera") as Camera3D).fov
	_ring = AudioStreamPlayer.new()
	_ring.stream = AudioOut.looped(RING)
	_ring.volume_db = -80.0
	add_child(_ring)


func _physics_process(delta: float) -> void:
	var looking := not _player.busy() and _looking_at_demon()
	value = move_toward(value, 1.0 if looking else 0.0, delta / (BUILD_TIME if looking else FADE_TIME))
	if value >= 1.0:
		_full += delta
		if _full >= HOLD_TIME:
			_full = 0.0
			_player.stumble(STUMBLE_TIME)
	else:
		_full = 0.0
	_player.camera.fov = _base_fov - FOV_DROP * value
	_player.lantern.stare = value
	get_tree().set_group(&"dose_driver", &"stare", value)
	if AudioOut.enabled():
		_ring.volume_db = linear_to_db(maxf(value * 0.6, 0.0001))
		if value > 0.01 and not _ring.playing:
			_ring.play()
		elif value <= 0.01 and _ring.playing:
			_ring.stop()


func _looking_at_demon() -> bool:
	var camera := _player.camera
	for demon: DemonCostume in get_tree().get_nodes_in_group(&"demon"):
		if not demon.is_visible_in_tree():
			continue
		for p in demon.stare_points():
			if camera.global_position.distance_to(p) < RANGE and ViewCheck.off_centre(camera, p) < CENTRE_ANGLE \
					and ViewCheck.on_screen(camera, [p]):
				return true
	return false
