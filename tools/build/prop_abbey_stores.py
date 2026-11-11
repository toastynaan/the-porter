"""The props of the abbey's working rooms: the stores and the granary, the
bakehouse and kitchen, the warming room and the latrine, the infirmary, the
mill. Each is its own model (art/models/prop_<name>.glb), sized to the
collision its scene already has (game/world/props/prop_<name>.tscn),
standing on the floor at its origin:

- barrel, barrel_tapped, barrel_stove: an ale cask on end, withy-hooped;
  with a spigot in it and a wet floor; with its head stove in.
- shelves: the cellarer's shelves, loaded.
- grain_sacks, grain_sacks_split, grain_sacks_gnawed: a heap of rye sacks;
  with one split and its grain run out; with one gnawed open.
- oven: the bakehouse oven, with a chamber he can crawl into.
- oven_bones: charred bones in a bed of ash, lying in the oven's chamber.
- mortar: the infirmarer's stone mortar and pestle.
- millstone: the mill's stones, the runner turned up for dressing.
- mill_wheel: the water wheel (its axle along y: the scene lays it over).
- hearth_kitchen, hearth_warming: a dead fire between stone jambs.
- latrine_seat: the long bench of the reredorter.
- cellar_closet: the boarded closet in the granary's corner (in the cellar
  scene's own coordinates).

Run: tools/build.sh prop_abbey_stores   (one prop: ... -- barrel)
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dress
import props
from porter import fbm, lerp, smoothstep
from props import CLOTH, IRON, IRON_C, OAK, OAK_DARK, PAINT, PINE, RUST_C, WOOD, beam, boards, plank, rgba, tone

RUBBLE = "stone_rubble"
ASHLAR = "stone_church"
DARK = "window_dark"
BLACK = (0.0, 0.0, 0.0, 1.0)
GRIME = dress.GRIME
# Loose grainy stuff (grain, ash, cinders, meal, a millstone's grit): untextured, as bright as its numbers.
GRIT = "grit"
SACK = (0.05, 0.047, 0.04)
RYE = (0.12, 0.1, 0.058)
STAVE = (0.52, 0.45, 0.37)
WITHY = (0.4, 0.31, 0.21)
ASH = (0.04, 0.039, 0.037)
CHAR = (0.012, 0.011, 0.01)
BONE = (0.12, 0.105, 0.075)
TAU = math.tau


# ---------------------------------------------------------------- shared

def grid(m, rows, mat, flip=False, close=False):
    """Faces through a grid of points that share their vertices (so the
    smooth mesh shades it round): `rows` is a list of rows, each a list of
    (point, colour) or (point, colour, uv). It faces the way a row's
    direction then the rows' direction turn counter-clockwise; `close`
    joins each row's end to its start."""
    ids = [[m.vert(q[0][0], q[0][1], q[0][2], q[1] if len(q[1]) == 4 else rgba(q[1]), q[2] if len(q) > 2 else (0.0, 0.0)) for q in row] for row in rows]
    n = len(ids[0])
    for j in range(len(ids) - 1):
        for i in range(n if close else n - 1):
            k = (i + 1) % n
            quad = (ids[j][i], ids[j][k], ids[j + 1][k], ids[j + 1][i])
            m.face(tuple(reversed(quad)) if flip else quad, mat)
    return ids


def ring_pts(c, r, n, turn=0.0, y=None):
    """`n` points round a level circle about `c`."""
    return [(c[0] + math.cos(TAU * i / n + turn) * r, c[1] if y is None else y, c[2] + math.sin(TAU * i / n + turn) * r) for i in range(n)]


def disc(m, c, r, n, mat, colour, up=1.0, turn=0.0):
    m.poly(ring_pts(c, r, n, turn), mat, colour if len(colour) == 4 else rgba(colour), facing=(0, up, 0))


def round_boards(m, c, r, n, colour, broken=None, mat=WOOD, spread=0.16):
    """A round of boards (a cask's head, a lid) about `c`: `n` boards
    running along x. `broken` maps a board's number to how it is left:
    None (gone), or (x0, x1) fractions of its length that remain."""
    broken = broken or {}
    cuts = [-r] + sorted(-r + 2.0 * r * (i + random.uniform(0.3, 0.7)) / n for i in range(n - 1)) + [r]
    for i in range(n):
        z0, z1 = cuts[i] + 0.0015, cuts[i + 1] - 0.0015
        col = tone(colour, spread)
        u0 = random.random()

        def reach(z):
            return math.sqrt(max(r * r - z * z, 0.0))

        zs = [z0, (z0 + z1) * 0.5, z1]
        if i in broken:
            if broken[i] is None:
                continue
            fa, fb = broken[i]
            x0, x1 = lerp(-reach(zs[1]), reach(zs[1]), fa), lerp(-reach(zs[1]), reach(zs[1]), fb)
            left = [(max(-reach(z), x0) + (random.uniform(-0.03, 0.03) if fa > 0.0 else 0.0), z) for z in zs]
            right = [(min(reach(z), x1) + (random.uniform(-0.03, 0.03) if fb < 1.0 else 0.0), z) for z in zs]
        else:
            left = [(-reach(z), z) for z in zs]
            right = [(reach(z), z) for z in zs]
        pts = left + list(reversed(right))
        clean = []
        for q in pts:
            if not clean or math.hypot(q[0] - clean[-1][0], q[1] - clean[-1][1]) > 0.004:
                clean.append(q)
        if len(clean) > 2 and math.hypot(clean[0][0] - clean[-1][0], clean[0][1] - clean[-1][1]) <= 0.004:
            clean.pop()
        if len(clean) < 3:
            continue
        m.poly([(c[0] + x, c[1], c[2] + z) for x, z in clean], mat, col, uvs=[(u0 + x * props.GRAIN, z * props.GRAIN) for x, z in clean], facing=(0, 1, 0))


def stain(m, pts_alpha, colour=dress.DARK, facing=(0, 1, 0)):
    """A stain as a fan: the first point is its middle."""
    (c, ca), rim = pts_alpha[0], pts_alpha[1:]
    for (a, aa), (b, ba) in zip(rim, rim[1:] + rim[:1]):
        m.poly([c, a, b], GRIME, [(colour[0], colour[1], colour[2], ca), (colour[0], colour[1], colour[2], aa), (colour[0], colour[1], colour[2], ba)], facing=facing)


def pool(m, c, r, strength=0.7, colour=dress.DARK, n=9, seed=0.0, lift=0.004):
    """A wet or dark place on the floor about `c`."""
    rim = []
    for i in range(n):
        a = TAU * i / n
        k = r * (0.75 + 0.4 * fbm(math.cos(a) * 1.3, math.sin(a) * 1.3, 1.0, 2, seed))
        rim.append(((c[0] + math.cos(a) * k, c[1] + lift, c[2] + math.sin(a) * k), 0.0))
    stain(m, [((c[0], c[1] + lift, c[2]), strength)] + rim, colour)


# ---------------------------------------------------------------- barrel

CASK = [(0.0, 0.283), (0.2, 0.33), (0.45, 0.347), (0.7, 0.33), (0.9, 0.283)]


def cask_r(y, prof=CASK):
    for (y0, r0), (y1, r1) in zip(prof, prof[1:]):
        if y <= y1:
            return lerp(r0, r1, (y - y0) / (y1 - y0))
    return prof[-1][1]


def cask(p, tapped=False, stove=False):
    hard, soft = p.hard, p.soft
    n = 14
    top = CASK[-1][0]
    # The staves: each its own tone, round up its length.
    for i in range(n):
        a0, a1 = TAU * i / n + 0.004, TAU * (i + 1) / n - 0.004
        col = tone(STAVE, 0.22)
        u0, w = random.random(), 0.15 * props.GRAIN
        rows = []
        for y, r in CASK:
            # Dark and damp at the foot, where it stands on the cellar floor.
            k = 0.62 + 0.38 * smoothstep(0.0, 0.3, y)
            c = (col[0] * k, col[1] * k, col[2] * k * (0.94 + 0.06 * k), 1.0)
            rows.append([((math.cos(a1) * r, y, math.sin(a1) * r), c, (u0 + w, y * props.GRAIN)), ((math.cos(a0) * r, y, math.sin(a0) * r), c, (u0, y * props.GRAIN))])
        grid(soft, rows, WOOD)
        # Its end, at the chime.
        r0, r1 = CASK[-1][1] - 0.02, CASK[-1][1]
        hard.poly([(math.cos(a0) * r0, top, math.sin(a0) * r0), (math.cos(a1) * r0, top, math.sin(a1) * r0), (math.cos(a1) * r1, top, math.sin(a1) * r1), (math.cos(a0) * r1, top, math.sin(a0) * r1)],
                  WOOD, rgba(col, 0.7), facing=(0, 1, 0))
        # Its inside face above the head (or, with the head stove in, down into the dark).
        deep = 0.42 if stove else top - 0.034
        am = (a0 + a1) * 0.5
        low = rgba(col, 0.04 if stove else 0.45)
        hard.poly([(math.cos(a0) * r0, deep, math.sin(a0) * r0), (math.cos(a1) * r0, deep, math.sin(a1) * r0), (math.cos(a1) * r0, top, math.sin(a1) * r0), (math.cos(a0) * r0, top, math.sin(a0) * r0)],
                  WOOD, [low, low, rgba(col, 0.5), rgba(col, 0.5)], facing=(-math.cos(am), 0, -math.sin(am)))
    # The hoops: split withies in pairs, lapped and bound.
    for k, y in enumerate((0.035, 0.085, 0.235, 0.285, 0.615, 0.665, 0.815, 0.865)):
        if stove and k == 7:
            continue   # the top hoop has sprung and lies round its foot
        c = tone(WITHY, 0.2)
        h = 0.03
        r0, r1, r2 = cask_r(y) + 0.002, cask_r(y + h * 0.5) + 0.008, cask_r(y + h) + 0.002
        soft.tube([(0, y, 0), (0, y + h * 0.5, 0), (0, y + h, 0)], [r0, r1, r2], n, WOOD, [rgba(c, 0.6), c, rgba(c, 0.8)])
        a = random.uniform(0.0, TAU)
        rr = cask_r(y + h * 0.5) + 0.009
        lap = props.Placed(hard, (math.sin(a) * rr, y + h * 0.5, math.cos(a) * rr), a)
        lap.box((-0.035, -h * 0.42, -0.004), (0.035, h * 0.42, 0.007), WOOD, rgba(c, 0.8), faces="xXyYZ")
    if stove:
        # The sprung hoop, fallen round the foot.
        c = tone(WITHY, 0.2)
        pts = [(math.cos(TAU * i / 16) * 0.37 + 0.03, 0.012 + 0.012 * math.sin(TAU * i / 16 * 2.0), math.sin(TAU * i / 16) * 0.36 - 0.02) for i in range(14)]
        soft.tube(pts, [0.012] * len(pts), 4, WOOD, c, caps=True)
    # The head, set down in the croze.
    y = top - 0.034
    if stove:
        round_boards(hard, (0, y, 0), CASK[-1][1] - 0.02, 5, OAK, broken={1: (0.0, 0.28), 2: None, 3: (0.74, 1.0)})
        disc(hard, (0, 0.42, 0), CASK[-1][1] - 0.02, n, DARK, BLACK)
        # A piece of it hanging in by a splinter, and one standing in the dark.
        b = props.Placed(hard, (-0.07, y - 0.01, 0.02), 0.25)
        beam(b, (0.0, 0.0, 0.0), (0.2, -0.17, 0.02), 0.1, 0.018, tone(OAK, 0.1), up=(0.5, 0.8, 0.0))
        beam(hard, (0.12, 0.44, -0.1), (0.2, 0.8, -0.05), 0.09, 0.018, rgba(OAK, 0.5), up=(1, 0, 0.2))
    else:
        round_boards(hard, (0, y, 0), CASK[-1][1] - 0.02, 5, OAK)
        # Wet rings and dust on the head.
        pool(hard, (0.06, y, -0.04), 0.12, 0.55, seed=3.0, lift=0.003)
    # The bung in the bilge.
    a = 2.2
    r = cask_r(0.47)
    soft.tube([(math.cos(a) * (r - 0.01), 0.47, math.sin(a) * (r - 0.01)), (math.cos(a) * (r + 0.012), 0.47, math.sin(a) * (r + 0.012))], [0.03, 0.026], 7, WOOD, rgba(PINE, 0.9), caps=True)
    if tapped:
        # A wooden spigot low in its front, the key through it, and what it has dripped.
        y = 0.15
        r = cask_r(y)
        soft.tube([(0.0, y, -r + 0.01), (0.0, y, -r - 0.05), (0.0, y - 0.004, -r - 0.075)], [0.021, 0.017, 0.014], 7, WOOD, rgba(PINE, 0.75), caps=True)
        soft.tube([(0.0, y + 0.05, -r - 0.035), (0.0, y - 0.02, -r - 0.035)], [0.008, 0.007], 5, WOOD, rgba(OAK, 0.8), caps=True)
        beam(hard, (-0.028, y + 0.052, -r - 0.035), (0.028, y + 0.052, -r - 0.035), 0.014, 0.02, rgba(OAK, 0.8))

        def f(u, v):
            a = -math.pi * 0.5 + (u - 0.5) * 0.5
            yy = lerp(0.0, y - 0.01, v)
            rr = cask_r(yy) + 0.012
            return (math.cos(a) * rr, yy, math.sin(a) * rr)

        def c(u, v):
            wide = 0.5 - 0.3 * v
            return (0.02, 0.016, 0.012, 0.85 * max(0.0, 1.0 - (abs(u - 0.5) / wide) ** 2) * (0.6 + 0.4 * v))

        props.sheet(hard, f, 4, 3, GRIME, c, flip=True)
        pool(hard, (0.01, 0.0, -0.4), 0.26, 0.8, (0.02, 0.016, 0.012), seed=5.0)
        pool(hard, (-0.06, 0.0, -0.52), 0.12, 0.6, (0.02, 0.016, 0.012), seed=6.0, lift=0.005)


def barrel(p):
    cask(p)


def barrel_tapped(p):
    cask(p, tapped=True)


def barrel_stove(p):
    cask(p, stove=True)


# ---------------------------------------------------------------- sacks

