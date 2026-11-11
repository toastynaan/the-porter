"""The lane outside the abbey's gate (every night): its ground, and what
closes its ends.

`env_lane_ground`, in the abbey's own coordinates
(game/world/abbey/areas/street.tscn): cobbles down the lane (along z, its
middle at x = -43.4), round the bend at each end (along x, at z = 47 and
-47) and up the two alleys, with mud down the cart track and against the
walls, a kennel down the middle with water in it, and rain in the hollows.
It has no collision: the lane's greybox blocks are still what is walked on
(and what footsteps sound on), with their own faces not drawn. The flags
before the abbey gate are left clear.

`env_lane_end`, in its own space (its mouth at z = 0, looking out along
-Z): a house built across the street on an archway. The passage under it
is dark, and through it the street goes on: house fronts, lit windows, a
lantern, a tower against the sky. Nobody gets through: there is a wall
that isn't seen a pace inside the arch.

`env_lane_wall`: the lane's face of the abbey's precinct wall (see wall()).

Run: tools/build.sh env_lane
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
import city_parts as cp
from porter import fbm, smoothstep

LANE_X = -43.4
HALF = 3.0
BEND_Z = 47.0
# The lane's length each way, the bends' far end, the alleys (z, half width, x of their far end).
REACH = 50.0
BEND_WEST = -71.5
ALLEYS = ((-19.0, 1.1, -58.4), (15.0, 1.1, -58.4))
# The flags before the abbey gate: x from, x to, z from, z to.
APRON = (-42.45, -38.6, -4.35, 0.35)

ASHLAR = "stone_ashlar"
RUBBLE = "stone_rubble"
OAK = "wood_frame"
PALE = (0.9, 0.89, 0.86)


def surface(side, along, seed):
    """Height and masks (mud, 0, 0, water) `side` metres from a street's middle, `along` it."""
    d = abs(side)
    h = 0.03 + 0.05 * smoothstep(0.2, HALF, d) + 0.015 * fbm(along, side, 0.5, 2, seed)
    kennel = 1.0 - smoothstep(0.1, 0.42, abs(side + 0.25 * fbm(along, 0.0, 0.15, 2, seed + 1.0)))
    h -= 0.05 * kennel
    track = 1.0 - smoothstep(1.2, 2.4, d + 0.6 * fbm(along, side, 0.2, 2, seed + 2.0))
    drift = smoothstep(HALF - 1.0, HALF - 0.1, d + 0.5 * fbm(along, side, 0.3, 2, seed + 3.0))
    mud = max(track * 0.7, drift)
    return h, (mud, 0.0, 0.0, kennel * smoothstep(-0.2, 0.3, fbm(along, side, 0.12, 2, seed + 4.0) + 0.25))


def strip(m, x0, x1, z0, z1, at, skip=None, step=0.5):
    nx, nz = int(round((x1 - x0) / step)), int(round((z1 - z0) / step))
    index = {}
    for i in range(nx + 1):
        for j in range(nz + 1):
            x, z = x0 + (x1 - x0) * i / nx, z0 + (z1 - z0) * j / nz
            h, mask, uv = at(x, z)
            index[(i, j)] = m.vert(x, h, z, mask, uv)
    for i in range(nx):
        for j in range(nz):
            cx, cz = x0 + (x1 - x0) * (i + 0.5) / nx, z0 + (z1 - z0) * (j + 0.5) / nz
            if skip and skip(cx, cz):
                continue
            m.face((index[(i, j)], index[(i, j + 1)], index[(i + 1, j + 1)], index[(i + 1, j)]), "ground_street")


