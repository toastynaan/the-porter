"""The rest of the precinct (every night): its wall, its ground, and the
buildings that stand apart from the cloister: the porter's cell and the
guesthouse in the outer court, the charnel house, the infirmary and the
mill. The model is in the abbey's own coordinates and is laid over the
greybox (abbey.tscn's Grounds, outer_court.tscn, graveyard_infirmary.tscn),
which still stops people and shapes the navmesh but is no longer drawn.

The walls are read from those scenes, as the ranges' are (env_ranges.py).
The precinct wall's face to the lane is the lane's own model, so it is not
made here.

`env_precinct`:
- Walls: the precinct wall inside (and outside on its north, east and
  south), with its squints and the gate, under a coping; the five
  buildings inside and out, plaster or rubble within. Recesses in them
  (NICHES): three for figures, one for bones, a walled-up postern.
- Ceilings and Roofs: every building is open to a timber roof under clay
  tiles; a chimney on the guesthouse and the infirmary. The charnel
  house's roof is mossed and its ridge sags.
- Floors: flags in the buildings, earth in the charnel house.
- Ground: read from the ground blocks. Trodden earth in the outer court
  with a flagged path from the gate; gravel between the ranges and the mill
  race; grass in the graveyard and round the infirmary; grass under the
  orchard and tilled rows in the kitchen garden.
- Dressing and Figures (dress_up()): what makes it uneasy. Stains, damp,
  leaves, ruts and puddles; bones behind bars in the charnel house's wall
  and a skull over its door; hooded figures in the niches; crows on the
  ridges and wall tops; an unlit lantern over the gate. None of it has
  collision: all of it is flat on the ground, inside a wall's thickness,
  close against a wall, or above head height.

Run: tools/build.sh env_precinct
"""
import math
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
import city_parts as cp
import dress
import env_ranges as rg
from porter import fbm, lerp, smoothstep

cl = rg.cl
ch = rg.ch
pale = cl.pale
F = rg.F

rg.SCENES = ("outer_court", "graveyard_infirmary", "../abbey")
rg.BORROWED = ()
rg.SKIP = (("z", -40, -1),)
rg.ROOMS = {
    "cell": (-40, -32, -12, -4, 0, "plaster"),
    "guest": (-36, -24, -24, -16, 0, "plaster"),
    "charnel": (32, 40, -24, -16, 0, "rubble"),
    "infirmary": (24, 36, -4, 4, 0, "plaster"),
    "mill": (24, 32, 8, 16, 0, "rubble"),
}
# Each building's roof: (ridge along, from, to, the ridge's place across, ridge height, what stands at each end: a room, or None for the precinct wall's far side).
ROOFS = {
    "cell": ("x", -40.0, -32.0, -8.0, 8.0),
    "guest": ("x", -36.0, -24.0, -20.0, 8.0),
    "charnel": ("z", -24.0, -16.0, 36.0, 7.8),
    "infirmary": ("x", 24.0, 36.0, 0.0, 8.0),
    "mill": ("x", 24.0, 32.0, 12.0, 8.0),
}
# How far the charnel house's ridge has sunk in the middle.
SAG = 0.3
GROUND_Y = 0.012
BLACK = (0.0, 0.0, 0.0, 1.0)


def zone(x, z):
    """What the ground is at a point."""
    if x < -20.0:
        on_path = (abs(z + 2.0) < 1.3 and x < -24.7) or (abs(x + 26.0) < 1.3 and -14.0 < z < -0.7) or (abs(z + 14.0) < 1.3 and x > -27.3)
        return "path" if on_path else "court"
    if z > 20.0:
        return "beds" if 0.0 <= x < 22.0 and 24.0 < z < 36.0 else "grass"
    if 4.0 < z < 16.5 and x < 22.0:
        return "yard"
    return "grass"


GROUND = {
    "court": ("gravel_path", (0.5, 0.42, 0.34)),
    "path": ("flags_worn", (0.8, 0.78, 0.74)),
    "yard": ("gravel_path", (0.72, 0.68, 0.6)),
    "grass": ("grass_leafy", (0.8, 0.86, 0.66)),
    "beds": ("grave_earth", (0.62, 0.52, 0.42)),
}


def ground(m):
    text = open(os.path.join(rg.ROOT, "game/world/abbey/abbey.tscn")).read()
    y = GROUND_Y
    for block in text.split("\n\n"):
        name = re.match(r'\[node name="(Ground_\d+)"', block)
        tr = re.search(r"transform = Transform3D\(([^)]*)\)", block)
        size = re.search(r"size = Vector3\(([^)]*)\)", block)
        if not name or not tr or not size or name.group(1) == "Ground_8":
            continue
        v = [float(q) for q in tr.group(1).split(",")]
        s = [float(q) for q in size.group(1).split(",")]
        x0, x1, z0, z1 = v[9] - s[0] * 0.5, v[9] + s[0] * 0.5, v[11] - s[2] * 0.5, v[11] + s[2] * 0.5
        xs, zs = cp.steps(x0, x1, 1.3), cp.steps(z0, z1, 1.3)
        for xa, xb in zip(xs, xs[1:]):
            for za, zb in zip(zs, zs[1:]):
                kind = zone((xa + xb) * 0.5, (za + zb) * 0.5)
                mat, c = GROUND[kind]
                pts = [(xa, y, za), (xb, y, za), (xb, y, zb), (xa, y, zb)]
                cols = []
                for p in pts:
                    k = 0.72 + 0.5 * fbm(p[0], p[2], 0.12, 3, 2.0)
                    if kind == "beds":
                        k *= 0.8 + 0.3 * (0.5 + 0.5 * math.sin(p[0] * math.pi / 0.65))
                    cols.append(cp.rgba(c, k))
                m.poly(pts, mat, cols, facing=(0, 1, 0))
    # Inside the gate the lane's apron of flags (a plain greybox block, 8 mm
    # over this ground) runs 1.4 m into the court: worn flags over it, and
    # a riser at its two open edges.
    ya = 0.03
    x0, x1, z0, z1 = -40.0 - F, -38.6, -4.0 + F, 0.3
    xs, zs = cp.steps(x0, x1, 1.0), cp.steps(z0, z1, 1.3)
    for xa, xb in zip(xs, xs[1:]):
        for za, zb in zip(zs, zs[1:]):
            pts = [(xa, ya, za), (xb, ya, za), (xb, ya, zb), (xa, ya, zb)]
            m.poly(pts, "flags_worn", [cp.rgba((0.74, 0.72, 0.68), 0.7 + 0.4 * fbm(p[0], p[2], 0.2, 3, 2.0)) for p in pts], facing=(0, 1, 0))
    edge = cp.rgba((0.5, 0.48, 0.45))
    m.poly([(x1, 0.0, z0), (x1, 0.0, z1), (x1, ya, z1), (x1, ya, z0)], "flags_worn", edge, facing=(1, 0, 0))
    m.poly([(x0, 0.0, z1), (x1, 0.0, z1), (x1, ya, z1), (x0, ya, z1)], "flags_worn", edge, facing=(0, 0, 1))


