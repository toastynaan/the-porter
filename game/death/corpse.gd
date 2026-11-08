class_name Corpse
extends CharacterBody3D
## A body that falls (docs/full-game-run.md, "Deaths and bodies": the body
## falls as a ragdoll, the kept ragdoll system). It stands as a figure on the
## ragdoll rig (game/ragdoll) in the victim's colours until fall() or
## lie_dead(); then it goes limp on Layers.DEAD_BODY and stays where it came
## to rest. Host contract (RagdollController): a direct child
## CollisionShape3D named "Capsule"; no move_and_slide while simulating;
## is_frozen() and get_actor_time() for hitstop.

signal settled

## Keys as HumanoidRig.build: skin, shirt, pants, height, width. A habit by
## default.
@export var appearance := {"skin": Color(0.78, 0.66, 0.55), "shirt": Color("#1E1B19"),
	"pants": Color("#1E1B19"), "height": 1.0, "width": 1.0}
@export var mass_kg := 70.0

var rig: HumanoidRig
var animator: PoseAnimator
var ragdoll: RagdollController
var dead := false


func _ready() -> void:
	add_to_group(&"corpses")
	collision_layer = 0
	collision_mask = Layers.WORLD
	var h := float(appearance.get("height", 1.0))
	var w := float(appearance.get("width", 1.0))
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
	rig.build(appearance, mass_kg)
	animator = PoseAnimator.new()
	animator.name = "PoseAnimator"
	add_child(animator)
	animator.setup(rig)
	ragdoll = RagdollController.new()
	ragdoll.name = "RagdollController"
	add_child(ragdoll)
	ragdoll.setup(self, rig, animator, true)
	ragdoll.settled.connect(settled.emit)


## Falls dead now, pushed by `push` (m/s), struck at `bone`.
func fall(push := Vector3.ZERO, bone := Bones.CHEST) -> void:
	if dead:
		return
	dead = true
	ragdoll.launch(push, global_position + Vector3.UP * 1.2, bone)
	ragdoll.kill()


## Already dead where it lies (a body found): falls with no push.
func lie_dead() -> void:
	fall(Vector3(0.0, 0.0, 0.3))


func is_settled() -> bool:
	return dead and ragdoll.is_settled()


func is_frozen() -> bool:
	return false


func get_actor_time() -> float:
	return 1.0


## Where the body is now (its chest), for looking at it.
func centre() -> Vector3:
	return rig.get_bone_global_transform(Bones.CHEST).origin if rig else global_position + Vector3.UP


func _physics_process(_delta: float) -> void:
	if ragdoll and ragdoll.is_simulating():
		return
	velocity = Vector3.ZERO
