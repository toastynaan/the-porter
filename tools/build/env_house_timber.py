"""The timber houses of the streets inside Aldgate (night 0, the road in):
oak frames with lime-plastered panels between, each upper floor jutting out
over the one below, tiled roofs with their gables to the street or their
eaves along it. Six houses, each its own model
(art/models/env_house_timber_a.glb ... _f.glb), so a street can be made of
them without two alike standing together.

In its own space a house's street front faces -z: its ground floor's face
is at z = 0, each floor above stands 0.5 m further out, and the house runs
back to z = 9. The origin is on the ground at the middle of the front.

- Every window and door pane is its own object (Window<floor>_<n>,
  Door0), dark as built: the house's scene lights the ones named in its
  `lit_windows` (game/world/street/timber_house.gd). Some windows are
  shuttered for good and are part of the walls.
- The whole frame leans a little, each house its own way: they are old.
- A house may have a hanging sign or an ale-stake, an iron bracket for a
  lantern (the scene hangs the lamp on it), a smoke louvre on the ridge.

Collision: a box for each floor.

Run: tools/build.sh env_house_timber
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
import city_parts as cp
from porter import fbm, lerp, smoothstep

DEPTH = 9.0
JETTY = 0.5
OAK = "wood_medieval"
DAUB = "plaster_daub"

# The houses. floors: the height of each; roof: "gable" (gable to the
# street) or "eaves" (ridge along the street), with `dormer` for a gablet
# in it; frame: the pattern of each upper floor's timbers; plaster: its
# colour; windows: for each floor, (middle x, width, height, sill, kind)
# with kind "pane" (may be lit), "shut" (boarded shutters) or "shop" (a
# wide shuttered shop front); door: (middle x, width, height).
HOUSES = {
    "a": dict(width=5.0, floors=(3.0, 2.8, 2.6), roof="gable", frame=("close", "square"), plaster=(0.8, 0.76, 0.66),
              door=(-1.45, 1.0, 2.05), lean=(0.012, -0.004), lamp=1.9, louvre=False,
              windows=(((0.85, 2.0, 1.15, 0.95, "shop"),), ((-1.1, 1.1, 1.2, 0.95, "pane"), (1.1, 1.1, 1.2, 0.95, "pane")),
                       ((0.0, 1.9, 1.1, 0.9, "pane"),)), attic="pane"),
    "b": dict(width=4.4, floors=(2.9, 2.7, 2.7), roof="gable", frame=("brace", "close"), plaster=(0.7, 0.7, 0.68),
              door=(1.2, 0.95, 2.0), lean=(-0.02, 0.006), sign="board", louvre=True,
              windows=(((-0.75, 1.7, 1.1, 1.0, "shop"),), ((0.0, 1.6, 1.25, 0.9, "pane"),),
                       ((-0.95, 0.9, 1.1, 0.95, "shut"), (0.95, 0.9, 1.1, 0.95, "pane"))), attic="shut"),
    "c": dict(width=6.0, floors=(3.0, 2.9), roof="eaves", dormer=True, frame=("square",), plaster=(0.78, 0.69, 0.52),
              door=(0.0, 1.1, 2.1), lean=(0.008, 0.01), lamp=-2.4, louvre=True,
              windows=(((-1.95, 1.3, 1.1, 1.0, "shut"), (1.95, 1.3, 1.1, 1.0, "pane")),
                       ((-1.9, 1.2, 1.2, 0.95, "pane"), (0.0, 1.0, 1.2, 0.95, "shut"), (1.9, 1.2, 1.2, 0.95, "pane"))), attic="pane"),
    "d": dict(width=5.4, floors=(3.2, 3.0, 2.8), roof="gable", frame=("close", "close"), plaster=(0.84, 0.82, 0.77),
              door=(-1.6, 1.0, 2.1), lean=(0.018, 0.012), louvre=False,
              windows=(((0.75, 2.4, 1.2, 0.95, "shop"),), ((0.0, 2.6, 1.3, 0.95, "pane"),),
                       ((-1.2, 1.0, 1.15, 0.95, "pane"), (1.2, 1.0, 1.15, 0.95, "shut"))), attic="pane"),
    "e": dict(width=6.2, floors=(3.0, 2.8, 2.5), roof="eaves", dormer=False, twin=True, frame=("square", "brace"),
              plaster=(0.74, 0.7, 0.66), door=(2.05, 1.0, 2.05), lean=(-0.01, 0.014), lamp=-2.6, louvre=False,
              windows=(((-1.0, 2.6, 1.15, 0.95, "shop"),), ((-1.6, 1.3, 1.2, 0.95, "pane"), (1.6, 1.3, 1.2, 0.95, "pane")),
                       ((-1.55, 1.1, 1.05, 0.9, "pane"), (1.55, 1.1, 1.05, 0.9, "shut"))), attic="pane"),
    "f": dict(width=4.8, floors=(3.1, 2.7), roof="gable", frame=("brace",), plaster=(0.8, 0.72, 0.64), stone=True,
              door=(-1.1, 1.05, 2.1), lean=(-0.014, -0.006), sign="stake", louvre=True,
              windows=(((1.15, 1.0, 1.0, 1.15, "pane"),), ((0.0, 2.2, 1.25, 0.9, "pane"),)), attic="shut"),
}


class Lean(porter.Mesh):
    """A mesh whose every point is pushed sideways and forward by its
    height: an old frame that has settled."""
    lean = (0.0, 0.0)

    def vert(self, x, y, z, color=(1.0, 1.0, 1.0, 1.0), uv=(0.0, 0.0)):
        return super().vert(x + self.lean[0] * max(y, 0.0), y, z + self.lean[1] * max(y, 0.0), color, uv)


def oak(k=1.0):
    v = (0.5 + random.uniform(-0.07, 0.07)) * k
    return (v, v * 0.95, v * 0.88, 1.0)


def plaster_tint(base, y0, y1, seed):
    """Limewash gone grey: dark under the floor above, splashed at the
    foot, blotched all over."""
    def tint(x, y, z):
        under = smoothstep(y1 - 0.7, y1, y) * 0.3
        foot = (1.0 - smoothstep(y0, y0 + 0.6, y)) * 0.22
        blot = 0.84 + 0.2 * fbm(x * 1.0 + seed * 7.0, y + z * 0.5, 0.35, 3, seed)
        run = 0.12 * smoothstep(0.1, 0.6, fbm(x * 2.2, y * 0.15, 1.0, 2, seed + 3.0)) * smoothstep(y0, y1, y)
        k = blot * (1.0 - under - foot - run)
        return (base[0] * k, base[1] * k, base[2] * k * (1.0 - foot * 0.3), 1.0)
    return tint


def beam(m, a, b, width, zf, proud=0.05, color=None, out=-1.0):
    """A timber on a wall's face from (x, y) `a` to `b`: its front, standing
    `proud` of the plane z = zf, and its two long edges."""
    c = color or oak()
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy) or 1.0
    px, py = -dy / n * width * 0.5, dx / n * width * 0.5
    z = zf + out * proud
    front = [(a[0] + px, a[1] + py, z), (b[0] + px, b[1] + py, z), (b[0] - px, b[1] - py, z), (a[0] - px, a[1] - py, z)]
    m.poly(front, OAK, c, facing=(0, 0, out))
    dark = (c[0] * 0.6, c[1] * 0.6, c[2] * 0.6, 1.0)
    for s in (1, -1):
        e = [(a[0] + s * px, a[1] + s * py, z), (b[0] + s * px, b[1] + s * py, z), (b[0] + s * px, b[1] + s * py, zf),
             (a[0] + s * px, a[1] + s * py, zf)]
        m.poly(e, OAK, dark, facing=(s * px, s * py, 0))


def side_beam(m, x, a, b, width, s, proud=0.04):
    """The same on a side wall (the plane x = `x`, looking toward s): from (z, y) `a` to `b`."""
    c = oak(0.9)
    dz, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dz, dy) or 1.0
    pz, py = -dy / n * width * 0.5, dz / n * width * 0.5
    xf = x + s * proud
    m.poly([(xf, a[1] + py, a[0] + pz), (xf, b[1] + py, b[0] + pz), (xf, b[1] - py, b[0] - pz), (xf, a[1] - py, a[0] - pz)], OAK, c,
           facing=(s, 0, 0))


def frame(m, pattern, x0, x1, y0, y1, zf, openings):
    """A floor's timbers on its street face: sill and plate, corner posts,
    then its pattern, kept clear of the windows."""
    def clear(x, ya, yb):
        return not any(ox0 - 0.05 < x < ox1 + 0.05 and ya < oy1 and yb > oy0 for ox0, ox1, oy0, oy1 in openings)

    beam(m, (x0, y0 + 0.13), (x1, y0 + 0.13), 0.26, zf, 0.08)
    beam(m, (x0, y1 - 0.09), (x1, y1 - 0.09), 0.18, zf, 0.06)
    for x in (x0 + 0.11, x1 - 0.11):
        beam(m, (x, y0 + 0.26), (x, y1 - 0.18), 0.22, zf, 0.07)
    rail = y0 + 0.26 + (y1 - y0 - 0.44) * 0.42
    lo, hi = y0 + 0.26, y1 - 0.18
    if pattern == "close":
        n = max(int(round((x1 - x0 - 0.44) / 0.46)), 2)
        for i in range(1, n):
            x = x0 + 0.22 + (x1 - x0 - 0.44) * i / n
            for ya, yb in ((lo, rail), (rail, hi)):
                if clear(x, ya, yb):
                    beam(m, (x, ya), (x, yb), 0.13, zf)
        segs = [(x0 + 0.22, x1 - 0.22)]
    else:
        n = max(int(round((x1 - x0 - 0.44) / 1.25)), 2)
        posts = [x0 + 0.22 + (x1 - x0 - 0.44) * i / n for i in range(n + 1)]
        for x in posts[1:-1]:
            for ya, yb in ((lo, rail), (rail, hi)):
                if clear(x, ya, yb):
                    beam(m, (x, ya), (x, yb), 0.16, zf)
        for i, (xa, xb) in enumerate(zip(posts, posts[1:])):
            mid = (xa + xb) * 0.5
            if pattern == "brace":
                # Chevrons: braces rising to the middle of each bay, above and below the rail.
                for ya, yb in ((lo, rail), (rail, hi)):
                    if clear(mid, ya, yb) and clear(xa + 0.2, ya, yb) and clear(xb - 0.2, ya, yb):
                        beam(m, (xa + 0.08, ya), (mid, yb), 0.12, zf, 0.045)
                        beam(m, (xb - 0.08, ya), (mid, yb), 0.12, zf, 0.045)
            elif i in (0, n - 1):
                # Square panels, with a brace across each end bay.
                if clear(mid, lo, rail) and clear(xa + 0.2, lo, rail) and clear(xb - 0.2, lo, rail):
                    a, b = ((xa + 0.08, rail), (xb - 0.08, lo)) if i == 0 else ((xb - 0.08, rail), (xa + 0.08, lo))
                    beam(m, a, b, 0.13, zf, 0.045)
    # The rail, broken where a window stands in it.
    cuts = sorted((ox0 - 0.1, ox1 + 0.1) for ox0, ox1, oy0, oy1 in openings if oy0 < rail < oy1)
    x = x0 + 0.22
    for c0, c1 in cuts + [(x1 - 0.22, x1)]:
        if c0 - x > 0.1:
            beam(m, (x, rail), (c0, rail), 0.14, zf)
        x = max(x, c1)


def window(m, panes, name, cx, w, h, y, zf, kind, lean):
    """A window on a street face: its frame, and either a pane of its own
    (an object, so it can be lit), with mullions, or boarded shutters."""
    xa, xb = cx - w * 0.5, cx + w * 0.5
    if kind == "pane":
        p = Lean(name)
        p.lean = lean
        p.centre = (cx, y + h * 0.5, zf)
        p.poly([(xa, y, zf - 0.015), (xb, y, zf - 0.015), (xb, y + h, zf - 0.015), (xa, y + h, zf - 0.015)], "window_dark",
               uvs=[(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)], facing=(0, 0, -1))
        panes.append(p)
        n = max(int(round(w / 0.3)), 2)
        for i in range(1, n):
            x = xa + w * i / n
            beam(m, (x, y), (x, y + h), 0.055, zf, 0.035, oak(0.8))
        if h > 1.0:
            beam(m, (xa, y + h * 0.56), (xb, y + h * 0.56), 0.06, zf, 0.04, oak(0.8))
    else:
        # Boards, a little apart, and two ledges across them.
        board = oak(0.75)
        m.poly([(xa, y, zf - 0.03), (xb, y, zf - 0.03), (xb, y + h, zf - 0.03), (xa, y + h, zf - 0.03)], OAK, board, facing=(0, 0, -1))
        x = xa + 0.2
        while x < xb - 0.05:
            m.poly([(x, y, zf - 0.034), (x + 0.02, y, zf - 0.034), (x + 0.02, y + h, zf - 0.034), (x, y + h, zf - 0.034)], "window_dark",
                   facing=(0, 0, -1))
            x += 0.2 + random.uniform(0.0, 0.05)
        for yy in (y + h * 0.2, y + h * 0.78):
            beam(m, (xa, yy), (xb, yy), 0.09, zf, 0.055, oak(0.65))
    # Its frame; a shop front has a stall board under it.
    beam(m, (xa - 0.07, y - 0.05), (xb + 0.07, y - 0.05), 0.12, zf, 0.075)
    beam(m, (xa - 0.07, y + h + 0.05), (xb + 0.07, y + h + 0.05), 0.12, zf, 0.065)
    for x in (xa - 0.05, xb + 0.05):
        beam(m, (x, y), (x, y + h), 0.11, zf, 0.065)
    if kind == "shop":
        m.box((xa - 0.05, y - 0.16, zf - 0.42), (xb + 0.05, y - 0.1, zf), OAK, oak(0.8))
        for x in (xa + 0.1, xb - 0.1):
            beam(m, (x, y - 0.75), (x, y - 0.16), 0.07, zf - 0.34, 0.0, oak(0.7))
    return (xa - 0.1, xb + 0.1, y - 0.12, y + h + 0.12)


def jetty(m, x0, x1, y, z_low, z_high):
    """The underside of an overhanging floor: the joists' ends showing, and a bracket at each corner."""
    under = (0.2, 0.19, 0.18, 1.0)
    m.poly([(x0, y, z_high), (x1, y, z_high), (x1, y, z_low), (x0, y, z_low)], OAK, under, facing=(0, -1, 0))
    n = int((x1 - x0) / 0.52)
    for i in range(n + 1):
        x = x0 + 0.1 + (x1 - x0 - 0.2) * i / n
        m.box((x - 0.07, y - 0.17, z_high - 0.04), (x + 0.07, y, z_low), OAK, oak(0.8), faces="xXzy")
    for x in (x0 + 0.11, x1 - 0.11):
        c = oak(0.85)
        for s in (-1, 1):
            m.poly([(x + s * 0.08, y - 0.75, z_low), (x + s * 0.08, y - 0.02, z_high), (x + s * 0.08, y - 0.02, z_low)], OAK, c,
                   facing=(s, 0, 0))
        m.poly([(x - 0.08, y - 0.75, z_low), (x + 0.08, y - 0.75, z_low), (x + 0.08, y - 0.02, z_high), (x - 0.08, y - 0.02, z_high)],
               OAK, c, facing=(0, -1, -1))


