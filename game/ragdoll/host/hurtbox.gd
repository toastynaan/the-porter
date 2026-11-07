class_name Hurtbox
extends Area3D
## One hittable part of a body: rides a bone's BoneAttachment3D (so it follows
## the animation and the ragdoll alike) with the bone's physical-body shape.
## Melee and, later, gunfire find it with ray queries on Layers.HURTBOX.

var host: Node
var bone: StringName

## Builds one hurtbox per physical bone of `rig`, owned by `p_host`. `grow`
## inflates the shapes a little so near-misses on thin limbs still count.
static func build_for(rig: HumanoidRig, p_host: Node, grow := 1.15) -> Array[Hurtbox]:
	var out: Array[Hurtbox] = []
	for b in Bones.PHYSICAL:
		var pb := rig.get_physical_bone(b)
		var src := pb.get_node_or_null(^"Shape") as CollisionShape3D if pb else null
		if src == null or src.shape == null:
			continue
		var hb := Hurtbox.new()
		hb.name = "Hurtbox_" + String(b)
		hb.host = p_host
		hb.bone = b
		hb.collision_layer = Layers.HURTBOX
		hb.collision_mask = 0
		hb.monitoring = false
		var cs := CollisionShape3D.new()
		cs.shape = _grown(src.shape, grow)
		hb.add_child(cs)
		hb.transform = rig.get_body_offset(b)
		rig.get_attachment(b).add_child(hb)
		out.append(hb)
	return out

static func _grown(shape: Shape3D, k: float) -> Shape3D:
	if shape is BoxShape3D:
		var b := BoxShape3D.new()
		b.size = (shape as BoxShape3D).size * k
		return b
	if shape is SphereShape3D:
		var s := SphereShape3D.new()
		s.radius = (shape as SphereShape3D).radius * k
		return s
	if shape is CapsuleShape3D:
		var c := CapsuleShape3D.new()
		c.radius = (shape as CapsuleShape3D).radius * k
		c.height = (shape as CapsuleShape3D).height * k
		return c
	return shape
