"""The Cross Keys, the inn opposite the abbey gate, as the lane sees it
(art/models/env_inn.glb; the scene is game/world/street/env_inn.tscn, where
this model is the node `Shell`). The best house in the lane and one of them:
a tall, dark, close-studded oak frame, each storey jutting out over the one
below on carved brackets, rows of leaded windows, an arched door in a carved
case, twin steep gables to the street, a stone chimney, the sign of the
crossed keys on an iron arm. It has settled: its north half racks and sags
toward the middle.

It is built in the idiom of the lane's houses (env_house_timber.py) and to
the plan shared with the inside (inn_plan.py): its windows are where the
plan puts them, and the two real openings (the street door and the porter's
window at the top right) are open. The inn's own space: the street front
faces -z, the origin is on the ground at the middle of the front.

- Every glazed window the lane can see is its own object (Window<floor>_<n>
  as the plan names them; Window3_<n> in the gables), dark as built (the
  plan's side windows are behind the neighbours and are not made): the
  scene lights the ones in its `lit_windows`. Their UVs are scaled for
  window_candle's leaded diamonds (the scene's lit_material, window_inn).
- The porter's window: the wall is drawn nearly 1 m deep there (the two
  jetties), so its reveal is splayed: the outer opening is the inner one as
  seen from where he stands (inn_plan.PORTER_STANDS), and then some. Every
  build checks it (check_view) and prints what it finds.
- No collision: the scene's hidden Blocks are that. On the ground nothing
  stands more than a hand out from the wall but the door's case; brackets,
  lantern arms, window boxes and the sign are above head height.
- The scene hangs a lamp on each of the three lantern arms (LAMPS).

Run: tools/build.sh env_inn
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
import city_parts as cp
import env_house_timber as ht
import inn_plan as plan
from porter import fbm, lerp, smoothstep

OAK = "wood_frame"
BOARDS = "wood_boards"
DAUB = "plaster_daub"
ROOF = "roof_tiles"
IRON = "iron_cart"
STONE = "stone_blocks"
GLASS = "window_dark"

X0, X1 = plan.X0, plan.X1
BACK = plan.Z1
F1, F2 = plan.FLOORS[1], plan.FLOORS[2]
EAVES = plan.EAVES
# The twin roofs are steeper than the plan's one (nothing under them is entered).
PEAK = plan.RIDGE + 1.0
# How far each storey stands out over the one below; the faces they make.
J1, J2, J3 = 0.5, 0.15, 0.25
ZA, ZB, ZC, ZG = 0.0, -J1, -(J1 + J2), -(J1 + J2 + J3)
# The frame's settling: the north (left) half racks north and sags toward
# the middle, and the whole front leans out a little. The south half, where
# the porter's window is, stands true.
RACK, SAG, LEAN = 0.008, 0.09, 0.004
PLASTER = (0.66, 0.6, 0.5)
TILE = (0.8, 0.78, 0.76)
IRON_C = (0.5, 0.5, 0.52, 1.0)
# Where the lamps hang (the dish; the arm's hook is 0.5 m above).
LAMPS = ((-1.35, 2.58, -0.95), (1.35, 2.58, -0.95), (-5.5, 2.58, -0.95))
# The porter's window: the hole in the wall, and the outer opening on the top storey's face.
PW = plan.PORTER_WINDOW
PW_OUT = (3.05, 4.95, 6.28, 8.3)
DOOR = plan.DOOR

beam = ht.beam
oak = ht.oak


class Old(porter.Mesh):
    """A mesh that has settled with the frame."""

    def vert(self, x, y, z, color=(1.0, 1.0, 1.0, 1.0), uv=(0.0, 0.0)):
        h = max(y, 0.0)
        left = 1.0 - smoothstep(-0.5, 2.0, x)
        mid = smoothstep(-6.0, -1.5, x) * (1.0 - smoothstep(0.2, 2.4, x))
        return super().vert(x - RACK * h * left, y - SAG * mid * smoothstep(1.0, 6.0, y), z - (LEAN * h if z < -1e-4 else 0.0), color, uv)


def wall(m, xa, xb, ya, yb, zf, tint, holes=(), out=-1, mat=DAUB):
    """A face of the front (or, with out=1, its lining seen from within), with rectangular holes."""
    xs = sorted({xa, xb} | {v for h in holes for v in h[:2] if xa < v < xb})
    ys = sorted({ya, yb} | {v for h in holes for v in h[2:] if ya < v < yb})
    for x0, x1 in zip(xs, xs[1:]):
        for y0, y1 in zip(ys, ys[1:]):
            cx, cy = (x0 + x1) * 0.5, (y0 + y1) * 0.5
            if any(h[0] < cx < h[1] and h[2] < cy < h[3] for h in holes):
                continue
            cp.panel(m, (x0, zf), (x1, zf), y0, y1, (0, 0, out), mat, tint, 1.4, 1.1)


def clear_spans(x, ya, yb, openings, pad=0.06):
    """The stretches of ya..yb at x that no opening covers."""
    spans = [(ya, yb)]
    for ox0, ox1, oy0, oy1 in openings:
        if ox0 - pad < x < ox1 + pad:
            nxt = []
            for a, b in spans:
                if oy0 > a:
                    nxt.append((a, min(b, oy0)))
                if oy1 < b:
                    nxt.append((max(a, oy1), b))
            spans = nxt
    return [(a, b) for a, b in spans if b - a > 0.14]


def studs(m, xa, xb, ya, yb, zf, openings, pitch=0.37):
    """Close studding: narrow uprights a hand apart, none quite plumb."""
    n = max(int(round((xb - xa) / pitch)), 1)
    for i in range(1, n):
        x = xa + (xb - xa) * i / n + random.uniform(-0.025, 0.025)
        w = random.uniform(0.16, 0.21)
        for a, b in clear_spans(x, ya, yb, openings):
            t = random.uniform(-0.012, 0.012)
            beam(m, (x - t, a), (x + t, b), w, zf, 0.05)


def rail(m, xa, xb, y, zf, openings, w=0.14, proud=0.055):
    cuts = sorted((o[0], o[1]) for o in openings if o[2] < y < o[3])
    x = xa
    for c0, c1 in cuts + [(xb, xb)]:
        if c0 - x > 0.1:
            beam(m, (x, y), (c0, y), w, zf, proud)
        x = max(x, c1)


def bressummer(m, y, zf, xa=X0, xb=X1, gap=None):
    """The moulded beam along a jetty's edge: a deep face, a roll under it and a fillet over."""
    beam(m, (xa, y + 0.15), (xb, y + 0.15), 0.3, zf, 0.09, oak(0.95))
    beam(m, (xa, y + 0.035), (xb, y + 0.035), 0.07, zf, 0.125, oak(0.8))
    for a, b in ((xa, gap[0]), (gap[1], xb)) if gap else ((xa, xb),):
        beam(m, (a, y + 0.285), (b, y + 0.285), 0.05, zf, 0.11, oak(0.85))
    # Carving along its face: a run of sunk lozenges.
    n = int((xb - xa - 0.3) / 0.34)
    for i in range(n + 1):
        x = xa + 0.15 + (xb - xa - 0.3) * i / n
        m.poly([(x - 0.085, y + 0.16, zf - 0.092), (x, y + 0.105, zf - 0.092), (x + 0.085, y + 0.16, zf - 0.092), (x, y + 0.215, zf - 0.092)], OAK, oak(0.42), facing=(0, 0, -1))
    # Its ends.
    for x, s in ((xa, -1), (xb, 1)):
        m.poly([(x, y, zf), (x, y, zf - 0.09), (x, y + 0.3, zf - 0.09), (x, y + 0.3, zf)], OAK, oak(0.6), facing=(s, 0, 0))