# ---------------------------------------------------------------- the walls

# Recesses in a wall's face, asked for where the wall stands in the abbey
# and cut by wall_face() as rg.walls() makes that face. Each: the point
# (x, z) on the face at the recess's middle, the way the face looks, half
# its width, its sill, its springing (its head, if `rise` is 0), the rise of
# its pointed head, its depth, and its back wall's (material, colour).
NICHES = []
FACE = ch.face


def niche(name, x, z, out, hw, sill, spring, rise=0.0, depth=0.3, back=None, ledge=False, shade=0.5):
    n = {"name": name, "x": x, "z": z, "out": out, "hw": hw, "sill": sill, "spring": spring, "rise": rise, "depth": depth,
         "back": back or (ch.STONE, pale(0.2)), "ledge": ledge, "shade": shade, "made": False}
    NICHES.append(n)
    return n


def wall_face(t, s, ua, ub, ya, yb, tint, cuts=(), **more):
    """env_church.face, for the precinct: the same face, but a recess is cut
    wherever NICHES asks for one in it, and the gate (the one opening wider
    than a door) gets a square head and a reveal right through the wall.
    (The church's face gives every tall opening a pointed head as high as
    it is wide, which for a 3 m gate is a two-humped thing that stands above
    the wall's top; and it makes the reveal only to the wall's middle, and
    the gate's far face is the lane's model, which has none.)"""
    v, out = s * F, (0, 0, s)
    o, p0, p1 = t.place(0.0, 0.0, 0.0), t.place(0.0, 0.0, v), t.place(1.0, 0.0, v)
    here = []
    for n in NICHES:
        if (p0[0] - o[0]) * n["out"][0] + (p0[2] - o[2]) * n["out"][1] < 0.3:
            continue
        u = (n["x"] - p0[0]) * (p1[0] - p0[0]) + (n["z"] - p0[2]) * (p1[2] - p0[2])
        q = t.place(u, 0.0, v)
        if math.hypot(q[0] - n["x"], q[2] - n["z"]) < 0.05 and ua < u - n["hw"] and u + n["hw"] < ub and ya <= n["sill"] and n["spring"] + n["rise"] < yb:
            here.append((u, n))
            n["made"] = True
    if not here and not any(c[1] > 1.0 for c in cuts):
        return FACE(t, s, ua, ub, ya, yb, tint, cuts, **more)
    mat = getattr(tint, "mat", ch.STONE)
    items = sorted([(c[0], c[1], c, None) for c in cuts] + [(u, n["hw"], None, n) for u, n in here], key=lambda it: it[0])
    u = ua
    for uc, hw, cut, n in items:
        a, b = max(uc - hw - 0.2, u), min(uc + hw + 0.2, ub)
        cp.panel(t, (u, v), (a, v), ya, yb, out, mat, tint, 1.6, 1.2)
        if n:
            recess(t, s, a, b, ya, yb, tint, uc, n)
        elif hw > 1.0:
            gateway(t, s, a, b, ya, yb, tint, cut)
        else:
            FACE(t, s, a, b, ya, yb, tint, [cut], **more)
        u = b
    cp.panel(t, (u, v), (ub, v), ya, yb, out, mat, tint, 1.6, 1.2)


def gateway(t, s, a, b, ya, yb, tint, cut):
    """The gate's opening in the face from a to b: square-headed, in a plain
    frame, its reveal carried through the whole wall."""
    uc, hw, y0, y1 = cut
    v, out = s * F, (0, 0, s)
    mat = getattr(tint, "mat", ch.STONE)
    cp.panel(t, (a, v), (uc - hw, v), ya, yb, out, mat, tint, 1.6, 1.2)
    cp.panel(t, (uc + hw, v), (b, v), ya, yb, out, mat, tint, 1.6, 1.2)
    cp.panel(t, (uc - hw, v), (uc + hw, v), y1, yb, out, mat, tint, 1.6, 1.2)
    c = pale(0.6)
    for e, k in ((uc - hw, 1), (uc + hw, -1)):
        for va, vb in ((-v, 0.0), (0.0, v)):
            t.poly([(e, y0, va), (e, y1, va), (e, y1, vb), (e, y0, vb)], ch.STONE, c, facing=(k, 0, 0))
    for ua2, ub2 in zip(cp.steps(uc - hw, uc + hw, 1.0), cp.steps(uc - hw, uc + hw, 1.0)[1:]):
        t.poly([(ua2, y1, -v), (ub2, y1, -v), (ub2, y1, v), (ua2, y1, v)], ch.STONE, pale(0.5), facing=(0, -1, 0))
    c = pale(0.8)
    fw = 0.16
    lo, hi = sorted((v, v + s * 0.07))
    zf = "Z" if s > 0 else "z"
    for k in (-1, 1):
        ea, eb = sorted((uc + k * hw, uc + k * (hw + fw)))
        t.box((ea, y0, lo), (eb, y1, hi), ch.STONE, c, faces="xX" + zf)
    t.box((uc - hw - fw, y1, lo), (uc + hw + fw, y1 + fw + 0.04, hi), ch.STONE, c, faces="xXyY" + zf)


