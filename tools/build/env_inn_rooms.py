"""The Cross Keys from within (night 0, and any dusk the porter goes in):
the taproom, the loft of beds over it, and the top floor with the porter's
room. Everything is in the inn's own space (game/world/street/env_inn.tscn:
the street front faces -z, the origin is on the ground at the middle of the
front) and is laid over that scene's hidden Blocks, which are the collision.
The plan (walls, floors, stairs, windows, the two real openings) is
inn_plan.py's, shared with env_inn.py, which builds the outside.

`env_inn_rooms` (art/models/env_inn_rooms.glb), out to the walls' inner faces:
- Walls: close-studded oak and plaster, a wood-lined recess with mullions
  and dark panes for every window in the plan, the street door's and the
  porter's window's holes with their frames.
- Floors and ceilings: wide boards below with flags round the hearth,
  boards above; each ceiling the floor's boards seen from under, on joists
  and a bridging beam, the beam on posts with curved braces.
- Stairs: two straight flights over the scene's ramps, closed strings,
  boarded under, railed; rails round the wells.
- The hearth: stone jambs, an oak lintel and mantel shelf, a deep sooted
  opening (drawn inside the solid Hearth Block), the stack going up through
  the floors. The fire itself is prop_inn_fire.
- The counter, and behind it casks on a stillage under shelves of jugs.
- Upstairs: pegs and cloaks, a chest, the porter's room's plank partition,
  its door folded back, his window's shutter; stores at the top.

Props of its own (art/models/prop_inn_<name>.glb, with scenes in
game/world/props/): `fire` (firedogs, logs, embers, flames), `settle` (a
high-backed bench), `candle_ring` (an iron ring of candles on chains),
`lantern` (an iron lantern to hang from a post).

Nothing here has collision: the scene's Blocks (and its `Solids`) do that.

Run: tools/build.sh env_inn_rooms   (one part: ... -- rooms | fire | settle | candle_ring | lantern)
"""
import math
import os
import random
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
import city_parts as cp
import dress
import inn_plan as P
import prop_abbey_stores as st
import props
from porter import fbm, lerp, smoothstep
from props import CLOTH, IRON, IRON_C, OAK, OAK_DARK, PAINT, RUST_C, WOOD, beam, plank, rgba, tone

G = props.GRAIN
X0, X1, Z0, Z1 = P.INNER
F0, F1, F2 = P.FLOORS
C0, C1, C2 = P.CEILINGS
WELL1 = P.STAIR_UP_1
WELL2 = P.STAIR_UP_2
# The chimney: the breast over the hearth in the taproom, the stack above.
HEARTH = (-2.2, 0.2, 9.05, Z1)
BREAST = (-2.2, 0.2, 9.14, Z1)
STACK = (-1.8, -0.2, 9.25, Z1)
# The bridging beam under each floor runs along x here; the posts under it.
BEAM_Z = 4.9
POSTS = (-1.9, 1.9)
LOFT_POST = 1.9
TIE_Z = 4.5

PLASTER = "plaster_abbey"
STONE = "stone_blocks"
FLAGS = "flags_worn"
DARK = "window_dark"
# Timber tones (the texture darkens them): smoked oak overhead, the frame, trodden boards.
SMOKED = (0.42, 0.32, 0.23)
STUD = (0.52, 0.41, 0.3)
TROD = (0.63, 0.5, 0.37)
BLACK_IRON = (0.42, 0.4, 0.38, 1.0)


def col(c, k=1.0):
    return (c[0] * k, c[1] * k, c[2] * k, 1.0)


# ---------------------------------------------------------------- timber

AX = {"x": 0, "y": 1, "z": 2}


def wbox(m, lo, hi, along, colour=None, faces="xXyYzZ", mat=WOOD, end=0.6):
    """The named faces of a timber filling the box `lo`..`hi`, its grain
    along `along`. (props.plank makes all six; a joist under a ceiling or a
    board in a floor shows one or three.)"""
    c = colour or tone(SMOKED)
    c = col(c)
    g = AX[along]
    u0, v0 = random.random(), random.random()
    for name in faces:
        a = AX[name.lower()]
        high = name.isupper()
        o = [i for i in range(3) if i != a]
        pts = []
        for s1, s2 in ((0, 0), (1, 0), (1, 1), (0, 1)):
            p = [0.0, 0.0, 0.0]
            p[a] = hi[a] if high else lo[a]
            p[o[0]] = (hi if s1 else lo)[o[0]]
            p[o[1]] = (hi if s2 else lo)[o[1]]
            pts.append(tuple(p))
        if a == g:
            uvs = [(u0 + p[o[0]] * G, v0 + p[o[1]] * G * 0.3) for p in pts]
            k = end
        else:
            other = o[0] if o[1] == g else o[1]
            uvs = [(u0 + p[other] * G, v0 + p[g] * G) for p in pts]
            k = 1.0 + (0.08 if high else -0.08) * (1.0 if a == 1 else 0.0)
        facing = [0.0, 0.0, 0.0]
        facing[a] = 1.0 if high else -1.0
        m.poly(pts, mat, (c[0] * k, c[1] * k, c[2] * k, 1.0), uvs=uvs, facing=tuple(facing))


def minus(a0, a1, cutouts):
    """a0..a1 less the intervals in `cutouts`."""
    out = [(a0, a1)]
    for c0, c1 in cutouts:
        nxt = []
        for s0, s1 in out:
            if c1 <= s0 or c0 >= s1:
                nxt.append((s0, s1))
                continue
            if c0 > s0:
                nxt.append((s0, c0))
            if c1 < s1:
                nxt.append((c1, s1))
        out = nxt
    return [s for s in out if s[1] - s[0] > 1e-3]


def cuts(a, b, marks, step):
    """a..b cut at `marks`, and no piece longer than `step`."""
    pts = sorted(set([a, b] + [q for q in marks if a + 1e-4 < q < b - 1e-4]))
    out = [pts[0]]
    for p0, p1 in zip(pts, pts[1:]):
        n = max(int(math.ceil((p1 - p0) / step - 1e-6)), 1)
        out += [p0 + (p1 - p0) * i / n for i in range(1, n + 1)]
    return out


def strips(a0, a1, wmin=0.24, wmax=0.36, marks=()):
    """a0..a1 cut into boards' widths, with a joint at each of `marks`."""
    edges = sorted(set([a0, a1] + [q for q in marks if a0 + 1e-4 < q < a1 - 1e-4]))
    out = []
    for e0, e1 in zip(edges, edges[1:]):
        x = e0
        while e1 - x > wmax * 1.5:
            w = random.uniform(wmin, wmax)
            out.append((x, x + w))
            x += w
        if e1 - x > wmax:
            out.append((x, (x + e1) * 0.5))
            out.append(((x + e1) * 0.5, e1))
        elif e1 - x > 1e-3:
            out.append((x, e1))
    return out


def lengths(a0, a1, lo, hi):
    """a0..a1 cut into boards' lengths."""
    out, x = [], a0
    first = True
    while a1 - x > hi:
        step = random.uniform(lo * (0.4 if first else 1.0), hi)
        out.append((x, x + step))
        x += step
        first = False
    out.append((x, a1))
    return out


def boards_plane(m, y, rect, holes, along, up, colour, shade=None, joints=None, gap=0.004, uneven=0.002, width=(0.24, 0.36)):
    """Boards lying side by side over `rect` (x0, x1, z0, z1) less `holes`,
    on the plane `y`: seen from above (`up`, a floor) or from below (a
    ceiling's boards between the joists). Only that face is made.
    `shade(x, z)` darkens a board by where it lies; `joints` (shortest,
    longest) cuts each run into boards."""
    x0, x1, z0, z1 = rect
    lie_x = along == "x"
    a0, a1, b0, b1 = (z0, z1, x0, x1) if lie_x else (x0, x1, z0, z1)
    marks = [q for h in holes for q in ((h[2], h[3]) if lie_x else (h[0], h[1]))]
    for sa, sb in strips(a0, a1, width[0], width[1], marks):
        sm = (sa + sb) * 0.5
        out = [((h[0], h[1]) if lie_x else (h[2], h[3])) for h in holes if (h[2] if lie_x else h[0]) < sm < (h[3] if lie_x else h[1])]
        for ra, rb in minus(b0, b1, out):
            for la, lb in (lengths(ra, rb, joints[0], joints[1]) if joints else [(ra, rb)]):
                lm = (la + lb) * 0.5
                k = shade(lm, sm) if lie_x and shade else shade(sm, lm) if shade else 1.0
                c = tone(colour, 0.13)
                c = (c[0] * k, c[1] * k, c[2] * k, 1.0)
                dy = random.uniform(-uneven, uneven)
                g = gap * 0.5
                if lie_x:
                    lo, hi = (la + g, y - 0.02 + dy, sa + g), (lb - g, y + dy, sb - g)
                else:
                    lo, hi = (sa + g, y - 0.02 + dy, la + g), (sb - g, y + dy, lb - g)
                if up:
                    wbox(m, lo, hi, along, c, faces="Y")
                else:
                    wbox(m, (lo[0], y + dy, lo[2]), (hi[0], y + 0.02 + dy, hi[2]), along, c, faces="y")


def under(m, y, rect, holes, up=True, colour=(0.03, 0.026, 0.022, 1.0)):
    """The dark between a floor's boards: one face just under them."""
    x0, x1, z0, z1 = rect
    zs = sorted(set([z0, z1] + [q for h in holes for q in (h[2], h[3]) if z0 < q < z1]))
    for za, zb in zip(zs, zs[1:]):
        zm = (za + zb) * 0.5
        for xa, xb in minus(x0, x1, [(h[0], h[1]) for h in holes if h[2] < zm < h[3]]):
            m.poly([(xa, y, za), (xb, y, za), (xb, y, zb), (xa, y, zb)], WOOD, colour, facing=(0, 1 if up else -1, 0))


def joists(m, y, xs, z0, z1, blocked, depth=0.17, wide=0.13, colour=SMOKED):
    """Joists along z under the ceiling `y`, stopping at whatever is in
    `blocked` (rectangles x0, x1, z0, z1: a well, a chimney, the beam they
    bear on)."""
    for x in xs:
        w = wide * random.uniform(0.9, 1.1)
        d = depth * random.uniform(0.94, 1.06)
        for za, zb in minus(z0, z1, [(r[2], r[3]) for r in blocked if r[0] < x < r[1]]):
            wbox(m, (x - w * 0.5, y - d, za), (x + w * 0.5, y, zb), "z", tone(colour, 0.14), faces="xXy")


def brace(m, a, b, ctrl, wide, thick, colour=None, n=7):
    """A curved brace from `a` to `b` (both in one upright plane), bowed
    toward `ctrl`: `wide` in its plane, `thick` across it."""
    c = col(colour or tone(SMOKED))
    hx, hz = b[0] - a[0], b[2] - a[2]
    hn = math.hypot(hx, hz) or 1.0
    e = (hz / hn, 0.0, -hx / hn)
    rings = []
    run = 0.0
    last = None
    u0 = random.random()
    for i in range(n + 1):
        t = i / n
        p = tuple((1 - t) ** 2 * a[k] + 2 * t * (1 - t) * ctrl[k] + t * t * b[k] for k in range(3))
        d = tuple(2 * (1 - t) * (ctrl[k] - a[k]) + 2 * t * (b[k] - ctrl[k]) for k in range(3))
        dn = math.sqrt(sum(q * q for q in d)) or 1.0
        d = tuple(q / dn for q in d)
        nrm = (e[1] * d[2] - e[2] * d[1], e[2] * d[0] - e[0] * d[2], e[0] * d[1] - e[1] * d[0])
        if last is not None:
            run += math.dist(p, last)
        last = p
        ring = []
        for s1, s2 in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            ring.append(tuple(p[k] + nrm[k] * s1 * wide * 0.5 + e[k] * s2 * thick * 0.5 for k in range(3)))
        rings.append((ring, p, run))
    for (ra, pa, la), (rb, pb, lb) in zip(rings, rings[1:]):
        mid = tuple((pa[k] + pb[k]) * 0.5 for k in range(3))
        for i in range(4):
            j = (i + 1) % 4
            pts = [ra[i], ra[j], rb[j], rb[i]]
            fm = tuple(sum(q[k] for q in pts) * 0.25 - mid[k] for k in range(3))
            uvs = [(u0 + i * 0.2, la * G), (u0 + i * 0.2 + 0.15, la * G), (u0 + i * 0.2 + 0.15, lb * G), (u0 + i * 0.2, lb * G)]
            m.poly(pts, WOOD, c, uvs=uvs, facing=fm)