def bracket(m, x, y_top, z_wall, out, drop, thick=0.16):
    """A carved knee under a jetty: a curved brace from the post up to the beam's edge, with a cusp cut in its curve."""
    c = oak(0.85)
    dark = (c[0] * 0.62, c[1] * 0.62, c[2] * 0.62, 1.0)
    n = 10
    curve = []
    for j in range(n + 1):
        t = j / n
        a = math.pi * 0.5 * t
        z = z_wall - 0.05 - (out - 0.05) * (1.0 - math.cos(a))
        y = y_top - 0.1 - (drop - 0.1) * (1.0 - math.sin(a))
        bump = 0.055 * max(0.0, 1.0 - abs(t - 0.5) / 0.14)
        curve.append((y - bump * 0.7, z - bump * 0.7))
    outline = [(y_top, z_wall), (y_top - drop - 0.08, z_wall), (y_top - drop - 0.08, z_wall - 0.05)] + curve + [(y_top, z_wall - out)]
    xa, xb = x - thick * 0.5, x + thick * 0.5
    for xx, s in ((xa, -1), (xb, 1)):
        m.poly([(xx, y, z) for y, z in outline], OAK, c, facing=(s, 0, 0))
    edge = outline[1:]
    for (ya, za), (yb, zb) in zip(edge, edge[1:]):
        my, mz = (ya + yb) * 0.5 - y_top, (za + zb) * 0.5 - z_wall
        ny, nz = -(zb - za), (yb - ya)
        if ny * my + nz * mz < 0.0:
            ny, nz = -ny, -nz
        m.poly([(xa, ya, za), (xb, ya, za), (xb, yb, zb), (xa, yb, zb)], OAK, dark, facing=(0, ny, nz))


def jetty(m, y, z_wall, z_out, posts, drop, xa=X0, xb=X1):
    """A jetty's underside: its soffit, the joists' rounded ends, and a carved bracket on every main post."""
    m.poly([(xa, y, z_out), (xb, y, z_out), (xb, y, z_wall), (xa, y, z_wall)], OAK, (0.2, 0.19, 0.18, 1.0), facing=(0, -1, 0))
    n = int((xb - xa) / 0.5)
    for i in range(n + 1):
        x = xa + 0.12 + (xb - xa - 0.24) * i / n
        if any(abs(x - p) < 0.17 for p in posts):
            continue
        c = oak(0.8)
        m.box((x - 0.07, y - 0.15, z_out + 0.03), (x + 0.07, y, z_wall), OAK, c, faces="xXy")
        m.poly([(x - 0.07, y - 0.15, z_out + 0.03), (x + 0.07, y - 0.15, z_out + 0.03), (x + 0.07, y, z_out - 0.035), (x - 0.07, y, z_out - 0.035)],
               OAK, (c[0] * 0.7, c[1] * 0.7, c[2] * 0.7, 1.0), facing=(0, -1, -1))
    for p in posts:
        bracket(m, p, y, z_wall, z_wall - z_out, drop)


def glazed(m, panes, name, xa, xb, ya, yb, zf, lights=4, transom=0.58, arched=False):
    """A leaded window on a face: its pane (an object of its own, so it can be lit) behind oak mullions, in a
    moulded frame. `arched`: each light has a round head cut in the timber over it."""
    w, h = xb - xa, yb - ya
    p = Old(name)
    p.centre = ((xa + xb) * 0.5, (ya + yb) * 0.5, zf)
    zp = zf - 0.015
    # For window_candle: leaded diamonds a hand across, and the light pooled low.
    uv = lambda x, y: ((x - xa) / 0.5, (y - ya) / 1.6)
    p.poly([(xa, ya, zp), (xb, ya, zp), (xb, yb, zp), (xa, yb, zp)], GLASS, uvs=[uv(xa, ya), uv(xb, ya), uv(xb, yb), uv(xa, yb)], facing=(0, 0, -1))
    panes.append(p)
    edges = [xa + w * i / lights for i in range(lights + 1)]
    for x in edges[1:-1]:
        beam(m, (x, ya), (x, yb), 0.08, zf, 0.065, oak(0.85))
    if transom:
        beam(m, (xa, ya + h * transom), (xb, ya + h * transom), 0.06, zf, 0.055, oak(0.8))
    if arched:
        for la, lb in zip(edges, edges[1:]):
            la, lb = la + 0.04, lb - 0.04
            c, r = (la + lb) * 0.5, (lb - la) * 0.5
            spring = yb - r
            col = oak(0.75)
            n = 6
            for s in (-1, 1):
                for i in range(n):
                    a0, a1 = math.pi * 0.5 * i / n, math.pi * 0.5 * (i + 1) / n
                    q = [(c + s * r * math.cos(a0), spring + r * math.sin(a0), zf - 0.04), (c + s * r * math.cos(a1), spring + r * math.sin(a1), zf - 0.04),
                         (c + s * r * math.cos(a1), yb, zf - 0.04), (c + s * r * math.cos(a0), yb, zf - 0.04)]
                    m.poly(q, OAK, col, facing=(0, 0, -1))
    # The frame: a sill that throws the rain off, jambs, a head.
    m.box((xa - 0.12, ya - 0.1, zf - 0.14), (xb + 0.12, ya, zf), OAK, oak(0.9), faces="xXzyY")
    beam(m, (xa - 0.1, yb + 0.06), (xb + 0.1, yb + 0.06), 0.12, zf, 0.095)
    for x in (xa - 0.05, xb + 0.05):
        beam(m, (x, ya), (x, yb), 0.1, zf, 0.085)
    return (xa - 0.1, xb + 0.1, ya - 0.1, yb + 0.12)


