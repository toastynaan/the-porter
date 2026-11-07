extends AudioStreamPlayer
## Night wind over the abbey: a loop that drops when the listener is under a
## roof (Look and Feel, "Sound feel": the room tone is never silent).

const STREAM := preload("res://art/sfx/amb_wind_night.wav")
const OUTDOOR_DB := -14.0
const INDOOR_DB := -26.0
## How high to look for a roof, m.
const ROOF_CHECK := 30.0

var _level := OUTDOOR_DB


func _ready() -> void:
	var loop := STREAM.duplicate() as AudioStreamWAV
	loop.loop_mode = AudioStreamWAV.LOOP_FORWARD
	loop.loop_begin = 0
	loop.loop_end = int(loop.get_length() * loop.mix_rate)
	stream = loop
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
	_level = move_toward(_level, INDOOR_DB if indoors else OUTDOOR_DB, delta * 12.0)
	volume_db = _level
