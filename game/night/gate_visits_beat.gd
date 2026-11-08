extends NightBeat
## Keeping the gate (design doc, "Core loop" 3: talk through the grate, read
## the visitor, admit to the guesthouse, refuse, or send for the prior.
## Night 3: "Walter again, with a bag that smells of the incense. A
## child-sized knock low on the gate; no one there (hallucination at Dose
## 50+).").
##
## Each visitor comes at his hour by the candle clock (`knock_hours`), walks
## up the lane with his lantern and knocks; the knock wakes a dozing porter
## (who hasn't seen him come: he is at the grille already). No dozing while
## someone is at the gate. At the grille they talk (Talk.begin: the porter's
## view eases in on him), and the porter reads him by looking him over: each
## VisitorDetail he looks at gives a line and goes into the ledger. He can
## walk away from the grille; the visitor waits, knocking now and then, until
## he comes back. Then he chooses:
## - Admit: lift the bar, open the gate; the visitor comes in; shut and bar
##   the gate behind him; he follows the porter to the guesthouse and takes
##   the bed the porter shows him; the porter writes him in the ledger.
## - Turn away: the visitor goes back down the lane.
## - Send for the prior (Suspicion +10, Ranulf overhears): the prior comes,
##   lets him in and takes him to a bed himself; the porter still writes him
##   in the ledger.

const KNOCK := preload("res://art/sfx/sfx_knock.wav")
const KNOCK_LOW := preload("res://art/sfx/sfx_knock_low.wav")
const PRIOR_SUSPICION := 10
const CHILD_KNOCK_DOSE := 50.0
## Reading: how close to the middle of the view, how near, and how long.
const READ_ANGLE := 9.0
const READ_RANGE := 4.0
const READ_TIME := 0.35
## At the grille he can look the visitor over, boots to face (degrees either
## side of the face, yaw and pitch).
const GRILLE_CONE := Vector2(40.0, 50.0)
const CHOICES := ["Admit him to the guesthouse", "Turn him away", "Send for the prior"]

@export var visitors: Array[Visitor] = []
## When each visitor knocks, in hours (in the order of `visitors`).
@export var knock_hours := PackedFloat32Array([20.0])
## The small knock with no one there (at Dose 50+).
@export var child_knock_hour := 22.0
@export var visitor_scene: PackedScene
@export var prior_visitor: Visitor
@export var visitor_speed := VisitorNPC.WALK_SPEED
## Where visitors come from and go back to, down the lane, out of sight.
@export var lane_start: Marker3D
@export var lane_leave: Marker3D
## Outside the grille, under the porch lantern; just inside the gate.
@export var porch: Marker3D
@export var inside: Marker3D
@export var prior_from: Marker3D
@export var grate: Duty
@export var bar_duty: Duty
@export var open_gate: Duty
@export var shut_gate: Duty
@export var ledger: Duty
## Duty children, one per guesthouse bed (each bed's top centre).
@export var beds: Node3D
@export var gate: AbbeyGate
## Seconds between knocks until answered.
@export var knock_every := 5.0

var _audio: AudioStreamPlayer3D
var _reading := false
var _taken_beds: Array[Duty] = []


func _ready() -> void:
	_audio = AudioStreamPlayer3D.new()
	_audio.unit_size = 6.0
	add_child(_audio)


func run() -> void:
	for i in visitors.size():
		await clock().wait_until(knock_hours[i] if i < knock_hours.size() else 0.0)
		can_doze = false
		await _receive(visitors[i])
		can_doze = true
	await clock().wait_until(child_knock_hour)
	if GameState.dose >= CHILD_KNOCK_DOSE:
		await _knock_until_answered(KNOCK_LOW, 0.4)
		GameState.set_flag(&"n3_child_knock")
		await say("", "(A small knock, low on the gate. No one there.)")


func _receive(v: Visitor) -> void:
	var npc := _spawn(v, porch if clock().dozing else lane_start)
	if not clock().dozing:
		await npc.walk_to(porch.global_position)
	npc.face(inside.global_position)
	await _knock_until_answered(KNOCK, 1.4)
	var noticed: Array[VisitorDetail] = []
	var pick := -1
	while pick < 0:
		Talk.begin(npc, GRILLE_CONE)
		await say(v.speaker, v.greeting)
		_reading = true
		_read.call(npc, v, noticed)
		pick = await Talk.choose(PackedStringArray(CHOICES), v.speaker, v.greeting)
		_reading = false
		Talk.end()
		if pick < 0:
			# He walked away from the grille; the visitor waits for him.
			await _knock_until_answered(KNOCK, 1.4)
	match pick:
		0:
			GameState.set_flag(v.flag, &"admitted")
			await _admit(npc)
		1:
			GameState.set_flag(v.flag, &"refused")
			await say("", "(You turn him away. He goes back down the lane.)")
			_send_away(npc)
			return
		_:
			GameState.set_flag(v.flag, &"prior")
			GameState.raise_suspicion(PRIOR_SUSPICION)
			await say("", "(You send for the prior.)")
			await _prior_admits(npc)
	await say("", "(Write him in the ledger, at your desk.)")
	await ledger.wait_for_use()
	var words := PackedStringArray()
	for d in noticed:
		words.append(d.ledger)
	GameState.write_ledger(v.ledger_name, ", ".join(words))
	await say("", "(You write: %s.)" % (v.ledger_name + (": " + ", ".join(words) if not words.is_empty() else "")))


