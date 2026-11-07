class_name Player
extends CharacterBody3D
## The porter, Brother Alric (Look and Feel, "Camera and player feel"): a
## 1.4 m/s walk, a 4 m/s run, gentle head bob that gets heavier when running,
## mouse look, and looking back over the shoulder while `look_back` is held.
## The lantern, interaction, footsteps and breath are child nodes.
##
## Esc frees the mouse; a click captures it again.

signal stepped(surface: String, running: bool)

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

## Tests and scripted moments drive the player through these instead of the
## keyboard: x right, y forward, as from Input.get_vector().
var input_override := Vector2.ZERO
var use_input_override := false
var run_override := false

var running := false
var crawling := false
## What the floor underfoot sounds like.
var floor_surface := "stone"

var _bob_phase := 0.0
var _bob_amp := 0.0
var _look_back := 0.0

@onready var head: Node3D = $Head
@onready var look_back_pivot: Node3D = $Head/LookBack
@onready var camera: Camera3D = $Head/LookBack/Camera
@onready var _collision: CollisionShape3D = $Collision


func _ready() -> void:
	add_to_group(&"player")
	collision_layer = Layers.CAPSULE
	collision_mask = Layers.MASK_PLAYER
	if DisplayServer.get_name() != "headless":
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func _unhandled_input(event: InputEvent) -> void:
	var motion := event as InputEventMouseMotion
	if motion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		rotate_y(-motion.relative.x * MOUSE_SENSITIVITY)
		var pitch := head.rotation.x - motion.relative.y * MOUSE_SENSITIVITY
		head.rotation.x = clampf(pitch, -deg_to_rad(PITCH_LIMIT), deg_to_rad(PITCH_LIMIT))
	elif event.is_action_pressed(&"ui_cancel"):
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	elif event is InputEventMouseButton and event.is_pressed() and Input.mouse_mode != Input.MOUSE_MODE_CAPTURED:
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
		get_viewport().set_input_as_handled()


func _physics_process(delta: float) -> void:
	_update_look_back(delta)
	if crawling:
		return
	var input := input_override if use_input_override else Input.get_vector(
		&"move_left", &"move_right", &"move_back", &"move_forward")
	var run_held := run_override if use_input_override else Input.is_action_pressed(&"run")
	running = run_held and input.length() > 0.1
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


## Crawls through `points` (feet positions) over `seconds`, eyes at
## `eye_height`, ignoring collisions; control comes back at the end.
func crawl_along(points: Array[Vector3], seconds: float, eye_height: float) -> void:
	if crawling or points.is_empty():
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
		EYE_HEIGHT - _bob_amp * (1.0 - cos(2.0 * _bob_phase)) * 0.5,
		0.0)


func _update_look_back(delta: float) -> void:
	var held := Input.is_action_pressed(&"look_back") and not crawling
	_look_back = move_toward(_look_back, 1.0 if held else 0.0, delta / LOOK_BACK_TIME)
	look_back_pivot.rotation.y = deg_to_rad(LOOK_BACK_ANGLE) * smoothstep(0.0, 1.0, _look_back)
