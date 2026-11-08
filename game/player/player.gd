class_name Player
extends CharacterBody3D
## The porter, Brother Alric (Look and Feel, "Camera and player feel"): a
## 1.4 m/s walk, a 4 m/s run that tires him (Stamina), gentle head bob that
## gets heavier when running, mouse look, and looking back over the shoulder
## while `look_back` is held. The lantern, interaction, footsteps, breath and
## body sounds are child nodes.
##
## He crawls through squeezes (crawl_along), hides in hiding spots (hide_in,
## then `interact` to climb out), and stumbles when he stares at the demon
## too long. `controls_locked` takes his body away (a capture, a cutscene).
## Talking to someone (start_talk, from Talk) he stands still, his view eased
## in on their face and held near it; a move key walks him away.
##
## Esc frees the mouse; a click captures it again.

signal stepped(surface: String, running: bool)
signal hid(spot: HidingSpot)
signal unhid(spot: HidingSpot)
## A move key while talking: he walks away from the conversation.
signal walked_away

const WALK_SPEED := 1.4
const RUN_SPEED := 4.0
const EYE_HEIGHT := 1.6
## m/s^2 speeding up and slowing down: a heavy habit, not a soldier.
const ACCEL := 8.0
const DECEL := 10.0
const GRAVITY := 9.8
## Head bob amplitude, m, walking and running.
const BOB_WALK := 0.02
const BOB_RUN := 0.05
## Stride length, m: one footstep per stride.
const STRIDE_WALK := 0.7
const STRIDE_RUN := 1.4
const LOOK_BACK_ANGLE := 150.0
const LOOK_BACK_TIME := 0.25
## Radians per pixel of mouse movement.
const MOUSE_SENSITIVITY := 0.0022
const PITCH_LIMIT := 85.0
## Seconds to climb into or out of a hiding spot.
const HIDE_TIME := 0.7
## Talking: degrees the view narrows, and seconds to turn to their face.
const TALK_ZOOM := 22.0
const TALK_TURN_TIME := 0.45

## Tests and scripted moments drive the player through these instead of the
## keyboard: x right, y forward, as from Input.get_vector().
var input_override := Vector2.ZERO
var use_input_override := false
var run_override := false

var running := false
var crawling := false
var stumbling := false
var controls_locked := false
## The spot he is hiding in, or null.
var hiding: HidingSpot
## What the floor underfoot sounds like.
var floor_surface := "stone"
## Talking to someone (Talk.begin).
var talking := false
## Degrees off the field of view while talking (StareMeter takes its own).
var zoom := 0.0

var _bob_phase := 0.0
var _bob_amp := 0.0
var _look_back := 0.0
## Eye height the bob works around: lower while hiding.
var _eye := EYE_HEIGHT
## Climbing in or out of a hiding spot.
var _hide_moving := false
## The hiding spot's view: look is limited around it.
var _hide_yaw := 0.0
var _hide_pitch := 0.0
## Talking: the view held on their face, and turning to it.
var _talk_yaw := 0.0
var _talk_pitch := 0.0
var _talk_cone := Vector2.ZERO
var _talk_turning := false
var _talk_tween: Tween

@onready var head: Node3D = $Head
@onready var look_back_pivot: Node3D = $Head/LookBack
@onready var camera: Camera3D = $Head/LookBack/Camera
@onready var lantern_hand: LanternHand = $Head/LanternHand
@onready var lantern: Lantern = $Head/LanternHand/Pivot/Lantern
@onready var stamina: Stamina = $Stamina
@onready var breath: Breath = $Breath
@onready var _collision: CollisionShape3D = $Collision


func _ready() -> void:
	add_to_group(&"player")
	collision_layer = Layers.CAPSULE
	collision_mask = Layers.MASK_PLAYER
	if DisplayServer.get_name() != "headless":
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


## True while something else has his body: crawling, hiding, stumbling,
## caught, talking.
func busy() -> bool:
	return crawling or hiding != null or stumbling or controls_locked or talking