# ---------------------------------------------------------------- walls

class Wall:
    """An upright plane seen from the room: `axis` "z" (it lies at z = `at`
    and runs along x) or "x" (at x = `at`, running along z), looking toward
    `sign`. p(u, y, d) is the point `u` along it, `y` up, `d` out into the
    room."""

    def __init__(self, axis, at, sign):
        self.axis, self.at, self.sign = axis, at, float(sign)
        self.n = (0.0, 0.0, self.sign) if axis == "z" else (self.sign, 0.0, 0.0)
        self.out = (self.n[0], self.n[2])

    def p(self, u, y, d=0.0):
        if self.axis == "z":
            return (u, y, self.at + self.sign * d)
        return (self.at + self.sign * d, y, u)

    def along(self, s=1.0):
        return (s, 0.0, 0.0) if self.axis == "z" else (0.0, 0.0, s)


FRONT = Wall("z", Z0, 1)
BACK = Wall("z", Z1, -1)
LEFT = Wall("x", X0, 1)
RIGHT = Wall("x", X1, -1)


def plaster_tint(y0, y1, seed, base=(1.0, 0.9, 0.72), smoke=0.4):
    """Limewash gone the colour of the smoke: darker under the ceiling,
    scuffed at the foot, blotched."""
    def tint(x, y, z):
        up = smoothstep(y1 - 1.1, y1, y) * smoke
        foot = (1.0 - smoothstep(y0, y0 + 0.5, y)) * 0.25
        blot = 0.84 + 0.22 * fbm(x * 0.9 + z * 0.9 + seed * 7.0, y, 0.6, 3, seed)
        k = blot * (1.0 - up) * (1.0 - foot)
        return (base[0] * k, base[1] * k, base[2] * k * (1.0 - 0.2 * up), 1.0)
    return tint


def face(m, W, u0, u1, y0, y1, holes, tint, mat=PLASTER, d=0.0, step=1.3):
    """A wall's face less its `holes` (u0, u1, y0, y1), cut small for the tint."""
    us = cuts(u0, u1, [q for h in holes for q in (h[0], h[1])], step)
    ys = cuts(y0, y1, [q for h in holes for q in (h[2], h[3])], step)
    for ua, ub in zip(us, us[1:]):
        for ya, yb in zip(ys, ys[1:]):
            um, ym = (ua + ub) * 0.5, (ya + yb) * 0.5
            if any(h[0] < um < h[1] and h[2] < ym < h[3] for h in holes):
                continue
            pts = [W.p(ua, ya, d), W.p(ub, ya, d), W.p(ub, yb, d), W.p(ua, yb, d)]
            m.poly(pts, mat, [tint(*q) for q in pts], facing=W.n)


def wtimber(m, W, ua, ub, ya, yb, proud=0.04, colour=None, grain=None, edges="lrbt", base=0.0):
    """A timber on a wall: its face `proud` of the wall and the named edges
    (left, right, bottom, top) back to `base`."""
    c = col(colour or tone(STUD))
    grain = grain or ("y" if (yb - ya) >= (ub - ua) else "u")
    o = (random.random(), random.random())

    def uv(u, y, d=0.0):
        return (o[0] + (u + d) * G, o[1] + y * G) if grain == "y" else (o[0] + (y + d) * G, o[1] + u * G)

    pts = [(ua, ya), (ub, ya), (ub, yb), (ua, yb)]
    m.poly([W.p(u, y, proud) for u, y in pts], WOOD, c, uvs=[uv(u, y) for u, y in pts], facing=W.n)
    dark = col(c, 0.72)
    for e, pa, pb, f in (("l", (ua, ya), (ua, yb), W.along(-1.0)), ("r", (ub, ya), (ub, yb), W.along(1.0)),
                         ("b", (ua, ya), (ub, ya), (0.0, -1.0, 0.0)), ("t", (ua, yb), (ub, yb), (0.0, 1.0, 0.0))):
        if e in edges:
            q = [W.p(pa[0], pa[1], base), W.p(pa[0], pa[1], proud), W.p(pb[0], pb[1], proud), W.p(pb[0], pb[1], base)]
            m.poly(q, WOOD, dark, uvs=[uv(pa[0], pa[1]), uv(pa[0], pa[1], proud - base), uv(pb[0], pb[1], proud - base), uv(pb[0], pb[1])], facing=f)


def wbrace(m, W, a, b, ctrl, wide=0.15, proud=0.047, colour=None, n=6):
    """A curved brace lying on a wall from (u, y) `a` to `b`, bowed toward `ctrl`."""
    c = col(colour or tone(STUD, 0.1))
    o = random.random()
    pts = []
    run = 0.0
    for i in range(n + 1):
        t = i / n
        p = tuple((1 - t) ** 2 * a[k] + 2 * t * (1 - t) * ctrl[k] + t * t * b[k] for k in range(2))
        d = tuple(2 * (1 - t) * (ctrl[k] - a[k]) + 2 * t * (b[k] - ctrl[k]) for k in range(2))
        dn = math.hypot(d[0], d[1]) or 1.0
        nrm = (-d[1] / dn * wide * 0.5, d[0] / dn * wide * 0.5)
        if pts:
            run += math.dist(p, pts[-1][2])
        pts.append(((p[0] + nrm[0], p[1] + nrm[1]), (p[0] - nrm[0], p[1] - nrm[1]), p, run))
    for (a0, a1, _p, la), (b0, b1, _q, lb) in zip(pts, pts[1:]):
        m.poly([W.p(a0[0], a0[1], proud), W.p(a1[0], a1[1], proud), W.p(b1[0], b1[1], proud), W.p(b0[0], b0[1], proud)], WOOD, c,
               uvs=[(o, la * G), (o + wide * G, la * G), (o + wide * G, lb * G), (o, lb * G)], facing=W.n)


def vboards(m, W, u0, u1, y0, y1, d=0.0, colour=STUD, holes=(), width=(0.2, 0.32), spread=0.14):
    """Upright boards side by side on a wall's plane (a partition, a
    boarded-in stair, the front of the counter)."""
    marks = [q for h in holes for q in (h[0], h[1])]
    for ua, ub in strips(u0, u1, width[0], width[1], marks):
        um = (ua + ub) * 0.5
        c = tone(colour, spread)
        o = random.random()
        for ya, yb in minus(y0, y1, [(h[2], h[3]) for h in holes if h[0] < um < h[1]]):
            pts = [(ua + 0.002, ya), (ub - 0.002, ya), (ub - 0.002, yb), (ua + 0.002, yb)]
            m.poly([W.p(u, y, d) for u, y in pts], WOOD, c, uvs=[(o + u * G, y * G) for u, y in pts], facing=W.n)


def window(m, W, uc, sill, w, h, depth=0.1):
    """A window that is never seen through, from within: a wood-lined
    recess, mullions, dark panes behind them, and its frame on the wall."""
    ua, ub, ya, yb = uc - w * 0.5, uc + w * 0.5, sill, sill + h
    wood = tone(STUD, 0.1)
    dark = col(wood, 0.6)
    for a, b, f in (((ua, ya), (ub, ya), (0.0, 1.0, 0.0)), ((ua, yb), (ub, yb), (0.0, -1.0, 0.0)),
                    ((ua, ya), (ua, yb), W.along(1.0)), ((ub, ya), (ub, yb), W.along(-1.0))):
        long = math.dist(a, b)
        m.poly([W.p(a[0], a[1], 0.0), W.p(b[0], b[1], 0.0), W.p(b[0], b[1], -depth), W.p(a[0], a[1], -depth)], WOOD, dark,
               uvs=[(0.0, 0.0), (0.0, long * G), (depth * G, long * G), (depth * G, 0.0)], facing=f)
    m.poly([W.p(ua, ya, -depth), W.p(ub, ya, -depth), W.p(ub, yb, -depth), W.p(ua, yb, -depth)], DARK, facing=W.n)
    n = max(int(round(w / 0.34)), 2)
    for i in range(1, n):
        u = ua + w * i / n
        wtimber(m, W, u - 0.028, u + 0.028, ya, yb, -depth + 0.07, col(wood, 0.9), edges="lr", base=-depth)
    if h >= 1.25:
        yt = ya + h * 0.6
        wtimber(m, W, ua, ub, yt - 0.03, yt + 0.03, -depth + 0.075, col(wood, 0.9), edges="bt", base=-depth)
    # Its frame on the wall: jambs, a head, and a sill that stands a little prouder.
    for a, b in ((ua - 0.13, ua), (ub, ub + 0.13)):
        wtimber(m, W, a, b, ya - 0.13, yb + 0.13, 0.044, tone(STUD), edges="lr")
    wtimber(m, W, ua - 0.13, ub + 0.13, yb, yb + 0.13, 0.048, tone(STUD), edges="bt")
    wtimber(m, W, ua - 0.16, ub + 0.16, ya - 0.13, ya, 0.05, tone(STUD), edges="btlr")


def framed_wall(m, W, u0, u1, y0, yc, y1, seed, windows=(), opens=(), base=(1.0, 0.9, 0.72), spacing=0.62, smoke=0.4, skip=()):
    """One storey of an outer wall from within: plaster between close-set
    studs, a sill, a plate under the ceiling `yc` (the face itself runs on up
    to the next floor, `y1`), a post at each end; `windows` (along, sill,
    width, height) get their recess, `opens` (u0, u1, y0, y1) are holes.
    Nothing is framed in `skip` (u0, u1): the chimney stands there."""
    tint = plaster_tint(y0, yc, seed, base, smoke)
    holes = [(uc - w * 0.5, uc + w * 0.5, sill, sill + h) for uc, sill, w, h in windows] + list(opens)
    face(m, W, u0, u1, y0, y1, holes, tint)
    for uc, sill, w, h in windows:
        window(m, W, uc, sill, w, h)
    cut = [(a - 0.2, b + 0.2, ya - 0.14, yb + 0.14) for a, b, ya, yb in holes]
    for a, b in minus(u0, u1, [(o[0] - 0.14, o[1] + 0.14) for o in opens if o[2] <= y0 + 0.01] + list(skip)):
        wtimber(m, W, a, b, y0, y0 + 0.14, 0.046, tone(STUD), edges="t")
    for a, b in minus(u0, u1, list(skip)):
        wtimber(m, W, a, b, yc - 0.2, yc, 0.05, tone(SMOKED), edges="b")
    n = max(int(round((u1 - u0 - 0.2) / spacing)), 1)
    for i in range(n + 1):
        end = i in (0, n)
        uc = u0 + 0.1 + (u1 - u0 - 0.2) * i / n + (0.0 if end else random.uniform(-0.03, 0.03))
        wd = 0.2 if end else random.uniform(0.13, 0.17)
        if any(a < uc < b for a, b in skip):
            continue
        for ya, yb in minus(y0 + 0.14, yc - 0.2, [(c[2], c[3]) for c in cut if c[0] < uc < c[1]]):
            wtimber(m, W, uc - wd * 0.5, uc + wd * 0.5, ya, yb, 0.04, tone(STUD), edges="lr")


def opening_frame(m, W, ua, ub, ya, yb, sill=False):
    """The timbers round a real opening: jambs, a head, and a sill if it is a window."""
    for a, b in ((ua - 0.14, ua), (ub, ub + 0.14)):
        wtimber(m, W, a, b, ya - (0.12 if sill else 0.0), yb + 0.14, 0.05, tone(STUD), edges="lr")
    wtimber(m, W, ua - 0.14, ub + 0.14, yb, yb + 0.14, 0.052, tone(STUD), edges="bt")
    if sill:
        wtimber(m, W, ua - 0.16, ub + 0.16, ya - 0.12, ya, 0.054, tone(STUD), edges="btlr")


def windows_of(wall, storey):
    """The plan's windows on `wall` whose sill is in the storey: (along, sill, width, height)."""
    y0 = P.FLOORS[storey]
    y1 = P.FLOORS[storey + 1] if storey + 1 < len(P.FLOORS) else P.EAVES
    return [(along, sill, w, h) for _name, side, along, sill, w, h in P.WINDOWS if side == wall and y0 <= sill < y1]


