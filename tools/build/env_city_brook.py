"""The brook through the city and the stone bridge over it (night 0, the
road in), in the road scene's coordinates (game/world/road/env_road.tscn:
the street runs along x at z = 47; the brook crosses it, running along z).

The street inside Aldgate ends at the water. The wagon goes over the bridge
with the porter looking back down the street to the gate, and there the
talk of the road ends and the night goes dark (docs/prologue.md).

- The bridge: one low arch of cut stone, hump-backed, cobbled, a parapet
  each side between stone piers. Each pier carries an iron standard for a
  lantern (the lanterns are in env_road.tscn). Cutwaters at its feet.
- The brook: black water between walls of rubble, running away north and
  south between the backs of the houses until a building closes over it
  on an arch, with a window lit over the water.
- Stairs down to the water on the north-west bank, and mooring posts.

Collision: the bridge's roadway and parapets, and the banks' kerbs.

Run: tools/build.sh env_city_brook
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
import city_parts as cp
from porter import smoothstep

ROAD_Z = 47.0
# The banks, the water's level and the bed.
WEST, EAST = -80.0, -72.0
MID = (WEST + EAST) * 0.5
WATER = -1.7
DEEP = -2.5
# How far the brook runs each way before a building closes over it.
REACH = 40.0
# The bridge: half the length of its hump, how high its crown, half the roadway, the parapet.
RAMP = 6.0
CROWN = 0.8
HALF = 2.5
PARAPET = 0.42
RAIL = 0.95
# The arch: its springing, and the stone over its crown.
SPRING = -1.45
THICK = 0.45

ASHLAR = "stone_ashlar"
RUBBLE = "stone_rubble"
IRON = "iron_cart"
PALE = (0.9, 0.89, 0.86)


def deck(x):
    """The roadway's height at x."""
    d = abs(x - MID)
    return CROWN * 0.5 * (1.0 + math.cos(math.pi * d / RAMP)) if d < RAMP else 0.0


def soffit(x):
    """The underside of the arch at x (the bed, outside it)."""
    d = abs(x - MID)
    half = (EAST - WEST) * 0.5
    if d >= half:
        return DEEP
    rise = CROWN - THICK - SPRING
    return SPRING + rise * math.sqrt(max(1.0 - (d / half) ** 2, 0.0))