def recess(t, s, a, b, ya, yb, tint, uc, n):
    """A recess in the face from a to b: the face round it, its sides and
    head, its sill, its back."""
    hw, y0, y1, rise, d = n["hw"], n["sill"], n["spring"], n["rise"], n["depth"]
    v, out = s * F, (0, 0, s)
    vb = v - s * d
    mat = getattr(tint, "mat", ch.STONE)
    cp.panel(t, (a, v), (uc - hw, v), ya, yb, out, mat, tint, 1.6, 1.2)
    cp.panel(t, (uc + hw, v), (b, v), ya, yb, out, mat, tint, 1.6, 1.2)
    cp.panel(t, (uc - hw, v), (uc + hw, v), ya, y0, out, mat, tint, 1.6, 1.2)
    k = n["shade"]

    def inside(x, y, z):
        return cp.rgba(cl.PALE, k * lerp(0.55, 1.0, abs(z - vb) / d))

    if rise:
        cp.arch_wall(t, v, uc - hw, uc + hw, y1, yb, hw, y1, rise, out, mat, tint, cx=uc, n=5)
        cp.vault(t, vb, v, hw, y1, rise, ch.STONE, inside, cx=uc, n=5, y0=y0, step=0.5)
        shape = [(uc + hw, y0)] + cp.arch_profile(hw, y1, rise, 5, uc) + [(uc - hw, y0)]
    else:
        cp.panel(t, (uc - hw, v), (uc + hw, v), y1, yb, out, mat, tint, 1.6, 1.2)
        for e, kx in ((uc - hw, 1), (uc + hw, -1)):
            pts = [(e, y0, vb), (e, y1, vb), (e, y1, v), (e, y0, v)]
            t.poly(pts, ch.STONE, [inside(*p) for p in pts], facing=(kx, 0, 0))
        pts = [(uc - hw, y1, vb), (uc + hw, y1, vb), (uc + hw, y1, v), (uc - hw, y1, v)]
        t.poly(pts, ch.STONE, [inside(*p) for p in pts], facing=(0, -1, 0))
        shape = [(uc + hw, y0), (uc + hw, y1), (uc - hw, y1), (uc - hw, y0)]
    if y0 > ya + 0.01:
        pts = [(uc - hw, y0, vb), (uc + hw, y0, vb), (uc + hw, y0, v), (uc - hw, y0, v)]
        t.poly(pts, ch.STONE, [cp.rgba(cl.PALE, k * lerp(0.6, 1.2, abs(p[2] - vb) / d)) for p in pts], facing=(0, 1, 0))
    bmat, bcol = n["back"]
    pts = [(x, y, vb) for x, y in shape]
    t.poly(pts, bmat, [bcol(*p) for p in pts] if callable(bcol) else bcol, facing=out)
    if n["ledge"]:
        lo, hi = sorted((v, v + s * 0.06))
        t.box((uc - hw - 0.07, y0 - 0.1, lo), (uc + hw + 0.07, y0, hi), ch.STONE, pale(0.62), faces="xXyY" + ("Z" if s > 0 else "z"))


def sway_roof(m, x0, x1, z0, z1, eave, ridge, mat, color, sag, over=0.5, tile=1.8, n=6):
    """cp.gable_roof with its ridge along z, sunk by `sag` in the middle in
    a curve. Each piece is two triangles, so its surface is known: returns
    the roof's height at (x, z)."""
    c, cu = cp.rgba(color), cp.rgba((0.25, 0.25, 0.25))
    half, mid = (x1 - x0) * 0.5, (x0 + x1) * 0.5
    run = half + over
    low = eave - (ridge - eave) * over / half
    slope = math.hypot(run, ridge - low)
    zs = cp.steps(z0 - over, z1 + over, (z1 - z0 + 2 * over) / n)

    def ry(z):
        return ridge - sag * math.sin(math.pi * (z - (z0 - over)) / (z1 - z0 + 2 * over))

    for za, zb in zip(zs, zs[1:]):
        for side in (-1, 1):
            ea, eb, rb, ra = (mid + side * run, low, za), (mid + side * run, low, zb), (mid, ry(zb), zb), (mid, ry(za), za)
            ua, ub, ur, uq = (za / tile, 0.0), (zb / tile, 0.0), (zb / tile, slope / tile), (za / tile, slope / tile)
            for pts, uv in (([ea, eb, rb], [ua, ub, ur]), ([ea, rb, ra], [ua, ur, uq])):
                m.poly(pts, mat, c, uv, facing=(side * 0.5, 1, 0))
                m.poly(pts, mat, cu, facing=(-side * 0.5, -1, 0))

    def height(x, z):
        g = max(0.0, 1.0 - abs(x - mid) / run)
        i = max(0, min(n - 1, int((z - zs[0]) / (zs[1] - zs[0]))))
        f = (z - zs[i]) / (zs[i + 1] - zs[i])
        ra, rb = ry(zs[i]), ry(zs[i + 1])
        return low + g * (rb - low) if g <= f else low + g * (ra - low) + f * (rb - ra)
    return height


# ------------------------------------------------------------- the dressing

class Tinted:
    """A mesh that changes the colour (and, if asked, the material) of what
    is built through it: for dress.py's bones and leaves, which come in one
    colour."""

    def __init__(self, mesh, colour, mat=None):
        self.mesh, self.colour, self.mat = mesh, colour, mat

    def vert(self, x, y, z, color=(1.0, 1.0, 1.0, 1.0), uv=(0.0, 0.0)):
        return self.mesh.vert(x, y, z, self.colour(color), uv)

    def face(self, indices, mat):
        self.mesh.face(indices, self.mat or mat)

    quad = porter.Mesh.quad
    poly = porter.Mesh.poly
    tube = porter.Mesh.tube
    box = porter.Mesh.box


def old_bone(c):
    """Bone long out of the ground: browner and a good deal darker."""
    return (c[0] * 0.6, c[1] * 0.55, c[2] * 0.48, 1.0)


def carved(c):
    """Bone's colours as the same shapes cut in stone."""
    k = max(c[0], c[1], c[2])
    return (0.03, 0.03, 0.03, 1.0) if k < 0.1 else (0.62 * k, 0.6 * k, 0.56 * k, 1.0)


def leaves(m, x0, x1, z0, z1, count, seed, toward=None, y=GROUND_Y + 0.006):
    """Fallen leaves in a rectangle, heaped toward one side if asked: as
    dress.py's, but each twice the size (at 4 cm those are specks from eye
    height) and wet-dark."""
    rng = random.Random(seed)
    for _ in range(count):
        fx, fz = rng.random(), rng.random()
        if toward:
            fx, fz = fx ** (2.4 if toward[0] else 1.0), fz ** (2.4 if toward[1] else 1.0)
            fx, fz = (1.0 - fx if toward[0] > 0 else fx), (1.0 - fz if toward[1] > 0 else fz)
        x, z = lerp(x0, x1, fx), lerp(z0, z1, fz)
        r, a, k = rng.uniform(0.045, 0.085), rng.uniform(0.0, math.tau), rng.uniform(0.55, 1.0)
        c = (0.24 * k, rng.uniform(0.11, 0.16) * k, 0.05 * k, 1.0)
        lift = rng.uniform(0.0, 0.02)
        pts = [(x + math.cos(a + math.tau * i / 4) * r * (1.0 if i % 2 else 0.55), y + rng.uniform(0.0, 0.004) + (lift if i == 1 else 0.0),
                z + math.sin(a + math.tau * i / 4) * r * (1.0 if i % 2 else 0.55)) for i in range(4)]
        m.poly(pts, "painted", c, facing=(0, 1, 0))