def side_walls(m, x0, x1, y0, y1, zf, tint):
    for x, s in ((x0, -1), (x1, 1)):
        cp.panel(m, (x, zf), (x, DEPTH), y0, y1, (s, 0, 0), DAUB, tint, 2.4, 1.5)
        for y in (y0 + 0.12, y1 - 0.09, (y0 + y1) * 0.5):
            side_beam(m, x, (zf, y), (DEPTH, y), 0.18, s)
        z = zf + 0.1
        while z < DEPTH:
            side_beam(m, x, (z, y0), (z, y1), 0.18, s)
            z += 2.2


def house(key, spec):
    random.seed(ord(key) * 13)
    w = spec["width"]
    x0, x1 = -w * 0.5, w * 0.5
    lean = spec["lean"]
    m = Lean("House")
    m.lean = lean
    panes = []
    seed = float(ord(key))
    base = spec["plaster"]
    y = 0.0
    zf = 0.0
    tops = []
    for k, height in enumerate(spec["floors"]):
        y0, y1 = y, y + height
        zf = -JETTY * k
        tint = plaster_tint(base, y0, y1, seed + k)
        openings = []
        stone = k == 0 and spec.get("stone")
        if stone:
            st = cp.stone_tint(0.0, y1, seed=seed)
            cp.panel(m, (x0, zf), (x1, zf), y0, y1, (0, 0, -1), "stone_rubble", st, 1.6, 1.2)
            for x, s in ((x0, -1), (x1, 1)):
                cp.panel(m, (x, zf), (x, DEPTH), y0, y1, (s, 0, 0), "stone_rubble", st, 2.4, 1.5)
        else:
            cp.panel(m, (x0, zf), (x1, zf), y0, y1, (0, 0, -1), DAUB, tint, 1.3, 1.0)
            side_walls(m, x0, x1, y0, y1, zf, tint)
        cp.panel(m, (x0, DEPTH), (x1, DEPTH), y0, y1, (0, 0, 1), DAUB, tint, 3.0, 2.0)
        if k == 0:
            # A stone footing, and the door.
            if not stone:
                cp.block(m, (x0 - 0.04, -0.3, -0.05), (x1 + 0.04, 0.42, 0.0), "stone_blocks", cp.rgba(cp.STONE_DAMP, 1.2), faces="xXzY")
            dx, dw, dh = spec["door"]
            d = Lean("Door0")
            d.lean = lean
            d.centre = (spec["door"][0], 1.0, 0.0)
            planks = int(dw / 0.24)
            for i in range(planks):
                xa, xb = dx - dw * 0.5 + dw * i / planks, dx - dw * 0.5 + dw * (i + 1) / planks
                c = oak(0.8)
                d.poly([(xa + 0.008, 0.02, zf - 0.03), (xb - 0.008, 0.02, zf - 0.03), (xb - 0.008, dh, zf - 0.03), (xa + 0.008, dh, zf - 0.03)],
                       OAK, c, uvs=[(0.0, 0.0), (0.3, 0.0), (0.3, 1.0), (0.0, 1.0)], facing=(0, 0, -1))
            panes.append(d)
            m.poly([(dx - dw * 0.5, 0.0, zf - 0.02), (dx + dw * 0.5, 0.0, zf - 0.02), (dx + dw * 0.5, dh, zf - 0.02), (dx - dw * 0.5, dh, zf - 0.02)],
                   "window_dark", facing=(0, 0, -1))
            for x in (dx - dw * 0.5 - 0.07, dx + dw * 0.5 + 0.07):
                beam(m, (x, 0.0), (x, dh + 0.14), 0.15, zf, 0.09)
            beam(m, (dx - dw * 0.5 - 0.14, dh + 0.08), (dx + dw * 0.5 + 0.14, dh + 0.08), 0.17, zf, 0.1)
            openings.append((dx - dw * 0.5 - 0.15, dx + dw * 0.5 + 0.15, 0.0, dh + 0.2))
        for i, (cx, ww, wh, sill, kind) in enumerate(spec["windows"][k]):
            openings.append(window(m, panes, "Window%d_%d" % (k, i), cx, ww, wh, y0 + sill, zf, kind, lean))
        if stone:
            beam(m, (x0, y1 - 0.1), (x1, y1 - 0.1), 0.2, zf, 0.06)
        else:
            pattern = "close" if k == 0 else spec["frame"][k - 1]
            frame(m, pattern, x0, x1, y0 + (0.4 if k == 0 else 0.0), y1, zf, openings)
        if k > 0:
            jetty(m, x0, x1, y0, zf + JETTY, zf)
        tops.append((y0, y1, zf))
        y = y1
    top = y
    roofs(m, panes, spec, x0, x1, top, zf, base, seed, lean)
    extras(m, spec, x0, x1, tops)
    m.build()
    for p in panes:
        p.build(origin=p.centre)
    for k, (y0, y1, z) in enumerate(tops):
        c = porter.Mesh("Floor%d-colonly" % k)
        c.box((x0, y0, z), (x1, y1 + (0.0 if k < len(tops) - 1 else 2.0), DEPTH), OAK)
        c.build()