def ground():
    porter.reset(71)
    m = porter.Mesh("Lane")

    def lane(x, z):
        h, mask = surface(x - LANE_X, z, 1.0)
        return h, mask, (z, x - LANE_X)

    def in_apron(x, z):
        return APRON[0] < x < APRON[1] and APRON[2] < z < APRON[3]

    strip(m, LANE_X - HALF, LANE_X + HALF, -REACH, REACH, lane, in_apron)
    for s in (-1, 1):
        def bend(x, z, s=s):
            h, mask = surface(z - s * BEND_Z, x, 5.0 + s)
            # Where it runs into the lane, the lane's own surface takes over.
            k = smoothstep(LANE_X - HALF - 2.0, LANE_X - HALF, x)
            hl, ml = surface(x - LANE_X, z, 1.0)
            return h * (1.0 - k) + hl * k, tuple(a * (1.0 - k) + b * k for a, b in zip(mask, ml)), (x, z - s * BEND_Z)
        strip(m, BEND_WEST, LANE_X - HALF, s * BEND_Z - HALF, s * BEND_Z + HALF, bend)
    for z_mid, half, west in ALLEYS:
        def alley(x, z, z_mid=z_mid, half=half):
            side = z - z_mid
            h = 0.04 + 0.03 * smoothstep(0.2, half, abs(side)) + 0.015 * fbm(x, z, 0.6, 2, 9.0)
            pool = (1.0 - smoothstep(0.1, 0.45, abs(side + 0.3 * fbm(x, 0.0, 0.3, 2, 10.0)))) * smoothstep(-0.3, 0.2, fbm(x, z, 0.25, 2, 11.0))
            return h - 0.03 * pool, (1.0, 0.0, 0.0, pool), (x, 7.0)
        strip(m, west, LANE_X - HALF, z_mid - half, z_mid + half, alley, step=0.55)
    m.build(smooth=True)
    porter.export("env_lane_ground")


# The abbey's precinct wall along the lane's east side: its west face, its
# length each way, its height; the gate's porch (left clear) and the squints
# (z of each; a slit is left open at eye level).
WALL_X = -40.4
WALL_REACH = 40.0
WALL_HIGH = 4.0
PORCH = (-4.32, 0.32)
SQUINTS = (-6.0, 6.0, 14.0)
BUTTRESSES = (-36.0, -27.0, -18.0, -10.5, 10.0, 21.0, 30.0, 37.5)


