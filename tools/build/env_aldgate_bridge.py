"""Aldgate's bridge over the city ditch (night 0, the road in), in the
gate's own space (tools/build/env_aldgate.py: the wall along x, the country
at -z, the road through at x = 0).

- The drawbridge: an oak leaf from the gate's sill out to a stone pier,
  lowered. Two lifting beams (gaffs) stand out of slots over the arch, a
  chain from each tip down to the leaf's outer corners, a toothed wheel and
  its shaft on the gate's face beside each beam, ropes back to the wall.
- Beyond the pier, a fixed timber span on a trestle to the outer bank,
  with posts and rails (one length of rail gone), and two tall posts at the
  bridgehead; a lantern hangs from one (in env_road.tscn).
- Stone: the sill under the arch, the sides of the bay the ditch makes
  before the gate, the pier, the outer bank's abutment and its wing walls,
  and rocks along the water's edge.
- A raised frame of cut stone round the arch: the recess the leaf shuts
  into when it is drawn up.

The ditch and its water are the ground's (tools/build/env_road_fields.py).

Collision: the rails and the leaf's sides, so nobody walks off it.

Run: tools/build.sh env_aldgate_bridge
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
import city_parts as cp
from mathutils import Vector

ASHLAR = "stone_ashlar"
RUBBLE = "stone_rubble"
BOARDS = "wood_boards"
OAK = "wood_frame"
IRON = "iron_cart"
RUST = (0.5, 0.42, 0.36, 1.0)
DARK_IRON = (0.4, 0.38, 0.37, 1.0)

# The gate's face, and the leaf: from its hinge at the sill out to the pier; half its width.
FACE = -2.8
LEAF = (-3.0, -8.7)
HALF = 2.55
# The pier the leaf comes down on, the trestle, and the bank the fixed span ends on.
PIER = (-8.7, -9.8)
TRESTLE = -13.4
BANK = -17.6
# Down to the ditch's bottom.
DEEP = -2.9
# The lifting beams: how far each side of the road, the height of their pivot, and their tips.
GAFF_X, GAFF_Y = 2.0, 6.85
TIP = (8.15, -8.45)


def bar(m, a, b, w, h, mat, color, ends=True):
    """A squared timber from `a` to `b`, `w` wide and `h` deep."""
    a, b = Vector(a), Vector(b)
    along = (b - a).normalized()
    side = along.cross(Vector((0.0, 1.0, 0.0)))
    side = side.normalized() if side.length > 1e-4 else Vector((1.0, 0.0, 0.0))
    up = side.cross(along).normalized()
    c = color if isinstance(color, tuple) and len(color) == 4 else cp.rgba(color)
    corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    ring_a = [a + side * (sx * w * 0.5) + up * (sy * h * 0.5) for sx, sy in corners]
    ring_b = [b + side * (sx * w * 0.5) + up * (sy * h * 0.5) for sx, sy in corners]
    for i in range(4):
        j = (i + 1) % 4
        mid = (ring_a[i] + ring_a[j]) * 0.5 - a
        m.poly([tuple(ring_a[i]), tuple(ring_a[j]), tuple(ring_b[j]), tuple(ring_b[i])], mat, c, facing=tuple(mid))
    if ends:
        m.poly([tuple(p) for p in ring_a], mat, c, facing=tuple(-along))
        m.poly([tuple(p) for p in ring_b], mat, c, facing=tuple(along))


def chain(m, a, b, sag=0.0, link=0.21, r=0.045):
    """A chain from `a` to `b`: flat links, each turned a quarter from the last."""
    a, b = Vector(a), Vector(b)
    n = max(int((b - a).length / link), 2)
    pts = []
    for i in range(n + 1):
        t = i / n
        p = a.lerp(b, t)
        p.y -= sag * 4.0 * t * (1.0 - t)
        pts.append(p)
    for i in range(n):
        p, q = pts[i], pts[i + 1]
        over = (q - p) * 0.12
        shade = 0.85 + 0.3 * random.random()
        col = (RUST[0] * shade, RUST[1] * shade * 0.96, RUST[2] * shade * 0.92, 1.0)
        m.tube([tuple(p - over), tuple(q + over)], [r, r], 4, IRON, col, squash=(1.0, 0.32) if i % 2 else (0.32, 1.0))


def rope(m, a, b, sag, r=0.022):
    a, b = Vector(a), Vector(b)
    pts = []
    for i in range(7):
        t = i / 6.0
        p = a.lerp(b, t)
        p.y -= sag * 4.0 * t * (1.0 - t)
        pts.append(tuple(p))
    m.tube(pts, [r] * 7, 4, "sacking", (0.5, 0.46, 0.4, 1.0))


def planks(m, z0, z1, half, y, thick, seed, base=(0.74, 0.7, 0.64)):
    """A deck of boards laid across, each its own shade and none quite level."""
    random.seed(seed)
    z = z0
    step = -0.29 if z1 < z0 else 0.29
    while abs(z - z0) < abs(z1 - z0) - 0.02:
        zb = z + step
        if abs(zb - z0) > abs(z1 - z0):
            zb = z1
        k = random.uniform(0.72, 1.12)
        lift = random.uniform(-0.008, 0.01)
        over = random.uniform(-0.03, 0.05)
        col = (base[0] * k, base[1] * k, base[2] * k, 1.0)
        lo = (-half - over, y - thick, min(z, zb) + 0.012)
        hi = (half + random.uniform(-0.03, 0.05), y + lift, max(z, zb) - 0.012)
        cp.block(m, lo, hi, BOARDS, col, faces="xXzZY")
        z = zb
    # Its underside, one dark face.
    m.poly([(-half, y - thick, z0), (half, y - thick, z0), (half, y - thick, z1), (-half, y - thick, z1)], BOARDS, (0.16, 0.15, 0.15, 1.0),
           facing=(0, -1, 0))


def leaf(m):
    z0, z1 = LEAF
    planks(m, z0, z1, HALF, 0.0, 0.11, 5)
    dark = (0.36, 0.34, 0.32, 1.0)
    # The frame under it, a kerb along each edge, iron straps across, and the rings the chains take.
    for x in (-2.1, -0.7, 0.7, 2.1):
        cp.block(m, (x - 0.11, -0.4, z1), (x + 0.11, -0.11, z0), OAK, dark, faces="xXzZy")
    for s in (-1, 1):
        cp.block(m, (min(s * HALF, s * (HALF - 0.16)), 0.0, z1), (max(s * HALF, s * (HALF - 0.16)), 0.15, z0), OAK,
                 (0.44, 0.42, 0.4, 1.0), faces="xXzZY")
    for z in (z0 - 0.35, (z0 + z1) * 0.5, z1 + 0.3):
        cp.block(m, (-HALF - 0.03, 0.005, z - 0.05), (HALF + 0.03, 0.026, z + 0.05), IRON, DARK_IRON, faces="xXzZY")
        x = -HALF + 0.4
        while x < HALF - 0.3:
            cp.block(m, (x - 0.025, 0.026, z - 0.025), (x + 0.025, 0.045, z + 0.025), IRON, RUST, faces="xXzZY")
            x += 0.62
    for s in (-1, 1):
        x = s * (HALF - 0.08)
        cp.block(m, (x - 0.09, 0.15, z1 + 0.22), (x + 0.09, 0.33, z1 + 0.42), IRON, DARK_IRON, faces="xXzZY")
    # The end beam the chains lift by, standing out each side.
    cp.block(m, (-HALF - 0.3, -0.3, z1 - 0.02), (HALF + 0.3, -0.06, z1 + 0.24), OAK, (0.4, 0.38, 0.36, 1.0))


def gaffs(m):
    oak = (0.46, 0.43, 0.4, 1.0)
    for s in (-1, 1):
        x = s * GAFF_X
        back = (x, GAFF_Y - 0.12, FACE + 0.5)
        tip = (x, TIP[0], TIP[1])
        bar(m, back, tip, 0.3, 0.36, OAK, oak)
        # Iron at the tip and where it turns, and the slot it stands out of.
        d = (Vector(tip) - Vector(back)).normalized()
        for t, w in ((0.25, 0.36), (5.55, 0.36), (5.25, 0.35), (2.9, 0.345)):
            p = Vector(back) + d * (t + 0.55)
            bar(m, tuple(p - d * 0.06), tuple(p + d * 0.06), w, w + 0.06, IRON, DARK_IRON, ends=False)
        m.poly([(x - 0.3, GAFF_Y - 0.75, FACE - 0.012), (x + 0.3, GAFF_Y - 0.75, FACE - 0.012), (x + 0.3, GAFF_Y + 1.5, FACE - 0.012),
                (x - 0.3, GAFF_Y + 1.5, FACE - 0.012)], "window_dark", facing=(0, 0, -1))
        for xa in (x - 0.42, x + 0.3):
            cp.block(m, (xa, GAFF_Y - 0.85, FACE - 0.1), (xa + 0.12, GAFF_Y + 1.6, FACE), ASHLAR, cp.rgba(cp.STONE, 0.92), faces="xXzyY")
        cp.block(m, (x - 0.42, GAFF_Y + 1.5, FACE - 0.12), (x + 0.42, GAFF_Y + 1.68, FACE), ASHLAR, cp.rgba(cp.STONE, 0.95), faces="xXzyY")
        # The chain down to the leaf's corner, a spare length hanging, and a rope back to the wall.
        hang = Vector(tip) - d * 0.22 - Vector((0.0, 0.2, 0.0))
        foot = (s * (HALF - 0.08), 0.3, LEAF[1] + 0.32)
        chain(m, tuple(hang), foot)
        chain(m, tuple(hang + Vector((s * 0.06, 0.0, 0.3))), (x + s * 0.1, TIP[0] - 2.3, TIP[1] + 0.5), link=0.2, r=0.04)
        rope(m, (x, 9.75, FACE - 0.04), tuple(Vector(back) + d * 3.4 + Vector((0.0, 0.18, 0.0))), 0.35)
        m.tube([(x, 9.75, FACE - 0.1), (x, 9.75, FACE)], [0.05, 0.05], 5, IRON, DARK_IRON)


def wheel(m, cx, cy, z, r, teeth, thick):
    """A toothed wheel on the gate's face, turned to the road."""
    zf, zb = z - thick, z
    seg = teeth * 2
    rim_in, rim_out, tip = r * 0.72, r * 0.9, r
    col = RUST

    def at(a, rr, zz):
        return (cx + math.cos(a) * rr, cy + math.sin(a) * rr, zz)

    for i in range(seg):
        a0, a1 = math.tau * i / seg, math.tau * (i + 1) / seg
        k = 0.8 + 0.35 * ((i * 7) % 5) / 4.0
        c = (col[0] * k, col[1] * k, col[2] * k, 1.0)
        out = rim_out
        m.poly([at(a0, rim_in, zf), at(a1, rim_in, zf), at(a1, out, zf), at(a0, out, zf)], "wood_cart", (c[0] * 1.5, c[1] * 1.5, c[2] * 1.5, 1.0),
               facing=(0, 0, -1))
        mid = (a0 + a1) * 0.5
        m.poly([at(a0, out, zf), at(a1, out, zf), at(a1, out, zb), at(a0, out, zb)], IRON, DARK_IRON, facing=(math.cos(mid), math.sin(mid), 0))
        m.poly([at(a0, rim_in, zf), at(a1, rim_in, zf), at(a1, rim_in, zb), at(a0, rim_in, zb)], IRON, DARK_IRON,
               facing=(-math.cos(mid), -math.sin(mid), 0))
        if i % 2 == 0:
            # A tooth.
            b0, b1 = a0 + (a1 - a0) * 0.15, a1 - (a1 - a0) * 0.15
            m.poly([at(a0, out, zf), at(a1, out, zf), at(b1, tip, zf), at(b0, tip, zf)], IRON, c, facing=(0, 0, -1))
            m.poly([at(b0, tip, zf), at(b1, tip, zf), at(b1, tip, zb), at(b0, tip, zb)], IRON, DARK_IRON, facing=(math.cos(mid), math.sin(mid), 0))
            for aa, bb, sgn in ((a0, b0, -1), (a1, b1, 1)):
                m.poly([at(aa, out, zf), at(bb, tip, zf), at(bb, tip, zb), at(aa, out, zb)], IRON, DARK_IRON,
                       facing=(-math.sin(mid) * sgn, math.cos(mid) * sgn, 0))
    for k in range(6):
        a = math.tau * k / 6 + 0.2
        bar(m, at(a, 0.1, z - thick * 0.6), at(a, rim_in + 0.02, z - thick * 0.6), 0.1, thick * 0.7, IRON, DARK_IRON, ends=False)
    m.tube([(cx, cy, z - thick - 0.06), (cx, cy, z)], [0.15, 0.17], 8, IRON, RUST, caps=True)


