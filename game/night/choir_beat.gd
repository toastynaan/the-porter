extends NightBeat
## Matins in the choir (design doc, "Core loop": count the brothers; the
## incense is lit here. Night 3: "you see a brother in the choir who died on
## night 2 (hallucination) or a hooded stranger in his place (sober)").
##
## The incense is +25 Dose, fast, and can't be avoided on nights 1-3; on
## those nights it takes Dose to 50 at least and keeps it there for the rest
## of the night, so no one sees a mask clearly before night 4 (M0 default).
## From night 4 it comes a breath at a time while it burns, and where he
## stands decides how much (docs/mechanics.md, "Incense from night 4"): in
## his stall, all of it; by the choir's west door, about a third; holding
## his breath, none. But if a brother sees him out of his stall while the
## office is sung, Suspicion +10.
## The porter counts the brothers by looking at each one in turn. The chant
## starts as the bell is rung, so he can follow it to the choir, and the way
## there is lit.

const CHANT := preload("res://art/sfx/sfx_chant_loop.wav")
const INCENSE_DOSE := 25.0
const INCENSE_TIME := 8.0
const NIGHT_FLOOR := 50.0
## A brother is counted after this many seconds near the centre of view.
const COUNT_LOOK := 0.3
const COUNT_ANGLE := 12.0
const COUNT_RANGE := 14.0
## From this night the incense can be partly avoided.
const AVOIDABLE_FROM := 4
## In his stall, and by the west door (m); the door's share of the incense.
const STALL_RADIUS := 1.3
const DOOR_RADIUS := 2.2
const DOOR_SHARE := 1.0 / 3.0
const OUT_OF_STALL_SUSPICION := 10

@export var choir: Marker3D
@export var choir_radius := 6.0
## The stranger in the dead brother's place.
@export var dead_brother: DualRender
## Seconds the office goes on after the count.
@export var office_time := 15.0
## His stall in the choir, and the choir's west door.
@export var stall: Marker3D
@export var west_door: Marker3D

var _chant: AudioStreamPlayer3D
## The office is being sung; seconds of incense still burning.
var _office := false
var _burning := 0.0
## Dose taken from the incense tonight (tests).
var taken := 0.0


func _ready() -> void:
	_chant = AudioStreamPlayer3D.new()
	_chant.stream = AudioOut.looped(CHANT)
	_chant.unit_size = 12.0
	_chant.max_distance = 120.0
	add_child(_chant)


func run() -> void:
	var p := player()
	_chant.global_position = choir.global_position + Vector3.UP * 1.5
	if AudioOut.enabled():
		_chant.play()
	var way := Wayfinding.show_way(self, choir.global_position)
	await until(func() -> bool: return p.global_position.distance_to(choir.global_position) < choir_radius)
	Wayfinding.put_out(way)
	await say("", "(The incense is lit.)")
	_office = true
	if GameState.night < AVOIDABLE_FROM:
		GameState.add_dose(maxf(INCENSE_DOSE, NIGHT_FLOOR - GameState.dose), INCENSE_TIME)
		GameState.dose_floor = NIGHT_FLOOR
	else:
		_burning = INCENSE_TIME
	GameState.set_flag(GameState.tonight("incense"))
	var saw_dead := await _count(p)
	GameState.set_flag(GameState.tonight("headcount"))
	GameState.set_flag(GameState.tonight("saw_dead_brother"), saw_dead)
	await say("", "(You count the brothers.)")
	await wait(office_time)
	while _burning > 0.0:
		await get_tree().physics_frame
	_office = false
	_chant.stop()
	await say("", "(Matins is over. Now the lantern round.)")


## While the incense burns (from night 4), he breathes in what reaches him
## where he stands; out of his stall, a brother may see him.
func _physics_process(delta: float) -> void:
	if not _office:
		return
	var p := player()
	if p == null:
		return
	if _burning > 0.0:
		_burning -= delta
		var share := 0.0 if p.breath.holding else (DOOR_SHARE if _near(p, west_door, DOOR_RADIUS) else 1.0)
		var amount := INCENSE_DOSE / INCENSE_TIME * delta * share
		taken += amount
		GameState.breathe_in(amount)
	var flag := GameState.tonight("seen_out_of_stall")
	if GameState.night >= AVOIDABLE_FROM and stall and not _near(p, stall, STALL_RADIUS) and not GameState.has_flag(flag):
		for b: Brother in get_tree().get_nodes_in_group(&"brothers"):
			if b.visible and b.global_position.distance_to(choir.global_position) < choir_radius + 4.0 and SeenWatch.sees(b, p):
				GameState.set_flag(flag, StringName(b.name))
				GameState.raise_suspicion(OUT_OF_STALL_SUSPICION)
				break


func _near(p: Player, m: Marker3D, radius: float) -> bool:
	return m != null and Vector2(p.global_position.x - m.global_position.x, p.global_position.z - m.global_position.z).length() < radius


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