def window_box(m, g, xa, xb, y, zf, deep=0.27, seed=0):
    """A trough of earth on two brackets under a sill, and what is left in it in November: ivy, and dead stalks hanging."""
    lo, hi = y - 0.24, y - 0.02
    c = oak(0.8)
    m.box((xa, lo, zf - deep), (xb, hi, zf), BOARDS, c, faces="xXzy")
    m.poly([(xa, hi - 0.03, zf - deep), (xb, hi - 0.03, zf - deep), (xb, hi - 0.03, zf), (xa, hi - 0.03, zf)], "grave_earth", (0.3, 0.27, 0.24, 1.0), facing=(0, 1, 0))
    beam(m, (xa, hi - 0.02), (xb, hi - 0.02), 0.05, zf - deep, 0.02, oak(0.7))
    for x in (xa + 0.12, xb - 0.12):
        for s in (-1, 1):
            m.poly([(x + s * 0.03, lo, zf), (x + s * 0.03, lo, zf - deep + 0.04), (x + s * 0.03, lo - 0.2, zf)], OAK, oak(0.7), facing=(s, 0, 0))
        m.poly([(x - 0.03, lo, zf - deep + 0.04), (x + 0.03, lo, zf - deep + 0.04), (x + 0.03, lo - 0.2, zf), (x - 0.03, lo - 0.2, zf)], OAK, oak(0.5), facing=(0, -1, -1))
    rnd = random.Random(seed * 31 + 7)
    n = max(int((xb - xa) / 0.26), 2)
    for i in range(n):
        x = xa + 0.1 + (xb - xa - 0.2) * (i + rnd.uniform(0.2, 0.8)) / n
        z = zf - deep * rnd.uniform(0.35, 0.7)
        green = rnd.random() < 0.6
        k = rnd.uniform(0.7, 1.3)
        col = (0.9 * k, 1.0 * k, 0.75 * k, 1.0) if green else (1.5 * k, 1.15 * k, 0.6 * k, 1.0)
        top = hi + rnd.uniform(0.08, 0.2)
        g.tube([(x, hi - 0.05, z), (x + rnd.uniform(-0.03, 0.03), hi + 0.04, z), (x + rnd.uniform(-0.05, 0.05), top - 0.04, z - 0.02), (x, top, z - 0.03)],
               [0.05, 0.1 * k, 0.075 * k, 0.015], 5, "yew", col)
        if rnd.random() < 0.75:
            # A trail over the front edge.
            fall = rnd.uniform(0.2, 0.5)
            zt = zf - deep
            xj = x + rnd.uniform(-0.08, 0.08)
            g.tube([(x, hi, zt + 0.05), (x, hi + 0.035, zt - 0.03), (xj, hi - fall * 0.5, zt - 0.06), (xj + rnd.uniform(-0.05, 0.05), hi - fall, zt - 0.045)],
                   [0.025, 0.04, 0.03, 0.006], 4, "yew", col)


def shutter(m, xa, xb, ya, yb, zf, hinge):
    """A boarded shutter thrown back flat against the wall, on two iron straps (`hinge`: the side it hangs on, -1 or 1)."""
    z = zf - 0.045
    n = max(int(round((xb - xa) / 0.2)), 2)
    for i in range(n):
        a, b = xa + (xb - xa) * i / n, xa + (xb - xa) * (i + 1) / n
        m.poly([(a + 0.006, ya, z), (b - 0.006, ya, z), (b - 0.006, yb, z), (a + 0.006, yb, z)], BOARDS, oak(0.85), facing=(0, 0, -1))
    m.poly([(xa, ya, z + 0.004), (xb, ya, z + 0.004), (xb, yb, z + 0.004), (xa, yb, z + 0.004)], GLASS, facing=(0, 0, -1))
    for x, s in ((xa, -1), (xb, 1)):
        m.poly([(x, ya, z), (x, yb, z), (x, yb, zf), (x, ya, zf)], BOARDS, oak(0.55), facing=(s, 0, 0))
    m.poly([(xa, ya, z), (xb, ya, z), (xb, ya, zf), (xa, ya, zf)], BOARDS, oak(0.5), facing=(0, -1, 0))
    for y in (ya + (yb - ya) * 0.18, ya + (yb - ya) * 0.8):
        beam(m, (xa + 0.03, y), (xb - 0.03, y), 0.1, z, 0.03, oak(0.7))
        x_h = xa if hinge < 0 else xb
        x_e = x_h - hinge * (xb - xa) * 0.7
        m.box((min(x_h, x_e), y - 0.022, z - 0.04), (max(x_h, x_e), y + 0.022, z - 0.03), IRON, IRON_C, faces="xXzyY")


def iron_arm(m, x, y, z_wall, reach, stay=0.4, r=0.016, span=0.78):
    """An iron arm out from the wall with a scrolled stay under it and a hook at its end."""
    z_end = z_wall - reach
    m.box((x - r, y - r, z_end), (x + r, y + r, z_wall), IRON, IRON_C, faces="xXzyY")
    pts = []
    for j in range(7):
        a = math.pi * 0.5 * j / 6
        pts.append((x, y - stay * (1.0 - math.sin(a)), z_wall - reach * span * (1.0 - math.cos(a)) - 0.01))
    m.tube(pts, [r * 0.75] * len(pts), 4, IRON, IRON_C)
    # A curl at its end.
    curl = [(x, y + 0.02 + 0.05 * math.sin(a), z_end - 0.05 + 0.05 * math.cos(a)) for a in [math.pi * 1.5 * j / 6 - math.pi * 0.5 for j in range(7)]]
    m.tube([(x, y, z_end + 0.02)] + curl, [r * 0.7] * 8, 4, IRON, IRON_C)
    return z_end


def lamp_arm(m, lamp):
    """The arm a lantern hangs from (the scene hangs the lamp: its chains rise half a metre to the hook)."""
    x, y, z = lamp
    top = y + 0.56
    iron_arm(m, x, top, ZB - 0.08, ZB - 0.08 - z + 0.05, stay=0.12)
    m.box((x - 0.01, y + 0.5, z - 0.01), (x + 0.01, top, z + 0.01), IRON, IRON_C, faces="xXzZ")


