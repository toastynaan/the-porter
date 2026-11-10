class_name Player
extends CharacterBody3D
## The porter, Brother Alric (Look and Feel, "Camera and player feel"): a
## 1.4 m/s walk, a 4 m/s run that tires him (Stamina), gentle head bob that
## gets heavier when running, mouse look, and looking back over the shoulder
## while `look_back` is held. The lantern, interaction, footsteps, breath and
## body sounds are child nodes.
##
## He crouches (`crouch`, held or toggled: 0.8 m/s, eyes at 1.0 m, no
## running, steps heard at half range, hidden behind anything 1 m high) and
## leans (`lean_left`, `lean_right`: the view moves 0.4 m aside and tilts
## 10°, and a hunter can see the leaning head). Look follows the mouse or the
## right stick at the Settings sensitivity (docs/mechanics.md, "Your body").
##
## He crawls through squeezes (crawl_along), hides in hiding spots (hide_in,
## then `interact` to climb out), and stumbles when he stares at the demon
## too long. `controls_locked` takes his body away (a capture, a cutscene).
## Talking to someone (start_talk, from Talk) he stands still: his view
## turns to their face (or to what the talk points him at) and narrows for a
## moment, then is his again, and a move key walks him away.
##
## He peeks through a squint (peek(), E again steps back): his eye to the
## bars, the view held within its few degrees.
##
## He holds one thing to throw at a time, in his right hand (docs/mechanics.md,
## "Throwing": a stone, a bone or a cup from his satchel): throw() sends it
## about 8 m ahead.
##
## The pause menu frees the mouse (Esc); a click captures it again.

signal stepped(surface: String, running: bool)
signal hid(spot: HidingSpot)
signal unhid(spot: HidingSpot)
## A move key while talking: he walks away from the conversation.
signal walked_away

const WALK_SPEED := 1.4
const RUN_SPEED := 4.0
const CROUCH_SPEED := 0.8
const EYE_HEIGHT := 1.6
## Crouched: eyes at 1.0 m, the body 1.15 m tall; seconds to crouch or stand.
const CROUCH_EYE := 1.0
const CROUCH_BODY := 1.15
const STAND_BODY := 1.75
const CROUCH_TIME := 0.25
## Leaning: the view moves this far aside and tilts this much; seconds to lean.
const LEAN_OFFSET := 0.4
const LEAN_TILT := 10.0
const LEAN_TIME := 0.2
## Kept clear of a wall when leaning toward it, m.
const LEAN_CLEARANCE := 0.15
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
## Radians per pixel of mouse movement, and per second at full stick.
const MOUSE_SENSITIVITY := 0.0022
const STICK_SPEED := 2.6
const PITCH_LIMIT := 85.0
## Seconds to climb into or out of a hiding spot.
const HIDE_TIME := 0.7
## Talking: degrees the view narrows, seconds to turn to their face, and
## seconds it stays on them before it's his again.
const TALK_ZOOM := 22.0
const TALK_TURN_TIME := 0.45
const TALK_HOLD := 1.2
## Seconds it follows something a talk points him at (a cart going by).
const TALK_WATCH := 3.6
## Pixels of mouse movement in one go that take his view off their face early.
const TALK_LET_GO := 3.0

## Tests and scripted moments drive the player through these instead of the
## keyboard: x right, y forward, as from Input.get_vector().
var input_override := Vector2.ZERO
var use_input_override := false
var run_override := false

var running := false
var crouching := false
## 0 standing to 1 crouched, eased.
var crouch_amount := 0.0
## -1 leaning left to 1 right, eased.
var lean := 0.0
## Tests and scripted moments: crouch and lean without the keys.
var crouch_override := false
var lean_override := 0.0
var crawling := false
var stumbling := false
var controls_locked := false
## The spot he is hiding in, or null.
var hiding: HidingSpot
## The squint he has his eye to, or null.
var peeking: Squint
## Riding on something (the wagon, night 0): he's carried with it, turns
## with it, and can only look about.
var riding: Node3D:
	set(value):
		riding = value
		if riding:
			_ride_yaw = riding.global_rotation.y
