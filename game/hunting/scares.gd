class_name Scares
extends Node3D
## Scares between chases (docs/log/full-game-run.md, "Scares between chases"):
## the hunter heard and glimpsed on every round, and a few jump scares, at
## most one a night. A night's round beats call these where the night wants
## them; each says whether it could play.
## - steps_above(): hooves or felt on the floor over his head.
## - light_out_ahead(): a light ahead of him gutters and goes out.
## - jump(kind): "body_drop", a body drops on a rope in front of him;
##   "face_at_grille", a face at the gate's grille that's gone when he
##   moves. Once a night (`jump_scare`).

signal played(kind: StringName)

const HOOVES: Array[AudioStream] = [preload("res://art/sfx/sfx_hoof_0.wav"),
	preload("res://art/sfx/sfx_hoof_1.wav"), preload("res://art/sfx/sfx_hoof_2.wav")]
const FELT: Array[AudioStream] = [preload("res://art/sfx/sfx_felt_0.wav"),
	preload("res://art/sfx/sfx_felt_1.wav"), preload("res://art/sfx/sfx_felt_2.wav")]
const STING := preload("res://art/sfx/sfx_sting.wav")
const DROP := preload("res://art/sfx/sfx_body_drop.wav")
const FACE := preload("res://game/characters/chr_stranger.tscn")
const BODY := preload("res://game/characters/chr_body.tscn")

## Where the face stands, outside the grille.
@export var grille_face: Marker3D

## What has played tonight, for tests.
var history: Array[StringName] = []


func _ready() -> void:
	add_to_group(&"scares")


func _player() -> Player:
	return get_tree().get_first_node_in_group(&"player") as Player


## Steps on the floor above him (hooves if `loud`), crossing over his head.
func steps_above(loud := false) -> bool:
	var p := _player()
	if p == null:
		return false
	var up := PhysicsRayQueryParameters3D.create(p.camera.global_position, p.camera.global_position + Vector3.UP * 6.0, Layers.WORLD)
	var hit := p.get_world_3d().direct_space_state.intersect_ray(up)
	if hit.is_empty():
		return false
	_walk_over.call(Vector3(hit["position"]) + Vector3.UP * 0.4, loud)
	_played(&"steps_above")
	return true


func _walk_over(above: Vector3, loud: bool) -> void:
	var p := _player()
	var across := p.global_basis.x if p else Vector3.RIGHT
	for i in 5:
		_play_at((HOOVES if loud else FELT)[i % 3], above + across * (i - 2) * 0.7, 0.0 if loud else -6.0)
		await get_tree().create_timer(0.6, false).timeout


## The nearest light ahead of him (not a duty's lamp, not the way's) gutters
## and goes out.
func light_out_ahead() -> bool:
	var p := _player()
	if p == null:
		return false
	var best: Candle = null
	for c: Candle in get_tree().get_nodes_in_group(&"candles"):
		if not c.lit or c.is_in_group(&"wayfinding") or c.is_in_group(&"duty_lamp") or c.is_in_group(&"rite_candle"):
			continue
		var flame := c.global_position + Vector3.UP * 0.15
		var d := c.global_position.distance_to(p.global_position)
		if d > 3.0 and d < 16.0 and ViewCheck.off_centre(p.camera, flame) < 40.0 and ViewCheck.on_screen(p.camera, [flame]) \
				and (best == null or d < best.global_position.distance_to(p.global_position)):
			best = c
	if best == null:
		return false
	_gutter_out.call(best)
	_played(&"light_out_ahead")
	return true


func _gutter_out(c: Candle) -> void:
	var e := c.energy
	for i in 6:
		c.energy = e * (0.3 if i % 2 == 0 else 0.8)
		await get_tree().create_timer(0.12, false).timeout
	c.energy = e
	c.lit = false


## A jump scare, at most one a night.
func jump(kind: StringName) -> bool:
	if GameState.has_flag(&"jump_scare"):
		return false
	var ok := false
	match kind:
		&"body_drop":
			ok = _body_drop()
		&"face_at_grille":
			ok = _face_at_grille()
	if ok:
		GameState.set_flag(&"jump_scare", kind)
		_played(kind)
	return ok


func _body_drop() -> bool:
	var p := _player()
	if p == null:
		return false
	var at := p.global_position - p.global_basis.z * 1.6
	var look := CharacterLook.new()
	look.look = preload("res://game/characters/chr_choir_brother_dead.tscn")
	add_child(look)
	look.global_position = at + Vector3.UP * 2.6
	var drop := create_tween()
	drop.tween_property(look, ^"global_position:y", at.y + 0.35, 0.22).set_ease(Tween.EASE_IN).set_trans(Tween.TRANS_QUAD)
	drop.tween_property(look, ^"global_position:y", at.y + 0.45, 0.15)
	_play_at(DROP, at + Vector3.UP * 1.5, 0.0)
	_play_at(STING, p.camera.global_position, 0.0)
	_gone_unseen.call(look, 1.5)
	return true


func _face_at_grille() -> bool:
	var p := _player()
	if p == null or grille_face == null:
		return false
	var look := CharacterLook.new()
	look.look = FACE
	add_child(look)
	look.global_transform = grille_face.global_transform
	_play_at(STING, p.camera.global_position, 0.0)
	_gone_unseen.call(look, 1.2)
	return true


## Gone once he looks away, or after `seconds` anyway.
func _gone_unseen(node: Node3D, seconds: float) -> void:
	var t := 0.0
	var p := _player()
	while is_instance_valid(node) and p and t < 8.0:
		t += PlayTime.idle(self)
		if t > seconds and not ViewCheck.on_screen(p.camera, [node.global_position + Vector3.UP * 1.0]):
			break
		await get_tree().process_frame
	if is_instance_valid(node):
		node.queue_free()


func _played(kind: StringName) -> void:
	history.append(kind)
	played.emit(kind)


func _play_at(stream: AudioStream, at: Vector3, db: float) -> void:
	if not AudioOut.enabled():
		return
	var a := AudioStreamPlayer3D.new()
	a.stream = stream
	a.volume_db = db
	a.unit_size = 5.0
	add_child(a)
	a.global_position = at
	a.play()
	a.finished.connect(a.queue_free)