def sign(m, x, y, zf):
    """The sign: two keys crossed, gold on red, on a board hung from an iron arm over the lane, to be read from up it and down it."""
    z_end = iron_arm(m, x, y, zf, 1.5, stay=0.62, r=0.022, span=0.3)
    zc = zf - 0.92
    half_w, top, foot = 0.4, y - 0.14, y - 1.12
    red = (0.04, 0.01, 0.008, 1.0)
    gold = (0.125, 0.085, 0.028, 1.0)
    m.box((x - 0.022, foot, zc - half_w), (x + 0.022, top, zc + half_w), "painted", red)
    # An oak frame round the board, and the two links it hangs by.
    for ya, yb, za, zb in ((foot - 0.035, foot + 0.02, zc - half_w - 0.035, zc + half_w + 0.035), (top - 0.02, top + 0.035, zc - half_w - 0.035, zc + half_w + 0.035),
                           (foot, top, zc - half_w - 0.035, zc - half_w + 0.02), (foot, top, zc + half_w - 0.02, zc + half_w + 0.035)):
        m.box((x - 0.035, ya, za), (x + 0.035, yb, zb), OAK, oak(0.8))
    for z in (zc - half_w * 0.7, zc + half_w * 0.7):
        m.box((x - 0.008, top + 0.03, z - 0.012), (x + 0.008, y, z + 0.012), IRON, IRON_C, faces="xXzZ")
    cy = (top + foot) * 0.5

    def key(way, xf, s):
        """One key lying aslant: its bow low, its bit high and turned outward."""
        d = (way * math.sin(math.radians(32)), math.cos(math.radians(32)))
        q = (d[1], -d[0])
        if q[0] * way < 0:
            q = (-q[0], -q[1])
        at = lambda a, b: (xf, cy + d[1] * a + q[1] * b, zc + d[0] * a + q[0] * b)
        put = lambda pts: m.poly(pts, "painted", gold, facing=(s, 0, 0))
        put([at(-0.2, -0.021), at(0.38, -0.021), at(0.38, 0.021), at(-0.2, 0.021)])
        for i in range(8):
            a0, a1 = math.tau * i / 8, math.tau * (i + 1) / 8
            put([at(-0.28 + 0.045 * math.cos(a0), 0.045 * math.sin(a0)), at(-0.28 + 0.045 * math.cos(a1), 0.045 * math.sin(a1)),
                 at(-0.28 + 0.095 * math.cos(a1), 0.095 * math.sin(a1)), at(-0.28 + 0.095 * math.cos(a0), 0.095 * math.sin(a0))])
        put([at(0.22, 0.021), at(0.27, 0.021), at(0.27, 0.12), at(0.22, 0.12)])
        put([at(0.31, 0.021), at(0.37, 0.021), at(0.37, 0.12), at(0.31, 0.12)])
        put([at(0.22, 0.085), at(0.37, 0.085), at(0.37, 0.12), at(0.22, 0.12)])

    for s in (-1, 1):
        for way in (-1, 1):
            key(way, x + s * (0.0235 + 0.001 * (way + 2)), s)
    return z_end


def door_case(m):
    """The street door's carved case: two moulded posts standing a hand out from the wall, a head with a low
    arch cut in it and a sunk spandrel each side, a hood over it; the wall's thickness behind; a worn stone threshold."""
    x0, x1, _, top = DOOR
    out = -0.24
    stone = cp.rgba(cp.STONE, 0.62)
    # The threshold: one worn slab through the wall, a thumb high.
    m.box((x0 - 0.3, 0.0, -0.34), (x1 + 0.3, 0.05, 0.0), "stone_ashlar", stone, faces="xXzY")
    m.box((x0, 0.0, 0.0), (x1, 0.05, plan.WALL), "stone_ashlar", cp.rgba(cp.STONE, 0.55), faces="ZY")
    # The wall's thickness: oak linings.
    lining = oak(0.7)
    for x, s in ((x0, 1), (x1, -1)):
        m.poly([(x, 0.05, out), (x, top, out), (x, top, plan.WALL), (x, 0.05, plan.WALL)], BOARDS, lining, facing=(s, 0, 0))
    m.poly([(x0, top, 0.0), (x1, top, 0.0), (x1, top, plan.WALL), (x0, top, plan.WALL)], BOARDS, oak(0.5), facing=(0, -1, 0))
    for s in (-1, 1):
        xi, xo = s * x1, s * (x1 + 0.26)
        c = oak(0.9)
        m.poly([(xi, 0.05, out), (xo, 0.05, out), (xo, top, out), (xi, top, out)], OAK, c, facing=(0, 0, -1))
        m.poly([(xo, 0.05, out), (xo, top, out), (xo, top, 0.0), (xo, 0.05, 0.0)], OAK, oak(0.6), facing=(s, 0, 0))
        # A shaft worked on its face, with a cap and a base.
        xs = s * (x1 + 0.13)
        m.tube([(xs, 0.42, out + 0.025), (xs, 1.86, out + 0.025), ], [0.04, 0.04], 6, OAK, oak(1.0))
        m.box((xs - 0.07, 0.05, out - 0.018), (xs + 0.07, 0.42, out), OAK, oak(0.8), faces="xXzY")
        m.box((xs - 0.075, 1.86, out - 0.018), (xs + 0.075, 2.0, out), OAK, oak(0.9), faces="xXzyY")
    # The head: its face, the arch cut under it, the spandrels sunk in it.
    rise = 0.42
    spring = top - rise
    half = x1
    n = 8
    arch = [(half * math.cos(math.pi * i / (2 * n)), spring + rise * math.sin(math.pi * i / (2 * n)) ** 0.85) for i in range(n + 1)]
    for s in (-1, 1):
        col = oak(0.72)
        for (xa, ya), (xb, yb) in zip(arch, arch[1:]):
            front = [(s * xa, ya, out + 0.03), (s * xb, yb, out + 0.03), (s * xb, top, out + 0.03), (s * xa, top, out + 0.03)]
            m.poly([q for i, q in enumerate(front) if math.dist(q, front[i - 1]) > 1e-4], OAK, col, facing=(0, 0, -1))
            m.poly([(s * xa, ya, out + 0.03), (s * xb, yb, out + 0.03), (s * xb, yb, 0.0), (s * xa, ya, 0.0)], OAK, oak(0.5), facing=(-s * (yb - ya), -1, 0))
            # The arch's moulded edge.
            m.poly([(s * xa, ya, out), (s * xb, yb, out), (s * xb * 0.93 + s * 0.0, yb + 0.05, out), (s * xa * 0.93, ya + 0.05, out)], OAK, oak(1.0), facing=(0, 0, -1))
        # A boss in the spandrel.
        bx, by = s * half * 0.72, top - 0.085
        m.poly([(bx + 0.055 * math.cos(math.tau * i / 6), by + 0.055 * math.sin(math.tau * i / 6), out + 0.012) for i in range(6)], OAK, oak(1.1), facing=(0, 0, -1))
    m.box((x0 - 0.3, top, out - 0.02), (x1 + 0.3, top + 0.3, 0.0), OAK, oak(0.9), faces="xXzyY")
    m.box((x0 - 0.36, top + 0.3, out - 0.1), (x1 + 0.36, top + 0.37, 0.0), OAK, oak(0.8), faces="xXzyY")
    m.poly([(x0 - 0.36, top + 0.37, out - 0.1), (x1 + 0.36, top + 0.37, out - 0.1), (x1 + 0.36, top + 0.47, 0.0), (x0 - 0.36, top + 0.47, 0.0)], OAK, oak(0.7),
           facing=(0, 1, -1))
    # Carving along the head: a row of sunk squares.
    for i in range(9):
        x = -0.72 + 1.44 * i / 8
        m.poly([(x - 0.045, top + 0.15, out - 0.021), (x, top + 0.1, out - 0.021), (x + 0.045, top + 0.15, out - 0.021), (x, top + 0.2, out - 0.021)], OAK, oak(0.45),
               facing=(0, 0, -1))
    return (x0 - 0.36, x1 + 0.36, 0.0, top + 0.47)