def windlass(m):
    """Beside each beam: its wheel, the shaft through to the beam, a pinion and a crank under it."""
    for s in (-1, 1):
        cx = s * 3.3
        wheel(m, cx, GAFF_Y - 0.25, FACE - 0.1, 0.78, 14, 0.13)
        m.tube([(cx, GAFF_Y - 0.25, FACE - 0.3), (s * (GAFF_X + 0.16), GAFF_Y - 0.25, FACE - 0.3)], [0.07, 0.07], 6, IRON, DARK_IRON)
        m.tube([(cx, GAFF_Y - 0.25, FACE - 0.3), (cx, GAFF_Y - 0.25, FACE - 0.1)], [0.07, 0.07], 6, IRON, DARK_IRON)
        px, py = cx + s * 0.1, GAFF_Y - 1.22
        wheel(m, px, py, FACE - 0.1, 0.24, 7, 0.13)
        m.tube([(px, py, FACE - 0.42), (px, py, FACE - 0.1)], [0.04, 0.04], 5, IRON, DARK_IRON)
        m.tube([(px, py, FACE - 0.4), (px + s * 0.05, py - 0.4, FACE - 0.4), (px + s * 0.05, py - 0.4, FACE - 0.62)], [0.03, 0.03, 0.03], 5, IRON,
               DARK_IRON)
        # Iron brackets holding it all to the stone.
        for y in (GAFF_Y - 1.5, GAFF_Y + 0.7):
            cp.block(m, (cx - 0.5, y, FACE - 0.07), (cx + 0.5, y + 0.09, FACE), IRON, DARK_IRON, faces="xXzyY")