def sheet(m, f, nu, nv, mat, colour, toward):
    """props.sheet, turned to face `toward`."""
    a, b, c = f(0.5, 0.5), f(0.6, 0.5), f(0.5, 0.6)
    du, dv = [b[k] - a[k] for k in range(3)], [c[k] - a[k] for k in range(3)]
    n = (du[1] * dv[2] - du[2] * dv[1], du[2] * dv[0] - du[0] * dv[2], du[0] * dv[1] - du[1] * dv[0])
    props.sheet(m, f, nu, nv, mat, colour, flip=n[0] * toward[0] + n[1] * toward[1] + n[2] * toward[2] < 0.0)


def outer_walls(m, storey, seed):
    y0 = P.FLOORS[storey]
    yc = P.CEILINGS[storey]
    y1 = P.FLOORS[storey + 1] if storey + 1 < len(P.FLOORS) else yc
    base = ((0.52, 0.42, 0.3), (0.5, 0.42, 0.31), (0.5, 0.42, 0.31))[storey]
    smoke = (0.5, 0.4, 0.4)[storey]
    front_open = [P.DOOR] if storey == 0 else [P.PORTER_WINDOW] if storey == 2 else []
    chimney = [(HEARTH[0] - 0.02, HEARTH[1] + 0.02)] if storey == 0 else [(STACK[0] - 0.02, STACK[1] + 0.02)]
    framed_wall(m, FRONT, X0, X1, y0, yc, y1, seed, windows_of("front", storey), front_open, base, smoke=smoke)
    # (The back wall's face is left out behind the chimney: the hearth's mouth goes back through it.)
    behind = [(HEARTH[0], HEARTH[1], y0, y1)] if storey == 0 else [(STACK[0], STACK[1], y0, y1)]
    framed_wall(m, BACK, X0, X1, y0, yc, y1, seed + 1.0, (), behind, base, smoke=smoke, skip=chimney)
    for x in (behind[0][0] - 0.1, behind[0][1] + 0.1):
        wtimber(m, BACK, x - 0.075, x + 0.075, y0 + 0.14, yc - 0.2, 0.04, tone(STUD), edges="lr")
        wtimber(m, BACK, x - 0.12, x + 0.12, y0, y0 + 0.14, 0.046, tone(STUD), edges="t")
    framed_wall(m, LEFT, Z0, Z1, y0, yc, y1, seed + 2.0, windows_of("left", storey), (), base, smoke=smoke)
    framed_wall(m, RIGHT, Z0, Z1, y0, yc, y1, seed + 3.0, windows_of("right", storey), (), base, smoke=smoke)
    # A brace at each corner, up to the plate.
    for W, a0, a1 in ((FRONT, X0, X1), (BACK, X0, X1), (LEFT, Z0, Z1), (RIGHT, Z0, Z1)):
        for end, s in ((a0, 1.0), (a1, -1.0)):
            if W is LEFT and storey < 2:
                continue    # the stairs climb this wall
            if W is FRONT and storey == 2 and s < 0:
                continue    # his window is there
            wbrace(m, W, (end + s * 0.2, y0 + 1.25), (end + s * 1.15, yc - 0.2), (end + s * 0.32, yc - 0.55), 0.15)


def seal(m):
    """Faces looking outward just behind the walls' inner faces and over the
    top ceiling, so no sun or moon comes in through the back of the plaster
    (the outside's model covers them)."""
    black = (0.0, 0.0, 0.0, 1.0)
    top = C2 + 0.02
    for W, a0, a1, holes in ((FRONT, X0, X1, [P.DOOR, P.PORTER_WINDOW]), (BACK, X0, X1, []), (LEFT, Z0, Z1, []), (RIGHT, Z0, Z1, [])):
        us = sorted(set([a0, a1] + [q for h in holes for q in (h[0], h[1])]))
        ys = sorted(set([0.0, top] + [q for h in holes for q in (h[2], h[3])]))
        for ua, ub in zip(us, us[1:]):
            for ya, yb in zip(ys, ys[1:]):
                if any(h[0] < (ua + ub) * 0.5 < h[1] and h[2] < (ya + yb) * 0.5 < h[3] for h in holes):
                    continue
                m.poly([W.p(ua, ya, -0.012), W.p(ub, ya, -0.012), W.p(ub, yb, -0.012), W.p(ua, yb, -0.012)], DARK, black, facing=(-W.n[0], 0.0, -W.n[2]))
    m.poly([(X0, top, Z0), (X1, top, Z0), (X1, top, Z1), (X0, top, Z1)], DARK, black, facing=(0, 1, 0))
    m.poly([(X0, -0.012, Z0), (X1, -0.012, Z0), (X1, -0.012, Z1), (X0, -0.012, Z1)], DARK, black, facing=(0, -1, 0))


# ---------------------------------------------------------------- floors and ceilings

def well_lining(m, well, y0, y1, sides):
    """The trimmers round a stair well, seen from within it: `sides` names
    the edges that are not a wall."""
    x0, x1, z0, z1 = well
    for name in sides:
        c = tone(SMOKED, 0.1)
        if name == "x":
            wbox(m, (x0 - 0.1, y0, z0), (x0, y1, z1), "z", c, faces="X")
        elif name == "X":
            wbox(m, (x1, y0, z0), (x1 + 0.1, y1, z1), "z", c, faces="x")
        elif name == "z":
            wbox(m, (x0, y0, z0 - 0.1), (x1, y1, z0), "x", c, faces="Z")
        else:
            wbox(m, (x0, y0, z1), (x1, y1, z1 + 0.1), "x", c, faces="z")


def trimmers(m, well, y, sides, depth=0.2, wide=0.14):
    """The same trimmers from the room below: their undersides and outer faces."""
    x0, x1, z0, z1 = well
    for name in sides:
        c = tone(SMOKED, 0.1)
        if name == "x":
            wbox(m, (x0 - wide, y - depth, z0 - wide), (x0, y, z1 + wide), "z", c, faces="xy")
        elif name == "X":
            wbox(m, (x1, y - depth, z0 - wide), (x1 + wide, y, z1 + wide), "z", c, faces="Xy")
        elif name == "z":
            wbox(m, (x0, y - depth, z0 - wide), (x1, y, z0), "x", c, faces="zy")
        else:
            wbox(m, (x0, y - depth, z1), (x1, y, z1 + wide), "x", c, faces="Zy")


def ground_floor(m):
    rect = (X0, X1, Z0, Z1)
    apron = (-2.9, 0.9, 7.75, Z1)

    def worn(x, z):
        # Trodden pale from the door to the fire and along the counter; dark in the corners.
        path = math.exp(-((x + 0.3 * (z / 9.0)) / 1.3) ** 2) + 0.7 * math.exp(-((z - 6.5) / 0.9) ** 2) * smoothstep(0.5, 2.0, x)
        return 0.78 + 0.26 * min(path, 1.0) + 0.1 * fbm(x, z, 0.7, 2, 3.0)

    under(m, -0.008, rect, [apron])
    boards_plane(m, 0.0, rect, [apron], "z", True, TROD, worn, joints=(2.2, 4.4), gap=0.006, width=(0.24, 0.4))
    # The flags before the hearth and beside it.
    x0, x1, z0, z1 = apron
    xs, zs = cuts(x0, x1, [], 0.95), cuts(z0, z1, [], 0.98)
    for xa, xb in zip(xs, xs[1:]):
        for za, zb in zip(zs, zs[1:]):
            pts = [(xa, 0.004, za), (xb, 0.004, za), (xb, 0.004, zb), (xa, 0.004, zb)]
            cols = []
            for p in pts:
                k = 0.78 + 0.2 * fbm(p[0], p[2], 0.8, 2, 5.0) - 0.3 * smoothstep(8.4, 9.2, p[2]) * (1.0 - smoothstep(0.9, 1.7, abs(p[0] + 1.0)))
                cols.append((k, k * 0.95, k * 0.86, 1.0))
            m.poly(pts, FLAGS, cols, facing=(0, 1, 0))
    wbox(m, (x0 - 0.05, -0.02, z0 - 0.07), (x1 + 0.05, 0.006, z0), "x", tone(TROD, 0.05), faces="Y")
    # Ash trodden out from the hearth, and what has been spilt at the counter.
    st.pool(m, (-1.0, 0.004, 8.7), 0.7, 0.55, (0.02, 0.019, 0.018), seed=2.0, lift=0.003)
    st.pool(m, (-0.5, 0.004, 8.2), 0.35, 0.35, (0.02, 0.019, 0.018), seed=4.0, lift=0.003)
    for x, z, r, s in ((3.3, 6.75, 0.3, 6.0), (4.1, 6.9, 0.22, 7.0), (2.4, 6.6, 0.18, 8.0), (4.2, 8.4, 0.3, 9.0)):
        st.pool(m, (x, 0.0, z), r, 0.5, (0.02, 0.016, 0.012), seed=s, lift=0.005)


def ceiling(m, storey):
    """The underside of the floor above (or of the roof space): boards on
    joists, the joists on a bridging beam, trimmers round a well."""
    y = P.CEILINGS[storey]
    rect = (X0, X1, Z0, Z1)
    if storey == 0:
        holes, well, sides = [WELL1, BREAST], WELL1, "XzZ"
        beam_x0, beam_z = WELL1[1], BEAM_Z
        chimney = BREAST
    elif storey == 1:
        holes, well, sides = [WELL2, STACK], WELL2, "xXzZ"
        beam_x0, beam_z = WELL2[1], BEAM_Z
        chimney = STACK
    else:
        holes, well, sides = [STACK], None, ""
        beam_x0, beam_z = X0, TIE_Z
        chimney = STACK
    deep = (0.36, 0.34, 0.27)[storey]
    jd = (0.17, 0.16, 0.14)[storey]

    def smoked(x, z):
        # Blacker over the fire and the candles.
        k = 0.82 + 0.16 * fbm(x, z, 0.5, 2, 11.0 + storey)
        if storey == 0:
            k *= 1.0 - 0.3 * math.exp(-(((x + 1.0) / 1.8) ** 2 + ((z - 8.6) / 1.4) ** 2))
        return k

    boards_plane(m, y, rect, holes, "x", False, SMOKED, smoked, joints=(2.4, 4.6), gap=0.003, width=(0.22, 0.34))
    blocked = [(beam_x0, X1, beam_z - 0.16, beam_z + 0.16), (chimney[0] - 0.16, chimney[1] + 0.16, chimney[2] - 0.16, Z1)]
    if well:
        blocked.append((well[0] - 0.15, well[1] + 0.15, well[2] - 0.15, well[3] + 0.15))
        trimmers(m, well, y, sides, jd + 0.03)
        well_lining(m, well, y - jd - 0.03, P.FLOORS[storey + 1], sides)
    xs = [X0 + 0.32 + 0.447 * i for i in range(25)]
    joists(m, y, xs, Z0, Z1, blocked, jd)
    # The trimmer before the chimney, which the joists stop at.
    wbox(m, (chimney[0] - 0.3, y - jd, chimney[2] - 0.15), (chimney[1] + 0.3, y, chimney[2] - 0.01), "x", tone(SMOKED), faces="zy")
    # The bridging beam, a chamfer's worth narrower underneath.
    c = tone(SMOKED, 0.06)
    wbox(m, (beam_x0, y - deep, beam_z - 0.16), (X1, y, beam_z + 0.16), "x", c, faces="zZy")
    return deep


def upper_floor(m, storey):
    """The boards of the first or second floor, less its stair well and the stack."""
    y = P.FLOORS[storey]
    rect = (X0, X1, Z0, Z1)
    holes = [WELL1 if storey == 1 else WELL2, STACK]

    def worn(x, z):
        return 0.8 + 0.2 * fbm(x, z, 0.6, 2, 20.0 + storey)

    under(m, y - 0.008, rect, holes)
    boards_plane(m, y, rect, holes, "x", True, (0.62, 0.53, 0.42), worn, joints=(2.2, 4.4), gap=0.006, width=(0.22, 0.36))