var _peek_from: Transform3D
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
## Talking: turning to their face, and his view still on it.
var _talk_turning := false
var _talk_glance := false
var _talk_tween: Tween
## What a talk has pointed his eyes at; they follow it while the glance lasts.
var _talk_watch: Node3D
## He has let go of the move keys since the talk began.
var _talk_still := false
## The heading of what he rides, last frame.
var _ride_yaw := 0.0

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
	return crawling or hiding != null or stumbling or controls_locked or talking or peeking != null


func _unhandled_input(event: InputEvent) -> void:
	var motion := event as InputEventMouseMotion
	if motion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		if _can_look():
			if _talk_glance and motion.relative.length() >= TALK_LET_GO:
				_let_go_of_face()
			_look(_turn(motion.relative * MOUSE_SENSITIVITY))
	elif Press.fresh(event, &"interact") and hiding and not _hide_moving and not controls_locked:
		leave_hiding()
		get_viewport().set_input_as_handled()
	elif Press.fresh(event, &"interact") and peeking and not _hide_moving:
		stop_peeking()
		get_viewport().set_input_as_handled()
	elif Press.fresh(event, &"crouch") and Settings.crouch_toggle:
		crouch_override = not crouch_override
	elif event is InputEventMouseButton and event.is_pressed() and Input.mouse_mode != Input.MOUSE_MODE_CAPTURED \
			and not get_tree().paused and DisplayServer.get_name() != "headless":
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
		get_viewport().set_input_as_handled()


func _can_look() -> bool:
	return not (controls_locked or stumbling or _hide_moving or _talk_turning)


## Mouse or stick movement (radians) at the Settings sensitivity and invert.
func _turn(raw: Vector2) -> Vector2:
	return Vector2(raw.x, -raw.y if Settings.invert_look else raw.y) * Settings.sensitivity


func _process(delta: float) -> void:
	if _talk_glance and is_instance_valid(_talk_watch):
		# His eyes follow what the talk is about.
		var to := _talk_watch.global_position - camera.global_position
		var k := 1.0 - exp(-8.0 * delta)
		rotation.y = lerp_angle(rotation.y, atan2(-to.x, -to.z), k)
		head.rotation.x = lerp_angle(head.rotation.x, clampf(atan2(to.y, Vector2(to.x, to.z).length()),
				-deg_to_rad(PITCH_LIMIT), deg_to_rad(PITCH_LIMIT)), k)
	var stick := Input.get_vector(&"look_left", &"look_right", &"look_up", &"look_down")
	if stick.length() > 0.0 and _can_look():
		if _talk_glance and stick.length() > 0.3:
			_let_go_of_face()
		_look(_turn(stick * STICK_SPEED * delta))


func _look(turn: Vector2) -> void:
	var yaw := rotation.y - turn.x
	var pitch := head.rotation.x - turn.y
	if hiding or peeking:
		var yaw_limit := deg_to_rad(hiding.look_yaw if hiding else Squint.PEEK_LOOK)
		var pitch_limit := deg_to_rad(hiding.look_pitch if hiding else Squint.PEEK_LOOK)
		yaw = _hide_yaw + clampf(wrapf(yaw - _hide_yaw, -PI, PI), -yaw_limit, yaw_limit)
		pitch = clampf(pitch, _hide_pitch - pitch_limit, _hide_pitch + pitch_limit)
	rotation.y = yaw
	head.rotation.x = clampf(pitch, -deg_to_rad(PITCH_LIMIT), deg_to_rad(PITCH_LIMIT))


