"""A watch fire: an iron fire basket on three legs, heaped with coals, as
stood by a city gate at dusk (night 0, Aldgate). About 1.2 m to the rim.

The coals are their own material (embers), and the flames are an object of
their own (Flame, crossed sheets with the flame shader on them); the
scene (game/world/props/prop_brazier.tscn) adds the light and the sparks.

Collision: a post, so nothing walks through it.

Run: tools/build.sh prop_brazier
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter

IRON = (0.5, 0.48, 0.46, 1.0)


def ring(m, y, r, thick, sides=12):
    pts = [(math.cos(math.tau * i / sides) * r, y, math.sin(math.tau * i / sides) * r) for i in range(sides + 1)]
    for a, b in zip(pts, pts[1:]):
        m.tube([a, b], [thick, thick], 4, "iron_cart", IRON)


def main():
    porter.reset(9)
    m = porter.Mesh("Brazier")
    # Three legs, splayed, meeting under the basket; a ring low down to tie them.
    for i in range(3):
        a = math.tau * i / 3 + 0.4
        foot = (math.cos(a) * 0.42, 0.0, math.sin(a) * 0.42)
        top = (math.cos(a) * 0.2, 0.82, math.sin(a) * 0.2)
        m.tube([foot, top], [0.022, 0.02], 4, "iron_cart", IRON)
    ring(m, 0.3, 0.34, 0.012, 9)
    # The basket: two hoops and the bars between, wider at the rim.
    ring(m, 0.8, 0.22, 0.018)
    ring(m, 1.0, 0.31, 0.014)
    ring(m, 1.2, 0.37, 0.02)
    for i in range(12):
        a = math.tau * i / 12
        m.tube([(math.cos(a) * 0.22, 0.8, math.sin(a) * 0.22), (math.cos(a) * 0.37, 1.2, math.sin(a) * 0.37)], [0.012, 0.012], 4,
               "iron_cart", IRON)
    m.poly([(math.cos(math.tau * i / 8) * 0.22, 0.8, math.sin(math.tau * i / 8) * 0.22) for i in range(8)], "iron_cart", IRON,
           facing=(0, -1, 0))
    m.build()
    # The coals: a rough heap of lumps, glowing.
    c = porter.Mesh("Coals")
    for i in range(16):
        a = random.uniform(0.0, math.tau)
        d = random.uniform(0.0, 0.25)
        y = 1.02 + (0.25 - d) * 0.6 + random.uniform(-0.03, 0.04)
        s = random.uniform(0.07, 0.12)
        heat = random.uniform(0.25, 1.0)
        x, z = math.cos(a) * d, math.sin(a) * d
        c.box((x - s, y - s * 0.7, z - s), (x + s, y + s * 0.7, z + s), "embers", (heat, heat, heat, 1.0))
    c.build()
    # The flames: three upright sheets through the middle of the heap.
    f = porter.Mesh("Flame")
    for i in range(3):
        a = math.pi * i / 3
        dx, dz = math.cos(a) * 0.36, math.sin(a) * 0.36
        ids = f.quad((-dx, 1.08, -dz), (dx, 1.08, dz), (dx, 2.05, dz), (-dx, 2.05, -dz), "flame",
                     uvs=[(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
    f.build()
    col = porter.Mesh("Post-colonly")
    col.box((-0.3, 0.0, -0.3), (0.3, 1.3, 0.3), "iron_cart")
    col.build()
    porter.export("prop_brazier")


if __name__ == "__main__":
    main()
