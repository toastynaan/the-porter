class_name OffHoursBell
extends Node3D
## The bell rope, out of hours (docs/mechanics.md, "The bell rope"): ring it
## any time but Matins and the whole abbey comes to the tower. The chase
## breaks off, because the hunter can't be seen in costume by the abbey. Who
## comes first follows rules he can learn:
## - a friend whose trust is 40 or more (Edwin; Simon, if he saved him)
##   walks him somewhere safe (his cell);
## - otherwise, at Suspicion below 60, the prior comes and questions him;
## - at 60 or more a cultist reaches him first, which is a capture.
## Each off-hours ring is Suspicion +10.

signal rung(who: StringName)

const SUSPICION := 10
const FRIEND_TRUST := 40
const PRIOR_BELOW := 60
const FRIENDS: Array[StringName] = [&"edwin", &"simon"]
const LOOKS := {
	&"edwin": preload("res://game/characters/chr_edwin.tscn"),
	&"simon": preload("res://game/characters/chr_choir_brother_c.tscn"),
	&"hugh": preload("res://game/characters/chr_hugh.tscn"),
}

## The Matins rope: while it's wanted, this one is.
@export var matins_rope: Duty
@export var tower: BellTower
## Where whoever comes comes from (the tower door), and where a friend takes him.
@export var arrive_at: Marker3D
@export var safe_place: Marker3D
@export var size := Vector3(0.8, 2.0, 0.8)

## Who came the last time: a friend's id, "hugh", or "cultist".
var last := &""

var _area: Area3D
var _busy := false


func _ready() -> void:
	add_to_group(&"off_hours_bell")
	_area = Area3D.new()
	_area.collision_mask = 0
	_area.monitoring = false
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = size
	shape.shape = box
	shape.position = Vector3(0, size.y * 0.5, 0)
	_area.add_child(shape)
	add_child(_area)


func _process(_delta: float) -> void:
	var on := not _busy and not (matins_rope and matins_rope.enabled) and GameState.phase != GameState.Phase.MATINS
	_area.collision_layer = Layers.INTERACT if on else 0


## Who would come if he rang now.
static func who_comes() -> StringName:
	for f in FRIENDS:
		var alive := not GameState.has_flag(StringName("died_" + String(f)))
		var met := f != &"simon" or GameState.has_flag(&"saved_simon")
		if alive and met and GameState.trust_of(f) >= FRIEND_TRUST:
			return f
	return &"hugh" if GameState.suspicion < PRIOR_BELOW else &"cultist"


func interact(by: Node) -> void:
	await ring(by as Player)


func ring(p: Player) -> void:
	if _busy or p == null:
		return
	_busy = true
	if tower:
		tower.ring(6)
	GameState.raise_suspicion(SUSPICION)
	GameState.set_flag(GameState.tonight("bell_rung"))
	# The abbey is coming: no costume can be seen. The chase breaks off.
	for h: Hunter in get_tree().get_nodes_in_group(&"hunters"):
		if not h.dormant and h.state != Hunter.State.PATROL:
			h.reset()
	last = who_comes()
	await Talk.say("", "(The bell clangs over the roofs. Doors bang open all over the abbey.)")
	match last:
		&"hugh":
			await _prior_questions(p)
		&"cultist":
			await _cultist(p)
		_:
			await _friend(p, last)
	rung.emit(last)
	_busy = false


func _arrive(look: PackedScene) -> VisitorNPC:
	var npc := (preload("res://game/gate/visitor_npc.tscn") as PackedScene).instantiate() as VisitorNPC
	var v := Visitor.new()
	v.look = look
	v.lantern = true
	npc.visitor = v
	get_parent().add_child(npc)
	npc.global_transform = arrive_at.global_transform if arrive_at else global_transform
	return npc


func _friend(p: Player, who: StringName) -> void:
	var npc := _arrive(LOOKS[who])
	await npc.walk_to(p.global_position + (npc.global_position - p.global_position).normalized() * 1.2)
	npc.face(p.global_position)
	await Talk.say(People.display_name(who), "Alric! What is it? No, don't tell me here. Come away, come with me.")
	p.controls_locked = true
	var flow := get_tree().get_first_node_in_group(&"capture_flow") as CaptureFlow
	if flow:
		await flow.fade.fade_to(1.0, 0.6)
	if safe_place:
		p.place(safe_place.global_position, safe_place.global_rotation.y)
	npc.queue_free()
	if flow:
		await flow.fade.fade_to(0.0, 1.0)
	p.controls_locked = false
	await Talk.say("", "(He sees you to your cell, and waits until you've barred the door.)")


func _prior_questions(p: Player) -> void:
	var npc := _arrive(LOOKS[&"hugh"])
	await npc.walk_to(p.global_position + (npc.global_position - p.global_position).normalized() * 1.2)
	npc.face(p.global_position)
	var pick := await Talk.answer(PackedStringArray(["Something was after me.", "I was frightened. It was nothing.", "(Say nothing.)"]),
		"Hugh", "The bell, at this hour? Speak, porter. What did you see?")
	match pick:
		0:
			GameState.set_flag(&"hugh_suspects", int(GameState.get_flag(&"hugh_suspects", 0)) + 1)
			await Talk.say("Hugh", "Something. Always something, in this house, and never anyone. Go back to your gate.")
		1:
			await Talk.say("Hugh", "Then don't wake the house for nothing again.")
		_:
			await Talk.say("Hugh", "(He looks at you a long time, and writes on his tablet.)")
	npc.queue_free()


func _cultist(p: Player) -> void:
	var h := (preload("res://game/hunting/hunter.tscn") as PackedScene).instantiate() as Hunter
	h.weapon = &"blade" if GameState.night >= 4 else &"cord"
	get_parent().add_child(h)
	h.global_position = p.global_position - p.global_basis.z * 0.8
	await Talk.say("", "(The first to reach you isn't a brother.)")
	var flow := get_tree().get_first_node_in_group(&"capture_flow") as CaptureFlow
	if flow:
		flow.on_captured(h, p)