def bridge(m):
    tint = cp.stone_tint(WATER, CROWN + RAIL, seed=5.0, worn=0.85)
    xs = cp.steps(WEST - 0.3, EAST + 0.3, 0.5)
    for s in (-1, 1):
        zo = ROAD_Z + s * (HALF + PARAPET)
        zi = ROAD_Z + s * HALF
        for xa, xb in zip(xs, xs[1:]):
            ta, tb = deck(xa) + RAIL, deck(xb) + RAIL
            # The outer face, from the arch (or the bed) up to the parapet's top, in two heights so its tint follows.
            for lo_a, lo_b, hi_a, hi_b in ((soffit(xa), soffit(xb), deck(xa) - 0.1, deck(xb) - 0.1), (deck(xa) - 0.1, deck(xb) - 0.1, ta, tb)):
                if hi_a - lo_a < 0.01 and hi_b - lo_b < 0.01:
                    continue
                pts = [(xa, lo_a, zo), (xb, lo_b, zo), (xb, hi_b, zo), (xa, hi_a, zo)]
                m.poly(pts, ASHLAR, [tint(*p) for p in pts], facing=(0, 0, s))
            # The parapet's inner face and its coping.
            pts = [(xa, deck(xa), zi), (xb, deck(xb), zi), (xb, tb, zi), (xa, ta, zi)]
            m.poly(pts, ASHLAR, [tint(*p) for p in pts], facing=(0, 0, -s))
            cope = [(xa, ta, zi - s * 0.04), (xb, tb, zi - s * 0.04), (xb, tb, zo + s * 0.04), (xa, ta, zo + s * 0.04)]
            m.poly(cope, ASHLAR, cp.rgba(PALE, 0.8 + 0.12 * math.sin(xa * 3.7)), facing=(0, 1, 0))
            for zz, f in ((zi - s * 0.04, -s), (zo + s * 0.04, s)):
                m.poly([(xa, ta - 0.12, zz), (xb, tb - 0.12, zz), (xb, tb, zz), (xa, ta, zz)], ASHLAR, cp.rgba(PALE, 0.72), facing=(0, 0, f))
            # A string course where the roadway is.
            band = [(xa, deck(xa) - 0.14, zo + s * 0.05), (xb, deck(xb) - 0.14, zo + s * 0.05), (xb, deck(xb) + 0.02, zo + s * 0.05),
                    (xa, deck(xa) + 0.02, zo + s * 0.05)]
            m.poly(band, ASHLAR, cp.rgba(PALE, 0.78), facing=(0, 0, s))
        # The arch's stones on this face: each its own shade, standing a little proud.
        half = (EAST - WEST) * 0.5
        rise = CROWN - THICK - SPRING
        n = 17
        for i in range(n):
            a0, a1 = math.pi * i / n, math.pi * (i + 1) / n
            inner = [(MID + half * math.cos(a), SPRING + rise * math.sin(a)) for a in (a0, a1)]
            outer = [(MID + (half + 0.42) * math.cos(a), SPRING + (rise + 0.4) * math.sin(a)) for a in (a0, a1)]
            k = 0.74 + 0.22 * ((i * 5) % 7) / 6.0
            zf = zo + s * 0.07
            m.poly([(inner[0][0], inner[0][1], zf), (inner[1][0], inner[1][1], zf), (outer[1][0], outer[1][1], zf), (outer[0][0], outer[0][1], zf)],
                   ASHLAR, cp.rgba(PALE, k), facing=(0, 0, s))
        # The keystone.
        m.poly([(MID - 0.24, CROWN - THICK, zo + s * 0.12), (MID + 0.24, CROWN - THICK, zo + s * 0.12), (MID + 0.3, CROWN - 0.02, zo + s * 0.12),
                (MID - 0.3, CROWN - 0.02, zo + s * 0.12)], ASHLAR, cp.rgba(PALE, 1.0), facing=(0, 0, s))
        # Cutwaters at the arch's feet.
        for bx, f in ((WEST, 1), (EAST, -1)):
            for za, zb, g in ((zo, zo + s * 0.9, 1), (zo, zo + s * 0.9, -1)):
                x_in = bx + f * 0.02
                pts = [(x_in + g * 0.55, DEEP, za), (x_in, DEEP, zb), (x_in, -0.55, zb - s * 0.35), (x_in + g * 0.55, -0.3, za)]
                m.poly(pts, ASHLAR, [tint(*p) for p in pts], facing=(g, 0.2, s))
    # Under the arch.
    for xa, xb in zip(xs, xs[1:]):
        if soffit(xa) <= DEEP and soffit(xb) <= DEEP:
            continue
        ya, yb = max(soffit(xa), WATER - 0.3), max(soffit(xb), WATER - 0.3)
        for za, zb in ((ROAD_Z - HALF - PARAPET, ROAD_Z), (ROAD_Z, ROAD_Z + HALF + PARAPET)):
            m.poly([(xa, ya, za), (xb, yb, za), (xb, yb, zb), (xa, ya, zb)], ASHLAR, (0.3, 0.31, 0.29, 0.5), facing=(0, -1, 0))
    # The piers: at each end of the parapets and at the crown, standing out a little, capped.
    for x in (WEST - 0.3, MID, EAST + 0.3):
        for s in (-1, 1):
            z0, z1 = sorted((ROAD_Z + s * (HALF - 0.08), ROAD_Z + s * (HALF + PARAPET + 0.1)))
            top = deck(x) + RAIL + 0.32
            cp.slab(m, (x - 0.34, deck(x) - 0.2, z0), (x + 0.34, top, z1), ASHLAR, tint, faces="xXzZ", step=0.8)
            cp.block(m, (x - 0.4, top, z0 - 0.06), (x + 0.4, top + 0.1, z1 + 0.06), ASHLAR, cp.rgba(PALE, 0.9))
            pz = (z0 + z1) * 0.5
            m.poly([(x - 0.4, top + 0.1, z0 - 0.06), (x + 0.4, top + 0.1, z0 - 0.06), (x, top + 0.32, pz)], ASHLAR, cp.rgba(PALE, 0.8), facing=(0, 1, -1))
            m.poly([(x - 0.4, top + 0.1, z1 + 0.06), (x + 0.4, top + 0.1, z1 + 0.06), (x, top + 0.32, pz)], ASHLAR, cp.rgba(PALE, 0.8), facing=(0, 1, 1))
            m.poly([(x - 0.4, top + 0.1, z0 - 0.06), (x - 0.4, top + 0.1, z1 + 0.06), (x, top + 0.32, pz)], ASHLAR, cp.rgba(PALE, 0.7), facing=(-1, 1, 0))
            m.poly([(x + 0.4, top + 0.1, z0 - 0.06), (x + 0.4, top + 0.1, z1 + 0.06), (x, top + 0.32, pz)], ASHLAR, cp.rgba(PALE, 0.7), facing=(1, 1, 0))


