"""A gibbet: an iron cage hung from a timber arm, with what is left of a
man in it, as a city hung them by its gates for the road to see (night 0,
Aldgate).

In its own space the arm is fixed to a wall at the origin and reaches out
along -z; the cage hangs under its end. The cage is its own object (Cage),
turning about the top of its chain, so the scene can swing it
(game/world/props/prop_gibbet.tscn).

No collision: it hangs out of reach.

Run: tools/build.sh prop_gibbet
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter

REACH = 2.3
IRON = (0.42, 0.4, 0.38, 1.0)
OAK = (0.42, 0.4, 0.37, 1.0)


def hoop(m, y, r, sides=10, thick=0.014):
    pts = [(math.cos(math.tau * i / sides) * r, y, -REACH + math.sin(math.tau * i / sides) * r) for i in range(sides + 1)]
    for a, b in zip(pts, pts[1:]):
        m.tube([a, b], [thick, thick], 4, "iron_cart", IRON)


def main():
    porter.reset(13)
    a = porter.Mesh("Arm")
    a.box((-0.09, -0.09, -REACH - 0.25), (0.09, 0.09, 0.3), "wood_medieval", OAK)
    # A brace under it, back to the wall.
    a.tube([(0.0, -1.3, 0.05), (0.0, -0.08, -1.5)], [0.07, 0.07], 4, "wood_medieval", OAK)
    a.box((-0.1, -1.5, 0.0), (0.1, 0.2, 0.16), "wood_medieval", OAK)
    a.build()
    c = porter.Mesh("Cage")
    # The chain, then the cage: a man's shape in iron bands.
    c.tube([(0.0, -0.09, -REACH), (0.0, -0.75, -REACH)], [0.018, 0.018], 4, "iron_cart", IRON)
    top, foot = -0.75, -2.65
    profile = ((top, 0.05), (top - 0.14, 0.17), (top - 0.38, 0.19), (top - 0.52, 0.13), (top - 0.75, 0.27), (top - 1.2, 0.25),
               (top - 1.6, 0.2), (foot, 0.15))
    for y, r in profile[1:]:
        hoop(c, y, r)
    for i in range(6):
        ang = math.tau * i / 6
        pts = [(math.cos(ang) * r, y, -REACH + math.sin(ang) * r) for y, r in profile]
        c.tube(pts, [0.011] * len(pts), 4, "iron_cart", IRON)
    # What is in it: slumped, wrapped in what he died in, the head fallen forward.
    rag = porter.srgb(0.13, 0.12, 0.11)
    body = [(0.0, foot + 0.05, -REACH), (0.0, top - 1.2, -REACH + 0.02), (0.0, top - 0.75, -REACH + 0.03), (0.02, top - 0.55, -REACH),
            (0.03, top - 0.47, -REACH - 0.04), (0.05, top - 0.32, -REACH - 0.09), (0.05, top - 0.2, -REACH - 0.1)]
    c.tube(body, [0.07, 0.17, 0.2, 0.1, 0.07, 0.105, 0.03], 7, "painted", [rag] * len(body), caps=True, squash=(1.0, 0.75))
    c.build(origin=(0.0, -0.09, -REACH))
    porter.export("prop_gibbet")


if __name__ == "__main__":
    main()