class Sack:
    """A full sack lying on its underside at `at` (the middle of its
    underside), its tied mouth toward local +z, turned `yaw` and tipped
    `tilt` (its mouth end down). `surface(t, a)` gives a point on it, and
    `out(t, a)` the way the cloth faces there (t: -0.5 its sewn end .. 0.5
    its mouth; a: round it, 0 its side, a quarter turn its top)."""

    STATIONS = [(-0.5, 0.86, 0.1), (-0.468, 0.96, 0.6), (-0.36, 1.0, 0.93), (-0.1, 1.0, 1.0), (0.17, 0.98, 0.97), (0.3, 0.84, 0.88), (0.375, 0.5, 0.58), (0.408, 0.17, 0.26), (0.425, 0.17, 0.26), (0.49, 0.4, 0.36)]

    def __init__(self, m, at, yaw=0.0, tilt=0.0, length=1.02, wide=0.5, thick=0.28, colour=SACK, seed=0.0, droop=0.0, slack=0.0):
        self.at, self.length, self.wide, self.thick, self.seed, self.droop, self.slack = at, length, wide, thick, seed, droop, slack
        self.cy, self.sy = math.cos(yaw), math.sin(yaw)
        self.ct, self.st = math.cos(tilt), math.sin(tilt)
        n = 8
        tint = random.uniform(0.78, 1.18)
        rows = []
        for j, (t, _kw, _kh) in enumerate(self.STATIONS):
            row = []
            for i in range(n):
                a = TAU * (i + 0.5) / n
                k = (0.74 + 0.26 * (0.5 + 0.5 * math.sin(a))) * (0.9 + 0.16 * fbm(t * 4.0 + seed, math.cos(a) * 1.5 + math.sin(a), 1.0, 2, seed)) * tint
                c = rgba(colour, k)
                if j in (len(self.STATIONS) - 2, len(self.STATIONS) - 3):
                    c = (0.016, 0.013, 0.009, 1.0)   # the cord round its neck
                row.append((self.surface(t, a), c))
            rows.append(row)
        grid(m, rows, CLOTH, close=True)
        m.poly([q[0] for q in rows[0]], CLOTH, rgba(colour, 0.7 * tint), facing=self.turn((0, 0, -1)))
        # The gathered mouth: folds running in to its middle.
        ring = [q[0] for q in rows[-1]]
        mid = self.surface(0.47, 0.0, centre=True)
        for i in range(n):
            m.poly([ring[i], ring[(i + 1) % n], mid], CLOTH, [rgba(colour, 0.9 * tint), rgba(colour, 0.9 * tint), rgba(colour, 0.55 * tint)], facing=self.turn((0, 0, 1)))

    def turn(self, v):
        x, y, z = v
        y, z = y * self.ct - z * self.st, y * self.st + z * self.ct
        return (x * self.cy + z * self.sy, y, -x * self.sy + z * self.cy)

    def local(self, t, a, centre=False):
        ts = [s[0] for s in self.STATIONS]
        t = min(max(t, ts[0]), ts[-1])
        for (t0, w0, h0), (t1, w1, h1) in zip(self.STATIONS, self.STATIONS[1:]):
            if t <= t1:
                f = (t - t0) / (t1 - t0)
                kw, kh = lerp(w0, w1, f), lerp(h0, h1, f)
                break
        ca, sa = math.cos(a), math.sin(a)
        ex = math.copysign(abs(ca) ** 0.75, ca)
        ey = math.copysign(abs(sa) ** 0.75, sa)
        z = t * self.length
        lump = 1.0 + 0.1 * fbm(z * 3.0 + self.seed * 3.1, ca * 1.2 + sa * 0.7, 1.0, 2, self.seed)
        h = self.thick * kh * (1.0 - self.slack * math.exp(-((t - 0.05) / 0.25) ** 2))
        x = ex * self.wide * 0.5 * kw * lump
        # It lies on its underside: flat below, round above; its neck a little off the floor.
        y = (0.36 + 0.64 * ey) * h if ey > 0.0 else (0.36 + 0.36 * ey) * h
        lift = 0.3 * self.thick * (1.0 - kh) * (0.4 if t < 0.0 else 1.0) - self.droop * (2.0 * t) ** 2
        yc = 0.36 * h
        # Above the cord the cloth stands out in pleats.
        pleat = 1.0 + 0.13 * math.sin(4.0 * a) * smoothstep(0.425, 0.5, t)
        if centre:
            return (0.0, yc + lift, z)
        return (x * pleat, yc + (y - yc) * pleat + lift, z)

    def surface(self, t, a, lift=0.0, centre=False):
        p = self.local(t, a, centre)
        if lift:
            o = self.out(t, a, turned=False)
            p = (p[0] + o[0] * lift, p[1] + o[1] * lift, p[2] + o[2] * lift)
        q = self.turn(p)
        return (self.at[0] + q[0], self.at[1] + q[1], self.at[2] + q[2])

    def out(self, t, a, turned=True):
        p, pa, pt = self.local(t, a), self.local(t, a + 0.05), self.local(t + 0.01, a)
        u, v = props._v(p, pa), props._v(p, pt)
        o = props._norm(props._cross(u, v))
        return self.turn(o) if turned else o

    def patch(self, m, t, a, outline, mat, colour, lift=0.004, dt=1.0, da=1.0):
        """A patch on the cloth about (t, a): `outline` is (along, round) offsets."""
        col = colour if len(colour) == 4 else rgba(colour)
        m.poly([self.surface(t + q[0] * dt, a + q[1] * da, lift) for q in outline], mat, col, facing=self.out(t, a))


def spill(m, at, rx, rz, h, colour=RYE, seed=0.0, against=False, stray=26, way=-1.0):
    """Grain (or ash) run out on the floor about `at`: a low cone, ragged
    at its edge. `against`: half a cone, heaped against something behind
    it, and spreading toward -z (or +z with `way` 1)."""
    def f(u, v):
        a, r = (math.pi + u * math.pi if against else u * TAU), v
        k = 1.0 + 0.16 * fbm(math.cos(a) * 1.4, math.sin(a) * 1.4, 1.0, 3, seed)
        x, z = at[0] + math.cos(a) * rx * r * k, at[2] - way * math.sin(a) * rz * r * k
        return (x, at[1] + 0.002 + h * (1.0 - r) * (1.0 - 0.35 * r), z)

    def c(u, v):
        return rgba(colour, 0.8 + 0.3 * fbm(u * 9.0, v * 4.0, 1.0, 2, seed + 1.0))

    props.sheet(m, f, 10 if against else 12, 5, GRIT, c, flip=way > 0)
    # Stray grains beyond it.
    for _ in range(stray):
        a, r = random.uniform(math.pi if against else 0.0, TAU), random.uniform(0.9, 1.5)
        x, z = at[0] + math.cos(a) * rx * r, at[2] - way * math.sin(a) * rz * r
        s, b = 0.007, random.uniform(0.0, TAU)
        m.poly([(x + math.cos(b) * s, at[1] + 0.003, z + math.sin(b) * s), (x + math.cos(b + 2.2) * s * 0.5, at[1] + 0.003, z + math.sin(b + 2.2) * s * 0.5),
                (x + math.cos(b + 4.1) * s * 0.5, at[1] + 0.003, z + math.sin(b + 4.1) * s * 0.5)], PAINT, rgba(colour, random.uniform(0.8, 1.2)), facing=(0, 1, 0))


def sack_heap(p, kind):
    """Six sacks in three rows of two, lying along x, the upper ones slumped
    into the hollows of those under them."""
    m = p.soft
    seed = {"heap": 1.0, "split": 20.0, "gnawed": 40.0}[kind]
    flip = 1.0 if kind != "split" else -1.0
    half = math.pi * 0.5
    low = []
    for i, z in enumerate((-0.215, 0.215)):
        low.append(Sack(m, (random.uniform(-0.02, 0.02), 0.0, z), flip * half + random.uniform(-0.05, 0.05), 0.0, 1.06, 0.47, 0.3, seed=seed + i))
    y = 0.255
    for i, z in enumerate((-0.2, 0.22)):
        Sack(m, (random.uniform(-0.04, 0.04), y, z), -flip * half + random.uniform(-0.1, 0.1), 0.0, 1.04, 0.46, 0.29, seed=seed + 4 + i, droop=0.035)
    y = 0.5
    if kind == "heap":
        Sack(m, (-0.03, y, -0.19), half + 0.12, 0.0, 1.02, 0.46, 0.28, seed=seed + 8, droop=0.05)
        Sack(m, (0.04, y + 0.005, 0.2), -half - 0.16, 0.0, 1.0, 0.45, 0.28, seed=seed + 9, droop=0.06)
    elif kind == "split":
        Sack(m, (0.03, y, -0.18), half - 0.18, 0.0, 1.02, 0.46, 0.28, seed=seed + 8, droop=0.06)
        Sack(m, (-0.04, y, 0.21), half + 0.1, 0.0, 1.0, 0.45, 0.28, seed=seed + 9, droop=0.05)
    else:
        Sack(m, (0.05, y, -0.2), -half + 0.08, 0.0, 1.02, 0.46, 0.28, seed=seed + 8, droop=0.05)
        Sack(m, (-0.04, y, 0.2), half + 0.22, 0.0, 0.98, 0.45, 0.28, seed=seed + 9, droop=0.06)
    # What is wrong with it is on its +z side and its -x end: in the granary the heaps stand in the far corner and
    # are seen from the south and the west.
    front = low[1]
    side = math.pi if flip > 0 else 0.0   # the angle round the sack that looks out at +z
    up = -1.0 if flip > 0 else 1.0        # and the way round it that climbs
    if kind == "split":
        # A seam gone along its side: the tear dark, the grain run down from it over the floor.
        a = side + up * 0.62
        tear = [(-0.17, 0.0), (-0.07, 0.17), (0.05, 0.22), (0.16, 0.03), (0.08, -0.2), (-0.06, -0.18)]
        front.patch(p.hard, 0.02, a, tear, PAINT, (0.006, 0.005, 0.004, 1.0), 0.005)
        q = front.surface(0.02, a - up * 0.12)
        spill(m, (q[0], 0.0, q[2] - 0.05), 0.4, 0.3, q[1], seed=seed, against=True, way=1.0)
        spill(m, (q[0] - 0.34, 0.0, q[2] + 0.1), 0.17, 0.12, 0.025, seed=seed + 2.0, stray=8)
    elif kind == "gnawed":
        # A corner gnawed through at the floor: a ragged black hole, the threads, a little grain, droppings.
        t, a = -0.41, side + up * 0.32
        hole = [(-0.05, -0.02), (-0.03, 0.2), (0.0, 0.1), (0.02, 0.26), (0.05, 0.06), (0.075, 0.12), (0.06, -0.1), (0.03, -0.24), (0.0, -0.12), (-0.02, -0.27)]
        front.patch(p.hard, t, a, hole, PAINT, (0.006, 0.005, 0.005, 1.0), 0.006)
        for q in hole[1::2]:
            front.patch(p.hard, t + q[0], a + q[1], [(0.0, -0.03), (0.0, 0.03), (0.03 if q[0] > 0 else -0.03, 0.0)], CLOTH, rgba(SACK, 1.5), 0.008)
        q = front.surface(t, a)
        spill(m, (q[0] - 0.02, 0.0, q[2] - 0.02), 0.16, 0.12, 0.06, seed=seed, against=True, stray=14, way=1.0)
        for _ in range(14):
            x, z = q[0] + random.uniform(-0.3, 0.25), q[2] + random.uniform(0.06, 0.28)
            b = random.uniform(0.0, TAU)
            p.hard.poly([(x + math.cos(b) * 0.008, 0.004, z + math.sin(b) * 0.008), (x - math.cos(b) * 0.008, 0.004, z - math.sin(b) * 0.008), (x - math.sin(b) * 0.004, 0.006, z + math.cos(b) * 0.004)],
                        PAINT, (0.008, 0.007, 0.006, 1.0), facing=(0, 1, 0))


def grain_sacks(p):
    sack_heap(p, "heap")


def grain_sacks_split(p):
    sack_heap(p, "split")


def grain_sacks_gnawed(p):
    sack_heap(p, "gnawed")


# ---------------------------------------------------------------- shelves

def lathe(m, at, profile, sides, mat, colour, inside=False, turn=0.0):
    """A turned shape standing on `at`: `profile` is (height, radius) pairs
    going up, `colour` one colour or one per pair. `inside`: seen from
    within (a bowl's hollow)."""
    rows = []
    for j, (y, r) in enumerate(profile):
        c = colour[j] if isinstance(colour, list) else colour
        rows.append([((at[0] + math.cos(TAU * i / sides + turn) * r, at[1] + y, at[2] + math.sin(TAU * i / sides + turn) * r), c) for i in range(sides)])
    return grid(m, rows, mat, flip=not inside, close=True)


def crock(m, at, r=0.13, h=0.28, colour=props.CLAY, sides=9):
    props.pot(m, at, [(0.0, r * 0.6), (h * 0.1, r * 0.84), (h * 0.45, r), (h * 0.78, r * 0.9), (h * 0.92, r * 0.7), (h, r * 0.78)], colour, sides)


def tied_jar(m, at, r=0.07, h=0.16, colour=props.CLAY, cloth=props.LINEN):
    """A jar with a cloth tied down over its mouth."""
    props.pot(m, at, [(0.0, r * 0.7), (h * 0.35, r), (h * 0.72, r * 0.94), (h * 0.9, r * 0.72), (h, r * 0.76)], colour, 8, dark_inside=False)
    rm = r * 0.76
    c = rgba(cloth, random.uniform(0.7, 1.0))
    cord = (0.016, 0.013, 0.009, 1.0)
    x, y, z = at
    m.tube([(x, y + h - 0.05, z), (x, y + h - 0.022, z), (x, y + h - 0.014, z), (x, y + h + 0.004, z), (x, y + h + 0.012, z)],
           [rm + 0.022, rm + 0.007, rm + 0.004, rm + 0.007, rm * 0.5], 8, CLOTH, [rgba(c, 0.8), cord, cord, c, c], caps=True)


def jug(m, at, yaw=0.0, tilt=0.0, k=1.0, colour=props.CLAY):
    j = props.Placed(m, at, yaw, k, tilt)
    props.pot(j, (0.0, 0.0, 0.0), [(0.0, 0.06), (0.05, 0.085), (0.13, 0.09), (0.19, 0.06), (0.23, 0.045), (0.26, 0.055)], colour=colour, sides=9)
    j.tube([(0.055, 0.24, 0.0), (0.12, 0.22, 0.0), (0.13, 0.15, 0.0), (0.085, 0.1, 0.0)], [0.012] * 4, 5, PAINT, rgba(colour))


