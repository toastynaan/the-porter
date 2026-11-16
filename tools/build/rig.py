"""The people's skeleton, and the clips they move by (tools/build/people.py
uses it). Look and Feel, "Characters"; docs/systems/assets.md, "People".

Every character is built on one skeleton: that of Quaternius's Universal
Animation Library (art/anim/ual1.glb and ual2.glb, CC0), its bones named as
Unreal's mannequin (root, pelvis, spine_01..03, neck_01, Head, clavicle_l,
upperarm_l, lowerarm_l, hand_l, thigh_l, calf_l, foot_l, ball_l, and _r).

- rig(spec): the library's skeleton turned to face -Z, scaled to his height,
  its arms lowered from the library's T-pose to hang at his sides, the pose
  his model is made in; his shoulders and hips set as wide as his build
  (`shoulders_wide`, `hips_wide`). JOINTS then has where his joints are,
  standing.
- skin(armature): every model in the file bound to it. Arms and legs bind
  bone by bone; the body by height (pelvis, spine_01..03), the skirt of a
  gown from the hips down to the thighs (below the knee, half to the
  calves), blended; a cloak only to the body;
  a vertex tagged "bone:<name>" to that bone alone (what a hand holds, a pack).
- clips(spec, armature): the clips he needs, from the library, made his: each
  bone turned as the library's is (so his own lengths are kept), the hips
  where the library's are. A seated clip has the seat at the origin, and his
  feet (and hands, if given) where the spec puts them. His `stoop` (degrees)
  bends his back in every clip.

Space: as people.py, the game's (metres, +Y up, facing -Z, his right +X);
Blender's is (x, -z, y).
"""
import math
import os

import bpy
from mathutils import Matrix, Quaternion, Vector

import porter

ANIM = os.path.join(porter.ROOT, "art", "anim")
LIBRARIES = ("ual1.glb", "ual2.glb")
## The library's figure has its neck (neck_01's head) at this height; ours at
## NECK for a spec's height 1.0 (the 1.75 m figure people.py dresses).
LIBRARY_NECK = 1.488
NECK = 1.47
## How far his arms hang out from straight down, standing at rest *(mine)*.
ARM_OUT = math.radians(8.0)
## Seated: his hips this far above the seat and behind its origin *(mine)*.
HIPS_ABOVE_SEAT = 0.075
HIPS_BEHIND_SEAT = 0.03
## The clips every character has (name: the library's clip).
CLIPS = {"idle": {"from": "Idle_Loop"}, "talk": {"from": "Idle_Talking_Loop"}, "walk": {"from": "Walk_Loop"}}

## His joints standing (the game's space), set by rig(): neck, head (the
## skull's pivot), shoulder, elbow, wrist, hand (the end of the hand), hip,
## knee, ankle, ball (the ball of the foot); given for his right side.
JOINTS = {}


def g2b(p):
    return Vector((p[0], -p[2], p[1]))


def b2g(v):
    return (v.x, v.z, -v.y)


def _select(obj):
    bpy.context.view_layer.update()
    for o in bpy.context.scene.objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def _fcurves(action):
    """Every F-curve of an action (Blender's layered actions)."""
    out = []
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                out.extend(bag.fcurves)
    return out


def _import_libraries():
    """The library's skeleton (one armature, its mannequin mesh dropped) and
    its clips by name, from every file."""
    arm = None
    clips = {}
    for name in LIBRARIES:
        before = set(bpy.data.objects)
        had = set(bpy.data.actions)
        bpy.ops.import_scene.gltf(filepath=os.path.join(ANIM, name))
        new = [o for o in bpy.data.objects if o not in before]
        for a in bpy.data.actions:
            if a not in had:
                clips.setdefault(a.name.split(".")[0], a)
        for o in new:
            if o.type == "ARMATURE" and arm is None:
                arm = o
            else:
                bpy.data.objects.remove(o, do_unlink=True)
    return arm, clips