def span(m):
    """The fixed length from the pier to the bank: boards on three beams, a trestle under its middle, rails."""
    z0, z1 = PIER[0], BANK
    planks(m, z0, z1, HALF + 0.05, 0.0, 0.11, 9, base=(0.68, 0.65, 0.6))
    dark = (0.34, 0.32, 0.3, 1.0)
    for x in (-2.0, 0.0, 2.0):
        cp.block(m, (x - 0.14, -0.45, z1 - 0.3), (x + 0.14, -0.11, z0), OAK, dark, faces="xXzZy")
    # The trestle: three piles, a cap, braces crossed between them. Green where the water takes them.
    z = TRESTLE
    for x in (-2.3, 0.0, 2.3):
        lean = x * 0.06
        cols = [(0.25, 0.3, 0.2, 1.0), (0.3, 0.32, 0.25, 1.0), (0.4, 0.38, 0.36, 1.0)]
        m.tube([(x + lean, DEEP, z), (x + lean * 0.4, -1.3, z), (x, -0.45, z)], [0.17, 0.15, 0.14], 7, OAK, cols)
    cp.block(m, (-2.75, -0.63, z - 0.15), (2.75, -0.45, z + 0.15), OAK, dark)
    for a, b in (((-2.3, -0.7, z + 0.16), (0.0, -2.0, z + 0.16)), ((2.3, -0.7, z + 0.16), (0.0, -2.0, z + 0.16)),
                 ((-2.4, -1.9, z - 0.16), (0.0, -0.75, z - 0.16)), ((2.4, -1.9, z - 0.16), (0.0, -0.75, z - 0.16))):
        bar(m, a, b, 0.07, 0.16, OAK, dark, ends=False)
    # Rails: posts, a top rail and one under it. One length of the lower rail is gone, and a post leans.
    random.seed(3)
    oak = lambda: (0.4 * random.uniform(0.8, 1.15), 0.38 * random.uniform(0.8, 1.15), 0.36 * random.uniform(0.8, 1.15), 1.0)
    zs = cp.steps(z0 - 0.25, z1 + 0.25, 1.55)
    for s in (-1, 1):
        x = s * (HALF + 0.1)
        tops = []
        for i, zz in enumerate(zs):
            tall = i == len(zs) - 1
            tip = (x + s * (0.1 if (i == 3 and s < 0) else random.uniform(-0.02, 0.03)), 2.6 if tall else 1.08, zz + random.uniform(-0.03, 0.03))
            bar(m, (x, -0.42, zz), tip, 0.15 if tall else 0.12, 0.15 if tall else 0.12, OAK, oak())
            tops.append(tip)
            if tall:
                # A cap, and an arm for a lantern on the north one.
                cp.block(m, (tip[0] - 0.11, 2.6, zz - 0.11), (tip[0] + 0.11, 2.68, zz + 0.11), OAK, (0.3, 0.29, 0.28, 1.0))
                if s > 0:
                    bar(m, (tip[0], 2.32, zz), (tip[0] - 0.62, 2.42, zz), 0.07, 0.08, OAK, (0.3, 0.29, 0.28, 1.0))
                    bar(m, (tip[0], 1.95, zz), (tip[0] - 0.38, 2.36, zz), 0.05, 0.06, OAK, (0.3, 0.29, 0.28, 1.0), ends=False)
        for i in range(len(zs) - 1):
            a, b = tops[i], tops[i + 1]
            ya, yb = min(a[1], 1.08), min(b[1], 1.08)
            bar(m, (a[0], ya - 0.06, a[2] - 0.08), (b[0], yb - 0.06, b[2] + 0.08), 0.09, 0.11, OAK, oak(), ends=True)
            if not (s > 0 and i == 2):
                bar(m, (x, 0.52, a[2]), (x, 0.52 + random.uniform(-0.03, 0.03), b[2]), 0.06, 0.1, OAK, oak(), ends=False)
            elif True:
                # What is left of it, hanging by one end.
                bar(m, (x, 0.52, a[2]), (x + 0.05, 0.12, a[2] - 0.75), 0.06, 0.1, OAK, oak())


