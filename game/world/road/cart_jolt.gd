class_name CartJolt
extends Node3D
## A cart's bed going over a rough road: put the bed and everything that
## rides on it (the cart, its load, the seats) under this node, and carry the
## cart's root along. Each wheel runs over its own ruts and stones; the bed
## follows them on a spring, so it jolts, sways side to side as one wheel
## drops before the other, and tips about the horse's back, which holds the
## shafts up. Faster is rougher; standing, it settles. The horse isn't under
## it. Riders sitting on a seat under it go with it (Player.riding).
##
## The road is the same every time it's driven: it is made from how far the
## cart has gone. With less motion it is a third as rough.

## How rough the road is: 1 a rutted country road.
@export var roughness := 1.0
## Metres between the wheels, and from the axle forward to the horse's back.
@export var track := 1.5
@export var shafts := 2.4
## The bed's spring: how quick it bounces (Hz), and how soon it settles (0 to 1).
@export var bounce_hz := 2.4
@export var damping := 0.3
## A different road for a different cart.
@export var seed_offset := 0

## The road under each wheel, m: long swells, short judder, and now and then a stone or a rut.
const SWELL := 0.04
const JUDDER := 0.01
const STONE := 0.08

var _last := Vector3.ZERO
var _along := 0.0
var _noise: Array[FastNoiseLite] = []
## Each wheel's corner of the bed: height and its speed.
var _y := [0.0, 0.0]
var _v := [0.0, 0.0]


func _ready() -> void:
	for i in 6:
		var n := FastNoiseLite.new()
		n.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
		n.seed = 11 + i * 37 + seed_offset
		n.frequency = [0.9, 4.0, 0.7][i % 3]
		_noise.append(n)
	_last = _root().global_position


func _physics_process(delta: float) -> void:
	if delta <= 0.0:
		return
	var root := _root()
	var moved := (root.global_position - _last).dot(-root.global_basis.z)
	_last = root.global_position
	# Carried a long way in a moment (the ride's cut through the dark): no jolt for it.
	if absf(moved) < 2.0:
		_along += absf(moved)
	var rough := roughness * (0.33 if Settings.less_motion else 1.0)
	var w := TAU * bounce_hz
	for wheel in 2:
		var ground := _ground(wheel) * rough
		var a: float = w * w * (ground - float(_y[wheel])) - 2.0 * damping * w * float(_v[wheel])
		_v[wheel] = float(_v[wheel]) + a * delta
		_y[wheel] = float(_y[wheel]) + float(_v[wheel]) * delta
	var left := float(_y[0])
	var right := float(_y[1])
	var mid := (left + right) * 0.5
	position.y = mid
	# The right side up tips the bed to its left; the axle up, with the horse
	# holding the front, tips its back up.
	rotation.z = atan2(right - left, track)
	rotation.x = -atan2(mid, shafts)


## The road's height under a wheel (0 left, 1 right) where the cart is now.
func _ground(wheel: int) -> float:
	var s := _along
	var off := wheel * 3
	var stone := maxf(0.0, _noise[off + 2].get_noise_1d(s) - 0.35) / 0.65
	return _noise[off].get_noise_1d(s) * SWELL + _noise[off + 1].get_noise_1d(s) * JUDDER + stone * stone * STONE


## The cart this bed belongs to: what is carried along.
func _root() -> Node3D:
	var p := get_parent() as Node3D
	return p if p else self