def post(m, x, z, y0, y1, w, brace_y, beam_y, sides=(-1, 1), reach=0.8):
    """A post under the bridging beam, with a curved brace up to it each way along the beam."""
    c = tone(SMOKED, 0.06)
    wbox(m, (x - w * 0.5, y0, z - w * 0.5), (x + w * 0.5, y1, z + w * 0.5), "y", c, faces="xXzZ")
    # A jowl: the post's head swells to carry the beam.
    wbox(m, (x - w * 0.5 - 0.03, y1 - 0.34, z - w * 0.5 - 0.012), (x + w * 0.5 + 0.03, y1, z + w * 0.5 + 0.012), "y", c, faces="xXzZy")
    for sx in sides:
        a = (x + sx * w * 0.5, brace_y, z)
        b = (x + sx * (w * 0.5 + reach), beam_y + 0.04, z)
        brace(m, a, b, (x + sx * (w * 0.5 + 0.1), beam_y - 0.12, z), 0.17, 0.1, tone(SMOKED, 0.08))


# ---------------------------------------------------------------- stairs

def stair(m, xa, xb, zf, zh, y0, y1, n=14):
    """A straight flight from its foot (zf, y0) to its head (zh, y1): the
    treads stand half a riser over the scene's ramp at their noses and half
    under it at their backs."""
    dz = (zh - zf) / n
    s = 1.0 if dz > 0 else -1.0
    rise = (y1 - y0) / n
    prev = y0
    for i in range(n):
        top = y0 + rise * (i + 0.5)
        za, zb = zf + dz * i, zf + dz * (i + 1)
        c = tone(TROD, 0.1)
        nose = za - s * 0.025
        wbox(m, (xa, top - 0.045, min(nose, zb)), (xb, top, max(nose, zb)), "x", c, faces="Y" + ("z" if s > 0 else "Z"))
        pts = [(xa, prev, za), (xb, prev, za), (xb, top - 0.045, za), (xa, top - 0.045, za)]
        m.poly(pts, WOOD, col(c, 0.55), uvs=[(p[1] * G, p[0] * G) for p in pts], facing=(0, 0, -s))
        prev = top
    pts = [(xa, prev, zh), (xb, prev, zh), (xb, y1, zh), (xa, y1, zh)]
    m.poly(pts, WOOD, col(tone(TROD, 0.1), 0.55), uvs=[(p[1] * G, p[0] * G) for p in pts], facing=(0, 0, -s))


def spandrel(m, x, look, zf, zh, y0, y1, drop=0.05):
    """Upright boards closing the side of a stair (the plane x, looking `look`), cut to its slope."""
    za, zb = min(zf, zh), max(zf, zh)

    def line(z):
        return y0 + (y1 - y0) * (z - zf) / (zh - zf) - drop

    for a, b in strips(za, zb, 0.2, 0.3):
        ya, yb = max(line(a), y0), max(line(b), y0)
        if max(ya, yb) < y0 + 0.03:
            continue
        c = tone(STUD, 0.14)
        o = random.random()
        pts = [(x, y0, a), (x, y0, b), (x, yb, b), (x, ya, a)]
        m.poly(pts, WOOD, c, uvs=[(o + p[2] * G, p[1] * G) for p in pts], facing=(look, 0, 0))


def stair_rail(m, x, zf, zh, y0, y1, ytop, height=0.92, newel=True):
    """A handrail and balusters up a stair's open side, from a newel at its
    foot to where the rail meets the floor above (`ytop`)."""
    s = 1.0 if zh > zf else -1.0

    def pitch(z):
        return y0 + (y1 - y0) * (z - zf) / (zh - zf)

    t_end = min(1.0, (ytop - 0.06 - (y0 + height)) / (y1 - y0))
    z_end = zf + (zh - zf) * t_end
    beam(m, (x, y0 + height, zf), (x, pitch(z_end) + height, z_end), 0.06, 0.085, tone(STUD))
    if newel:
        c = tone(SMOKED, 0.06)
        wbox(m, (x - 0.055, y0, zf - 0.055), (x + 0.055, y0 + height + 0.16, zf + 0.055), "y", c, faces="xXzZY")
    step = 0.2
    for i in range(1, int(abs(z_end - zf) / step) + 1):
        z = zf + s * step * i
        wbox(m, (x - 0.017, pitch(z) + 0.22, z - 0.017), (x + 0.017, pitch(z) + height - 0.03, z + 0.017), "y", tone(STUD, 0.1), faces="xXzZ")
    return z_end


def level_rail(m, a, b, y, height=0.95, newels="ab"):
    """A rail along a well's edge from (x, z) `a` to `b` on the floor `y`."""
    long = math.dist(a, b)
    ux, uz = (b[0] - a[0]) / long, (b[1] - a[1]) / long
    for name, p in (("a", a), ("b", b)):
        if name in newels:
            wbox(m, (p[0] - 0.055, y, p[1] - 0.055), (p[0] + 0.055, y + height + 0.14, p[1] + 0.055), "y", tone(SMOKED, 0.06), faces="xXzZY")
    beam(m, (a[0], y + height, a[1]), (b[0], y + height, b[1]), 0.07, 0.07, tone(STUD), ends="")
    beam(m, (a[0], y + 0.12, a[1]), (b[0], y + 0.12, b[1]), 0.05, 0.06, tone(STUD), ends="")
    n = max(int(long / 0.19), 1)
    for i in range(1, n):
        px, pz = a[0] + ux * long * i / n, a[1] + uz * long * i / n
        wbox(m, (px - 0.017, y + 0.15, pz - 0.017), (px + 0.017, y + height - 0.035, pz + 0.017), "y", tone(STUD, 0.1), faces="xXzZ")


def ledged(m, W, ua, ub, ya, yb, d=0.02, colour=STUD, latch=None):
    """A boarded door or shutter lying on a wall: boards, two ledges, strap hinges."""
    vboards(m, W, ua, ub, ya, yb, d, colour, width=(0.16, 0.24))
    dark = col(tone(colour, 0.05), 0.6)
    for pa, pb, f in (((ua, ya), (ua, yb), W.along(-1.0)), ((ub, ya), (ub, yb), W.along(1.0)), ((ua, ya), (ub, ya), (0.0, -1.0, 0.0)), ((ua, yb), (ub, yb), (0.0, 1.0, 0.0))):
        m.poly([W.p(pa[0], pa[1], 0.0), W.p(pa[0], pa[1], d), W.p(pb[0], pb[1], d), W.p(pb[0], pb[1], 0.0)], WOOD, dark, facing=f)
    for yy in (ya + (yb - ya) * 0.2, ya + (yb - ya) * 0.8):
        wtimber(m, W, ua + 0.02, ub - 0.02, yy - 0.05, yy + 0.05, d + 0.022, tone(colour, 0.1), edges="bt", base=d)
        a, b = W.p(ua + 0.01, yy, d + 0.022), W.p(ua + (ub - ua) * 0.6, yy, d + 0.022)
        props.strap(m, a, b, W.n, width=0.035, nails=3, colour=BLACK_IRON, taper=0.5)
    if latch is not None:
        p = W.p(latch, (ya + yb) * 0.5, d)
        props.ring(m, (p[0] + W.n[0] * 0.012, p[1], p[2] + W.n[2] * 0.012), W.n, r=0.04, thick=0.006, colour=BLACK_IRON)


def stairs(g, f, s):
    """Both flights, their boarded sides and rails, and the rails round the wells."""
    # Ground to first: along the left wall, from the back toward the street.
    stair(g, -5.66, -4.54, 8.6, 4.0, F0, F1)
    beam(g, (-5.675, F0 + 0.1, 8.6), (-5.675, F1 + 0.1, 4.0), 0.05, 0.3, tone(SMOKED))
    beam(g, (-4.515, F0 + 0.1, 8.6), (-4.515, F1 + 0.1, 4.0), 0.05, 0.3, tone(SMOKED))
    spandrel(g, -4.535, 1.0, 8.6, 4.0, F0, F1)
    stair_rail(g, -4.5, 8.6, 4.0, F0, F1, C0)
    # Under its head, a boarded cupboard with a door.
    end = Wall("z", 4.0, -1)
    vboards(g, end, -5.7, -4.5, F0, C0, 0.0, STUD)
    ledged(g, end, -5.45, -4.75, 0.06, 1.7, 0.018, SMOKED, latch=-4.85)
    # First to second: beside the first's well, climbing back from the street.
    stair(f, -4.46, -3.34, 4.0, 8.6, F1, F2)
    beam(f, (-4.475, F1 + 0.1, 4.0), (-4.475, F2 + 0.1, 8.6), 0.05, 0.3, tone(SMOKED))
    beam(f, (-3.325, F1 + 0.1, 4.0), (-3.325, F2 + 0.1, 8.6), 0.05, 0.3, tone(SMOKED))
    spandrel(f, -4.495, -1.0, 4.0, 8.6, F1, F2)
    spandrel(f, -3.305, 1.0, 4.0, 8.6, F1, F2)
    stair_rail(f, -4.42, 4.0, 8.6, F1, F2, C1)
    stair_rail(f, -3.38, 4.0, 8.6, F1, F2, C1)
    end = Wall("z", 8.6, 1)
    vboards(f, end, -4.5, -3.3, F1, C1, 0.0, STUD)
    # The first floor's well: a rail across its back end (the other sides are the wall, the stair's head and the second flight).
    level_rail(f, (X0 + 0.06, 8.66), (-4.56, 8.66), F1, newels="b")
    # The second floor's well: rails on three sides; the flight comes up at the fourth.
    level_rail(s, (-3.24, 3.94), (-3.24, 8.66), F2)
    level_rail(s, (-4.56, 3.94), (-4.56, 8.66), F2)
    level_rail(s, (-4.56, 3.94), (-3.24, 3.94), F2, newels="")


# ---------------------------------------------------------------- the hearth

def stone_tint(k=1.0, soot=None, seed=6.0):
    def tint(x, y, z):
        v = (0.92 + 0.16 * fbm(x * 1.3 + z, y * 1.3, 1.0, 2, seed)) * k
        if soot:
            v *= 1.0 - soot(x, y, z)
        return (v, v * 0.93, v * 0.8, 1.0)
    return tint


def key(m, cx, cy, z, turn, long, colour, flip=1.0):
    """A key painted on a cloth hanging at z (it faces -z): its bow down, its bit up, leaning `turn`."""
    c, s = math.cos(turn), math.sin(turn)

    def at(px, py):
        return (cx + (px * c - py * s) * flip, cy + px * s + py * c, z)

    def piece(pts):
        m.poly([at(*p) for p in pts], PAINT, colour, facing=(0, 0, -1))

    w = long * 0.045
    piece([(-w, -long * 0.3), (w, -long * 0.3), (w, long * 0.5), (-w, long * 0.5)])
    # The bow: a ring.
    r0, r1, by = long * 0.085, long * 0.15, -long * 0.42
    for i in range(8):
        a0, a1 = math.tau * i / 8, math.tau * (i + 1) / 8
        piece([(math.cos(a0) * r0, by + math.sin(a0) * r0), (math.cos(a1) * r0, by + math.sin(a1) * r0), (math.cos(a1) * r1, by + math.sin(a1) * r1), (math.cos(a0) * r1, by + math.sin(a0) * r1)])
    # The bit: two wards.
    for y0, y1, reach in ((long * 0.42, long * 0.5, 0.2), (long * 0.28, long * 0.36, 0.16)):
        piece([(w, y0), (long * reach, y0), (long * reach, y1), (w, y1)])


def hanging(m, soft, W, x0, x1, y0, y1, colour, border, seed, keys=False):
    """A painted cloth on a wall, from `x0` to `x1` along it: hung from a
    rod by its top edge, its hem uneven."""
    def f(u, v):
        x = lerp(x0, x1, u)
        sag = 0.02 * math.sin(u * math.pi * 5.0) ** 2
        y = lerp(y1 - sag * (1.0 - v), y0 + 0.03 * fbm(x * 2.0, seed, 1.0, 2, seed), v)
        return W.p(x, y, 0.022 + 0.012 * fbm(x * 3.0, y * 2.0, 1.0, 2, seed))

    def c(u, v):
        edge = min(u, 1.0 - u, v, 1.0 - v)
        k = 0.8 + 0.25 * fbm(u * 4.0, v * 4.0, 1.0, 3, seed + 2.0)
        return rgba(border if edge < 0.07 else colour, k)

    sheet(soft, f, 10, 8, CLOTH, c, W.n)
    beam(m, W.p(x0 - 0.06, y1 + 0.012, 0.03), W.p(x1 + 0.06, y1 + 0.012, 0.03), 0.022, 0.022, tone(SMOKED))
    if keys:
        gold = (0.12, 0.085, 0.028, 1.0)
        cx, cy, long = (x0 + x1) * 0.5, (y0 + y1) * 0.5 + 0.01, (y1 - y0) * 0.78
        key(m, cx, cy, W.at - 0.04, 0.6, long, gold)
        key(m, cx, cy, W.at - 0.043, 0.6, long, col(gold, 0.85), flip=-1.0)


