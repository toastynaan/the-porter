extends Node3D
## Ragdoll checks on the example host (game/ragdoll/host): a hit flinches and
## recovers, a combo staggers, a shin hit stumbles, a heavy hit knocks down
## with a get-up, and death leaves a corpse that settles.
## Run: tools/check.sh

var _fails := 0


func _ready() -> void:
	var floor_body := StaticBody3D.new()
	floor_body.collision_layer = Layers.WORLD
	var cs := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(60, 1, 60)
	cs.shape = box
	cs.position = Vector3(0, -0.5, 0)
	floor_body.add_child(cs)
	add_child(floor_body)
	_run.call_deferred()


func _run() -> void:
	var z := _spawn(Vector3.ZERO)
	await _frames(60)
	_check(z.ragdoll.state == RagdollController.State.ANIMATED, "stands animated")
	var head_y := z.rig.get_bone_global_position(Bones.HEAD).y
	_check(head_y > 1.3 and head_y < 1.8, "head height %.2f m" % head_y)
	_check(z.hurtboxes.size() == Bones.PHYSICAL.size(), "one hurtbox per physical bone")

	# A head hit flinches: the head snaps back, then the body recovers.
	var kind := z.take_punch(Bones.HEAD, Vector3.BACK, z.global_position + Vector3.UP * 1.6, false)
	_check(kind == &"flinch" and z.ragdoll.state == RagdollController.State.FLINCH, "head hit flinches (%s)" % kind)
	var head0 := z.rig.get_bone_global_transform(Bones.HEAD) * Vector3(0, 0.15, 0)
	var moved := 0.0
	for i in 40:
		await _frames(1)
		moved = maxf(moved, (z.rig.get_bone_global_transform(Bones.HEAD) * Vector3(0, 0.15, 0)).distance_to(head0))
	_check(moved > 0.04, "head snaps back %.3f m" % moved)
	await _frames(90)
	_check(z.ragdoll.state == RagdollController.State.ANIMATED, "flinch recovers")

	# Third hit inside the combo window staggers.
	var z2 := _spawn(Vector3(4, 0, 0))
	await _frames(30)
	var r: Array[StringName] = []
	for i in 3:
		r.append(z2.take_punch(Bones.CHEST, Vector3.BACK, z2.global_position + Vector3.UP * 1.3, false))
		await _frames(20)
	var want: Array[StringName] = [&"flinch", &"flinch", &"stagger"]
	_check(r == want, "combo: %s" % [r])
	await _frames(150)
	_check(z2.ragdoll.state == RagdollController.State.ANIMATED, "stagger recovers")

	# A shin hit stumbles.
	kind = z2.take_punch(Bones.L_LOWER_LEG, Vector3.BACK, z2.global_position + Vector3.UP * 0.3, false)
	_check(kind == &"stumble", "leg hit stumbles (%s)" % kind)
	await _frames(150)

	# A heavy hit knocks down; the body gets back up.
	var z3 := _spawn(Vector3(-4, 0, 0))
	await _frames(30)
	var recovered := [false]
	z3.ragdoll.recovered.connect(func() -> void: recovered[0] = true)
	kind = z3.take_punch(Bones.CHEST, Vector3.BACK, z3.global_position + Vector3.UP * 1.3, true)
	_check(kind == &"knockdown" and z3.ragdoll.is_full_ragdoll(), "heavy hit knocks down")
	var waited := 0
	while not recovered[0] and waited < 120 * 8:
		await _frames(10)
		waited += 10
	_check(recovered[0], "gets up after %.1f s" % (waited / 120.0))
	_check(z3.ragdoll.state == RagdollController.State.ANIMATED, "animated after get-up")

	# Hits until dead: the body flies back, stays a ragdoll and settles.
	var start := z3.global_position
	var died := [false]
	z3.died.connect(func(_z: Zombie) -> void: died[0] = true)
	while not z3.is_dead():
		kind = z3.take_punch(Bones.HEAD, Vector3.BACK, z3.global_position + Vector3.UP * 1.6, false)
		await _frames(30)
	_check(kind == &"kill" and died[0], "killing blow")
	_check(z3.ragdoll.state == RagdollController.State.DEAD, "dead state")
	waited = 0
	while not z3.ragdoll.is_settled() and waited < 120 * 12:
		await _frames(10)
		waited += 10
	_check(z3.ragdoll.is_settled(), "corpse settles after %.1f s" % (waited / 120.0))
	var pushed := z3.ragdoll.get_ground_position() - start
	_check(pushed.z > 0.3, "corpse thrown back %.2f m" % pushed.z)

	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


func _spawn(at: Vector3) -> Zombie:
	var z := Zombie.new()
	z.passive = true
	z.appearance = {"skin": Zombie.SKINS[0], "shirt": Zombie.SHIRTS[0], "pants": Zombie.PANTS[0]}
	z.position = at
	add_child(z)
	return z


func _frames(n: int) -> void:
	for i in n:
		await get_tree().physics_frame


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
