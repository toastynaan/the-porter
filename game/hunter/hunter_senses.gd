class_name HunterSenses
extends Node3D
## The hunter's eyes and ears, at eye height (design doc, "The hunter is a
## man": he needs light to see you). Within his 100° view he sees the porter's
## head or chest (Player.sight_points: a leaning head shows past a corner, a
## crouched porter hides behind anything 1 m high) out to LIT_RANGE when the
## porter is lit (lantern uncovered, or standing in a candle's light), and
## only within DARK_RANGE when he isn't. Never in a hiding spot. Noticing takes a moment, longer the further away; once he is
## `focused` (chasing) it is instant.
##
## He hears every Noise within its radius, half that through a wall, double
## while he stands `listening` (winded). (M2 report defaults.)

signal heard(at: Vector3, source: Node)

const FOV := 100.0
const LIT_RANGE := 20.0
const DARK_RANGE := 2.0
## Seconds to notice a lit porter right in front, and at LIT_RANGE.
const NOTICE_NEAR := 0.3
const NOTICE_FAR := 1.5
## How fast awareness falls away when he can't see, per second.
const FORGET_RATE := 0.5

## Chasing: no noticing delay, and he keeps his eyes on you.
var focused := false
var listening := false
## 0..1; at 1 he has seen the porter.
var awareness := 0.0
## Seen this physics frame.
var sees_player := false
## Glimpsed this frame but not noticed yet.
var glimpsed := false

var _player: Player


func _ready() -> void:
	add_to_group(&"listeners")


## Forgets everything he has seen (a reset).
func forget() -> void:
	awareness = 0.0
	sees_player = false
	glimpsed = false
	focused = false
	listening = false


func _physics_process(delta: float) -> void:
	if _player == null or not is_instance_valid(_player):
		_player = get_tree().get_first_node_in_group(&"player") as Player
	glimpsed = _player != null and (can_see(_player) or _glow_in_fog(_player))
	if glimpsed:
		var d := global_position.distance_to(_player.camera.global_position)
		var notice := lerpf(NOTICE_NEAR, NOTICE_FAR, clampf(d / LIT_RANGE, 0.0, 1.0))
		awareness = 1.0 if focused else minf(awareness + delta / notice, 1.0)
	else:
		awareness = maxf(awareness - FORGET_RATE * delta, 0.0)
	sees_player = glimpsed and awareness >= 1.0 and _player != null and can_see(_player)


## In the fog an uncovered lantern is a glowing ball he can make out from
## Weather.LANTERN_GLOW off, though he can't see the porter: enough to come
## and look (a glimpse), not to chase.
func _glow_in_fog(player: Player) -> bool:
	if Weather.now(get_tree()) != Weather.Kind.FOG or player.lantern.covered or player.hiding:
		return false
	var at := player.lantern.global_position
	var to := at - global_position
	var forward := -global_basis.z
	return to.length() < Weather.LANTERN_GLOW and to.length() > Weather.FOG_SIGHT \
		and rad_to_deg(Vector3(forward.x, 0, forward.z).angle_to(Vector3(to.x, 0, to.z))) < FOV * 0.5 \
		and ViewCheck.clear(self, global_position, at)


## Whether the porter is in view now, by the light rules.
func can_see(player: Player) -> bool:
	return sees_from(self, global_position, -global_basis.z, player)


## The sight rules for anyone (a hunter, a brother): from `eye`, looking
## along `forward`, can he see the porter? His head (aside, if he leans; low,
## if he crouches) or his chest, in the 100° view, out to LIT_RANGE when the
## porter is lit and DARK_RANGE when he isn't, with nothing solid between.
static func sees_from(from: Node3D, eye: Vector3, forward: Vector3, player: Player) -> bool:
	if player.hiding:
		return false
	var points := player.sight_points()
	var d := eye.distance_to(points[0])
	if d > Weather.sight(from.get_tree(), LIT_RANGE if is_lit(player) else DARK_RANGE):
		return false
	var to := points[0] - eye
	if d > 1.0 and rad_to_deg(Vector3(forward.x, 0, forward.z).angle_to(Vector3(to.x, 0, to.z))) > FOV * 0.5:
		return false
	return points.any(func(p: Vector3) -> bool: return ViewCheck.clear(from, eye, p))


## Lit: his lantern is uncovered, or a lit candle is close enough to show him.
static func is_lit(player: Player) -> bool:
	if not player.lantern.covered:
		return true
	for candle: Candle in player.get_tree().get_nodes_in_group(&"candles"):
		if candle.lit and candle.global_position.distance_to(player.global_position + Vector3.UP) < candle.light.omni_range:
			return true
	return false


func hear(at: Vector3, radius: float, source: Node) -> void:
	if source == owner:
		return
	var r := radius * (2.0 if listening else 1.0) * Weather.hearing_factor(get_tree())
	var d := global_position.distance_to(at)
	if d > r:
		return
	if d > r * 0.5 and not ViewCheck.clear(self, global_position, at):
		return
	heard.emit(at, source)