def hearth(m, soft):
    """The taproom's fireplace: the Hearth Block is solid, and its opening
    is drawn inside it and on into the back wall."""
    x0, x1, zf = HEARTH[0], HEARTH[1], HEARTH[2]
    ja, jb, top, back, splay = -1.86, -0.14, 1.25, 9.86, 0.16
    zb = BREAST[2]

    def near(x, y, z):
        # Smoke-black round the mouth and up the breast.
        side = smoothstep(0.55, 0.0, min(abs(x - ja), abs(x - jb))) if ja - 0.6 < x < jb + 0.6 else 0.0
        return 0.45 * side * smoothstep(0.2, 1.3, y) + 0.3 * smoothstep(1.2, 2.8, y) * (1.0 - smoothstep(0.9, 1.6, abs(x + 1.0)))

    warm = stone_tint(1.0, near)
    for a, b in ((x0, ja), (jb, x1)):
        cp.panel(m, (a, zf), (b, zf), 0.0, top, (0, 0, -1), STONE, warm, 0.5, 0.45)
    cp.panel(m, (x0, zb), (x1, zb), top + 0.3, C0, (0, 0, -1), STONE, warm, 0.62, 0.42)
    for x, look in ((x0, -1.0), (x1, 1.0)):
        cp.panel(m, (x, zf), (x, Z1), 0.0, top + 0.31, (look, 0, 0), STONE, warm, 0.5, 0.45)
        cp.panel(m, (x, zb), (x, Z1), top + 0.31, C0, (look, 0, 0), STONE, warm, 0.5, 0.45)
    # The lintel: one great oak, black underneath; the mantel shelf on it.
    oak = tone(SMOKED, 0.05)
    wbox(m, (x0 - 0.06, top, zf - 0.03), (x1 + 0.06, top + 0.31, zf + 0.26), "x", oak, faces="xXz")
    wbox(m, (x0 - 0.06, top, zf - 0.03), (x1 + 0.06, top + 0.31, zf + 0.26), "x", col(oak, 0.35), faces="yZ")
    wbox(m, (x0 - 0.1, top + 0.31, zf - 0.05), (x1 + 0.1, top + 0.36, zb), "x", tone(STUD, 0.06), faces="xXyYz")

    def black(k):
        return stone_tint(k, lambda x, y, z: 0.55 * smoothstep(0.0, 0.6, y) * (0.5 + 0.5 * smoothstep(zf, back, z)), 9.0)

    # Inside: splayed cheeks, the fireback, the throat going up behind the lintel, the hearth stone.
    cp.panel(m, (ja, zf), (ja + splay, back), 0.0, top, (1, 0, 0), STONE, black(0.14), 0.45, 0.45)
    cp.panel(m, (jb, zf), (jb - splay, back), 0.0, top, (-1, 0, 0), STONE, black(0.14), 0.45, 0.45)
    cp.panel(m, (ja + splay, back), (jb - splay, back), 0.0, 1.95, (0, 0, -1), STONE, black(0.09), 0.5, 0.45)
    zt = zf + 0.26
    fa, fb = ja + splay * (zt - zf) / (back - zf), jb - splay * (zt - zf) / (back - zf)
    soot = (0.025, 0.023, 0.021, 1.0)
    m.poly([(fa, top, zt), (fb, top, zt), (jb - splay, 1.95, back), (ja + splay, 1.95, back)], STONE, soot, facing=(0, -1, -0.4))
    m.poly([(fa, top, zt), (ja + splay, top, back), (ja + splay, 1.95, back)], STONE, soot, facing=(1, 0, 0))
    m.poly([(fb, top, zt), (jb - splay, top, back), (jb - splay, 1.95, back)], STONE, soot, facing=(-1, 0, 0))
    pts = [(ja, 0.04, zf), (jb, 0.04, zf), (jb - splay, 0.04, back), (ja + splay, 0.04, back)]
    m.poly(pts, FLAGS, [(0.16, 0.15, 0.135, 1.0), (0.16, 0.15, 0.135, 1.0), (0.05, 0.047, 0.042, 1.0), (0.05, 0.047, 0.042, 1.0)], facing=(0, 1, 0))
    m.poly([(ja, 0.0, zf), (jb, 0.0, zf), (jb, 0.04, zf), (ja, 0.04, zf)], FLAGS, (0.4, 0.38, 0.34, 1.0), facing=(0, 0, -1))
    dress.soot(m, (-1.0, top + 0.02, zf - 0.031), (0.0, -1.0), 1.5, 0.3, 0.8)
    dress.soot(m, (-1.0, top + 0.36, zb), (0.0, -1.0), 1.7, 1.1, 0.55)
    # On the shelf: jugs and crocks, a wooden bowl. (The scene stands a candle at its left end.)
    y = top + 0.36
    zs = (zf - 0.05 + zb) * 0.5
    st.jug(soft, (-0.1, y, zs), 2.2, 0.0, 0.62)
    st.jug(soft, (-0.36, y, zs + 0.01), 0.7, 0.0, 0.5, colour=(0.03, 0.027, 0.022))
    st.crock(soft, (-1.25, y, zs), 0.06, 0.13)
    st.tied_jar(soft, (-1.45, y, zs + 0.01), 0.05, 0.11)
    props.pot(soft, (-0.75, y, zs), [(0.0, 0.035), (0.02, 0.06), (0.04, 0.07)], colour=(0.05, 0.036, 0.022), sides=9)
    # The house's sign over it: two keys crossed, on a painted cloth.
    hanging(m, soft, Wall("z", zb, -1), -1.62, -0.38, 1.8, 2.5, (0.05, 0.02, 0.014), (0.07, 0.055, 0.025), 31.0, keys=True)
    # Two stubs of candle left on the shelf, not lit.
    props.candle(soft, (-1.95, y, zs), h=0.09, r=0.014, lean=0.05)
    props.candle(soft, (-2.07, y, zs + 0.01), h=0.05, r=0.014)
    # The stack going up through the loft and the top floor.
    for storey, y0, y1 in ((1, F1, F2), (2, F2, C2)):
        t = stone_tint(0.62, lambda x, y, z, y0=y0: 0.25 * smoothstep(y0 + 1.0, y0 + 2.8, y), 12.0 + storey)
        mm = FLOORS_M[storey]
        cp.panel(mm, (STACK[0], STACK[2]), (STACK[1], STACK[2]), y0, y1, (0, 0, -1), STONE, t, 0.55, 0.5)
        for x, look in ((STACK[0], -1.0), (STACK[1], 1.0)):
            cp.panel(mm, (x, STACK[2]), (x, Z1), y0, y1, (look, 0, 0), STONE, t, 0.5, 0.5)
    # A stack of split logs in the corner by the left jamb, and a stone for the poker.
    logs(m, soft, -2.9, -2.3, 9.26, 9.68, 0.0, 0.52, 14)
    iron = col(RUST_C, 0.55)
    beam(m, (x1 + 0.05, 0.0, zf + 0.1), (x1 + 0.012, 1.02, zf + 0.3), 0.016, 0.016, iron, IRON, end_shade=1.0)
    beam(m, (x1 + 0.09, 0.0, zf + 0.22), (x1 + 0.014, 0.95, zf + 0.42), 0.014, 0.014, iron, IRON, end_shade=1.0)


def logs(m, soft, x0, x1, z0, z1, y0, high, seed):
    """Split logs stacked ends-out (they lie along z) in the box given."""
    rng = random.Random(seed)
    bark = (0.26, 0.22, 0.18)
    y = y0
    while y < y0 + high - 0.06:
        x = x0 + rng.uniform(0.0, 0.03)
        tallest = 0.0
        stop = x1 if y < y0 + high * 0.6 else lerp(x0, x1, rng.uniform(0.5, 0.9))
        while x < stop - 0.1:
            r = rng.uniform(0.05, 0.075)
            sides = rng.choice((3, 3, 4))
            a = rng.uniform(0.0, math.tau)
            cx, cy = x + r, y + r * 0.85
            e0, e1 = z0 + rng.uniform(-0.03, 0.03), z1
            ring = [(cx + math.cos(a + math.tau * i / sides) * r * 1.1, cy + math.sin(a + math.tau * i / sides) * r * 0.95) for i in range(sides)]
            k = rng.uniform(0.8, 1.15)
            for i in range(sides):
                (xa, ya), (xb, yb) = ring[i], ring[(i + 1) % sides]
                c = rgba(bark if i == 0 else props.PINE, k * (0.9 if i == 0 else 0.62))
                m.poly([(xa, ya, e0), (xb, yb, e0), (xb, yb, e1), (xa, ya, e1)], WOOD, c, uvs=[(0.0, 0.0), (0.1, 0.0), (0.1, 0.4), (0.0, 0.4)],
                       facing=((xa + xb) * 0.5 - cx, (ya + yb) * 0.5 - cy, 0.0))
            m.poly([(px, py, e0) for px, py in ring], WOOD, rgba(props.PINE, k * 0.8), uvs=[(px, py * 0.3) for px, py in ring], facing=(0, 0, -1))
            x += r * 2.0 + rng.uniform(0.0, 0.015)
            tallest = max(tallest, r * 1.75)
        y += tallest or 0.1


# ---------------------------------------------------------------- the counter

def counter(m, soft):
    """The bar: heavy boards on a framed front (the Counter Block)."""
    x0, x1, z0, z1, h = 2.1, 5.1, 7.1, 7.7, 1.05
    props.boards(m, (x0 - 0.045, h - 0.07, z0 - 0.05), (x1 + 0.045, h, z1 + 0.03), "x", "z", 2, TROD, gap=0.005, uneven=0.002, ragged=0.012)
    front = Wall("z", z0, -1)
    back = Wall("z", z1, 1)
    for W in (front, back):
        vboards(m, W, x0, x1, 0.0, h - 0.07, -0.03, STUD, width=(0.18, 0.27))
        wtimber(m, W, x0, x1, 0.0, 0.14, 0.0, tone(SMOKED), edges="t", base=-0.03)
        wtimber(m, W, x0, x1, h - 0.2, h - 0.07, 0.0, tone(SMOKED), edges="b", base=-0.03)
        for x in (x0 + 0.07, x0 + 1.02, x1 - 1.02, x1 - 0.07):
            wtimber(m, W, x - 0.07, x + 0.07, 0.14, h - 0.2, 0.0, tone(SMOKED), edges="lr", base=-0.03)
    for x, look in ((x0, -1), (x1, 1)):
        vboards(m, Wall("x", x, look), z0, z1, 0.0, h - 0.07, 0.0, STUD, width=(0.18, 0.27))
    # On it: a jug and cups, a bowl, a cloth. (The scene stands a candle at its left end.)
    st.jug(soft, (3.25, h, 7.45), 0.5, 0.0, 1.0)
    for x, z in ((3.55, 7.3), (3.72, 7.42), (4.55, 7.3)):
        props.pot(soft, (x, h, z), [(0.0, 0.03), (0.05, 0.036), (0.1, 0.04)], colour=(0.045, 0.036, 0.026), sides=8)
    props.pot(soft, (4.2, h, 7.48), [(0.0, 0.05), (0.025, 0.09), (0.05, 0.105)], colour=(0.05, 0.036, 0.022), sides=10)
    props.tick(soft, 4.7, 4.98, 7.36, 7.6, h, 0.02, colour=props.LINEN, lumps=0.5, seed=7.0, edge=0.3)
    # Rings where cups have stood.
    for x, z in ((2.9, 7.3), (3.9, 7.25), (4.4, 7.5)):
        st.pool(m, (x, h, z), 0.07, 0.5, (0.02, 0.016, 0.012), seed=x, lift=0.004)


