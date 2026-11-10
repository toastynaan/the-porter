"""London's wall each side of Aldgate (night 0, the road in), in the gate's
own space (tools/build/env_aldgate.py): the wall runs along x, the country
is at -z, the city at +z, and the gate fills the gap from x = -9 to 9.

- The wall: ragstone rubble laced with bands of old tile, battered at the
  foot, 8 m to its walk, battlements on the country side. Damp climbs it
  from the ditch and dark runs down it from the parapet. Merlons have
  fallen here and there, and one stretch to the north has come down to
  half its height and never been mended.
- Bastions: half-round towers standing out from it every fifty or sixty
  metres. One has a candle in a slit: an anchorite's cell.
- The stair up to the walk, against the city side, south of the gate.
- The causeway that carries the road over the city ditch (the ditch
  itself is the ground's: tools/build/env_road_fields.py), with a low
  parapet each side.

Collision: the wall, the bastions, the stair, the causeway's parapets.

Run: tools/build.sh env_city_wall
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
import city_parts as cp
from porter import fbm, smoothstep

# Along the wall: its two ends, and the gap the gatehouse fills.
SOUTH, NORTH = -143.0, 137.0
GAP = 9.0
# Its faces (country, city), the height of its walk, and how deep its foot goes.
OUT_Z, IN_Z = -1.5, 1.5
WALK = 8.0
FOOT = -2.4
# Bastions: where along the wall, and whether a candle burns in it.
BASTIONS = ((-112.0, False), (-56.0, True), (52.0, False), (109.0, False))
BASTION_R, BASTION_TOP = 3.4, 10.3
# The stretch that has come down: its middle, half its length, how far down.
RUIN = (78.0, 11.0, 3.4)
# The causeway over the ditch: half the road's width to the parapet, and its z from and to.
CAUSEWAY = (4.3, -18.0, -5.5)

RUBBLE = "stone_rubble"
ASHLAR = "stone_blocks"


def fallen(x):
    """How far the wall's top is down at x."""
    mid, half, deep = RUIN
    d = abs(x - mid) / half
    if d >= 1.0:
        return 0.0
    return deep * (1.0 - d * d) * (0.75 + 0.35 * fbm(x, 0.0, 0.45, 2, 2.0)) + 0.25


def wall(m, x0, x1, seed):
    tint = cp.stone_tint(0.0, WALK + 1.0, seed=seed)
    xs = cp.steps(x0, x1, 2.3)
    for xa, xb in zip(xs, xs[1:]):
        fa, fb = fallen(xa), fallen(xb)
        whole = fa == 0.0 and fb == 0.0
        top = lambda u, fa=fa, fb=fb: WALK - (fa + (fb - fa) * u)
        # The country side: the battered foot, then the face.
        cp.panel(m, (xa, OUT_Z), (xb, OUT_Z), FOOT, 1.7, (0, 0, -1), RUBBLE, tint, 2.3, 1.4, lean=0.55)
        cp.panel(m, (xa, OUT_Z), (xb, OUT_Z), 1.7, WALK, (0, 0, -1), RUBBLE, tint, 2.3, 1.3, top=top)
        # The city side.
        cp.panel(m, (xa, IN_Z), (xb, IN_Z), -0.6, WALK, (0, 0, 1), RUBBLE, tint, 2.3, 1.4, top=top)
        # The walk, or the broken top.
        ya, yb = top(0.0), top(1.0)
        back = OUT_Z + (0.5 if whole else 0.0)
        pts = [(xa, ya, back), (xb, yb, back), (xb, yb, IN_Z), (xa, ya, IN_Z)]
        m.poly(pts, RUBBLE, [tint(*p) for p in pts], facing=(0, 1, 0))
        # Bands of tile through the rubble.
        for y in (2.6, 4.5, 6.4):
            if min(ya, yb) > y + 0.6:
                m.poly([(xa, y, OUT_Z - 0.03), (xb, y, OUT_Z - 0.03), (xb, y + 0.17, OUT_Z - 0.03), (xa, y + 0.17, OUT_Z - 0.03)],
                       "tile_course", cp.rgba((0.8, 0.74, 0.7), 0.85 + 0.15 * fbm(xa, y, 0.2, 2, 4.0)), facing=(0, 0, -1))
    # Battlements, where the wall is whole. A merlon is gone here and there.
    def gone(x_from):
        def skip(d):
            x = x_from + d
            return fallen(x) > 0.0 or (math.sin(x * 12.9898 + seed) * 43758.5453) % 1.0 < 0.1
        return skip
    runs = []
    mid, half, _deep = RUIN
    if x0 < mid - half < x1:
        runs = [(x0, mid - half), (mid + half, x1)]
    else:
        runs = [(x0, x1)]
    for a, b in runs:
        cp.battlements(m, (a, OUT_Z), (b, OUT_Z), WALK, (0, 0, -1), RUBBLE, tint, skip=gone(a))