def standards(m):
    """On each pier an iron standard: a stem, a scrolled arm toward the road, a hook for the lantern."""
    iron = (0.42, 0.4, 0.4, 1.0)
    for x in (WEST - 0.3, MID, EAST + 0.3):
        for s in (-1, 1):
            z = ROAD_Z + s * (HALF + PARAPET * 0.5)
            foot = deck(x) + RAIL + 0.6
            top = foot + 1.75
            m.tube([(x, foot, z), (x, foot + 0.12, z), (x, top, z)], [0.07, 0.035, 0.028], 6, IRON, iron)
            arm = [(x, top, z), (x, top + 0.14, z - s * 0.14), (x, top + 0.12, z - s * 0.34), (x, top - 0.02, z - s * 0.46), (x, top - 0.14, z - s * 0.46)]
            m.tube(arm, [0.028, 0.026, 0.024, 0.02, 0.016], 5, IRON, iron)
            m.tube([(x, top - 0.5, z), (x, top - 0.2, z - s * 0.16), (x, top + 0.08, z - s * 0.2)], [0.016, 0.016, 0.016], 4, IRON, iron)
            # The lantern on its hook: an iron cage, a cap, four panes of horn with the light behind them.
            lz, hi = z - s * 0.46, top - 0.2
            lo = hi - 0.3
            for y0, y1, w in ((lo - 0.03, lo, 0.11), (hi, hi + 0.025, 0.12)):
                cp.block(m, (x - w, y0, lz - w), (x + w, y1, lz + w), IRON, iron)
            for dx, dz in ((0.1, 0.1), (-0.1, 0.1), (0.1, -0.1), (-0.1, -0.1)):
                cp.block(m, (x + dx - 0.012, lo, lz + dz - 0.012), (x + dx + 0.012, hi, lz + dz + 0.012), IRON, iron, faces="xXzZ")
            for f in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                c0 = (x + f[0] * 0.095, lz + f[1] * 0.095)
                ax = (f[1] * 0.09, f[0] * 0.09)
                pts = [(c0[0] - ax[0], lo, c0[1] - ax[1]), (c0[0] + ax[0], lo, c0[1] + ax[1]), (c0[0] + ax[0], hi, c0[1] + ax[1]), (c0[0] - ax[0], hi, c0[1] - ax[1])]
                m.poly(pts, "window_horn", uvs=[(0, 1), (1, 1), (1, 0), (0, 0)], facing=(f[0], 0, f[1]))
            for f in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                a0 = (x + f[0] * 0.12 - f[1] * 0.12, hi + 0.025, lz + f[1] * 0.12 - f[0] * 0.12)
                a1 = (x + f[0] * 0.12 + f[1] * 0.12, hi + 0.025, lz + f[1] * 0.12 + f[0] * 0.12)
                m.poly([a0, a1, (x, hi + 0.14, lz)], IRON, iron, facing=(f[0], 1, f[1]))