def drift(m, x0, x1, z0, z1, count, seed, toward=None):
    """Dead leaves blown into a heap: the dark of old leaf mould, and the leaves on it."""
    cx, cz = (x0 + x1) * 0.5, (z0 + z1) * 0.5
    if toward:
        cx, cz = cx + toward[0] * (x1 - x0) * 0.2, cz + toward[1] * (z1 - z0) * 0.2
    blot(m, cx, cz, (x1 - x0) * 0.62, (z1 - z0) * 0.62, (0.05, 0.035, 0.02), 0.6, seed, GROUND_Y + 0.003)
    leaves(m, x0, x1, z0, z1, count, seed, toward)


def on_wall(p, out, proud=0.01):
    """A point's frame on a wall: from (along, up) offsets to a point just proud of the wall."""
    ox, oz = out
    return lambda u, v: (p[0] - oz * u + ox * proud, p[1] + v, p[2] + ox * u + oz * proud)


def blot(m, cx, cz, rx, rz, colour, strength, seed=0.0, y=GROUND_Y + 0.008, turn=0.0, n=10):
    """A blotch on the ground: mud, a wet place."""
    c, s = math.cos(turn), math.sin(turn)

    def pt(i, f):
        a = math.tau * (i % n) / n
        k = f * (0.9 + 0.28 * fbm(cx + math.cos(a) * 2.0, cz + math.sin(a) * 2.0, 1.0, 2, seed))
        x, z = math.cos(a) * rx * k, math.sin(a) * rz * k
        return (cx + x * c - z * s, y, cz + x * s + z * c)

    full, none = (colour[0], colour[1], colour[2], strength), (colour[0], colour[1], colour[2], 0.0)
    for i in range(n):
        m.poly([(cx, y, cz), pt(i, 0.55), pt(i + 1, 0.55)], dress.GRIME, full, facing=(0, 1, 0))
        m.poly([pt(i, 0.55), pt(i, 1.0), pt(i + 1, 1.0), pt(i + 1, 0.55)], dress.GRIME, [full, none, none, full], facing=(0, 1, 0))


def puddle(m, cx, cz, rx, rz, seed=0.0, turn=0.0, n=16):
    """Standing water a few millimetres deep in a hollow, the earth dark and wet round it."""
    blot(m, cx, cz, rx * 1.6, rz * 2.2, (0.02, 0.016, 0.012), 0.8, seed + 3.0, GROUND_Y + 0.009, turn)
    c, s = math.cos(turn), math.sin(turn)
    pts = []
    for i in range(n):
        a = math.tau * i / n
        k = 0.9 + 0.28 * fbm(cx + math.cos(a) * 2.0, cz + math.sin(a) * 2.0, 1.0, 2, seed)
        x, z = math.cos(a) * rx * k, math.sin(a) * rz * k
        pts.append((cx + x * c - z * s, GROUND_Y + 0.012, cz + x * s + z * c))
    m.poly(pts, "water_still", (1.0, 1.0, 1.0, 1.0), facing=(0, 1, 0))


def ruts(m, pts, gauge=1.4, width=0.42, strength=0.9, seed=0.0, y=GROUND_Y + 0.006):
    """A cart's two wheel ruts along a line of (x, z) points: dark strips in
    the earth. Returns where a rut is, a share `f` of the way along on
    `side` (-1 or 1): (x, z, the way it runs), for a puddle to lie in it."""
    path = []
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, len(pts) - 1)]
        for k in range(4):
            f = k / 4.0
            path.append(tuple(0.5 * (2 * p1[j] + (p2[j] - p0[j]) * f + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * f * f
                                     + (3 * p1[j] - p0[j] - 3 * p2[j] + p3[j]) * f ** 3) for j in range(2)))
    path.append(pts[-1])
    rows = []
    for i, p in enumerate(path):
        a, b = path[max(i - 1, 0)], path[min(i + 1, len(path) - 1)]
        dx, dz = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dz) or 1.0
        fade = smoothstep(0.0, 3.0, i) * smoothstep(0.0, 3.0, len(path) - 1 - i)
        rows.append((p, (-dz / d, dx / d), fade))
    dark = (0.02, 0.016, 0.012)
    for side in (-1, 1):
        def at(row, e):
            p, nrm, fade = row
            off = side * gauge * 0.5 + e * width * 0.5
            return (p[0] + nrm[0] * off, y, p[1] + nrm[1] * off)

        def col(row, e):
            p, nrm, fade = row
            a = 0.0 if e else strength * fade * (0.72 + 0.28 * fbm(p[0], p[1], 0.6, 2, seed + side))
            return (dark[0], dark[1], dark[2], max(0.0, min(1.0, a)))

        for ra, rb in zip(rows, rows[1:]):
            for e0, e1 in ((-1, 0), (0, 1)):
                m.poly([at(ra, e0), at(rb, e0), at(rb, e1), at(ra, e1)], dress.GRIME, [col(ra, e0), col(rb, e0), col(rb, e1), col(ra, e1)], facing=(0, 1, 0))

    def spot(f, side):
        p, nrm, fade = rows[int(f * (len(rows) - 1))]
        return (p[0] + nrm[0] * side * gauge * 0.5, p[1] + nrm[1] * side * gauge * 0.5, math.atan2(-nrm[0], nrm[1]))
    return spot


def slime(m, a, b, y0, out, height=0.5, strength=0.75, seed=0.0, step=2.0):
    """A green band along a wall at a water line, cut coarse (dress.damp, for 40 m of wall nobody stands near)."""
    length = math.hypot(b[0] - a[0], b[1] - a[1])
    n = max(int(length / step), 1)
    g = dress.GREEN

    def pt(i, v):
        f = i / n
        return (lerp(a[0], b[0], f) + out[0] * 0.012, y0 + v, lerp(a[1], b[1], f) + out[1] * 0.012)

    def alpha(i, v):
        return strength * (1.0 - v / height) * (0.75 + 0.25 * fbm(i * 1.7, v * 3.0, 1.0, 2, seed))

    for i in range(n):
        for va, vb in ((0.0, height * 0.4), (height * 0.4, height)):
            cols = [(g[0], g[1], g[2], max(0.0, min(1.0, alpha(j, v)))) for j, v in ((i, va), (i + 1, va), (i + 1, vb), (i, vb))]
            m.poly([pt(i, va), pt(i + 1, va), pt(i + 1, vb), pt(i, vb)], dress.GRIME, cols, facing=(out[0], 0, out[1]))