def bastion(m, bx, candle, seed):
    r, top = BASTION_R, BASTION_TOP
    tint = cp.stone_tint(0.0, top + 1.6, seed=seed)
    arc = (math.pi, math.tau)
    sides = 20
    cp.drum(m, bx, OUT_Z, [FOOT, 2.0, top - 0.9, top - 0.45, top], [r + 0.6, r, r, r + 0.28, r + 0.28], sides, RUBBLE, tint, arc)
    for y in (2.6, 4.5, 6.4, 8.6):
        cp.drum(m, bx, OUT_Z, [y, y + 0.17], [r + 0.025, r + 0.025], sides, "tile_course", cp.flat_tint((0.8, 0.74, 0.7)), arc)
    cp.disc(m, bx, OUT_Z, top, r + 0.28, sides, RUBBLE, cp.STONE_DARK, arc=arc)
    cp.ring_battlements(m, bx, OUT_Z, top, r + 0.28, sides, RUBBLE, tint, arc=arc, broken=(int(seed) % 5,))
    # Its back, above the wall's walk.
    cp.panel(m, (bx - r - 0.28, OUT_Z), (bx + r + 0.28, OUT_Z), WALK, top + 0.9, (0, 0, 1), RUBBLE, tint)
    m.poly([(bx - r - 0.28, top + 0.9, OUT_Z), (bx + r + 0.28, top + 0.9, OUT_Z), (bx + r + 0.28, top + 0.9, OUT_Z - 0.4),
            (bx - r - 0.28, top + 0.9, OUT_Z - 0.4)], RUBBLE, cp.rgba(cp.STONE_DARK), facing=(0, 1, 0))
    step = math.pi / 10
    for a, y, lit in ((-90, 4.9, candle), (-90, 8.0, False), (-145, 6.4, False), (-35, 6.4, False)):
        ang = math.radians(a)
        ang = round(ang / step - 0.5) * step + step * 0.5
        rr = r * math.cos(step * 0.5)
        c = (bx + math.cos(ang) * rr, OUT_Z + math.sin(ang) * rr)
        if lit:
            cp.lancet(m, c, y, 0.26, 0.8, (math.cos(ang), 0, math.sin(ang)), "window_candle", frame=0.1, proud=0.05)
        else:
            cp.loop(m, c, y, 1.1, (math.cos(ang), 0, math.sin(ang)), proud=0.05, width=0.11, cross=False)


def stair(m):
    """Up the city side to the walk, south of the gate: twenty steps."""
    n = 20
    rise = WALK / n
    x_top = -GAP - 1.4
    going = 0.46
    for i in range(n):
        xa = x_top - (n - i) * going
        shade = 0.62 + 0.3 * i / n + random.uniform(-0.04, 0.04)
        cp.block(m, (xa, -0.4, IN_Z), (xa + going, (i + 1) * rise, IN_Z + 1.35), ASHLAR, cp.rgba(cp.STONE, shade), faces="xzZY")
    cp.block(m, (x_top, -0.4, IN_Z), (x_top + 1.5, WALK, IN_Z + 1.35), ASHLAR, cp.rgba(cp.STONE, 0.9), faces="XZY")