func _physics_process(delta: float) -> void:
	_update_look_back(delta)
	if riding:
		global_position = riding.global_position
		var turned := wrapf(riding.global_rotation.y - _ride_yaw, -PI, PI)
		_ride_yaw = riding.global_rotation.y
		rotation.y += turned
		velocity = Vector3.ZERO
		return
	if crawling or hiding or _hide_moving or peeking:
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
	_update_crouch(delta)
	running = run_held and input.length() > 0.1 and stamina.can_run() and not crouching
	stamina.update(running, delta)
	_update_lean(delta)
	var wish := global_basis * Vector3(input.x, 0.0, -input.y)
	wish.y = 0.0
	wish = wish.limit_length(1.0)
	var target := wish * (RUN_SPEED if running else (CROUCH_SPEED if crouching else WALK_SPEED))
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


## Crouches while `crouch` is held (or toggled, by the Settings), and stands
## again once there is headroom.
func _update_crouch(delta: float) -> void:
	var want := crouch_override if (Settings.crouch_toggle or use_input_override) else (
		Input.is_action_pressed(&"crouch") or crouch_override)
	if controls_locked:
		want = crouching
	if not want and crouching and not _headroom():
		want = true
	crouching = want
	crouch_amount = move_toward(crouch_amount, 1.0 if crouching else 0.0, delta / CROUCH_TIME)
	var capsule := _collision.shape as CapsuleShape3D
	var height := lerpf(STAND_BODY, CROUCH_BODY, crouch_amount)
	if not is_equal_approx(capsule.height, height):
		capsule.height = height
		_collision.position.y = height * 0.5


## Room to stand up: nothing solid over his head.
func _headroom() -> bool:
	var from := global_position + Vector3.UP * (CROUCH_BODY - 0.05)
	var query := PhysicsRayQueryParameters3D.create(from, global_position + Vector3.UP * (STAND_BODY + 0.05), Layers.WORLD | Layers.DOOR)
	query.exclude = [get_rid()]
	return get_world_3d().direct_space_state.intersect_ray(query).is_empty()


## Leans while a lean key is held, not running, short of any wall.
func _update_lean(delta: float) -> void:
	var want := lean_override
	if not use_input_override:
		want += Input.get_axis(&"lean_left", &"lean_right")
	if running or controls_locked or stumbling:
		want = 0.0
	want = clampf(want, -1.0, 1.0)
	if not is_zero_approx(want):
		var side := global_basis.x * signf(want)
		var eye := global_position + Vector3.UP * _stand_eye()
		var query := PhysicsRayQueryParameters3D.create(eye, eye + side * (LEAN_OFFSET + LEAN_CLEARANCE), Layers.WORLD | Layers.DOOR)
		query.exclude = [get_rid()]
		var hit := get_world_3d().direct_space_state.intersect_ray(query)
		if not hit.is_empty():
			var room := maxf(eye.distance_to(hit["position"]) - LEAN_CLEARANCE, 0.0)
			want = signf(want) * minf(absf(want), room / LEAN_OFFSET)
	lean = move_toward(lean, want, delta / LEAN_TIME)


## Eye height standing or crouched (not hiding).
func _stand_eye() -> float:
	return lerpf(_eye, CROUCH_EYE, crouch_amount) if _eye > CROUCH_EYE else _eye


## Where a hunter looks for him: his head (moved aside when he leans) and his
## chest. Crouched, the head is the top of his back, below a 1 m stall.
func sight_points() -> Array[Vector3]:
	var head_at := camera.global_position - Vector3.UP * 0.12 * crouch_amount
	var chest := global_position + Vector3.UP * lerpf(1.1, 0.55, crouch_amount)
	return [head_at, chest]