def gable_front(m, panes, name, xa, xb, y, peak, zf, base, seed, attic, lean, barge=True):
    """A gable to the street: plaster and timbers in the triangle, an
    attic window, and bargeboards down its edges."""
    mid = (xa + xb) * 0.5
    tint = plaster_tint(base, y, peak, seed + 5.0)
    pts = [(xa, y, zf), (xb, y, zf), (mid, peak, zf)]
    # Cut the triangle across so the tint has something to hold on to.
    cut = y + (peak - y) * 0.45
    ka = (cut - y) / (peak - y)
    la, lb = (lerp(xa, mid, ka), cut, zf), (lerp(xb, mid, ka), cut, zf)
    for poly in ([pts[0], pts[1], lb, la], [la, lb, pts[2]]):
        m.poly(poly, DAUB, [tint(*p) for p in poly], facing=(0, 0, -1))
    beam(m, (xa, y + 0.1), (xb, y + 0.1), 0.2, zf, 0.07)
    beam(m, (la[0], cut), (lb[0], cut), 0.14, zf)
    half = (xb - xa) * 0.5
    opening = None
    if attic and half > 1.6:
        ww, wh = 0.8, 0.75
        opening = window(m, panes, name, mid, ww, wh, y + 0.45, zf, attic, lean)
    for dx in (-half * 0.5, 0.0, half * 0.5):
        x = mid + dx
        y_top = y + (peak - y) * (1.0 - abs(dx) / half) - 0.15
        if opening and opening[0] < x < opening[1]:
            beam(m, (x, opening[3]), (x, y_top), 0.14, zf)
        else:
            beam(m, (x, y + 0.2), (x, y_top), 0.14, zf)
    if barge:
        for s in (-1, 1):
            beam(m, (mid + s * (half + 0.28), y - 0.22), (mid, peak + 0.06), 0.24, zf - 0.3, 0.06, oak(0.7))


