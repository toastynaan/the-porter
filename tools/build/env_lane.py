"""The lane outside the abbey's gate (every night): its ground, and what
closes its ends.

`env_lane_ground`, in the abbey's own coordinates
(game/world/abbey/areas/street.tscn): a carriageway of setts down the lane (along z, its
middle at x = -43.4) and round the bend at each end (along x, at z = 47 and
-47), cambered, with a gutter along each kerb; a kerb and a flagged
sidewalk each side, along the abbey wall and out round the gate's apron,
along the house fronts and round their corners; the two alleys left as
trodden earth. Mud is in the joints, the gutters and the alleys. It has no
collision and nothing in it is more than 6 cm off y = 0: the lane's greybox
blocks are still what is walked on (and what footsteps sound on), with
their own faces not drawn. The flags before the abbey gate are that
greybox block, still drawn, in the same material.

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
from porter import fbm, lerp, smoothstep

LANE_X = -43.4
HALF = 3.0
WEST, EAST = LANE_X - HALF, LANE_X + HALF
BEND_Z = 47.0
# The lane's length each way, the bends' far end, the alleys (z, half width, x of their far end).
REACH = 50.0
BEND_WEST = -71.5
ALLEYS = ((-19.0, 1.1, -58.4), (15.0, 1.1, -58.4))
# The flags before the abbey gate (the greybox block GateApron, which is still drawn): x from, x to, z from, z to; its top.
APRON = (-42.4, -38.6, -4.3, 0.3)
APRON_TOP = 0.02

# The paving. Nothing here is solid: the walked surface is the greybox at
# y = 0, so it all lies within 6 cm of that. A sidewalk (kerb and flags) is
# WALK wide and UP high; the carriageway between the kerbs falls from its
# crown to a gutter GUTTER wide at each kerb's foot.
PAVING = "ground_lane"
WALK = 1.0
UP = 0.05
KERB = 0.16
ARRIS = 0.022
CROWN = 2.0
GUTTER = 0.28
GUTTER_DEEP = -0.045

ASHLAR = "stone_ashlar"
RUBBLE = "stone_rubble"
OAK = "wood_frame"
PALE = (0.9, 0.89, 0.86)


def near(d):
    """How the paving's material is told how far a point of the road is from the nearest kerb (see ground_lane.gdshader)."""
    return min(max((d + 0.25) / 2.25, 0.0), 1.0)


def road_height(d):
    """The carriageway `d` metres from the nearest kerb: the gutter, then the camber up to the crown."""
    if d <= GUTTER:
        return GUTTER_DEEP
    t = min((d - GUTTER) / (CROWN - GUTTER), 1.0)
    return -0.04 * (1.0 - t) ** 2


class Kerb:
    """A kerb's line (x, z) with the height of its top at each point, and
    the wall line that closes its sidewalk behind it."""

    def __init__(self, wall=()):
        self.pts = []
        self.ups = []
        self.marks = {}
        self.wall = list(wall)

    def to(self, x, z, up=UP):
        self.pts.append((x, z))
        self.ups.append(up)
        return self

    def arc(self, cx, cz, r, a0, a1, n=5, up=UP):
        """Round (cx, cz) from angle a0 to a1 (degrees from +x toward +z); the line is already at a0."""
        for i in range(1, n + 1):
            a = math.radians(a0 + (a1 - a0) * i / n)
            self.to(cx + r * math.cos(a), cz + r * math.sin(a), up)
        return self

    def mark(self, name):
        self.marks[name] = len(self.pts) - 1
        return self

    def flip(self):
        """The same kerb the other side of z = 0."""
        self.pts = [(x, -z) for x, z in self.pts]
        self.wall = [(x, -z) for x, z in self.wall]
        return self

    def outline(self):
        return self.pts + self.wall

    def inward(self):
        """At each point, the way into the sidewalk, long enough at a corner that the kerb keeps its width (a mitre)."""
        out = self.outline()
        area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(out, out[1:] + out[:1]))
        s = 1.0 if area > 0.0 else -1.0
        normals = []
        for (ax, az), (bx, bz) in zip(self.pts, self.pts[1:]):
            n = math.hypot(bx - ax, bz - az)
            normals.append((-s * (bz - az) / n, s * (bx - ax) / n))
        ways = []
        for i in range(len(self.pts)):
            a = normals[max(i - 1, 0)]
            b = normals[min(i, len(normals) - 1)]
            k = 1.0 + a[0] * b[0] + a[1] * b[1]
            ways.append(((a[0] + b[0]) / k, (a[1] + b[1]) / k))
        return ways

    def inner(self, d=KERB):
        return [(p[0] + w[0] * d, p[1] + w[1] * d) for p, w in zip(self.pts, self.inward())]

    def distance(self, x, z):
        best = 1.0e9
        for (ax, az), (bx, bz) in zip(self.pts, self.pts[1:]):
            dx, dz = bx - ax, bz - az
            t = min(max(((x - ax) * dx + (z - az) * dz) / (dx * dx + dz * dz), 0.0), 1.0)
            best = min(best, math.hypot(x - ax - dx * t, z - az - dz * t))
        return best

    def holds(self, x, z):
        """Whether (x, z) is on its sidewalk, the edge included."""
        out = self.outline()
        inside = False
        for (ax, az), (bx, bz) in zip(out, out[1:] + out[:1]):
            dx, dz = bx - ax, bz - az
            t = min(max(((x - ax) * dx + (z - az) * dz) / max(dx * dx + dz * dz, 1e-12), 0.0), 1.0)
            if math.hypot(x - ax - dx * t, z - az - dz * t) < 1e-3:
                return True
            if (az > z) != (bz > z) and x < ax + (z - az) * dx / dz:
                inside = not inside
        return inside