def cheese(m, at, r=0.14, h=0.1, cut=0.0, yaw=0.0, colour=(0.1, 0.078, 0.036)):
    """A wheel of cheese; `cut` is how much of the round is gone (radians)."""
    c = rgba(colour, random.uniform(0.85, 1.05))
    n = 12
    if not cut:
        m.tube([(at[0], at[1] + y, at[2]) for y in (0.0, h * 0.2, h * 0.8, h)], [r * 0.88, r, r, r * 0.88], n, PAINT, c, caps=True)
        return
    q = props.Placed(m, at, yaw)
    a0, a1 = cut * 0.5, TAU - cut * 0.5
    arc = [(math.cos(lerp(a0, a1, i / n)) * r, math.sin(lerp(a0, a1, i / n)) * r) for i in range(n + 1)]
    q.poly([(0.0, h, 0.0)] + [(x, h, z) for x, z in arc], PAINT, c, facing=(0, 1, 0))
    for (xa, za), (xb, zb) in zip(arc, arc[1:]):
        q.poly([(xa, 0.0, za), (xb, 0.0, zb), (xb, h, zb), (xa, h, za)], PAINT, rgba(c, 0.85), facing=(xa + xb, 0.0, za + zb))
    pale = rgba(colour, 1.25)
    for (x, z), way in ((arc[0], -1.0), (arc[-1], 1.0)):
        q.poly([(0.0, 0.0, 0.0), (x, 0.0, z), (x, h, z), (0.0, h, 0.0)], PAINT, pale, facing=(0.3, 0.0, way))


def basket(m, at, r=0.15, h=0.2, handle=True, colour=(0.075, 0.058, 0.032)):
    """A round withy basket, its weave in ridges."""
    n = max(int(h / 0.022), 3)
    prof = []
    for i in range(n + 1):
        t = i / n
        prof.append((h * t, r * (0.72 + 0.28 * t ** 0.6) + (0.004 if i % 2 else 0.0)))
    c = rgba(colour, random.uniform(0.85, 1.1))
    cols = [rgba(c, 0.75 if i % 2 == 0 else 1.05) for i in range(n + 1)]
    lathe(m, at, prof, 10, PAINT, cols)
    disc(m, (at[0], at[1] + h - 0.03, at[2]), prof[-1][1] - 0.008, 10, PAINT, (0.012, 0.01, 0.008, 1.0))
    m.tube([(at[0], at[1] + h - 0.006, at[2]), (at[0], at[1] + h + 0.008, at[2])], [prof[-1][1] + 0.006, prof[-1][1] + 0.002], 10, PAINT, rgba(c, 0.9))
    if handle:
        rr = prof[-1][1]
        arc = [(at[0] + math.cos(math.pi * i / 8) * rr, at[1] + h + math.sin(math.pi * i / 8) * rr * 0.75, at[2]) for i in range(9)]
        m.tube(arc, [0.008] * 9, 4, PAINT, rgba(c, 0.9))


def shelves(p):
    hard, soft = p.hard, p.soft
    levels = (0.2, 0.62, 1.04, 1.46)
    for x in (-1.46, -0.5, 0.5, 1.46):
        for z in (-0.215, 0.215):
            beam(hard, (x, 0.0, z), (x, 1.8 - random.uniform(0.0, 0.03), z), 0.06, 0.06, tone(OAK_DARK))
        for y in levels:
            beam(hard, (x, y - 0.055, -0.185), (x, y - 0.055, 0.185), 0.04, 0.05, tone(OAK_DARK), ends="")
    for y in levels:
        boards(hard, (-1.5, y - 0.03, -0.25), (1.5, y, 0.25), "x", "z", 2, OAK, gap=0.006, uneven=0.004, ragged=0.012)
    beam(hard, (-1.46, 1.76, 0.215), (1.46, 1.76, 0.215), 0.03, 0.05, tone(OAK_DARK), ends="")
    for sx in (-1, 1):
        beam(hard, (sx * 1.46, 0.26, 0.238), (sx * 0.5, 1.4, 0.238), 0.06, 0.02, tone(OAK_DARK), up=(0, 0, 1))
    a, b, c, d = levels
    # The floor shelf: the heavy things. Two crocks, one with a board for a lid; a sack; a coffer; a coil of rope.
    crock(soft, (-1.17, a, 0.0), 0.15, 0.31)
    props.slab(hard, [(math.cos(TAU * i / 9) * 0.125, math.sin(TAU * i / 9) * 0.125) for i in range(9)], "y", a + 0.31, a + 0.328, tone(OAK, 0.1))
    crock(soft, (-0.8, a, 0.04), 0.125, 0.26, colour=(0.03, 0.027, 0.022))
    Sack(soft, (-0.02, a, 0.01), math.pi * 0.5 + 0.05, 0.0, 0.84, 0.4, 0.26, seed=61.0)
    boards(hard, (0.62, a, -0.17), (1.08, a + 0.25, 0.17), "x", "y", 2, OAK_DARK, uneven=0.0)
    lid = props.Placed(hard, (0.86, a + 0.25, 0.0), 0.09)
    plank(lid, (-0.25, 0.0, -0.185), (0.25, 0.022, 0.185), tone(OAK_DARK), along="x")
    for x in (0.72, 0.98):
        props.strap(hard, (x, a + 0.01, -0.17), (x, a + 0.24, -0.17), (0, 0, -1), width=0.03, nails=2, colour=RUST_C)
    coil = [(1.28 + math.cos(i * 0.72) * (0.1 - i * 0.0012), a + 0.014 + i * 0.0016, 0.02 + math.sin(i * 0.72) * (0.1 - i * 0.0012)) for i in range(19)]
    props.rope(soft, coil, r=0.013, sides=4)
    # The second: jars tied over with cloth, one taken (its ring left in the dust), one pushed back; cheeses, one cut; jugs and bowls.
    for x, z in ((-1.34, -0.07), (-1.17, -0.09), (-0.83, -0.06), (-0.7, 0.1)):
        tied_jar(soft, (x, b, z), random.uniform(0.066, 0.076), random.uniform(0.15, 0.18))
    pool(hard, (-1.0, b, -0.08), 0.075, 0.6, seed=8.0, lift=0.003)
    cheese(soft, (-0.2, b, 0.02), 0.145, 0.1)
    cheese(soft, (0.16, b, -0.03), 0.125, 0.09, cut=1.5, yaw=1.2)
    k = props.Placed(hard, (0.0, b + 0.002, -0.17), 0.25)
    plank(k, (-0.07, 0.0, -0.008), (0.02, 0.014, 0.008), tone(OAK_DARK), along="x")
    k.poly([(0.02, 0.006, -0.008), (0.14, 0.006, -0.002), (0.02, 0.006, 0.008)], IRON, IRON_C, facing=(0, 1, 0))
    jug(soft, (0.72, b, 0.06), 0.6)
    for i in range(3):
        props.pot(soft, (0.99 + i * 0.004, b + i * 0.018, -0.02), [(0.0, 0.04), (0.02, 0.075), (0.042, 0.09)], colour=(0.045, 0.033, 0.022), sides=9, dark_inside=i == 2)
    jug(soft, (1.33, b + 0.088, -0.02), 1.9, math.pi * 0.5, 0.95, colour=(0.03, 0.027, 0.022))
    # The third: folded cloths, a bundle of rushes for lights, small things; a basket and a tied crock.
    props.tick(soft, -1.38, -0.98, -0.19, 0.17, c, 0.05, colour=props.LINEN, lumps=0.1, seed=31.0, edge=0.07)
    props.tick(soft, -1.36, -1.0, -0.17, 0.15, c + 0.045, 0.045, colour=props.UNDYED, lumps=0.1, seed=32.0, edge=0.07)
    props.tick(soft, -1.34, -1.04, -0.18, 0.1, c + 0.085, 0.04, colour=props.LINEN, lumps=0.15, seed=33.0, edge=0.08)
    ts = (0.0, 0.26, 0.28, 0.3, 0.68, 0.7, 0.72, 1.0)
    straw, cord = rgba(props.STRAW, 1.2), (0.016, 0.013, 0.009, 1.0)
    soft.tube([(lerp(-0.92, -0.56, t), c + 0.042, lerp(-0.08, 0.0, t)) for t in ts], [0.04, 0.041, 0.037, 0.041, 0.041, 0.037, 0.041, 0.043], 6, PAINT,
              [straw, straw, cord, straw, straw, cord, straw, rgba(props.STRAW, 0.7)], caps=True)
    props.pot(soft, (0.26, c, 0.1), [(0.0, 0.04), (0.025, 0.075), (0.05, 0.09)], colour=(0.045, 0.033, 0.022), sides=9)
    soft.tube([(-0.3, c + y, 0.08) for y in (0.0, 0.02, 0.055, 0.09, 0.105)], [0.02, 0.045, 0.056, 0.042, 0.015], 7, CLOTH, rgba(props.LINEN, 0.8), caps=True)
    basket(soft, (0.9, c, 0.0), 0.15, 0.19, handle=False)
    tied_jar(soft, (1.25, c, 0.05), 0.095, 0.21, colour=(0.03, 0.027, 0.022))
    # Tallow dips hung in pairs by their wicks from a rod under the top shelf; some pairs gone.
    beam(hard, (-0.47, d - 0.075, -0.1), (0.47, d - 0.075, -0.1), 0.016, 0.016, tone(PINE))
    for x in (-0.4, -0.33, -0.26, -0.19, -0.12, 0.09, 0.16, 0.37):
        for z in (-0.122, -0.078):
            xx, top = x + random.uniform(-0.006, 0.006), d - 0.067
            long = random.uniform(0.2, 0.24)
            sway = random.uniform(-0.01, 0.01)
            wax = rgba(props.WAX, random.uniform(0.7, 0.9))
            soft.tube([(xx, top, -0.1), (xx, top - 0.03, z), (xx + sway * 0.3, top - 0.055, z), (xx + sway, top - long, z), (xx + sway, top - long - 0.008, z)],
                      [0.002, 0.003, 0.009, 0.012, 0.006], 5, PAINT, [(0.03, 0.025, 0.02, 1.0), wax, wax, wax, wax], caps=True)
    # The top: a handled basket, a crock, a small coffer, two jars (one over on its side), and a bay left empty.
    basket(soft, (-1.08, d, 0.0), 0.165, 0.2)
    crock(soft, (-0.72, d, 0.05), 0.1, 0.23)
    boards(hard, (-0.24, d, -0.14), (0.12, d + 0.15, 0.13), "x", "y", 2, OAK, uneven=0.0)
    plank(hard, (-0.25, d + 0.15, -0.15), (0.13, d + 0.168, 0.14), tone(OAK), along="x")
    tied_jar(soft, (0.3, d, 0.02), 0.07, 0.16)
    j = props.Placed(soft, (0.86, d + 0.07, 0.02), 0.5, tilt=math.pi * 0.5)
    props.pot(j, (0.0, 0.0, 0.0), [(0.0, 0.05), (0.06, 0.07), (0.12, 0.066), (0.15, 0.05), (0.165, 0.054)], colour=props.CLAY, sides=8)
    # Herbs hung to dry from its edge.
    for x in (0.98, 1.16):
        g = (0.03, 0.034, 0.018)
        soft.tube([(x, d - 0.03, -0.235), (x, d - 0.09, -0.235), (x + 0.005, d - 0.16, -0.23), (x, d - 0.26, -0.225), (x, d - 0.3, -0.225)],
                  [0.005, 0.012, 0.035, 0.05, 0.02], 6, PAINT, [rgba(g, 0.7), rgba(g, 0.8), rgba(g), rgba(g, 1.1), rgba(g, 0.8)], caps=True)
        hard.box((x - 0.004, d - 0.032, -0.262), (x + 0.004, d - 0.01, -0.25), IRON, IRON_C)
    # Cobwebs where nothing is moved: the empty top corner, and under the floor shelf.
    dress.cobweb(hard, (1.43, 1.77, 0.2), (0, -1, 0), (-1, 0, 0), 0.42, 3)
    dress.cobweb(hard, (1.43, d + 0.001, 0.19), (-1, 0, 0), (0, 0, -1), 0.36, 4, sag=0.0)
    dress.cobweb(hard, (-1.43, a - 0.05, 0.0), (0, -1, 0.2), (1, 0, 0.2), 0.3, 5)


# ---------------------------------------------------------------- mortar

def sprig(m, at, yaw, length=0.11, colour=(0.032, 0.042, 0.02)):
    """A cut sprig lying flat: a stem and its leaves."""
    s = props.Placed(m, at, yaw)
    s.poly([(0.0, 0.0, -0.0012), (length, 0.0, -0.0008), (length, 0.0, 0.0008), (0.0, 0.0, 0.0012)], PAINT, rgba(colour, 0.7), facing=(0, 1, 0))
    n = int(length / 0.014)
    for i in range(1, n):
        x = length * i / n
        for side in (-1, 1):
            w = 0.018 * (0.5 + 0.5 * math.sin(math.pi * i / n)) * random.uniform(0.7, 1.2)
            s.poly([(x, 0.0005, 0.0), (x + 0.012, 0.002 + random.uniform(0.0, 0.004), side * w * 0.6), (x + 0.02, 0.001, side * w), (x + 0.008, 0.001, side * w * 0.5)], PAINT,
                   rgba(colour, random.uniform(0.7, 1.25)), facing=(0, 1, 0))


