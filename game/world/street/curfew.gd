class_name Curfew
extends Node3D
## The city's curfew (docs/systems/mechanics.md, "The lane at dusk"; design doc,
## "Setting"): at nine the curfew bell rings and the lane empties. Its people
## (group "lane_people") go home down the lane; the Cross Keys shuts its door;
## the lane's lit windows go dark one by one through the next hour, but for
## one or two that stay lit all night (someone who can't sleep; which, the
## night decides). The lanterns hung out in the lane and at the inn's door
## burn out one by one in the two hours after the bell, in an order the night
## decides, so the lane gets darker as the night goes on; the gate lamp, the
## porter's, burns on (your rule, 2026-11-12). After it
## only Gib the watchman walks the lane with his lantern, calling the hour on
## the hour: a clock the porter can hear from inside the walls. If a night
## stops him (silence()), his calls stop: something has happened.

signal rung
signal called(hour: int)

const BELL := preload("res://art/sfx/sfx_bell.wav")
const CALL := preload("res://art/sfx/sfx_watch_call.wav")
const TAPROOM := preload("res://art/sfx/amb_taproom_loop.wav")
const HOUR := 21.0
## The hours he calls, in his words.
const CALLS := {22: "Ten of the clock, and a cold night.", 23: "Eleven of the clock. Bar your doors.",
	24: "Midnight, and all quiet.", 25: "One of the clock.", 26: "Two of the clock, and a frost.",
	27: "Three of the clock.", 28: "Four of the clock.", 29: "Five of the clock, and the night near done."}

## The lane's houses (their lit windows go dark, and the lane's people go in
## at the nearest door), the inn's door, Gib, where they go if there's no
## house, and the ends of his round.
@export var houses: Node3D
@export var inn_door: Door
@export var gib: VisitorNPC
@export var home: Marker3D
@export var round_ends: Array[Marker3D] = []
## Where the Keys' taproom talk comes from while it's open.
@export var taproom: Node3D
## What holds the lanterns that burn out after the bell (their Candle
## children, at any depth): the lane's, and the inn's door lamps.
@export var lanterns: Array[Node3D] = []
## Hours after the bell over which they go out, the first to the last. *(mine)*
@export var lanterns_out := Vector2(0.0, 2.0)
## How many houses keep a window lit all night (1 to this; the night picks).
@export var stay_lit := 2

var has_rung := false
var silenced := false
## The hours he has called tonight.
var calls: Array[int] = []

var _bell: AudioStreamPlayer
var _talk: AudioStreamPlayer3D
var _dark := 0
var _end := 0
## Each lantern and the hour it goes out, once the bell has rung.
var _burn: Array = []
## The houses that keep a window lit tonight.
var kept: Array[TimberHouse] = []


func _ready() -> void:
	add_to_group(&"curfew")
	_bell = AudioStreamPlayer.new()
	_bell.stream = BELL
	_bell.pitch_scale = 0.8
	_bell.volume_db = -6.0
	add_child(_bell)
	if taproom and GameState.hour < HOUR:
		_talk = AudioStreamPlayer3D.new()
		_talk.stream = AudioOut.looped(TAPROOM)
		_talk.unit_size = 3.0
		_talk.volume_db = -8.0
		taproom.add_child(_talk)
		if AudioOut.enabled():
			_talk.play.call_deferred()
	if gib:
		gib.arrived.connect(_gib_turns)
	_choose_kept()


func _process(_delta: float) -> void:
	var h := GameState.hour
	if not has_rung and h >= HOUR + 0.25:
		_rung_before()
	elif not has_rung and h >= HOUR:
		ring()
	if not has_rung:
		return
	_darken(h)
	_burn_out(h)
	var on := floori(h)
	if on > HOUR and CALLS.has(on) and not calls.has(on) and not silenced:
		calls.append(on)
		if gib and AudioOut.enabled():
			var a := AudioStreamPlayer3D.new()
			a.stream = CALL
			a.unit_size = 8.0
			gib.add_child(a)
			a.position = Vector3.UP * 1.6
			a.play()
			a.finished.connect(a.queue_free)
		Talk.say("Gib {calm}", "(From the lane.) %s" % CALLS[on])
		called.emit(on)


## The bell: the lane empties, the Keys shuts, Gib begins his round.
func ring() -> void:
	has_rung = true
	GameState.set_flag(GameState.tonight("curfew"))
	if AudioOut.enabled():
		_bell.play()
	for p: Node in get_tree().get_nodes_in_group(&"lane_people"):
		var npc := p as VisitorNPC
		if npc and npc != gib and npc.visible and outdoors(npc):
			var walk := npc.get_node_or_null(^"Walk")
			if walk:
				walk.queue_free()
			_go_home.call(npc)
	if inn_door:
		inn_door.set_open(false, true)
	if _talk:
		_talk.queue_free()
		_talk = null
	if gib and not round_ends.is_empty():
		var walk := gib.get_node_or_null(^"Round")
		if walk:
			walk.queue_free()
		gib.go_to(round_ends[0].global_position)
	rung.emit()