def roofs(m, panes, spec, x0, x1, top, zf, base, seed, lean):
    tile = (0.82, 0.8, 0.78)
    w = x1 - x0
    if spec["roof"] == "gable":
        peak = top + w * 0.5 * 1.2
        gable_front(m, panes, "Window%d_0" % len(spec["floors"]), x0, x1, top, peak, zf, base, seed, spec.get("attic"), lean)
        cp.gable_roof(m, x0, x1, zf - 0.32, DEPTH, top, peak, "roof_tiles", tile, along="z", over=0.3, sag=0.16)
        tint = plaster_tint(base, top, peak, seed + 6.0)
        back = [(x0, top, DEPTH), (x1, top, DEPTH), ((x0 + x1) * 0.5, peak, DEPTH)]
        m.poly(back, DAUB, [tint(*p) for p in back], facing=(0, 0, 1))
        ridge = (0.0, peak, DEPTH * 0.55)
    else:
        # Eaves along the street: a steep slope up from the front, a long one down the back.
        rz = zf + 3.4
        peak = top + 3.9
        over = 0.35
        drop = over * 3.9 / 3.4
        front = [(x0 - 0.3, top - drop, zf - over), (x1 + 0.3, top - drop, zf - over), (x1 + 0.3, peak, rz), (x0 - 0.3, peak, rz)]
        span = math.hypot(3.4 + over, 3.9 + drop)
        m.poly(front, "roof_tiles", cp.rgba(tile), [(0.0, 0.0), ((w + 0.6) / 1.8, 0.0), ((w + 0.6) / 1.8, span / 1.8), (0.0, span / 1.8)],
               facing=(0, 1, -1))
        m.poly(front, "roof_tiles", (0.2, 0.2, 0.2, 1.0), facing=(0, -1, 1))
        back = [(x0 - 0.3, peak, rz), (x1 + 0.3, peak, rz), (x1 + 0.3, top - 0.6, DEPTH + 0.3), (x0 - 0.3, top - 0.6, DEPTH + 0.3)]
        span = math.hypot(DEPTH + 0.3 - rz, peak - top + 0.6)
        m.poly(back, "roof_tiles", cp.rgba(tile, 0.9), [(0.0, 0.0), ((w + 0.6) / 1.8, 0.0), ((w + 0.6) / 1.8, span / 1.8), (0.0, span / 1.8)],
               facing=(0, 1, 1))
        tint = plaster_tint(base, top, peak, seed + 6.0)
        for x, s in ((x0, -1), (x1, 1)):
            end = [(x, top, zf), (x, top, DEPTH), (x, peak, rz)]
            m.poly(end, DAUB, [tint(*p) for p in end], facing=(s, 0, 0))
            side_beam(m, x, (zf, top), (rz, peak), 0.2, s)
            side_beam(m, x, (rz, peak), (DEPTH, top), 0.2, s)
            side_beam(m, x, (rz, top), (rz, peak), 0.16, s)
        gablets = []
        if spec.get("twin"):
            gablets = [(x0 + 0.15, x0 + w * 0.5 - 0.1), (x1 - w * 0.5 + 0.1, x1 - 0.15)]
        elif spec.get("dormer"):
            gablets = [(-1.25, 1.25)]
        for i, (xa, xb) in enumerate(gablets):
            # A gablet standing on the front wall, its own little roof running back into the slope.
            gp = top + (xb - xa) * 0.5 * 1.25
            gable_front(m, panes, "Window%d_%d" % (len(spec["floors"]), i), xa, xb, top, gp, zf, base, seed + i, spec.get("attic"), lean)
            back_z = zf + (gp - top) * 3.4 / 3.9 + 0.2
            mid = (xa + xb) * 0.5
            for s, xe in ((-1, xa - 0.25), (1, xb + 0.25)):
                eave = top - 0.25 * 1.25
                pts = [(xe, eave, zf - 0.3), (mid, gp, zf - 0.3), (mid, gp, back_z), (xe, eave, zf + 0.1)]
                m.poly(pts, "roof_tiles", cp.rgba(tile), [(0.0, 0.0), (0.0, 1.0), (1.2, 1.0), (0.3, 0.0)], facing=(s, 1, 0))
                m.poly(pts, "roof_tiles", (0.2, 0.2, 0.2, 1.0), facing=(-s, -1, 0))
        ridge = (0.0, peak, rz)
    if spec.get("louvre"):
        # A smoke louvre astride the ridge: a little boarded turret with its own roof.
        lx, ly, lz = ridge[0] + (0.0 if spec["roof"] == "gable" else w * 0.2), ridge[1] - 0.25, ridge[2]
        m.box((lx - 0.32, ly, lz - 0.32), (lx + 0.32, ly + 0.6, lz + 0.32), OAK, oak(0.6), faces="xXzZ")
        for s in (-1, 1):
            pts = [(lx - 0.45, ly + 0.55, lz + s * 0.45), (lx + 0.45, ly + 0.55, lz + s * 0.45), (lx, ly + 1.0, lz)]
            m.poly(pts, "roof_tiles", cp.rgba(tile, 0.8), [(0, 0), (0.5, 0), (0.25, 0.4)], facing=(0, 1, s))
            pts = [(lx + s * 0.45, ly + 0.55, lz - 0.45), (lx + s * 0.45, ly + 0.55, lz + 0.45), (lx, ly + 1.0, lz)]
            m.poly(pts, "roof_tiles", cp.rgba(tile, 0.8), [(0, 0), (0.5, 0), (0.25, 0.4)], facing=(s, 1, 0))