def mortar(p):
    hard, soft = p.hard, p.soft
    stone = (0.075, 0.075, 0.072, 1.0)
    low = (0.05, 0.05, 0.048, 1.0)
    ASHLAR = PAINT
    lathe(soft, (0, 0, 0), [(0.0, 0.066), (0.012, 0.074), (0.07, 0.092), (0.128, 0.099), (0.15, 0.097)], 12, ASHLAR, [low, low, stone, stone, stone])
    disc(soft, (0, 0.001, 0), 0.066, 12, ASHLAR, low, up=-1.0)
    grid(soft, [[(q, stone) for q in ring_pts((0, 0.15, 0), 0.097, 12)], [(q, stone) for q in ring_pts((0, 0.15, 0), 0.072, 12)]], ASHLAR, flip=True, close=True)
    dark = (0.025, 0.025, 0.022, 1.0)
    lathe(soft, (0, 0, 0), [(0.066, 0.02), (0.08, 0.05), (0.12, 0.068), (0.15, 0.072)], 12, ASHLAR, [dark, dark, low, stone], inside=True)
    # What was being ground: dark green in the bottom.
    disc(soft, (0, 0.074, 0), 0.04, 12, PAINT, (0.02, 0.026, 0.012, 1.0))
    # Its lugs.
    for sx in (-1, 1):
        hard.box((sx * 0.094 - 0.012, 0.07, -0.016), (sx * 0.094 + 0.012, 0.125, 0.016), PAINT, low, faces="xXyYzZ")
    # The pestle left standing in it.
    props.turned(soft, (0.012, 0.074, 0.008), (0.085, 0.235, -0.035), [(0.0, 0.016), (0.1, 0.021), (0.3, 0.017), (0.55, 0.011), (0.9, 0.012), (1.0, 0.009)], tone(OAK, 0.05), sides=7)
    # Sprigs beside it, and what has dropped from them.
    sprig(hard, (-0.14, 0.002, -0.1), 0.5, 0.12)
    sprig(hard, (-0.19, 0.003, -0.07), 0.9, 0.1)
    sprig(hard, (-0.11, 0.004, -0.13), 0.2, 0.09, colour=(0.04, 0.038, 0.018))
    for _ in range(9):
        x, z = random.uniform(-0.17, 0.02), random.uniform(-0.17, -0.1)
        b = random.uniform(0.0, TAU)
        hard.poly([(x, 0.002, z), (x + math.cos(b) * 0.008, 0.002, z + math.sin(b) * 0.008), (x - math.sin(b) * 0.004, 0.003, z + math.cos(b) * 0.004)], PAINT, (0.03, 0.038, 0.018, 1.0),
                  facing=(0, 1, 0))


# ---------------------------------------------------------------- millstone

GRITSTONE = (0.072, 0.07, 0.065)
MEAL = (0.17, 0.155, 0.125)


def dust(m, c, r0, r1, strength=0.4, colour=MEAL, n=14, seed=0.0, lift=0.003):
    """Meal lying in a ring about `c`, thick at `r0` and gone by `r1`."""
    for i in range(n):
        a0, a1 = TAU * i / n, TAU * (i + 1) / n
        k0 = 0.5 + 0.5 * fbm(math.cos(a0) * 2.0, math.sin(a0) * 2.0, 1.0, 2, seed)
        k1 = 0.5 + 0.5 * fbm(math.cos(a1) * 2.0, math.sin(a1) * 2.0, 1.0, 2, seed)
        ra, rb = lerp(r0, r1, 0.5 + 0.5 * k0), lerp(r0, r1, 0.5 + 0.5 * k1)
        pts = [(c[0] + math.cos(a0) * r0, c[1] + lift, c[2] + math.sin(a0) * r0), (c[0] + math.cos(a1) * r0, c[1] + lift, c[2] + math.sin(a1) * r0),
               (c[0] + math.cos(a1) * rb, c[1] + lift, c[2] + math.sin(a1) * rb), (c[0] + math.cos(a0) * ra, c[1] + lift, c[2] + math.sin(a0) * ra)]
        cols = [(colour[0], colour[1], colour[2], strength * (0.4 + 0.6 * k0)), (colour[0], colour[1], colour[2], strength * (0.4 + 0.6 * k1)), (colour[0], colour[1], colour[2], 0.0),
                (colour[0], colour[1], colour[2], 0.0)]
        m.poly(pts, GRIME, cols, facing=(0, 1, 0))


def stone_round(p, y0, y1, r, eye=0.0, n=20, seed=0.0, top=True):
    """A millstone lying flat: its skirt (round), its top with an eye through it."""
    k = [1.0 + 0.022 * fbm(math.cos(TAU * i / n) * 2.0, math.sin(TAU * i / n) * 2.0, 1.0, 2, seed) for i in range(n)]
    rows = []
    for y, s, shade in ((y0, 0.985, 0.6), (y0 + 0.02, 1.0, 0.75), (y1 - 0.02, 1.0, 1.0), (y1, 0.975, 1.05)):
        rows.append([((math.cos(TAU * i / n) * r * s * k[i], y, math.sin(TAU * i / n) * r * s * k[i]), rgba(GRITSTONE, shade * (0.85 + 0.3 * fbm(i * 0.9, y * 9.0, 1.0, 2, seed)))) for i in range(n)])
    grid(p.soft, rows, GRIT, flip=True, close=True)
    if top:
        for i in range(n):
            a0, a1 = TAU * i / n, TAU * (i + 1) / n
            j = (i + 1) % n
            c = rgba(GRITSTONE, 1.0 + 0.22 * fbm(i * 1.3, 0.0, 1.0, 2, seed + 2.0))
            p.hard.poly([(math.cos(a0) * eye, y1, math.sin(a0) * eye), (math.cos(a1) * eye, y1, math.sin(a1) * eye), (math.cos(a1) * r * 0.975 * k[j], y1, math.sin(a1) * r * 0.975 * k[j]),
                         (math.cos(a0) * r * 0.975 * k[i], y1, math.sin(a0) * r * 0.975 * k[i])], GRIT, c, facing=(0, 1, 0))


def millstone(p):
    hard, soft = p.hard, p.soft
    # The bedstone, and the runner lifted off it and turned face up on two battens to be dressed.
    stone_round(p, 0.0, 0.215, 0.69, seed=1.0, top=True)
    for z in (-0.3, 0.32):
        beam(hard, (-0.6, 0.235, z), (0.6, 0.235, z + 0.03), 0.07, 0.04, tone(OAK_DARK))
    y0, y1, r, eye = 0.255, 0.49, 0.655, 0.085
    stone_round(p, y0, y1, r, eye, seed=2.0)
    grid(soft, [[(q, BLACK) for q in ring_pts((0, y0 + 0.02, 0), eye, 20)], [(q, rgba(GRITSTONE, 0.8)) for q in ring_pts((0, y1, 0), eye, 20)]], GRIT, close=True)
    disc(hard, (0, y0 + 0.02, 0), eye, 20, DARK, BLACK)
    # The slots for the rynd, either side of the eye.
    for sx in (-1, 1):
        hard.poly([(sx * eye * 0.9, y1 + 0.0015, -0.03), (sx * (eye + 0.085), y1 + 0.0015, -0.03), (sx * (eye + 0.085), y1 + 0.0015, 0.03), (sx * eye * 0.9, y1 + 0.0015, 0.03)], GRIT,
                  rgba(GRITSTONE, 0.18), facing=(0, 1, 0))
    # The furrows: eight harps, each a master furrow and three behind it, all cut on the skew.
    d, w, harps = 0.125, 0.11, 8
    rim = r * 0.965
    for h in range(harps):
        th = TAU * h / harps
        nx, nz = math.cos(th), math.sin(th)
        tx, tz = -nz, nx
        for j in range(4):
            off = d + j * w
            s0 = 0.02 if j == 0 else j * w - 0.414 * d + 0.012
            s1 = math.sqrt(max(rim * rim - off * off, 0.0))
            if s1 - s0 < 0.05:
                continue
            half = 0.011 if j == 0 else 0.008
            pts = [(nx * (off + sgn * half) + tx * s, y1 + 0.002, nz * (off + sgn * half) + tz * s) for s, sgn in ((s0, -1), (s1, -1), (s1, 1), (s0, 1))]
            # The half of the stone he has not come to yet is worn smooth: its furrows faint.
            faint = 0.55 if (nx * (off) + tx * (s0 + s1) * 0.5) > 0.12 else 1.0
            hard.poly(pts, GRIT, rgba(GRITSTONE, lerp(1.0, 0.36, faint)), facing=(0, 1, 0))
    # His bill left on the stone, and the rynd beside the eye.
    b = props.Placed(hard, (-0.36, y1 + 0.002, -0.2), 0.7)
    beam(b, (-0.16, 0.022, 0.0), (0.12, 0.022, 0.0), 0.034, 0.034, tone(OAK))
    beam(b, (0.09, 0.022, -0.085), (0.09, 0.022, 0.0), 0.022, 0.03, IRON_C, IRON, end_shade=1.0, taper=0.2, ends="b")
    beam(b, (0.09, 0.022, 0.085), (0.09, 0.022, 0.0), 0.022, 0.03, IRON_C, IRON, end_shade=1.0, taper=0.2, ends="b")
    ry = props.Placed(hard, (0.2, y1 + 0.002, 0.34), -0.5)
    for sx in (-1, 1):
        beam(ry, (sx * 0.035, 0.012, 0.0), (sx * 0.2, 0.012, 0.0), 0.05, 0.024, RUST_C, IRON, end_shade=1.0)
    for sz in (-1, 1):
        beam(ry, (-0.04, 0.012, sz * 0.035), (0.04, 0.012, sz * 0.035), 0.022, 0.024, RUST_C, IRON, end_shade=1.0)
    # Meal: dust on the stone, in a ring on the floor where it has been swept from, and the grit he has cut.
    dust(hard, (0, y1, 0), eye + 0.02, 0.45, 0.3, seed=1.0)
    dust(hard, (0, 0.0, 0), 0.67, 1.0, 0.4, seed=2.0)
    for _ in range(40):
        a, rr = random.uniform(2.6, 5.2), random.uniform(0.15, 0.6)
        x, z = math.cos(a) * rr, math.sin(a) * rr
        bb = random.uniform(0.0, TAU)
        hard.poly([(x + math.cos(bb) * 0.008, y1 + 0.003, z + math.sin(bb) * 0.008), (x + math.cos(bb + 2.1) * 0.006, y1 + 0.006, z + math.sin(bb + 2.1) * 0.006),
                   (x + math.cos(bb + 4.2) * 0.007, y1 + 0.003, z + math.sin(bb + 4.2) * 0.007)], GRIT, rgba(GRITSTONE, random.uniform(1.0, 1.5)), facing=(0, 1, 0))


# ---------------------------------------------------------------- oven

def arch_pts(half, spring, crown, n=8):
    """A segmental arch from (-half, spring) over (0, crown) to (half, spring), as (x, y)."""
    rise = crown - spring
    rad = (half * half + rise * rise) / (2.0 * rise)
    a = math.asin(min(half / rad, 1.0))
    return [(rad * math.sin(lerp(-a, a, i / n)), crown - rad + rad * math.cos(lerp(-a, a, i / n))) for i in range(n + 1)]


def ash_bed(m, x0, x1, z0, z1, y, h, seed=0.0, colour=ASH, nu=9, nv=9, heap=None, edge=0.12):
    """Ash lying over a floor, deeper in drifts; `heap` (x, z, r, h) is a
    place it has been raked up."""
    def f(u, v):
        x, z = lerp(x0, x1, u), lerp(z0, z1, v)
        e = min(smoothstep(0.0, edge, u) * smoothstep(0.0, edge, 1.0 - u), 1.0) * min(smoothstep(0.0, edge, v) * smoothstep(0.0, edge, 1.0 - v), 1.0)
        yy = h * e * (0.55 + 0.45 * fbm(x, z, 3.0, 3, seed))
        if heap:
            yy += heap[3] * math.exp(-((x - heap[0]) ** 2 + (z - heap[1]) ** 2) / (heap[2] ** 2))
        return (x, y + 0.002 + max(yy, 0.0), z)

    def c(u, v):
        x, z = lerp(x0, x1, u), lerp(z0, z1, v)
        k = 0.75 + 0.5 * fbm(x, z, 5.0, 3, seed + 3.0)
        dark = smoothstep(0.1, 0.5, fbm(x, z, 2.2, 2, seed + 7.0))
        return rgba((lerp(colour[0], CHAR[0] * 2.0, dark), lerp(colour[1], CHAR[1] * 2.0, dark), lerp(colour[2], CHAR[2] * 2.0, dark)), k)

    props.sheet(m, f, nu, nv, GRIT, c, flip=True)


def cinders(m, x0, x1, z0, z1, y, count, seed=0, size=0.02):
    """Bits of charcoal lying about."""
    rng = random.Random(seed)
    for _ in range(count):
        x, z = rng.uniform(x0, x1), rng.uniform(z0, z1)
        s, a = rng.uniform(0.4, 1.0) * size, rng.uniform(0.0, TAU)
        top = (x + rng.uniform(-s, s) * 0.3, y + s * 0.8, z + rng.uniform(-s, s) * 0.3)
        base = [(x + math.cos(a + TAU * i / 3) * s, y + 0.002, z + math.sin(a + TAU * i / 3) * s) for i in range(3)]
        k = rng.uniform(0.6, 2.2)
        for i in range(3):
            q0, q1 = base[i], base[(i + 1) % 3]
            m.poly([q0, q1, top], GRIT, rgba(CHAR, k * (1.0 + 0.5 * i)), facing=((q0[0] + q1[0]) * 0.5 - x, 0.6, (q0[2] + q1[2]) * 0.5 - z))


