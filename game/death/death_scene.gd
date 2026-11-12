class_name DeathScene
extends Node3D
## A death the porter sees (docs/log/full-game-run.md, "Deaths and bodies"; Look
## and Feel, "Deaths"). The node stands where the victim stands, facing -Z;
## a beat calls play() when the porter is where the night wants him, and
## control is never taken away. It plays in one of three styles:
## - IMPLIED: a struggle half-seen, a cry cut off, a lantern dropped; then
##   the body, or only the blood.
## - GORY: one blow, blood up the wall (the "Spray" marker), the body left
##   as it fell, its blood around it.
## - THROAT: one quick cut, blood flying through the light, then down.
## The killer is the demon costume by default, which renders by Dose (sober,
## a man in a mask; drugged, the demon with long fingers and a crown of
## horns), or `killer_node`, someone already there (the night-3 hunter).
## He never moves while the porter looks; he is gone once the porter looks
## away, unless a beat keeps him (turn_to: in danger).
##
## The body falls as a ragdoll (Corpse) and stays; its blood stays until the
## cult cleans it (BloodMarks). A real death sets died_<id> and, with
## `rite`, feeds the rite a soul. A `fake` one is a hallucination (Dose 75+):
## the same on screen, but it feeds nothing, and once the porter has looked
## away the body, the blood and the killer are gone. Reloaded after a real
## death (a save after it), the body lies where it fell.

signal played

enum Style { IMPLIED, GORY, THROAT }

const KILLER := preload("res://game/demon/demon_costume.tscn")
const BODY := preload("res://game/characters/chr_body.tscn")
const CRY := preload("res://art/sfx/sfx_cry.wav")
const CUT := preload("res://art/sfx/sfx_cut.wav")
const FALL := preload("res://art/sfx/sfx_body_fall.wav")
const LANTERN_DROP := preload("res://art/sfx/sfx_lantern_drop.wav")
const OLD_BLOOD := Color("#5A1A14")
## Seconds the porter must have looked away before a fake is gone.
const FAKE_UNSEEN := 1.0

## Names the flags: died_<id>, fed_<id>.
@export var id := &""
@export var style := Style.IMPLIED
## Someone already in the world who dies here (a Brother, a VisitorNPC). He
## is put here at play() and taken out of the world as the body falls.
@export var victim: Node3D
## Or a figure to stand here (a character scene) when there is no `victim`.
@export var victim_look: PackedScene
## The body's colours (HumanoidRig: skin, shirt, pants, height, width).
@export var appearance := {"skin": Color(0.78, 0.66, 0.55), "shirt": Color("#1E1B19"),
	"pants": Color("#1E1B19"), "height": 1.0, "width": 1.0}
## Who does it: a scene to stand at the "Killer" marker (the costume by
## default), or someone already there.
@export var killer_scene: PackedScene = KILLER
@export var killer_node: Node3D
## Feeds the rite (the night-0 killing doesn't).
@export var rite := true
## A hallucination: leaves nothing, feeds nothing.
@export var fake := false
## The victim carries a lit lantern: the struggle is shapes against its light,
## then it falls from his hand, rolls, and burns low on the ground.
@export var lantern := false
## How bright his lantern burns (brighter where it must be seen from afar).
@export var lantern_energy := 1.6
## Which way the body falls, in this node's frame (-Z: forward, away from
## the killer behind him); m/s.
@export var fall_push := Vector3(0.0, 0.0, -1.6)
@export var struggle_time := 1.2

var killer: Node3D
var body: Corpse
var has_played := false

var _figure: Node3D
var _fleeting: Array[Node3D] = []
var _audio: AudioStreamPlayer3D
var _flame: OmniLight3D


func _ready() -> void:
	add_to_group(&"death_scenes")
	_audio = AudioStreamPlayer3D.new()
	_audio.unit_size = 8.0
	add_child(_audio)
	if not fake and not id.is_empty() and GameState.has_flag(died_flag()):
		has_played = true
		_take_out(victim)
		if not GameState.has_flag(StringName("moved_" + String(id))):
			_spawn_body.call_deferred(true)


func died_flag() -> StringName:
	return StringName("died_" + String(id))


## Plays the death; await it (it returns once the body is down).
func play() -> void:
	if has_played:
		return
	has_played = true
	_stand_victim()
	_stand_killer()
	if lantern:
		_light_lantern()
	match style:
		Style.IMPLIED:
			await _struggle(struggle_time)
			_sound(CRY)
		Style.GORY:
			await _struggle(minf(struggle_time, 0.6))
			_sound(CUT)
			_mark(&"spray", _marker_xform("Spray", Transform3D(Basis.IDENTITY, Vector3(0, 1.3, -1.0))))
		Style.THROAT:
			await _wait(0.25)
			_sound(CUT)
			_throat_spray()
	_fall()
	if lantern:
		_drop_lantern()
	await _wait(0.4)
	_mark(&"pool", _marker_xform("Pool", Transform3D(Basis.IDENTITY, Vector3(0, 0.02, -0.9))))
	if not fake:
		GameState.set_flag(died_flag())
		if rite:
			GameState.feed_rite(id)
	played.emit()
	if killer and killer_node == null:
		_killer_goes_unseen.call()
	if fake:
		_vanish_unseen.call()


