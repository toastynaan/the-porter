class_name Hallucinations
extends Node3D
## What the drug does to the porter's senses, never to his body (design doc,
## "Effect tiers"; docs/systems/mechanics.md, "The drug, and food": Dose changes
## only what he sees and hears). Every so often, while he's about, it plays
## an event the tier allows; the tiers stack:
## - 25+, his ears: a whisper at his shoulder, steps behind him, his name
##   called from somewhere (in Edwin's voice once Edwin is dead).
## - 50+, his eyes: a shape at the edge of his view, gone when he looks; a
##   face in the grain of a door, gone when he stares at it. (The carvings
##   turn their heads by themselves, Carving.)
## - 75+, both, and lies: hooves running at him from behind that stop just
##   short; a death in front of him that never happened (a fake DeathScene).
##   (The walls breathe, DoseLook; the dead stand in the choir, DeadInChoir.)
## Nothing an event shows is left behind. None plays in a chase, while he
## talks, dozes or reads, or while a menu or card is up.

signal fired(kind: StringName)

enum Tier { CLEAR, EARS, EYES, FULL }

const TIER_DOSE: Array[float] = [25.0, 50.0, 75.0]
const EVENTS := {
	Tier.EARS: [&"whisper", &"steps_behind", &"name"],
	Tier.EYES: [&"edge_shape", &"face_in_grain"],
	Tier.FULL: [&"fake_rush", &"fake_death"],
}
const WHISPERS: Array[AudioStream] = [preload("res://art/sfx/sfx_whisper_0.wav"),
	preload("res://art/sfx/sfx_whisper_1.wav"), preload("res://art/sfx/sfx_whisper_2.wav")]
const NAME := preload("res://art/sfx/sfx_name.wav")
const STEPS: Array[AudioStream] = [preload("res://art/sfx/sfx_step_stone_0.wav"),
	preload("res://art/sfx/sfx_step_stone_1.wav"), preload("res://art/sfx/sfx_step_stone_2.wav")]
const HOOVES: Array[AudioStream] = [preload("res://art/sfx/sfx_hoof_0.wav"),
	preload("res://art/sfx/sfx_hoof_1.wav"), preload("res://art/sfx/sfx_hoof_2.wav")]
const SHAPE := preload("res://game/characters/chr_stranger.tscn")
const FACE := preload("res://art/tex/tex_face_grain.png")
const FAKE_VICTIM := preload("res://game/characters/chr_choir_brother_b.tscn")
## Seconds between events, by tier (EARS, EYES, FULL).
const GAPS: Array[Vector2] = [Vector2(40.0, 70.0), Vector2(30.0, 55.0), Vector2(20.0, 40.0)]
## A shape at the edge of view: how far off centre, how far away, how long.
const SHAPE_ANGLE := 48.0
const SHAPE_RANGE := Vector2(7.0, 12.0)
const SHAPE_TIME := 2.5
const SHAPE_SEEN_ANGLE := 22.0

@export var active := true

## What has fired: [kind, Dose].
var history: Array = []

var _timer := 20.0
var _audio: AudioStreamPlayer3D
var _rng := RandomNumberGenerator.new()


func _ready() -> void:
	add_to_group(&"hallucinations")
	_audio = AudioStreamPlayer3D.new()
	_audio.unit_size = 3.0
	add_child(_audio)


static func tier(dose: float) -> Tier:
	if dose >= TIER_DOSE[2]:
		return Tier.FULL
	if dose >= TIER_DOSE[1]:
		return Tier.EYES
	if dose >= TIER_DOSE[0]:
		return Tier.EARS
	return Tier.CLEAR


## The events the tier at `dose` allows.
static func allowed(dose: float) -> Array[StringName]:
	var out: Array[StringName] = []
	for t in range(Tier.EARS, tier(dose) + 1):
		for e: StringName in EVENTS[t]:
			out.append(e)
	return out


func _process(delta: float) -> void:
	var t := tier(GameState.dose)
	if not active or t == Tier.CLEAR or not _quiet_enough():
		return
	_timer -= delta
	if _timer <= 0.0:
		var gap := GAPS[t - 1]
		_timer = _rng.randf_range(gap.x, gap.y)
		var kinds := allowed(GameState.dose)
		fire(kinds[_rng.randi() % kinds.size()])


## Nothing else is going on: no chase, no talk, no dozing, nothing held up.
func _quiet_enough() -> bool:
	if GameState.seconds_per_hour <= 0.0 or get_tree().paused or Talk.talking:
		return false
	var clock := get_tree().get_first_node_in_group(&"night_clock") as NightClock
	if clock and clock.dozing:
		return false
	for h: Hunter in get_tree().get_nodes_in_group(&"hunters"):
		if not h.dormant and h.state == Hunter.State.CHASE:
			return false
	return DutyGlyph.allowed(get_tree()) or not Settings.guidance


## Plays the event `kind` now. Returns whether it could.
func fire(kind: StringName) -> bool:
	var p := get_tree().get_first_node_in_group(&"player") as Player
	if p == null:
		return false
	var ok := true
	match kind:
		&"whisper":
			_play_at(WHISPERS[_rng.randi() % WHISPERS.size()], _around(p, 1.0, true), -4.0)
		&"steps_behind":
			_steps_behind.call(p)
		&"name":
			_play_at(NAME, _around(p, _rng.randf_range(10.0, 15.0), false), 0.0)
			var who := "Edwin's voice, calling your name." if GameState.has_flag(&"died_edwin") else "Someone calls your name."
			Talk.say("", "(%s)" % who)
		&"edge_shape":
			ok = _edge_shape(p)
		&"face_in_grain":
			ok = _face_in_grain(p)
		&"fake_rush":
			_fake_rush.call(p)
		&"fake_death":
			ok = _fake_death(p)
		_:
			ok = false
	if ok:
		history.append([kind, GameState.dose])
		fired.emit(kind)
	return ok


