extends NightBeat
## The road in (design doc, night 0; docs/prologue.md, "The ride"): on rails,
## the carter's wagon drives itself from the fields past the white chapel,
## through Aldgate, along the close streets and into the lane, about two
## minutes. The porter rides at the back and can look about. The traveller
## beside him turns to him as they set off, and he can talk to the traveller
## again whenever he likes. The RideCues along the road play as the wagon
## passes them: lines, talks, sounds, a new pace, a stop at the city gate.
## Early on the carter pulls in (his "Whoa" breaks off any talk) to let a
## cart go by the other way with a covered body on it (the hook): the
## porter's view goes to the body and follows it by, and the traveller talks
## about it. The night comes up out of black as the wagon sets off. On the
## bridge over the brook, once the talk is done, it goes dark, and comes up
## again in the lane as the wagon reaches the abbey gate. It ends when the
## carter sets him down there and drives off down the lane.

## The wagon (its Seat, TravellerSeat and CarterSeat markers), and the road.
@export var wagon: Node3D
@export var path: Node3D
## m/s along the road at the start; RideCues change it.
@export var speed := 3.5
## m/s² speeding up and slowing down.
@export var accel := 1.2
## Every pace and hold is scaled by this (tests drive faster).
@export var pace_scale := 1.0
## The RideCues along the road.
@export var cues: Node3D
## The cart with the body, where the carter pulls in to let it by, and how
## fast it comes. It starts `cart_lead` m past the spot.
@export var body_cart: Node3D
@export var pull_over: Marker3D
@export var cart_speed := 2.0
@export var cart_lead := 40.0
## Where the carter sets him down, and the traveller, and the carter's look.
@export var set_down: Marker3D
@export var traveller: Node3D
@export var carter: Node3D
## Seconds the night takes to come up out of black as the wagon sets off.
@export var fade_in := 3.5
## Where the night goes dark on the road (the bridge over the brook: the
## talk of the road is over), and where it comes up again (the lane, as the
## wagon comes to the abbey gate). The road between isn't ridden.
@export var dark_at: Marker3D
@export var light_at: Marker3D
## Seconds it takes to go dark, stays dark, and takes to come up again.
@export var dark_fade := 2.5
@export var dark_hold := 1.2
## Metres the wagon drives on down the lane after it, out of sight.
@export var drive_off := 45.0
## The abbey gate: barred tonight, nobody keeps it; Cole isn't at it.
@export var gate: AbbeyGate
@export var cole: VisitorNPC
## What the traveller says as the body goes by, and the carter at the gate.
@export var traveller_talk: Conversation
@export var carter_talk: Conversation

const RUMBLE := preload("res://art/sfx/amb_wagon_loop.wav")
## The wagon's place across the road: its right of the middle, more when it
## pulls in. The body cart keeps to its own right.
const SIDE := 1.2
const PULLED_IN := 1.7
const CART_SIDE := 1.2
## The cart waits this far off until the wagon has pulled in.
const CART_WAIT := 9.0
## Slowest the wagon rolls toward a stop, so it gets there.
const CREEP := 0.3

var _points: Array[Vector3] = []
var _length := 0.0
var _along := 0.0
var _v := 0.0
## The pace now, m/s (before pace_scale).
var _pace := 0.0
var _side := SIDE
var _riding := false
## Cues in order along the road; the next to pass; lines waiting to be said.
var _cues: Array[RideCue] = []
var _next := 0
var _queue: Array[RideCue] = []
var _speaking := false
## No new lines from the cues for now (the cart is coming).
var _hush := false
var _held: Array[RideCue] = []
var _pull_along := INF
var _dark_along := INF
var _light_along := INF
var _crossed := false
var _pulled_in := false
var _hook_done := false
var _cart_along := INF
var _rumble: AudioStreamPlayer3D


func _ready() -> void:
	gate.swing.call_deferred(false)
	gate.show_bar.call_deferred(true)
	if cole:
		cole.set_present.call_deferred(false)