def rig(spec):
    """His skeleton (an armature named Skeleton) and the library's, both
    turned and scaled to him; returns (his, the library's, its clips)."""
    src, library = _import_libraries()
    s = spec.get("height", 1.0) * NECK / LIBRARY_NECK
    src.name = "Library"
    # (The importer leaves it turning by quaternion: set the whole matrix.)
    src.matrix_world = Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Scale(s, 4)
    _select(src)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    # Applying the scale leaves the clips' moves in the old size.
    for a in library.values():
        for fc in _fcurves(a):
            if fc.data_path.endswith(".location"):
                for k in fc.keyframe_points:
                    k.co.y *= s
                    k.handle_left.y *= s
                    k.handle_right.y *= s
    arm = src.copy()
    arm.data = src.data.copy()
    arm.name = "Skeleton"
    arm.data.name = "Skeleton"
    arm.animation_data_clear()
    bpy.context.scene.collection.objects.link(arm)
    # His arms down from the library's T-pose, and that made his rest.
    _select(arm)
    bpy.ops.object.mode_set(mode="POSE")
    for side, sx in (("l", -1.0), ("r", 1.0)):
        pb = arm.pose.bones["upperarm_" + side]
        head = pb.bone.head_local
        now = (pb.bone.tail_local - head).normalized()
        want = g2b((sx * math.sin(ARM_OUT), -math.cos(ARM_OUT), 0.0))
        turn = now.rotation_difference(want).to_matrix().to_4x4()
        pb.matrix = Matrix.Translation(head) @ turn @ Matrix.Translation(-head) @ pb.bone.matrix_local
        bpy.context.view_layer.update()
    bpy.ops.pose.armature_apply(selected=False)
    # His own breadth: the arms out or in at the shoulders, the legs at the hips.
    wide = spec.get("shoulders_wide", 1.0)
    hips = spec.get("hips_wide", 1.0)
    if abs(wide - 1.0) > 1e-4 or abs(hips - 1.0) > 1e-4:
        bpy.ops.object.mode_set(mode="EDIT")
        ebs = arm.data.edit_bones
        for side, sx in (("l", -1.0), ("r", 1.0)):
            for root, k in (("upperarm_" + side, wide), ("thigh_" + side, hips)):
                dx = sx * abs(ebs[root].head.x) * (k - 1.0)
                for eb in [ebs[root]] + list(ebs[root].children_recursive):
                    eb.head.x += dx
                    eb.tail.x += dx
    bpy.ops.object.mode_set(mode="OBJECT")
    bones = arm.data.bones

    def at(name, end="head"):
        b = bones[name]
        return b2g(b.head_local if end == "head" else b.tail_local)

    JOINTS.clear()
    JOINTS.update({
        "neck": at("neck_01"), "head": at("Head"), "shoulder": at("upperarm_r"), "elbow": at("lowerarm_r"),
        "wrist": at("hand_r"), "hand": at("hand_r", "tail"), "hip": at("thigh_r"), "knee": at("calf_r"),
        "ankle": at("foot_r"), "ball": at("ball_r"),
    })
    return arm, src, library


# ------------------------------------------------------------------ binding

def _chain(p, links):
    """The bone of the link (bone, a, b) nearest the point."""
    best, bd = None, 1e9
    for bone, a, b in links:
        a, b = Vector(a), Vector(b)
        ab = b - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
        d = (p - (a + ab * t)).length
        if d < bd:
            best, bd = bone, d
    return {best: 1.0}


def _smooth(a, b, x):
    return porter.smoothstep(min(a, b), max(a, b), x) if a < b else 1.0 - porter.smoothstep(b, a, x)


def _torso(p, skirt=True):
    """The body by height: pelvis to spine_03, each blended into the next;
    below the hips, a skirt to the thighs (or the pelvis, for a cloak)."""
    bones = bpy.data.objects["Skeleton"].data.bones
    marks = [("pelvis", b2g(bones["pelvis"].head_local)[1] + 0.03), ("spine_01", b2g(bones["spine_01"].head_local)[1] + 0.04),
             ("spine_02", b2g(bones["spine_02"].head_local)[1] + 0.05), ("spine_03", b2g(bones["spine_03"].head_local)[1] + 0.06)]
    hip = JOINTS["hip"][1]
    y = p.y
    w = {}
    if y <= marks[0][1]:
        w = {"pelvis": 1.0}
    elif y >= marks[-1][1]:
        w = {"spine_03": 1.0}
    else:
        for (b0, y0), (b1, y1) in zip(marks, marks[1:]):
            if y0 <= y <= y1:
                t = (y - y0) / (y1 - y0)
                w = {b0: 1.0 - t, b1: t}
                break
    if skirt and y < hip:
        f = porter.smoothstep(0.0, 0.22, hip - y)
        right = porter.smoothstep(-0.07, 0.07, p.x)
        # A long skirt: below the knee it goes half with the calves.
        knee = JOINTS["knee"][1]
        shin = 0.5 * porter.smoothstep(0.0, 0.18, knee - y)
        w = {k: v * (1.0 - f) for k, v in w.items()}
        for side, share in (("r", right), ("l", 1.0 - right)):
            w["thigh_" + side] = w.get("thigh_" + side, 0.0) + f * share * (1.0 - shin)
            if shin > 0.0:
                w["calf_" + side] = w.get("calf_" + side, 0.0) + f * share * shin
    return w