def extras(m, spec, x0, x1, tops):
    iron = (0.5, 0.5, 0.52, 1.0)
    if "lamp" in spec:
        # An iron bracket by the door for a lantern (the scene hangs it): out from the wall, and a stay under it.
        lx = spec["lamp"]
        m.box((lx - 0.02, 2.82, -1.0), (lx + 0.02, 2.86, 0.0), "iron_cart", iron)
        m.poly([(lx, 2.84, -0.6), (lx + 0.012, 2.84, -0.6), (lx + 0.012, 2.45, 0.0), (lx, 2.45, 0.0)], "iron_cart", iron, facing=(1, 0, 0))
        m.poly([(lx, 2.84, -0.6), (lx + 0.012, 2.84, -0.6), (lx + 0.012, 2.45, 0.0), (lx, 2.45, 0.0)], "iron_cart", iron, facing=(-1, 0, 0))
    y1, zf1 = (tops[1][0], tops[1][2]) if len(tops) > 1 else (tops[0][1], 0.0)
    if spec.get("sign") == "board":
        # A painted board on an iron arm, out over the street.
        sx = x0 + 0.5
        y = y1 + 0.75
        m.box((sx - 0.025, y, zf1 - 1.05), (sx + 0.025, y + 0.05, zf1), "iron_cart", iron)
        m.poly([(sx, y, zf1 - 0.9), (sx + 0.014, y, zf1 - 0.9), (sx + 0.014, y + 0.5, zf1), (sx, y + 0.5, zf1)], "iron_cart", iron, facing=(1, 0, 0))
        m.poly([(sx, y, zf1 - 0.9), (sx + 0.014, y, zf1 - 0.9), (sx + 0.014, y + 0.5, zf1), (sx, y + 0.5, zf1)], "iron_cart", iron, facing=(-1, 0, 0))
        board = porter.srgb(0.3, 0.33, 0.3)
        m.box((sx - 0.02, y - 0.72, zf1 - 0.98), (sx + 0.02, y - 0.1, zf1 - 0.36), "painted", board)
        mark = porter.srgb(0.5, 0.42, 0.25)
        for s, xf in ((-1, sx - 0.024), (1, sx + 0.024)):
            # What it sells: a pale loaf shape, worn.
            m.poly([(xf, y - 0.56, zf1 - 0.84), (xf, y - 0.56, zf1 - 0.5), (xf, y - 0.36, zf1 - 0.44), (xf, y - 0.24, zf1 - 0.56),
                    (xf, y - 0.24, zf1 - 0.78), (xf, y - 0.36, zf1 - 0.9)], "painted", mark, facing=(s, 0, 0))
    if spec.get("sign") == "stake":
        # An ale-stake: a long pole out over the street with a bush tied to its end. Ale is sold here.
        sx = x1 - 0.7
        a = (sx, y1 + 0.3, zf1)
        b = (sx, y1 + 1.1, zf1 - 2.0)
        m.tube([a, b], [0.045, 0.03], 5, OAK, oak(0.7))
        bush = [(sx, b[1] - 0.05, b[2] + 0.15), (sx, b[1] + 0.05, b[2] - 0.1), (sx, b[1] + 0.12, b[2] - 0.35), (sx, b[1] + 0.16, b[2] - 0.5)]
        m.tube(bush, [0.05, 0.26, 0.22, 0.03], 6, "bark", (0.4, 0.45, 0.32, 1.0))


def main():
    for key, spec in HOUSES.items():
        porter.reset(40 + ord(key))
        house(key, spec)
        porter.export("env_house_timber_" + key)


if __name__ == "__main__":
    main()
