class_name Zombie
extends CharacterBody3D
## A shambling zombie on the ragdoll ported from big-kick (game/ragdoll):
## HumanoidRig + PoseAnimator + RagdollController under a capsule host. It
## lurches toward the player with its arms out; hits play out through the
## ragdoll (flinch, stumble, stagger, knockdown and get-up), and a dead one
## stays a ragdoll on Layers.DEAD_BODY until it settles and freezes.
##
## It follows the navigation mesh when the level has one (NavigationAgent3D),
## else walks straight at the player.
##
## Host contract (RagdollController): a direct child CollisionShape3D named
## "Capsule"; never move_and_slide while ragdoll.is_simulating(); is_frozen()
## and get_actor_time() drive hitstop.

signal died(zombie: Zombie)

const SKINS: Array[Color] = [Color(0.48, 0.55, 0.42), Color(0.56, 0.58, 0.47), Color(0.42, 0.47, 0.40), Color(0.60, 0.55, 0.50)]
const SHIRTS: Array[Color] = [Color(0.33, 0.30, 0.26), Color(0.25, 0.30, 0.36), Color(0.45, 0.20, 0.17), Color(0.52, 0.50, 0.44), Color(0.22, 0.27, 0.20)]
const PANTS: Array[Color] = [Color(0.17, 0.19, 0.25), Color(0.27, 0.23, 0.18), Color(0.20, 0.20, 0.19)]
## s between path requests while chasing.
const REPATH := 0.4
## Stuck: wanting to walk but moving slower than STUCK_SPEED for STUCK_AFTER s
## makes it side-step for UNSTICK_TIME s.
const STUCK_SPEED := 0.15
const STUCK_AFTER := 0.8
const UNSTICK_TIME := 0.6
const LEG_BONES: Array[StringName] = [Bones.L_UPPER_LEG, Bones.L_LOWER_LEG, Bones.L_FOOT,
	Bones.R_UPPER_LEG, Bones.R_LOWER_LEG, Bones.R_FOOT]

## Empty: a random zombie look. Keys as HumanoidRig.build (skin, shirt, pants, height, width).
@export var appearance: Dictionary = {}
@export var mass_kg := Tuning.ZOMBIE_MASS
## Stand still instead of chasing the player (test dummies).
@export var passive := false

var health := Tuning.ZOMBIE_HEALTH
var rig: HumanoidRig
var animator: PoseAnimator
var ragdoll: RagdollController
var hurtboxes: Array[Hurtbox] = []

var _speed := Tuning.ZOMBIE_SPEED
var _freeze_until := 0.0
var _hit_times: Array[float] = []
var _target: Node3D
var _nav: NavigationAgent3D
var _repath_left := 0.0
var _stuck_t := 0.0
var _unstick_left := 0.0
var _unstick_side := 1.0


func _ready() -> void:
	add_to_group(&"zombies")
	var app := appearance if not appearance.is_empty() else _random_appearance()
	var h := float(app.get("height", 1.0))
	var w := float(app.get("width", 1.0))
	_speed = Tuning.ZOMBIE_SPEED * randf_range(0.8, 1.25)
	collision_layer = Layers.CAPSULE
	collision_mask = Layers.MASK_CAPSULE
	var cap := CollisionShape3D.new()
	cap.name = "Capsule"
	var cs := CapsuleShape3D.new()
	cs.radius = 0.3 * w
	cs.height = 1.8 * h
	cap.shape = cs
	cap.position = Vector3(0, 0.9 * h, 0)
	add_child(cap)
	rig = HumanoidRig.new()
	rig.name = "Rig"
	add_child(rig)
	rig.build(app, mass_kg)
	animator = PoseAnimator.new()
	animator.name = "PoseAnimator"
	add_child(animator)
	animator.setup(rig)
	animator.set_locomotion_style(&"limp")
	animator.set_upper_overlay(&"zombie_reach")
	ragdoll = RagdollController.new()
	ragdoll.name = "RagdollController"
	add_child(ragdoll)
	ragdoll.setup(self, rig, animator, true)
	hurtboxes = Hurtbox.build_for(rig, self)
	_nav = NavigationAgent3D.new()
	_nav.name = "NavigationAgent3D"
	_nav.radius = 0.3
	_nav.height = 1.8
	_nav.path_desired_distance = 0.7
	_nav.target_desired_distance = Tuning.ZOMBIE_STOP_DIST
	add_child(_nav)
	_repath_left = randf() * REPATH


func _random_appearance() -> Dictionary:
	return {
		"skin": SKINS.pick_random(),
		"shirt": SHIRTS.pick_random(),
		"pants": PANTS.pick_random(),
		"height": randf_range(0.94, 1.06),
		"width": randf_range(0.95, 1.1),
	}


func is_dead() -> bool:
	return health <= 0.0


## Hitstop (TimeDirector.hitstop calls this): the animation stops and the
## RagdollController holds its bodies while is_frozen() is true.
func freeze_hitstop(duration_real: float) -> void:
	if duration_real <= 0.0:
		return
	_freeze_until = maxf(_freeze_until, TimeDirector.now() + duration_real)
	animator.time_scale = 0.0


func is_frozen() -> bool:
	return TimeDirector.now() < _freeze_until