def oven(p):
    hard, soft = p.hard, p.soft
    X, Z, TOP = 1.2, 1.15, 2.35           # the box
    CX, CZ, FLOOR, CEIL = 0.8, 0.85, 0.6, 1.95   # the chamber
    MW, SPRING, CROWN = 0.4, 1.06, 1.3      # the mouth
    arch = arch_pts(MW, SPRING, CROWN, 8)

    def stone(x, y, z, k=1.0, soot=0.0):
        """Rubble's tone at a point: uneven, dark at the foot, black where the smoke goes."""
        v = (0.56 + 0.09 * fbm(x + z, y, 1.7, 2, 4.0)) * k * (0.72 + 0.28 * smoothstep(0.0, 0.5, y))
        v *= 1.0 - soot
        return (v, v * 0.98, v * 0.94, 1.0)

    def smoke(x, y):
        """How black the front is at (x, y): a plume up from the mouth."""
        if y < SPRING:
            return 0.0
        up = (y - SPRING) / (TOP - SPRING)
        return 0.94 * max(0.0, 1.0 - (abs(x) / (0.62 + 0.5 * up)) ** 2) * (1.0 - 0.4 * up)

    def wall(pts, facing, k=1.0, sooty=False, mat=RUBBLE):
        hard.poly(pts, mat, [stone(q[0], q[1], q[2], k, smoke(q[0], q[1]) if sooty else 0.0) for q in pts], facing=facing)

    # --- Outside. The front, round the mouth: below the sill, the two sides of the mouth, and above the arch in strips.
    zf = -Z
    xs = [-X, -0.8, -MW]
    for xa, xb in zip(xs, xs[1:]):
        for ya, yb in ((0.0, FLOOR), (FLOOR, SPRING), (SPRING, 1.7), (1.7, TOP)):
            for sx in (-1, 1):
                wall([(sx * xa, ya, zf), (sx * xb, ya, zf), (sx * xb, yb, zf), (sx * xa, yb, zf)], (0, 0, -1), sooty=True)
    wall([(-MW, 0.0, zf), (MW, 0.0, zf), (MW, FLOOR, zf), (-MW, FLOOR, zf)], (0, 0, -1))
    for (xa, ya), (xb, yb) in zip(arch, arch[1:]):
        wall([(xa, ya, zf), (xb, yb, zf), (xb, 1.7, zf), (xa, 1.7, zf)], (0, 0, -1), sooty=True)
        wall([(xa, 1.7, zf), (xb, 1.7, zf), (xb, TOP, zf), (xa, TOP, zf)], (0, 0, -1), sooty=True)
    # The sides, the back and the top.
    for sx in (-1, 1):
        for za, zb in ((-Z, 0.0), (0.0, Z)):
            for ya, yb in ((0.0, 0.7), (0.7, TOP)):
                wall([(sx * X, ya, za), (sx * X, ya, zb), (sx * X, yb, zb), (sx * X, yb, za)], (sx, 0, 0))
    wall([(-X, 0.0, Z), (X, 0.0, Z), (X, TOP, Z), (-X, TOP, Z)], (0, 0, 1), 0.8)
    wall([(-X, TOP, -Z), (X, TOP, -Z), (X, TOP, Z), (-X, TOP, Z)], (0, 1, 0), 0.7)
    # The flue: drawn in from the oven's back to the stack in the wall. (All above his head.)
    f0, f1 = [(-0.95, TOP, 0.15), (0.95, TOP, 0.15), (0.95, TOP, 1.13), (-0.95, TOP, 1.13)], [(-0.6, 3.97, 0.72), (0.6, 3.97, 0.72), (0.6, 3.97, 1.13), (-0.6, 3.97, 1.13)]
    for i, facing in ((0, (0, 0.4, -1)), (1, (1, 0.3, 0)), (3, (-1, 0.3, 0))):
        j = (i + 1) % 4
        hard.poly([f0[i], f0[j], f1[j], f1[i]], RUBBLE, [stone(q[0], q[1], q[2], 0.8, 0.35 if q[1] > 3.0 else 0.15) for q in (f0[i], f0[j], f1[j], f1[i])], facing=facing)
    # A plinth course round its foot, and a capping course: each a hand proud.
    for ya, yb, out in ((0.0, 0.16, 0.035), (TOP - 0.14, TOP, 0.03)):
        for sx in (-1, 1):
            hard.box((sx * X - (0.0 if sx > 0 else out), ya, -Z - out), (sx * X + (out if sx > 0 else 0.0), yb, Z), RUBBLE, stone(sx, 1.0, 0.0, 0.85), faces="xXyY" + "z")
        hard.box((-X, ya, -Z - out), (X, yb, -Z), RUBBLE, stone(0.3, 1.0, zf, 0.85, 0.55 if ya > 1.0 else 0.0), faces="yYz")
    # The mouth's dressed stones: jambs, an arch of voussoirs, the sill. They stand a finger proud of the rubble.
    zr = zf - 0.014
    ring = 0.17
    for sx in (-1, 1):
        for ya, yb in ((FLOOR, 0.84), (0.84, SPRING)):
            c = stone(sx, ya, zf, random.uniform(0.92, 1.1), 0.3 + 0.3 * (ya > 0.8))
            c = (c[0], c[1], c[2], 1.0)
            x0, x1 = sx * MW, sx * (MW + ring + random.uniform(-0.02, 0.03))
            hard.poly([(x0, ya + 0.004, zr), (x1, ya + 0.004, zr), (x1, yb - 0.004, zr), (x0, yb - 0.004, zr)], ASHLAR, c, facing=(0, 0, -1))
            hard.poly([(x1, ya + 0.004, zr), (x1, yb - 0.004, zr), (x1, yb - 0.004, zf), (x1, ya + 0.004, zf)], ASHLAR, rgba(c, 0.7), facing=(sx, 0, 0))
    cy = CROWN - (MW * MW + (CROWN - SPRING) ** 2) / (2.0 * (CROWN - SPRING))
    for i, ((xa, ya), (xb, yb)) in enumerate(zip(arch, arch[1:])):
        def outer(x, y, k=ring):
            d = math.hypot(x, y - cy)
            return (x + x / d * k, y + (y - cy) / d * k)
        (oxa, oya), (oxb, oyb) = outer(xa, ya), outer(xb, yb)
        sooted = 0.5 + 0.42 * (1.0 - abs(i - 3.5) / 4.0)
        c = stone(xa, ya, zf, random.uniform(0.92, 1.1), sooted)
        hard.poly([(xa * 0.995, ya, zr), (xb * 0.995, yb, zr), (oxb, oyb, zr), (oxa, oya, zr)], ASHLAR, c, facing=(0, 0, -1))
        hard.poly([(oxa, oya, zr), (oxb, oyb, zr), (oxb, oyb, zf), (oxa, oya, zf)], ASHLAR, rgba(c, 0.7), facing=(oxa + oxb, oya + oyb - 2 * cy, 0))
    hard.box((-MW - ring - 0.03, FLOOR - 0.09, zf - 0.05), (MW + ring + 0.03, FLOOR, zf), ASHLAR, stone(0.2, 0.5, zf, 1.05), faces="xXyYz")
    # --- The way in, through the wall's thickness: black with smoke.
    zi = -CZ

    def lining(x, y, z, k=1.0):
        """The inside's tone: sooted stone, blacker the higher and the farther in."""
        deep = smoothstep(-Z, 0.3, z)
        v = (0.2 - 0.13 * deep) * (0.85 + 0.25 * fbm(x * 2.0 + z, y * 2.0, 1.0, 2, 9.0)) * (1.0 - 0.6 * smoothstep(FLOOR, CEIL, y)) * k
        return (v, v * 0.96, v * 0.9, 1.0)

    def inner(pts, facing, k=1.0):
        hard.poly(pts, ASHLAR, [lining(q[0], q[1], q[2], k) for q in pts], facing=facing)

    for sx in (-1, 1):
        inner([(sx * MW, FLOOR, zr), (sx * MW, FLOOR, zi), (sx * MW, SPRING, zi), (sx * MW, SPRING, zr)], (-sx, 0, 0), 1.2)
    for (xa, ya), (xb, yb) in zip(arch, arch[1:]):
        inner([(xa, ya, zr), (xb, yb, zr), (xb, yb, zi), (xa, ya, zi)], (-(xa + xb), cy * 2 - ya - yb, 0), 0.9)
    # --- The chamber he crawls into: a floor, four walls and a barrel vault, all of it seen from inside.
    hard.poly([(-CX, FLOOR, -CZ), (CX, FLOOR, -CZ), (CX, FLOOR, CZ), (-CX, FLOOR, CZ)], ASHLAR, lining(0, FLOOR, 0.0, 1.3), facing=(0, 1, 0))
    hard.poly([(-MW, FLOOR, zf - 0.05), (MW, FLOOR, zf - 0.05), (MW, FLOOR, -CZ), (-MW, FLOOR, -CZ)], ASHLAR, stone(0, 1.0, zf, 0.6), facing=(0, 1, 0))
    for sx in (-1, 1):
        for za, zb in ((-CZ, 0.0), (0.0, CZ)):
            inner([(sx * CX, FLOOR, za), (sx * CX, FLOOR, zb), (sx * CX, CROWN, zb), (sx * CX, CROWN, za)], (-sx, 0, 0))
        # The front wall beside the mouth.
        inner([(sx * MW, FLOOR, zi), (sx * CX, FLOOR, zi), (sx * CX, CROWN, zi), (sx * MW, CROWN, zi)], (0, 0, 1), 1.15)
    for (xa, ya), (xb, yb) in zip(arch, arch[1:]):
        if yb < CROWN - 1e-4 or ya < CROWN - 1e-4:
            inner([(xa, ya, zi), (xb, yb, zi), (xb, CROWN, zi), (xa, CROWN, zi)], (0, 0, 1), 1.15)
    inner([(-CX, FLOOR, CZ), (CX, FLOOR, CZ), (CX, CROWN, CZ), (-CX, CROWN, CZ)], (0, 0, -1), 0.9)
    n = 8
    vault = [(-CX * math.cos(math.pi * i / n), CROWN + (CEIL - 0.03 - CROWN) * math.sin(math.pi * i / n)) for i in range(n + 1)]
    for (xa, ya), (xb, yb) in zip(vault, vault[1:]):
        for za, zb in ((-CZ, 0.0), (0.0, CZ)):
            inner([(xa, ya, za), (xb, yb, za), (xb, yb, zb), (xa, ya, zb)], (-(xa + xb), -1.0, 0), 0.8)
    for z, way, k in ((-CZ, 1, 1.0), (CZ, -1, 0.8)):
        hard.poly([(x, y, z) for x, y in vault], ASHLAR, [lining(x, y, z, k) for x, y in vault], facing=(0, 0, way))
    # --- Ash: over the chamber's floor, raked toward the mouth, out over the sill and down on the floor in front.
    ash_bed(soft, -CX - 0.02, CX + 0.02, -CZ - 0.02, CZ + 0.02, FLOOR, 0.035, seed=2.0, heap=(0.35, -0.45, 0.25, 0.05), edge=0.04)
    ash_bed(soft, -MW + 0.03, MW - 0.03, zf - 0.04, -CZ + 0.1, FLOOR, 0.02, seed=3.0, nu=4, nv=3, edge=0.3)
    cinders(hard, -0.7, 0.7, -0.7, 0.75, FLOOR + 0.02, 26, seed=4)
    spill(soft, (0.08, 0.0, zf - 0.02), 0.5, 0.36, 0.045, colour=ASH, seed=5.0, against=True, stray=0)
    cinders(hard, -0.5, 0.6, zf - 0.42, zf - 0.06, 0.012, 14, seed=6, size=0.014)
    # --- Soot: the plume above the mouth, laid over the stones as well.
    dress.soot(hard, (0.0, SPRING + 0.02, zr), (0, -1), 1.9, 1.28, 1.0)
    dress.soot(hard, (0.05, CROWN - 0.05, zr - 0.002), (0, -1), 1.0, 1.0, 1.0)
    # --- The iron doors: two leaves on pintles, swung back flat against the front. One has dropped off its top pintle.
    for sx, drop in ((-1, 0.0), (1, 0.085)):
        hx, w, zd = sx * (MW + 0.035), 0.4, zr - 0.012
        c0 = math.cos(drop * sx)
        s0 = math.sin(drop * sx)

        def at(x, y, z, hx=hx, c0=c0, s0=s0, sx=sx):
            # About the lower pintle, in the wall's plane.
            dx, dy = x, y - (FLOOR + 0.12)
            return (hx + dx * c0 - dy * s0, FLOOR + 0.12 + dx * s0 + dy * c0, z)

        top = [(sx * w * i / 4.0, SPRING + (CROWN - SPRING) * (1.0 - (1.0 - i / 4.0) ** 2) ** 0.5) for i in range(5)]
        outline = [(0.0, FLOOR + 0.03), (sx * w, FLOOR + 0.03)] + list(reversed(top))
        rust = [rgba(RUST_C, 0.8 + 0.3 * fbm(x * 5.0, y * 5.0, 1.0, 2, 3.0 + sx)) for x, y in outline]
        hard.poly([at(x, y, zd) for x, y in outline], IRON, rust, facing=(0, 0, -1))
        hard.poly([at(x, y, zd + 0.01) for x, y in outline], IRON, rgba(RUST_C, 0.5), facing=(0, 0, 1))
        for y in (FLOOR + 0.12, SPRING - 0.02):
            a, b = at(-sx * 0.03, y, zd), at(sx * (w - 0.04), y, zd)
            props.strap(hard, a, b, (0, 0, -1), width=0.04, thick=0.006, nails=4, colour=rgba(RUST_C, 0.75))
        props.ring(hard, at(sx * (w - 0.07), 0.86, zd - 0.012), (0, 0, -1), r=0.035, thick=0.005, colour=IRON_C)
        # The pintles in the jamb.
        for y, held in ((FLOOR + 0.12, True), (SPRING - 0.02, not drop)):
            hard.box((hx - 0.014, y - 0.03, zr - 0.03), (hx + 0.014, y + 0.03, zr), IRON, rgba(RUST_C, 0.7))
    dress.run(hard, (MW + 0.06, SPRING - 0.05, zr), (0, -1), 0.14, 0.5, dress.RUST, 0.55, 1.0)
    # --- The peel, stood blade up against the front.
    pole = tone(PINE, 0.08)
    beam(hard, (-1.04, 0.0, zf - 0.032), (-0.99, 1.62, zf - 0.02), 0.032, 0.03, pole)
    blade = props.Placed(hard, (-0.985, 1.6, zf - 0.016), 0.0)
    props.slab(blade, [(-0.13, 0.0), (0.12, -0.01), (0.14, 0.33), (0.1, 0.4), (-0.09, 0.41), (-0.14, 0.34)], "z", -0.012, 0.0, rgba(pole, 0.8))
    # A web in the corner the peel leaves alone.
    dress.cobweb(hard, (-X - 0.03, TOP - 0.14, zf - 0.03), (0, -1, 0), (1, 0, 0), 0.45, 7)


# ---------------------------------------------------------------- bones

def long_bone(m, a, b, r=0.013, colour=BONE, char=0.5, seed=0.0, broken=False):
    """A limb bone from `a` to `b`, knobbed at its ends, burnt black in places."""
    prof = [(0.0, 1.5), (0.035, 1.95), (0.1, 1.5), (0.2, 1.05), (0.5, 0.95), (0.82, 1.1), (0.93, 1.7), (0.985, 1.6), (1.0, 1.0)]
    if broken:
        prof = prof[:5] + [(0.62, 1.0), (0.64, 0.5)]
    pts, cols = [], []
    for t, _k in prof:
        q = tuple(a[i] + (b[i] - a[i]) * t for i in range(3))
        pts.append(q)
        burnt = smoothstep(-0.25, 0.3, fbm(q[0] * 15.0, q[2] * 15.0, 1.0, 2, seed) + char - 0.5)
        k = lerp(0.8, 0.09, burnt)
        cols.append((colour[0] * k, lerp(colour[1], colour[0], burnt) * k, lerp(colour[2], colour[0], burnt) * k, 1.0))
    m.tube(pts, [r * k for _t, k in prof], 6, PAINT, cols, caps=True, squash=(1.0, 0.85))