def porter_window(m):
    """The porter's window at the top right, really open. The hole in the wall (the plan's) is 0.3 m deep; from
    its outer edge the reveal splays out through the two jetties' depth to an opening on the top storey's face
    as big as the hole looks from where he stands and a margin more, so nothing of it narrows his view of the
    gate and the court. Its shutters are thrown back against the wall."""
    x0, x1, y0, y1 = PW
    ox0, ox1, oy0, oy1 = PW_OUT
    zo = ZC
    lining = oak(0.8)
    # The hole's own depth, lined with oak.
    for pts, f in (([(x0, y0, 0.0), (x0, y1, 0.0), (x0, y1, plan.WALL), (x0, y0, plan.WALL)], (1, 0, 0)),
                   ([(x1, y0, 0.0), (x1, y1, 0.0), (x1, y1, plan.WALL), (x1, y0, plan.WALL)], (-1, 0, 0)),
                   ([(x0, y0, 0.0), (x1, y0, 0.0), (x1, y0, plan.WALL), (x0, y0, plan.WALL)], (0, 1, 0)),
                   ([(x0, y1, 0.0), (x1, y1, 0.0), (x1, y1, plan.WALL), (x0, y1, plan.WALL)], (0, -1, 0))):
        m.poly(pts, BOARDS, lining, facing=f)
    # The splay: boarded cheeks and head, dark, and a boarded sill falling outward.
    for pts, f, k in (([(x0, y0, 0.0), (x0, y1, 0.0), (ox0, oy1, zo), (ox0, oy0, zo)], (1, 0, -0.3), 0.6),
                      ([(x1, y0, 0.0), (x1, y1, 0.0), (ox1, oy1, zo), (ox1, oy0, zo)], (-1, 0, -0.3), 0.6),
                      ([(x0, y1, 0.0), (x1, y1, 0.0), (ox1, oy1, zo), (ox0, oy1, zo)], (0, -1, -0.3), 0.45),
                      ([(x0, y0, 0.0), (x1, y0, 0.0), (ox1, oy0, zo), (ox0, oy0, zo)], (0, 1, -0.3), 0.75)):
        m.poly(pts, BOARDS, oak(k), facing=f)
    # Its frame on the face, standing on the jetty's beam.
    for x in (ox0 - 0.065, ox1 + 0.065):
        beam(m, (x, oy0 - 0.04), (x, oy1 + 0.13), 0.13, zo, 0.09)
    beam(m, (ox0 - 0.13, oy1 + 0.065), (ox1 + 0.13, oy1 + 0.065), 0.13, zo, 0.1)
    m.box((ox0 - 0.13, oy0 - 0.03, zo - 0.09), (ox1 + 0.13, oy0, zo), OAK, oak(0.9), faces="xXzY")
    shutter(m, ox0 - 0.86, ox0 - 0.14, oy0 + 0.04, oy1 - 0.02, zo, 1)
    shutter(m, ox1 + 0.14, ox1 + 0.76, oy0 + 0.04, oy1 - 0.02, zo, -1)
    return [(ox0 - 0.13, ox1 + 0.13, oy0 - 0.05, oy1 + 0.14), (ox0 - 0.88, ox0 - 0.12, oy0, oy1), (ox1 + 0.12, ox1 + 0.78, oy0, oy1)]


def gable(m, panes, name, xa, xb, tint, seed):
    """One of the two gables to the street: studs and a collar, a small window into the roof space, carved bargeboards."""
    zf = ZG
    mid = (xa + xb) * 0.5
    half = (xb - xa) * 0.5
    rise = PEAK - EAVES
    top = lambda x: EAVES + rise * (1.0 - abs(x - mid) / half)
    # The plaster, cut small so the tint has something to hold.
    xs = cp.steps(xa, xb, 1.0)
    for x0, x1 in zip(xs, xs[1:]):
        for v0, v1 in ((0.0, 0.5), (0.5, 1.0)):
            pts = [(x0, lerp(EAVES, top(x0), v0), zf), (x1, lerp(EAVES, top(x1), v0), zf), (x1, lerp(EAVES, top(x1), v1), zf), (x0, lerp(EAVES, top(x0), v1), zf)]
            pts = [q for i, q in enumerate(pts) if math.dist(q, pts[i - 1]) > 1e-4]
            if len(pts) >= 3:
                m.poly(pts, DAUB, [tint(*q) for q in pts], facing=(0, 0, -1))
    bressummer(m, EAVES, zf, xa, xb)
    wy, ww, wh = EAVES + 0.72, 1.0, 0.8
    opening = glazed(m, panes, name, mid - ww * 0.5, mid + ww * 0.5, wy, wy + wh, zf, lights=2, transom=0.0)
    collar = EAVES + rise * 0.56
    half_c = half * (1.0 - 0.56) - 0.12
    beam(m, (mid - half_c, collar), (mid + half_c, collar), 0.16, zf, 0.06)
    # The rafters' feet on the face, under the bargeboards.
    for s in (-1, 1):
        beam(m, (mid + s * (half - 0.12), EAVES + 0.3), (mid, PEAK - 0.16), 0.2, zf, 0.06, oak(0.8))
    n = int(round((xb - xa) / 0.4))
    for i in range(1, n):
        x = xa + (xb - xa) * i / n + random.uniform(-0.02, 0.02)
        hi = top(x) - 0.2
        for a, b in clear_spans(x, EAVES + 0.3, hi, [opening, (mid - half_c, mid + half_c, collar - 0.07, collar + 0.07)]):
            beam(m, (x, a), (x, b), random.uniform(0.15, 0.2), zf, 0.05)


