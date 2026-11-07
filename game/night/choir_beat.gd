extends NightBeat
## Matins in the choir (design doc, "Core loop": count the brothers; the
## incense is lit here. Night 3: "you see a brother in the choir who died on
## night 2 (hallucination) or a hooded stranger in his place (sober)").
##
## The incense is +25 Dose, fast, and can't be avoided on nights 1-3; on
## those nights it takes Dose to 50 at least and keeps it there for the rest
## of the night, so no one sees a mask clearly before night 4 (M0 default).
## The porter counts the brothers by looking at each one in turn.

const CHANT := preload("res://art/sfx/sfx_chant_loop.wav")
const INCENSE_DOSE := 25.0
const INCENSE_TIME := 8.0
const NIGHT_FLOOR := 50.0
## A brother is counted after this many seconds near the centre of view.
const COUNT_LOOK := 0.3
const COUNT_ANGLE := 12.0
const COUNT_RANGE := 14.0

@export var choir: Marker3D
@export var choir_radius := 6.0
## The stranger in the dead brother's place.
@export var dead_brother: DualRender
## Seconds the office goes on after the count.
@export var office_time := 15.0

var _chant: AudioStreamPlayer3D


func _ready() -> void:
	_chant = AudioStreamPlayer3D.new()
	_chant.stream = AudioOut.looped(CHANT)
	_chant.unit_size = 8.0
	add_child(_chant)


func run() -> void:
	var p := player()
	await until(func() -> bool: return p.global_position.distance_to(choir.global_position) < choir_radius)
	_chant.global_position = choir.global_position + Vector3.UP * 1.5
	if AudioOut.enabled():
		_chant.play()
	await say("", "(The incense is lit.)")
	GameState.add_dose(maxf(INCENSE_DOSE, NIGHT_FLOOR - GameState.dose), INCENSE_TIME)
	GameState.dose_floor = NIGHT_FLOOR
	GameState.set_flag(&"n3_incense")
	var saw_dead := await _count(p)
	GameState.set_flag(&"n3_headcount")
	GameState.set_flag(&"n3_saw_dead_brother", saw_dead)
	await say("", "(You count the brothers.)")
	await wait(office_time)
	_chant.stop()
	await say("", "(Matins is over. Now the lantern round.)")


## Waits until the porter has looked at every brother in the choir. Returns
## whether the dead brother was showing when he counted that place.
func _count(p: Player) -> bool:
	var targets: Array[Node3D] = []
	for b: Brother in get_tree().get_nodes_in_group(&"brothers"):
		if b.visible and b.global_position.distance_to(choir.global_position) < choir_radius + 4.0:
			targets.append(b)
	var looked := {}
	var saw_dead := false
	while targets.any(func(t: Node3D) -> bool: return looked.get(t, 0.0) < COUNT_LOOK):
		var dt := get_physics_process_delta_time()
		for t in targets:
			var head := t.global_position + Vector3.UP * 1.6
			if p.camera.global_position.distance_to(head) < COUNT_RANGE \
					and ViewCheck.off_centre(p.camera, head) < COUNT_ANGLE and ViewCheck.on_screen(p.camera, [head]):
				var before: float = looked.get(t, 0.0)
				looked[t] = before + dt
				if before < COUNT_LOOK and before + dt >= COUNT_LOOK and dead_brother and t.is_ancestor_of(dead_brother):
					saw_dead = dead_brother.drugged
		await get_tree().physics_frame
	return saw_dead