## The killer drags the body to `to` (night 0: toward the cellar), at a
## walk, leaving drag marks, and both are gone there. Await it. With
## `carry_light`, he takes up the victim's dropped lantern and carries it
## low as he goes, so a watcher far off sees the light and the shapes go.
func drag_to(to: Vector3, speed := 1.0, carry_light := false) -> void:
	if killer == null or body == null:
		return
	if carry_light and _flame and is_instance_valid(_flame):
		_flame.reparent(killer, false)
		_flame.position = Vector3(0.35, 0.55, -0.2)
		create_tween().tween_property(_flame, ^"light_energy", lantern_energy * 0.9, 0.6)
	killer.set_meta(&"stays", true)
	var from := body.centre()
	_mark(&"drag", Transform3D(Basis.looking_at((to - from) * Vector3(1, 0, 1), Vector3.UP), from * Vector3(1, 0, 1) + Vector3(0, global_position.y, 0)))
	body.visible = false
	var dragged := CharacterLook.new()
	dragged.look = victim_look
	add_child(dragged)
	dragged.rotation = Vector3(-PI * 0.5, 0.0, 0.0)
	var start := killer.global_position
	var d := start.distance_to(to)
	var t := 0.0
	while t < d / speed and is_instance_valid(killer):
		t += PlayTime.physics(self)
		var at := start.lerp(to, minf(t * speed / d, 1.0))
		killer.global_position = at
		var dir := (to - start).normalized()
		killer.rotation = Vector3(0.0, atan2(dir.x, dir.z), 0.0)
		dragged.global_position = at - dir * 0.9 + Vector3.UP * 0.15
		await PlayTime.physics_frame(self)
	if is_instance_valid(killer):
		killer.queue_free()
	killer = null
	dragged.queue_free()
	if body:
		body.queue_free()
		body = null
	if not fake:
		GameState.set_flag(StringName("moved_" + String(id)))


## The killer turns to the porter (in danger: he's seen you) and stays.
func turn_to(point: Vector3) -> void:
	if killer:
		var to := point - killer.global_position
		killer.rotation.y = atan2(-to.x, -to.z)
		killer.set_meta(&"stays", true)


func _stand_victim() -> void:
	if victim:
		if victim.has_method(&"place"):
			victim.call(&"place", global_transform)
		elif victim.has_method(&"set_present"):
			victim.call(&"set_present", true, global_transform)
		else:
			victim.global_transform = global_transform
		_figure = victim
	elif victim_look:
		var look := CharacterLook.new()
		look.look = victim_look
		add_child(look)
		_figure = look


func _stand_killer() -> void:
	var at := _marker_xform("Killer", Transform3D(Basis.IDENTITY, Vector3(0, 0, 0.6)))
	if killer_node:
		killer = killer_node
		return
	if killer_scene == null:
		return
	killer = killer_scene.instantiate() as Node3D
	var to := global_position - at.origin
	var facing := Basis(Vector3.UP, atan2(-to.x, -to.z)) if Vector2(to.x, to.z).length() > 0.05 else at.basis
	killer.transform = global_transform.affine_inverse() * Transform3D(facing, at.origin)
	add_child(killer)


## The two of them shake together for `seconds`.
func _struggle(seconds: float) -> void:
	var t := 0.0
	while t < seconds:
		var k := sin(t * 23.0) * 0.12 + sin(t * 37.0) * 0.06
		if _figure:
			_figure.rotation.z = k
		if killer and killer_node == null:
			killer.rotation.z = -k * 0.5
		await get_tree().process_frame
		t += PlayTime.idle(self)
	if _figure:
		_figure.rotation.z = 0.0
	if killer and killer_node == null:
		killer.rotation.z = 0.0


func _fall() -> void:
	var at := _figure.global_transform if _figure else global_transform
	if victim:
		_take_out(victim)
	elif _figure:
		_figure.queue_free()
	_figure = null
	_spawn_body(false, at)
	_sound(FALL)


## Takes someone out of the world (a Brother, a VisitorNPC, anything else).
static func _take_out(who: Node3D) -> void:
	if who == null:
		return
	if who.has_method(&"place"):
		who.call(&"place", null)
	elif who.has_method(&"set_present"):
		who.call(&"set_present", false)
	else:
		who.visible = false


func _spawn_body(already_dead: bool, at := Transform3D()) -> void:
	if not is_inside_tree():
		return
	body = BODY.instantiate() as Corpse
	body.appearance = appearance
	var origin := at.origin if at != Transform3D() else global_position
	body.transform = global_transform.affine_inverse() * Transform3D(global_basis, origin)
	add_child(body)
	if already_dead:
		body.lie_dead.call_deferred()
	else:
		body.fall.call_deferred(global_basis * fall_push)
	if fake:
		_fleeting.append(body)