func run() -> void:
	var p := player()
	# It opens on black and comes up as the wagon rolls.
	await fade_to(1.0, 0.0)
	_points = points(path)
	_length = _length_of(_points)
	_gather_cues()
	if pull_over and body_cart:
		_pull_along = _along_of(pull_over.global_position)
		_cart_along = _pull_along + cart_lead
	else:
		_hook_done = true
	if dark_at and light_at:
		_dark_along = _along_of(dark_at.global_position)
		_light_along = _along_of(light_at.global_position)
	GameState.set_flag(&"n0_riding")
	_seat(p)
	if AudioOut.enabled():
		_rumble = AudioStreamPlayer3D.new()
		_rumble.stream = AudioOut.looped(RUMBLE)
		_rumble.volume_db = -6.0
		wagon.add_child(_rumble)
		_rumble.play()
	_pace = speed
	_v = _pace * pace_scale
	_riding = true
	fade_to(0.0, fade_in / pace_scale)
	_speak.call()
	_watch.call()
	while true:
		var dt := PlayTime.physics(self)
		_pass_cues()
		var stop := _next_stop()
		var d := stop - _along
		var target := minf(_pace * pace_scale, sqrt(2.0 * accel * maxf(d, 0.0)))
		if not _crossed and _along >= _dark_along:
			if Talk.quiet() and not _speaking and _queue.is_empty():
				_crossed = true
				await _through_the_dark()
				continue
			# Still talking on the bridge: the carter lets the horse stand.
			_v = move_toward(_v, 0.0, accel * dt)
		else:
			_v = move_toward(_v, maxf(target, CREEP * pace_scale), accel * dt)
		_along = minf(_along + _v * dt, stop)
		if not _hook_done:
			# Pulls in toward the ditch over the last 15 m.
			_side = lerpf(SIDE, PULLED_IN, clampf(1.0 - (_pull_along - _along) / 15.0, 0.0, 1.0))
		else:
			_side = move_toward(_side, SIDE, 0.25 * dt * pace_scale)
		_place(wagon, _along, _side)
		if _rumble:
			_rumble.volume_db = -6.0 + linear_to_db(clampf(_v / (2.0 * pace_scale), 0.08, 1.0))
		if _along >= stop - 0.01:
			_v = 0.0
			if stop == _pull_along and not _hook_done:
				await _let_the_cart_by()
				_hook_done = true
			elif stop < _length - 0.01:
				var cue := _hold_here()
				await _hold_at(cue)
				_held.append(cue)
			else:
				break
		await PlayTime.physics_frame(self)
	# Set down once nobody's talking and the road's lines are said.
	await until(func() -> bool: return Talk.quiet() and not _speaking and _queue.is_empty())
	_riding = false
	p.riding = null
	p.place(set_down.global_position, set_down.global_rotation.y)
	GameState.flags.erase(&"n0_riding")
	GameState.set_flag(&"n0_arrived")
	if body_cart:
		body_cart.queue_free()
	if carter_talk and carter:
		await Talk.converse(carter_talk, carter)
	# The carter drives off down the lane, and the traveller with him.
	_drive_off.call()


## The night goes dark as the wagon rolls on off the bridge, and comes up
## again in the lane with the gate a little way ahead. What the cues between
## would have said is left unsaid.
func _through_the_dark() -> void:
	_hush = true
	fade_to(1.0, dark_fade / pace_scale)
	var left := dark_fade / pace_scale
	while left > 0.0:
		var dt := PlayTime.physics(self)
		left -= dt
		_along += _v * dt
		_place(wagon, _along, _side)
		await PlayTime.physics_frame(self)
	_along = _light_along
	_side = SIDE
	while _next < _cues.size() and _cues[_next].along < _light_along:
		_next += 1
	_queue.clear()
	_place(wagon, _along, _side)
	await wait(dark_hold / pace_scale)
	_hush = false
	fade_to(0.0, dark_fade / pace_scale)


## Seats him and the traveller and the carter on the wagon.
func _seat(p: Player) -> void:
	_place(wagon, 0.0, SIDE)
	var seat := wagon.get_node(^"Seat") as Marker3D
	p.place(seat.global_position, seat.global_rotation.y)
	p.riding = seat
	traveller.reparent(wagon.get_node(^"TravellerSeat"), false)
	traveller.position = Vector3.ZERO
	traveller.rotation = Vector3.ZERO
	if carter:
		carter.reparent(wagon.get_node(^"CarterSeat"), false)
		carter.position = Vector3.ZERO
		carter.rotation = Vector3.ZERO


func _gather_cues() -> void:
	if cues == null:
		return
	for c in cues.get_children():
		if c is RideCue:
			(c as RideCue).along = _along_of((c as RideCue).global_position)
			_cues.append(c)
	_cues.sort_custom(func(a: RideCue, b: RideCue) -> bool: return a.along < b.along)


## The cues the wagon has reached: sounds now, lines to the queue, new paces.
func _pass_cues() -> void:
	while _next < _cues.size() and _cues[_next].along <= _along + 0.01:
		var cue := _cues[_next]
		_next += 1
		if cue.pace > 0.0:
			_pace = cue.pace
		if cue.sound and AudioOut.enabled():
			var a := AudioStreamPlayer3D.new()
			a.stream = cue.sound
			a.volume_db = cue.volume_db
			cue.add_child(a)
			a.play()
			a.finished.connect(a.queue_free)
		if cue.hold <= 0.0 and cue.cut_in:
			# What was waiting to be said is past now.
			Talk.interrupt()
			_queue.clear()
			_queue.append(cue)
		elif cue.hold <= 0.0 and (not cue.lines.is_empty() or cue.talk):
			_queue.append(cue)


## Where the wagon must stop next: the pull-over, a cue that holds, the end.
func _next_stop() -> float:
	var stop := _length
	if not _hook_done:
		stop = minf(stop, _pull_along)
	var cue := _hold_here()
	if cue:
		stop = minf(stop, cue.along)
	return stop


## The next cue the wagon stops at, or null.
func _hold_here() -> RideCue:
	for c in _cues:
		if c.hold > 0.0 and not _held.has(c):
			return c
	return null