def _links(part):
    """The bones an arm or a leg binds to, by its object's name (people.py:
    LegL, LegR, UpperArmL..., ForearmL...), or None."""
    side = "l" if part.endswith("L") else "r"
    sx = -1.0 if side == "l" else 1.0

    def j(k):
        p = JOINTS[k]
        return (p[0] * sx, p[1], p[2])

    if part.startswith("Leg"):
        toe = Vector(j("ball")) + Vector((0.0, 0.0, -0.1))
        return [("thigh_" + side, j("hip"), j("knee")), ("calf_" + side, j("knee"), j("ankle")),
                ("foot_" + side, j("ankle"), j("ball")), ("ball_" + side, j("ball"), tuple(toe))]
    if part.startswith("UpperArm") or part.startswith("Forearm"):
        return [("upperarm_" + side, j("shoulder"), j("elbow")), ("lowerarm_" + side, j("elbow"), j("wrist")),
                ("hand_" + side, j("wrist"), j("hand"))]
    return None


def skin(arm, keep_apart=()):
    """Binds every mesh in the file to the skeleton (see the top), and joins
    them into one, Body, but those named in `keep_apart`. Empties are dropped."""
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    empties = [o for o in bpy.data.objects if o.type == "EMPTY"]
    for o in meshes:
        tags = porter.TAGS.get(o.name, [None] * len(o.data.vertices))
        assert len(tags) == len(o.data.vertices), o.name
        links = _links(o.name)
        groups = {}
        mw = o.matrix_world
        for v, tag in zip(o.data.vertices, tags):
            p = Vector(b2g(mw @ v.co))
            if tag and tag.startswith("bone:"):
                w = {tag[5:]: 1.0}
            elif links:
                w = _chain(p, links)
            else:
                w = _torso(p, skirt=tag != "cloak")
            for bone, x in w.items():
                if x <= 1e-4:
                    continue
                g = groups.get(bone) or o.vertex_groups.new(name=bone)
                groups[bone] = g
                g.add([v.index], x, "REPLACE")
    # Everything where it is, unparented, its transforms applied.
    for o in meshes:
        mw = o.matrix_world.copy()
        o.parent = None
        o.matrix_world = mw
    for e in empties:
        e.parent = None
    _select(meshes[0])
    for o in meshes:
        o.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    body = [o for o in meshes if o.name not in keep_apart]
    _select(body[0])
    for o in body:
        o.select_set(True)
    if len(body) > 1:
        bpy.ops.object.join()
    bpy.context.view_layer.objects.active.name = "Body"
    for o in [o for o in bpy.data.objects if o.type == "MESH"]:
        o.parent = arm
        mod = o.modifiers.new("Skeleton", "ARMATURE")
        mod.object = arm
    for e in empties:
        bpy.data.objects.remove(e, do_unlink=True)


# -------------------------------------------------------------------- clips

def _order(arm):
    out = []
    todo = [b for b in arm.data.bones if b.parent is None]
    while todo:
        b = todo.pop(0)
        out.append(b)
        todo.extend(b.children)
    return out


def _frame(d, n):
    """A rotation matrix whose columns are d, n (made square to d) and d x n."""
    d = d.normalized()
    n = (n - d * n.dot(d)).normalized()
    return Matrix((d, n, d.cross(n))).transposed()


def _bend(a, c, l1, l2, pole):
    """The middle joint of a limb from a to c (l1, l2 long), bent toward pole."""
    d = c - a
    dist = min(max(d.length, abs(l1 - l2) + 1e-3), l1 + l2 - 1e-4)
    d.normalize()
    along = (l1 * l1 - l2 * l2 + dist * dist) / (2.0 * dist)
    h = math.sqrt(max(l1 * l1 - along * along, 0.0))
    side = (pole - d * pole.dot(d)).normalized()
    return a + d * along + side * h


