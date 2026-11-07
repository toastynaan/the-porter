extends Node
## Abbey navigation checks on the baked navmesh: every area is reachable and
## within a minute's walk (1.4 m/s) of the cloister; the night stairs and the
## hidden cellar stair are shortcuts on the navmesh; the mill wheel gap and
## the latrine chute are not (hunters must go round).
## Run: tools/check.sh

const WALK_SPEED := 1.4
const MINUTE := 60.0

var _fails := 0
var _map: RID
var _markers := {}


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	var abbey: Node3D = load("res://game/world/abbey/abbey.tscn").instantiate()
	add_child(abbey)
	_map = (abbey.get_node(^"Navigation") as NavigationRegion3D).get_navigation_map()
	# Wait for the navigation server to take in the region.
	for i in 30:
		await get_tree().physics_frame
	var region: NavigationRegion3D = abbey.get_node(^"Navigation")
	var probe := NavigationServer3D.map_get_path(_map, Vector3(0, 0, -16), Vector3(0, 0.05, -32), true)
	print("  info map iteration %d, regions %d, navmesh polygons %d, closest to garth %s, probe path %d points" % [
		NavigationServer3D.map_get_iteration_id(_map), NavigationServer3D.map_get_regions(_map).size(),
		region.navigation_mesh.get_polygon_count(), NavigationServer3D.map_get_closest_point(_map, Vector3(0, 0, -16)), probe.size()])
	for m in get_tree().get_nodes_in_group(&"area_marker"):
		_markers[String(m.name)] = (m as Node3D).global_position
	_check(_markers.size() >= 20, "%d area markers" % _markers.size())

	# Every area from the cloister garth, at a walk.
	var from: Vector3 = _markers["Cloister"]
	var worst := 0.0
	var worst_name := ""
	for marker_name: String in _markers:
		var length := _path_length(from, _markers[marker_name])
		if length < 0.0:
			_check(false, "%s is unreachable" % marker_name)
			continue
		if length > worst:
			worst = length
			worst_name = marker_name
	_check(worst / WALK_SPEED <= MINUTE, "every area within a minute's walk of the cloister (farthest %s, %.0f m, %.0f s)" % [
		worst_name, worst, worst / WALK_SPEED])

	# The widest crossing, for the record.
	var far := 0.0
	var pair := ""
	var names := _markers.keys()
	for i in names.size():
		for k in range(i + 1, names.size()):
			var length := _path_length(_markers[names[i]], _markers[names[k]])
			if length > far:
				far = length
				pair = "%s - %s" % [names[i], names[k]]
	print("  info widest crossing: %s, %.0f m (%.0f s walking, %.0f s running)" % [pair, far, far / WALK_SPEED, far / 4.0])

	# Shortcuts the hunters use.
	var night := _path_length(_markers["Choir"], Vector3(16, 4.02, -25.5))
	_check(night > 0.0 and night < 25.0, "night stairs: choir to the dormitory's north end %.1f m" % night)
	var hidden := _path_length(_markers["Granary"], _markers["Passage"])
	_check(hidden > 0.0 and hidden < 32.0, "hidden stair: granary to the passage %.1f m" % hidden)
	var crypt := _path_length(_markers["HiddenStairTop"], _markers["Crypt"])
	_check(crypt > 0.0, "hidden stair reaches the crypt (%.1f m)" % crypt)

	# Gaps only the porter fits through.
	var wheel := _path_length(_markers["RaceWest"], _markers["RaceEast"])
	_check(wheel > 30.0, "no way under the mill wheel: round is %.1f m" % wheel)
	var chute := _path_length(_markers["Latrine"], Vector3(16, -1.2, 18.6))
	_check(chute > 30.0, "no way down the latrine chute: round is %.1f m" % chute)

	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


## Length of the navmesh path, or -1 when it doesn't reach `to`.
func _path_length(from: Vector3, to: Vector3) -> float:
	var path := NavigationServer3D.map_get_path(_map, from, to, true)
	if path.is_empty():
		return -1.0
	var end := path[path.size() - 1]
	if Vector2(end.x - to.x, end.z - to.z).length() > 0.7 or absf(end.y - to.y) > 0.8:
		return -1.0
	var length := 0.0
	for i in range(1, path.size()):
		length += path[i - 1].distance_to(path[i])
	return length


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
