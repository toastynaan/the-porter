"""The street inside Aldgate (night 0, the road in): the ground from under
the gate to the brook's bank, in the road scene's
coordinates (game/world/road/env_road.tscn; the street runs along x at
z = 47).

Cobbles, with mud down the middle where the carts go and against the
houses, a kennel (the gutter) down the middle with water in it, and every
hollow full of rain. The ground's shader
(game/world/materials/real/ground_street.gdshader) reads each vertex's
colour as masks: red mud, alpha standing water. UV is (metres along the
street, metres to the side of its middle), for the wheel ruts.

Run: tools/build.sh env_aldgate_street
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
from porter import fbm, smoothstep

ROAD_Z = 47.0
# From the fields' edge under the gate to the brook's bank (tools/build/env_city_brook.py), how far each
# side of the street its ground is made (the houses stand on the rest; the alleys have their own floors,
# tools/build/env_alley.py), and how far each side it can be walked on.
WEST_X, EAST_X = -119.5, -80.0
HALF = 3.5
WALK = 17.0
# The house fronts stand this far from the middle.
FRONT = 3.2


def ground(x, z):
    d = abs(z - ROAD_Z)
    # A shallow fall to the kennel in the middle, and a little unevenness.
    h = 0.05 * smoothstep(0.2, FRONT, d) + 0.015 * fbm(x, z, 0.5, 2, 4.0)
    kennel = 1.0 - smoothstep(0.1, 0.45, abs(d - 0.0 + 0.25 * fbm(x, 0.0, 0.15, 2, 2.0)))
    h -= 0.05 * kennel
    # Mud: the cart track, drifts against the houses, and the trampled ground just inside the gate.
    track = 1.0 - smoothstep(1.4, 2.6, d + 0.6 * fbm(x, z, 0.2, 2, 5.0))
    drift = smoothstep(FRONT - 1.0, FRONT - 0.1, d + 0.5 * fbm(x, z, 0.3, 2, 6.0))
    inside = 1.0 - smoothstep(-117.0, -110.0, x)
    mud = max(track * 0.8, drift, inside)
    return h, (mud, 0.0, 0.0, kennel * smoothstep(-0.2, 0.3, fbm(x, z, 0.12, 2, 7.0) + 0.25))


# Beyond the brook the street runs on a little and turns south out of sight:
# its two lengths, as (x from, x to, z from, z to). The wagon is on it only
# as the night goes dark (docs/places/prologue.md).
BEYOND = ((-72.0, -56.8, 43.8, 50.2), (-63.0, -56.8, 50.2, 64.6))


def beyond(m, c):
    step = 0.55
    for x0, x1, z0, z1 in BEYOND:
        nx, nz = int(round((x1 - x0) / step)), int(round((z1 - z0) / step))
        index = {}
        for i in range(nx + 1):
            for j in range(nz + 1):
                x, z = x0 + (x1 - x0) * i / nx, z0 + (z1 - z0) * j / nz
                h = 0.02 + 0.015 * fbm(x, z, 0.5, 2, 4.0)
                mud = smoothstep(-0.25, 0.35, fbm(x, z, 0.2, 2, 5.0))
                pool = smoothstep(0.15, 0.4, fbm(x, z, 0.16, 2, 7.0))
                index[(i, j)] = m.vert(x, h - 0.02 * pool, z, (mud, 0.0, 0.0, pool), (x, 7.0))
        for i in range(nx):
            for j in range(nz):
                m.face((index[(i, j)], index[(i, j + 1)], index[(i + 1, j + 1)], index[(i + 1, j)]), "ground_street")
        c.quad((x0, 0.0, z0), (x0, 0.0, z1), (x1, 0.0, z1), (x1, 0.0, z0), "ground_street")


def main():
    porter.reset(3)
    step = 0.5
    nx = int((EAST_X - WEST_X) / step)
    nz = int(2 * HALF / step)
    m = porter.Mesh("Street")
    index = {}
    for i in range(nx + 1):
        for j in range(nz + 1):
            x, z = WEST_X + i * step, ROAD_Z - HALF + j * step
            h, mask = ground(x, z)
            index[(i, j)] = m.vert(x, h, z, mask, (x, z - ROAD_Z))
    for i in range(nx):
        for j in range(nz):
            m.face((index[(i, j)], index[(i, j + 1)], index[(i + 1, j + 1)], index[(i + 1, j)]), "ground_street")
    m.build(smooth=True)
    c = porter.Mesh("Ground-colonly")
    c.quad((WEST_X, 0.0, ROAD_Z - WALK), (WEST_X, 0.0, ROAD_Z + WALK), (EAST_X, 0.0, ROAD_Z + WALK), (EAST_X, 0.0, ROAD_Z - WALK), "ground_street")
    b = porter.Mesh("Beyond")
    beyond(b, c)
    b.build(smooth=True)
    c.build()
    porter.export("env_aldgate_street")


if __name__ == "__main__":
    main()