def lying_cask(m, soft, x, y, z_back, k=0.88, tap=True):
    """An ale cask on its side, its head toward -z (st.cask stands one on end)."""
    p = types.SimpleNamespace(hard=props.Placed(m, (x, y, z_back), 0.0, k, -math.pi * 0.5), soft=props.Placed(soft, (x, y, z_back), 0.0, k, -math.pi * 0.5))
    st.cask(p)
    zh = z_back - 0.9 * k
    if tap:
        yt = y - 0.2 * k
        soft.tube([(x, yt, zh + 0.03), (x, yt, zh - 0.05), (x, yt - 0.004, zh - 0.085)], [0.02, 0.017, 0.013], 7, WOOD, rgba(props.PINE, 0.75), caps=True)
        soft.tube([(x, yt + 0.05, zh - 0.035), (x, yt - 0.02, zh - 0.035)], [0.008, 0.007], 5, WOOD, rgba(OAK, 0.8), caps=True)
        beam(m, (x - 0.028, yt + 0.052, zh - 0.035), (x + 0.028, yt + 0.052, zh - 0.035), 0.014, 0.02, rgba(OAK, 0.8))
    return zh


def back_bar(m, soft):
    """Behind the counter, against the back wall: casks on a stillage, and
    shelves over them loaded with what the house pours into."""
    x0, x1 = 2.5, 5.6
    for z in (9.0, 9.5):
        beam(m, (x0, 0.29, z), (x1, 0.29, z), 0.1, 0.1, tone(SMOKED))
    for x in (x0 + 0.12, (x0 + x1) * 0.5, x1 - 0.12):
        for z in (9.0, 9.5):
            wbox(m, (x - 0.05, 0.0, z - 0.05), (x + 0.05, 0.24, z + 0.05), "y", tone(SMOKED), faces="xXzZ")
        beam(m, (x, 0.2, 8.93), (x, 0.2, 9.57), 0.06, 0.08, tone(SMOKED))
    for i, x in enumerate((3.02, 3.86, 4.7)):
        zh = lying_cask(m, soft, x, 0.34 + 0.285, 9.67, 0.88)
        for sx in (-1, 1):
            for z in (9.0, 9.5):
                props.slab(m, [(x + sx * 0.33, 0.34), (x + sx * 0.2, 0.34), (x + sx * 0.33, 0.43)], "z", z - 0.04, z + 0.04, tone(STUD))
        if i == 1:
            st.pool(m, (x, 0.0, zh - 0.05), 0.2, 0.7, (0.02, 0.016, 0.012), seed=5.0)
    # A pail under the middle tap, inside the stillage's line.
    props.pot(soft, (3.86, 0.0, 8.86), [(0.0, 0.1), (0.1, 0.115), (0.2, 0.125)], colour=(0.06, 0.05, 0.036), sides=10)
    # Shelves on brackets.
    levels = (1.38, 1.82)
    for y in levels:
        props.boards(m, (x0 - 0.05, y - 0.035, 9.37), (x1 + 0.05, y, Z1), "x", "z", 2, STUD, gap=0.004, uneven=0.003, ragged=0.012)
        for x in (x0 + 0.1, (x0 + x1) * 0.5, x1 - 0.1):
            props.slab(m, [(9.4, y - 0.035), (Z1, y - 0.035), (Z1, y - 0.3)], "x", x - 0.02, x + 0.02, tone(SMOKED))
    a, b = levels
    z = 9.53
    # The lower: jugs in a row, cups, a stack of bowls.
    for i, x in enumerate((2.62, 2.84, 3.07, 3.3)):
        st.jug(soft, (x, a, z + random.uniform(-0.03, 0.03)), random.uniform(0.0, 6.0), 0.0, random.uniform(0.85, 1.05), colour=(props.CLAY, (0.03, 0.027, 0.022), (0.05, 0.036, 0.022))[i % 3])
    for x in (3.55, 3.68, 3.81, 3.94, 4.07):
        props.pot(soft, (x, a, z + random.uniform(-0.05, 0.05)), [(0.0, 0.03), (0.05, 0.036), (0.1, 0.04)], colour=(0.045, 0.036, 0.026), sides=7)
    for i in range(4):
        props.pot(soft, (4.35 + i * 0.003, a + i * 0.02, z), [(0.0, 0.04), (0.02, 0.075), (0.042, 0.09)], colour=(0.05, 0.036, 0.022), sides=9, dark_inside=i == 3)
    st.crock(soft, (4.68, a, z), 0.11, 0.24)
    st.crock(soft, (4.98, a, z - 0.01), 0.12, 0.27, colour=(0.03, 0.027, 0.022))
    st.tied_jar(soft, (5.28, a, z), 0.075, 0.17)
    st.tied_jar(soft, (5.46, a, z + 0.02), 0.07, 0.15)
    # Leather jacks hung by their handles from pegs under it.
    for x in (2.75, 2.95, 3.4, 3.6, 4.2):
        beam(m, (x, a - 0.07, Z1 - 0.005), (x, a - 0.06, Z1 - 0.09), 0.016, 0.016, tone(STUD))
        j = props.Placed(soft, (x, a - 0.27 + random.uniform(-0.01, 0.01), Z1 - 0.075), random.uniform(1.3, 1.9))
        props.pot(j, (0.0, 0.0, 0.0), [(0.0, 0.05), (0.07, 0.047), (0.14, 0.04), (0.17, 0.043)], colour=props.LEATHER, sides=8)
        j.tube([(0.04, 0.16, 0.0), (0.085, 0.15, 0.0), (0.09, 0.08, 0.0), (0.05, 0.05, 0.0)], [0.008] * 4, 4, PAINT, rgba(props.LEATHER))
    # The upper: a firkin, baskets, crocks, a cheese.
    p = types.SimpleNamespace(hard=props.Placed(m, (2.8, b, z), 0.4, 0.5), soft=props.Placed(soft, (2.8, b, z), 0.4, 0.5))
    st.cask(p)
    p = types.SimpleNamespace(hard=props.Placed(m, (3.2, b, z + 0.01), 1.9, 0.44), soft=props.Placed(soft, (3.2, b, z + 0.01), 1.9, 0.44))
    st.cask(p)
    st.basket(soft, (3.75, b, z), 0.14, 0.18)
    st.crock(soft, (4.15, b, z), 0.1, 0.22)
    st.cheese(soft, (4.5, b, z), 0.13, 0.09)
    st.jug(soft, (4.85, b, z), 4.0, 0.0, 1.1, colour=(0.03, 0.027, 0.022))
    st.basket(soft, (5.25, b, z), 0.15, 0.2, handle=False)
    # Herbs and onions hung from the joists over the bar (above anyone's head).
    for x, z2, long in ((2.5, 8.2, 0.26), (3.4, 8.35, 0.3), (4.4, 8.25, 0.24), (5.2, 8.3, 0.3)):
        g = (0.03, 0.034, 0.018) if long != 0.3 else (0.06, 0.04, 0.022)
        top = C0 - 0.17
        soft.tube([(x, top, z2), (x, top - 0.05, z2), (x + 0.005, top - long * 0.5, z2), (x, top - long * 0.9, z2), (x, top - long, z2)],
                  [0.004, 0.012, 0.04, 0.055, 0.02], 6, PAINT, [rgba(g, 0.7), rgba(g, 0.8), rgba(g), rgba(g, 1.1), rgba(g, 0.8)], caps=True)


# ---------------------------------------------------------------- things on walls and upstairs

def cloak(m, soft, W, u, y, colour, seed, long=1.05, wide=0.42, peg=True):
    """A cloak hung by its hood from a peg on a wall at (u, y)."""
    if peg:
        a, b = W.p(u, y + 0.01, 0.0), W.p(u, y + 0.035, 0.09)
        beam(m, a, b, 0.022, 0.022, tone(STUD))

    def f(a, v):
        s = (a - 0.5) * 2.0
        half = lerp(0.05, wide * 0.5, smoothstep(0.0, 0.55, v)) * (1.0 + 0.1 * fbm(v * 3.0, seed, 1.0, 2, seed))
        fold = 0.012 * math.sin(s * 7.0 + seed) * smoothstep(0.1, 0.6, v)
        out = 0.014 + 0.05 * math.sqrt(max(1.0 - s * s, 0.0)) * lerp(0.7, 1.0, v) + fold
        hem = v * long * (1.0 + 0.05 * math.sin(s * 3.0 + seed))
        return W.p(u + s * half, y - hem, out)

    def c(a, v):
        return rgba(colour, 0.75 + 0.3 * fbm(a * 5.0, v * 3.0, 1.0, 3, seed + 1.0))

    sheet(soft, f, 8, 7, CLOTH, c, W.n)


def peg_rail(m, soft, W, u0, u1, y, cloaks):
    """A rail of pegs on a wall, and what hangs from it: `cloaks` are (along, colour, seed)."""
    wtimber(m, W, u0, u1, y - 0.04, y + 0.04, 0.03, tone(STUD), edges="bt")
    n = max(int((u1 - u0) / 0.3), 1)
    hung = [round((u - u0) / (u1 - u0) * n) for u, _c, _s in cloaks]
    for i in range(n + 1):
        u = u0 + (u1 - u0) * (i + 0.5) / (n + 1)
        a, b = W.p(u, y, 0.03), W.p(u, y + 0.03, 0.11)
        beam(m, a, b, 0.02, 0.02, tone(STUD))
    for u, colour, seed in cloaks:
        cloak(m, soft, W, u, y + 0.02, colour, seed, peg=False)
    return hung


def chest(m, x, y, z, long=0.9, deep=0.45, high=0.5):
    """A boarded chest standing with its back to +z, iron-strapped."""
    props.boards(m, (x - long * 0.5, y + 0.05, z - deep * 0.5), (x + long * 0.5, y + high - 0.04, z - deep * 0.5 + 0.025), "x", "y", 2, STUD, uneven=0.0)
    props.boards(m, (x - long * 0.5, y + 0.05, z + deep * 0.5 - 0.025), (x + long * 0.5, y + high - 0.04, z + deep * 0.5), "x", "y", 2, STUD, uneven=0.0)
    for sx in (-1, 1):
        plank(m, (x + sx * long * 0.5 - (0.03 if sx > 0 else 0.0), y, z - deep * 0.5), (x + sx * long * 0.5 + (0.03 if sx < 0 else 0.0), y + high - 0.04, z + deep * 0.5), tone(SMOKED), along="y")
    props.boards(m, (x - long * 0.5 - 0.015, y + high - 0.04, z - deep * 0.5 - 0.015), (x + long * 0.5 + 0.015, y + high, z + deep * 0.5), "x", "z", 2, STUD, uneven=0.002)
    for px in (x - long * 0.28, x + long * 0.28):
        props.strap(m, (px, y + 0.08, z - deep * 0.5), (px, y + high - 0.05, z - deep * 0.5), (0, 0, -1), width=0.035, nails=3, colour=BLACK_IRON)
        props.strap(m, (px, y + high, z - deep * 0.5), (px, y + high, z + deep * 0.4), (0, 1, 0), width=0.035, nails=3, colour=BLACK_IRON)
    props.ring(m, (x, y + high - 0.14, z - deep * 0.5 - 0.012), (0, 0, -1), r=0.035, thick=0.006, colour=BLACK_IRON)


def loft(m, soft):
    """The first floor: a post under its beam with cloaks on it, pegs along
    the walls, a chest. (The scene sets out the beds.)"""
    post(m, LOFT_POST, BEAM_Z, F1, C1 - 0.34, 0.24, F1 + 1.75, C1 - 0.34)
    for k, (look, colour, seed) in enumerate(((Wall("x", LOFT_POST - 0.12, -1), props.UNDYED, 4.0), (Wall("z", BEAM_Z - 0.12, -1), props.RUSSET, 5.0))):
        cloak(m, soft, look, BEAM_Z if look.axis == "x" else LOFT_POST, F1 + 1.62, colour, seed, long=0.95, wide=0.36)
    peg_rail(m, soft, BACK, 1.3, 5.5, F1 + 1.7, ((1.55, props.UNDYED, 6.0), (3.05, (0.02, 0.026, 0.022), 7.0), (4.5, props.LEATHER, 8.0)))
    peg_rail(m, soft, RIGHT, 6.4, 7.5, F1 + 1.7, ((6.9, props.RUSSET, 9.0),))
    chest(m, 2.3, F1, 7.2)
    # A pair of shoes by a bed, a bundle on the chest.
    props.tick(soft, 2.0, 2.4, 7.05, 7.33, F1 + 0.5, 0.12, colour=props.UNDYED, lumps=0.3, seed=12.0, edge=0.3)


