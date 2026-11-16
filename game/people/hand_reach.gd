class_name HandReach
extends SkeletonModifier3D
## One arm of a PersonModel reaching for what its hand holds (the warden's
## lantern, his staff): after the clip has posed him, the upper arm and
## forearm turn (two bones, the elbow toward `elbow_toward`) so the hand's
## grip (GRIP along the hand from the wrist) is at the held thing's origin. If that
## is out of reach, the thing comes back into the hand, at the end of his arm.

## "r" or "l".
var side := &"r"
## What the hand holds; its origin is where the hand holds it.
var held: Node3D
## The PersonModel; elbow_toward is in its space.
var person: Node3D
var elbow_toward := Vector3(0.5, -1.0, 0.35)

## Where a hand holds, from the wrist along the hand (tools/build/people.py,
## standing_limbs).
const GRIP := 0.05

var _upper := -1
var _lower := -1
var _hand := -1
## Where the hand holds, in the hand bone's space (it runs from the wrist
## along the hand).
var _grip := Vector3(0.0, GRIP, 0.0)


func _ready() -> void:
	var sk := get_skeleton()
	if sk == null:
		return
	_upper = sk.find_bone("upperarm_" + side)
	_lower = sk.find_bone("lowerarm_" + side)
	_hand = sk.find_bone("hand_" + side)


func _process_modification_with_delta(_delta: float) -> void:
	var sk := get_skeleton()
	if sk == null or _upper < 0 or _lower < 0 or _hand < 0 or not is_instance_valid(held):
		return
	var up := sk.get_bone_global_pose(_upper)
	var low := sk.get_bone_global_pose(_lower)
	var hand := sk.get_bone_global_pose(_hand)
	var s := up.origin
	var e := low.origin
	var g := hand * _grip
	var l1 := s.distance_to(e)
	var l2 := e.distance_to(g)
	var to_skel := sk.global_transform.affine_inverse()
	var want := to_skel * held.global_position
	var to := want - s
	var dist := clampf(to.length(), absf(l1 - l2) + 0.01, l1 + l2 - 0.002)
	var dir := to.normalized()
	var pole := (to_skel.basis * person.global_basis * elbow_toward).normalized()
	var aside := (pole - dir * pole.dot(dir)).normalized()
	var along := (l1 * l1 - l2 * l2 + dist * dist) / (2.0 * dist)
	var elbow := s + dir * along + aside * sqrt(maxf(l1 * l1 - along * along, 0.0))
	var end := s + dir * dist
	var turn_up := Quaternion((e - s).normalized(), (elbow - s).normalized())
	var up2 := Transform3D(Basis(turn_up) * up.basis, s)
	var low1 := Transform3D(Basis(turn_up) * low.basis, elbow)
	var g1 := s + turn_up * (g - s)
	var turn_low := Quaternion((g1 - elbow).normalized(), (end - elbow).normalized())
	var low2 := Transform3D(Basis(turn_low) * low1.basis, elbow)
	var parent := sk.get_bone_parent(_upper)
	var parent_pose := sk.get_bone_global_pose(parent) if parent >= 0 else Transform3D.IDENTITY
	var up_local := parent_pose.affine_inverse() * up2
	var low_local := up2.affine_inverse() * low2
	sk.set_bone_pose_rotation(_upper, up_local.basis.get_rotation_quaternion())
	sk.set_bone_pose_rotation(_lower, low_local.basis.get_rotation_quaternion())
	if to.length() > dist + 0.005:
		# Out of reach: it is in his hand, at the end of his arm.
		held.global_position = sk.global_transform * end