def rib(m, at, yaw, span=0.2, rise=0.06, colour=BONE, seed=0.0):
    """A rib lying on its side: a thin curve."""
    r = props.Placed(m, at, yaw)
    pts = [(span * (i / 6.0 - 0.5), 0.006 + 0.004 * math.sin(i * 1.3 + seed), rise * math.sin(math.pi * i / 6.0) ** 0.8) for i in range(7)]
    cols = [rgba(colour, lerp(0.25, 0.9, 0.5 + 0.5 * fbm(i * 0.7, seed, 1.0, 2, seed))) for i in range(7)]
    r.tube(pts, [0.004, 0.006, 0.0065, 0.0065, 0.006, 0.005, 0.003], 4, PAINT, cols, caps=True, squash=(1.0, 0.6))


def skull(hard, soft, at, yaw=0.0, tilt=0.0, scale=1.0, colour=BONE, jaw=False, char=0.0, seed=0.0):
    """A skull standing on `at` (under the middle of its braincase), looking
    along +z turned by `yaw`, tipped back by `tilt`: a round braincase, a
    brow, deep sockets, the nose's hole, cheekbones, the upper teeth.
    `hard` and `soft` are the flat-shaded and the smooth mesh. `tilt` below
    zero tips its face up. `char` blackens its crown (0..1)."""
    s = props.Placed(soft, at, yaw, scale, tilt)
    h = props.Placed(hard, at, yaw, scale, tilt)

    def bone(k=1.0, y=0.0, z=0.0):
        burnt = char * min(max(0.3 + 0.4 * fbm(z * 14.0, y * 14.0, 1.0, 2, seed) + (y - 0.05) * 7.0, 0.0), 1.0)
        k *= lerp(1.0, 0.1, burnt)
        return (colour[0] * k, colour[1] * k, colour[2] * k, 1.0)

    # The braincase.
    spine = [(-0.094, 0.086, 0.016), (-0.088, 0.09, 0.046), (-0.058, 0.099, 0.066), (-0.012, 0.106, 0.074), (0.032, 0.103, 0.069), (0.062, 0.096, 0.055), (0.078, 0.09, 0.036)]
    s.tube([(0.0, y, z) for z, y, _r in spine], [r for _z, _y, r in spine], 9, PAINT, [bone(1.0 - 0.25 * (i == 0), y, z) for i, (z, y, _r) in enumerate(spine)], caps=True, squash=(0.95, 1.0))
    # Behind the face: the dark of the sockets and the nose.
    dark = (0.006, 0.005, 0.004, 1.0)
    h.poly([(-0.05, 0.022, 0.063), (0.05, 0.022, 0.063), (0.054, 0.09, 0.062), (-0.054, 0.09, 0.062)], PAINT, dark, facing=(0, 0, 1))
    z0, z1 = 0.05, 0.079
    # The brow, the bridge of the nose, the cheekbones, the upper jaw with the nose's hole cut in it.
    props.slab(h, [(-0.057, 0.08), (0.057, 0.08), (0.05, 0.1), (-0.05, 0.1)], "z", z0, z1 - 0.003, bone(1.0, 0.09, 0.07), mat=PAINT, edge_shade=0.55)
    props.slab(h, [(-0.007, 0.052), (0.007, 0.052), (0.009, 0.082), (-0.009, 0.082)], "z", z0, z1, bone(1.0, 0.07, 0.07), mat=PAINT, edge_shade=0.55)
    for sx in (-1, 1):
        props.slab(h, [(sx * 0.043, 0.036), (sx * 0.06, 0.046), (sx * 0.061, 0.082), (sx * 0.05, 0.082), (sx * 0.046, 0.058)], "z", z0 - 0.01, z1 - 0.006, bone(0.95, 0.06, 0.07), mat=PAINT, edge_shade=0.55)
        # The arch back to the ear.
        beam(h, (sx * 0.058, 0.05, z0), (sx * 0.064, 0.056, -0.012), 0.006, 0.012, bone(0.8, 0.05, 0.0), mat=PAINT, ends="")
    props.slab(h, [(-0.046, 0.052), (-0.011, 0.056), (-0.016, 0.03), (0.0, 0.026), (0.016, 0.03), (0.011, 0.056), (0.046, 0.052), (0.034, 0.012), (-0.034, 0.012)], "z", z0 - 0.012, z1 + 0.004,
               bone(1.0, 0.03, 0.07), mat=PAINT, edge_shade=0.55)
    # The teeth, some gone.
    for i in range(8):
        if i in (2, 6):
            continue
        x = -0.031 + i * 0.0089
        h.box((x - 0.0036, 0.0, z1 - 0.004), (x + 0.0036, 0.013, z1 + 0.003), PAINT, bone(1.15, 0.0, 0.07), faces="xXyZ")
    # Under the braincase, and the jaw if it still has one.
    props.slab(h, [(-0.034, 0.012), (0.034, 0.012), (0.04, 0.03), (-0.04, 0.03)], "z", -0.03, z0 - 0.012, bone(0.6, 0.02, 0.0), mat=PAINT, edge_shade=0.8)
    if jaw:
        props.slab(h, [(-0.036, -0.03), (0.036, -0.03), (0.04, -0.004), (-0.04, -0.004)], "z", 0.045, z1 + 0.002, bone(0.95, 0.0, 0.07), mat=PAINT, edge_shade=0.6)
        for sx in (-1, 1):
            props.slab(h, [(-0.02, -0.03), (0.07, -0.03), (0.075, -0.012), (0.01, 0.0), (-0.012, 0.04), (-0.03, 0.04)], "x", sx * 0.046 - 0.004, sx * 0.046 + 0.004, bone(0.9, 0.0, 0.0), mat=PAINT,
                       edge_shade=0.7)


def oven_bones(p):
    hard, soft = p.hard, p.soft
    y = 0.6
    # Deeper ash where they lie, and the charcoal of what burnt with them.
    ash_bed(soft, -0.74, 0.7, -0.6, 0.8, y + 0.012, 0.05, seed=11.0, nu=8, nv=8, edge=0.45, heap=(-0.2, 0.25, 0.3, 0.04))
    cinders(hard, -0.6, 0.55, -0.4, 0.7, y + 0.035, 30, seed=12, size=0.024)
    # The long bones, half in the ash: thighs and shins of more than one man.
    for i, (a, b, r, char, broken) in enumerate((
            ((-0.52, 0.045, 0.3), (-0.3, 0.06, 0.66), 0.014, 0.55, False),
            ((-0.34, 0.05, -0.16), (0.06, 0.07, 0.04), 0.0135, 0.7, False),
            ((0.04, 0.045, -0.3), (0.42, 0.065, -0.2), 0.012, 0.65, False),
            ((0.22, 0.05, 0.42), (0.52, 0.04, 0.1), 0.012, 0.7, True),
            ((-0.48, 0.045, -0.24), (-0.18, 0.055, -0.36), 0.0105, 0.45, False),
            ((0.0, 0.05, 0.62), (0.26, 0.05, 0.7), 0.01, 0.8, True))):
        long_bone(soft, (a[0], y + a[1], a[2]), (b[0], y + b[1], b[2]), r, char=char, seed=20.0 + i, broken=broken)
    # Ribs, and the small bones of hands and feet.
    for i, (x, z, yaw) in enumerate(((0.3, 0.02, 0.4), (0.36, 0.07, 0.6), (0.27, 0.13, 0.2), (-0.4, 0.08, 1.9), (-0.12, 0.5, 2.7))):
        rib(soft, (x, y + 0.045, z), yaw, random.uniform(0.17, 0.22), random.uniform(0.04, 0.07), seed=30.0 + i)
    for i in range(9):
        x, z, a = random.uniform(-0.45, 0.5), random.uniform(-0.35, 0.6), random.uniform(0.0, TAU)
        long = random.uniform(0.025, 0.06)
        soft.tube([(x, y + 0.046, z), (x + math.cos(a) * long, y + 0.05, z + math.sin(a) * long)], [0.007, 0.0055], 5, PAINT, rgba(BONE, random.uniform(0.15, 0.6)), caps=True)
    # A skull on its side by the wall, sunk to the cheek, its crown burnt black; and the top of another, face down.
    skull(hard, soft, (-0.2, y - 0.004, 0.22), yaw=math.pi + 0.45, tilt=-0.42, colour=rgba(BONE, 0.8), char=0.9, seed=3.0)
    cap = props.Placed(soft, (0.47, y + 0.005, 0.5), 2.1, 1.0, -0.4)
    cap.tube([(0.0, 0.0, -0.085), (0.0, 0.02, -0.08), (0.0, 0.05, -0.04), (0.0, 0.058, 0.01), (0.0, 0.045, 0.05), (0.0, 0.02, 0.07)], [0.02, 0.05, 0.068, 0.07, 0.058, 0.03], 8, PAINT,
             [rgba(BONE, k) for k in (0.1, 0.14, 0.3, 0.45, 0.2, 0.1)], caps=True, squash=(0.95, 0.75))


# ---------------------------------------------------------------- mill wheel

def mill_wheel(p):
    """Its axle runs along y (the scene lays it over, across the race: y 0
    is the mill's wall, +z is down into the race, x along the race)."""
    hard = p.hard
    R, RIN, Y0, Y1 = 1.57, 1.33, 0.14, 2.86

    def P(a, r, y):
        return (math.sin(a) * r, y, math.cos(a) * r)

    def wet(q, base=OAK_DARK, k=1.0):
        """Old oak that stands in a race: black with wet, green with weed, worse the lower it hangs."""
        low = smoothstep(-1.2, 1.6, q[2])
        green = smoothstep(-0.25, 0.35, fbm(q[0] * 1.7 + q[1], q[2] * 1.7, 1.0, 3, 5.0) + 0.35 * low - 0.1)
        v = lerp(0.58, 0.3, low) * random.uniform(0.85, 1.1) * k
        return (lerp(base[0], 0.27, green) * v, lerp(base[1], 0.44, green) * v, lerp(base[2], 0.2, green) * v, 1.0)

    # The axle: an oak trunk hewn to eight sides, iron-bound at its ends, a gudgeon in each.
    hard.tube([(0, -0.22, 0), (0, 1.5, 0), (0, 3.16, 0)], [0.19, 0.2, 0.19], 8, WOOD, [wet((0.3, 0.0, -0.3), k=0.9), wet((0.0, 1.5, 0.0), k=0.9), wet((0.3, 3.0, 0.3), k=0.9)], caps=True)
    for y in (0.045, 2.99):
        hard.tube([(0, y, 0), (0, y + 0.07, 0)], [0.206, 0.206], 8, IRON, rgba(RUST_C, 0.7))
    hard.tube([(0, 3.16, 0), (0, 3.24, 0)], [0.045, 0.04], 6, IRON, rgba(RUST_C, 0.6), caps=True)
    n = 16
    for yr in (Y0 + 0.11, Y1 - 0.11):
        ya, yb = yr - 0.05, yr + 0.05
        # The rim, in felloes.
        for i in range(n):
            a0, a1 = TAU * (i + 0.5) / n + 0.006, TAU * (i + 1.5) / n - 0.006
            am = (a0 + a1) * 0.5
            c = wet(P(am, R, yr))
            arc, u0 = (a1 - a0) * R * props.GRAIN, random.random()
            out = (math.sin(am), 0.0, math.cos(am))
            hard.poly([P(a0, R, ya), P(a1, R, ya), P(a1, R, yb), P(a0, R, yb)], WOOD, c, uvs=[(u0, 0), (u0, arc), (u0 + 0.08, arc), (u0 + 0.08, 0)], facing=out)
            hard.poly([P(a0, RIN, ya), P(a1, RIN, ya), P(a1, RIN, yb), P(a0, RIN, yb)], WOOD, rgba(c, 0.8), uvs=[(u0, 0), (u0, arc), (u0 + 0.08, arc), (u0 + 0.08, 0)],
                      facing=(-out[0], 0.0, -out[2]))
            for y, way in ((ya, -1), (yb, 1)):
                hard.poly([P(a0, RIN, y), P(a1, RIN, y), P(a1, R, y), P(a0, R, y)], WOOD, rgba(c, 0.92), uvs=[(u0, 0), (u0, arc), (u0 + 0.19, arc), (u0 + 0.19, 0)], facing=(0, way, 0))
            for a, way in ((a0, -1), (a1, 1)):
                hard.poly([P(a, RIN, ya), P(a, R, ya), P(a, R, yb), P(a, RIN, yb)], WOOD, rgba(c, 0.5), facing=(way * math.cos(a), 0.0, -way * math.sin(a)))
        # Six arms let into the axle.
        for j in range(6):
            a = TAU * j / 6 + 0.26
            beam(hard, P(a, 0.16, yr), P(a, RIN + 0.02, yr), 0.11, 0.085, wet(P(a, 0.8, yr)), up=(0, 1, 0), ends="")
    # The floats: sixteen boards between the rims. The one that hangs lowest has broken away, all but its ends.
    rm, deep = (R + 1.19) * 0.5, R - 1.19
    for i in range(n):
        a = TAU * i / n
        tang = (math.cos(a), 0.0, -math.sin(a))
        if i == 0:
            beam(hard, P(a, rm + deep * 0.25, Y0), P(a, rm + deep * 0.25, Y0 + 0.62), deep * 0.5, 0.034, wet(P(a, rm, Y0)), up=tang)
            beam(hard, P(a, rm - deep * 0.25, Y0), P(a, rm - deep * 0.25, Y0 + 0.38), deep * 0.5, 0.034, wet(P(a, rm, Y0)), up=tang)
            beam(hard, P(a, rm - deep * 0.1, Y1 - 0.3), P(a, rm - deep * 0.1, Y1), deep * 0.8, 0.034, wet(P(a, rm, Y1)), up=tang)
            continue
        slip = random.uniform(-0.02, 0.02)
        beam(hard, P(a, rm, Y0 + slip), P(a, rm, Y1 + slip), deep, 0.034, wet(P(a, rm, 1.5)), up=tang)
    # Weed hanging from what stays wet.
    for _ in range(26):
        i = random.choice((1, 2, 3, 15, 14, 13, 4, 12))
        a = TAU * i / n
        y = random.uniform(Y0 + 0.1, Y1 - 0.1)
        q = P(a, random.uniform(1.25, R), y)
        long, w = random.uniform(0.08, 0.3), random.uniform(0.012, 0.03)
        g = rgba((0.028, 0.045, 0.02), random.uniform(0.6, 1.2))
        pts = [(q[0], q[1] - w, q[2]), (q[0], q[1] + w, q[2]), (q[0] + random.uniform(-0.03, 0.03), q[1] + random.uniform(-0.02, 0.02), q[2] + long)]
        hard.poly(pts, PAINT, g, facing=(1, 0, 0))
        hard.poly(pts, PAINT, g, facing=(-1, 0, 0))
    # Its outer bearing: an oak block on a stone pier standing in the race against the far wall.
    plank(hard, (-0.3, 2.9, 0.1), (0.3, 3.19, 0.31), wet((0.0, 3.0, 0.2), k=0.9), along="x")
    for za, zb in ((0.31, 1.0), (1.0, 1.6), (1.6, 2.2)):
        low = (0.42, 0.43, 0.4, 0.25 if za > 0.9 else 0.6)
        hard.box((-0.36, 2.88, za), (0.36, 3.2, zb), RUBBLE, low, faces="xXy" + ("z" if za < 0.4 else ""))