def bargeboard(m, x_foot, y_foot, x_peak, y_peak, z, thick=0.07):
    """A bargeboard down a gable's edge, its lower edge cut in cusps."""
    n = 9
    c = oak(0.7)
    dark = (c[0] * 0.6, c[1] * 0.6, c[2] * 0.6, 1.0)
    upper, lower = [], []
    for i in range(n * 4 + 1):
        t = i / (n * 4)
        x, y = lerp(x_foot, x_peak, t), lerp(y_foot, y_peak, t)
        cusp = abs(math.sin(math.pi * n * t))
        upper.append((x, y + 0.03))
        lower.append((x, y - 0.22 - 0.13 * cusp ** 0.6))
    for (ua, ub, la, lb) in zip(upper, upper[1:], lower, lower[1:]):
        for zz, f in ((z, -1), (z + thick, 1)):
            m.poly([(la[0], la[1], zz), (lb[0], lb[1], zz), (ub[0], ub[1], zz), (ua[0], ua[1], zz)], OAK, c, facing=(0, 0, f))
        m.poly([(la[0], la[1], z), (lb[0], lb[1], z), (lb[0], lb[1], z + thick), (la[0], la[1], z + thick)], OAK, dark, facing=(0, -1, 0))


def roof_slope(m, x_eave, x_ridge, z0, z1, over, seed):
    """One slope of a gable roof whose ridge runs back from the street: from its eave (at x_eave, overhanging
    by `over`) up to the ridge, which sags along its length. Tiles by UV; the underside dark."""
    s = 1.0 if x_eave > x_ridge else -1.0
    run = abs(x_eave - x_ridge)
    pitch = (PEAK - EAVES) / run
    zs = cp.steps(z0, z1, 1.9)
    us = [-over / run, 0.0, 0.34, 0.67, 1.0] if over else [0.0, 0.34, 0.67, 1.0]
    slope = math.hypot(run, PEAK - EAVES)

    def at(u, z):
        t = (z - z0) / (z1 - z0)
        sag = 0.2 * math.sin(math.pi * t) * max(u, 0.0)
        wave = 0.03 * fbm(z * 0.9, u * 3.0, 1.0, 2, seed) * (1.0 if 0.0 < u < 1.0 else 0.0)
        return (lerp(x_eave, x_ridge, u), EAVES + (PEAK - EAVES) * u - sag + wave, z)

    def colour(u, z):
        k = 0.82 + 0.22 * fbm(z * 0.6, u * 2.0 + seed, 1.0, 3, seed + 2.0)
        damp = 1.0 - 0.3 * (1.0 - smoothstep(0.0, 0.3, u))
        return (TILE[0] * k * damp, TILE[1] * k * damp, TILE[2] * k * damp * 0.98, 1.0)

    for za, zb in zip(zs, zs[1:]):
        for ua, ub in zip(us, us[1:]):
            grid = [(ua, za), (ua, zb), (ub, zb), (ub, za)]
            pts = [at(u, z) for u, z in grid]
            uv = [(z / 1.8, u * slope / 1.8) for u, z in grid]
            m.poly(pts, ROOF, [colour(u, z) for u, z in grid], uv, facing=(s * pitch, 1, 0))
            m.poly(pts, OAK, (0.16, 0.15, 0.15, 1.0), facing=(-s * pitch, -1, 0))
    return at


def roofs(m):
    """Twin roofs, their ridges running back from the two gables, a lead valley between them, crested ridges."""
    z0, z1 = ZG - 0.36, BACK + 0.25
    for k, (xa, xb) in enumerate(((X0, 0.0), (0.0, X1))):
        mid = (xa + xb) * 0.5
        left = roof_slope(m, xa, mid, z0, z1, 0.22 if k == 0 else 0.0, 3.0 + k)
        roof_slope(m, xb, mid, z0, z1, 0.22 if k == 1 else 0.0, 5.0 + k)
        # Ridge tiles: a low cap along the ridge, lifted at each joint.
        zs = cp.steps(z0, z1, 0.95)
        for za, zb in zip(zs, zs[1:]):
            ya, yb = left(1.0, za)[1] + 0.02, left(1.0, zb)[1] + 0.02
            c = cp.rgba(TILE, random.uniform(0.6, 0.85))
            for s in (-1, 1):
                m.poly([(mid + s * 0.19, ya - 0.17, za), (mid + s * 0.19, yb - 0.17, zb), (mid, yb + 0.06, zb), (mid, ya + 0.09, za)], ROOF, c,
                       [(0.0, 0.0), (0.5, 0.0), (0.5, 0.15), (0.0, 0.15)], facing=(s, 1, 0))
        # Bargeboards on the street verge, and a pendant post where they meet.
        zb_ = z0 - 0.01
        for xe, over in ((xa, 0.22 if k == 0 else 0.0), (xb, 0.22 if k == 1 else 0.0)):
            s = 1.0 if xe > mid else -1.0
            pitch = (PEAK - EAVES) / abs(xe - mid)
            bargeboard(m, xe + s * over, EAVES - pitch * over, mid, PEAK, zb_)
        m.box((mid - 0.07, PEAK - 0.75, zb_ - 0.03), (mid + 0.07, PEAK + 0.55, zb_ + 0.1), OAK, oak(0.8))
        m.tube([(mid, PEAK - 0.75, zb_ + 0.035), (mid, PEAK - 0.86, zb_ + 0.035), (mid, PEAK - 0.95, zb_ + 0.035)], [0.07, 0.1, 0.015], 6, OAK, oak(0.7))
        m.tube([(mid, PEAK + 0.55, zb_ + 0.035), (mid, PEAK + 0.66, zb_ + 0.035), (mid, PEAK + 0.8, zb_ + 0.035)], [0.07, 0.09, 0.01], 6, OAK, oak(0.7))
    # The valley: lead, and a spout to throw its water clear of the front.
    lead = (0.5, 0.5, 0.52, 1.0)
    for s in (-1, 1):
        m.poly([(0.0, EAVES + 0.03, z0), (0.0, EAVES + 0.03, z1), (s * 0.3, EAVES + 0.36, z1), (s * 0.3, EAVES + 0.36, z0)], "lead_roof", lead, facing=(-s, 1, 0))
    m.box((-0.1, EAVES - 0.1, z0 - 0.55), (0.1, EAVES + 0.04, z0 + 0.1), "lead_roof", lead, faces="xXzy")
    m.poly([(-0.1, EAVES + 0.0, z0 - 0.55), (0.1, EAVES + 0.0, z0 - 0.55), (0.1, EAVES + 0.0, z0 + 0.1), (-0.1, EAVES + 0.0, z0 + 0.1)], GLASS, facing=(0, 1, 0))