def _limb(rest, rot, pos, upper, lower, end, target, pole, facing):
    """Turns a limb (upper, lower bones; `end` the point it reaches with)
    so its end is at `target`, the middle joint bent toward `pole`. `facing`
    is the way the middle joint points at rest (a knee forward, an elbow back)."""
    a = pos[upper]
    m0, e0 = rest[lower].translation, end
    a0 = rest[upper].translation
    l1, l2 = (m0 - a0).length, (e0 - m0).length
    mid = _bend(a, target, l1, l2, pole)
    out = (mid - (a + (target - a) * ((mid - a).dot(target - a) / max((target - a).length_squared, 1e-9))))
    out = out.normalized() if out.length > 1e-6 else pole.normalized()
    turn_u = _frame(mid - a, out) @ _frame(m0 - a0, facing).transposed()
    turn_l = _frame(target - mid, out) @ _frame(e0 - m0, facing).transposed()
    rot[upper] = (turn_u @ rest[upper].to_3x3()).to_quaternion()
    rot[lower] = (turn_l @ rest[lower].to_3x3()).to_quaternion()
    return turn_l


## A stoop bends the back at these bones, each by this share of it; the
## head lifts again by HEAD_UP of the whole, to look ahead.
STOOP = {"spine_01": 0.2, "spine_02": 0.3, "spine_03": 0.35, "neck_01": 0.15}
HEAD_UP = 0.75


def _stoop(spec, order, rot):
    """His posture, in every clip: `stoop` degrees his back bends forward
    (a hunched old man 30 or more). His arms still hang as the clip has them."""
    deg = spec.get("stoop", 0.0)
    if abs(deg) < 0.01:
        return
    bent = {}
    for b in order:
        up = bent.get(b.parent.name, 0.0) if b.parent else 0.0
        if b.name.startswith("clavicle") or b.name.startswith("thigh"):
            up = 0.0
        if b.name == "Head":
            up -= deg * HEAD_UP
        bent[b.name] = up + deg * STOOP.get(b.name, 0.0)
    for name, a in bent.items():
        if abs(a) > 0.01:
            # Forward is Blender's +Y: a turn about X by -a tips the top of him forward.
            rot[name] = Quaternion((1.0, 0.0, 0.0), math.radians(-a)) @ rot[name]


def clips(spec, arm, src, library):
    """Bakes his clips (CLIPS and the spec's "clips") onto his skeleton as
    actions of their names; then drops the library."""
    wanted = dict(CLIPS)
    wanted.update(spec.get("clips", {}))
    if spec.get("only_clips"):
        # The kit's catalogue: he only stands.
        wanted = {k: v for k, v in wanted.items() if k in spec["only_clips"]}
    order = _order(arm)
    rest = {b.name: b.matrix_local.copy() for b in arm.data.bones}
    scene = bpy.context.scene
    src.animation_data_create()
    made = []
    for name, c in wanted.items():
        act = library[c["from"]]
        src.animation_data.action = act
        if len(act.slots):
            src.animation_data.action_slot = act.slots[0]
        f0, f1 = act.frame_range
        n = max(1, int(round(f1 - f0)))
        frames = [f0 + (f1 - f0) * i / n for i in range(n + 1)]
        samples = {b.name: [] for b in order}
        hips = []
        offset = None
        for f in frames:
            scene.frame_set(int(math.floor(f)), subframe=f - math.floor(f))
            ev = src.evaluated_get(bpy.context.evaluated_depsgraph_get())
            pose = {b.name: ev.pose.bones[b.name].matrix.copy() for b in order}
            rot = {k: m.to_quaternion() for k, m in pose.items()}
            _stoop(spec, order, rot)
            pos = {}
            hip = pose["pelvis"].translation.copy()
            if "seat" in c:
                if offset is None:
                    want = g2b((0.0, c["seat"] + HIPS_ABOVE_SEAT, HIPS_BEHIND_SEAT))
                    offset = want - hip
                hip = hip + offset

            def place(b):
                if b.parent is None:
                    pos[b.name] = pose[b.name].translation.copy()
                elif b.name == "pelvis":
                    pos[b.name] = hip
                else:
                    p = b.parent.name
                    parent = Matrix.LocRotScale(pos[p], rot[p], None)
                    pos[b.name] = parent @ (rest[p].inverted() @ rest[b.name]).translation

            for b in order:
                place(b)
            # A seated clip's legs (and hands) where the spec puts them.
            for side, sx in (("l", -1.0), ("r", 1.0)):
                if "ankle" in c:
                    ax, ay, az = c["ankle"]
                    knee = c.get("knee", (0.0, 1.0, -0.4))
                    _limb(rest, rot, pos, "thigh_" + side, "calf_" + side, rest["foot_" + side].translation,
                          g2b((ax * sx, ay, az)), g2b((knee[0] * sx, knee[1], knee[2])), g2b((0.0, 0.0, -1.0)))
                    for k in ("foot_", "ball_"):
                        rot[k + side] = rest[k + side].to_quaternion()
                if "wrist" in c:
                    wx, wy, wz = c["wrist"]
                    elbow = c.get("elbow", (0.6, -0.3, 0.5))
                    turn = _limb(rest, rot, pos, "upperarm_" + side, "lowerarm_" + side, rest["hand_" + side].translation,
                                 g2b((wx * sx, wy, wz)), g2b((elbow[0] * sx, elbow[1], elbow[2])), g2b((0.0, 0.0, 1.0)))
                    rot["hand_" + side] = (turn @ rest["hand_" + side].to_3x3()).to_quaternion()
            if "ankle" in c or "wrist" in c:
                for b in order:
                    place(b)
            for b in order:
                k = b.name
                m = Matrix.LocRotScale(pos[k], rot[k], None)
                if b.parent is None:
                    local = rest[k].inverted() @ m
                else:
                    p = b.parent.name
                    parent = Matrix.LocRotScale(pos[p], rot[p], None)
                    local = (rest[p].inverted() @ rest[k]).inverted() @ parent.inverted() @ m
                samples[k].append(local)
        made.append(_write(arm, name, frames, samples))
    src.animation_data.action = None
    arm.animation_data.action = None
    for a in list(bpy.data.actions):
        if a not in made:
            bpy.data.actions.remove(a)
    bpy.data.objects.remove(src, do_unlink=True)
    for pb in arm.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
    return made


