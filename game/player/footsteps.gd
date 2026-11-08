extends AudioStreamPlayer3D
## Footsteps: one sound per stride from the player, picked by the surface
## underfoot (placeholder synthesised sounds, art/sfx/sfx_step_*). Running
## is louder (Look and Feel, "Sound feel": every surface has its own sound),
## and hunters hear it further (Earshot.RUN, Earshot.WALK); crouched steps
## are quieter still (Earshot.CROUCH).

const SURFACES: Array[String] = ["stone", "wood", "mud", "grass"]
const VARIANTS := 4
const WALK_DB := -16.0
const RUN_DB := -8.0
const CROUCH_DB := -24.0

var _streams := {}


func _ready() -> void:
	for surface in SURFACES:
		var list: Array[AudioStream] = []
		for i in VARIANTS:
			list.append(load("res://art/sfx/sfx_step_%s_%d.wav" % [surface, i]))
		_streams[surface] = list
	(owner as Player).stepped.connect(_on_stepped)


func _on_stepped(surface: String, running: bool) -> void:
	var crouched := (owner as Player).crouching
	Earshot.make(owner, global_position, Earshot.RUN if running else (Earshot.CROUCH if crouched else Earshot.WALK), owner)
	if not AudioOut.enabled():
		return
	var list: Array = _streams.get(surface, _streams["stone"])
	stream = list.pick_random()
	volume_db = RUN_DB if running else (CROUCH_DB if crouched else WALK_DB)
	pitch_scale = randf_range(0.92, 1.08)
	play()