def wall():
    """`env_lane_wall`: the face the lane sees of the precinct wall, laid over
    the greybox wall (game/world/abbey/abbey.tscn, which still stops people
    and is what the abbey's side sees): rubble with a plinth, a coping,
    and buttresses of cut stone."""
    porter.reset(79)
    m = porter.Mesh("Wall")
    tint = cp.stone_tint(0.0, WALL_HIGH, seed=6.0, worn=0.9)
    x = WALL_X - 0.04

    def face(z0, z1, y0, y1):
        cp.panel(m, (x, z0), (x, z1), y0, y1, (-1, 0, 0), RUBBLE, tint, 2.0, 1.0)

    cuts = sorted([(PORCH[0], PORCH[1], 0.0, WALL_HIGH + 1.0)] + [(z - 0.22, z + 0.22, 1.3, 1.9) for z in SQUINTS])
    z = -WALL_REACH
    for z0, z1, y0, y1 in cuts + [(WALL_REACH, WALL_REACH, 0.0, 0.0)]:
        face(z, z0, 0.0, WALL_HIGH)
        if z1 > z0 and y1 < WALL_HIGH:
            face(z0, z1, 0.0, y0)
            face(z0, z1, y1, WALL_HIGH)
            # The slit's splayed sides, so the skin has thickness there.
            for zz, f in ((z0, 1), (z1, -1)):
                m.poly([(x, y0, zz), (x, y1, zz), (WALL_X + 0.1, y1, zz + f * 0.1), (WALL_X + 0.1, y0, zz + f * 0.1)], ASHLAR, cp.rgba(cp.STONE, 0.6),
                       facing=(0, 0, f))
            for yy, f in ((y0, 1), (y1, -1)):
                m.poly([(x, yy, z0), (x, yy, z1), (WALL_X + 0.1, yy, z1), (WALL_X + 0.1, yy, z0)], ASHLAR, cp.rgba(cp.STONE, 0.55), facing=(0, f, 0))
        z = z1
    for z0, z1 in ((-WALL_REACH, PORCH[0]), (PORCH[1], WALL_REACH)):
        # A plinth of long stones at its foot, and a weathered coping over its top.
        for za, zb in zip(cp.steps(z0, z1, 1.9), cp.steps(z0, z1, 1.9)[1:]):
            k = 0.62 + 0.14 * math.sin(za * 2.3)
            cp.block(m, (x - 0.09, 0.0, za + 0.01), (x, 0.36 + 0.03 * math.sin(za), zb - 0.01), ASHLAR, cp.rgba(cp.STONE_DAMP, 1.2 * k / 0.62), faces="xzZY")
            top = WALL_HIGH + 0.02 * math.sin(za * 1.7)
            cp.block(m, (x - 0.1, top - 0.04, za + 0.008), (WALL_X + 0.92, top + 0.13, zb - 0.008), ASHLAR, cp.rgba(PALE, k + 0.12), faces="xXzZy")
            m.poly([(x - 0.1, top + 0.13, za), (x - 0.1, top + 0.13, zb), (WALL_X + 0.4, top + 0.3, zb), (WALL_X + 0.4, top + 0.3, za)], ASHLAR,
                   cp.rgba(PALE, k), facing=(-1, 1, 0))
            m.poly([(WALL_X + 0.92, top + 0.13, za), (WALL_X + 0.92, top + 0.13, zb), (WALL_X + 0.4, top + 0.3, zb), (WALL_X + 0.4, top + 0.3, za)], ASHLAR,
                   cp.rgba(PALE, k * 0.9), facing=(1, 1, 0))
    # Buttresses: two stages, each weathered back at its head.
    for i, bz in enumerate(BUTTRESSES):
        bt = cp.stone_tint(0.0, 3.4, seed=10.0 + i, worn=0.6)
        for y0, y1, out in ((0.0, 1.9, 0.42), (1.9, 3.2, 0.26)):
            cp.slab(m, (x - out, y0, bz - 0.36), (x, y1, bz + 0.36), ASHLAR, bt, faces="xzZ", step=1.0)
            slope = [(x - out, y1, bz - 0.36), (x - out, y1, bz + 0.36), (x - (0.26 if y0 == 0.0 else 0.0), y1 + 0.3, bz + 0.36),
                     (x - (0.26 if y0 == 0.0 else 0.0), y1 + 0.3, bz - 0.36)]
            m.poly(slope, ASHLAR, cp.rgba(PALE, 0.8), facing=(-1, 1, 0))
            for zz, f in ((bz - 0.36, -1), (bz + 0.36, 1)):
                m.poly([(x - out, y1, zz), (x - (0.26 if y0 == 0.0 else 0.0), y1 + 0.3, zz), (x, y1 + 0.3, zz), (x, y1, zz)], ASHLAR,
                       cp.rgba(cp.STONE, 0.75), facing=(0, 0, f))
        c = porter.Mesh("Buttress%d-colonly" % i)
        c.box((x - 0.42, 0.0, bz - 0.36), (x, 3.2, bz + 0.36), ASHLAR)
        c.build()
    m.build()
    porter.export("env_lane_wall")


# The house over the arch: half its width, the passage (half width, springing, rise, length), its floors.
WIDE = 3.5
PASS = (1.7, 2.0, 1.5, 7.0)
STONE_TOP, UPPER_TOP = 4.4, 7.2