def _write(arm, name, frames, samples):
    """An action `name` on the skeleton: each bone's rotation at each frame,
    and the hips' place."""
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    arm.animation_data_create()
    arm.animation_data.action = act
    for bone, mats in samples.items():
        qs = []
        prev = None
        for m in mats:
            q = m.to_quaternion()
            if prev is not None and q.dot(prev) < 0.0:
                q.negate()
            qs.append(q)
            prev = q
        channels = [("rotation_quaternion", [[q[i] for q in qs] for i in range(4)])]
        if bone in ("pelvis", "root"):
            channels.append(("location", [[m.translation[i] for m in mats] for i in range(3)]))
        for prop, comps in channels:
            for i, values in enumerate(comps):
                fc = act.fcurve_ensure_for_datablock(arm, 'pose.bones["%s"].%s' % (bone, prop), index=i, group_name=bone)
                fc.keyframe_points.add(len(frames))
                co = []
                for f, v in zip(frames, values):
                    co.extend((f, v))
                fc.keyframe_points.foreach_set("co", co)
                for k in fc.keyframe_points:
                    k.interpolation = "LINEAR"
                fc.update()
    return act


def posed(arm, clip, frame=0.0):
    """Each bone's matrix (the armature's space) in one of his clips."""
    act = bpy.data.actions[clip]
    arm.animation_data.action = act
    if len(act.slots):
        arm.animation_data.action_slot = act.slots[0]
    bpy.context.scene.frame_set(int(math.floor(frame)), subframe=frame - math.floor(frame))
    ev = arm.evaluated_get(bpy.context.evaluated_depsgraph_get())
    out = {pb.name: pb.matrix.copy() for pb in ev.pose.bones}
    arm.animation_data.action = None
    for pb in arm.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()
    return out


def at(pose, bone):
    """Where a bone's head is in a pose (posed()), in the game's space."""
    return b2g(pose[bone].translation)


def bind(obj, arm, bone, pose=None):
    """Binds a mesh (built where it is, unparented) wholly to one bone. With
    `pose` (posed()), it was made where it is in that pose, and goes with the
    bone back to its rest."""
    if pose is not None:
        obj.data.transform(arm.data.bones[bone].matrix_local @ pose[bone].inverted())
        obj.data.update()
    g = obj.vertex_groups.new(name=bone)
    g.add(list(range(len(obj.data.vertices))), 1.0, "REPLACE")
    obj.parent = arm
    obj.modifiers.new("Skeleton", "ARMATURE").object = arm


def carry(pose, arm, bone, point):
    """Where a point that goes with a bone (the game's space, at rest) is in
    a pose (posed())."""
    m = pose[bone] @ arm.data.bones[bone].matrix_local.inverted()
    return b2g(m @ g2b(point))