def roadway(m, c):
    """The cobbles over the hump, and the low ramps each side of it."""
    xs = cp.steps(MID - RAMP, MID + RAMP, 0.5)
    zs = cp.steps(ROAD_Z - HALF, ROAD_Z + HALF, 0.5)
    for xa, xb in zip(xs, xs[1:]):
        for za, zb in zip(zs, zs[1:]):
            pts = [(xa, deck(xa), za), (xb, deck(xb), za), (xb, deck(xb), zb), (xa, deck(xa), zb)]
            mud = [0.25 * (1.0 - smoothstep(0.6, 2.2, abs(p[2] - ROAD_Z))) + 0.5 * smoothstep(RAMP - 1.5, RAMP, abs(p[0] - MID)) for p in pts]
            m.poly(pts, "ground_street", [(k, 0.0, 0.0, 0.0) for k in mud], uvs=[(p[0], p[2] - ROAD_Z) for p in pts], facing=(0, 1, 0))
        c.poly([(xa, deck(xa), ROAD_Z - HALF), (xb, deck(xb), ROAD_Z - HALF), (xb, deck(xb), ROAD_Z + HALF), (xa, deck(xa), ROAD_Z + HALF)],
               ASHLAR, facing=(0, 1, 0))
        # Outside the parapets the ramp has a kerb of long stones.
        if xb <= WEST - 0.3 or xa >= EAST + 0.3:
            for s in (-1, 1):
                z0, z1 = sorted((ROAD_Z + s * HALF, ROAD_Z + s * (HALF + 0.3)))
                cp.block(m, (xa, -0.05, z0), (xb, max(deck(xa), deck(xb)) + 0.12, z1), ASHLAR, cp.rgba(PALE, 0.7 + 0.1 * math.sin(xa * 5.0)),
                         faces="xXzZY")
    for s in (-1, 1):
        z0, z1 = sorted((ROAD_Z + s * HALF, ROAD_Z + s * (HALF + PARAPET)))
        c.box((WEST - 0.6, -1.0, z0), (EAST + 0.6, CROWN + RAIL + 0.3, z1), ASHLAR)


def banks(m, c):
    """The brook's walls, their kerbs, and what closes it at each end."""
    tint = cp.stone_tint(WATER, 0.4, seed=8.0, worn=0.95)
    z_n, z_s = ROAD_Z - REACH, ROAD_Z + REACH
    edge_n, edge_s = ROAD_Z - HALF - PARAPET, ROAD_Z + HALF + PARAPET
    for x, out in ((WEST, 1), (EAST, -1)):
        for za, zb in ((z_n, edge_n), (edge_s, z_s)):
            cp.panel(m, (x, za), (x, zb), DEEP, 0.0, (out, 0, 0), RUBBLE, tint, 2.4, 1.25, lean=0.12)
            x0, x1 = sorted((x, x - out * 0.45))
            cp.block(m, (x0, 0.0, za), (x1, 0.28, zb), ASHLAR, cp.rgba(PALE, 0.72), faces="xXzZY")
            c.box((x0, -1.0, za), (x1, 1.2, zb), ASHLAR)
    # The bed, so whoever goes down the steps stands in the water and gets no further than the two ends.
    c.box((WEST - 0.5, DEEP - 0.5, z_n), (EAST + 0.5, DEEP + 0.1, z_s), ASHLAR)
    c.box((WEST - 1.2, DEEP, z_n - 0.5), (EAST + 1.2, 4.0, z_n), ASHLAR)
    c.box((WEST - 1.2, DEEP, z_s), (EAST + 1.2, 4.0, z_s + 0.5), ASHLAR)
    # Each end: a house built over the water on an arch, a window lit over it.
    for z, s in ((z_n, -1), (z_s, 1)):
        over = cp.stone_tint(WATER, 7.5, seed=12.0 + s)
        cp.arch_wall(m, z, WEST - 1.2, EAST + 1.2, DEEP, 4.2, 2.9, WATER + 0.25, 1.9, (0, 0, -s), RUBBLE, over, cx=MID)
        cp.arch_band(m, z, 2.9, WATER + 0.25, 1.9, 0.34, 0.06, (0, 0, -s), ASHLAR, PALE, cx=MID)
        m.poly([(MID - 2.9, DEEP, z + s * 0.05), (MID + 2.9, DEEP, z + s * 0.05), (MID + 2.9, 1.2, z + s * 0.05), (MID - 2.9, 1.2, z + s * 0.05)],
               "window_dark", facing=(0, 0, -s))
        plaster = cp.flat_tint((0.5, 0.48, 0.44))
        cp.panel(m, (WEST - 1.2, z + s * 0.45), (EAST + 1.2, z + s * 0.45), 4.2, 7.4, (0, 0, -s), "plaster_worn", plaster, 2.5, 1.6)
        cp.block(m, (WEST - 1.3, 4.05, min(z, z - s * 0.5)), (EAST + 1.3, 4.3, max(z, z - s * 0.5)), "wood_frame", (0.3, 0.29, 0.28, 1.0))
        za, zb = sorted((z - s * 0.9, z + s * 5.0))
        cp.gable_roof(m, WEST - 1.5, EAST + 1.5, za, zb, 7.4, 10.4, "roof_mossy", (0.7, 0.7, 0.7), along="x", over=0.2)
        cp.lancet(m, (MID + 1.4, z + s * 0.45), 5.0, 0.7, 1.2, (0, 0, -s), "window_candle", frame=0.1)
        cp.lancet(m, (MID - 2.2, z + s * 0.45), 5.2, 0.6, 1.0, (0, 0, -s), "window_dark", frame=0.1)


