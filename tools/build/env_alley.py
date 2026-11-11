"""The alleys off the street inside Aldgate (night 0, the road in): what
stands in the gap between two houses, so the porter sees down it as the
wagon passes. The houses each side are the alley's walls for their own
depth (9 m); this makes the rest.

In its own space the alley's mouth is at z = 0 on the line of the house
fronts, and it runs back along +z; x = 0 is its middle.

- `a`: a room built across it from house to house, a little way in, on
  two heavy beams, with a shuttered window; the alley goes on under it to
  a wall with a low door and a lit window over the door.
- `b`: washing lines across it, a lean-to against one side, and at its end
  an archway through a wall into a yard, where a light burns.

Both: a floor of trodden mud with rain standing down its middle, yard
walls where the houses end, and things left against the walls. The scenes
(game/world/street/env_alley_*.tscn) add the lights.

Collision: the end walls and the yard walls.

Run: tools/build.sh env_alley
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
import city_parts as cp
from porter import fbm, smoothstep
from prop_street import barrel, crate, sack

HALF = 1.1
# Where the houses end, and where the alley does.
HOUSES = 9.0
END = 13.0
RUBBLE = "stone_rubble"
OAK = "wood_frame"
BOARDS = "wood_boards"
DARK = (0.3, 0.29, 0.28, 1.0)


def floor(m, seed):
    xs = cp.steps(-HALF - 0.15, HALF + 0.15, 0.6)
    zs = cp.steps(0.2, END, 0.64)
    index = {}
    for i, x in enumerate(xs):
        for j, z in enumerate(zs):
            h = 0.05 + 0.03 * smoothstep(0.2, HALF, abs(x)) + 0.015 * fbm(x, z, 0.6, 2, seed)
            pool = (1.0 - smoothstep(0.1, 0.5, abs(x + 0.3 * fbm(z, 0.0, 0.3, 2, seed + 1.0)))) * smoothstep(-0.3, 0.2, fbm(x, z, 0.25, 2, seed + 2.0))
            index[(i, j)] = m.vert(x, h - 0.03 * pool, z, (1.0, 0.0, 0.0, pool), (z, 7.0))
    for i in range(len(xs) - 1):
        for j in range(len(zs) - 1):
            m.face((index[(i, j)], index[(i, j + 1)], index[(i + 1, j + 1)], index[(i + 1, j)]), "ground_street")


def yard_walls(m, c, seed, height=2.7, sides=(-1, 1)):
    tint = cp.stone_tint(0.0, height, seed=seed, worn=0.9)
    for s in sides:
        x0, x1 = sorted((s * HALF, s * (HALF + 0.4)))
        cp.slab(m, (x0, -0.2, HOUSES - 0.1), (x1, height, END), RUBBLE, tint, faces="xXzY", step=1.6)
        cp.block(m, (x0 - 0.05, height, HOUSES - 0.15), (x1 + 0.05, height + 0.12, END), "stone_ashlar", cp.rgba(cp.STONE, 0.75), faces="xXzyY")
        c.box((x0, -0.5, HOUSES - 0.1), (x1, height, END), RUBBLE)


def alley_a(m, c):
    floor(m, 3.0)
    yard_walls(m, c, 2.0)
    # The room across the alley: two beams, joists' ends, plaster and timber over, a shuttered window to the street.
    z0, z1, y0, y1 = 1.9, 4.5, 2.55, 5.3
    for z in (z0, z1 - 0.26):
        cp.block(m, (-HALF - 0.3, y0, z), (HALF + 0.3, y0 + 0.28, z + 0.26), OAK, (0.4, 0.38, 0.36, 1.0))
    m.poly([(-HALF - 0.2, y0 + 0.14, z0), (HALF + 0.2, y0 + 0.14, z0), (HALF + 0.2, y0 + 0.14, z1), (-HALF - 0.2, y0 + 0.14, z1)], BOARDS,
           (0.14, 0.13, 0.13, 1.0), facing=(0, -1, 0))
    x = -HALF + 0.15
    while x < HALF:
        cp.block(m, (x, y0 + 0.28, z0 - 0.1), (x + 0.12, y0 + 0.42, z0 + 0.05), OAK, DARK, faces="xXzy")
        x += 0.42
    daub = cp.flat_tint((0.62, 0.59, 0.52))
    for z, out in ((z0 - 0.06, -1), (z1 + 0.02, 1)):
        cp.panel(m, (-HALF - 0.3, z), (HALF + 0.3, z), y0 + 0.28, y1, (0, 0, out), "plaster_daub", daub, 1.2, 1.4)
        zf = z + out * 0.03
        for xa in (-HALF - 0.3, -0.42, 0.3, HALF + 0.12):
            m.poly([(xa, y0 + 0.28, zf), (xa + 0.16, y0 + 0.28, zf), (xa + 0.16, y1, zf), (xa, y1, zf)], OAK, DARK, facing=(0, 0, out))
        for y in (y0 + 0.4, y1 - 0.16):
            m.poly([(-HALF - 0.3, y, zf), (HALF + 0.3, y, zf), (HALF + 0.3, y + 0.16, zf), (-HALF - 0.3, y + 0.16, zf)], OAK, DARK, facing=(0, 0, out))
        m.poly([(-0.26, 3.6, zf - out * 0.01), (0.3, 3.6, zf - out * 0.01), (0.3, 4.5, zf - out * 0.01), (-0.26, 4.5, zf - out * 0.01)],
               "window_candle" if out > 0 else BOARDS, (0.55, 0.52, 0.48, 1.0), uvs=[(0, 0), (1, 0), (1, 1), (0, 1)], facing=(0, 0, out))
    cp.gable_roof(m, -HALF - 0.4, HALF + 0.4, z0 - 0.3, z1 + 0.3, y1, y1 + 1.1, "roof_plain", (0.7, 0.7, 0.7), along="x", over=0.1)
    # A hook under the first beam for a lantern.
    m.tube([(0.1, y0, z0 + 0.13), (0.1, y0 - 0.14, z0 + 0.13)], [0.014, 0.012], 4, "iron_cart", (0.4, 0.38, 0.37, 1.0))
    # Braces from the house walls up to the beams.
    for s in (-1, 1):
        for z in (z0 + 0.13, z1 - 0.13):
            pts = [(s * HALF, y0 - 0.9, z), (s * HALF, y0, z), (s * (HALF - 0.8), y0, z)]
            for f in (-1, 1):
                m.poly(pts, OAK, DARK, facing=(0, 0, f))
    # The end: a wall, a low door in it, a lit window over the door.
    tint = cp.stone_tint(0.0, 5.0, seed=4.0, worn=0.9)
    cp.panel(m, (-HALF - 0.4, END), (HALF + 0.4, END), 0.0, 5.0, (0, 0, -1), RUBBLE, tint, 1.2, 1.25)
    zf = END - 0.03
    m.poly([(-0.42, 0.0, zf), (0.42, 0.0, zf), (0.42, 1.6, zf), (0.0, 1.95, zf), (-0.42, 1.6, zf)], BOARDS, (0.3, 0.28, 0.26, 1.0), facing=(0, 0, -1))
    cp.lancet(m, (0.1, END), 3.0, 0.55, 0.95, (0, 0, -1), "window_candle", frame=0.09)
    c.box((-HALF - 0.4, -0.5, END), (HALF + 0.4, 5.0, END + 0.4), RUBBLE)
    # Left about: a cask and a broken one, a crate, sacks; a plank bridging the wet.
    random.seed(11)
    barrel(m, -0.72, 5.9, r=0.28, h=0.8)
    barrel(m, 0.66, 10.6, r=0.3, h=0.85, lying=1.3)
    crate(m, (0.35, 0.03, 7.3), (0.95, 0.5, 7.95), 0.2)
    sack(m, -0.7, 11.6, turn=0.4)
    sack(m, -0.62, 12.2, turn=1.3, slump=0.8)
    # Something long under sacking, at the far end.
    sack(m, 0.0, 11.45, r=0.23, length=1.75, turn=0.25, slump=0.9)


def alley_b(m, c):
    floor(m, 9.0)
    yard_walls(m, c, 6.0, height=2.4)
    # Washing lines from wall to wall, and what is still hanging on them, sodden.
    random.seed(7)
    for z, y, cloths in ((2.6, 3.3, ((-0.6, 0.5, 0.9), (0.2, 0.42, 0.6))), (5.8, 3.0, ((-0.3, 0.7, 1.15),)), (7.4, 3.5, ((0.3, 0.4, 0.55), (-0.7, 0.3, 0.4)))):
        pts = [(-HALF, y, z), (-HALF * 0.5, y - 0.07, z), (0.0, y - 0.1, z), (HALF * 0.5, y - 0.07, z), (HALF, y, z)]
        m.tube(pts, [0.012] * 5, 3, "sacking", (0.5, 0.47, 0.42, 1.0))
        for x, w, drop in cloths:
            k = random.uniform(0.3, 0.55)
            col = (k, k * 0.97, k * 0.92, 1.0)
            cloth = [(x, y - 0.09, z), (x + w, y - 0.09, z), (x + w - 0.03, y - 0.09 - drop, z + 0.04), (x + 0.04, y - 0.09 - drop * 0.92, z + 0.05)]
            for f in (-1, 1):
                m.poly(cloth, "painted", col if f < 0 else (k * 0.6, k * 0.58, k * 0.55, 1.0), facing=(0, 0, f))
    # A lean-to against the east side where the houses end: posts, a boarded roof, firewood under it.
    x1, z0, z1 = HALF, 9.2, 11.4
    roof = [(x1, 2.3, z0), (x1, 2.3, z1), (x1 - 1.0, 1.75, z1), (x1 - 1.0, 1.75, z0)]
    m.poly(roof, BOARDS, (0.5, 0.48, 0.46, 1.0), facing=(-0.4, 1, 0))
    m.poly(roof, BOARDS, (0.15, 0.14, 0.14, 1.0), facing=(0.4, -1, 0))
    for z in (z0 + 0.08, z1 - 0.08):
        cp.block(m, (x1 - 1.0, 0.0, z - 0.05), (x1 - 0.9, 1.75, z + 0.05), OAK, DARK, faces="xXzZ")
    for i in range(7):
        y = 0.08 + 0.15 * (i // 2)
        zz = z0 + 0.4 + 0.5 * (i % 3)
        m.tube([(x1 - 0.75, y + 0.07, zz), (x1 - 0.05, y + 0.07, zz + 0.05)], [0.075, 0.07], 5, OAK, (0.5, 0.46, 0.4, 1.0), caps=True)
    # The end: an archway through a wall into a yard, and the yard's back wall behind it.
    tint = cp.stone_tint(0.0, 4.0, seed=7.0, worn=0.9)
    cp.arch_wall(m, 11.6, -HALF - 0.4, HALF + 0.4, 0.0, 3.6, 0.72, 1.45, 0.8, (0, 0, -1), RUBBLE, tint, n=5)
    cp.arch_band(m, 11.6, 0.72, 1.45, 0.8, 0.2, 0.05, (0, 0, -1), "stone_ashlar", cp.STONE, n=5, y0=0.0)
    cp.vault(m, 11.6, 12.0, 0.72, 1.45, 0.8, RUBBLE, lambda x, y, z: (0.4, 0.4, 0.38, 1.0), n=5, step=0.5)
    cp.arch_wall(m, 12.0, -HALF - 0.4, HALF + 0.4, 0.0, 3.6, 0.72, 1.45, 0.8, (0, 0, 1), RUBBLE, tint, n=5)
    cp.block(m, (-HALF - 0.45, 3.6, 11.55), (HALF + 0.45, 3.74, 12.05), "stone_ashlar", cp.rgba(cp.STONE, 0.75))
    back = cp.flat_tint((0.72, 0.68, 0.6))
    cp.panel(m, (-3.2, END + 2.6), (3.2, END + 2.6), 0.0, 4.4, (0, 0, -1), "plaster_worn", back, 1.6, 1.5)
    for x, out in ((-3.2, 1), (3.2, -1)):
        cp.panel(m, (x, 12.0), (x, END + 2.6), 0.0, 4.4, (out, 0, 0), "plaster_worn", back, 1.8, 1.5)
    m.poly([(-3.2, 0.03, 12.0), (3.2, 0.03, 12.0), (3.2, 0.03, END + 2.6), (-3.2, 0.03, END + 2.6)], "ground_street",
           [(1.0, 0.0, 0.0, 0.0)] * 4, uvs=[(12.0, 7.0), (12.0, 7.0), (15.0, 7.0), (15.0, 7.0)], facing=(0, 1, 0))
    for lo, hi in (((-HALF - 0.4, -0.5, 11.6), (-0.72, 3.6, 12.0)), ((0.72, -0.5, 11.6), (HALF + 0.4, 3.6, 12.0)), ((-3.2, -0.5, END + 2.6), (3.2, 4.4, END + 3.0))):
        c.box(lo, hi, RUBBLE)
    random.seed(13)
    barrel(m, -0.74, 4.3, r=0.3, h=0.9)
    barrel(m, -0.7, 8.2, r=0.26, h=0.7)
    crate(m, (-0.98, 0.03, 9.6), (-0.4, 0.55, 10.3), 0.1)
    # An iron arm for a lantern, just inside the mouth.
    m.tube([(HALF, 2.95, 0.9), (HALF - 0.3, 3.0, 0.9), (HALF - 0.34, 2.86, 0.9)], [0.02, 0.018, 0.014], 4, "iron_cart", (0.4, 0.38, 0.37, 1.0))


def main():
    for key, fn in (("a", alley_a), ("b", alley_b)):
        porter.reset(60 + ord(key))
        m = porter.Mesh("Alley")
        c = porter.Mesh("Alley-colonly")
        fn(m, c)
        m.build()
        c.build()
        porter.export("env_alley_" + key)


if __name__ == "__main__":
    main()
