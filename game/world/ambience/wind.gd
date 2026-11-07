extends AudioStreamPlayer
## Night wind over the abbey: a loop that drops when the listener is under a
## roof (Look and Feel, "Sound feel": the room tone is never silent). Full
## silence, at most once a night, stops it too (set_quiet with `full`).

const STREAM := preload("res://art/sfx/amb_wind_night.wav")
const OUTDOOR_DB := -14.0
const INDOOR_DB := -26.0
## How high to look for a roof, m.
const ROOF_CHECK := 30.0
const SILENT_DB := -60.0

var _level := OUTDOOR_DB
var _silent := false


func _ready() -> void:
	add_to_group(&"room_tone")
	stream = AudioOut.looped(STREAM)
	volume_db = _level
	if AudioOut.enabled():
		play()


func _physics_process(delta: float) -> void:
	var camera := get_viewport().get_camera_3d()
	if camera == null:
		return
	var from := camera.global_position
	var query := PhysicsRayQueryParameters3D.create(from, from + Vector3.UP * ROOF_CHECK, Layers.WORLD)
	var indoors := not camera.get_world_3d().direct_space_state.intersect_ray(query).is_empty()
	var target := SILENT_DB if _silent else (INDOOR_DB if indoors else OUTDOOR_DB)
	_level = move_toward(_level, target, delta * (40.0 if _silent else 12.0))
	volume_db = _level


func set_quiet(on: bool, full := false) -> void:
	_silent = on and full