func _unhandled_input(event: InputEvent) -> void:
	var motion := event as InputEventMouseMotion
	if motion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		if not (controls_locked or stumbling or _hide_moving or _talk_turning):
			_look(motion.relative * MOUSE_SENSITIVITY)
	elif event.is_action_pressed(&"interact") and hiding and not _hide_moving and not controls_locked:
		leave_hiding()
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed(&"ui_cancel"):
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	elif event is InputEventMouseButton and event.is_pressed() and Input.mouse_mode != Input.MOUSE_MODE_CAPTURED:
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
		get_viewport().set_input_as_handled()


func _look(turn: Vector2) -> void:
	var yaw := rotation.y - turn.x
	var pitch := head.rotation.x - turn.y
	if hiding:
		var yaw_limit := deg_to_rad(hiding.look_yaw)
		var pitch_limit := deg_to_rad(hiding.look_pitch)
		yaw = _hide_yaw + clampf(wrapf(yaw - _hide_yaw, -PI, PI), -yaw_limit, yaw_limit)
		pitch = clampf(pitch, _hide_pitch - pitch_limit, _hide_pitch + pitch_limit)
	elif talking:
		var yaw_cone := deg_to_rad(_talk_cone.x)
		var pitch_cone := deg_to_rad(_talk_cone.y)
		yaw = _talk_yaw + clampf(wrapf(yaw - _talk_yaw, -PI, PI), -yaw_cone, yaw_cone)
		pitch = clampf(pitch, _talk_pitch - pitch_cone, _talk_pitch + pitch_cone)
	rotation.y = yaw
	head.rotation.x = clampf(pitch, -deg_to_rad(PITCH_LIMIT), deg_to_rad(PITCH_LIMIT))


func _physics_process(delta: float) -> void:
	_update_look_back(delta)
	if crawling or hiding or _hide_moving:
		stamina.update(false, delta)
		return
	if talking:
		_stand_and_talk(delta)
		return
	var input := Vector2.ZERO
	var run_held := false
	if not (controls_locked or stumbling):
		input = input_override if use_input_override else Input.get_vector(
			&"move_left", &"move_right", &"move_back", &"move_forward")
		run_held = run_override if use_input_override else Input.is_action_pressed(&"run")
	running = run_held and input.length() > 0.1 and stamina.can_run()
	stamina.update(running, delta)
	var wish := global_basis * Vector3(input.x, 0.0, -input.y)
	wish.y = 0.0
	wish = wish.limit_length(1.0)
	var target := wish * (RUN_SPEED if running else WALK_SPEED)
	var flat := Vector3(velocity.x, 0.0, velocity.z)
	var rate := ACCEL if target.length() > flat.length() else DECEL
	flat = flat.move_toward(target, rate * delta)
	velocity.x = flat.x
	velocity.z = flat.z
	if not is_on_floor():
		velocity.y -= GRAVITY * delta
	move_and_slide()
	_read_floor()
	_update_bob(delta)


## Holds his view on `at` (someone's face): he turns to it and his view
## narrows, and he can look about only within `cone` (degrees either side).
func start_talk(at: Vector3, cone: Vector2) -> void:
	talking = true
	running = false
	_talk_cone = cone
	var to := at - camera.global_position
	_talk_yaw = atan2(-to.x, -to.z)
	_talk_pitch = clampf(atan2(to.y, Vector2(to.x, to.z).length()), -deg_to_rad(PITCH_LIMIT), deg_to_rad(PITCH_LIMIT))
	_talk_turning = true
	if _talk_tween:
		_talk_tween.kill()
	_talk_tween = create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	_talk_tween.tween_property(self, ^"rotation:y", rotation.y + wrapf(_talk_yaw - rotation.y, -PI, PI), TALK_TURN_TIME)
	_talk_tween.tween_property(head, ^"rotation:x", _talk_pitch, TALK_TURN_TIME)
	_talk_tween.tween_property(self, ^"zoom", TALK_ZOOM, TALK_TURN_TIME)
	_talk_tween.chain().tween_callback(func() -> void: _talk_turning = false)