## A point `distance` from him: behind his shoulder, or anywhere around.
func _around(p: Player, distance: float, behind: bool) -> Vector3:
	var yaw := p.rotation.y + (PI + _rng.randf_range(-0.8, 0.8) if behind else _rng.randf_range(-PI, PI))
	return p.camera.global_position + Vector3(-sin(yaw), 0.0, -cos(yaw)) * distance


func _play_at(stream: AudioStream, at: Vector3, db: float) -> void:
	if not AudioOut.enabled():
		return
	var a := AudioStreamPlayer3D.new()
	a.stream = stream
	a.volume_db = db
	a.unit_size = 4.0
	add_child(a)
	a.global_position = at
	a.play()
	a.finished.connect(a.queue_free)


func _steps_behind(p: Player) -> void:
	for i in 3:
		_play_at(STEPS[i], p.global_position + p.global_basis.z * (2.5 - i * 0.4) + Vector3.UP * 0.1, -10.0)
		await get_tree().create_timer(0.55, false).timeout


func _fake_rush(p: Player) -> void:
	for i in 6:
		var d := 12.0 - i * 2.2
		_play_at(HOOVES[i % HOOVES.size()], p.global_position + p.global_basis.z * d, -2.0)
		await get_tree().create_timer(0.3, false).timeout


## A tall shape at the edge of his view, gone when he looks at it.
func _edge_shape(p: Player) -> bool:
	var at := _point_in_view(p, SHAPE_ANGLE * (1.0 if _rng.randf() < 0.5 else -1.0), _rng.randf_range(SHAPE_RANGE.x, SHAPE_RANGE.y))
	if at == Vector3.INF:
		return false
	var shape := CharacterLook.new()
	shape.look = SHAPE
	add_child(shape)
	shape.global_position = at
	var to := p.global_position - at
	shape.rotation.y = atan2(-to.x, -to.z)
	shape.scale = Vector3(1.0, 1.15, 1.0)
	_shape_life.call(shape, p)
	return true


func _shape_life(shape: Node3D, p: Player) -> void:
	var t := 0.0
	while t < SHAPE_TIME and is_instance_valid(shape):
		if ViewCheck.off_centre(p.camera, shape.global_position + Vector3.UP * 1.5) < SHAPE_SEEN_ANGLE:
			break
		await get_tree().process_frame
		t += PlayTime.idle(self)
	if is_instance_valid(shape):
		shape.queue_free()


## A face in the grain of the nearest wooden door he isn't looking at.
func _face_in_grain(p: Player) -> bool:
	var best: Door = null
	for d: Door in get_tree().get_nodes_in_group(&"doors"):
		var dist := d.global_position.distance_to(p.global_position)
		if dist < 7.0 and not d.grille and (best == null or dist < best.global_position.distance_to(p.global_position)) \
				and not ViewCheck.on_screen(p.camera, [d.global_position + Vector3.UP * 1.3]):
			best = d
	if best == null:
		return false
	var face := Decal.new()
	face.texture_albedo = FACE
	face.size = Vector3(0.6, 0.6, 0.6)
	face.cull_mask = 1048573
	best.add_child(face)
	# On the door's face, toward the porter.
	var side := signf((best.global_transform.affine_inverse() * p.global_position).z)
	face.position = Vector3(0.0, 1.45, side * 0.6)
	face.rotation = Vector3(-side * PI * 0.5, 0.0, 0.0)
	_face_life.call(face, p)
	return true


func _face_life(face: Decal, p: Player) -> void:
	var stared := 0.0
	var t := 0.0
	while t < 20.0 and stared < 1.5 and is_instance_valid(face):
		if ViewCheck.off_centre(p.camera, face.global_position) < 15.0:
			stared += PlayTime.idle(self)
		await get_tree().process_frame
		t += PlayTime.idle(self)
	if is_instance_valid(face):
		face.queue_free()


## A death in front of him that never happened: it leaves nothing.
func _fake_death(p: Player) -> bool:
	var at := _point_in_view(p, _rng.randf_range(-12.0, 12.0), _rng.randf_range(7.0, 10.0))
	if at == Vector3.INF:
		return false
	var death := DeathScene.new()
	death.id = StringName("hallucination_%d" % history.size())
	death.fake = true
	death.victim_look = FAKE_VICTIM
	add_child(death)
	var to := p.global_position - at
	death.global_transform = Transform3D(Basis(Vector3.UP, atan2(to.x, to.z)), at)
	death.play()
	_free_later.call(death)
	return true


func _free_later(death: DeathScene) -> void:
	await get_tree().create_timer(30.0, false).timeout
	if is_instance_valid(death) and death.body == null:
		death.queue_free()


## A point on the navmesh `distance` ahead, `angle` degrees off his view,
## that he can see; Vector3.INF if there is none.
func _point_in_view(p: Player, angle: float, distance: float) -> Vector3:
	var map := p.get_world_3d().navigation_map
	for attempt in 6:
		var yaw := p.rotation.y + deg_to_rad(angle) * (1.0 - attempt * 0.12)
		var want := p.global_position + Vector3(-sin(yaw), 0.0, -cos(yaw)) * distance * (1.0 - attempt * 0.1)
		var at := NavigationServer3D.map_get_closest_point(map, want)
		if at.distance_to(want) < 1.5 and absf(at.y - p.global_position.y) < 1.0 \
				and ViewCheck.clear(p, p.camera.global_position, at + Vector3.UP * 1.4):
			return at
	return Vector3.INF