def stairs(m, c):
    """Steps down to the water along the west bank's wall, north of the bridge, and mooring posts."""
    x0, x1 = WEST, WEST + 1.1
    top_z = ROAD_Z - 3.6
    for i in range(9):
        y = -0.18 * (i + 1)
        z = top_z - 0.34 * i
        cp.block(m, (x0, DEEP if i == 8 else y - 0.5, z - 0.34), (x1, y, z), ASHLAR, cp.rgba(PALE, 0.62 - 0.03 * i + 0.05 * (i % 2)), faces="XzZY")
    # A landing at the water, and the wall under the steps.
    foot = top_z - 0.34 * 9
    cp.block(m, (x0, DEEP, foot - 1.3), (x1, -1.62, foot), ASHLAR, cp.rgba(PALE, 0.42), faces="XzZY")
    c.poly([(x0, 0.0, top_z), (x1, 0.0, top_z), (x1, -1.62, foot), (x0, -1.62, foot)], ASHLAR, facing=(0, 1, 0))
    c.box((x0, DEEP, foot - 1.3), (x1, -1.62, foot), ASHLAR)
    random.seed(5)
    for x, z in ((WEST + 0.5, ROAD_Z - 7.2), (WEST + 0.45, ROAD_Z - 12.5), (EAST - 0.5, ROAD_Z + 9.0), (EAST - 0.4, ROAD_Z + 15.5),
                 (WEST + 0.5, ROAD_Z + 21.0)):
        lean = random.uniform(-0.12, 0.12)
        m.tube([(x, DEEP, z), (x + lean * 0.5, WATER, z), (x + lean, WATER + random.uniform(0.7, 1.3), z + lean)], [0.12, 0.1, 0.08], 6, "wood_frame",
               [(0.2, 0.24, 0.17, 1.0), (0.26, 0.28, 0.22, 1.0), (0.36, 0.34, 0.32, 1.0)], caps=True)


def water(m):
    zs = cp.steps(ROAD_Z - REACH - 0.5, ROAD_Z + REACH + 0.5, 4.0)
    for za, zb in zip(zs, zs[1:]):
        m.poly([(WEST - 0.3, WATER, za), (EAST + 0.3, WATER, za), (EAST + 0.3, WATER, zb), (WEST - 0.3, WATER, zb)], "water_brook",
               uvs=[(WEST, za), (EAST, za), (EAST, zb), (WEST, zb)], facing=(0, 1, 0))


def main():
    porter.reset(53)
    c = porter.Mesh("Bridge-colonly")
    b = porter.Mesh("Bridge")
    bridge(b)
    roadway(b, c)
    b.build()
    i = porter.Mesh("Standards")
    standards(i)
    i.build()
    k = porter.Mesh("Banks")
    banks(k, c)
    stairs(k, c)
    k.build()
    w = porter.Mesh("Water")
    water(w)
    w.build()
    c.build()
    porter.export("env_city_brook")


if __name__ == "__main__":
    main()