## A night picked up after the bell (a save): the lane is already empty, the
## Keys shut, and Gib on his round; he calls from the next hour.
func _rung_before() -> void:
	has_rung = true
	GameState.set_flag(GameState.tonight("curfew"))
	for p: Node in get_tree().get_nodes_in_group(&"lane_people"):
		var npc := p as VisitorNPC
		if npc and npc != gib and outdoors(npc):
			npc.set_present(false)
	if inn_door:
		inn_door.set_open(false, true)
	calls.append(floori(GameState.hour))
	if gib and not round_ends.is_empty():
		var walk := gib.get_node_or_null(^"Round")
		if walk:
			walk.queue_free()
		gib.go_to.call_deferred(round_ends[0].global_position)


## Gib's calls stop (a night's event: something has happened in the lane).
func silence() -> void:
	silenced = true
	GameState.set_flag(GameState.tonight("watch_silent"))
	if gib:
		gib.set_present(false)


## The lane is empty of its people (those indoors, at the Keys, don't count).
func lane_empty() -> bool:
	return get_tree().get_nodes_in_group(&"lane_people").all(func(p: Node) -> bool:
		return p == gib or not (p as Node3D).visible or p.is_queued_for_deletion() or not outdoors(p as Node3D))


## Nothing over `who`'s head: he's out in the lane, not under a roof.
static func outdoors(who: Node3D) -> bool:
	var from := who.global_position + Vector3.UP * 1.8
	var up := PhysicsRayQueryParameters3D.create(from, from + Vector3.UP * 8.0, Layers.WORLD)
	return who.get_world_3d().direct_space_state.intersect_ray(up).is_empty()


## Walks him to his door and in (or in where he is, if someone's in the way).
func _go_home(npc: VisitorNPC) -> void:
	var door := _nearest_door(npc.global_position)
	npc.go_to(door)
	var t := 0.0
	while is_instance_valid(npc) and npc.visible and t < 30.0 and npc.global_position.distance_to(door) > 1.2:
		await get_tree().physics_frame
		# Someone the porter is talking to hears him out first.
		if Talk.talking_to != npc:
			t += PlayTime.physics(self)
	if is_instance_valid(npc):
		npc.set_present(false)


## The front door of the house nearest `at`, on the lane's side.
func _nearest_door(at: Vector3) -> Vector3:
	var best := home.global_position if home else at
	var dist := INF
	if houses:
		for h: Node in houses.get_children():
			var house := h as TimberHouse
			if house == null:
				continue
			var door := house.global_position - house.global_basis.z * 2.6
			if door.distance_to(at) < dist:
				dist = door.distance_to(at)
				best = door
	var map := get_world_3d().navigation_map
	if NavigationServer3D.map_get_iteration_id(map) == 0:
		return best
	return NavigationServer3D.map_get_closest_point(map, best)


func _gib_turns() -> void:
	if not has_rung or silenced or round_ends.size() < 2:
		return
	_end = (_end + 1) % round_ends.size()
	gib.go_to(round_ends[_end].global_position)


## Windows go dark one by one through the hour after the bell.
func _darken(h: float) -> void:
	if houses == null:
		return
	var list := houses.get_children().filter(func(c: Node) -> bool: return c is TimberHouse)
	var due := clampi(floori((h - HOUR) / 1.0 * list.size()), 0, list.size())
	while _dark < due:
		var house := list[_dark] as TimberHouse
		# Someone who can't sleep: one window stays lit all night.
		house.lit_windows = house.lit_windows.slice(0, 1) if kept.has(house) else PackedStringArray()
		_dark += 1


## Which houses keep a window lit tonight: one or two of those lit at dusk,
## not the Keys, the same each time the night is played.
func _choose_kept() -> void:
	kept.clear()
	if houses == null or stay_lit <= 0:
		return
	var rng := RandomNumberGenerator.new()
	rng.seed = 7919 * (GameState.night + 1)
	var lit := houses.get_children().filter(func(c: Node) -> bool:
		return c is TimberHouse and not (c as TimberHouse).lit_windows.is_empty() and c.name != "Inn")
	var count := mini(1 + rng.randi_range(0, stay_lit - 1), lit.size())
	for i in count:
		var pick := rng.randi_range(0, lit.size() - 1)
		kept.append(lit[pick] as TimberHouse)
		lit.remove_at(pick)


## The lanterns go out one by one after the bell, each at its own hour.
func _burn_out(h: float) -> void:
	if _burn.is_empty() and not lanterns.is_empty():
		_schedule()
	for b: Array in _burn:
		var c := b[0] as Candle
		if is_instance_valid(c) and c.lit and h >= float(b[1]):
			c.lit = false


func _schedule() -> void:
	var all: Array[Candle] = []
	for holder in lanterns:
		if holder:
			for c in holder.find_children("*", "Candle", true, false):
				all.append(c as Candle)
	all.sort_custom(func(a: Candle, b: Candle) -> bool: return str(a.get_path()) < str(b.get_path()))
	var rng := RandomNumberGenerator.new()
	rng.seed = 104729 * (GameState.night + 1)
	for c in all:
		_burn.append([c, HOUR + lerpf(lanterns_out.x, lanterns_out.y, rng.randf())])


## The lanterns still burning (for tests and the review).
func lanterns_lit() -> int:
	if _burn.is_empty() and not lanterns.is_empty():
		_schedule()
	return _burn.filter(func(b: Array) -> bool: return is_instance_valid(b[0]) and (b[0] as Candle).lit).size()