def chimney(m):
    """The hearth's stack, up through the north roof against the back wall: rubble, with a weathered cap."""
    cx, z0, z1 = -1.0, BACK - 1.05, BACK - 0.05
    lo, hi = EAVES, PEAK + 1.5
    tint = cp.stone_tint(lo, hi, seed=4.0, worn=0.5)
    cp.slab(m, (cx - 0.7, lo, z0), (cx + 0.7, hi, z1), "stone_rubble", tint, faces="xXzZ", step=1.2)
    cp.block(m, (cx - 0.8, hi, z0 - 0.1), (cx + 0.8, hi + 0.16, z1 + 0.1), "stone_ashlar", cp.rgba(cp.STONE, 0.6))
    cp.block(m, (cx - 0.62, hi + 0.16, z0 + 0.08), (cx + 0.62, hi + 0.42, z1 - 0.08), "stone_ashlar", cp.rgba(cp.STONE, 0.5), faces="xXzZY")
    m.poly([(cx - 0.45, hi + 0.425, z0 + 0.22), (cx + 0.45, hi + 0.425, z0 + 0.22), (cx + 0.45, hi + 0.425, z1 - 0.22), (cx - 0.45, hi + 0.425, z1 - 0.22)], GLASS,
           facing=(0, 1, 0))


def sides_and_back(m, tint):
    """What is seldom or never seen but keeps the weather and the light out: the side walls (the neighbours
    hide all but the top storey and the jetties' cheeks), the back, the back gables."""
    for x, s in ((X0, -1), (X1, 1)):
        cp.panel(m, (x, ZA), (x, BACK), 0.0, F2, (s, 0, 0), DAUB, tint, 5.0, 3.0)
        cp.panel(m, (x, ZB), (x, ZA), F1, F2, (s, 0, 0), DAUB, tint, 1.0, 1.5)
        cp.panel(m, (x, ZC), (x, BACK), F2, EAVES, (s, 0, 0), DAUB, tint, 2.2, 1.4)
        for y in (F1 + 0.14, F2 - 0.1):
            ht.side_beam(m, x, (ZB, y), (ZA, y), 0.22, s)
        for y in (F2 + 0.13, EAVES - 0.1, (F2 + EAVES) * 0.5):
            ht.side_beam(m, x, (ZC, y), (BACK, y), 0.2, s)
        ht.side_beam(m, x, (ZB + 0.1, F1), (ZB + 0.1, F2), 0.2, s)
        z = ZC + 0.1
        while z < BACK:
            ht.side_beam(m, x, (z, F2), (z, EAVES), 0.18, s)
            z += 0.9
        # The gable jetty's cheek.
        m.poly([(x, EAVES, ZG), (x, EAVES, ZC), (x, EAVES + 0.3, ZC), (x, EAVES + 0.3, ZG)], OAK, oak(0.7), facing=(s, 0, 0))
    cp.panel(m, (X0, BACK), (X1, BACK), 0.0, EAVES, (0, 0, 1), DAUB, tint, 4.0, 3.0)
    for xa, xb in ((X0, 0.0), (0.0, X1)):
        pts = [(xa, EAVES, BACK), (xb, EAVES, BACK), ((xa + xb) * 0.5, PEAK, BACK)]
        m.poly(pts, DAUB, [tint(*q) for q in pts], facing=(0, 0, 1))