def crosses(m, p, out, width=1.0, height=0.7, count=15, seed=0):
    """Small crosses scratched into plaster, many times, in one patch."""
    rng = random.Random(seed)
    at = on_wall(p, out, 0.006)
    c = (0.1, 0.085, 0.07, 0.8)
    for _ in range(count):
        u, v = rng.uniform(-0.5, 0.5) * width, rng.uniform(-0.5, 0.5) * height * (0.5 + 0.5 * rng.random())
        h, w, lean = rng.uniform(0.07, 0.13), 0.005, rng.uniform(-0.15, 0.15)
        arm, cross_at = h * rng.uniform(0.25, 0.36), h * rng.uniform(0.55, 0.75)
        m.poly([at(u - w, v), at(u + w, v), at(u + w + lean * h, v + h), at(u - w + lean * h, v + h)], dress.GRIME, c, facing=(out[0], 0, out[1]))
        uc, vc = u + lean * cross_at, v + cross_at
        m.poly([at(uc - arm, vc - w - lean * arm), at(uc + arm, vc - w + lean * arm), at(uc + arm, vc + w + lean * arm), at(uc - arm, vc + w - lean * arm)],
               dress.GRIME, c, facing=(out[0], 0, out[1]))


def crow(m, p, yaw=0.0, scale=1.0, down=0.0):
    """A crow perched on `p`, looking along `yaw` (0: toward +z), its head lowered by `down`."""
    c, d = (0.02, 0.02, 0.025, 1.0), (0.035, 0.035, 0.04, 1.0)
    t = dress.Placed(m, p, yaw, scale)
    t.tube([(0, 0.1, -0.13), (0, 0.11, -0.06), (0, 0.13, 0.03), (0, 0.16, 0.1), (0, 0.2 - down * 0.5, 0.14)], [0.025, 0.055, 0.068, 0.055, 0.03], 6, "painted",
           [c, c, d, c, c], caps=True, squash=(0.85, 1.0))
    hy = 0.235 - down
    t.tube([(0, hy - 0.035, 0.12), (0, hy, 0.15), (0, hy + 0.01, 0.19)], [0.03, 0.04, 0.026], 5, "painted", c, caps=True)
    t.tube([(0, hy + 0.008, 0.2), (0, hy - 0.004 - down * 0.3, 0.245), (0, hy - 0.02 - down * 0.5, 0.285)], [0.017, 0.012, 0.002], 4, "painted", (0.03, 0.03, 0.03, 1.0))
    tail = [(-0.028, 0.1, -0.12), (0.028, 0.1, -0.12), (0.04, 0.045, -0.3), (-0.04, 0.045, -0.3)]
    t.poly(tail, "painted", c, facing=(0, 1, 0))
    t.poly(tail, "painted", c, facing=(0, -1, 0))
    for sx in (-1, 1):
        t.tube([(sx * 0.03, 0.07, 0.02), (sx * 0.032, 0.0, 0.035)], [0.007, 0.006], 3, "painted", (0.04, 0.04, 0.04, 1.0))


def lantern_bracket(m, x, y, z, ox, oz, reach=0.6):
    """An iron arm on a wall and a lantern hung from it, unlit: its horn panes dark."""
    iron = (0.07, 0.065, 0.06, 1.0)
    tip = (x + ox * reach, y, z + oz * reach)
    m.tube([(x, y, z), tip], [0.02, 0.016], 4, "iron_cart", iron)
    m.tube([(x, y - 0.3, z), (x + ox * reach * 0.75, y - 0.02, z + oz * reach * 0.75)], [0.014, 0.014], 4, "iron_cart", iron)
    hx, hz = tip[0] - ox * 0.06, tip[2] - oz * 0.06
    m.tube([(hx, y, hz), (hx, y - 0.07, hz)], [0.006, 0.006], 3, "iron_cart", iron)
    top = y - 0.07
    m.tube([(hx, top, hz), (hx, top - 0.035, hz), (hx, top - 0.06, hz)], [0.012, 0.05, 0.085], 4, "iron_cart", iron)
    r, h = 0.075, 0.24
    for i in range(4):
        a0, a1 = math.tau * (i + 0.5) / 4, math.tau * (i + 1.5) / 4
        pa, pb = (hx + math.cos(a0) * r, hz + math.sin(a0) * r), (hx + math.cos(a1) * r, hz + math.sin(a1) * r)
        m.tube([(pa[0], top - 0.06, pa[1]), (pa[0], top - 0.06 - h, pa[1])], [0.008, 0.008], 3, "iron_cart", iron)
        am = (a0 + a1) * 0.5
        m.poly([(pa[0], top - 0.06, pa[1]), (pb[0], top - 0.06, pb[1]), (pb[0], top - 0.06 - h, pb[1]), (pa[0], top - 0.06 - h, pa[1])], "painted",
               (0.06, 0.05, 0.035, 1.0), facing=(math.cos(am), 0, math.sin(am)))
    m.box((hx - 0.085, top - 0.085 - h, hz - 0.085), (hx + 0.085, top - 0.06 - h, hz + 0.085), "iron_cart", iron)