def kerbs():
    """Every kerb of the lane: along the abbey wall and out round the
    gate's apron; along the house fronts, turning in at each alley's mouth
    and round the corner into each bend; and along each bend's far side,
    turning in at the arch that closes the lane."""
    out = []
    # East. The apron stands out into the lane: the kerb goes round it, its top let down to the apron's flags.
    xk, zs, zn, r, low = APRON[0] - KERB + 0.02, APRON[2] - KERB + 0.02, APRON[3] + KERB - 0.02, 0.3, APRON_TOP + 0.007
    xe = EAST - WALK
    east = Kerb(wall=[(EAST, REACH + 0.2), (EAST, -REACH - 0.2)])
    east.to(xe, -REACH - 0.2).to(xe, zs).mark("apron0").to(xe - 0.35, zs, low).to(xk + r, zs, low).arc(xk + r, zs + r, r, -90, -180, 4, low)
    east.to(xk, zn - r, low).arc(xk + r, zn - r, r, 180, 90, 4, low).to(xe - 0.35, zn, low).to(xe, zn).mark("apron1").to(xe, REACH + 0.2)
    east.flags = [("z", EAST, [(0, "apron0"), (EAST, APRON[2]), (EAST, -REACH - 0.2)]), ("z", EAST, [("apron1", -1), (EAST, REACH + 0.2), (EAST, APRON[3])])]
    out.append(east)
    xw, r = WEST + WALK, 0.3
    # West, between the alleys.
    z0, z1 = ALLEYS[0][0] + ALLEYS[0][1], ALLEYS[1][0] - ALLEYS[1][1]
    mid = Kerb()
    mid.to(WEST, z0).to(xw - r, z0).arc(xw - r, z0 + r, r, -90, 0).to(xw, z1 - r).arc(xw - r, z1 - r, r, 0, 90).to(WEST, z1)
    mid.flags = [("z", WEST, [(0, -1)])]
    out.append(mid)
    for s in (1, -1):
        # West, from an alley to the lane's end, and round the houses' corner along the bend.
        za = ALLEYS[1][0] + ALLEYS[1][1] if s > 0 else -(ALLEYS[0][0] - ALLEYS[0][1])
        zc = BEND_Z - HALF
        k = Kerb(wall=[(BEND_WEST, zc), (WEST, zc)])
        k.to(WEST, za).to(xw - r, za).arc(xw - r, za + r, r, -90, 0).to(xw, zc).mark("corner").arc(WEST, zc, WALK, 0, 90, 7).to(BEND_WEST, zc + WALK)
        k.flags = [("z", WEST, [(0, "corner"), (WEST, s * zc)]), ("x", s * zc, [("corner", -1), (BEND_WEST, s * zc), (WEST, s * zc)])]
        out.append(k if s > 0 else k.flip())
        # The bend's far side, ending at the jamb of the arch across the lane.
        zf = BEND_Z + HALF
        k = Kerb(wall=[(BEND_WEST, zf + 0.2)])
        k.to(BEND_WEST, zf - WALK).to(WEST, zf - WALK).arc(WEST, zf, WALK, -90, 0, 7).to(xw, zf + 0.2)
        k.flags = [("x", s * zf, [(0, -1), (BEND_WEST, s * (zf + 0.2))])]
        out.append(k if s > 0 else k.flip())
    return out


