class_name LanternHand
extends Node3D
## Holds the lantern low in the left hand, always in view (Look and Feel,
## "Camera and player feel"). The hand follows the head's pitch only partly,
## the lantern hangs straight down and swings like a pendulum from the hand's
## movement (its swing is the main motion on screen; much less with the less
## motion setting), and holding
## `cover_lantern` tucks it under the cloak (so does hiding: `force_cover`).
## Hunger shakes the hand (Look and Feel, "Hunger": hand tremor on the
## lantern); `tremor` adds more for scripted moments.
##
## He may not have it at all (`owned`: night 0; he's given it on day 1), and
## he can put it away in his satchel and take it out again (`stow_lantern`,
## docs/systems/mechanics.md, "Your hands"). Put away, it gives no light and
## shows nothing; the hunters see an unlit man. Some places make him put it
## away while he's in them (LanternAway: the Cross Keys), and he takes it out
## again as he leaves if he had it out before.

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
## He has a lantern (GameState flag has_lantern; NightDirector sets it).
var owned := true:
	set(value):
		owned = value
		_show()
## In his hand, not put away in the satchel.
var held := true:
	set(value):
		held = value
		_show()
## Places that have made him put it away (LanternAway) while he's in them.
var _away_in: Array[Node] = []
## Whether it was out when the first such place put it away.
var _held_before_away := true

signal changed


## In his hand and giving light (owned, out, and nowhere has put it away).
func showing() -> bool:
	return owned and held and _away_in.is_empty()


## Puts it away or takes it out (`stow_lantern`). Nothing while a place has
## made him put it away, or if he has none.
func toggle() -> void:
	if not owned or not _away_in.is_empty():
		return
	held = not held


## A place makes him put it away while he's in it (the Keys' rooms).
func put_away_for(place: Node) -> void:
	if _away_in.has(place):
		return
	if _away_in.is_empty():
		_held_before_away = held
	_away_in.append(place)
	_show()


## He leaves that place: out again if it was out before.
func release(place: Node) -> void:
	_away_in.erase(place)
	if _away_in.is_empty():
		held = _held_before_away
	_show()


func _show() -> void:
	visible = showing()
	changed.emit()

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
	# Put away (or none at all): covered too, so nothing counts him lit.
	var cover := force_cover or not showing() or Input.is_action_pressed(&"cover_lantern")
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
	if Settings.less_motion:
		_swing = _swing * 0.2
	pivot.global_basis = yaw * Basis.from_euler(Vector3(_swing.x, 0.0, _swing.y))