def dress_up(m, soft, roof_charnel):
    """Everything that is not the place itself. `m` takes the flat things
    (stains, leaves, water, iron); `soft` the rounded ones (figures, bones,
    crows), built smooth."""
    # --- The charnel house: bones in its wall, a skull over its door.
    n = BONES
    back = n["x"] + n["depth"] - 0.015
    dress.bones(Tinted(soft, old_bone), (back, n["z"] - n["hw"] + 0.03), (back, n["z"] + n["hw"] - 0.03), n["sill"], (-1, 0), rows=3, skulls=True, seed=7, depth=0.21)
    iron = (0.06, 0.055, 0.05, 1.0)
    xb = n["x"] + 0.035
    for i in range(8):
        z = lerp(n["z"] - n["hw"], n["z"] + n["hw"], (i + 0.5) / 8.0)
        m.tube([(xb, n["sill"], z), (xb, n["spring"], z)], [0.011, 0.011], 4, "iron_cart", iron)
    m.box((xb - 0.006, n["sill"] + 0.3, n["z"] - n["hw"]), (xb + 0.006, n["sill"] + 0.335, n["z"] + n["hw"]), "iron_cart", iron, faces="xyY")
    for i, z in enumerate((-20.75, -20.15, -19.6)):
        dress.run(m, (n["x"], n["sill"], z), (-1, 0), 0.2, 0.75 + 0.2 * i, dress.RUST, 0.6, 3.0 + i)
    # Over the door, cut in the stone of its head: a skull and two bones crossed.
    stone = Tinted(soft, carved, ch.STONE)
    dress.skull(stone, (31.56, 2.3, -18.0), -math.pi * 0.5, 1.4, jaw=True, seed=2.0)
    for k in (-1, 1):
        ends = [(31.54, 2.23, -18.0 - k * 0.33), (31.54, 2.47, -18.0 + k * 0.33)]
        pts = [tuple(lerp(ends[0][j], ends[1][j], f) for j in range(3)) for f in (0.0, 0.07, 0.2, 0.8, 0.93, 1.0)]
        stone.tube(pts, [0.018, 0.03, 0.018, 0.018, 0.03, 0.018], 5, "painted", (0.55, 0.55, 0.55, 1.0), caps=True)
    dress.run(m, (31.58, 2.15, -18.74), (-1, 0), 0.16, 1.0, dress.DARK, 0.45, 8.0)
    dress.crack(m, (31.58, 0.3, -19.05), (-1, 0), 2.3, seed=5)
    for a, b, out in (((31.58, -24.4), (31.58, -18.62), (-1, 0)), ((31.58, -17.38), (31.58, -15.6), (-1, 0)), ((31.6, -24.42), (39.6, -24.42), (0, -1)),
                      ((31.6, -15.58), (39.6, -15.58), (0, 1))):
        dress.damp(m, a, b, 0.0, out, 0.8, dress.GREEN, 0.6, seed=a[0] + a[1])
    drift(m, 30.9, 31.5, -19.4, -16.6, 80, 11, toward=(1, 0))
    # Tiles slipped from its roof: the laths show dark.
    for z, f, w in ((-21.4, 0.34, 0.5), (-21.1, 0.42, 0.3), (-18.3, 0.66, 0.4), (-22.7, 0.18, 0.3), (-17.2, 0.3, 0.35)):
        def at(dz, df):
            x = 31.6 + 4.4 * (f + df)
            return (x - 0.012, roof_charnel(x, z + dz) + 0.02, z + dz)
        m.poly([at(0, 0), at(w, 0), at(w, 0.06), at(0, 0.06)], "painted", (0.03, 0.026, 0.022, 1.0), facing=(-0.5, 1, 0))
    # Webs in its far corners, and one in the mill's and the guesthouse's.
    for corner, a, b, size, seed in (((39.58, 3.96, -23.58), (-1, -0.2, 0), (0, -0.2, 1), 1.1, 1), ((39.58, 3.96, -16.42), (-1, -0.25, 0), (0, -0.25, -1), 0.9, 2),
                                     ((39.58, 2.6, -23.58), (-1, 0.5, 0), (0, 0.5, 1), 0.6, 3), ((31.58, 3.96, 15.58), (-1, -0.2, 0), (0, -0.2, -1), 1.0, 4),
                                     ((-35.58, 3.96, -23.58), (1, -0.2, 0), (0, -0.2, 1), 0.8, 5)):
        dress.cobweb(m, corner, a, b, size, seed)

    # --- Figures where a sightline ends: beside the porter's own door, at
    # the end of the graves, at the top of the steps out of the mill race.
    grey = (0.4, 0.39, 0.36)
    for n, height, bowed in ((CELL_FIGURE, 1.22, 0.0), (GRAVE_FIGURE, 1.4, 1.0), (RACE_FIGURE, 1.4, 0.4)):
        ox, oz = n["out"]
        back = n["depth"] - 0.15
        dress.figure(soft, (n["x"] - ox * back, n["sill"], n["z"] - oz * back), math.atan2(ox, oz), height, "stone_church", grey, hooded=True, bowed=bowed)
        dress.run(m, (n["x"], n["sill"] - 0.1, n["z"]), n["out"], 0.5, 1.0, dress.DARK, 0.5, n["x"])
    for a, b, out, h in (((29.0, -39.58), (39.5, -39.58), (0, 1), 0.75), ((39.58, -39.5), (39.58, -24.5), (-1, 0), 0.9), ((39.58, 14.0), (39.58, 22.0), (-1, 0), 0.75)):
        dress.damp(m, a, b, 0.0, out, h, dress.GREEN, 0.6, seed=a[0] - a[1])
    drift(m, 37.9, 39.5, -39.5, -37.9, 110, 12, toward=(1, -1))
    drift(m, 34.1, 35.9, -39.5, -38.95, 50, 13, toward=(0, -1))
    drift(m, 38.95, 39.5, 16.6, 19.4, 55, 22, toward=(1, 0))

    # --- The walled-up postern in the north wall, behind the church.
    n = POSTERN
    zb = n["z"] - n["depth"]
    dress.crack(m, (n["x"] + 0.12, 0.2, zb), (0, 1), 1.9, seed=9)
    dress.damp(m, (n["x"] - n["hw"], zb), (n["x"] + n["hw"], zb), 0.0, (0, 1), 1.1, dress.GREEN, 0.7, seed=4.0)
    dress.patch(m, (n["x"] - 0.1, 1.5, zb), (0, 1), 0.9, 1.1, dress.DARK, 0.45, 6.0)
    for a, b in (((n["x"] - 6.0, n["z"]), (n["x"] - n["hw"] - 0.05, n["z"])), ((n["x"] + n["hw"] + 0.05, n["z"]), (n["x"] + 6.0, n["z"]))):
        dress.damp(m, a, b, 0.0, (0, 1), 1.0, dress.GREEN, 0.55, seed=a[0])
    drift(m, n["x"] - 1.0, n["x"] + 1.1, zb + 0.01, n["z"] + 0.5, 75, 14, toward=(0, -1))

    # --- The gate and the outer court.
    lantern_bracket(m, -40.0 + F, 3.9, -2.0, 1, 0)
    dress.damp(m, (-40.0 + F, 0.5), (-40.0 + F, 5.7), 0.0, (1, 0), 0.9, dress.GREEN, 0.55, seed=1.0)
    blot(m, -37.4, -2.1, 2.0, 1.5, (0.07, 0.055, 0.04), 0.6, 1.0, 0.03 + 0.006)
    rut = ruts(m, [(-38.5, -2.0), (-37.0, -1.9), (-35.0, -0.9), (-33.4, 2.4), (-31.6, 6.2), (-28.8, 9.6), (-24.8, 12.4), (-20.6, 14.0)], seed=3.0)
    for i, (f, side, long, wide) in enumerate(((0.5, -1, 0.85, 0.24), (0.68, 1, 0.7, 0.22), (0.86, -1, 1.0, 0.26))):
        x, z, turn = rut(f, side)
        puddle(m, x, z, long, wide, 1.0 + i, turn)
    puddle(m, -36.3, 7.2, 0.8, 0.5, 4.0, 0.3)
    drift(m, -39.5, -38.4, 0.5, 3.2, 90, 15, toward=(-1, 0))
    drift(m, -39.5, -38.8, -20.6, -17.4, 100, 16, toward=(-1, 0))
    drift(m, -31.5, -29.0, -15.5, -15.0, 60, 17, toward=(0, -1))
    # The guesthouse: crosses scratched in the plaster by the last bed.
    crosses(m, (-25.7, 1.05, -24.0 + F), (0, 1), 0.9, 0.8, 17, seed=4)

    # The infirmary: damp in the plaster over the last bed, and under the sill beside it. The mill: a crack up its west wall.
    dress.patch(m, (32.6, 1.25, 4.0 - F), (0, -1), 1.3, 1.1, dress.DARK, 0.42, 5.0)
    dress.run(m, (34.0, 1.57, 4.0 - F), (0, -1), 0.5, 1.1, dress.DARK, 0.45, 6.0)
    dress.crack(m, (24.0 + F, 0.4, 11.6), (1, 0), 2.7, seed=12)

    # --- Runs under every window sill outdoors.
    for along, line, at, level, kind, only in rg.pieces():
        if kind != "wall_window":
            continue
        for s in (1, -1):
            x, z = (at, line + s) if along == "x" else (line + s, at)
            if rg.room_at(x, z, level) != "out":
                continue
            p = (at, 1.57, line + s * F) if along == "x" else (line + s * F, 1.57, at)
            dress.run(m, p, (0, s) if along == "x" else (s, 0), 0.6, 1.0 + 0.4 * fbm(at, line, 1.0, 1, 2.0), dress.DARK, 0.5, at + line)

    # --- The mill race: slime at the water line. The gardens and the orchard: leaves.
    slime(m, (-8.0, 16.4), (36.0, 16.4), -1.06, (0, 1), seed=1.0)
    slime(m, (-8.0, 19.6), (36.0, 19.6), -1.06, (0, -1), seed=2.0)
    leaves(m, -36.0, -8.0, 23.0, 39.4, 110, 18)
    drift(m, -35.2, -31.6, 38.8, 39.5, 90, 19, toward=(0, 1))
    drift(m, -22.2, -18.6, 38.8, 39.5, 90, 23, toward=(0, 1))
    drift(m, 29.0, 31.2, -5.0, -4.5, 45, 20, toward=(0, 1))
    drift(m, 25.0, 27.2, 7.05, 7.55, 40, 21, toward=(0, 1))

    # --- Crows: on the charnel house's ridge, over each figure in the
    # precinct wall, over the gate, on the guesthouse's chimney and the mill.
    for p, yaw, down in (((36.0, roof_charnel(36.0, -22.9), -22.9), -1.9, 0.03), ((36.0, roof_charnel(36.0, -22.3), -22.3), -1.2, 0.0), ((36.0, roof_charnel(36.0, -17.1), -17.1), -2.4, 0.02),
                         ((33.7, 4.3, -40.0), 0.3, 0.03), ((36.6, 4.3, -40.0), -0.2, 0.0), ((40.0, 4.3, 19.4), -1.4, 0.03), ((-40.0, 4.31, 1.3), 1.5, 0.03),
                         ((-40.0, 4.31, 2.0), 2.3, 0.0), ((-24.4, 8.8, -19.5), -2.2, 0.0), ((31.2, 8.0, 12.0), 2.8, 0.02)):
        crow(soft, p, yaw, 1.0, down)