def lay_kerb(m, k):
    """The kerb stones along a kerb's line: each its own length, its top,
    its worn arris and its face down into the gutter. A stone's colour is
    (its tone, 0.5, half its length, a number of its own); its UV is
    (metres from its end, metres over its top and down its face)."""
    ways = k.inward()
    for i in range(len(k.pts) - 1):
        (ax, az), (bx, bz) = k.pts[i], k.pts[i + 1]
        run = math.hypot(bx - ax, bz - az)
        n = max(1, int(round(run / random.uniform(0.75, 1.05)))) if run > 1.3 else 1
        cuts = [0.0] + sorted(min(max((j + random.uniform(-0.18, 0.18)) / n, 0.0), 1.0) for j in range(1, n)) + [1.0]
        nx, nz = -(bz - az) / run, (bx - ax) / run
        if nx * ways[i][0] + nz * ways[i][1] < 0.0:
            nx, nz = -nx, -nz
        for ta, tb in zip(cuts, cuts[1:]):
            length = (tb - ta) * run
            tone, own, tip = random.random(), random.random(), random.uniform(-0.003, 0.003)
            ends = []
            for t in (ta, tb):
                w = ways[i] if t == 0.0 else ways[i + 1] if t == 1.0 else (nx, nz)
                x, z, up = ax + (bx - ax) * t, az + (bz - az) * t, k.ups[i] + (k.ups[i + 1] - k.ups[i]) * t
                u = 0.0 if t == ta else length
                ends.append(((x + w[0] * KERB, up, z + w[1] * KERB), (x + w[0] * ARRIS, up + tip, z + w[1] * ARRIS), (x, up + tip - ARRIS, z),
                             (x - w[0] * 0.006, -0.085, z - w[1] * 0.006), u))
            colour = (tone, 0.5, min(length * 0.5, 1.0), own)
            a, b = ends
            v = (0.0, KERB - ARRIS, KERB + 0.009, KERB + 0.009 + 0.13)
            for j, facing in ((0, (0.0, 1.0, 0.0)), (1, (-nx, 1.0, -nz)), (2, (-nx, 0.0, -nz))):
                m.poly([a[j], b[j], b[j + 1], a[j + 1]], PAVING, colour, uvs=[(a[4], v[j]), (b[4], v[j]), (b[4], v[j + 1]), (a[4], v[j + 1])], facing=facing)


def lay_flags(m, k):
    """A kerb's sidewalk: flags from the back of the kerb to the wall, each
    stretch a single face (the material draws the flags). UV is (metres
    along the walk, metres from its wall)."""
    inner = k.inner()
    for frame, wall, parts in k.flags:
        pts = []
        for a, b in parts:
            if isinstance(a, float):
                pts.append((a, b))
                continue
            i0 = k.marks[a] if isinstance(a, str) else a
            i1 = k.marks[b] if isinstance(b, str) else b if b >= 0 else len(inner) - 1
            pts.extend(inner[i0:i1 + 1])
        uvs = [(z, abs(x - wall)) if frame == "z" else (x, abs(z - wall)) for x, z in pts]
        m.poly([(x, UP, z) for x, z in pts], PAVING, (0.0, 1.0, 1.0, 0.0), uvs=uvs, facing=(0, 1, 0))


def lines(a, b, step, more=()):
    n = int(round((b - a) / step))
    return sorted(set([round(a + (b - a) * i / n, 4) for i in range(n + 1)] + [round(v, 4) for v in more if a < v < b]))