## Talking to someone: he turns to `at` (their face) and his view narrows,
## stays on them for TALK_HOLD seconds (less if he looks away), then widens
## again and is his: he stands still, and looks where he likes.
## With `watch`, his view goes to that instead and follows it (as it moves)
## for TALK_WATCH seconds: what the talk is about.
func start_talk(at: Vector3, watch: Node3D = null) -> void:
	talking = true
	_talk_still = false
	running = false
	_talk_turning = true
	_talk_glance = true
	_talk_watch = watch
	if _talk_tween:
		_talk_tween.kill()
	_talk_tween = create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	if watch == null:
		var to := at - camera.global_position
		var yaw := atan2(-to.x, -to.z)
		var pitch := clampf(atan2(to.y, Vector2(to.x, to.z).length()), -deg_to_rad(PITCH_LIMIT), deg_to_rad(PITCH_LIMIT))
		_talk_tween.tween_property(self, ^"rotation:y", rotation.y + wrapf(yaw - rotation.y, -PI, PI), TALK_TURN_TIME)
		_talk_tween.tween_property(head, ^"rotation:x", pitch, TALK_TURN_TIME)
	_talk_tween.tween_property(self, ^"zoom", TALK_ZOOM, TALK_TURN_TIME)
	_talk_tween.chain().tween_callback(func() -> void: _talk_turning = false)
	_talk_tween.chain().tween_interval(TALK_HOLD if watch == null else TALK_WATCH)
	_talk_tween.chain().tween_callback(func() -> void:
		_talk_glance = false
		_talk_watch = null)
	_talk_tween.tween_property(self, ^"zoom", 0.0, TALK_TURN_TIME)


## His view comes off their face before its time: he looked away.
func _let_go_of_face() -> void:
	_talk_glance = false
	_talk_watch = null
	if _talk_tween:
		_talk_tween.kill()
	_talk_tween = create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	_talk_tween.tween_property(self, ^"zoom", 0.0, TALK_TURN_TIME)


## Lets his view go: the conversation is over, or he walked away.
func end_talk() -> void:
	if not talking:
		return
	talking = false
	_talk_turning = false
	_talk_glance = false
	_talk_watch = null
	if _talk_tween:
		_talk_tween.kill()
	_talk_tween = create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	_talk_tween.tween_property(self, ^"zoom", 0.0, TALK_TURN_TIME)


## Talking: he stands still, and a move key walks him away; not the keys
## he walked up with, until he has let go of them.
func _stand_and_talk(delta: float) -> void:
	stamina.update(false, delta)
	var wish := input_override if use_input_override else Input.get_vector(
		&"move_left", &"move_right", &"move_back", &"move_forward")
	if wish.length() < 0.2:
		_talk_still = true
	elif wish.length() > 0.5 and _talk_still and not controls_locked:
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


## Puts his eye to `squint`, from whichever side he's on.
func peek(squint: Squint) -> void:
	if busy() or _hide_moving:
		return
	peeking = squint
	_peek_from = global_transform
	_hide_moving = true
	velocity = Vector3.ZERO
	var eye := squint.eye_for(global_position)
	var look := -eye.basis.z
	_hide_yaw = atan2(-look.x, -look.z)
	_hide_pitch = 0.0
	var tween := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tween.tween_property(self, ^"global_position", eye.origin - Vector3.UP * EYE_HEIGHT, HIDE_TIME)
	tween.tween_property(self, ^"rotation:y", rotation.y + wrapf(_hide_yaw - rotation.y, -PI, PI), HIDE_TIME)
	tween.tween_property(head, ^"rotation:x", 0.0, HIDE_TIME)
	tween.chain().tween_callback(func() -> void: _hide_moving = false)


## Steps back from the squint.
func stop_peeking() -> void:
	if peeking == null:
		return
	_hide_moving = true
	var tween := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tween.tween_property(self, ^"global_position", _peek_from.origin, HIDE_TIME)
	tween.tween_callback(func() -> void:
		peeking = null
		_hide_moving = false)


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
	# A step back. Less motion: half the tip and the drop.
	var k := 0.5 if Settings.less_motion else 1.0
	velocity = global_basis.z * 1.2
	var tween := create_tween().set_trans(Tween.TRANS_SINE)
	tween.set_parallel()
	tween.tween_property(head, ^"rotation:z", 0.35 * k, seconds * 0.3).set_ease(Tween.EASE_OUT)
	tween.tween_property(self, ^"_eye", EYE_HEIGHT - 0.5 * k, seconds * 0.3).set_ease(Tween.EASE_OUT)
	tween.tween_property(head, ^"rotation:x", deg_to_rad(-25.0 * k), seconds * 0.3)
	tween.chain().tween_property(head, ^"rotation:z", 0.0, seconds * 0.7).set_ease(Tween.EASE_IN_OUT)
	tween.tween_property(self, ^"_eye", EYE_HEIGHT, seconds * 0.7).set_ease(Tween.EASE_IN_OUT)
	tween.chain().tween_callback(func() -> void: stumbling = false)