# ---------------------------------------------------------------- hearths

def firedog(hard, x, y, z_front, z_back, tall=0.5):
    """An andiron: a bar the logs lie on, a tall front on two feet."""
    c = rgba(RUST_C, 0.55)
    beam(hard, (x, y + 0.17, z_front), (x, y + 0.14, z_back), 0.03, 0.03, c, IRON, end_shade=1.0)
    beam(hard, (x, y, z_back - 0.02), (x, y + 0.15, z_back - 0.02), 0.03, 0.03, c, IRON, end_shade=1.0)
    beam(hard, (x, y + 0.1, z_front), (x, y + tall, z_front), 0.036, 0.036, c, IRON, end_shade=1.0)
    for sx in (-1, 1):
        beam(hard, (x + sx * 0.11, y, z_front), (x, y + 0.13, z_front), 0.03, 0.03, c, IRON, end_shade=1.0)
    hard.tube([(x, y + tall, z_front), (x, y + tall + 0.03, z_front), (x, y + tall + 0.065, z_front)], [0.02, 0.034, 0.012], 6, IRON, c, caps=True)


def burnt_log(m, a, b, r, seed=0.0, burnt=(0.3, 0.75)):
    """A log lying from `a` to `b`, burnt through between the fractions `burnt`."""
    n = 8
    pts, cols, radii = [], [], []
    bark = (0.3, 0.25, 0.2)
    for i in range(n):
        t = i / (n - 1.0)
        char = smoothstep(burnt[0] - 0.14, burnt[0] + 0.04, t) * (1.0 - smoothstep(burnt[1] - 0.04, burnt[1] + 0.14, t))
        k = 0.85 + 0.3 * fbm(t * 5.0, seed, 1.0, 2, seed)
        pts.append(tuple(a[j] + (b[j] - a[j]) * t for j in range(3)))
        cols.append((lerp(bark[0], 0.03, char) * k, lerp(bark[1], 0.028, char) * k, lerp(bark[2], 0.026, char) * k, 1.0))
        radii.append(r * (1.0 - 0.3 * char) * (1.0 + 0.06 * fbm(t * 7.0, seed + 2.0, 1.0, 2, seed)))
    m.tube(pts, radii, 7, WOOD, cols, caps=True)


def cauldron(hard, soft, at, r=0.24, h=0.34):
    """An iron pot with a bail, hanging: `at` is under its middle."""
    black = (0.3, 0.29, 0.28)
    props.pot(soft, at, [(0.0, r * 0.45), (h * 0.1, r * 0.8), (h * 0.4, r), (h * 0.72, r * 0.94), (h * 0.9, r * 0.78), (h * 0.95, r * 0.86), (h, r * 0.9)], colour=black, sides=12, mat=IRON)
    for i in range(3):
        a = TAU * i / 3 + 0.5
        beam(hard, (at[0] + math.cos(a) * r * 0.6, at[1] + 0.03, at[2] + math.sin(a) * r * 0.6), (at[0] + math.cos(a) * r * 0.72, at[1] - 0.08, at[2] + math.sin(a) * r * 0.72), 0.03, 0.03,
             rgba(black), IRON, end_shade=1.0, taper=0.5)
    top = at[1] + h
    arc = [(at[0] + math.cos(math.pi * i / 8) * r * 0.9, top - 0.02 + math.sin(math.pi * i / 8) * r * 0.95, at[2]) for i in range(9)]
    soft.tube(arc, [0.009] * 9, 4, IRON, rgba(black))
    return (at[0], top - 0.02 + r * 0.95, at[2])


def chain(hard, a, b, link=0.066, colour=None):
    """A chain hanging from `a` down to `b`: flat links, each turned across the last."""
    c = colour or rgba(RUST_C, 0.6)
    n = max(int((a[1] - b[1]) / (link * 0.78)), 1)
    step = (a[1] - b[1]) / n
    for i in range(n):
        y1 = a[1] - i * step
        y0 = y1 - step - link * 0.2
        x, z = lerp(a[0], b[0], (i + 0.5) / n), lerp(a[2], b[2], (i + 0.5) / n)
        w, t = 0.017, 0.0045
        if i % 2:
            w, t = t, w
        for sx in (-1, 1):
            hard.box((x + sx * w - 0.004 * (w > t), y0, z + sx * t * (t > w) - 0.004 * (t > w) - t * (w > t)), (x + sx * w + 0.004 * (w > t), y1, z + sx * t * (t > w) + 0.004 * (t > w) + t * (w > t)), IRON, c,
                     faces="xXzZ")


def hearth_stone(x, y, z, k=1.0, soot=0.0, moss=1.0):
    v = (0.5 + 0.1 * fbm(x * 1.3 + z, y * 1.3, 1.0, 2, 6.0)) * k * (1.0 - soot)
    return (v, v * 0.98, v * 0.94, moss)


def fire_bed(p, x0, x1, z0, z1, y, seed=0.0, dogs=0.4, logs=3):
    """What a fire leaves: ash, dead embers, the ends of the logs that fed
    it lying over two firedogs."""
    hard, soft = p.hard, p.soft
    cx, cz = (x0 + x1) * 0.5, (z0 + z1) * 0.5
    ash_bed(soft, x0, x1, z0, z1, y, 0.06, seed=seed, heap=(cx, cz + 0.05, min(x1 - x0, z1 - z0) * 0.3, 0.07), edge=0.2)
    cinders(hard, x0 + 0.1, x1 - 0.1, z0 + 0.1, z1 - 0.08, y + 0.04, 36, seed=int(seed) + 1, size=0.026)
    zf, zb = z0 + 0.14, z1 - 0.2
    for sx in (-1, 1):
        firedog(hard, cx + sx * dogs, y, zf, zb)
    reach = dogs + 0.16
    burnt_log(soft, (cx - reach, y + 0.24, cz - 0.02), (cx + reach * 0.9, y + 0.23, cz + 0.06), 0.07, seed + 1.0, (0.3, 0.72))
    if logs > 1:
        burnt_log(soft, (cx - reach * 0.75, y + 0.23, cz + 0.2), (cx + reach, y + 0.24, cz + 0.16), 0.06, seed + 2.0, (0.2, 0.6))
    if logs > 2:
        # One burnt through and fallen in two between the dogs.
        burnt_log(soft, (cx - reach * 0.9, y + 0.25, cz - 0.2), (cx - 0.04, y + 0.07, cz - 0.14), 0.055, seed + 3.0, (0.55, 1.2))
        burnt_log(soft, (cx + reach * 0.85, y + 0.25, cz - 0.24), (cx + 0.1, y + 0.06, cz - 0.2), 0.055, seed + 4.0, (0.5, 1.2))
    return zf


def hearth_kitchen(p):
    """The kitchen's fireplace below its hood: jambs under the range's stone
    cheeks, a fireback, a kerbed hearth. Faces -z; the wall is at z 0.68."""
    hard, soft = p.hard, p.soft
    W, IN, D, BACK, TOP = 1.2, 0.95, 0.6, 0.68, 1.0
    # The jambs: rubble, as the cheeks they carry; their inner faces black.
    for sx in (-1, 1):
        for ya, yb in ((0.0, 0.5), (0.5, TOP)):
            for za, zb in ((-D, 0.0), (0.0, BACK)):
                pts = [(sx * W, ya, za), (sx * W, ya, zb), (sx * W, yb, zb), (sx * W, yb, za)]
                hard.poly(pts, RUBBLE, [hearth_stone(q[0], q[1], q[2], 0.62, moss=0.6) for q in pts], facing=(sx, 0, 0))
                pts = [(sx * IN, ya, za), (sx * IN, ya, zb), (sx * IN, yb, zb), (sx * IN, yb, za)]
                hard.poly(pts, RUBBLE, [hearth_stone(q[0], q[1], q[2], 0.5, 0.35 + 0.5 * smoothstep(-D, 0.2, q[2]), 0.6) for q in pts], facing=(-sx, 0, 0))
            pts = [(sx * IN, ya, -D), (sx * W, ya, -D), (sx * W, yb, -D), (sx * IN, yb, -D)]
            hard.poly(pts, RUBBLE, [hearth_stone(q[0], q[1], q[2], 0.62, moss=0.6) for q in pts], facing=(0, 0, -1))
    # The fireback: the wall behind the fire, burnt black.
    for xa, xb in ((-IN, 0.0), (0.0, IN)):
        for ya, yb in ((0.0, 0.6), (0.6, 1.4), (1.4, 2.27)):
            pts = [(xa, ya, BACK - 0.012), (xb, ya, BACK - 0.012), (xb, yb, BACK - 0.012), (xa, yb, BACK - 0.012)]
            hard.poly(pts, ASHLAR, [hearth_stone(q[0], q[1], q[2], 0.5, 0.9 - 0.25 * abs(q[0]) / IN - 0.12 * q[1] / 2.27) for q in pts], facing=(0, 0, -1))
    # The hearth: a stone floor a little raised, a kerb of three stones along its front.
    y = 0.05
    hard.poly([(-IN, y, -D + 0.12), (IN, y, -D + 0.12), (IN, y, BACK), (-IN, y, BACK)], ASHLAR, hearth_stone(0.0, 0.0, 0.0, 0.3), facing=(0, 1, 0))
    for xa, xb in ((-IN, -0.34), (-0.335, 0.3), (0.305, IN)):
        h = 0.13 + random.uniform(-0.008, 0.008)
        hard.box((xa + 0.003, 0.0, -D), (xb - 0.003, h, -D + 0.15), ASHLAR, hearth_stone(xa, 0.1, -D, random.uniform(0.75, 0.9), 0.25), faces="xXYzZ")
    zf = fire_bed(p, -IN + 0.03, IN - 0.03, -D + 0.16, BACK - 0.03, y, seed=40.0, dogs=0.46)
    # The spit across the firedogs' hooks, its crank at one end.
    iron = rgba(RUST_C, 0.6)
    for sx in (-1, 1):
        beam(hard, (sx * 0.46, y + 0.4, zf), (sx * 0.46, y + 0.385, zf - 0.07), 0.02, 0.02, iron, IRON, end_shade=1.0)
        beam(hard, (sx * 0.46, y + 0.385, zf - 0.06), (sx * 0.46, y + 0.45, zf - 0.075), 0.02, 0.02, iron, IRON, end_shade=1.0)
    ys, zs = y + 0.415, zf - 0.04
    beam(hard, (-0.82, ys, zs), (0.8, ys, zs), 0.016, 0.016, iron, IRON, end_shade=1.0, taper=0.4, ends="a")
    beam(hard, (-0.82, ys, zs), (-0.82, ys - 0.13, zs + 0.03), 0.016, 0.016, iron, IRON, end_shade=1.0)
    beam(hard, (-0.82, ys - 0.13, zs + 0.03), (-0.91, ys - 0.13, zs + 0.03), 0.024, 0.024, tone(OAK_DARK), end_shade=0.8)
    # The cauldron on its chain, from a bar set across the flue.
    bar_y = 2.16
    beam(hard, (-IN, bar_y, 0.2), (IN, bar_y, 0.2), 0.03, 0.03, iron, IRON, end_shade=1.0)
    hook = cauldron(hard, soft, (0.08, 0.64, 0.2))
    beam(hard, (hook[0], hook[1] - 0.012, hook[2]), (hook[0], hook[1] + 0.09, hook[2]), 0.014, 0.014, iron, IRON, end_shade=1.0)
    beam(hard, (hook[0], hook[1] - 0.012, hook[2]), (hook[0] + 0.03, hook[1] - 0.012, hook[2]), 0.014, 0.014, iron, IRON, end_shade=1.0)
    chain(hard, (hook[0], bar_y - 0.015, hook[2]), (hook[0], hook[1] + 0.08, hook[2]))
    # A ladle hung on the jamb, and soot run down beside it.
    beam(hard, (-IN + 0.012, 0.9, -0.3), (-IN + 0.02, 0.5, -0.3), 0.014, 0.014, iron, IRON, end_shade=1.0)
    props.pot(soft, (-IN + 0.05, 0.43, -0.3), [(0.0, 0.02), (0.02, 0.04), (0.04, 0.045)], colour=(0.3, 0.29, 0.28), sides=7, mat=IRON)
    # Ash trodden out over the kerb onto the floor.
    spill(soft, (0.2, 0.0, -D - 0.01), 0.5, 0.2, 0.015, colour=ASH, seed=41.0, against=True, stray=0)