def ground():
    porter.reset(71)
    all_kerbs = kerbs()

    def kerb_distance(x, z):
        d = min(k.distance(x, z) for k in all_kerbs)
        return -d if any(k.holds(x, z) for k in all_kerbs) else d

    def alleyness(x, z):
        for z_mid, half, _west in ALLEYS:
            if abs(z - z_mid) <= half + 1e-6:
                return 1.0 - smoothstep(WEST - 1.2, WEST, x)
        return 0.0

    def at(x, z):
        """The road at (x, z): its height, and its colour (mud, 0, how near a kerb, standing water)."""
        d = kerb_distance(x, z)
        h = road_height(d) + 0.006 * fbm(x, z, 0.5, 2, 1.0)
        # A few shallow puddles where the setts have sunk, away from the crown.
        pool = smoothstep(0.32, 0.55, fbm(x, z, 0.16, 2, 4.0)) * (1.0 - 0.6 * smoothstep(1.0, CROWN, d))
        h -= 0.012 * pool
        mud = 0.1 + 0.1 * fbm(x, z, 0.3, 2, 3.0)
        k = alleyness(x, z)
        if k > 0.0:
            # An alley: trodden earth over what paving it ever had, a runnel down it, wet.
            z_mid = min(ALLEYS, key=lambda a: abs(a[0] - z))[0]
            side = z - z_mid
            run = (1.0 - smoothstep(0.1, 0.45, abs(side + 0.3 * fbm(x, 0.0, 0.3, 2, 10.0)))) * smoothstep(-0.3, 0.2, fbm(x, z, 0.25, 2, 11.0))
            ha = 0.005 + 0.02 * smoothstep(0.2, 1.1, abs(side)) + 0.012 * fbm(x, z, 0.6, 2, 9.0) - 0.03 * run
            h, mud, pool, d = lerp(h, ha, k), lerp(mud, 0.95, k), lerp(pool, run, k), lerp(d, CROWN, k)
        return max(h, -0.058), (mud, 0.0, near(d), pool)

    m = porter.Mesh("Lane")

    def strip(xs, zs, uv):
        index = {}

        def vert(i, j):
            if (i, j) not in index:
                h, colour = at(xs[i], zs[j])
                index[(i, j)] = m.vert(xs[i], h, zs[j], colour, uv(xs[i], zs[j]))
            return index[(i, j)]

        for i in range(len(xs) - 1):
            for j in range(len(zs) - 1):
                corners = ((xs[i], zs[j]), (xs[i], zs[j + 1]), (xs[i + 1], zs[j + 1]), (xs[i + 1], zs[j]))
                # Nothing is laid where a sidewalk or the gate's apron covers it.
                if all(any(k.holds(x, z) for k in all_kerbs) for x, z in corners):
                    continue
                m.face((vert(i, j), vert(i, j + 1), vert(i + 1, j + 1), vert(i + 1, j)), PAVING)

    # The lines the road's faces follow: close under each kerb, the gutter's edge, then up to the crown.
    across = [0.0, 0.44, 0.88, 1.32, 1.7, 2.1, HALF]
    edge = [BEND_Z - HALF + v for v in (0.0, 0.9, 1.3, 1.68, 2.12, 2.56, 3.0, 3.44, 3.88, 4.32, 4.7, 5.1, 6.0)]
    xs = sorted(set([round(LANE_X + s * v, 4) for v in across for s in (-1, 1)] + [APRON[0] - KERB - 0.28, APRON[0] - 0.05]))
    alley_edges = [z + s * half for z, half, _w in ALLEYS for s in (-1, 1)]
    zs = sorted(set(lines(-(BEND_Z - HALF), BEND_Z - HALF, 0.5, alley_edges) + edge + [-v for v in edge]))
    strip(xs, zs, lambda x, z: (z, x - LANE_X))
    for s in (-1, 1):
        strip(lines(BEND_WEST, WEST, 0.5), sorted(s * v for v in edge), lambda x, z, s=s: (x, z - s * BEND_Z))
    for z_mid, half, west in ALLEYS:
        strip(lines(west, WEST, 0.5), [z for z in zs if z_mid - half - 1e-6 <= z <= z_mid + half + 1e-6], lambda x, z, z_mid=z_mid: (x, z - z_mid))
    m.build(smooth=True)

    walks = porter.Mesh("Walks")
    for k in all_kerbs:
        lay_kerb(walks, k)
        lay_flags(walks, k)
    walks.build()
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


def road(m, half, z0, z1, step):
    """A length of the lane's carriageway in a model of its own, along z about x = 0: setts, cambered, a gutter at each side `half` out."""
    xs = [s * v for v in (0.0, 0.7, 1.4, 1.72, 2.0) for s in (-1, 1) if v or s > 0]
    xs = sorted(x * half / 2.0 if abs(x) < 2.0 else math.copysign(half, x) for x in xs)
    zs = cp.steps(z0, z1, step)
    for za, zb in zip(zs, zs[1:]):
        for xa, xb in zip(xs, xs[1:]):
            pts = [(x, road_height(half - abs(x)), z) for x, z in ((xa, za), (xb, za), (xb, zb), (xa, zb))]
            m.poly(pts, PAVING, [(0.15, 0.0, near(half - abs(q[0])), 0.0) for q in pts], uvs=[(q[2], q[0]) for q in pts], facing=(0, 1, 0))


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
    # The passage's floor: the lane's setts go on through it, a gutter along each wall.
    road(m, half + 0.3, -0.05, length, 1.0)
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
    road(b, 3.2, length, far, 2.0)
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
