"""The lane's own props (the lane outside the abbey gate).

- lane_bracket: the iron that a house's lantern hangs in. It is built about
  the lamp it holds (game/world/props/lamp.tscn, whose origin is the dish;
  its chains rise 0.52 m to a hook), with the house's wall 0.45 m behind it
  at x = -0.45 and the lane toward +x: a strap up the wall, an arm out from
  it on a curved stay with a curled end, and on the arm an open lantern, four
  bars and a hood, round the dish and its flame (its hood ends 0.22 m above
  the dish, under the lowest jetty's joists). A second arm at the head of
  the strap carries the hook the chains hang from; under a jetty it is lost
  in the joists, and the lantern hangs from the house itself. Nothing is
  solid and it all stands above 2 m.

Run: tools/build.sh prop_lane
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import props
from props import IRON, IRON_C, beam, rgba

WALL = -0.45
HOOK = 0.52
DARK = rgba(IRON_C[:3], 0.7)
SOOT = rgba(IRON_C[:3], 0.4)


def bar(m, pts, r, colour=IRON_C):
    """A forged bar through `pts`, square, as thick as 2 r."""
    m.tube(pts, [r * 1.41] * len(pts), 4, IRON, colour, caps=True)


def lane_bracket(p):
    m = p.hard
    # The strap up the wall, nailed.
    props.strap(m, (WALL, -0.6, 0.0), (WALL, HOOK + 0.08, 0.0), (1, 0, 0), width=0.05, thick=0.01, nails=5)
    # The arm the lantern stands on, and the stay under it.
    arm = -0.172
    beam(m, (WALL + 0.01, arm, 0.0), (0.12, arm, 0.0), 0.022, 0.024, IRON_C, IRON, end_shade=0.8)
    stay = []
    for i in range(9):
        t = math.pi * 0.5 * i / 8
        stay.append((WALL + 0.012 + 0.36 * (1.0 - math.cos(t)), -0.56 + (0.56 + arm - 0.022) * math.sin(t), 0.0))
    bar(m, stay, 0.009)
    # The arm's end curls under.
    curl = []
    for i in range(9):
        a = math.pi * 1.5 * i / 8
        r = 0.04 * (1.0 - 0.55 * i / 8)
        curl.append((0.12 + r * math.sin(a), arm - 0.04 + r * math.cos(a) * 1.0 + (0.04 - r), 0.0))
    bar(m, curl, 0.007)
    # A small scroll in the corner of arm and strap.
    scroll = []
    for i in range(9):
        a = math.pi * 1.6 * i / 8
        r = 0.055 * (1.0 - 0.6 * i / 8)
        scroll.append((WALL + 0.02 + 0.06 - r * math.cos(a), arm + 0.02 + r * math.sin(a) + 0.03 * 0.0, 0.0))
    bar(m, scroll, 0.006)
    # The arm overhead and its hook.
    beam(m, (WALL + 0.01, HOOK + 0.03, 0.0), (0.03, HOOK + 0.03, 0.0), 0.02, 0.022, IRON_C, IRON, end_shade=0.8)
    bar(m, [(0.0, HOOK + 0.02, 0.0), (0.0, HOOK - 0.02, 0.0)], 0.005)
    brace = [(WALL + 0.012, HOOK - 0.2, 0.0), (WALL + 0.07, HOOK - 0.09, 0.0), (WALL + 0.2, HOOK + 0.018, 0.0)]
    bar(m, brace, 0.007)

    # The lantern: a floor, four bars, a rail round their heads and a hood.
    half, foot, head = 0.115, arm + 0.012, 0.135
    m.box((-half, foot, -half), (half, foot + 0.012, half), IRON, DARK)
    for sx in (-1, 1):
        for sz in (-1, 1):
            beam(m, (sx * (half - 0.007), foot + 0.012, sz * (half - 0.007)), (sx * (half - 0.007), head, sz * (half - 0.007)), 0.013, 0.013, IRON_C, IRON, ends="")
    for s in (-1, 1):
        beam(m, (-half, head + 0.007, s * (half - 0.007)), (half, head + 0.007, s * (half - 0.007)), 0.014, 0.014, IRON_C, IRON, end_shade=0.9)
        beam(m, (s * (half - 0.007), head + 0.007, -half), (s * (half - 0.007), head + 0.007, half), 0.014, 0.014, IRON_C, IRON, end_shade=0.9)
        # A low rail to keep the dish from swinging out.
        beam(m, (-half, foot + 0.06, s * (half - 0.007)), (half, foot + 0.06, s * (half - 0.007)), 0.008, 0.008, DARK, IRON, ends="")
        beam(m, (s * (half - 0.007), foot + 0.06, -half), (s * (half - 0.007), foot + 0.06, half), 0.008, 0.008, DARK, IRON, ends="")
    # The hood: four plates up to a vent the chains pass through, sooted inside.
    eave, vent, top = half + 0.035, 0.03, head + 0.085
    low = head + 0.012
    for i in range(4):
        a0, a1 = math.pi * 0.5 * i + math.pi * 0.25, math.pi * 0.5 * (i + 1) + math.pi * 0.25
        c0, s0, c1, s1 = math.cos(a0), math.sin(a0), math.cos(a1), math.sin(a1)
        k = math.sqrt(2.0)
        pts = [(c0 * eave * k, low, s0 * eave * k), (c1 * eave * k, low, s1 * eave * k), (c1 * vent * k, top, s1 * vent * k), (c0 * vent * k, top, s0 * vent * k)]
        out = (c0 + c1, 0.8, s0 + s1)
        m.poly(pts, IRON, IRON_C, facing=out)
        m.poly([(x, y - 0.004, z) for x, y, z in pts], IRON, SOOT, facing=(-out[0], -out[1], -out[2]))
        # The hood's edge, turned down.
        m.poly([pts[0], pts[1], (pts[1][0], low - 0.014, pts[1][2]), (pts[0][0], low - 0.014, pts[0][2])], IRON, DARK, facing=(c0 + c1, 0.0, s0 + s1))
        m.poly([pts[0], pts[1], (pts[1][0], low - 0.014, pts[1][2]), (pts[0][0], low - 0.014, pts[0][2])], IRON, SOOT, facing=(-c0 - c1, 0.0, -s0 - s1))
    props.ring(m, (0.0, top + 0.004, 0.0), (0, 1, 0), r=vent * 1.25, thick=0.005, sides=8)


BUILDERS = {"lane_bracket": lane_bracket}

if __name__ == "__main__":
    props.run(BUILDERS)