## What he holds to throw, or empty.
static func held() -> StringName:
	for id in GameState.satchel:
		if Items.kind(id) == &"throwable":
			return id
	return &""


## Throws what he holds, from his right hand along his view. Returns it.
func throw() -> Thrown:
	var what := held()
	if what == &"" or busy():
		return null
	GameState.satchel.erase(what)
	var t := Thrown.new()
	t.item = what
	get_parent().add_child(t)
	var forward := -camera.global_basis.z
	t.global_position = camera.global_position + forward * 0.4 + camera.global_basis.x * 0.2 - Vector3.UP * 0.1
	t.linear_velocity = (forward + Vector3.UP * Thrown.LOFT).normalized() * Thrown.SPEED
	return t


## Lying on his back, looking up (waking in the infirmary).
func lie_down() -> void:
	_eye = 0.7
	head.position = Vector3(0.0, _eye, 0.0)
	head.rotation = Vector3(deg_to_rad(60.0), 0.0, 0.0)


## Falls dead: the view drops to the floor and rolls; await it.
func fall_dead(seconds: float) -> void:
	velocity = Vector3.ZERO
	var tween := create_tween().set_parallel().set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tween.tween_property(self, ^"_eye", 0.25, seconds)
	tween.tween_property(head, ^"position:y", 0.25, seconds)
	tween.tween_property(head, ^"rotation:z", deg_to_rad(80.0), seconds)
	tween.tween_property(head, ^"rotation:x", deg_to_rad(-10.0), seconds)
	await tween.finished


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
	peeking = null
	_hide_moving = false
	global_position = at
	velocity = Vector3.ZERO
	rotation = Vector3(0.0, yaw, 0.0)
	head.rotation = Vector3.ZERO
	lean = 0.0
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
	if Settings.less_motion:
		target_amp = 0.0
	_bob_amp = move_toward(_bob_amp, target_amp, delta * 0.2)
	var stride := lerpf(STRIDE_WALK, STRIDE_RUN, t)
	var before := floori(_bob_phase / PI)
	_bob_phase += speed * delta / stride * PI
	if floori(_bob_phase / PI) != before and speed > 0.3:
		stepped.emit(floor_surface, running)
	# The head dips once per step and sways once per two; crouching lowers
	# it, leaning moves it aside and tilts it.
	head.position = Vector3(
		_bob_amp * 0.5 * sin(_bob_phase) + LEAN_OFFSET * lean,
		_stand_eye() - _bob_amp * (1.0 - cos(2.0 * _bob_phase)) * 0.5,
		0.0)
	if not stumbling:
		head.rotation.z = -deg_to_rad(LEAN_TILT) * lean


## Drunk (3 ales and more), the view drifts a little (none with less motion).
func _drift() -> void:
	var k := DoseDriver.drunk_amount() if not Settings.less_motion else 0.0
	var t := Time.get_ticks_msec() / 1000.0
	look_back_pivot.rotation.z = sin(t * 0.43) * 0.035 * k
	look_back_pivot.rotation.x = sin(t * 0.31 + 1.0) * 0.02 * k


func _update_look_back(delta: float) -> void:
	_drift()
	var looking := Input.is_action_pressed(&"look_back") and not busy()
	_look_back = move_toward(_look_back, 1.0 if looking else 0.0, delta / LOOK_BACK_TIME)
	look_back_pivot.rotation.y = deg_to_rad(LOOK_BACK_ANGLE) * smoothstep(0.0, 1.0, _look_back)
