class_name LanternHand
extends Node3D
## Holds the lantern low in the left hand, always in view (Look and Feel,
## "Camera and player feel"). The hand follows the head's pitch only partly,
## the lantern hangs straight down and swings like a pendulum from the hand's
## movement (its swing is the main motion on screen), and holding
## `cover_lantern` tucks it under the cloak (so does hiding: `force_cover`).
## Hunger shakes the hand (Look and Feel, "Hunger": hand tremor on the
## lantern); `tremor` adds more for scripted moments.

## Hand position relative to the head, held and tucked under the cloak.
const HOLD := Vector3(-0.22, -0.22, -0.52)
const TUCKED := Vector3(-0.1, -0.62, -0.26)
## Hiding: held close under the chin, so its glow stays inside the spot.
const HIDDEN := Vector3(-0.08, -0.14, -0.2)
## How much of the head's pitch the hand follows.
const PITCH_FOLLOW := 0.6
## Lantern length from handle to centre, m: sets the swing's period.
const PENDULUM_LENGTH := 0.15
const SWING_DAMPING := 3.0
const SWING_LIMIT := 0.7
const TUCK_TIME := 0.3
## Tremor amplitude at tremor 1, m.
const TREMOR_SIZE := 0.008

## Extra hand tremor, 0..1, on top of hunger's.
@export var tremor := 0.0

## Keeps the lantern covered whatever the player holds (hiding).
var force_cover := false

var _swing := Vector2.ZERO
var _swing_vel := Vector2.ZERO
var _prev_pos := Vector3.ZERO
var _prev_vel := Vector3.ZERO
var _tuck := 0.0
var _noise := FastNoiseLite.new()
var _t := 0.0

@onready var pivot: Node3D = $Pivot
@onready var lantern: Lantern = $Pivot/Lantern
@onready var _head: Node3D = get_parent()


func _ready() -> void:
	_noise.frequency = 2.0
	_prev_pos = global_position


func _process(delta: float) -> void:
	delta = clampf(delta, 0.001, 1.0 / 30.0)
	_t += delta
	var cover := force_cover or Input.is_action_pressed(&"cover_lantern")
	if cover != lantern.covered:
		lantern.covered = cover
	_tuck = move_toward(_tuck, 1.0 if lantern.covered else 0.0, delta / TUCK_TIME)
	var unpitch := Basis(Vector3.RIGHT, _head.rotation.x * (PITCH_FOLLOW - 1.0))
	var jitter := Vector3(_noise.get_noise_1d(_t * 40.0), _noise.get_noise_1d(_t * 40.0 + 70.0), 0.0)
	var shake := maxf(tremor, 1.0 if GameState.is_hungry() else 0.0)
	var tucked := HIDDEN if force_cover else TUCKED
	position = unpitch * HOLD.lerp(tucked, smoothstep(0.0, 1.0, _tuck)) + jitter * TREMOR_SIZE * shake
	basis = unpitch
	_update_swing(delta)


## A pendulum hanging from the hand: the hand's acceleration in the body's
## frame pushes the lantern the other way, gravity pulls it back.
func _update_swing(delta: float) -> void:
	var pos := global_position
	var vel := (pos - _prev_pos) / delta
	var acc := (vel - _prev_vel) / delta
	_prev_pos = pos
	_prev_vel = vel
	var yaw := Basis(Vector3.UP, _head.global_rotation.y)
	var a := yaw.inverse() * acc
	var omega2 := 9.8 / PENDULUM_LENGTH
	var push := Vector2(a.z, -a.x) / PENDULUM_LENGTH
	_swing_vel += (-omega2 * _swing - SWING_DAMPING * _swing_vel + push) * delta
	_swing = (_swing + _swing_vel * delta).clamp(Vector2(-SWING_LIMIT, -SWING_LIMIT), Vector2(SWING_LIMIT, SWING_LIMIT))
	pivot.global_basis = yaw * Basis.from_euler(Vector3(_swing.x, 0.0, _swing.y))
