"""The city behind the wall (night 0, the road in), in the road scene's
coordinates (game/world/road/env_road.tscn; the wall stands along z at
x = -118, the street runs in along x at z = 47): what shows over the wall
from the fields, and over the roofs from the street.

- Near: the backs of the wards each side of the street. Rows of houses
  with their roofs every way, a candle in a window here and there; parish
  churches among them with square towers, some with a short lead spire,
  a light in a belfry.
- Far: more church towers further in, and St Paul's on its hill, its
  spire the tallest thing in England. They are only ever seen through
  rain and distance, against the last pale break in the cloud, so they
  are flat shapes in the colour of that distance (far_city: unlit, and
  the fog leaves it alone; the further, the paler). They are their own
  object: the scene hides it once the wagon is near the lane.

No collision: nothing here can be reached.

Run: tools/build.sh env_city_skyline
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
import city_parts as cp

WALL_X = -116.5
STREET_Z = 47.0
# Nothing near stands in the street's own ground, or east of this (the lane's).
KEEP_OFF = (30.0, 64.0)
EAST = -75.0


def house(m, x, z, w, d, h, along, lit):
    wall = random.choice(((0.5, 0.48, 0.42), (0.44, 0.44, 0.43), (0.5, 0.44, 0.36)))
    k = random.uniform(0.75, 1.0)
    tint = cp.flat_tint(wall, k)
    cp.slab(m, (x - w * 0.5, -0.5, z - d * 0.5), (x + w * 0.5, h, z + d * 0.5), "plaster_daub", tint, faces="xXzZ", step=20.0)
    span = d if along == "x" else w
    ridge = h + span * 0.5 * random.uniform(0.95, 1.25)
    cp.gable_roof(m, x - w * 0.5, x + w * 0.5, z - d * 0.5, z + d * 0.5, h, ridge, "roof_tiles",
                  (0.78 * k, 0.76 * k, 0.74 * k), along=along, over=0.25)
    for s in (-1, 1):
        if along == "x":
            pts = [(x + s * w * 0.5, h, z - d * 0.5), (x + s * w * 0.5, h, z + d * 0.5), (x + s * w * 0.5, ridge, z)]
            m.poly(pts, "plaster_daub", cp.rgba(wall, k * 0.9), facing=(s, 0, 0))
        else:
            pts = [(x - w * 0.5, h, z + s * d * 0.5), (x + w * 0.5, h, z + s * d * 0.5), (x, ridge, z + s * d * 0.5)]
            m.poly(pts, "plaster_daub", cp.rgba(wall, k * 0.9), facing=(0, 0, s))
    if lit:
        # A candle in an upper window, toward the wall.
        y = h - random.uniform(1.4, 2.0)
        zz = z + random.uniform(-d * 0.3, d * 0.3)
        xf = x - w * 0.5 - 0.03
        m.poly([(xf, y, zz - 0.35), (xf, y, zz + 0.35), (xf, y + 0.8, zz + 0.35), (xf, y + 0.8, zz - 0.35)], "window_candle",
               uvs=[(0, 0), (1, 0), (1, 1), (0, 1)], facing=(-1, 0, 0))


def church(m, x, z, w, h, spire, nave, lit, mat="stone_rubble", plain=None):
    """A parish church: a square tower with battlements and perhaps a
    spire, and its nave running east from it."""
    tint = plain or cp.stone_tint(0.0, h + 1.5, clean=(0.62, 0.62, 0.6), seed=x)
    half = w * 0.5
    cp.slab(m, (x - half, -0.5, z - half), (x + half, h, z + half), mat, tint, faces="xXzZY", step=3.0)
    for a, b, out in (((x - half, z - half), (x + half, z - half), (0, 0, -1)), ((x + half, z + half), (x - half, z + half), (0, 0, 1)),
                      ((x - half, z + half), (x - half, z - half), (-1, 0, 0)), ((x + half, z - half), (x + half, z + half), (1, 0, 0))):
        cp.battlements(m, a, b, h, out, mat, tint, thick=0.4, wall=0.7, merlon=0.8, width=0.9, gap=0.7)
    roof = mat if plain else "roof_slates"
    lead = plain(0, 0, 0) if plain else (0.7, 0.72, 0.76, 1.0)
    if spire > 0:
        cp.spire(m, x, z, h + 0.4, h + spire, half * 0.8, roof, lead)
    else:
        # Pinnacles at the corners.
        for sx in (-1, 1):
            for sz in (-1, 1):
                cp.spire(m, x + sx * (half - 0.3), z + sz * (half - 0.3), h + 1.3, h + 3.4, 0.38, roof, lead, sides=4)
    if not plain:
        # The belfry's openings, and a light in one if the ringers are up there.
        for out, c in (((-1, 0, 0), (x - half, z)), ((0, 0, -1), (x, z - half)), ((0, 0, 1), (x, z + half))):
            glass = "window_candle" if lit and out[0] == -1 else "window_dark"
            cp.lancet(m, c, h - 4.2, 0.9, 2.4, out, glass, frame=0.2)
    # The nave, east of the tower.
    nh = h * 0.42
    cp.slab(m, (x + half, -0.5, z - half * 1.25), (x + half + nave, nh, z + half * 1.25), mat, tint, faces="XzZ", step=4.0)
    cp.gable_roof(m, x + half, x + half + nave, z - half * 1.25, z + half * 1.25, nh, nh + half * 1.5, roof, lead,
                  along="x", over=0.2, under=lead[:3] if plain else (0.25, 0.25, 0.25))


def near(m):
    for row, x in enumerate((-109.5, -99.0, -88.5, -79.0)):
        z = -86.0
        while z < 186.0:
            w = random.uniform(5.0, 8.0)
            d = random.uniform(5.5, 8.5)
            zc = z + d * 0.5
            z += d + random.choice((0.0, 0.0, 0.3, 1.6))
            if KEEP_OFF[0] - d * 0.5 < zc < KEEP_OFF[1] + d * 0.5:
                continue
            xc = x + random.uniform(-1.2, 1.2)
            if xc + w * 0.5 > EAST or any(abs(xc - cx) < 9.0 and abs(zc - cz) < 9.0 for cx, cz in CHURCHES):
                continue
            h = random.choice((5.6, 5.9, 8.4, 8.6, 8.9, 9.4))
            house(m, xc, zc, w, d, h, random.choice(("x", "z", "z")), random.random() < 0.16)


# The parish churches near the wall: x, z.
CHURCHES = ((-101.0, 16.0), (-92.0, -42.0), (-104.0, 92.0), (-86.0, 141.0), (-98.0, -78.0))


def main():
    porter.reset(1420)
    m = porter.Mesh("Near")
    near(m)
    specs = ((6.0, 23.0, 0.0, 16.0, True), (5.2, 19.0, 11.0, 13.0, False), (6.4, 26.0, 0.0, 18.0, False),
             (5.0, 18.0, 9.0, 12.0, True), (5.6, 21.0, 0.0, 14.0, False))
    for (x, z), (w, h, spire, nave, lit) in zip(CHURCHES, specs):
        church(m, x, z, w, h, spire, nave, lit)
    m.build()
    f = porter.Mesh("Far")
    dark = cp.flat_tint(porter.srgb(0.06, 0.066, 0.082)[:3])
    haze = porter.srgb(0.085, 0.095, 0.118)[:3]
    far = cp.flat_tint(haze)
    for x, z, w, h, spire, nave in ((-20.0, -70.0, 7.0, 27.0, 14.0, 20.0), (30.0, 130.0, 8.0, 30.0, 0.0, 22.0),
                                    (60.0, -120.0, 7.0, 26.0, 16.0, 20.0), (-10.0, 185.0, 7.0, 24.0, 12.0, 18.0),
                                    (95.0, 60.0, 8.0, 31.0, 0.0, 24.0), (10.0, -170.0, 7.0, 25.0, 0.0, 18.0)):
        church(f, x, z, w, h, spire, nave, False, mat="far_city", plain=dark)
    # St Paul's: the long roof, the transepts, the tower and the spire.
    px, pz = 250.0, -85.0
    cp.slab(f, (px - 70.0, -1.0, pz - 13.0), (px + 90.0, 24.0, pz + 13.0), "far_city", far, faces="xXzZ", step=200.0)
    cp.gable_roof(f, px - 70.0, px + 90.0, pz - 13.0, pz + 13.0, 24.0, 36.0, "far_city", haze, along="x", over=0.0, under=haze)
    cp.slab(f, (px - 12.0, -1.0, pz - 40.0), (px + 12.0, 24.0, pz + 40.0), "far_city", far, faces="xXzZ", step=200.0)
    cp.gable_roof(f, px - 12.0, px + 12.0, pz - 40.0, pz + 40.0, 24.0, 36.0, "far_city", haze, along="z", over=0.0, under=haze)
    cp.slab(f, (px - 9.0, 20.0, pz - 9.0), (px + 9.0, 62.0, pz + 9.0), "far_city", far, faces="xXzZY", step=200.0)
    cp.spire(f, px, pz, 62.0, 128.0, 8.0, "far_city", haze)
    for sx in (-1, 1):
        for sz in (-1, 1):
            cp.spire(f, px + sx * 8.0, pz + sz * 8.0, 62.0, 74.0, 1.6, "far_city", haze, sides=4)
    f.build()
    porter.export("env_city_skyline")


if __name__ == "__main__":
    main()