## Looks the visitor over while the porter decides: the detail he holds his
## eyes on for a moment (the part nearest the middle of his view) gives a
## line, once. Talking to him through the grille, that starts with his face.
func _read(npc: VisitorNPC, v: Visitor, noticed: Array[VisitorDetail]) -> void:
	var p := player()
	var dwell := {}
	while _reading:
		var looked_at: VisitorDetail = null
		var nearest := READ_ANGLE
		for d in v.details:
			var at := npc.part_position(d.part)
			var off := ViewCheck.off_centre(p.camera, at)
			if p.camera.global_position.distance_to(at) < READ_RANGE and p.camera.is_position_in_frustum(at) and off < nearest:
				nearest = off
				looked_at = d
		for d in v.details:
			dwell[d] = float(dwell.get(d, 0.0)) + get_physics_process_delta_time() if d == looked_at else 0.0
			if d == looked_at and not noticed.has(d) and dwell[d] >= READ_TIME:
				noticed.append(d)
				Talk.say("", d.line)
		await get_tree().physics_frame


## Lift the bar, open the gate, let him in, shut and bar it, take him to a bed.
func _admit(npc: VisitorNPC) -> void:
	await say("", "(Lift the bar and open the gate.)")
	await bar_duty.wait_for_use()
	gate.show_bar(false)
	await open_gate.wait_for_use()
	await gate.swing(true)
	await npc.walk_to(inside.global_position)
	await say("", "(Shut the gate behind him, and bar it.)")
	await shut_gate.wait_for_use()
	await gate.swing(false)
	await bar_duty.wait_for_use()
	gate.show_bar(true)
	npc.follow(player())
	await say("", "(He follows you. Show him a bed in the guesthouse.)")
	var bed := await _pick_bed()
	await npc.walk_to(_beside(bed))
	npc.lie_down(_bed_top(bed))


## The prior comes to the gate, lets him in and takes him to a bed.
func _prior_admits(npc: VisitorNPC) -> void:
	var prior := _spawn(prior_visitor, prior_from)
	await prior.walk_to(inside.global_position)
	await say(prior_visitor.speaker, "(Lets him in, and takes him to the guesthouse himself.)")
	gate.show_bar(false)
	await gate.swing(true)
	await npc.walk_to(inside.global_position + Vector3(1.2, 0, 0.8))
	await gate.swing(false)
	gate.show_bar(true)
	var bed := _free_beds()[0]
	_taken_beds.append(bed)
	npc.follow(prior)
	await prior.walk_to(_beside(bed) + Vector3(1.0, 0, 0))
	await npc.walk_to(_beside(bed))
	npc.lie_down(_bed_top(bed))
	_send_away(prior, prior_from)


## Waits for the porter to choose a free bed.
func _pick_bed() -> Duty:
	var chosen: Array[Duty] = []
	var free := _free_beds()
	for bed in free:
		bed.used.connect(func(_by: Node) -> void: chosen.append(bed), CONNECT_ONE_SHOT)
		bed.enabled = true
	while chosen.is_empty():
		await get_tree().physics_frame
	for bed in free:
		bed.enabled = false
		for c in bed.used.get_connections():
			bed.used.disconnect(c["callable"])
	_taken_beds.append(chosen[0])
	return chosen[0]


func _free_beds() -> Array[Duty]:
	var out: Array[Duty] = []
	for c in beds.get_children():
		if c is Duty and not _taken_beds.has(c):
			out.append(c)
	return out


## Lying on a guesthouse bed (0.45 m high, its length along Z).
func _bed_top(bed: Duty) -> Transform3D:
	return Transform3D(Basis.IDENTITY, bed.global_position + Vector3.UP * 0.45)


## The floor beside a bed, on its open side.
func _beside(bed: Duty) -> Vector3:
	return bed.global_position + Vector3(0, 0, 1.5)


## Someone come to the gate tonight (group "callers", unlike the people who
## are just about).
func _spawn(v: Visitor, at: Marker3D) -> VisitorNPC:
	var npc := visitor_scene.instantiate() as VisitorNPC
	npc.add_to_group(&"callers")
	npc.visitor = v
	npc.speed = visitor_speed
	get_parent().get_parent().add_child(npc)
	npc.global_transform = at.global_transform
	return npc


func _send_away(npc: VisitorNPC, to: Marker3D = null) -> void:
	await npc.walk_to((to if to else lane_leave).global_position)
	npc.queue_free()


func _knock_until_answered(stream: AudioStream, height: float) -> void:
	var answered := [false]
	grate.used.connect(func(_by: Node) -> void: answered[0] = true, CONNECT_ONE_SHOT)
	grate.enabled = true
	var t := 0.0
	clock().wake()
	while not answered[0]:
		if t <= 0.0:
			t = knock_every
			if AudioOut.enabled():
				_audio.global_position = grate.global_position + Vector3(-0.6, height, 0.0)
				_audio.stream = stream
				_audio.play()
		await get_tree().physics_frame
		t -= get_physics_process_delta_time()
	grate.enabled = false
