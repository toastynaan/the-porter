extends NightBeat
## The road in (design doc, night 0; docs/mechanics.md, "The ride in"): on
## rails, the carter's wagon drives itself from the fields past the white
## chapel, through Aldgate, along the close streets and into the lane, about
## three minutes. In the first minute it pulls aside for a cart coming the
## other way with a covered body on it (the hook). The porter rides at the
## back and can look about, and talk to the traveller beside him. It ends
## when the carter sets him down by the abbey gate.

## The wagon (its Seat, TravellerSeat and CarterSeat markers), and the road.
@export var wagon: Node3D
@export var path: Node3D
## m/s along the road.
@export var speed := 1.5
## The cart with the body, and the seconds into the ride it passes.
@export var body_cart: Node3D
@export var meet_at := 40.0
## Where the carter sets him down, and the traveller, and the carter's look.
@export var set_down: Marker3D
@export var traveller: Node3D
@export var carter: Node3D
## The abbey gate: barred tonight, nobody keeps it; Cole isn't at it.
@export var gate: AbbeyGate
@export var cole: VisitorNPC
## What the traveller says as the body goes by, and the carter at the gate.
@export var traveller_talk: Conversation
@export var carter_talk: Conversation

const RUMBLE := preload("res://art/sfx/amb_wagon_loop.wav")

var _points: Array[Vector3] = []
var _t := 0.0


func _ready() -> void:
	gate.swing.call_deferred(false)
	gate.show_bar.call_deferred(true)
	if cole:
		cole.set_present.call_deferred(false)


func run() -> void:
	var p := player()
	_points = points(path)
	var length := _length(_points)
	GameState.set_flag(&"n0_riding")
	_seat(p)
	if AudioOut.enabled():
		var rumble := AudioStreamPlayer3D.new()
		rumble.stream = AudioOut.looped(RUMBLE)
		rumble.volume_db = -6.0
		wagon.add_child(rumble)
		rumble.play()
	var cart_from := length * minf(meet_at * speed * 2.0 / length, 1.0)
	var said_body := false
	var said_city := false
	while _t * speed < length:
		var dt := get_physics_process_delta_time()
		_t += dt
		var along := _t * speed
		_place(wagon, along, 1.2)
		if body_cart:
			_place(body_cart, maxf(cart_from - _t * speed, 0.0), 1.4, true)
		if not said_city and _t > 6.0:
			said_city = true
			Talk.say("", "(Dusk over the fields. Ahead, the city wall, and London behind it.)")
		if not said_body and _t > meet_at - 2.0:
			said_body = true
			_hook.call()
		await get_tree().physics_frame
	p.riding = null
	p.place(set_down.global_position, set_down.global_rotation.y)
	if carter_talk and carter:
		await Talk.converse(carter_talk, carter)
	else:
		await say("Carter", "Here's your abbey, brother. They'll not be up to let you in, I'll wager.")
	# The carter drives off, and the traveller with him.
	wagon.queue_free()
	if body_cart:
		body_cart.queue_free()
	GameState.flags.erase(&"n0_riding")
	GameState.set_flag(&"n0_arrived")


## Seats him and the traveller and the carter on the wagon.
func _seat(p: Player) -> void:
	_place(wagon, 0.0, 1.2)
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


func _hook() -> void:
	await say("", "(The carter pulls over.)")
	if traveller_talk:
		await Talk.converse(traveller_talk, traveller)
		return
	await say("", "(A cart comes the other way, and something under a sheet on it, shaped like a man.)")
	await say("Traveller", "Another one. A pilgrim, found in the ditch by Aldgate. That's the third this month.")


## Puts `node` `along` metres down the road, `side` m to its right (facing
## the way it goes, or back up it with `reverse`).
func _place(node: Node3D, along: float, side: float, reverse := false) -> void:
	var at := _at(along)
	var ahead := _at(along + 0.5) - at
	if ahead.length() < 0.01:
		ahead = at - _at(along - 0.5)
	var dir := ahead.normalized() * (-1.0 if reverse else 1.0)
	var right := dir.cross(Vector3.UP).normalized()
	node.global_transform = Transform3D(Basis.looking_at(dir, Vector3.UP), at + right * side)


func _at(along: float) -> Vector3:
	var left := along
	for i in range(1, _points.size()):
		var seg := _points[i - 1].distance_to(_points[i])
		if left <= seg:
			return _points[i - 1].lerp(_points[i], left / maxf(seg, 0.001))
		left -= seg
	return _points[-1]


static func _length(pts: Array[Vector3]) -> float:
	var l := 0.0
	for i in range(1, pts.size()):
		l += pts[i - 1].distance_to(pts[i])
	return l
