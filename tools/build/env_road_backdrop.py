"""What stands on the horizon of the fields outside Aldgate (night 0): the
far woods and hedges, as two ragged dark bands round the west, north and
south edges of the ground (tools/build/env_road_fields.py).

They are only ever seen far off through rain and haze, so they are flat
shapes with a broken top edge, one material (far_dark), no collision.

Run: tools/build.sh env_road_backdrop
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
from porter import fbm

# The ground's edges (env_road_fields.py), a little inside them.
WEST, EAST, NORTH, SOUTH = -370.0, -119.5, -88.0, 188.0


def edge_path(inset):
    """Along the north edge going west, down the west edge, back east along the south."""
    pts = []
    step = 3.0
    x = EAST
    while x > WEST + inset:
        pts.append((x, NORTH + inset))
        x -= step
    z = NORTH + inset
    while z < SOUTH - inset:
        pts.append((WEST + inset, z))
        z += step
    x = WEST + inset
    while x < EAST:
        pts.append((x, SOUTH - inset))
        x += step
    return pts


def band(m, inset, base, high, seed, shade):
    """A wood's edge: a wall of dark with a ragged top."""
    pts = edge_path(inset)
    tops = []
    for i, (x, z) in enumerate(pts):
        clump = max(fbm(i * 3.0, seed * 10.0, 0.035, 3, seed), -0.2)
        rag = random.uniform(-0.5, 1.0)
        tops.append(base + high * (0.35 + clump) + rag * (0.9 + high * 0.12))
    color = (shade, shade, shade, 1.0)
    for i in range(len(pts) - 1):
        (x0, z0), (x1, z1) = pts[i], pts[i + 1]
        # A crown between each pair of posts: the top edge rises to a point.
        xm, zm = (x0 + x1) * 0.5, (z0 + z1) * 0.5
        peak = max(tops[i], tops[i + 1]) + random.uniform(0.2, 1.6)
        a = m.vert(x0, -1.0, z0, color)
        b = m.vert(x1, -1.0, z1, color)
        c = m.vert(x1, tops[i + 1], z1, color)
        d = m.vert(xm, peak, zm, color)
        e = m.vert(x0, tops[i], z0, color)
        # Both ways round: it is seen from inside the ring only, but cheaply made sure of.
        m.face((a, b, c, d, e), "far_dark")
        m.face((e, d, c, b, a), "far_dark")


def main():
    porter.reset(5)
    m = porter.Mesh("FarWoods")
    band(m, 0.0, 3.0, 7.0, 1.0, 0.8)
    band(m, 9.0, 1.5, 4.5, 2.0, 1.0)
    m.build()
    porter.export("env_road_backdrop")


if __name__ == "__main__":
    main()