def end():
    porter.reset(73)
    half, spring, rise, length = PASS
    m = porter.Mesh("End")
    tint = cp.stone_tint(0.0, STONE_TOP, seed=3.0, worn=0.85)
    soot = lambda x, y, z: tuple(c * 0.5 for c in tint(x, y, z)[:3]) + (1.0,)
    # The stone floor: its face with the arch in two orders, the passage, the sides.
    cp.arch_wall(m, 0.0, -WIDE, WIDE, 0.0, STONE_TOP, half + 0.3, spring, rise + 0.22, (0, 0, -1), ASHLAR, tint)
    cp.vault(m, 0.0, 0.4, half + 0.3, spring, rise + 0.22, ASHLAR, tint, step=0.5)
    cp.arch_wall(m, 0.4, -half - 0.6, half + 0.6, 0.0, spring + rise + 0.6, half, spring, rise, (0, 0, -1), ASHLAR, tint)
    cp.arch_band(m, 0.0, half + 0.3, spring, rise + 0.22, 0.3, 0.07, (0, 0, -1), ASHLAR, PALE, y0=0.0)
    cp.vault(m, 0.4, length, half, spring, rise, RUBBLE, soot)
    for z in (2.4, 4.8):
        cp.vault(m, z, z + 0.3, half - 0.12, spring, rise - 0.1, ASHLAR, soot, step=0.4)
    cp.arch_wall(m, length, -WIDE, WIDE, 0.0, STONE_TOP, half, spring, rise, (0, 0, 1), RUBBLE, tint)
    for s in (-1, 1):
        cp.panel(m, (s * WIDE, 0.0), (s * WIDE, length), 0.0, UPPER_TOP, (s, 0, 0), RUBBLE, tint, 2.4, 1.5)
    # A string course, and the timber floor over it, jettied on its joists.
    cp.block(m, (-WIDE, STONE_TOP - 0.12, -0.08), (WIDE, STONE_TOP + 0.06, 0.0), ASHLAR, cp.rgba(PALE, 0.85), faces="xXzyY")
    zf = -0.55
    m.poly([(-WIDE, STONE_TOP + 0.06, 0.0), (WIDE, STONE_TOP + 0.06, 0.0), (WIDE, STONE_TOP + 0.06, zf), (-WIDE, STONE_TOP + 0.06, zf)], OAK,
           (0.18, 0.17, 0.16, 1.0), facing=(0, -1, 0))
    x = -WIDE + 0.12
    while x < WIDE:
        m.box((x - 0.07, STONE_TOP - 0.1, zf - 0.04), (x + 0.07, STONE_TOP + 0.06, 0.0), OAK, (0.42, 0.4, 0.37, 1.0), faces="xXzy")
        x += 0.5
    daub = lambda x, y, z: tuple(c * (0.9 + 0.14 * fbm(x, y, 0.4, 2, 2.0)) for c in (0.7, 0.68, 0.62)) + (1.0 - 0.6 * smoothstep(0.0, 0.4, fbm(x, y, 0.3, 2, 5.0)),)
    cp.panel(m, (-WIDE, zf), (WIDE, zf), STONE_TOP + 0.06, UPPER_TOP, (0, 0, -1), "plaster_daub", daub, 1.2, 1.0)
    for s in (-1, 1):
        cp.panel(m, (s * WIDE, zf), (s * WIDE, 0.0), STONE_TOP + 0.06, UPPER_TOP, (s, 0, 0), "plaster_daub", daub, 1.0, 1.4)
    oak = (0.36, 0.34, 0.32, 1.0)
    zb = zf - 0.04
    for y in (STONE_TOP + 0.06, UPPER_TOP - 0.2):
        m.poly([(-WIDE, y, zb), (WIDE, y, zb), (WIDE, y + 0.2, zb), (-WIDE, y + 0.2, zb)], OAK, oak, facing=(0, 0, -1))
    x = -WIDE
    while x < WIDE + 0.01:
        xa = min(x, WIDE - 0.16)
        if not (-2.25 < xa < -0.95 or 1.0 < xa < 2.2):
            m.poly([(xa, STONE_TOP + 0.26, zb), (xa + 0.16, STONE_TOP + 0.26, zb), (xa + 0.16, UPPER_TOP - 0.2, zb), (xa, UPPER_TOP - 0.2, zb)], OAK, oak,
                   facing=(0, 0, -1))
        x += 0.7
    # Two windows: one with a light behind it, one shuttered.
    for cx, mat in ((-1.6, "window_candle"), (1.6, "wood_boards")):
        pts = [(cx - 0.5, 5.2, zb - 0.01), (cx + 0.5, 5.2, zb - 0.01), (cx + 0.5, 6.35, zb - 0.01), (cx - 0.5, 6.35, zb - 0.01)]
        m.poly(pts, mat, (0.45, 0.42, 0.4, 1.0), uvs=[(0, 0), (1, 0), (1, 1), (0, 1)], facing=(0, 0, -1))
        for xa, xb, ya, yb in ((cx - 0.58, cx + 0.58, 5.1, 5.2), (cx - 0.58, cx + 0.58, 6.35, 6.45), (cx - 0.58, cx - 0.5, 5.2, 6.35),
                               (cx + 0.5, cx + 0.58, 5.2, 6.35), (cx - 0.03, cx + 0.03, 5.2, 6.35)):
            m.poly([(xa, ya, zb - 0.03), (xb, ya, zb - 0.03), (xb, yb, zb - 0.03), (xa, yb, zb - 0.03)], OAK, oak, facing=(0, 0, -1))
    cp.gable_roof(m, -WIDE - 0.3, WIDE + 0.3, zf - 0.35, length + 0.4, UPPER_TOP, UPPER_TOP + 3.0, "roof_tiles", (0.8, 0.78, 0.76), along="x", over=0.1,
                  sag=0.12)
    for s in (-1, 1):
        pts = [(s * WIDE, UPPER_TOP, zf), (s * WIDE, UPPER_TOP, length), (s * WIDE, UPPER_TOP + 3.0, (zf + length) * 0.5)]
        m.poly(pts, "plaster_daub", [daub(*p) for p in pts], facing=(s, 0, 0))
    # The passage's floor: trodden mud, wet down the middle.
    for za, zb3 in zip(cp.steps(-0.05, length, 1.0), cp.steps(-0.05, length, 1.0)[1:]):
        for xa, xb in zip(cp.steps(-half - 0.3, half + 0.3, 1.0), cp.steps(-half - 0.3, half + 0.3, 1.0)[1:]):
            pts = [(xa, 0.04, za), (xb, 0.04, za), (xb, 0.04, zb3), (xa, 0.04, zb3)]
            m.poly(pts, "ground_street", [(0.9, 0.0, 0.0, 0.5 if abs(q[0]) < 0.6 else 0.0) for q in pts], uvs=[(q[2], 7.0) for q in pts], facing=(0, 1, 0))
    # A stone to keep wheels off each jamb.
    for s in (-1, 1):
        m.tube([(s * (half + 0.42), 0.0, -0.22), (s * (half + 0.42), 0.55, -0.2), (s * (half + 0.42), 0.7, -0.16)], [0.2, 0.17, 0.06], 7, ASHLAR,
               cp.rgba(cp.STONE, 0.7), caps=True)
    m.build()

    # The street beyond, seen through the passage: never reached, so it is all faces.
    b = porter.Mesh("Beyond")
    random.seed(4)
    far = 36.0
    zs = cp.steps(length, far, 2.0)
    for za, zb2 in zip(zs, zs[1:]):
        b.poly([(-3.2, 0.03, za), (3.2, 0.03, za), (3.2, 0.03, zb2), (-3.2, 0.03, zb2)], "ground_street",
               [(0.6, 0.0, 0.0, 0.3 if abs(x) < 1.0 else 0.0) for x in (-3.2, 3.2, 3.2, -3.2)], uvs=[(za, 7.0), (za, 7.0), (zb2, 7.0), (zb2, 7.0)],
               facing=(0, 1, 0))
    for s in (-1, 1):
        z = length
        while z < far - 0.1:
            w = min(random.choice((4.6, 5.2, 6.0)), far - z)
            tone = random.uniform(0.5, 0.8)
            wash = cp.flat_tint((tone, tone * 0.97, tone * 0.9))
            low, high = random.uniform(2.8, 3.2), random.uniform(5.6, 8.2)
            mat = random.choice(("plaster_daub", "plaster_worn", "plaster_ochre"))
            cp.panel(b, (s * 3.2, z), (s * 3.2, z + w), 0.0, low, (-s, 0, 0), mat if random.random() < 0.6 else RUBBLE, wash, 3.0, 1.6)
            cp.panel(b, (s * 2.75, z), (s * 2.75, z + w), low, high, (-s, 0, 0), mat, wash, 3.0, 1.4)
            b.poly([(s * 3.2, low, z), (s * 3.2, low, z + w), (s * 2.75, low, z + w), (s * 2.75, low, z)], OAK, (0.15, 0.14, 0.14, 1.0), facing=(0, -1, 0))
            for y in (low, (low + high) * 0.5, high - 0.18):
                b.poly([(s * 2.72, y, z), (s * 2.72, y, z + w), (s * 2.72, y + 0.18, z + w), (s * 2.72, y + 0.18, z)], OAK, (0.3, 0.29, 0.27, 1.0),
                       facing=(-s, 0, 0))
            for zz in (z + 0.08, z + w - 0.08):
                b.poly([(s * 2.72, low, zz - 0.08), (s * 2.72, low, zz + 0.08), (s * 2.72, high, zz + 0.08), (s * 2.72, high, zz - 0.08)], OAK,
                       (0.3, 0.29, 0.27, 1.0), facing=(-s, 0, 0))
            # A window up, sometimes lit, and a dark door below.
            wz = z + w * random.uniform(0.35, 0.65)
            lit = random.random() < 0.45
            pts = [(s * 2.7, low + 0.9, wz - 0.5), (s * 2.7, low + 0.9, wz + 0.5), (s * 2.7, low + 1.95, wz + 0.5), (s * 2.7, low + 1.95, wz - 0.5)]
            b.poly(pts, "window_candle" if lit else "window_dark", uvs=[(0, 0), (1, 0), (1, 1), (0, 1)], facing=(-s, 0, 0))
            dz = z + w * random.uniform(0.15, 0.3)
            b.poly([(s * 3.17, 0.0, dz - 0.45), (s * 3.17, 0.0, dz + 0.45), (s * 3.17, 2.0, dz + 0.45), (s * 3.17, 2.0, dz - 0.45)], "window_dark",
                   facing=(-s, 0, 0))
            # Its roof, sloping back.
            b.poly([(s * 2.5, high, z), (s * 2.5, high, z + w), (s * 6.0, high + 2.8, z + w), (s * 6.0, high + 2.8, z)], "roof_tiles",
                   (0.6, 0.6, 0.6, 1.0), uvs=[(0, 0), (w / 1.8, 0), (w / 1.8, 2.0), (0, 2.0)], facing=(-s, 1, 0))
            z += w
    # What stands across its end, and a church tower over the roofs, against the sky.
    wash = cp.flat_tint((0.6, 0.58, 0.54))
    cp.panel(b, (-3.2, far), (3.2, far), 0.0, 7.5, (0, 0, -1), "plaster_worn", wash, 3.2, 1.9)
    b.poly([(-0.45, 3.9, far - 0.03), (0.45, 3.9, far - 0.03), (0.45, 5.0, far - 0.03), (-0.45, 5.0, far - 0.03)], "window_candle",
           uvs=[(0, 0), (1, 0), (1, 1), (0, 1)], facing=(0, 0, -1))
    b.poly([(-3.6, 7.5, far - 0.3), (3.6, 7.5, far - 0.3), (3.6, 10.2, far + 3.0), (-3.6, 10.2, far + 3.0)], "roof_tiles", (0.6, 0.6, 0.6, 1.0),
           uvs=[(0, 0), (4, 0), (4, 2), (0, 2)], facing=(0, 1, -1))
    tx, tz, tw = 1.6, far + 16.0, 2.6
    for y0, y1, w in ((0.0, 19.0, tw), (19.0, 20.2, tw + 0.35)):
        b.box((tx - w, y0, tz - w), (tx + w, y1, tz + w), "far_dark", faces="xXzZY")
    for dx in (-1, 1):
        for dz in (-1, 1):
            b.box((tx + dx * (tw + 0.1) - 0.3, 20.2, tz + dz * (tw + 0.1) - 0.3), (tx + dx * (tw + 0.1) + 0.3, 21.6, tz + dz * (tw + 0.1) + 0.3),
                  "far_dark", faces="xXzZY")
    for dx in (-0.8, 0.8):
        b.poly([(tx + dx - 0.3, 14.5, tz - tw - 0.02), (tx + dx + 0.3, 14.5, tz - tw - 0.02), (tx + dx + 0.3, 16.6, tz - tw - 0.02),
                (tx + dx - 0.3, 16.6, tz - tw - 0.02)], "window_dark", facing=(0, 0, -1))
    b.build()

    # Nobody goes through: a wall a pace inside the arch, and the house itself.
    for name, lo, hi in (("Stop", (-half - 0.3, 0.0, 1.0), (half + 0.3, STONE_TOP, 1.4)), ("PierW", (-WIDE, 0.0, 0.0), (-half, UPPER_TOP, length)),
                         ("PierE", (half, 0.0, 0.0), (WIDE, UPPER_TOP, length)), ("Over", (-half, spring + rise * 0.6, zf), (half, UPPER_TOP, length))):
        c = porter.Mesh(name + "-colonly")
        c.box(lo, hi, ASHLAR)
        c.build()
    porter.export("env_lane_end")


if __name__ == "__main__":
    ground()
    end()
    wall()