def rock(m, x, y, z, r):
    k = random.uniform(0.75, 1.1)
    damp = [(0.3 * k, 0.34 * k, 0.27 * k, 0.25), (0.45 * k, 0.47 * k, 0.42 * k, 0.5), (0.62 * k, 0.61 * k, 0.58 * k, 0.9),
            (0.66 * k, 0.65 * k, 0.62 * k, 1.0)]
    lean = random.uniform(-0.25, 0.25) * r
    m.tube([(x, y - 0.4 * r, z), (x + lean * 0.4, y + 0.15 * r, z), (x + lean, y + 0.6 * r, z + lean * 0.5), (x + lean, y + 0.8 * r, z + lean * 0.5)],
           [r, r * random.uniform(0.9, 1.1), r * random.uniform(0.55, 0.75), r * 0.2], 6, RUBBLE, damp, caps=True,
           squash=(random.uniform(0.7, 1.0), random.uniform(0.7, 1.0)))


def stone(m):
    tint = cp.stone_tint(DEEP, 0.3, seed=11.0, worn=0.9)
    # The sill under the arch and the bay's two sides, capped.
    cp.slab(m, (-3.55, DEEP, LEAF[0] - 0.25), (3.55, -0.03, FACE + 0.05), ASHLAR, tint, faces="zY", step=1.4)
    for s in (-1, 1):
        lo = (min(s * 3.25, s * 3.75), DEEP, -5.9)
        hi = (max(s * 3.25, s * 3.75), 0.16, LEAF[0] - 0.25)
        cp.slab(m, lo, hi, ASHLAR, tint, faces="xXzY", step=1.4)
        cp.block(m, (lo[0] - 0.05, 0.16, lo[2] - 0.05), (hi[0] + 0.05, 0.3, hi[2]), ASHLAR, cp.rgba(cp.STONE, 0.9), faces="xXzyY")
    # The pier, with a cutwater to each side and a string course.
    cp.slab(m, (-3.0, DEEP, PIER[1]), (3.0, -0.12, PIER[0] + 0.25), ASHLAR, tint, faces="zZY", step=1.4)
    for s in (-1, 1):
        zc = (PIER[0] + 0.25 + PIER[1]) * 0.5
        for za, zb, f in ((PIER[1], zc, -1), (zc, PIER[0] + 0.25, 1)):
            pts = [(s * 3.0, DEEP, za if f < 0 else zb), (s * 3.75, DEEP, zc), (s * 3.75, -0.5, zc), (s * 3.0, -0.12, za if f < 0 else zb)]
            m.poly(pts, ASHLAR, [tint(*p) for p in pts], facing=(s, 0, f))
    cp.block(m, (-3.08, -0.3, PIER[1] - 0.06), (3.08, -0.12, PIER[0] + 0.31), ASHLAR, cp.rgba(cp.STONE, 0.85), faces="xXzZyY")
    # The outer bank: an abutment under the span's end, and wing walls splayed back into the bank.
    cp.slab(m, (-3.6, DEEP, BANK - 0.9), (3.6, -0.03, BANK + 0.25), ASHLAR, tint, faces="ZY", step=1.4)
    for s in (-1, 1):
        a, b = (s * 3.2, BANK + 0.25), (s * 5.4, BANK - 1.6)
        for out in ((0.4 * s, 0, 1), (-0.4 * s, 0, -1)):
            cp.panel(m, a, b, DEEP, 0.55, out, RUBBLE, tint, 1.4, 1.2)
        pts = [(a[0], 0.55, a[1] + 0.2), (b[0], 0.55, b[1] + 0.2), (b[0], 0.55, b[1] - 0.2), (a[0], 0.55, a[1] - 0.2)]
        m.poly(pts, ASHLAR, cp.rgba(cp.STONE, 0.85), facing=(0, 1, 0))
        # A stone where the cart wheels strike.
        cp.block(m, (s * 2.75 - 0.2, -0.05, BANK - 0.75), (s * 2.75 + 0.2, 0.55, BANK - 0.3), ASHLAR, cp.rgba(cp.STONE, 0.75), faces="xXzZY")
    # Rocks along the water's edge: under the towers' feet, at the pier, under the bank.
    random.seed(21)
    for _ in range(34):
        s = random.choice((-1, 1))
        z = random.uniform(BANK + 0.4, -3.6)
        near_bank = z < BANK + 2.4 or z > -6.2
        x = s * random.uniform(3.6 if z > -6.0 else 2.9, 7.5) if near_bank else s * random.uniform(3.2, 4.4)
        if not near_bank and abs(z - (PIER[0] + PIER[1]) * 0.5) > 1.6:
            continue
        rock(m, x, random.uniform(-2.25, -1.75), z, random.uniform(0.3, 0.75))