def build():
    ht.TONE = (0.3, (1.0, 0.94, 0.86))
    ht.BEAM[0] = OAK
    random.seed(1420)
    m = Old("CrossKeys")
    g = Old("Greens")
    panes = []
    win = {w[0]: w for w in plan.WINDOWS}

    def rect(name):
        _, _, along, sill, width, height = win[name]
        return (along - width * 0.5, along + width * 0.5, sill, sill + height)

    dark = lambda x, y, z: (0.0, 0.0, 0.0, 1.0)

    # ---- The ground floor: a stone plinth, close studding, the door in its case, an arched window each side.
    tint = ht.plaster_tint(PLASTER, 0.0, F1, 1.0)
    door_hole = (DOOR[0], DOOR[1], DOOR[2], DOOR[3])
    wall(m, X0, X1, 0.0, F1, ZA, tint, [door_hole])
    wall(m, X0, X1, 0.0, F1, ZA + 0.01, dark, [door_hole], out=1, mat=GLASS)
    case = door_case(m)
    st = cp.stone_tint(0.0, 0.6, seed=2.0, worn=0.8)
    for xa, xb in ((X0 - 0.04, case[0] + 0.1), (case[1] - 0.1, X1 + 0.04)):
        cp.slab(m, (xa, 0.0, -0.055), (xb, 0.52, 0.0), STONE, st, faces="xXzY", step=1.3)
    openings = [case]
    for name in ("Window0_0", "Window0_1"):
        xa, xb, ya, yb = rect(name)
        openings.append(glazed(m, panes, name, xa, xb, ya, yb, ZA, lights=3, transom=0.0, arched=True))
        # Two iron bars across each light, as a ground-floor window has, and a shallow trough under the sill.
        for y in (ya + 0.42, ya + 0.84):
            m.box((xa, y - 0.012, ZA - 0.05), (xb, y + 0.012, ZA - 0.03), IRON, IRON_C, faces="zyY")
        window_box(m, g, xa + 0.05, xb - 0.05, ya - 0.1, ZA - 0.03, deep=0.14, seed=len(openings))
        openings.append((xa, xb, ya - 0.36, ya))
    beam(m, (X0, 0.63), (case[0] + 0.1, 0.63), 0.22, ZA, 0.085)
    beam(m, (case[1] - 0.1, 0.63), (X1, 0.63), 0.22, ZA, 0.085)
    beam(m, (X0, F1 - 0.1), (X1, F1 - 0.1), 0.2, ZA, 0.07)
    posts0 = (-5.86, -4.5, -1.9, -1.0, 1.0, 1.9, 4.5, 5.86)
    for x in posts0:
        beam(m, (x, 0.52), (x, F1 - 0.2), 0.27 if abs(x) > 5.0 else 0.25, ZA, 0.09, oak(1.0))
        # A moulded cap where the bracket springs, above head height.
        m.box((x - 0.17, 2.3, ZA - 0.14), (x + 0.17, 2.38, ZA), OAK, oak(0.9), faces="xXzyY")
        m.box((x - 0.15, 2.38, ZA - 0.115), (x + 0.15, 2.43, ZA), OAK, oak(0.75), faces="xXzY")
    for xa, xb in zip(posts0, posts0[1:]):
        if xa != -1.0:
            studs(m, xa + 0.12, xb - 0.12, 0.74, F1 - 0.2, ZA, openings)

    # ---- The first floor: out half a metre on carved brackets; three wide leaded windows with boxes under them.
    tint = ht.plaster_tint(PLASTER, F1, F2, 2.0)
    wall(m, X0, X1, F1, F2, ZB, tint)
    wall(m, X0, X1, F1, F2, ZB + 0.01, dark, out=1, mat=GLASS)
    jetty(m, F1, ZA, ZB, posts0, 0.54)
    bressummer(m, F1, ZB)
    openings = []
    for i, name in enumerate(("Window1_0", "Window1_1", "Window1_2")):
        xa, xb, ya, yb = rect(name)
        openings.append(glazed(m, panes, name, xa, xb, ya, yb, ZB, lights=4, transom=0.6))
        window_box(m, g, xa + 0.05, xb - 0.05, ya - 0.1, ZB - 0.02, seed=10 + i)
        openings.append((xa - 0.05, xb + 0.05, ya - 0.56, ya))
    beam(m, (X0, F2 - 0.1), (X1, F2 - 0.1), 0.2, ZB, 0.07)
    posts1 = (-5.86, -4.64, -2.36, -1.14, 1.14, 2.36, 4.64, 5.86)
    for x in posts1:
        beam(m, (x, F1 + 0.3), (x, F2 - 0.2), 0.24, ZB, 0.085, oak(1.0))
    rail(m, X0 + 0.24, X1 - 0.24, F1 + 0.58, ZB, [(p - 0.12, p + 0.12, 0, 99) for p in posts1[1:-1]])
    for xa, xb in zip(posts1, posts1[1:]):
        studs(m, xa + 0.12, xb - 0.12, F1 + 0.65, F2 - 0.2, ZB, openings)
        studs(m, xa + 0.12, xb - 0.12, F1 + 0.3, F1 + 0.51, ZB, [])

    # ---- The top floor: out a hand more; a leaded window, and the porter's open one with its shutters back.
    tint = ht.plaster_tint(PLASTER, F2, EAVES, 3.0)
    wall(m, X0, X1, F2, EAVES, ZC, tint, [PW_OUT])
    wall(m, X0, X1, F2, EAVES, ZC + 0.01, dark, [PW_OUT], out=1, mat=GLASS)
    jetty(m, F2, ZB, ZC, posts1, 0.42)
    bressummer(m, F2, ZC, gap=(PW_OUT[0] - 0.13, PW_OUT[1] + 0.13))
    openings = porter_window(m)
    xa, xb, ya, yb = rect("Window2_0")
    openings.append(glazed(m, panes, "Window2_0", xa, xb, ya, yb, ZC, lights=3, transom=0.6))
    window_box(m, g, xa + 0.05, xb - 0.05, ya - 0.1, ZC - 0.02, seed=20)
    openings.append((xa - 0.05, xb + 0.05, ya - 0.56, ya))
    beam(m, (X0, EAVES - 0.1), (X1, EAVES - 0.1), 0.2, ZC, 0.07)
    posts2 = (-5.86, -4.6, -3.4, -1.4, 0.0, 2.0, 5.86)
    for x in posts2:
        beam(m, (x, F2 + 0.3), (x, EAVES - 0.2), 0.24, ZC, 0.085, oak(1.0))
    rail(m, X0 + 0.24, X1 - 0.24, F2 + 0.6, ZC, openings + [(p - 0.12, p + 0.12, 0, 99) for p in posts2[1:-1]])
    for xa, xb in zip(posts2, posts2[1:]):
        studs(m, xa + 0.12, xb - 0.12, F2 + 0.67, EAVES - 0.2, ZC, openings)
        studs(m, xa + 0.12, xb - 0.12, F2 + 0.3, F2 + 0.53, ZC, openings)

    # ---- The gables and the roofs.
    jetty(m, EAVES, ZC, ZG, posts2, 0.42)
    tint = ht.plaster_tint(PLASTER, EAVES, PEAK, 4.0)
    gable(m, panes, "Window3_0", X0, 0.0, tint, 1.0)
    gable(m, panes, "Window3_1", 0.0, X1, tint, 2.0)
    for xa, xb in ((X0, 0.0), (0.0, X1)):
        pts = [(xa, EAVES, ZG + 0.01), (xb, EAVES, ZG + 0.01), ((xa + xb) * 0.5, PEAK, ZG + 0.01)]
        m.poly(pts, GLASS, facing=(0, 0, 1))
    roofs(m)
    chimney(m)
    sides_and_back(m, ht.plaster_tint(PLASTER, 0.0, EAVES, 5.0))

    # ---- Ironwork: the lantern arms and the sign.
    for lamp in LAMPS:
        lamp_arm(m, lamp)
    sign(m, -1.75, F2 - 0.42, ZB)

    shell = m.build()
    greens = g.build(smooth=True)
    check_view([shell, greens])
    for p in panes:
        p.build(origin=p.centre)


def check_view(objects):
    """Is the porter's view narrowed? Casts rays from where his eye is (and from a little to each side, lower,
    and closer to the window) through the hole in the wall, and counts those that anything of this model stops."""
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    deps = bpy.context.evaluated_depsgraph_get()
    trees = [BVHTree.FromObject(o, deps) for o in objects]
    x0, x1, y0, y1 = PW
    sx, sy, sz = plan.PORTER_STANDS
    eyes = {"where he stands": (sx, sy + 1.65, sz), "a step left": (sx - 0.2, sy + 1.65, sz), "a step right": (sx + 0.2, sy + 1.65, sz),
            "stooping": (sx, sy + 1.5, sz), "close to the wall": (sx, sy + 1.65, 0.72)}
    for name, eye in eyes.items():
        through = stopped = 0
        n = 48
        for i in range(n):
            for j in range(n):
                tx, ty = lerp(x0 + 0.004, x1 - 0.004, i / (n - 1)), lerp(y0 + 0.004, y1 - 0.004, j / (n - 1))
                # It must pass the hole's inner edge too.
                k = (eye[2] - plan.WALL) / eye[2]
                ix, iy = lerp(eye[0], tx, k), lerp(eye[1], ty, k)
                if not (x0 < ix < x1 and y0 < iy < y1):
                    continue
                through += 1
                o = Vector((eye[0], -eye[2], eye[1]))
                d = (Vector((tx, 0.0, ty)) - o).normalized()
                if any(t.ray_cast(o, d, 40.0)[0] is not None for t in trees):
                    stopped += 1
        print("porter's window, %s: %d of %d rays through the hole are stopped by the model" % (name, stopped, through))


def main():
    porter.reset(1420)
    build()
    porter.export("env_inn")


if __name__ == "__main__":
    main()