def triangles(mesh):
    return sum(len(f) - 2 for f in mesh.faces)


def build():
    global BONES, CELL_FIGURE, GRAVE_FIGURE, RACE_FIGURE, POSTERN
    porter.reset(733)
    cl.STONE = "stone_church"
    wall_m, roof_m, ceil_m, floor_m, ground_m = (porter.Mesh(n) for n in ("Walls", "Roofs", "Ceilings", "Floors", "Ground"))
    dress_m, soft_m = porter.Mesh("Dressing"), porter.Mesh("Figures")
    outside = cp.stone_tint(0.0, 5.0, seed=63.0, worn=0.6)
    outside.mat = "stone_rubble"
    tints = {name: rg.styled(r[5], 31.0 + 2.0 * i) for i, (name, r) in enumerate(rg.ROOMS.items())}

    # The recesses (see NICHES), then the walls with them cut in.
    del NICHES[:]
    BONES = niche("bones", 32.0 - F, -20.2, (-1, 0), 0.78, 1.02, 1.58, depth=0.3, back=("window_dark", BLACK), shade=0.34)
    CELL_FIGURE = niche("cell figure", -36.6, -4.0 + F, (0, 1), 0.3, 1.15, 2.2, 0.36, ledge=True)
    GRAVE_FIGURE = niche("grave figure", 35.0, -40.0 + F, (0, 1), 0.33, 1.0, 2.2, 0.4, ledge=True)
    RACE_FIGURE = niche("race figure", 40.0 - F, 18.0, (-1, 0), 0.33, 1.0, 2.2, 0.4, ledge=True)
    block_tint = cp.stone_tint(0.0, 2.4, clean=(0.5, 0.49, 0.46), seed=17.0, worn=0.9)
    POSTERN = niche("postern", 2.0, -40.0 + F, (0, 1), 0.55, 0.0, 1.65, 0.62, depth=0.09, back=("stone_cloister", block_tint), shade=0.42)
    ch.face = wall_face
    try:
        rg.walls(wall_m, tints, outside)
    finally:
        ch.face = FACE
    for n in NICHES:
        if not n["made"]:
            print("NICHE NOT MADE: %s (no wall face found through its point)" % n["name"])

    # The precinct wall's coping.
    cope = pale(0.62)
    # (Not where the porter's cell and the charnel house stand against it: their gables are there.)
    for x0, x1, z0, z1 in ((-40.5, 40.5, -40.5, -39.5), (-40.5, 40.5, 39.5, 40.5), (-40.5, -39.5, -40.5, -12.4), (-40.5, -39.5, -3.6, 40.5),
                           (39.5, 40.5, -40.5, -24.4), (39.5, 40.5, -15.6, 40.5)):
        wall_m.box((x0, 4.0, z0), (x1, 4.14, z1), "stone_cloister", cope)
        cx, cz = (x0 + x1) * 0.5, (z0 + z1) * 0.5
        along_x = x1 - x0 > 2.0
        a, b = ((x0, 4.3, cz), (x1, 4.3, cz)) if along_x else ((cx, 4.3, z0), (cx, 4.3, z1))
        for s in (-1, 1):
            e0 = (x0, 4.14, cz + s * 0.5) if along_x else (cx + s * 0.5, 4.14, z0)
            e1 = (x1, 4.14, cz + s * 0.5) if along_x else (cx + s * 0.5, 4.14, z1)
            wall_m.poly([e0, e1, b, a], "stone_cloister", cope, facing=(0, 1, s) if along_x else (s, 1, 0))
        # Its two ends, so nobody looks in under its ridge.
        for end, k in ((a, -1), (b, 1)):
            tri = [(end[0], 4.14, end[2] - 0.5), (end[0], 4.14, end[2] + 0.5), end] if along_x else [(end[0] - 0.5, 4.14, end[2]), (end[0] + 0.5, 4.14, end[2]), end]
            wall_m.poly(tri, "stone_cloister", cope, facing=(k, 0, 0) if along_x else (0, 0, k))

    tile = (0.85, 0.8, 0.76)
    gable_tint = cp.stone_tint(4.0, 8.0, seed=71.0, worn=0.5)
    gable_tint.mat = "stone_rubble"
    roof_charnel = None
    for name, (axis, a0, a1, c, ridge) in ROOFS.items():
        within = ridge
        if name == "charnel":
            # An old roof: mossed, its ridge sunk. Inside, the timbers and the gables stop under the lowest of it.
            roof_charnel = sway_roof(roof_m, c - 4.4, c + 4.4, a0, a1, 4.0, ridge, "roof_mossy", tile, SAG)
            within = ridge - SAG
        elif axis == "x":
            cp.gable_roof(roof_m, a0, a1, c - 4.4, c + 4.4, 4.0, ridge, "roof_tiles", tile, along="x", over=0.5)
        else:
            cp.gable_roof(roof_m, c - 4.4, c + 4.4, a0, a1, 4.0, ridge, "roof_tiles", tile, along="z", over=0.5)
        mid = (a0 + a1) * 0.5
        rg.open_roof(ceil_m, axis, a0 + F, a1 - F, c, 4.4, 4.0, within, [mid] if a1 - a0 < 10 else [a0 + 4.0, a1 - 4.0])
        rg.gable(wall_m, axis, a0 + F, c, 4.4, 4.0, within, 1, tints[name])
        rg.gable(wall_m, axis, a1 - F, c, 4.4, 4.0, within, -1, tints[name])
        rg.gable(wall_m, axis, a0 - F, c, 4.4, 4.0, ridge, -1, gable_tint)
        rg.gable(wall_m, axis, a1 + F, c, 4.4, 4.0, ridge, 1, gable_tint)
        r = rg.ROOMS[name]
        rect = (r[0] + F, r[1] - F, r[2] + F, r[3] - F)
        if name == "charnel":
            ys = 0.056
            pts = [(rect[0], ys, rect[2]), (rect[1], ys, rect[2]), (rect[1], ys, rect[3]), (rect[0], ys, rect[3])]
            floor_m.poly(pts, "grave_earth", [cp.rgba((0.5, 0.44, 0.38), 0.8 + 0.3 * fbm(p[0], p[2], 0.4, 2, 1.0)) for p in pts], facing=(0, 1, 0))
        else:
            rg.floor(floor_m, rect, 0.056, "flags", 40.0 + len(name))
    st = cp.stone_tint(4.0, 9.0, seed=75.0, worn=0.5)
    rg.stack(roof_m, -24.5, -23.5, -20.6, -19.4, 4.0, 8.8, st)
    rg.stack(roof_m, 35.5, 36.5, -0.6, 0.6, 4.0, 8.8, st)
    # Thresholds, each with a riser down to the ground on both sides.
    for along, line, at, level, kind, only in rg.pieces():
        if kind in ("wall_door", "wall_gate"):
            hw = 0.47 if kind == "wall_door" else 1.5
            r = (at - hw, at + hw, line - F, line + F) if along == "x" else (line - F, line + F, at - hw, at + hw)
            c = (0.6, 0.6, 0.58, 1.0)
            floor_m.poly([(r[0], 0.056, r[2]), (r[1], 0.056, r[2]), (r[1], 0.056, r[3]), (r[0], 0.056, r[3])], "flags_worn", c, facing=(0, 1, 0))
            for k in (-1, 1):
                e = line + k * F
                pts = [(r[0], 0.0, e), (r[1], 0.0, e), (r[1], 0.056, e), (r[0], 0.056, e)] if along == "x" else [(e, 0.0, r[2]), (e, 0.0, r[3]), (e, 0.056, r[3]), (e, 0.056, r[2])]
                floor_m.poly(pts, "flags_worn", (0.42, 0.42, 0.4, 1.0), facing=(0, 0, k) if along == "x" else (k, 0, 0))
    ground(ground_m)
    # Beyond the north, east and south walls: rough grass falling away, so
    # the upper windows don't look out on nothing. (West is the lane.)
    for x0, x1, z0, z1 in ((-40.42, 86.0, -86.0, -40.42), (-40.42, 86.0, 40.42, 86.0), (40.42, 86.0, -40.42, 40.42)):
        xs, zs = cp.steps(x0, x1, 6.0), cp.steps(z0, z1, 6.0)
        for xa, xb in zip(xs, xs[1:]):
            for za, zb in zip(zs, zs[1:]):
                pts = []
                for x, z in ((xa, za), (xb, za), (xb, zb), (xa, zb)):
                    far = max(abs(x), abs(z)) - 40.42
                    pts.append((x, -0.03 - 0.04 * far, z))
                cols = [cp.rgba((0.42, 0.46, 0.34), 0.6 + 0.5 * fbm(q[0], q[2], 0.08, 3, 6.0)) for q in pts]
                ground_m.poly(pts, "grass_leafy", cols, facing=(0, 1, 0))
    plain = sum(triangles(q) for q in (wall_m, roof_m, ceil_m, floor_m, ground_m))
    dress_up(dress_m, soft_m, roof_charnel)
    print("precinct: %d triangles in the place, %d in its dressing (%d flat, %d rounded)" % (plain, triangles(dress_m) + triangles(soft_m), triangles(dress_m),
                                                                                              triangles(soft_m)))

    wall_m.build()
    roof_m.build()
    ceil_m.build()
    floor_m.build()
    ground_m.build()
    dress_m.build()
    soft_m.build(smooth=True)
    porter.export("env_precinct")


if __name__ == "__main__":
    build()