## Lets his view go: the conversation is over, or he walked away.
func end_talk() -> void:
	if not talking:
		return
	talking = false
	_talk_turning = false
	if _talk_tween:
		_talk_tween.kill()
	_talk_tween = create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	_talk_tween.tween_property(self, ^"zoom", 0.0, TALK_TURN_TIME)


## Talking: he stands still, and a move key walks him away.
func _stand_and_talk(delta: float) -> void:
	stamina.update(false, delta)
	var wish := input_override if use_input_override else Input.get_vector(
		&"move_left", &"move_right", &"move_back", &"move_forward")
	if wish.length() > 0.5 and not controls_locked:
		walked_away.emit()
	var flat := Vector3(velocity.x, 0.0, velocity.z).move_toward(Vector3.ZERO, DECEL * delta)
	velocity.x = flat.x
	velocity.z = flat.z
	if not is_on_floor():
		velocity.y -= GRAVITY * delta
	move_and_slide()
	_update_bob(delta)


## Crawls through `points` (feet positions) over `seconds`, eyes at
## `eye_height`, ignoring collisions; control comes back at the end.
func crawl_along(points: Array[Vector3], seconds: float, eye_height: float) -> void:
	if busy() or points.is_empty():
		return
	crawling = true
	_collision.disabled = true
	velocity = Vector3.ZERO
	var total := 0.0
	var from := global_position
	for p in points:
		total += from.distance_to(p)
		from = p
	var tween := create_tween()
	tween.tween_property(head, ^"position:y", eye_height, 0.4)
	from = global_position
	for p in points:
		tween.tween_property(self, ^"global_position", p, seconds * from.distance_to(p) / maxf(total, 0.01))
		from = p
	tween.tween_property(head, ^"position:y", EYE_HEIGHT, 0.4)
	tween.finished.connect(_end_crawl)


func _end_crawl() -> void:
	crawling = false
	_collision.disabled = false


## Climbs into `spot`: the camera drops to the spot's view and the lantern
## goes under the cloak (Look and Feel: "Camera drops low, view framed by
## whatever you hide in"). `interact` climbs out.
func hide_in(spot: HidingSpot) -> void:
	if busy() or _hide_moving:
		return
	hiding = spot
	_hide_moving = true
	_collision.disabled = true
	velocity = Vector3.ZERO
	running = false
	lantern_hand.force_cover = true
	var view := spot.view.global_transform
	var look := -view.basis.z
	_hide_yaw = atan2(-look.x, -look.z)
	_hide_pitch = asin(clampf(look.y, -1.0, 1.0))
	var tween := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tween.tween_property(self, ^"global_position", view.origin - Vector3.UP * spot.eye_height, HIDE_TIME)
	tween.tween_property(self, ^"_eye", spot.eye_height, HIDE_TIME)
	tween.tween_property(self, ^"rotation:y", rotation.y + wrapf(_hide_yaw - rotation.y, -PI, PI), HIDE_TIME)
	tween.tween_property(head, ^"rotation:x", _hide_pitch, HIDE_TIME)
	tween.tween_property(head, ^"position", Vector3(0.0, spot.eye_height, 0.0), HIDE_TIME)
	tween.chain().tween_callback(func() -> void: _hide_moving = false)
	spot.enter(self)
	hid.emit(spot)


## Climbs out of the hiding spot to its exit. `instant` for being dragged out.
func leave_hiding(instant := false) -> void:
	if hiding == null:
		return
	var spot := hiding
	spot.exit_spot(self)
	var to := spot.exit.global_position
	var done := func() -> void:
		hiding = null
		_hide_moving = false
		_collision.disabled = false
		lantern_hand.force_cover = false
		unhid.emit(spot)
	if instant:
		global_position = to
		_eye = EYE_HEIGHT
		head.position = Vector3(0.0, EYE_HEIGHT, 0.0)
		done.call()
		return
	_hide_moving = true
	var tween := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tween.tween_property(self, ^"global_position", to, HIDE_TIME)
	tween.tween_property(self, ^"_eye", EYE_HEIGHT, HIDE_TIME)
	tween.tween_property(head, ^"position", Vector3(0.0, EYE_HEIGHT, 0.0), HIDE_TIME)
	tween.tween_property(head, ^"rotation:x", 0.0, HIDE_TIME)
	tween.chain().tween_callback(done)


