extends Node3D
## The porter's body (docs/systems/mechanics.md, "Your body" and "Tests"): crouching
## is 0.8 m/s with the eyes at 1.0 m and no running, its steps are heard at
## half the walking range (2 m), and it hides him from a hunter behind
## anything 1 m high; leaning moves the view 0.4 m aside and tilts it 10°,
## stops short of a wall, and shows a hunter his head past a corner; the
## right stick looks about. Built
## in a bare test room, driven through the input actions.
## Run: tools/check.sh

var _fails := 0
var _player: Player
var _hunter: Hunter
var _heard: Array[float] = []


## Hears every Earshot sound (group "listeners") and keeps the range of
## those made at his feet (his steps, not his breathing).
class Ear:
	extends Node
	var heard: Array[float]
	func hear(at: Vector3, radius: float, _source: Node) -> void:
		if at.y < 0.5:
			heard.append(radius)


func _ready() -> void:
	_run.call_deferred()


func _block(at: Vector3, size: Vector3) -> void:
	var b := Block.new()
	b.size = size
	add_child(b)
	b.global_position = at


func _run() -> void:
	_block(Vector3(0, -0.2, 0), Vector3(60, 0.2, 60))
	# A stall 1 m high, in front of where he crouches.
	_block(Vector3(0, 0, -1.0), Vector3(3, 1.0, 0.3))
	# A wall with an edge at x = 10.25, in front of where he leans.
	_block(Vector3(9.125, 0, -1.05), Vector3(2.25, 3.0, 0.3))
	# A wall right beside him, to lean into.
	_block(Vector3(13.65, 0, 0), Vector3(0.7, 3.0, 2.0))
	_player = (load("res://game/player/player.tscn") as PackedScene).instantiate()
	add_child(_player)
	_hunter = (load("res://game/hunting/hunter.tscn") as PackedScene).instantiate()
	_hunter.dormant = true
	add_child(_hunter)
	var ear := Ear.new()
	ear.heard = _heard
	ear.add_to_group(&"listeners")
	add_child(ear)
	await _frames(10)

	# Crouch: slow, low, no running.
	_player.place(Vector3(-10, 0.05, 10), PI)
	Input.action_press(&"crouch")
	Input.action_press(&"move_forward")
	Input.action_press(&"run")
	await _seconds(1.5)
	_check(absf(_flat_speed() - Player.CROUCH_SPEED) < 0.05 and not _player.running and _player.crouching,
		"crouched he moves at 0.8 m/s and can't run (%.2f)" % _flat_speed())
	_check(absf(_player.head.position.y - Player.CROUCH_EYE) < 0.03, "his eyes are at 1.0 m (%.2f)" % _player.head.position.y)
	_heard.clear()
	await _seconds(1.5)
	_check(not _heard.is_empty() and _heard.all(func(r: float) -> bool: return r == Earshot.CROUCH),
		"crouched steps carry 2 m %s" % [_heard])
	Input.action_release(&"crouch")
	Input.action_release(&"run")
	await _seconds(0.6)
	_heard.clear()
	await _seconds(1.5)
	Input.action_release(&"move_forward")
	_check(not _player.crouching and _heard.has(Earshot.WALK) and not _heard.has(Earshot.CROUCH),
		"standing, walking steps carry 4 m %s" % [_heard])

	# Behind a 1 m stall, a hunter 9 m off sees him standing, not crouched.
	_player.place(Vector3(0, 0.05, 0), 0.0)
	_hunter.global_transform = Transform3D(Basis(Vector3.UP, PI), Vector3(0, 0.05, -9))
	await _seconds(0.5)
	var senses := _hunter.senses
	_check(senses.can_see(_player), "standing behind the stall, the hunter sees him")
	Input.action_press(&"crouch")
	await _seconds(0.5)
	_check(not senses.can_see(_player), "crouched behind it (1 m high), he doesn't")
	Input.action_release(&"crouch")
	await _seconds(0.5)

	# Lean: 0.4 m aside and 10° of tilt.
	_player.place(Vector3(10, 0.05, 0), 0.0)
	_hunter.global_transform = Transform3D(Basis(Vector3.UP, PI), Vector3(10, 0.05, -8))
	await _seconds(0.3)
	_check(not senses.can_see(_player), "behind the wall's edge, the hunter can't see him")
	Input.action_press(&"lean_right")
	await _seconds(0.5)
	_check(absf(_player.head.position.x - Player.LEAN_OFFSET) < 0.02 and absf(rad_to_deg(_player.head.rotation.z) + Player.LEAN_TILT) < 0.5,
		"leaning right, the view moves 0.4 m and tilts 10° (%.2f m, %.1f°)" % [_player.head.position.x, rad_to_deg(_player.head.rotation.z)])
	_check(senses.can_see(_player), "leaning past the edge, the hunter sees his head")
	Input.action_release(&"lean_right")
	Input.action_press(&"lean_left")
	await _seconds(0.5)
	_check(_player.head.position.x < -0.35 and not senses.can_see(_player), "leaning the other way, he is hidden again")
	Input.action_release(&"lean_left")

	# Leaning into a wall stops short of it.
	_player.place(Vector3(13.0, 0.05, 0), 0.0)
	Input.action_press(&"lean_right")
	await _seconds(0.5)
	_check(_player.head.position.x > 0.05 and _player.head.position.x < 0.2,
		"against a wall he can only lean a little (%.2f m)" % _player.head.position.x)
	Input.action_release(&"lean_right")
	await _seconds(0.4)
	_check(absf(_player.head.position.x) < 0.02, "and stands straight again")

	# The gamepad: the right stick looks about.
	_player.place(Vector3(0, 0.05, 10), 0.0)
	Input.action_press(&"look_right")
	await _seconds(0.5)
	Input.action_release(&"look_right")
	_check(_player.rotation.y < -0.5, "the right stick turns him (%.2f rad)" % _player.rotation.y)

	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


func _flat_speed() -> float:
	return Vector2(_player.velocity.x, _player.velocity.z).length()


func _frames(n: int) -> void:
	for i in n:
		await get_tree().physics_frame


func _seconds(s: float) -> void:
	await get_tree().create_timer(s, true, true).timeout


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