def hearth_warming(p):
    """The warming room's hearth: a low stone fireplace against the wall,
    open above. Faces -z; the wall is at z 0.58."""
    hard, soft = p.hard, p.soft
    W, IN, D, BACK = 0.8, 0.58, 0.4, 0.58
    for sx in (-1, 1):
        # The cheeks: three courses of cut stone, a chamfered cap.
        for ya, yb in ((0.0, 0.3), (0.3, 0.6), (0.6, 0.88)):
            k = random.uniform(0.85, 1.0)
            for pts, facing, soot in (
                    ([(sx * W, ya, -D), (sx * W, ya, BACK), (sx * W, yb, BACK), (sx * W, yb, -D)], (sx, 0, 0), 0.0),
                    ([(sx * IN, ya, -D), (sx * IN, ya, BACK), (sx * IN, yb, BACK), (sx * IN, yb, -D)], (-sx, 0, 0), 0.6),
                    ([(sx * IN, ya, -D), (sx * W, ya, -D), (sx * W, yb, -D), (sx * IN, yb, -D)], (0, 0, -1), 0.1)):
                hard.poly(pts, ASHLAR, [hearth_stone(q[0], q[1], q[2], k, soot * smoothstep(-D - 0.1, 0.1, q[2])) for q in pts], facing=facing)
        cap = hearth_stone(sx, 0.9, 0.0, 0.95)
        hard.box((min(sx * IN, sx * W) - 0.02, 0.88, -D - 0.02), (max(sx * IN, sx * W) + 0.02, 0.97, BACK), ASHLAR, cap, faces="xXyYz")
    # The fireback, burnt black, a stone higher than the cheeks.
    for xa, xb in ((-IN, 0.0), (0.0, IN)):
        for ya, yb in ((0.0, 0.5), (0.5, 1.02)):
            pts = [(xa, ya, BACK - 0.14), (xb, ya, BACK - 0.14), (xb, yb, BACK - 0.14), (xa, yb, BACK - 0.14)]
            hard.poly(pts, ASHLAR, [hearth_stone(q[0], q[1], q[2], 0.5, 0.85 - 0.3 * abs(q[0]) / IN) for q in pts], facing=(0, 0, -1))
    hard.poly([(-IN, 1.02, BACK - 0.14), (IN, 1.02, BACK - 0.14), (IN, 1.02, BACK), (-IN, 1.02, BACK)], ASHLAR, hearth_stone(0, 1.0, 0, 0.5, 0.5), facing=(0, 1, 0))
    y = 0.04
    hard.poly([(-IN, y, -D + 0.1), (IN, y, -D + 0.1), (IN, y, BACK - 0.14), (-IN, y, BACK - 0.14)], ASHLAR, hearth_stone(0.0, 0.0, 0.0, 0.3), facing=(0, 1, 0))
    for xa, xb in ((-IN, -0.02), (-0.015, IN)):
        hard.box((xa + 0.003, 0.0, -D), (xb - 0.003, 0.11 + random.uniform(-0.006, 0.006), -D + 0.13), ASHLAR, hearth_stone(xa, 0.1, -D, random.uniform(0.75, 0.9), 0.25), faces="xXYzZ")
    fire_bed(p, -IN + 0.02, IN - 0.02, -D + 0.14, BACK - 0.16, y, seed=50.0, dogs=0.27, logs=2)
    # A poker left leaning in the corner of it.
    beam(hard, (IN - 0.06, y + 0.02, -0.05), (IN - 0.025, 0.86, 0.25), 0.014, 0.014, rgba(RUST_C, 0.6), IRON, end_shade=1.0)
    spill(soft, (-0.15, 0.0, -D - 0.01), 0.36, 0.16, 0.012, colour=ASH, seed=51.0, against=True, stray=0)


# ---------------------------------------------------------------- latrine

def seat_hole(m, x, z, y, half, r, colour, thick=0.035, sides=8):
    """A square of seat board about (x, z), `half` each way, with a round hole through it."""
    c = colour
    u0 = random.random()
    for i in range(sides):
        a0, a1 = TAU * (i + 0.5) / sides, TAU * (i + 1.5) / sides

        def edge(a):
            k = half / max(abs(math.cos(a)), abs(math.sin(a)))
            return (x + math.cos(a) * k, z + math.sin(a) * k)

        (ax, az), (bx, bz) = edge(a0), edge(a1)
        ia, ib = (x + math.cos(a0) * r, z + math.sin(a0) * r), (x + math.cos(a1) * r, z + math.sin(a1) * r)
        pts = [(ia[0], y, ia[1]), (ib[0], y, ib[1]), (bx, y, bz), (ax, y, az)]
        m.poly(pts, WOOD, c, uvs=[(u0 + q[0] * props.GRAIN, q[2] * props.GRAIN) for q in pts], facing=(0, 1, 0))
        # The hole's worn edge, going down into the dark.
        m.poly([(ia[0], y, ia[1]), (ib[0], y, ib[1]), (ib[0], y - thick, ib[1]), (ia[0], y - thick, ia[1])], WOOD, [rgba(c, 0.6), rgba(c, 0.6), rgba(c, 0.15), rgba(c, 0.15)],
               facing=(x - (ia[0] + ib[0]) * 0.5, 0.0, z - (ia[1] + ib[1]) * 0.5))


def latrine_seat(p):
    hard, soft = p.hard, p.soft
    L, H, D = 3.0, 0.45, 0.4
    seats = (-2.4, -1.2, 0.0, 1.2, 2.4)
    hz, half, r = -0.05, 0.19, 0.14
    # The front of the bench, boarded; the seat in three runs: before the holes, the holes, behind them.
    boards(hard, (-L, 0.0, -D), (L, H - 0.035, -D + 0.03), "x", "y", 2, OAK_DARK, uneven=0.003, gap=0.006)
    for xa, xb in ((-L, -0.6), (-0.6, 0.6), (0.6, L)):
        plank(hard, (xa + 0.002, H - 0.035, -D - 0.02), (xb - 0.002, H, hz - half), tone(OAK, 0.1), along="x")
        plank(hard, (xa + 0.002, H - 0.035, hz + half), (xb - 0.002, H, D - 0.03), tone(OAK, 0.1), along="x")
    last = -L
    for s in seats:
        lifted = s == 0.0
        w = 0.3 if lifted else half
        plank(hard, (last, H - 0.035, hz - half), (s - w, H, hz + half), tone(OAK, 0.1), along="x")
        last = s + w
        if lifted:
            # The middle seat's board is off: the drain open under it, black, wide enough for a man.
            hard.poly([(s - w, H - 0.03, hz - half), (s + w, H - 0.03, hz - half), (s + w, H - 0.03, hz + half), (s - w, H - 0.03, hz + half)], DARK, BLACK, facing=(0, 1, 0))
            for x, way in ((s - w, 1), (s + w, -1)):
                hard.poly([(x, H, hz - half), (x, H, hz + half), (x, H - 0.035, hz + half), (x, H - 0.035, hz - half)], WOOD, rgba(OAK, 0.3), facing=(way, 0, 0))
            # The board itself, stood against the back of the stall.
            b = props.Placed(hard, (s + 0.22, H + 0.005, D - 0.1), 0.12, tilt=-1.36)
            c = tone(OAK, 0.1)
            seat_hole(b, 0.0, 0.2, 0.035, half, r, c)
            b.poly([(-half, 0.0, 0.2 - half), (half, 0.0, 0.2 - half), (half, 0.0, 0.2 + half), (-half, 0.0, 0.2 + half)], WOOD, rgba(c, 0.6), facing=(0, -1, 0))
            for sx in (-1, 1):
                plank(b, (sx * half - (0.11 if sx < 0 else 0.0), 0.0, 0.2 - half), (sx * half + (0.11 if sx > 0 else 0.0), 0.035, 0.2 + half), c, along="z")
        else:
            seat_hole(hard, s, hz, H, half, r, tone(OAK, 0.1))
            hard.poly(ring_pts((s, H - 0.034, hz), r + 0.03, 8, TAU / 16), DARK, BLACK, facing=(0, 1, 0))
    plank(hard, (last, H - 0.035, hz - half), (L, H, hz + half), tone(OAK, 0.1), along="x")
    # The stalls: a boarded back, and a partition between each seat and the next.
    edges = (-L, -1.8, -0.6, 0.6, 1.8, L)
    for xa, xb in zip(edges, edges[1:]):
        boards(hard, (xa, H, D - 0.03), (xb, H + 0.95, D), "y", "x", 6, OAK_DARK, gap=0.005, uneven=0.003, ragged=0.03, spread=0.2)
    for x in edges:
        xx = min(max(x, -L + 0.016), L - 0.016)
        boards(hard, (xx - 0.015, H, -D + 0.04), (xx + 0.015, H + 0.9, D - 0.03), "y", "z", 3, OAK_DARK, gap=0.004, uneven=0.002, ragged=0.04, spread=0.2)
    beam(hard, (-L, H + 0.8, D - 0.045), (L, H + 0.8, D - 0.045), 0.03, 0.07, tone(OAK_DARK), ends="")
    # What runs down its front, a tub of moss for wiping, a web in the end stall.
    for s in seats:
        dress.run(hard, (s + random.uniform(-0.08, 0.08), H - 0.04, -D), (0, -1), 0.2, 0.36, dress.DARK, 0.45, s)
    props.pot(soft, (2.84, H, 0.2), [(0.0, 0.085), (0.07, 0.095), (0.13, 0.1)], colour=(0.3, 0.26, 0.2), sides=9, mat=WOOD)
    props.heap(soft, (2.84, H + 0.1, 0.2), 0.085, 0.085, 0.05, colour=(0.028, 0.04, 0.02), seed=4.0, mat=PAINT)
    dress.cobweb(hard, (-L + 0.04, H + 0.9, D - 0.04), (0, -1, 0), (0, 0, -1), 0.4, 2)
    dress.cobweb(hard, (-L + 0.04, H + 0.88, D - 0.04), (1, 0, 0), (0, -1, 0), 0.35, 3)


# ---------------------------------------------------------------- closet

def cellar_closet(p):
    """The boarded closet in the granary's corner over the hidden stair, in
    the cellar scene's own coordinates: its east and north walls, and the
    two panels and the head round its door in the south one."""
    hard = p.hard
    Y0, Y1 = 0.05, 2.25
    XE, ZN, ZS, XW = -18.0, -25.2, -18.9, -19.6
    dark = OAK_DARK

    def upright(lo, hi, across, n, **kw):
        boards(hard, lo, hi, "y", across, n, dark, gap=kw.get("gap", 0.009), uneven=0.005, ragged=kw.get("ragged", 0.04), spread=0.24)

    # The east wall: upright boards on the granary's side, nailed to three rails on posts.
    cut = (-21.92, -21.73)
    upright((XE - 0.03, Y0, ZN + 0.1), (XE, Y1, cut[0]), "z", 17)
    upright((XE - 0.03, Y0, cut[1]), (XE, Y1, ZS), "z", 15)
    # One board broken off at a knot: a slot into the dark at the height of his eyes.
    props.slab(hard, [(cut[0] + 0.006, Y0), (cut[1] - 0.006, Y0), (cut[1] - 0.006, 1.42), (cut[1] - 0.07, 1.5), (cut[0] + 0.08, 1.38), (cut[0] + 0.006, 1.47)], "x", XE - 0.03, XE, tone(dark, 0.2))
    props.slab(hard, [(cut[0] + 0.006, Y1 - 0.02), (cut[1] - 0.006, Y1), (cut[1] - 0.006, 2.02), (cut[1] - 0.09, 1.96), (cut[0] + 0.006, 2.06)], "x", XE - 0.03, XE, tone(dark, 0.2))
    for y in (0.32, 1.2, 2.1):
        beam(hard, (XE - 0.065, y, ZN + 0.1), (XE - 0.065, y, ZS - 0.1), 0.07, 0.1, tone(dark), ends="")
        z = ZN + 0.2
        while z < ZS - 0.1:
            if not (cut[0] - 0.02 < z < cut[1] + 0.02) or y < 1.3:
                props.nail(hard, (XE, y + random.uniform(-0.02, 0.02), z), (1, 0, 0), r=0.012)
            z += random.uniform(0.17, 0.21)
    for z in (ZN + 0.05, -23.65, -22.1, -20.5, ZS - 0.05):
        corner = z in (ZN + 0.05, ZS - 0.05)
        beam(hard, (XE - (0.05 if corner else 0.07), Y0, z), (XE - (0.05 if corner else 0.07), Y1 - (0.0 if corner else 0.06), z), 0.1 if corner else 0.08, 0.1, tone(dark))
    # The north wall, the same, its boards to the granary.
    upright((XW, Y0, ZN), (XE - 0.1, Y1, ZN + 0.03), "x", 8)
    for y in (0.32, 1.2, 2.1):
        beam(hard, (XW, y, ZN + 0.065), (XE - 0.1, y, ZN + 0.065), 0.07, 0.1, tone(dark), ends="")
    beam(hard, (XW + 0.05, Y0, ZN + 0.05), (XW + 0.05, Y1, ZN + 0.05), 0.1, 0.1, tone(dark))
    # The south wall: a panel each side of the door, and the head over it.
    upright((XW, Y0, ZS - 0.03), (-19.3, Y1, ZS), "x", 2, ragged=0.02)
    upright((-18.4, Y0, ZS - 0.03), (XE - 0.1, Y1, ZS), "x", 2, ragged=0.02)
    for x in (-19.33, -18.37):
        beam(hard, (x, Y0, ZS - 0.065), (x, 2.05, ZS - 0.065), 0.06, 0.07, tone(dark))
    beam(hard, (-19.36, 2.09, ZS - 0.05), (-18.34, 2.09, ZS - 0.05), 0.1, 0.08, tone(dark))
    boards(hard, (-19.3, 2.13, ZS - 0.03), (-18.4, Y1, ZS), "y", "x", 5, dark, gap=0.008, uneven=0.004, ragged=0.012, spread=0.24)
    beam(hard, (XW + 0.05, Y0, ZS - 0.05), (XW + 0.05, Y1, ZS - 0.05), 0.1, 0.1, tone(dark))
    for y in (0.32, 1.2):
        beam(hard, (XW, y, ZS - 0.065), (-19.36, y, ZS - 0.065), 0.07, 0.1, tone(dark), ends="")
        beam(hard, (-18.34, y, ZS - 0.065), (XE - 0.1, y, ZS - 0.065), 0.07, 0.1, tone(dark), ends="")
    # Webs in the corners nobody reaches, inside and out.
    dress.cobweb(hard, (XE - 0.11, 2.16, ZN + 0.11), (0, -1, 0), (0, 0, 1), 0.55, 11)
    dress.cobweb(hard, (XE - 0.11, 2.14, ZN + 0.11), (-1, 0, 0), (0, 0, 1), 0.5, 12, sag=0.05)
    dress.cobweb(hard, (XE + 0.004, Y1 - 0.02, ZN + 0.04), (0, -1, 0), (0, 0, 1), 0.4, 13)


BUILDERS = {
    "barrel": barrel, "barrel_tapped": barrel_tapped, "barrel_stove": barrel_stove,
    "grain_sacks": grain_sacks, "grain_sacks_split": grain_sacks_split, "grain_sacks_gnawed": grain_sacks_gnawed,
    "shelves": shelves, "mortar": mortar, "millstone": millstone, "oven": oven, "oven_bones": oven_bones,
    "mill_wheel": mill_wheel, "hearth_kitchen": hearth_kitchen, "hearth_warming": hearth_warming, "latrine_seat": latrine_seat, "cellar_closet": cellar_closet,
}

if __name__ == "__main__":
    props.run(BUILDERS)
