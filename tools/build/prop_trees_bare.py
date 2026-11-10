"""Bare winter trees (late autumn, 1420s London): what stands against the
sky on the road in. Each is grown, not drawn: a trunk that forks and forks
again, every branch wandering a little and reaching for the light, down to
twigs. Four of them, each its own model:

    prop_tree_elm      a tall hedgerow elm, about 13 m, its branches swept up
    prop_tree_oak      a broad, crooked field oak, about 10 m
    prop_tree_thorn    a wind-bent hawthorn, about 5 m
    prop_tree_pollard  a pollard willow by the ditch: a short thick trunk, a
                       knuckle of a head, a spray of straight shoots

Trunks are 7-sided, twigs 3-sided. Only the trunk is solid (a "-colonly"
post). Material: bark. Vertex colour darkens toward the twigs.

Run: tools/build.sh prop_trees_bare
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
from mathutils import Matrix, Vector

UP = Vector((0.0, 1.0, 0.0))


def perpendicular(v):
    other = Vector((1.0, 0.0, 0.0)) if abs(v.x) < 0.8 else Vector((0.0, 0.0, 1.0))
    return v.cross(other).normalized()


def tube(m, points, radii, sides, shade):
    """A tapering tube along `points` (game space), `sides` round."""
    rings = []
    side = perpendicular((points[1] - points[0]).normalized())
    length = 0.0
    for i, p in enumerate(points):
        ahead = (points[min(i + 1, len(points) - 1)] - points[max(i - 1, 0)]).normalized()
        # Carry the ring's frame along the branch so it doesn't twist.
        side = (side - ahead * side.dot(ahead)).normalized()
        other = ahead.cross(side)
        if i > 0:
            length += (p - points[i - 1]).length
        ring = []
        for s in range(sides):
            a = math.tau * s / sides
            q = p + (side * math.cos(a) + other * math.sin(a)) * radii[i]
            ring.append(m.vert(q.x, q.y, q.z, (shade, shade, shade, 1.0), (s / sides, length * 0.5)))
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        for s in range(sides):
            t = (s + 1) % sides
            m.face((a[s], a[t], b[t], b[s]), "bark")


def grow(m, start, direction, length, radius, depth, kind):
    """One branch and everything that grows from it."""
    steps = max(2, int(length / kind["step"]))
    d = direction.normalized()
    points = [start]
    for _ in range(steps):
        wander = Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))) * kind["wander"]
        lean = UP * kind["reach"][min(depth, len(kind["reach"]) - 1)] + kind["wind"] * (0.02 * depth)
        d = (d + wander + lean).normalized()
        points.append(points[-1] + d * (length / steps))
    last = depth >= kind["depth"]
    tip = radius * (0.12 if last else kind["taper"])
    radii = [porter.lerp(radius, tip, i / steps) for i in range(steps + 1)]
    sides = kind["sides"][min(depth, len(kind["sides"]) - 1)]
    tube(m, points, radii, sides, porter.lerp(1.0, 0.55, depth / max(kind["depth"], 1)))
    if last:
        return
    forks = kind["forks"][min(depth, len(kind["forks"]) - 1)]
    for k in range(forks):
        # Forks come off the upper part of the branch, turned round it in turn.
        at = random.uniform(kind["from"], 1.0) if k < forks - 1 else 1.0
        i = min(int(at * steps), steps)
        along = (points[min(i + 1, steps)] - points[max(i - 1, 0)]).normalized()
        out = Matrix.Rotation(math.tau * (k / forks + random.uniform(-0.12, 0.12)), 3, along) @ perpendicular(along)
        angle = math.radians(random.uniform(*kind["angle"])) * (0.35 if k == forks - 1 and at == 1.0 else 1.0)
        child = (along * math.cos(angle) + out * math.sin(angle)).normalized()
        grow(m, points[i], child, length * random.uniform(*kind["shrink"]), radii[i] * kind["thin"], depth + 1, kind)


def post(name, radius, height):
    """What you walk into: the trunk as a box."""
    c = porter.Mesh(name + "-colonly")
    c.box((-radius, 0.0, -radius), (radius, height, radius), "bark")
    c.build()


KINDS = {
    "elm": {"height": 5.2, "radius": 0.34, "depth": 5, "step": 0.55, "wander": 0.09, "taper": 0.62, "thin": 0.62,
            "reach": [0.05, 0.16, 0.2, 0.16, 0.1, 0.06], "wind": Vector((0.3, 0.0, 0.1)), "sides": [7, 6, 5, 4, 3, 3],
            "forks": [5, 4, 3, 3, 2], "from": 0.4, "angle": (20, 44), "shrink": (0.64, 0.84), "seed": 11},
    "oak": {"height": 3.1, "radius": 0.52, "depth": 5, "step": 0.5, "wander": 0.2, "taper": 0.66, "thin": 0.66,
            "reach": [0.0, 0.02, 0.05, 0.08, 0.06, 0.04], "wind": Vector((0.2, 0.0, 0.0)), "sides": [7, 6, 5, 4, 3, 3],
            "forks": [5, 4, 3, 3, 2], "from": 0.3, "angle": (36, 70), "shrink": (0.7, 0.9), "seed": 23},
    "thorn": {"height": 1.5, "radius": 0.16, "depth": 4, "step": 0.3, "wander": 0.24, "taper": 0.6, "thin": 0.64,
              "reach": [0.0, 0.03, 0.04, 0.02, 0.0], "wind": Vector((2.2, -0.3, 0.6)), "sides": [6, 5, 4, 3, 3],
              "forks": [3, 3, 3, 3], "from": 0.25, "angle": (30, 65), "shrink": (0.6, 0.82), "seed": 37},
}


def tree(kind_name):
    kind = KINDS[kind_name]
    porter.reset(kind["seed"])
    m = porter.Mesh("Tree")
    lean = Vector((random.uniform(-0.06, 0.06), 1.0, random.uniform(-0.06, 0.06)))
    # The root flare: a short thick foot under the trunk.
    tube(m, [Vector((0.0, -0.2, 0.0)), Vector((0.0, 0.25, 0.0))], [kind["radius"] * 1.6, kind["radius"] * 1.05], 7, 1.0)
    grow(m, Vector((0.0, 0.2, 0.0)), lean, kind["height"], kind["radius"], 0, kind)
    m.build(smooth=True)
    post("Trunk", kind["radius"] * 0.9, kind["height"])
    porter.export("prop_tree_" + kind_name)


def pollard():
    porter.reset(53)
    m = porter.Mesh("Tree")
    # A short trunk, leaning over the water, thickening into a head.
    points = [Vector((0.0, -0.2, 0.0)), Vector((0.02, 0.5, 0.0)), Vector((0.1, 1.3, 0.04)), Vector((0.22, 2.0, 0.08)),
              Vector((0.3, 2.45, 0.1)), Vector((0.33, 2.75, 0.1))]
    tube(m, points, [0.42, 0.3, 0.27, 0.3, 0.42, 0.3], 8, 1.0)
    head = points[-2]
    shoot = {"depth": 1, "step": 0.5, "wander": 0.04, "taper": 0.5, "thin": 0.5, "reach": [0.1, 0.12],
             "wind": Vector((0.5, 0.0, 0.2)), "sides": [3, 3], "forks": [1], "from": 0.5, "angle": (10, 25),
             "shrink": (0.4, 0.6)}
    for i in range(34):
        a = math.tau * (i / 34.0) + random.uniform(-0.2, 0.2)
        out = Vector((math.cos(a), 0.0, math.sin(a)))
        tilt = math.radians(random.uniform(8, 58))
        d = (UP * math.cos(tilt) + out * math.sin(tilt)).normalized()
        grow(m, head + out * 0.26 + UP * random.uniform(-0.05, 0.25), d, random.uniform(1.4, 2.7),
             random.uniform(0.025, 0.045), 0, shoot)
    m.build(smooth=True)
    post("Trunk", 0.3, 2.4)
    porter.export("prop_tree_pollard")


for name in KINDS:
    tree(name)
pollard()