def hook(m, x, y, z, drop):
    """An iron hook in a ceiling timber at (x, y, z), `drop` long."""
    m.tube([(x, y, z), (x, y - drop, z)], [0.006, 0.006], 4, IRON, BLACK_IRON)
    props.ring(m, (x, y - drop - 0.02, z), (1, 0, 0), r=0.02, thick=0.005, colour=BLACK_IRON, sides=8)


def top_floor(m, soft):
    """The second floor: the porter's room behind a plank partition (its
    door folded back inside, his window's shutter folded back beside it),
    and the rest of the floor, where the house keeps what it isn't using."""
    rx0, rx1, rz0, rz1 = P.PORTER_ROOM
    wx0, wx1 = rx0 - 0.125, rx0 + 0.125      # the west partition's two faces
    bz0, bz1 = rz1 - 0.125, rz1 + 0.125      # the back partition's
    door = (2.5, 3.5, F2, F2 + 2.2)
    y0, y1 = F2, C2

    def muntins(W, u0, u1, holes=()):
        vboards(m, W, u0, u1, y0, y1, 0.0, STUD, holes, width=(0.26, 0.4))
        for a, b in minus(u0, u1, [(h[0] - 0.1, h[1] + 0.1) for h in holes]):
            wtimber(m, W, a, b, y0, y0 + 0.12, 0.03, tone(SMOKED), edges="t")
        wtimber(m, W, u0, u1, y1 - 0.14, y1, 0.03, tone(SMOKED), edges="b")
        n = max(int(round((u1 - u0) / 0.8)), 1)
        for i in range(n + 1):
            u = u0 + 0.05 + (u1 - u0 - 0.1) * i / n
            if any(h[0] - 0.12 < u < h[1] + 0.12 for h in holes):
                continue
            wtimber(m, W, u - 0.05, u + 0.05, y0 + 0.12, y1 - 0.14, 0.03, tone(SMOKED), edges="lr")

    muntins(Wall("x", wx0, -1), Z0, bz1)
    muntins(Wall("x", wx1, 1), Z0, bz0)
    inside, outside = Wall("z", bz0, -1), Wall("z", bz1, 1)
    muntins(inside, wx1, X1, [door])
    muntins(outside, wx0, X1, [door])
    # The partition's free corner, and the doorway through it: its jambs, its head, the boards' thickness.
    wbox(m, (door[0] - 0.1, y0, bz0 - 0.03), (door[0], door[3], bz1 + 0.03), "y", tone(SMOKED), faces="XzZ")
    wbox(m, (door[1], y0, bz0 - 0.03), (door[1] + 0.1, door[3], bz1 + 0.03), "y", tone(SMOKED), faces="xzZ")
    wbox(m, (door[0] - 0.1, door[3], bz0 - 0.03), (door[1] + 0.1, door[3] + 0.12, bz1 + 0.03), "x", tone(SMOKED), faces="yzZ")
    wbox(m, (door[0], y0 - 0.02, bz0), (door[1], y0 + 0.004, bz1), "x", tone(TROD), faces="Y")
    # His door, folded back flat against the partition inside the room.
    ledged(m, inside, door[1] + 0.12, door[1] + 1.06, y0 + 0.03, door[3] - 0.03, 0.034, STUD, latch=door[1] + 0.95)
    # His window: its frame, and the shutter folded back beside it.
    wx_a, wx_b, wy_a, wy_b = P.PORTER_WINDOW
    opening_frame(m, FRONT, wx_a, wx_b, wy_a, wy_b, sill=True)
    ledged(m, FRONT, wx_b + 0.16, wx_b + 0.16 + (wx_b - wx_a), wy_a, wy_b, 0.056, STUD)
    # A peg by his door with his cloak, and a shelf with nothing on it but a cup.
    cloak(m, soft, Wall("x", wx1, 1), 3.3, y0 + 1.7, (0.022, 0.02, 0.018), 15.0)
    # (It is over the foot of his bed, where nobody walks.)
    plank(m, (X1 - 0.2, y0 + 1.3, 2.2), (X1, y0 + 1.33, 3.0), tone(STUD), along="z")
    for z in (2.3, 2.9):
        props.slab(m, [(X1 - 0.18, y0 + 1.3), (X1, y0 + 1.3), (X1, y0 + 1.12)], "z", z - 0.015, z + 0.015, tone(SMOKED), grain="p")
    props.pot(soft, (X1 - 0.1, y0 + 1.33, 2.45), [(0.0, 0.03), (0.05, 0.036), (0.1, 0.04)], colour=(0.045, 0.036, 0.026), sides=8)
    st.jug(soft, (X1 - 0.1, y0 + 1.33, 2.75), 1.2, 0.0, 0.8)
    # Outside his room, at the back: sacks, a spare cask's worth of crocks, a rolled pallet (the scene's `Stores` Block).
    st.Sack(soft, (4.5, y0, 9.2), 1.5, 0.0, 0.95, 0.5, 0.3, seed=71.0)
    st.Sack(soft, (5.15, y0, 9.25), 0.2, 0.0, 0.9, 0.5, 0.28, seed=72.0)
    st.Sack(soft, (4.75, y0 + 0.27, 9.25), 1.45, 0.05, 0.9, 0.46, 0.26, seed=73.0, droop=0.03)
    st.crock(soft, (3.75, y0, 9.4), 0.15, 0.32)
    st.crock(soft, (3.45, y0, 9.42), 0.13, 0.27, colour=(0.03, 0.027, 0.022))
    soft.tube([(3.2, y0 + 0.14, 8.55), (3.2, y0 + 0.14, 9.5)], [0.14, 0.14], 9, CLOTH, rgba(props.STRAW, 0.9), caps=True)
    for z in (8.8, 9.25):
        props.rope(soft, [(3.2 + 0.15 * math.cos(a), y0 + 0.14 + 0.15 * math.sin(a), z) for a in [math.tau * i / 8 for i in range(9)]], r=0.008)
    peg_rail(m, soft, BACK, 0.6, 2.6, y0 + 1.7, ((1.0, props.UNDYED, 17.0),))
    dress.cobweb(m, (X0 + 0.03, y1 - 0.03, Z0 + 0.03), (1, 0, 0), (0, 0, 1), 0.7, 3)
    dress.cobweb(m, (X1 - 0.03, y1 - 0.03, Z1 - 0.03), (-1, 0, 0), (0, -1, 0), 0.6, 5)
    dress.cobweb(m, (wx0 - 0.03, y1 - 0.03, Z0 + 0.03), (-1, 0, 0), (0, 0, 1), 0.5, 6)


def rushes(m):
    """Rushes strewn on the taproom's floor: thick along the walls and
    under the tables, kicked thin where people walk."""
    rng = random.Random(77)
    made = 0
    while made < 420:
        x, z = rng.uniform(X0 + 0.1, X1 - 0.1), rng.uniform(Z0 + 0.1, Z1 - 0.1)
        if -2.9 < x < 0.9 and z > 7.6:
            continue    # the hearth's flags are swept
        if x < -4.5 and 3.9 < z < 8.7:
            continue    # the stair
        walked = math.exp(-((x + 0.3 * (z / 9.0)) / 1.2) ** 2) + math.exp(-((z - 6.4) / 0.8) ** 2) * smoothstep(0.5, 2.0, x)
        edge = min(x - X0, X1 - x, z - Z0, Z1 - z)
        if rng.random() < min(walked, 0.92) * smoothstep(0.2, 0.9, edge):
            continue
        a = rng.uniform(0.0, math.pi)
        long, wide = rng.uniform(0.16, 0.34), rng.uniform(0.006, 0.012)
        dx, dz = math.cos(a) * long * 0.5, math.sin(a) * long * 0.5
        px, pz = -math.sin(a) * wide, math.cos(a) * wide
        y = 0.008 + rng.uniform(0.0, 0.006)
        k = rng.uniform(0.6, 1.25)
        c = (props.STRAW[0] * k, props.STRAW[1] * k, props.STRAW[2] * k * 0.9, 1.0)
        m.poly([(x - dx - px, y, z - dz - pz), (x + dx - px, y, z + dz - pz), (x + dx + px, y + 0.003, z + dz + pz), (x - dx + px, y + 0.003, z - dz + pz)], PAINT, c, facing=(0, 1, 0))
        made += 1


def taproom(m, soft):
    """What stands in the taproom and is the house's own: the posts and
    their braces, the door's frame, a hanging, hooks for the lights."""
    deep = 0.36
    for x in POSTS:
        post(m, x, BEAM_Z, F0, C0 - deep, 0.28, 1.72, C0 - deep)
        # A stone under its foot, level with the floor.
        m.poly([(x - 0.21, 0.004, BEAM_Z - 0.21), (x + 0.21, 0.004, BEAM_Z - 0.21), (x + 0.21, 0.004, BEAM_Z + 0.21), (x - 0.21, 0.004, BEAM_Z + 0.21)], FLAGS, (0.5, 0.48, 0.42, 1.0),
               facing=(0, 1, 0))
    # Where the beam meets the right wall: a wall post, and a brace out to the beam over the settle there.
    wtimber(m, RIGHT, BEAM_Z - 0.13, BEAM_Z + 0.13, F0 + 0.14, C0 - deep, 0.05, tone(SMOKED), edges="lr")
    brace(m, (X1 - 0.05, 1.72, BEAM_Z), (X1 - 0.9, C0 - deep + 0.04, BEAM_Z), (X1 - 0.16, C0 - deep - 0.12, BEAM_Z), 0.17, 0.1, tone(SMOKED, 0.08))
    opening_frame(m, FRONT, P.DOOR[0], P.DOOR[1], P.DOOR[2], P.DOOR[3])
    # An iron bracket on the post by the long table, for the lantern the scene hangs from it.
    x = POSTS[1]
    iron = BLACK_IRON
    beam(m, (x, 2.34, BEAM_Z - 0.14), (x, 2.34, BEAM_Z - 0.36), 0.016, 0.022, iron, IRON, end_shade=1.0)
    beam(m, (x, 2.16, BEAM_Z - 0.14), (x, 2.33, BEAM_Z - 0.3), 0.012, 0.016, iron, IRON, end_shade=1.0)
    props.ring(m, (x, 2.305, BEAM_Z - 0.33), (1, 0, 0), r=0.022, thick=0.005, colour=iron, sides=8)
    # Hooks: for the ring of candles, and for the lamp over the bar.
    hook(m, 0.0, C0 - 0.17, 2.7, 0.0)
    m.tube([(4.3, C0 - 0.02, 7.4), (4.3, 2.44, 7.4)], [0.005, 0.005], 4, IRON, BLACK_IRON)
    # A painted cloth on the back wall left of the hearth, and one by the door.
    hanging(m, soft, BACK, -4.25, -3.15, 1.2, 2.3, (0.02, 0.034, 0.028), (0.07, 0.055, 0.025), 41.0)
    hanging(m, soft, RIGHT, 5.95, 6.95, 1.3, 2.3, (0.05, 0.022, 0.014), (0.07, 0.055, 0.025), 43.0)
    rushes(m)
    # A peg rail inside the door with what the drinkers came in.
    peg_rail(m, soft, FRONT, 0.95, 1.95, 1.72, ((1.2, props.UNDYED, 21.0), (1.7, (0.03, 0.02, 0.014), 22.0)))


# ---------------------------------------------------------------- the model

FLOORS_M = {}


def rooms():
    porter.reset(1420)
    g, f, s = porter.Mesh("InnGround"), porter.Mesh("InnFirst"), porter.Mesh("InnSecond")
    soft = porter.Mesh("InnSoft")
    FLOORS_M.update({0: g, 1: f, 2: s})
    for storey, m in FLOORS_M.items():
        outer_walls(m, storey, 3.0 + storey * 5.0)
        ceiling(m, storey)
    ground_floor(g)
    upper_floor(f, 1)
    upper_floor(s, 2)
    stairs(g, f, s)
    hearth(g, soft)
    counter(g, soft)
    back_bar(g, soft)
    taproom(g, soft)
    loft(f, soft)
    top_floor(s, soft)
    seal(s)
    for m in (g, f, s):
        m.build()
    soft.build(smooth=True)
    porter.export("env_inn_rooms")