def causeway(m):
    half, z0, z1 = CAUSEWAY
    tint = cp.stone_tint(-2.0, 1.4, seed=7.0)
    for s in (-1, 1):
        lo = (min(s * half, s * (half + 0.5)), -3.0, z0)
        hi = (max(s * half, s * (half + 0.5)), 0.85, z1)
        cp.slab(m, lo, hi, RUBBLE, tint, faces="xXzZ", step=1.8)
        cp.block(m, (lo[0] - 0.06, 0.85, z0 - 0.06), (hi[0] + 0.06, 1.0, z1), ASHLAR, cp.rgba(cp.STONE, 0.9), faces="xXzyY")
        # A stone at its end, where the cart wheels strike.
        cp.block(m, (lo[0] - 0.12, -0.3, z0 - 0.55), (hi[0] + 0.12, 1.25, z0), ASHLAR, cp.rgba(cp.STONE, 0.8), faces="xXzZY")
    # The bank under the road, between them.
    earth = cp.rgba((0.3, 0.29, 0.27))
    m.poly([(-half, 0.0, z0), (half, 0.0, z0), (half, -3.0, z0), (-half, -3.0, z0)], RUBBLE, earth, facing=(0, 0, -1))


def colliders():
    boxes = [("WallS", (SOUTH, -1.0, OUT_Z), (-GAP, WALK + 2.0, IN_Z)), ("WallN", (GAP, -1.0, OUT_Z), (NORTH, WALK + 2.0, IN_Z))]
    for i, (bx, _c) in enumerate(BASTIONS):
        boxes.append(("Bastion%d" % i, (bx - BASTION_R, -1.0, OUT_Z - BASTION_R), (bx + BASTION_R, BASTION_TOP + 1.8, OUT_Z)))
    half, z0, z1 = CAUSEWAY
    for s, name in ((-1, "ParapetS"), (1, "ParapetN")):
        boxes.append((name, (min(s * half, s * (half + 0.5)), -1.0, z0 - 0.5), (max(s * half, s * (half + 0.5)), 1.1, z1)))
    for name, lo, hi in boxes:
        c = porter.Mesh(name + "-colonly")
        c.box(lo, hi, RUBBLE)
        c.build()
    # The stair, as a ramp.
    x_top = -GAP - 1.4
    xa = x_top - 20 * 0.46
    c = porter.Mesh("Stair-colonly")
    z0, z1 = IN_Z, IN_Z + 1.35
    c.poly([(xa, 0.0, z0), (x_top, WALK, z0), (x_top, WALK, z1), (xa, 0.0, z1)], ASHLAR, facing=(-1, 1, 0))
    c.poly([(xa, 0.0, z1), (x_top, WALK, z1), (x_top + 1.5, WALK, z1), (x_top + 1.5, 0.0, z1)], ASHLAR, facing=(0, 0, 1))
    c.poly([(x_top, WALK, z0), (x_top + 1.5, WALK, z0), (x_top + 1.5, WALK, z1), (x_top, WALK, z1)], ASHLAR, facing=(0, 1, 0))
    c.build()


def main():
    porter.reset(17)
    m = porter.Mesh("Wall")
    wall(m, SOUTH, -GAP, 1.0)
    wall(m, GAP, NORTH, 2.0)
    m.build()
    b = porter.Mesh("Bastions")
    for i, (bx, candle) in enumerate(BASTIONS):
        bastion(b, bx, candle, 3.0 + i)
    b.build()
    s = porter.Mesh("Stair")
    stair(s)
    causeway(s)
    s.build()
    colliders()
    porter.export("env_city_wall")


if __name__ == "__main__":
    main()