func get_actor_time() -> float:
	return 0.0 if is_frozen() else 1.0


## A punch landed on `bone`, travelling along `direction`. `heavy` (a sprinting
## punch) knocks the zombie down. Returns the reaction: &"flinch", &"stumble",
## &"stagger", &"knockdown" or &"kill" (the caller sizes the hitstop by it).
func take_punch(bone: StringName, direction: Vector3, hit_point: Vector3, heavy: bool) -> StringName:
	if is_dead():
		ragdoll.flinch(direction, bone)   # knocks the corpse's hit bone about
		return &"flinch"
	health -= Tuning.PUNCH_DAMAGE * (Tuning.PUNCH_HEAD_MULT if bone == Bones.HEAD else 1.0)
	if health <= 0.0:
		_die(direction * Tuning.PUNCH_KILL_PUSH.x + Vector3.UP * Tuning.PUNCH_KILL_PUSH.y, hit_point, bone)
		return &"kill"
	if ragdoll.is_full_ragdoll():
		ragdoll.flinch(direction, bone)
		return &"flinch"
	var now := TimeDirector.now()
	_hit_times = _hit_times.filter(func(t: float) -> bool: return now - t < Tuning.PUNCH_COMBO_WINDOW)
	_hit_times.append(now)
	if heavy:
		_hit_times.clear()
		ragdoll.knockdown(direction, bone)
		return &"knockdown"
	if bone in LEG_BONES:
		ragdoll.stumble(direction, bone)
		return &"stumble"
	if _hit_times.size() >= Tuning.PUNCH_STAGGER_HITS:
		_hit_times.clear()
		ragdoll.stagger(direction)
		return &"stagger"
	ragdoll.flinch(direction, bone)
	return &"flinch"


func _die(velocity_change: Vector3, hit_point: Vector3, bone: StringName) -> void:
	health = 0.0
	ragdoll.launch(velocity_change, hit_point, bone)
	ragdoll.kill()
	died.emit(self)


func _physics_process(delta: float) -> void:
	if _freeze_until > 0.0 and not is_frozen():
		_freeze_until = 0.0
		animator.time_scale = 1.0
	if ragdoll.is_simulating() or is_frozen():
		return
	if ragdoll.state == RagdollController.State.GETUP:
		velocity = Vector3.ZERO
		return
	var wish := Vector3.ZERO
	var target := _find_target()
	if target and not passive:
		var to := target.global_position - global_position
		to.y = 0.0
		var dist := to.length()
		if dist > Tuning.ZOMBIE_STOP_DIST:
			to = _steer(target.global_position, delta)
		if dist > 0.01 and dist < Tuning.ZOMBIE_SIGHT and to.length_squared() > 1e-4:
			var dir := to.normalized()
			var face := Basis.looking_at(dir, Vector3.UP)
			global_basis = global_basis.orthonormalized().slerp(face, clampf(Tuning.ZOMBIE_TURN_SPEED * delta, 0.0, 1.0)).orthonormalized()
			if dist > Tuning.ZOMBIE_STOP_DIST:
				# Along the path, slower while still turning toward it (no corner cutting).
				wish = dir * _speed * lerpf(0.35, 1.0, clampf(dir.dot(-global_basis.z), 0.0, 1.0))
				wish = _unstick(wish, delta)
	var horizontal := Vector3(velocity.x, 0.0, velocity.z).lerp(wish, 1.0 - exp(-6.0 * delta))
	velocity.x = horizontal.x
	velocity.z = horizontal.z
	velocity.y = -0.5 if is_on_floor() else velocity.y - get_gravity().length() * delta
	move_and_slide()
	animator.set_locomotion(global_basis.inverse() * velocity, Tuning.ZOMBIE_SPEED)


## Side-steps for a moment when the zombie has been pushing into something.
func _unstick(wish: Vector3, delta: float) -> Vector3:
	if _unstick_left > 0.0:
		_unstick_left -= delta
		return wish.cross(Vector3.UP).normalized() * _speed * _unstick_side + wish * 0.3
	var moving := Vector2(velocity.x, velocity.z).length()
	_stuck_t = _stuck_t + delta if moving < STUCK_SPEED else 0.0
	if _stuck_t > STUCK_AFTER:
		_stuck_t = 0.0
		_unstick_left = UNSTICK_TIME
		_unstick_side = -_unstick_side
	return wish


## Flat direction to walk toward `goal`: along the navigation path when the
## level has a navigation mesh, else straight at it.
func _steer(goal: Vector3, delta: float) -> Vector3:
	var straight := Vector3(goal.x - global_position.x, 0.0, goal.z - global_position.z)
	if NavigationServer3D.map_get_iteration_id(_nav.get_navigation_map()) == 0:
		return straight
	_repath_left -= delta
	if _repath_left <= 0.0:
		_repath_left = REPATH
		_nav.target_position = goal
	var next := _nav.get_next_path_position()   # also refreshes the path
	if _nav.get_current_navigation_path().is_empty():
		return straight
	var to := Vector3(next.x - global_position.x, 0.0, next.z - global_position.z)
	return to if to.length_squared() > 0.01 else straight


func _find_target() -> Node3D:
	if not is_instance_valid(_target):
		_target = get_tree().get_first_node_in_group(&"player") as Node3D
	return _target