# ---------------------------------------------------------------- props

def fire(p):
    """The taproom's fire, standing on the hearth stone: firedogs, logs
    burning across them, a bed of embers, the flames (an object of their
    own, `Flame`). It faces -z and is 1.3 m wide."""
    hard, soft = p.hard, p.soft
    st.ash_bed(soft, -0.7, 0.7, -0.36, 0.36, 0.0, 0.05, seed=3.0, heap=(0.0, 0.03, 0.3, 0.06), edge=0.2)
    st.cinders(hard, -0.6, 0.6, -0.3, 0.3, 0.035, 26, seed=4, size=0.024)
    for sx in (-1, 1):
        st.firedog(hard, sx * 0.4, 0.0, -0.3, 0.2, tall=0.5)
    st.burnt_log(soft, (-0.62, 0.23, 0.0), (0.6, 0.22, 0.06), 0.085, 1.0, (0.2, 0.8))
    st.burnt_log(soft, (-0.5, 0.22, 0.2), (0.64, 0.23, 0.17), 0.07, 2.0, (0.15, 0.7))
    st.burnt_log(soft, (-0.56, 0.36, 0.12), (0.5, 0.33, 0.06), 0.06, 3.0, (0.3, 0.9))
    st.burnt_log(soft, (-0.58, 0.24, -0.18), (-0.03, 0.07, -0.12), 0.055, 4.0, (0.5, 1.2))
    st.burnt_log(soft, (0.58, 0.24, -0.2), (0.12, 0.06, -0.16), 0.055, 5.0, (0.45, 1.2))
    c = p.part("Embers")
    for _ in range(90):
        x, z = random.uniform(-0.52, 0.52), random.uniform(-0.24, 0.28)
        d = math.hypot(x / 0.54, z / 0.3)
        y = 0.04 + max(0.0, 1.0 - d) * 0.09 + random.uniform(-0.01, 0.02)
        r = random.uniform(0.016, 0.034)
        heat = random.uniform(0.35, 1.0) * (1.0 - 0.5 * smoothstep(0.5, 1.1, d))
        c.box((x - r, y - r * 0.6, z - r), (x + r, y + r * 0.6, z + r), "embers", (heat, heat, heat, 1.0))
    fl = p.part("Flame")
    for turn, wide, y0, y1, dx, dz in ((0.0, 0.62, 0.08, 1.12, 0.0, 0.05), (0.7, 0.5, 0.08, 1.0, -0.12, 0.08), (-0.75, 0.5, 0.08, 0.94, 0.16, 0.04),
                                       (0.2, 0.34, 0.06, 0.72, -0.4, 0.0), (-0.3, 0.34, 0.06, 0.66, 0.42, 0.02), (1.57, 0.34, 0.08, 0.8, 0.05, 0.02),
                                       (0.1, 0.4, 0.06, 0.6, 0.2, -0.14), (-0.15, 0.4, 0.06, 0.56, -0.24, -0.12)):
        ax, az = math.cos(turn) * wide, math.sin(turn) * wide
        fl.quad((dx - ax, y0, dz - az), (dx + ax, y0, dz + az), (dx + ax, y1, dz + az), (dx - ax, y1, dz - az), "flame", uvs=[(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])


def settle(p):
    """A high-backed settle: 1.8 m long (along x), 0.5 m deep, its back
    1.45 m high at +z. Sat on facing -z."""
    m = p.hard
    hx = 0.9
    end = [(-0.25, 0.0), (-0.13, 0.0), (-0.07, 0.07), (0.1, 0.07), (0.16, 0.0), (0.25, 0.0), (0.25, 1.45), (0.2, 1.45), (0.15, 1.38), (0.11, 1.2), (0.06, 0.98), (-0.06, 0.78),
           (-0.19, 0.71), (-0.25, 0.66)]
    for sx in (-1, 1):
        lo, hi = (hx - 0.045, hx) if sx > 0 else (-hx, -hx + 0.045)
        props.slab(m, end, "x", lo, hi, tone(OAK_DARK, 0.08))
    props.boards(m, (-hx + 0.045, 0.41, -0.235), (hx - 0.045, 0.45, 0.2), "x", "z", 2, OAK, gap=0.004, uneven=0.002)
    props.boards(m, (-hx + 0.045, 0.1, 0.2), (hx - 0.045, 1.38, 0.228), "y", "x", 7, OAK_DARK, gap=0.004, uneven=0.003)
    plank(m, (-hx + 0.045, 1.34, 0.18), (hx - 0.045, 1.43, 0.245), tone(OAK_DARK, 0.06), along="x", ends="")
    plank(m, (-hx + 0.045, 0.74, 0.185), (hx - 0.045, 0.81, 0.205), tone(OAK_DARK, 0.06), along="x", ends="")
    plank(m, (-hx + 0.045, 0.18, -0.22), (hx - 0.045, 0.41, -0.195), tone(OAK_DARK, 0.08), along="x", ends="")
    plank(m, (-hx + 0.045, 0.05, 0.19), (hx - 0.045, 0.14, 0.235), tone(OAK_DARK, 0.06), along="x", ends="")
    # A cushion of sorts: a folded blanket at one end.
    props.tick(p.soft, 0.25, 0.8, -0.2, 0.17, 0.45, 0.05, colour=props.RUSSET, lumps=0.25, seed=5.0, edge=0.12)


RING_R = 0.5
RING_CANDLES = (0.12, 0.085, 0.11, 0.07, 0.115, 0.095, 0.1, 0.08)


def candle_ring(p):
    """An iron ring of candles to hang from a ceiling: 1 m across. Its
    origin is the middle of the ring; the chains rise 0.3 m to the hook."""
    m, soft = p.hard, p.soft
    n = 16
    iron = BLACK_IRON
    for i in range(n):
        a0, a1 = math.tau * i / n, math.tau * (i + 1) / n
        out = (math.cos((a0 + a1) * 0.5), 0.0, math.sin((a0 + a1) * 0.5))
        for r, way in ((RING_R + 0.005, 1.0), (RING_R - 0.005, -1.0)):
            m.poly([(math.cos(a0) * r, -0.025, math.sin(a0) * r), (math.cos(a1) * r, -0.025, math.sin(a1) * r), (math.cos(a1) * r, 0.025, math.sin(a1) * r), (math.cos(a0) * r, 0.025, math.sin(a0) * r)],
                   IRON, iron, facing=(out[0] * way, 0.0, out[2] * way))
        m.poly([(math.cos(a0) * (RING_R - 0.005), 0.025, math.sin(a0) * (RING_R - 0.005)), (math.cos(a1) * (RING_R - 0.005), 0.025, math.sin(a1) * (RING_R - 0.005)),
                (math.cos(a1) * (RING_R + 0.005), 0.025, math.sin(a1) * (RING_R + 0.005)), (math.cos(a0) * (RING_R + 0.005), 0.025, math.sin(a0) * (RING_R + 0.005))], IRON, iron, facing=(0, 1, 0))
        m.poly([(math.cos(a0) * (RING_R - 0.005), -0.025, math.sin(a0) * (RING_R - 0.005)), (math.cos(a1) * (RING_R - 0.005), -0.025, math.sin(a1) * (RING_R - 0.005)),
                (math.cos(a1) * (RING_R + 0.005), -0.025, math.sin(a1) * (RING_R + 0.005)), (math.cos(a0) * (RING_R + 0.005), -0.025, math.sin(a0) * (RING_R + 0.005))], IRON, iron, facing=(0, -1, 0))
    # Two flat bars across it.
    for a in (0.3, 0.3 + math.pi * 0.5):
        beam(m, (math.cos(a) * RING_R, 0.0, math.sin(a) * RING_R), (-math.cos(a) * RING_R, 0.0, -math.sin(a) * RING_R), 0.03, 0.008, iron, IRON, end_shade=1.0, ends="")
    # The candles, each on a pricket in a drip pan, standing out from the ring.
    k = len(RING_CANDLES)
    for i, h in enumerate(RING_CANDLES):
        a = math.tau * (i + 0.5) / k
        x, z = math.cos(a) * (RING_R + 0.045), math.sin(a) * (RING_R + 0.045)
        beam(m, (math.cos(a) * RING_R, -0.01, math.sin(a) * RING_R), (x, 0.0, z), 0.014, 0.01, iron, IRON, end_shade=1.0)
        props.pot(soft, (x, 0.0, z), [(0.0, 0.012), (0.008, 0.03), (0.016, 0.036)], colour=(0.42, 0.4, 0.38), sides=8, mat=IRON, dark_inside=False)
        props.candle(soft, (x, 0.008, z), h=h, r=0.012, lean=random.uniform(-0.04, 0.04), drips=2)
        # Wax run down and hanging from the pan.
        soft.tube([(x + 0.02, 0.0, z), (x + 0.021, -0.03, z), (x + 0.021, -0.05, z)], [0.005, 0.004, 0.002], 4, PAINT, rgba(props.WAX, 0.85), caps=True)
    # Four chains up to a ring on the hook.
    for i in range(4):
        a = math.tau * (i + 0.5) / 4 + 0.3
        foot = (math.cos(a) * RING_R, 0.02, math.sin(a) * RING_R)
        m.tube([foot, (foot[0] * 0.45, 0.17, foot[2] * 0.45), (0.0, 0.27, 0.0)], [0.005, 0.005, 0.005], 4, IRON, iron)
    props.ring(m, (0.0, 0.29, 0.0), (1, 0, 0), r=0.025, thick=0.006, colour=iron, sides=8)


def lantern(p):
    """An iron lantern to hang from a bracket: a square cage with a
    candle in it, a peaked cap, a ring. Its origin is the foot of the
    flame; the ring is 0.3 m above it."""
    m, soft = p.hard, p.soft
    iron = BLACK_IRON
    w, y0, y1 = 0.065, -0.085, 0.14
    m.box((-w, y0 - 0.008, -w), (w, y0, w), IRON, iron)
    m.box((-w - 0.006, y1, -w - 0.006), (w + 0.006, y1 + 0.008, w + 0.006), IRON, iron)
    for sx in (-1, 1):
        for sz in (-1, 1):
            beam(m, (sx * w, y0, sz * w), (sx * w, y1, sz * w), 0.01, 0.01, iron, IRON, end_shade=1.0, ends="")
    # Two thin bars across each side, and a band round the middle.
    for a in range(4):
        c, s = math.cos(a * math.pi * 0.5), math.sin(a * math.pi * 0.5)
        for t in (-0.33, 0.33):
            px, pz = c * w - s * t * w, s * w + c * t * w
            beam(m, (px, y0, pz), (px, y1, pz), 0.005, 0.005, iron, IRON, end_shade=1.0, ends="")
        beam(m, (c * w - s * w, 0.03, s * w + c * w), (c * w + s * w, 0.03, s * w - c * w), 0.012, 0.004, iron, IRON, end_shade=1.0, ends="", up=(c, 0, s))
        # The cap: four sloping plates to a point.
        apex = (0.0, y1 + 0.085, 0.0)
        e = w + 0.012
        pa, pb = (c * e - s * e, y1 + 0.008, s * e + c * e), (c * e + s * e, y1 + 0.008, s * e - c * e)
        m.poly([pa, pb, apex], IRON, iron, facing=(c, 0.7, s))
        m.poly([pa, pb, apex], IRON, col(iron, 0.4), facing=(-c, -0.7, -s))
    m.tube([(0.0, y1 + 0.08, 0.0), (0.0, y1 + 0.13, 0.0)], [0.005, 0.005], 4, IRON, iron)
    props.ring(m, (0.0, y1 + 0.145, 0.0), (1, 0, 0), r=0.02, thick=0.005, colour=iron, sides=8)
    props.candle(soft, (0.0, y0, 0.0), h=-y0 - 0.012, r=0.016, drips=3)


BUILDERS = {"fire": fire, "settle": settle, "candle_ring": candle_ring, "lantern": lantern}


def main():
    only = porter.argv()
    if not only or "rooms" in only:
        rooms()
    for name, fn in BUILDERS.items():
        if only and name not in only:
            continue
        p = props.Prop("inn_" + name)
        fn(p)
        p.export()


if __name__ == "__main__":
    main()
