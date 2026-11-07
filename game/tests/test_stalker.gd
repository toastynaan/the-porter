extends Node
## The demon stalking the porter in the graveyard (Stalking phase): the
## animals go quiet before every appearance; it only ever appears off screen;
## it never moves while he looks at it; it is gone once he looks away; each
## appearance is closer; staring at it builds the stare meter (narrower
## view) until he stumbles; the last appearance is right behind him in full
## silence, and it can't leave his lantern light: covered, it hands over.
## Run: tools/check.sh

## Where the porter stands, facing the infirmary wall with the graveyard behind.
const STAND := Vector3(30, 0.0, -6)

var _fails := 0
var _player: Player
var _stalker: Stalker
var _animals: Animals
var _sim := 0.0
var _sim_total := 0.0
var _quiet_since := -1.0
var _calls_while_quiet := 0
var _appear_log: Array = []


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	seed(7)
	var abbey: Node3D = load("res://game/world/abbey/abbey.tscn").instantiate()
	add_child(abbey)
	_player = abbey.get_node(^"Player")
	_animals = abbey.get_node(^"Animals")
	_animals.called.connect(func(_kind: StringName) -> void:
		if _animals.quiet:
			_calls_while_quiet += 1)
	_stalker = (load("res://game/demon/stalker.tscn") as PackedScene).instantiate()
	_stalker.interval = Vector2(1.0, 1.5)
	_stalker.quiet_lead = 1.0
	_stalker.rearm = false
	add_child(_stalker)
	_stalker.appeared.connect(_on_appeared)
	await _frames(30)
	GameState.snap_dose(0.0)
	_face_away()

	var distances: Array[float] = []
	for n in 6:
		await _until(func() -> bool: return _appear_log.size() > n, 20.0)
		if _appear_log.size() <= n:
			_check(false, "appearance %d came" % (n + 1))
			break
		var entry: Array = _appear_log[n]
		_check(entry[0], "appearance %d: arrived off screen" % (n + 1))
		_check(entry[1] >= _stalker.quiet_lead - 0.05, "appearance %d: the animals went quiet %.1f s before" % [n + 1, entry[1]])
		distances.append(_stalker.last_distance)
		if _stalker.final:
			break
		# Look at it: it stays exactly where it is.
		_face(_stalker.global_position + Vector3.UP * 1.3)
		var at := _stalker.global_position
		var moved := 0.0
		var hold := 0.6 if n > 0 else 5.3
		_sim = 0.0
		var stare_peak := 0.0
		var fov_min := 90.0
		while _sim < hold and not _player.stumbling:
			await get_tree().physics_frame
			moved = maxf(moved, _stalker.global_position.distance_to(at))
			stare_peak = maxf(stare_peak, _stare())
			fov_min = minf(fov_min, _player.camera.fov)
		_check(_stalker.seen and _stalker.visible and moved == 0.0, "appearance %d: seen, and it never moves in view" % (n + 1))
		if n == 0:
			_check(stare_peak > 0.99 and absf(fov_min - 65.0) < 0.3,
				"staring builds the meter in 3 s and narrows the view 5° (%.2f, %.1f°)" % [stare_peak, fov_min])
			var stared := _sim
			await _until(func() -> bool: return _player.stumbling, 3.0)
			stared += _sim
			_check(_player.stumbling and absf(stared - 5.0) < 0.3,
				"held full for 2 s, he loses his footing (after %.1f s of staring)" % stared)
			await _until(func() -> bool: return not _player.stumbling, 3.0)
		_face_away()
		var gone_by := [false]
		_stalker.vanished.connect(func() -> void: gone_by[0] = true, CONNECT_ONE_SHOT)
		await _until(func() -> bool: return gone_by[0], 2.0)
		_check(gone_by[0] and not _stalker.visible, "appearance %d: gone when he looks away (%.1f s)" % [n + 1, _sim])
	var closer := true
	for i in range(1, distances.size()):
		closer = closer and distances[i] <= distances[i - 1] * _stalker.closer + 0.01
	_check(closer and distances.size() >= 3, "closer every time %s" % [distances.map(func(d: float) -> String: return "%.1f" % d)])
	_check(_calls_while_quiet == 0, "not a sound from the animals while quiet")

	# The last one: right behind him, in full silence.
	_check(_stalker.final and distances[-1] < 4.5, "the last appearance is behind him (%.1f m)" % distances[-1])
	_check(_player.get_parent().get_node(^"Wind").get(&"_silent") == true, "full silence: even the wind stops")
	_face(_stalker.global_position + Vector3.UP * 1.3)
	await _seconds(0.6)
	var handed := [false]
	_stalker.handed_over.connect(func() -> void: handed[0] = true)
	_face_away()
	await _seconds(1.5)
	_check(not handed[0] and _stalker.visible, "it can't move while his lantern lights it")
	Input.action_press(&"cover_lantern")
	await _until(func() -> bool: return handed[0], 2.0)
	Input.action_release(&"cover_lantern")
	_check(handed[0] and not _stalker.visible, "covered, it comes for him (the hunter takes over)")

	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


func _on_appeared(_at: Vector3) -> void:
	var off := not ViewCheck.on_screen(_player.camera, _stalker._points())
	var quiet_for := (_sim_total - _quiet_since) if _animals.quiet and _quiet_since >= 0.0 else 0.0
	_appear_log.append([off, quiet_for])


func _stare() -> float:
	return (_player.get_node(^"StareMeter") as StareMeter).value


func _face_away() -> void:
	_player.place(STAND, PI)


func _face(point: Vector3) -> void:
	var to := point - _player.camera.global_position
	_player.rotation.y = atan2(-to.x, -to.z)
	_player.head.rotation.x = atan2(to.y, Vector2(to.x, to.z).length())


func _physics_process(delta: float) -> void:
	_sim += delta
	_sim_total += delta
	if _animals:
		if _animals.quiet and _quiet_since < 0.0:
			_quiet_since = _sim_total
		elif not _animals.quiet:
			_quiet_since = -1.0


func _until(cond: Callable, limit: float) -> void:
	_sim = 0.0
	while not cond.call() and _sim < limit:
		await get_tree().physics_frame


func _frames(n: int) -> void:
	for i in n:
		await get_tree().physics_frame


func _seconds(s: float) -> void:
	await get_tree().create_timer(s, true, true).timeout


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