def recess(m):
    """The frame of cut stone the leaf shuts into, round the arch."""
    pale = cp.rgba(cp.STONE, 0.95)
    for s in (-1, 1):
        cp.block(m, (min(s * 3.2, s * 3.42), 0.0, FACE - 0.1), (max(s * 3.2, s * 3.42), 6.12, FACE), ASHLAR, pale, faces="xXz")
    cp.block(m, (-3.42, 6.0, FACE - 0.11), (3.42, 6.18, FACE), ASHLAR, pale, faces="zy")


def main():
    porter.reset(41)
    s = porter.Mesh("Stone")
    stone(s)
    recess(s)
    s.build()
    t = porter.Mesh("Timber")
    leaf(t)
    span(t)
    t.build()
    g = porter.Mesh("Gear")
    gaffs(g)
    windlass(g)
    g.build()
    for name, lo, hi in (("RailS", (-HALF - 0.3, -1.0, BANK - 0.5), (-HALF, 1.15, LEAF[0])), ("RailN", (HALF, -1.0, BANK - 0.5), (HALF + 0.3, 1.15, LEAF[0]))):
        c = porter.Mesh(name + "-colonly")
        c.box(lo, hi, OAK)
        c.build()
    porter.export("env_aldgate_bridge")


if __name__ == "__main__":
    main()