## Loses his footing for `seconds` (staring at the demon): the view tips and
## drops, and he can't move or look.
func stumble(seconds: float) -> void:
	if busy():
		return
	stumbling = true
	# A step back.
	velocity = global_basis.z * 1.2
	var tween := create_tween().set_trans(Tween.TRANS_SINE)
	tween.set_parallel()
	tween.tween_property(head, ^"rotation:z", 0.35, seconds * 0.3).set_ease(Tween.EASE_OUT)
	tween.tween_property(self, ^"_eye", EYE_HEIGHT - 0.5, seconds * 0.3).set_ease(Tween.EASE_OUT)
	tween.tween_property(head, ^"rotation:x", deg_to_rad(-25.0), seconds * 0.3)
	tween.chain().tween_property(head, ^"rotation:z", 0.0, seconds * 0.7).set_ease(Tween.EASE_IN_OUT)
	tween.tween_property(self, ^"_eye", EYE_HEIGHT, seconds * 0.7).set_ease(Tween.EASE_IN_OUT)
	tween.chain().tween_callback(func() -> void: stumbling = false)


## Lying on his back, looking up (waking in the infirmary).
func lie_down() -> void:
	_eye = 0.7
	head.position = Vector3(0.0, _eye, 0.0)
	head.rotation = Vector3(deg_to_rad(60.0), 0.0, 0.0)


## Gets up from lying over `seconds`; await it.
func get_up(seconds: float) -> void:
	var tween := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tween.tween_property(self, ^"_eye", EYE_HEIGHT, seconds)
	tween.tween_property(head, ^"rotation:x", 0.0, seconds)
	await tween.finished


## Puts him at `at` facing `yaw`, standing, with nothing in progress.
func place(at: Vector3, yaw: float) -> void:
	if hiding:
		leave_hiding(true)
	global_position = at
	velocity = Vector3.ZERO
	rotation = Vector3(0.0, yaw, 0.0)
	head.rotation = Vector3.ZERO
	_eye = EYE_HEIGHT
	head.position = Vector3(0.0, EYE_HEIGHT, 0.0)


func _read_floor() -> void:
	for i in get_slide_collision_count():
		var hit := get_slide_collision(i)
		if hit.get_normal().y > 0.7:
			var collider := hit.get_collider()
			if collider:
				floor_surface = collider.get_meta(&"surface", "stone")
			return


func _update_bob(delta: float) -> void:
	var speed := Vector2(velocity.x, velocity.z).length() if is_on_floor() else 0.0
	var t := clampf((speed - WALK_SPEED) / (RUN_SPEED - WALK_SPEED), 0.0, 1.0)
	var target_amp := lerpf(BOB_WALK, BOB_RUN, t) * minf(speed / WALK_SPEED, 1.0)
	_bob_amp = move_toward(_bob_amp, target_amp, delta * 0.2)
	var stride := lerpf(STRIDE_WALK, STRIDE_RUN, t)
	var before := floori(_bob_phase / PI)
	_bob_phase += speed * delta / stride * PI
	if floori(_bob_phase / PI) != before and speed > 0.3:
		stepped.emit(floor_surface, running)
	# The head dips once per step and sways once per two.
	head.position = Vector3(
		_bob_amp * 0.5 * sin(_bob_phase),
		_eye - _bob_amp * (1.0 - cos(2.0 * _bob_phase)) * 0.5,
		0.0)


func _update_look_back(delta: float) -> void:
	var held := Input.is_action_pressed(&"look_back") and not busy()
	_look_back = move_toward(_look_back, 1.0 if held else 0.0, delta / LOOK_BACK_TIME)
	look_back_pivot.rotation.y = deg_to_rad(LOOK_BACK_ANGLE) * smoothstep(0.0, 1.0, _look_back)
