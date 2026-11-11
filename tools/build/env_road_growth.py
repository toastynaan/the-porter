"""What grows on the fields outside Aldgate in late autumn (night 0, the
road in), in the road scene's own coordinates, standing on the ground
tools/build/env_road_fields.py makes:

- dead grass in tufts along the road's verges and ditch banks, thick near
  the road and thinning into the fields;
- reeds and rushes at the water's edge in the ditches and along the city
  ditch under the wall, taller, with seed heads;
- docks and thistles, dark and stiff, here and there in the fields and
  along the headlands.

All of it is one material (growth: its shader bends each blade in the
wind by its UV's height, and lights it as the ground it stands on). A tuft
is eight to eleven flat blades, a reed three. The mesh is cut into lengths of
the road so what is behind the camera is not drawn. No collision.

Run: tools/build.sh env_road_growth
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
from porter import fbm, srgb
from env_road_fields import (ground, yard_amount, ROAD_Z, ROAD_HALF, DITCH, DITCH_HALF, WALL_X, WEST_X, CITY_DITCH_X,
                             CITY_DITCH_HALF, CAUSEWAY_HALF)

CHUNK = 42.0
STRAW = srgb(0.42, 0.39, 0.28)
DEAD = srgb(0.36, 0.33, 0.24)
GREEN = srgb(0.22, 0.27, 0.15)
REED = srgb(0.42, 0.36, 0.22)
DARK = srgb(0.13, 0.12, 0.09)


def mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def blade(m, x, y, z, yaw, lean, height, width, col, tip_k=1.25):
    """One flat blade: wide at the root, a point at the tip, leaning out."""
    c, s = math.cos(yaw), math.sin(yaw)
    ax, az = -s * width * 0.5, c * width * 0.5
    tx, tz = x + c * lean * height, z + s * lean * height
    root = (col[0] * 0.45, col[1] * 0.45, col[2] * 0.45, 1.0)
    tip = (col[0] * tip_k, col[1] * tip_k, col[2] * tip_k, 1.0)
    a = m.vert(x - ax, y - 0.05, z - az, root, (0.0, 0.0))
    b = m.vert(x + ax, y - 0.05, z + az, root, (1.0, 0.0))
    t = m.vert(tx, y + height, tz, tip, (0.5, height))
    m.face((a, b, t), "growth")


def tuft(m, x, z, size, col):
    y, _mask = ground(x, z)
    n = random.randint(8, 11)
    for i in range(n):
        yaw = math.tau * i / n + random.uniform(-0.5, 0.5)
        blade(m, x + math.cos(yaw) * 0.07, y, z + math.sin(yaw) * 0.07, yaw, random.uniform(0.1, 0.75), size * random.uniform(0.45, 1.0),
              random.uniform(0.03, 0.055) * (0.7 + size), mix(col, DEAD, random.uniform(0.0, 0.6)))


def reed(m, x, z, height):
    y, _mask = ground(x, z)
    y = max(y, -2.2)
    for i in range(random.randint(3, 5)):
        ox, oz = random.uniform(-0.12, 0.12), random.uniform(-0.12, 0.12)
        h = height * random.uniform(0.7, 1.0)
        yaw = random.uniform(0.0, math.tau)
        blade(m, x + ox, y, z + oz, yaw, random.uniform(0.03, 0.2), h, 0.05, mix(REED, DEAD, random.uniform(0.0, 0.5)), 1.0)
        if random.random() < 0.5:
            # A seed head: a dark spindle at the top.
            tx, tz = x + ox + math.cos(yaw) * 0.12 * h, z + oz + math.sin(yaw) * 0.12 * h
            a = m.vert(tx - 0.035, y + h * 0.78, tz, DARK, (0.0, h * 0.78))
            b = m.vert(tx + 0.035, y + h * 0.78, tz, DARK, (1.0, h * 0.78))
            t = m.vert(tx, y + h * 1.08, tz, DARK, (0.5, h * 1.08))
            m.face((a, b, t), "growth")


def dock(m, x, z):
    """A dead dock or thistle: a few stiff dark stalks."""
    y, _mask = ground(x, z)
    for i in range(random.randint(2, 4)):
        yaw = random.uniform(0.0, math.tau)
        blade(m, x, y, z, yaw, random.uniform(0.0, 0.25), random.uniform(0.6, 1.2), 0.07, mix(DARK, DEAD, random.uniform(0.0, 0.4)), 0.9)


def scatter(x0, x1):
    """Everything growing between x0 and x1."""
    m = porter.Mesh("Growth%03d" % int(-x0))
    span = x1 - x0
    # Verges and ditch banks, both sides of the road.
    for _ in range(int(span * 22)):
        x = random.uniform(x0, x1)
        d = ROAD_HALF + 0.15 + abs(random.gauss(0.0, 2.6))
        if d > 13.0:
            continue
        z = ROAD_Z + random.choice((-1, 1)) * d
        in_water = abs(d - DITCH) < DITCH_HALF * 0.45
        if in_water or (abs(x - CITY_DITCH_X) < CITY_DITCH_HALF and d > CAUSEWAY_HALF):
            continue
        if x > WALL_X - 1.0:
            continue
        thick = 0.55 + 0.45 * fbm(x, z, 0.08, 2, 3.0)
        if random.random() > thick:
            continue
        tuft(m, x, z, random.uniform(0.3, 0.75) * (1.15 if d > DITCH - 1.0 else 0.8), mix(STRAW, GREEN, random.uniform(0.0, 0.5)))
    # Reeds at the ditches' edges.
    for _ in range(int(span * 5)):
        x = random.uniform(x0, x1)
        if fbm(x, 0.0, 0.05, 2, 9.0) < -0.1 or abs(x - CITY_DITCH_X) < CITY_DITCH_HALF + 1.0 or x > WALL_X - 1.0:
            continue
        side = random.choice((-1, 1))
        z = ROAD_Z + side * (DITCH + random.choice((-1, 1)) * DITCH_HALF * random.uniform(0.35, 0.7))
        reed(m, x, z, random.uniform(0.9, 1.7))
    # Out in the fields: thin tufts along the furrows, docks on the headlands.
    for _ in range(int(span * 16)):
        x = random.uniform(x0, x1)
        d = 9.0 + abs(random.gauss(0.0, 22.0))
        z = ROAD_Z + random.choice((-1, 1)) * d
        if d > 70.0 or x > WALL_X - 1.0 or abs(x - CITY_DITCH_X) < CITY_DITCH_HALF:
            continue
        _h, mask = ground(x, z)
        if mask[3] > 0.3:
            continue
        if mask[2] > 0.5 and random.random() < 0.8:
            continue
        if random.random() < 0.18:
            dock(m, x, z)
        else:
            tuft(m, x, z, random.uniform(0.25, 0.6), mix(STRAW, GREEN, random.uniform(0.2, 0.8)))
    # The city ditch: reeds thick along both its banks.
    if x0 < CITY_DITCH_X + CITY_DITCH_HALF and x1 > CITY_DITCH_X - CITY_DITCH_HALF:
        for _ in range(420):
            z = ROAD_Z + random.choice((-1, 1)) * random.uniform(CAUSEWAY_HALF + 0.6, 60.0)
            x = CITY_DITCH_X + random.choice((-1, 1)) * CITY_DITCH_HALF * random.uniform(0.42, 0.9)
            if not x0 <= x < x1:
                continue
            if random.random() < 0.6:
                reed(m, x, z, random.uniform(1.2, 2.2))
            else:
                tuft(m, x, z, random.uniform(0.5, 0.9), mix(STRAW, GREEN, random.uniform(0.0, 0.6)))
    if m.faces:
        m.build()


def main():
    porter.reset(13)
    x = -330.0
    while x < WALL_X:
        scatter(x, min(x + CHUNK, WALL_X))
        x += CHUNK
    porter.export("env_road_growth")


if __name__ == "__main__":
    main()
