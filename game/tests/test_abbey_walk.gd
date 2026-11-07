extends Node
## Walks the porter's own body round the whole abbey along navmesh paths, so
## every stair, doorway and ramp is proven walkable, not just baked. All
## doors are opened first. Runs at 4 m/s to keep the test short; walking
## times come from the path lengths (test_abbey_nav).
## Run: tools/check.sh

## The tour, from the spawn in the outer court.
const TOUR: Array[String] = ["PortersCell", "Guesthouse", "Tower", "Nave", "Choir", "Crypt", "Choir",
	"Dormitory", "Latrine", "ChapterHouse", "CloisterWalk", "Cloister", "Granary", "HiddenStairTop",
	"Passage", "Crypt", "Passage", "Cellar", "Refectory", "Kitchen", "Bakehouse", "RaceWest", "Mill",
	"Infirmary", "Charnel", "Graveyard", "Fishpond", "RaceEast", "OuterCourt"]
## Next waypoint when this close, m.
const REACH := 0.35

var _fails := 0
var _player: Player
var _map: RID


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	var abbey: Node3D = load("res://game/world/abbey/abbey.tscn").instantiate()
	add_child(abbey)
	_player = abbey.get_node(^"Player")
	_map = (abbey.get_node(^"Navigation") as NavigationRegion3D).get_navigation_map()
	for door in get_tree().get_nodes_in_group(&"doors"):
		if String(door.name).begins_with("Gate"):
			continue
		door.locked = false
		door.set_open(true, true)
	for i in 30:
		await get_tree().physics_frame
	var markers := {}
	for m in get_tree().get_nodes_in_group(&"area_marker"):
		markers[String(m.name)] = (m as Node3D).global_position
	_player.use_input_override = true
	_player.run_override = true
	var total := 0.0
	var sim := 0.0
	for stop in TOUR:
		var target: Vector3 = markers[stop]
		var path := NavigationServer3D.map_get_path(_map, _player.global_position, target, true)
		var length := 0.0
		for i in range(1, path.size()):
			length += path[i - 1].distance_to(path[i])
		var limit := length / Player.RUN_SPEED * 1.6 + 3.0
		var t := await _follow(path, limit)
		var arrived := _flat(_player.global_position - target).length() < 0.8 and absf(_player.global_position.y - target.y) < 0.6
		_check(arrived, "reaches %s (%.0f m in %.1f s)" % [stop, length, t])
		if not arrived:
			print("       stuck at %s" % _player.global_position)
			_player.global_position = target
		total += length
		sim += t
	_player.use_input_override = false
	print("  info toured %.0f m in %.0f s of running" % [total, sim])
	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


## Steers along `path` until its end or `limit` seconds; returns the time taken.
func _follow(path: PackedVector3Array, limit: float) -> float:
	var t := 0.0
	var i := 1
	var dt := 1.0 / Engine.physics_ticks_per_second
	while i < path.size() and t < limit:
		var to := _flat(path[i] - _player.global_position)
		if to.length() < REACH and absf(path[i].y - _player.global_position.y) < 1.0:
			i += 1
			continue
		_player.rotation.y = atan2(-to.x, -to.z)
		_player.input_override = Vector2(0, 1)
		await get_tree().physics_frame
		t += dt
	_player.input_override = Vector2.ZERO
	for k in 30:
		await get_tree().physics_frame
	return t


func _flat(v: Vector3) -> Vector3:
	return Vector3(v.x, 0.0, v.z)


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
