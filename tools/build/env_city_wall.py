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

- Buttresses of cut stone, arrow slits, and north of the gate a mason's
  scaffold against a stretch that has been mended in new pale stone.

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
ASHLAR = "stone_ashlar"
# Buttresses against the country face, and the mason's scaffold north of the gate (from x, to x).
BUTTRESSES = (-128.0, -98.0, -84.0, -70.0, -41.0, -27.0, -13.5, 13.5, 27.0, 38.0, 66.0, 94.0, 123.0)
SCAFFOLD = (15.0, 24.0)


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


def buttresses(m):
    for i, bx in enumerate(BUTTRESSES):
        tint = cp.stone_tint(0.0, 7.0, seed=30.0 + i, worn=0.5)
        w = 0.75
        # Two stages, each with a sloped offset on top.
        for z_out, y0, y1 in ((OUT_Z - 1.5, FOOT, 3.0), (OUT_Z - 0.85, 3.0, 6.1)):
            cp.slab(m, (bx - w, y0, z_out), (bx + w, y1, OUT_Z), ASHLAR, tint, faces="xXz", step=1.6)
            cap = [(bx - w, y1, z_out), (bx + w, y1, z_out), (bx + w, y1 + 0.7, OUT_Z), (bx - w, y1 + 0.7, OUT_Z)]
            m.poly(cap, ASHLAR, [tint(*q) for q in cap], facing=(0, 1, -1))
            for s in (-1, 1):
                m.poly([(bx + s * w, y1, z_out), (bx + s * w, y1, OUT_Z), (bx + s * w, y1 + 0.7, OUT_Z)], ASHLAR, cp.rgba(cp.STONE_DARK),
                       facing=(s, 0, 0))
            w -= 0.12


def slits(m):
    x = SOUTH + 9.0
    while x < NORTH - 5.0:
        clear = abs(x) > GAP + 3.0 and fallen(x) == 0.0 and all(abs(x - b) > 5.0 for b, _c in BASTIONS) \
            and all(abs(x - b) > 1.6 for b in BUTTRESSES)
        if clear:
            cp.loop(m, (x, OUT_Z), 4.7 + 0.5 * fbm(x, 0.0, 0.3, 1, 5.0), 1.0, (0, 0, -1), proud=0.03, width=0.1, cross=False)
        x += 11.3


def scaffold(m):
    """Poles lashed together against the wall, two lifts of planks, a
    ladder: the masons have gone home for the day. The stone behind it is
    new and pale."""
    xa, xb = SCAFFOLD
    pole = lambda k=1.0: (0.42 * k, 0.4 * k, 0.37 * k, 1.0)
    fresh = lambda x, y, z: (1.08, 1.06, 1.0, 1.0)
    cp.panel(m, (xa + 1.2, OUT_Z - 0.04), (xb - 1.0, OUT_Z - 0.04), 3.4, WALK - 0.2, (0, 0, -1), ASHLAR, fresh, 2.6, 2.4)
    xs = cp.steps(xa, xb, 2.4)
    rows = (OUT_Z - 0.35, OUT_Z - 1.55)
    for i, x in enumerate(xs):
        for z in rows:
            lean = 0.05 * math.sin(i * 2.3 + z)
            m.tube([(x + lean, -0.4, z), (x - lean, WALK + 0.9 + 0.5 * math.sin(i * 1.7 + z * 3.0), z)], [0.06, 0.045], 5, "wood_frame", pole(0.9 + 0.1 * (i % 2)))
        for y in (2.3, 4.6, 6.9):
            m.tube([(x, y - 0.1, rows[0] + 0.2), (x, y - 0.1, rows[1] - 0.25)], [0.045, 0.045], 4, "wood_frame", pole(0.8))
    for y in (2.3, 4.6, 6.9):
        for z in rows:
            m.tube([(xa - 0.3, y + 0.02 * z, z - 0.07), (xb + 0.3, y - 0.02 * z, z - 0.07)], [0.045, 0.04], 4, "wood_frame", pole())
    for a, b in (((xs[0], 0.0), (xs[1], 2.3)), ((xs[-1], 2.3), (xs[-2], 4.6)), ((xs[1], 4.6), (xs[2], 6.9))):
        m.tube([(a[0], a[1], rows[1] - 0.09), (b[0], b[1], rows[1] - 0.09)], [0.04, 0.04], 4, "wood_frame", pole(0.85))
    # Planks on the upper two lifts, not all of them there.
    for y, bays in ((4.6, (0, 1, 2)), (6.9, (1, 2, 3))):
        for b in bays:
            if b + 1 >= len(xs):
                continue
            for k, z in enumerate((rows[0] - 0.05, rows[0] - 0.42, rows[0] - 0.79)):
                if (b + k + int(y)) % 5 == 0:
                    continue
                c = 0.44 + 0.08 * ((b * 3 + k) % 3)
                cp.block(m, (xs[b] - 0.25, y, z - 0.32), (xs[b + 1] + 0.25, y + 0.045, z), "wood_boards", (c, c * 0.96, c * 0.9, 1.0), faces="xXzZyY")
    # The ladder, from the ground to the first lift of planks.
    lx = xs[1] + 0.9
    for dx in (0.0, 0.42):
        m.tube([(lx - 1.2 + dx, -0.3, rows[1] - 0.8), (lx + 0.5 + dx, 4.9, rows[1])], [0.035, 0.035], 4, "wood_frame", pole(1.1))
    for i in range(1, 14):
        k = i / 14.0
        x0 = lx - 1.2 + 1.7 * k
        m.tube([(x0, -0.3 + 5.2 * k, rows[1] - 0.8 + 0.8 * k), (x0 + 0.42, -0.3 + 5.2 * k, rows[1] - 0.8 + 0.8 * k)], [0.022, 0.022], 4, "wood_frame", pole(1.0))


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
    buttresses(m)
    slits(m)
    m.build()
    sc = porter.Mesh("Scaffold")
    scaffold(sc)
    sc.build()
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