func _mark(kind: StringName, xform: Transform3D) -> void:
	if fake:
		_fleeting.append(BloodMarks.add_fleeting(self, kind, xform))
	else:
		BloodMarks.add(get_tree(), kind, xform, id)


## One quick cut: blood flying through the light, toward the porter's side.
func _throat_spray() -> void:
	var p := CPUParticles3D.new()
	p.one_shot = true
	p.amount = 70
	p.lifetime = 0.9
	p.explosiveness = 0.95
	p.direction = Vector3(0.0, 0.25, -1.0)
	p.spread = 22.0
	p.initial_velocity_min = 2.0
	p.initial_velocity_max = 4.0
	p.gravity = Vector3(0.0, -9.8, 0.0)
	var quad := QuadMesh.new()
	quad.size = Vector2(0.035, 0.035)
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.albedo_color = OLD_BLOOD
	mat.billboard_mode = BaseMaterial3D.BILLBOARD_PARTICLES
	quad.material = mat
	p.mesh = quad
	p.position = Vector3(0.0, 1.5, -0.1)
	add_child(p)
	p.emitting = true
	_mark(&"spray", _marker_xform("Spray", Transform3D(Basis.IDENTITY, Vector3(0, 1.0, -1.6))))
	get_tree().create_timer(2.0, false).timeout.connect(p.queue_free)


func _drop_lantern() -> void:
	var lamp := MeshInstance3D.new()
	var box := CylinderMesh.new()
	box.top_radius = 0.06
	box.bottom_radius = 0.07
	box.height = 0.2
	lamp.mesh = box
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.2, 0.17, 0.12)
	lamp.material_override = mat
	add_child(lamp)
	lamp.position = Vector3(0.25, 0.08, -0.3)
	lamp.rotation = Vector3(0.0, 0.0, PI * 0.5)
	if _flame:
		_flame.reparent(lamp, false)
		_flame.position = Vector3.ZERO
		create_tween().tween_property(_flame, ^"light_energy", lantern_energy * 0.4, 2.5)
	var roll := create_tween()
	roll.tween_property(lamp, ^"position", Vector3(0.9, 0.07, -0.9), 1.6).set_ease(Tween.EASE_OUT)
	roll.parallel().tween_property(lamp, ^"rotation:x", 7.0, 1.6).set_ease(Tween.EASE_OUT)
	_sound(LANTERN_DROP)
	if fake:
		_fleeting.append(lamp)


## The victim's lantern, lit in his hand.
func _light_lantern() -> void:
	_flame = OmniLight3D.new()
	_flame.light_color = Color(0.95, 0.62, 0.32)
	_flame.light_energy = lantern_energy
	_flame.omni_range = 7.0 * maxf(1.0, sqrt(lantern_energy / 1.6))
	_flame.shadow_enabled = true
	add_child(_flame)
	_flame.position = Vector3(0.3, 0.95, -0.15)


## Where a named marker child is, or `fallback` in this node's frame.
func _marker_xform(marker: String, fallback: Transform3D) -> Transform3D:
	var m := get_node_or_null(NodePath(marker)) as Node3D
	return m.global_transform if m else global_transform * fallback


## He never moves while the porter looks: gone once he looks away.
func _killer_goes_unseen() -> void:
	await _until_unseen(killer, 0.5)
	if is_instance_valid(killer) and not killer.has_meta(&"stays"):
		killer.queue_free()
		killer = null


## A hallucination: once he has looked away, nothing is left.
func _vanish_unseen() -> void:
	var anchor := body as Node3D
	await _until_unseen(anchor, FAKE_UNSEEN)
	for n in _fleeting:
		if is_instance_valid(n):
			n.queue_free()
	_fleeting.clear()
	body = null
	if is_instance_valid(killer) and killer_node == null:
		killer.queue_free()
		killer = null
	GameState.set_flag(StringName("fake_seen_" + String(id)))


func _until_unseen(node: Node3D, seconds: float) -> void:
	var away := 0.0
	while away < seconds and is_instance_valid(node):
		var camera := get_viewport().get_camera_3d()
		var at := node.global_position + Vector3.UP * 1.0
		if node is Corpse:
			at = (node as Corpse).centre()
		var seen := camera != null and ViewCheck.on_screen(camera, [at, node.global_position + Vector3.UP * 0.3])
		away = 0.0 if seen else away + PlayTime.idle(self)
		await get_tree().process_frame


func _sound(stream: AudioStream) -> void:
	if AudioOut.enabled():
		_audio.position = Vector3(0.0, 1.4, 0.0)
		_audio.stream = stream
		_audio.play()


func _wait(seconds: float) -> void:
	await get_tree().create_timer(seconds, false).timeout