## Says the cues' lines in turn, and starts their talks, while nobody's
## talking; drops those the wagon has left behind, and stops one short if a
## talk begins.
func _speak() -> void:
	while _riding:
		if _queue.is_empty() or _hush or not Talk.quiet():
			await PlayTime.physics_frame(self)
			continue
		var cue: RideCue = _queue.pop_front()
		if _along > cue.along + cue.keep:
			continue
		_speaking = true
		await _say_unless_talking(cue.lines)
		if cue.talk and cue.talker and not Talk.talking and not _hush:
			# Not while he can't talk (the chapter card still up).
			await until(func() -> bool: return not player().busy() or Talk.talking or _hush)
			if not Talk.talking and not _hush:
				await Talk.converse(cue.talk, cue.talker)
		_speaking = false


func _say_unless_talking(lines: PackedStringArray) -> void:
	for line in lines:
		if Talk.talking:
			return
		await say_lines(PackedStringArray([line]))


## The cart: comes on down the road, waits short of the wagon until it has
## pulled in, then goes by. People at the cues turn to watch the wagon.
func _watch() -> void:
	while _riding:
		var dt := PlayTime.physics(self)
		if is_instance_valid(body_cart) and _cart_along < INF:
			var floor_at := -INF if _pulled_in else _pull_along + CART_WAIT
			_cart_along = maxf(_cart_along - cart_speed * pace_scale * dt, floor_at)
			_place(body_cart, maxf(_cart_along, 0.0), CART_SIDE, true)
		for c in _cues:
			for w in c.watchers:
				if is_instance_valid(w) and w.has_method(&"face") and w.global_position.distance_to(wagon.global_position) < 15.0:
					w.call(&"face", wagon.global_position)
		await PlayTime.physics_frame(self)


## Stopped at the side of the road: the traveller breaks off, the cart comes
## by close on his side, and the traveller talks about it as the wagon goes on.
func _let_the_cart_by() -> void:
	_hush = true
	Talk.interrupt()
	await until(func() -> bool: return not _speaking)
	_pulled_in = true
	await until(func() -> bool: return _cart_along < _pull_along + 6.0)
	_hook.call()
	_hush = false
	await until(func() -> bool: return _cart_along < _pull_along - 4.0)


func _hook() -> void:
	if traveller_talk == null:
		return
	Talk.interrupt()
	# His eyes go to what is on the cart, not to the man beside him.
	var body: Node3D = body_cart.get_node_or_null(^"ShroudedBody") if is_instance_valid(body_cart) else null
	await Talk.converse(traveller_talk, traveller, body if body else body_cart)


## Stopped at a cue: once nobody's talking, its lines, then it stands a while.
func _hold_at(cue: RideCue) -> void:
	await until(func() -> bool: return Talk.quiet() and not _speaking)
	_speaking = true
	await _say_unless_talking(cue.lines)
	_speaking = false
	await wait(cue.hold / pace_scale)


## On down the lane, out of sight; then gone.
func _drive_off() -> void:
	var to := _length + drive_off
	var v := 0.0
	while is_instance_valid(wagon) and _along < to:
		var dt := PlayTime.physics(self)
		v = move_toward(v, 2.0 * pace_scale, accel * dt)
		_along += v * dt
		_place(wagon, _along, SIDE)
		await PlayTime.physics_frame(self)
	if is_instance_valid(wagon):
		wagon.queue_free()


## Puts `node` `along` metres down the road, `side` m to its right (facing
## the way it goes, or back up it with `reverse`).
func _place(node: Node3D, along: float, side: float, reverse := false) -> void:
	var at := _at(along)
	# Heading from 1.5 m behind to 1.5 m ahead: corners are taken in a curve.
	var dir := (_at(along + 1.5) - _at(along - 1.5)).normalized() * (-1.0 if reverse else 1.0)
	var right := dir.cross(Vector3.UP).normalized()
	node.global_transform = Transform3D(Basis.looking_at(dir, Vector3.UP), at + right * side)


## The point `along` metres down the road; past its end, straight on.
func _at(along: float) -> Vector3:
	var left := along
	for i in range(1, _points.size()):
		var seg := _points[i - 1].distance_to(_points[i])
		if left <= seg:
			return _points[i - 1].lerp(_points[i], left / maxf(seg, 0.001))
		left -= seg
	return _points[-1] + (_points[-1] - _points[-2]).normalized() * left


## How far along the road the point nearest `at` is.
func _along_of(at: Vector3) -> float:
	var best := INF
	var best_along := 0.0
	var walked := 0.0
	for i in range(1, _points.size()):
		var a := _points[i - 1]
		var b := _points[i]
		var seg := a.distance_to(b)
		var k := clampf((at - a).dot(b - a) / maxf(seg * seg, 0.0001), 0.0, 1.0)
		var d := at.distance_to(a.lerp(b, k))
		if d < best:
			best = d
			best_along = walked + k * seg
		walked += seg
	return best_along


static func _length_of(pts: Array[Vector3]) -> float:
	var l := 0.0
	for i in range(1, pts.size()):
		l += pts[i - 1].distance_to(pts[i])
	return l
