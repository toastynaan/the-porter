"""The props of the abbey church, its crypt and tower, and two seats of
office. Each is its own model (art/models/prop_<name>.glb), sized to the
collision its scene already has (game/world/props/prop_<name>.tscn),
standing on the floor at its origin:

- choir_stalls, choir_stalls_b, choir_stalls_c: a 4 m run of oak stalls: a
  desk in front, six seats between shaped arms, a panelled back, poppy
  heads on the ends, a block on the middle arm for the run's candle. One
  has a psalter left open and a misericord tipped up (a face under it);
  one a candle stub run down the desk; one is bare.
- altar: the high altar: a stone mensa on a stone back, open under it
  behind a dark frontal; a linen, two prickets, a cross.
- tomb_open: a tomb chest with weepers in its arcading, its lid cracked
  across, one half pushed askew, the other fallen behind it.
- reliquary: the crypt's shrine: a stone plinth, a gabled chest of dull
  gilt copper behind an iron grille.
- bell: the bell on its headstock, hung from the bell floor's beams.
- bell_rope: the rope from the bell's clapper to the tower floor.
- carved_saint, carved_saint_b, carved_saint_c: a stone saint on a plinth
  (hands together; holding a book; a staff), without its head.
- carved_saint_head: the head, which game/drug/carving.gd turns.
- crypt_rail: the oak rail round the crypt stair's well, in the church
  scene's own space.
- abbot_seat: the abbot's seat in the chapter house, on its step.
- lectern: the reader's desk in the refectory, the book left open.

New materials: bronze_bell, gilt_dull (game/world/materials/real/).

Run: tools/build.sh prop_abbey_church   (one prop: ... -- altar)
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import props
import dress
import city_parts as cp
from porter import fbm, lerp, smoothstep
from props import IRON, IRON_C, OAK, OAK_DARK, PAINT, WOOD, CLOTH, beam, boards, plank, rgba, tone

STONE = "stone_church"
DARK = "window_dark"
BLACK = (0.0, 0.0, 0.0, 1.0)
BRONZE = "bronze_bell"
GILT = "gilt_dull"
GRIME = dress.GRIME
G = props.GRAIN
# Stone's tones (the material is pale ashlar; these darken it).
ASHLAR = (0.6, 0.58, 0.54)
CARVED = (0.5, 0.48, 0.45)
# An open book's leaves: as pale as wax, or they are lost against oak.
PAGE = (0.125, 0.11, 0.078)


def stone(k=1.0, base=ASHLAR, a=1.0):
    return (base[0] * k, base[1] * k, base[2] * k, a)


def face(m, pts, facing, colour, mat=WOOD, grain="y"):
    """A flat face through `pts`, looking along `facing`, with the UVs
    timber needs: its grain runs along `grain` ("x", "y" or "z")."""
    c = rgba(colour) if len(colour) == 3 else colour
    k = "xyz".index(grain)
    others = [i for i in range(3) if i != k]
    # Across the grain: whichever other axis the face is not flat to.
    j = others[0] if abs(facing[others[0]]) < abs(facing[others[1]]) else others[1]
    m.poly(pts, mat, c, uvs=[(p[j] * G, p[k] * G) for p in pts], facing=facing)


def face_boards(m, a, b, y0, y1, out, n, colour=OAK_DARK, spread=0.14, mat=WOOD):
    """One face of `n` upright boards from (x, z) `a` to `b`, between y0
    and y1, looking along `out`: a boarded back seen from one side only."""
    cuts = [0.0] + sorted((random.uniform(0.3, 0.7) + i) / n for i in range(n - 1)) + [1.0]
    for t0, t1 in zip(cuts, cuts[1:]):
        p0, p1 = (lerp(a[0], b[0], t0), lerp(a[1], b[1], t0)), (lerp(a[0], b[0], t1), lerp(a[1], b[1], t1))
        w = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        u0, v0 = random.random(), random.random()
        m.poly([(p0[0], y0, p0[1]), (p1[0], y0, p1[1]), (p1[0], y1, p1[1]), (p0[0], y1, p0[1])], mat, tone(colour, spread),
               uvs=[(u0, v0), (u0 + w * G, v0), (u0 + w * G, v0 + (y1 - y0) * G), (u0, v0 + (y1 - y0) * G)], facing=out)


def blind_arch(m, at, out, u0, u1, y0, spring, rise, top, colour, mat=WOOD, back=None, deep=0.02, n=4, sides=True, sill=False, soffit=False):
    """The head of a blind arch cut in a board or a stone: the two
    spandrels between u0 and u1 from `spring` up to `top`, on the face
    `at(u, y, 0)`, and (with `back`, a colour) the face behind the opening,
    `deep` in, from y0 up. `at(u, y, w)` gives a point: u along, y up, w
    out of the face."""
    cx, half = (u0 + u1) * 0.5, (u1 - u0) * 0.5
    prof = cp.arch_profile(half, spring, rise, n, cx)
    right, left = prof[:n + 1], prof[n:]
    c = rgba(colour) if len(colour) == 3 else colour

    def put(pts2, col, w=0.0):
        pts = [at(u, y, w) for u, y in pts2]
        if mat == WOOD:
            m.poly(pts, mat, col, uvs=[(u * G, y * G) for u, y in pts2], facing=out)
        else:
            m.poly(pts, mat, col, facing=out)

    put(right + [(cx, top), (u1, top)], c)
    put(left + [(u0, top), (cx, top)], c)
    if back is not None:
        b = rgba(back) if len(back) == 3 else back
        put([(u0, y0), (u1, y0), (u1, top), (u0, top)], b, -deep)
        if sides:
            for u, way in ((u0, 1.0), (u1, -1.0)):
                side = (at(1, 0, 0)[0] - at(0, 0, 0)[0], 0.0, at(1, 0, 0)[2] - at(0, 0, 0)[2])
                m.poly([at(u, y0, 0.0), at(u, spring, 0.0), at(u, spring, -deep), at(u, y0, -deep)], mat, (c[0] * 0.7, c[1] * 0.7, c[2] * 0.7, 1.0),
                       facing=(side[0] * way, 0.0, side[2] * way))
        if soffit:
            for (ua, ya), (ub, yb) in zip(prof, prof[1:]):
                pa, pb = at(ua, ya, 0.0), at(ub, yb, 0.0)
                mid = at(cx, spring, 0.0)
                m.poly([pa, pb, at(ub, yb, -deep), at(ua, ya, -deep)], mat, (c[0] * 0.6, c[1] * 0.6, c[2] * 0.6, 1.0),
                       facing=(mid[0] - (pa[0] + pb[0]) * 0.5, mid[1] - (pa[1] + pb[1]) * 0.5, mid[2] - (pa[2] + pb[2]) * 0.5))
        if sill:
            m.poly([at(u0, y0, 0.0), at(u1, y0, 0.0), at(u1, y0, -deep), at(u0, y0, -deep)], mat, c, facing=(0, 1, 0))


def mask(m, c, w, h, deep, colour, mat=WOOD, yaw=math.pi, gape=1.0, tilt=0.0):
    """A carved face, a mask: `w` wide and `h` high about `c`, standing
    `deep` out of the face it is cut on. It looks toward -z (`yaw` turns
    it; `tilt` below zero turns it to look up). Worn: a brow, a nose, and
    the dark of two sockets and a mouth, no more."""
    t = props.Placed(m, c, yaw, 1.0, tilt)
    base = rgba(colour) if len(colour) == 3 else colour

    def surface(x, y):
        r = min(math.hypot(x, y * 0.92), 1.0)
        dome = math.sqrt(max(1.0 - r * r, 0.0))
        brow = 0.2 * math.exp(-((y - 0.42) / 0.12) ** 2) * (1.0 - 0.5 * math.exp(-(x / 0.12) ** 2))
        nose = 0.24 * math.exp(-(x / 0.13) ** 2) * math.exp(-((y + 0.1) / 0.3) ** 2)
        return dome * (1.0 + brow + nose) * deep

    def f(u, v):
        # Round, as a head is: u goes round it, v out from its middle.
        x, y = math.cos(u * math.tau) * v, math.sin(u * math.tau) * v / 0.92
        return (x * w * 0.5, y * h * 0.5 * 0.92, surface(x, y * 0.92))

    props.sheet(t, f, 14, 5, mat, lambda u, v: rgba(base, 1.05 - 0.35 * v), uv=(w * G * 3.0, h * G), flip=True)
    dark = (0.02, 0.016, 0.012, 1.0)
    for cx, cy, rx, ry in ((-0.38, 0.2, 0.16, 0.09), (0.38, 0.2, 0.16, 0.09), (0.0, -0.52, 0.26, 0.05 * gape)):
        pts = []
        for i in range(8):
            a = math.tau * i / 8
            x, y = cx + math.cos(a) * rx, cy + math.sin(a) * ry
            pts.append((x * w * 0.5, y * h * 0.5, surface(x, y) + 0.004))
        t.poly(pts, PAINT, dark, facing=(0, 0, 1))


# ---------------------------------------------------------------- choir stalls

def poppy(cz, y0, w, h):
    """A poppy head's outline (z, y) about `cz`, from its neck's +z side
    over its tip to its -z side."""
    half = [(0.3, 0.0), (0.2, 0.13), (0.5, 0.3), (0.56, 0.5), (0.3, 0.6), (0.34, 0.78), (0.13, 0.9)]
    right = [(cz + a * w, y0 + b * h) for a, b in half]
    left = [(cz - a * w, y0 + b * h) for a, b in reversed(half)]
    return right + [(cz, y0 + h)] + left


def open_book(m, p, yaw=0.0, tilt=0.0, w=0.4, d=0.27):
    """A book lying open on `p`: its boards, two blocks of leaves, the
    written columns."""
    b = props.Placed(m, p, yaw, 1.0, tilt)
    b.box((-w * 0.5, 0.0, -d * 0.5), (w * 0.5, 0.008, d * 0.5), PAINT, rgba(props.LEATHER), faces="xXzZY")
    for s in (-1, 1):
        x0, x1 = (0.004, w * 0.5 - 0.012) if s > 0 else (-w * 0.5 + 0.012, -0.004)
        thick = 0.026 if s > 0 else 0.018
        page = rgba(PAGE, 1.0 if s > 0 else 0.88)
        b.box((x0, 0.008, -d * 0.5 + 0.01), (x1, 0.008 + thick, d * 0.5 - 0.01), PAINT, page, faces="xXzZY")
        ink = rgba(PAGE, 0.4)
        for k in range(2):
            u0 = x0 + 0.018 + k * (x1 - x0 - 0.03) * 0.5
            b.poly([(u0, 0.0085 + thick, -d * 0.5 + 0.035), (u0 + (x1 - x0) * 0.5 - 0.03, 0.0085 + thick, -d * 0.5 + 0.035),
                    (u0 + (x1 - x0) * 0.5 - 0.03, 0.0085 + thick, d * 0.5 - 0.045), (u0, 0.0085 + thick, d * 0.5 - 0.045)], PAINT, ink, facing=(0, 1, 0))
    # A rubric: the one mark of dull red.
    b.poly([(0.03, 0.035, -d * 0.5 + 0.035), (0.075, 0.035, -d * 0.5 + 0.035), (0.075, 0.035, -d * 0.5 + 0.075), (0.03, 0.035, -d * 0.5 + 0.075)], PAINT,
           (0.05, 0.014, 0.01, 1.0), facing=(0, 1, 0))


STALL_END = [(-0.03, 0.0), (0.35, 0.0), (0.35, 1.36), (0.33, 1.41)] + poppy(0.245, 1.41, 0.27, 0.31) + \
            [(0.16, 1.41), (0.13, 1.36), (0.1, 1.24), (0.05, 1.12), (0.0, 1.06), (-0.04, 1.0), (-0.05, 0.9), (-0.03, 0.8)]
STALL_ARM = [(0.31, 0.0), (0.31, 1.0), (0.14, 1.0), (0.04, 0.985), (-0.03, 0.94), (-0.04, 0.88), (0.0, 0.8), (0.07, 0.72), (0.09, 0.6), (0.05, 0.5),
             (-0.03, 0.46), (-0.03, 0.0)]
DESK_END = [(-0.36, 0.0), (-0.1, 0.0), (-0.1, 0.86), (-0.12, 0.93), (-0.17, 0.98)] + poppy(-0.235, 0.98, 0.2, 0.24) + [(-0.3, 0.98), (-0.36, 0.96)]


def desk_y(z):
    """The top of the stalls' desk at `z`: it slopes down to the monk."""
    return 0.985 - (z + 0.36) * 0.36


def stalls(p, tipped=(), carved=None, psalter=None, stub=None, shut=None):
    """A run of six stalls. `tipped`: the seats (0..5) left up; `carved`:
    the one of them with a face under it; `psalter`, `stub`, `shut`: the x
    along the desk of an open book, a candle stub, a shut book."""
    m, s = p.hard, p.soft
    n = 6
    xe = 1.93
    pitch = 2.0 * xe / n
    # The boarded floor the stalls stand on, and the back: boards below, a frame of blind arches above the arms, a cornice.
    plank(m, (-xe, 0.0, -0.31), (xe, 0.05, 0.31), tone(OAK_DARK, 0.05), along="x", ends="")
    face_boards(m, (-xe, 0.31), (xe, 0.31), 0.05, 1.05, (0, 0, -1), 14, OAK_DARK)
    face(m, [(-xe, 0.0, 0.345), (xe, 0.0, 0.345), (xe, 1.44, 0.345), (-xe, 1.44, 0.345)], (0, 0, 1), rgba(OAK_DARK, 0.7), grain="x")
    beam(m, (-xe, 1.47, 0.315), (xe, 1.47, 0.315), 0.085, 0.06, tone(OAK_DARK), ends="")
    beam(m, (-xe, 1.03, 0.3), (xe, 1.03, 0.3), 0.03, 0.05, tone(OAK_DARK), ends="")
    for i in range(n + 1):
        x = -xe + i * pitch
        if 0 < i < n:
            beam(m, (x, 1.05, 0.3), (x, 1.44, 0.3), 0.05, 0.025, tone(OAK_DARK), ends="")
            props.slab(m, STALL_ARM, "x", x - 0.025, x + 0.025, tone(OAK_DARK))
            # The elbow, pale where hands have rubbed it.
            beam(m, (x, 1.012, -0.035), (x, 1.012, 0.3), 0.075, 0.03, tone(OAK, 0.06), ends="a")
        if i < n:
            x0, x1 = x + 0.025, x + pitch - 0.025
            mid = (x0 + x1) * 0.5
            for a, b in ((x0, mid), (mid, x1)):
                blind_arch(m, lambda u, y, w: (u, y, 0.292 - w), (0, 0, -1), a, b, 1.05, 1.2, 0.2, 1.44, tone(OAK_DARK, 0.08), back=rgba(OAK_DARK, 0.42), deep=0.018, n=3, sides=False)
            if i in tipped:
                plank(m, (x0 + 0.012, 0.47, 0.268), (x1 - 0.012, 0.84, 0.305), tone(OAK), along="x")
                ledge = [(mid - 0.15, 0.268), (mid - 0.13, 0.215), (mid - 0.07, 0.185), (mid + 0.07, 0.185), (mid + 0.13, 0.215), (mid + 0.15, 0.268)]
                props.slab(m, ledge, "y", 0.8, 0.84, tone(OAK), grain="p")
                if i == carved:
                    mask(s, (mid, 0.672, 0.238), 0.19, 0.24, 0.07, rgba(OAK, 0.95), tilt=-0.2)
                else:
                    m.tube([(mid, 0.8, 0.24), (mid, 0.7, 0.252), (mid, 0.6, 0.266)], [0.075, 0.05, 0.012], 6, WOOD, tone(OAK), squash=(1.0, 0.5))
            else:
                plank(m, (x0 + 0.012, 0.43, -0.04), (x1 - 0.012, 0.465, 0.305), tone(OAK), along="x")
    # On the middle arm, a block for the run's candle (the night scenes stand a candle at the run's middle, 1.1 m up), waxed over.
    beam(m, (0.0, 1.027, 0.0), (0.0, 1.075, 0.0), 0.06, 0.06, tone(OAK_DARK), ends="")
    props.slab(m, [(-0.075, -0.075), (0.075, -0.075), (0.075, 0.075), (-0.075, 0.075)], "y", 1.075, 1.099, tone(OAK_DARK), grain="p")
    for a, length in ((0.4, 0.05), (2.3, 0.075), (4.1, 0.04), (5.2, 0.06)):
        x, z = math.cos(a) * 0.078, math.sin(a) * 0.078
        x, z = max(min(x, 0.0765), -0.0765), max(min(z, 0.0765), -0.0765)
        s.tube([(x, 1.1, z), (x, 1.1 - length * 0.6, z), (x, 1.1 - length, z)], [0.006, 0.007, 0.009], 4, PAINT, rgba(props.WAX, 0.8), caps=True)
    for sx in (-1, 1):
        props.slab(m, STALL_END, "x", sx * 2.0 - (0.07 if sx > 0 else 0.0), sx * 2.0 + (0.07 if sx < 0 else 0.0), tone(OAK_DARK, 0.06))
        props.slab(m, DESK_END, "x", sx * 2.0 - (0.06 if sx > 0 else 0.0), sx * 2.0 + (0.06 if sx < 0 else 0.0), tone(OAK_DARK, 0.06))
    # The desk: a boarded front in a frame, its sloping top, the ledge that stops a book.
    xd = 1.94
    face(m, [(-xd, 0.0, -0.31), (xd, 0.0, -0.31), (xd, 0.9, -0.31), (-xd, 0.9, -0.31)], (0, 0, 1), rgba(OAK_DARK, 0.6), grain="x")
    beam(m, (-xd, 0.06, -0.335), (xd, 0.06, -0.335), 0.05, 0.12, tone(OAK_DARK), ends="")
    beam(m, (-xd, 0.875, -0.337), (xd, 0.875, -0.337), 0.045, 0.09, tone(OAK_DARK), ends="")
    for i in range(n + 1):
        x = -xe + i * pitch
        beam(m, (x, 0.12, -0.335), (x, 0.83, -0.335), 0.06, 0.04, tone(OAK_DARK), ends="")
    for i in range(n):
        x0, x1 = -xe + i * pitch + 0.03, -xe + (i + 1) * pitch - 0.03
        mid = (x0 + x1) * 0.5
        for a, b in ((x0, mid), (mid, x1)):
            blind_arch(m, lambda u, y, w: (u, y, -0.348 - w), (0, 0, -1), a, b, 0.12, 0.6, 0.2, 0.83, tone(OAK_DARK, 0.08), back=rgba(OAK_DARK, 0.42), deep=0.025, n=3, sides=False)
    zc = -0.235
    beam(m, (-xd, desk_y(zc) - 0.016, zc), (xd, desk_y(zc) - 0.016, zc), 0.27, 0.032, tone(OAK, 0.06), up=(0.0, 0.94, 0.34), ends="")
    beam(m, (-xd, desk_y(-0.108) + 0.004, -0.108), (xd, desk_y(-0.108) + 0.004, -0.108), 0.022, 0.04, tone(OAK_DARK), ends="")
    tilt = math.atan(0.36)
    if psalter is not None:
        open_book(m, (psalter, desk_y(-0.225) + 0.002, -0.225), 0.06, tilt)
    if shut is not None:
        props.book(props.Placed(m, (shut, desk_y(-0.225) + 0.002, -0.225), 0.0, 1.0, tilt), (0.0, 0.0, 0.0), 1.45, 0.17, 0.24, 0.05, clasps=1)
    if stub is not None:
        z = -0.3
        y = desk_y(z)
        props.candle(s, (stub, y - 0.004, z), h=0.045, r=0.015, drips=2)
        # What ran down the slope and set against the ledge.
        run = [(stub - 0.012, z), (stub + 0.012, z), (stub + 0.016, -0.22), (stub + 0.006, -0.16), (stub + 0.03, -0.122), (stub - 0.028, -0.122), (stub - 0.008, -0.17),
               (stub - 0.017, -0.24)]
        m.poly([(x, desk_y(zz) + 0.003, zz) for x, zz in run], PAINT, rgba(props.WAX, 0.75), facing=(0, 1, 0))
        for dx, dz in ((0.3, -0.26), (0.34, -0.2), (-0.21, -0.28)):
            r = random.uniform(0.012, 0.02)
            m.poly([(stub + dx + math.cos(math.tau * i / 6) * r, desk_y(dz) + 0.003, dz + math.sin(math.tau * i / 6) * r) for i in range(6)], PAINT,
                   rgba(props.WAX, 0.8), facing=(0, 1, 0))


def choir_stalls(p):
    stalls(p, tipped=(4,), carved=4, psalter=-0.5)


def choir_stalls_b(p):
    stalls(p, tipped=(1, 2), stub=0.7, shut=-1.3)


def choir_stalls_c(p):
    stalls(p, tipped=(), shut=1.1)


# ----------------------------------------------------------------------- altar

def pricket_stick(m, p, h=0.3, taper=0.3, burnt=0.0, lean=0.0, mat=GILT, colour=(0.8, 0.8, 0.8)):
    """A pricket candlestick of latten standing on `p`: a spread foot, a
    knopped stem, a pan, and on its spike a wax taper, unlit, `burnt` down."""
    x, y, z = p
    prof = [(0.0, 0.07), (0.012, 0.072), (0.03, 0.05), (0.05, 0.022), (0.36, 0.016), (0.42, 0.034), (0.48, 0.034), (0.54, 0.016), (0.86, 0.015), (0.93, 0.03),
            (0.985, 0.06), (1.0, 0.062)]
    m.tube([(x, y + t * h, z) for t, _r in prof], [r for _t, r in prof], 8, mat, [rgba(colour, 0.7 + 0.3 * t) for t, _r in prof], caps=True)
    top = y + h
    m.poly([(x + math.cos(math.tau * i / 8) * 0.055, top - 0.006, z + math.sin(math.tau * i / 8) * 0.055) for i in range(8)], PAINT, rgba(props.WAX, 0.6),
           facing=(0, 1, 0))
    ch = taper * (1.0 - burnt)
    tip = (x + lean * ch, top + ch, z)
    wax = rgba(props.WAX, 0.92)
    m.tube([(x, top - 0.006, z), (x + lean * ch * 0.5, top + ch * 0.5, z), tip], [0.016, 0.0145, 0.0125], 7, PAINT, [rgba(props.WAX, 0.7), wax, wax], caps=True)
    m.tube([tip, (tip[0], tip[1] + 0.012, tip[2])], [0.002, 0.0012], 3, PAINT, (0.02, 0.02, 0.02, 1.0))
    for _ in range(3):
        a, length = random.uniform(0.0, math.tau), random.uniform(0.2, 0.6) * ch
        dx, dz = math.cos(a) * 0.012, math.sin(a) * 0.012
        m.tube([(tip[0] + dx, tip[1] - 0.004, tip[2] + dz), (tip[0] + dx, tip[1] - length, tip[2] + dz)], [0.004, 0.0065], 4, PAINT, wax, caps=True)


def altar(p):
    m, s = p.hard, p.soft
    # The mensa, a moulding under its edge, and the stone back it stands on. Under it, in front of the back, is open: he hides there.
    m.box((-1.02, 0.91, -0.52), (1.02, 1.0, 0.5), STONE, stone(0.95), faces="xXzZ")
    m.box((-0.99, 0.86, -0.49), (0.99, 0.91, 0.5), STONE, stone(0.75), faces="xXzZ")
    m.poly([(-0.99, 0.86, -0.49), (0.99, 0.86, -0.49), (0.99, 0.86, 0.2), (-0.99, 0.86, 0.2)], STONE, stone(0.12), facing=(0, -1, 0))
    for (a, b, out) in (((-0.98, 0.5), (0.98, 0.5), (0, 0, 1)), ((-0.98, 0.2), (-0.98, 0.5), (-1, 0, 0)), ((0.98, 0.2), (0.98, 0.5), (1, 0, 0))):
        m.poly([(a[0], 0.0, a[1]), (b[0], 0.0, b[1]), (b[0], 0.86, b[1]), (a[0], 0.86, a[1])], STONE, [stone(0.6), stone(0.6), stone(0.85), stone(0.85)], facing=out)
    m.poly([(-0.98, 0.0, 0.2), (0.98, 0.0, 0.2), (0.98, 0.86, 0.2), (-0.98, 0.86, 0.2)], STONE, [stone(0.05), stone(0.05), stone(0.16), stone(0.16)], facing=(0, 0, -1))
    # The floor under it, black.
    m.poly([(-1.0, 0.012, -0.5), (1.0, 0.012, -0.5), (1.0, 0.012, 0.2), (-1.0, 0.012, 0.2)], DARK, BLACK, facing=(0, 1, 0))

    # The frontal: dark cloth round the front and both ends, hanging from under the mensa's edge to a hand above the floor
    # (he looks out under its hem). Two orphreys and a band along its head, in dull thread. In one place it has been pushed in.
    xf, zf, zb = 1.035, -0.537, 0.2
    side = zb - zf
    total = side * 2.0 + xf * 2.0
    ground, band, edge = (0.018, 0.0105, 0.009), (0.045, 0.034, 0.017), (0.012, 0.01, 0.009)

    def path(d):
        if d < side:
            return (-xf, zb - d, (-1.0, 0.0))
        if d < side + 2.0 * xf:
            return (-xf + (d - side), zf, (0.0, -1.0))
        return (xf, zf + (d - side - 2.0 * xf), (1.0, 0.0))

    def cloth(u, v, lift=0.0):
        d = u * total
        x, z, n = path(d)
        hem = 0.135 + 0.022 * fbm(d, 0.0, 1.7, 2, 3.0)
        # Where it was pushed in: the hem caught up, the cloth drawn back under the stone.
        push = math.exp(-((d - side - 0.62) / 0.2) ** 2) if side < d < side + 2.0 * xf else 0.0
        hem += 0.1 * push
        y = lerp(0.985, hem, v)
        fold = (0.012 * math.sin(d * 13.0 + 1.3 * math.sin(d * 3.1)) + 0.009 * fbm(d, y, 5.0, 2, 7.0)) * smoothstep(0.0, 0.5, v)
        out = fold + 0.004 + lift - 0.07 * push * smoothstep(0.2, 1.0, v)
        return (x + n[0] * out, y, z + n[1] * out)

    def dye(base):
        def c(u, v):
            # Dirty at the hem, from the floor.
            return rgba(base, (0.8 + 0.3 * fbm(u * total, v, 2.2, 3, 5.0)) * (1.0 - 0.35 * smoothstep(0.75, 1.0, v)))
        return c

    props.sheet(s, cloth, 46, 8, CLOTH, dye(ground), both=True)
    props.sheet(s, lambda u, v: cloth(u, v * 0.19, 0.004), 46, 1, CLOTH, dye(band))
    props.sheet(s, lambda u, v: cloth(u, 0.19 + v * 0.012, 0.005), 46, 1, CLOTH, dye(edge))
    for x in (-0.6, 0.6):
        d0 = (side + xf + x - 0.075) / total
        props.sheet(s, lambda u, v: cloth(d0 + u * 0.15 / total, 0.2 + v * 0.8, 0.004), 2, 7, CLOTH, dye(band))

    # The linen over the top, hanging at the ends; a little over the front edge.
    wide, drop, z0, z1 = 2.07, 0.44, -0.537, 0.47

    def linen(u, v):
        k = u * 20.0
        d = (k / 4.0 - 1.0) * drop if k < 4.0 else ((k - 4.0) / 12.0 * wide if k < 16.0 else wide + (k - 16.0) / 4.0 * drop)
        x = -wide * 0.5 + min(max(d, 0.0), wide)
        z = lerp(z0, z1, v)
        down = max(-d, d - wide, 0.0)
        out = (0.008 + 0.022 * smoothstep(0.0, drop, down) + 0.01 * fbm(d * 2.0, z, 5.0, 2, 9.0)) if down > 0.0 else 0.0
        y = 1.006 - down * (1.0 + 0.05 * fbm(z, d, 2.0, 2, 4.0)) + (0.002 * fbm(d, z, 6.0, 2, 1.0) if down == 0.0 else 0.0)
        return (x + (out if d > wide else -out), y, z)

    props.sheet(s, linen, 20, 5, CLOTH, lambda u, v: rgba(props.LINEN, 0.84 + 0.2 * fbm(u * 3.0, v, 3.0, 3, 2.0)), both=True)
    # Two prickets, their tapers unlit, one burnt lower; a plain cross of oak on a stepped foot.
    pricket_stick(s, (-0.68, 1.008, 0.22), h=0.3, taper=0.34, burnt=0.0, lean=0.0)
    pricket_stick(s, (0.68, 1.008, 0.24), h=0.3, taper=0.34, burnt=0.42, lean=0.035)
    m.poly([(0.68 + math.cos(math.tau * i / 7) * r, 1.0095, 0.3 + math.sin(math.tau * i / 7) * r * 0.7) for i, r in enumerate((0.03, 0.022, 0.035, 0.02, 0.028, 0.018, 0.03))], PAINT,
           rgba(props.WAX, 0.7), facing=(0, 1, 0))
    plank(m, (-0.13, 1.006, 0.27), (0.13, 1.04, 0.43), tone(OAK_DARK), along="x")
    plank(m, (-0.085, 1.04, 0.3), (0.085, 1.075, 0.4), tone(OAK_DARK), along="x")
    beam(m, (0.0, 1.075, 0.35), (0.004, 1.72, 0.35), 0.05, 0.032, tone(OAK_DARK))
    beam(m, (-0.2, 1.53, 0.349), (0.2, 1.534, 0.349), 0.032, 0.05, tone(OAK_DARK))


# ------------------------------------------------------------------------ tomb

def tomb_open(p):
    m, s = p.hard, p.soft
    X, Z, y0, y1 = 1.1, 0.5, 0.13, 0.75
    # The plinth, the chest's cap, its rim.
    m.box((-X - 0.035, 0.0, -Z - 0.035), (X + 0.035, 0.09, Z + 0.035), STONE, stone(0.62), top_color=stone(0.8), faces="xXzZY")
    m.box((-X - 0.015, 0.09, -Z - 0.015), (X + 0.015, y0, Z + 0.015), STONE, stone(0.75), faces="xXzZY")
    m.box((-X - 0.03, y1, -Z - 0.03), (X + 0.03, 0.85, Z + 0.03), STONE, stone(0.9), faces="xXzZy")
    for a, b in (((-X - 0.03, -Z - 0.03), (X + 0.03, -Z + 0.1)), ((-X - 0.03, Z - 0.1), (X + 0.03, Z + 0.03)), ((-X - 0.03, -Z + 0.1), (-X + 0.1, Z - 0.1)),
                 ((X - 0.1, -Z + 0.1), (X + 0.03, Z - 0.1))):
        m.poly([(a[0], 0.85, a[1]), (b[0], 0.85, a[1]), (b[0], 0.85, b[1]), (a[0], 0.85, b[1])], STONE, stone(0.9), facing=(0, 1, 0))
    # Inside: stone a little way down, then black.
    xi, zi = X - 0.1, Z - 0.1
    for a, b, n in (((-xi, -zi), (xi, -zi), (0, 0, 1)), ((xi, zi), (-xi, zi), (0, 0, -1)), ((-xi, zi), (-xi, -zi), (1, 0, 0)), ((xi, -zi), (xi, zi), (-1, 0, 0))):
        m.poly([(a[0], 0.55, a[1]), (b[0], 0.55, b[1]), (b[0], 0.85, b[1]), (a[0], 0.85, a[1])], STONE, [stone(0.03), stone(0.03), stone(0.4), stone(0.4)], facing=n)
        m.poly([(a[0], 0.1, a[1]), (b[0], 0.1, b[1]), (b[0], 0.55, b[1]), (a[0], 0.55, a[1])], DARK, BLACK, facing=n)
    m.poly([(-xi, 0.1, -zi), (xi, 0.1, -zi), (xi, 0.1, zi), (-xi, 0.1, zi)], DARK, BLACK, facing=(0, 1, 0))

    def arcade(at, out, length, bays, empty, yaw):
        pier, shaft = 0.06, 0.05
        w = (length - 2.0 * pier - (bays - 1) * shaft) / bays
        u = -length * 0.5
        strips = [(u, u + pier)]
        for i in range(bays):
            u0 = -length * 0.5 + pier + i * (w + shaft)
            blind_arch(m, at, out, u0, u0 + w, y0, y0 + 0.3, 0.28, y1, stone(0.92), mat=STONE, back=stone(0.36), deep=0.05, sill=True, soffit=True)
            strips.append((u0 + w, u0 + w + (shaft if i < bays - 1 else pier)))
            if i not in empty:
                c = at((u0 + u0 + w) * 0.5, y0, -0.028)
                dress.figure(s, c, yaw, 0.5, STONE, CARVED)
        for a, b in strips:
            m.poly([at(a, y0, 0.0), at(b, y0, 0.0), at(b, y1, 0.0), at(a, y1, 0.0)], STONE, stone(0.92), facing=out)

    arcade(lambda u, y, w: (u, y, Z + w), (0, 0, 1), 2.0 * X, 5, (3,), 0.0)
    arcade(lambda u, y, w: (-u, y, -Z - w), (0, 0, -1), 2.0 * X, 5, (0, 3), math.pi)
    arcade(lambda u, y, w: (X + w, y, -u), (1, 0, 0), 2.0 * Z, 2, (0, 1), 0.0)
    arcade(lambda u, y, w: (-X - w, y, u), (-1, 0, 0), 2.0 * Z, 2, (0, 1), 0.0)

    # The lid, cracked across: the half that is left lies askew over the head end, a cross cut in relief along it.
    lid = props.Placed(m, (-0.45, 0.85, 0.0), math.radians(-3.0))
    edge = [(0.63, -0.54), (0.66, -0.4), (0.6, -0.27), (0.68, -0.12), (0.62, 0.02), (0.7, 0.16), (0.64, 0.3), (0.71, 0.43), (0.66, 0.54)]
    props.slab(lid, [(-0.69, -0.54)] + edge + [(-0.69, 0.54)], "y", 0.0, 0.075, stone(0.95), mat=STONE)
    props.slab(lid, [(-0.66, -0.51)] + [(x - 0.02, max(min(z, 0.51), -0.51)) for x, z in edge] + [(-0.66, 0.51)], "y", 0.075, 0.12, stone(1.0), mat=STONE)
    lid.box((-0.6, 0.12, -0.025), (0.6, 0.135, 0.025), STONE, stone(0.85), faces="xzZY")
    lid.box((-0.42, 0.12, -0.2), (-0.36, 0.135, 0.2), STONE, stone(0.85), faces="xXzZY")
    # The other half stands where it fell, behind the chest, against its side.
    half = props.Placed(m, (0.5, 0.0, -Z - 0.035 - 0.25), math.radians(4.0), 1.0, math.radians(-74.0))
    props.slab(half, [(-0.5, 0.0), (0.46, 0.0), (0.52, 0.2), (0.44, 0.38), (0.5, 0.55), (0.42, 0.72), (0.48, 0.9), (-0.5, 0.9)], "y", 0.0, 0.12, stone(0.7), mat=STONE)


# ------------------------------------------------------------------- reliquary

def frustum(m, lo, hi, y0, y1, mat, colour, top=True, top_colour=None):
    """A square course of stone, `lo` half-wide at y0 and `hi` at y1."""
    c = colour if len(colour) == 4 else rgba(colour)
    tc = top_colour or c
    for sx, sz in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        tx, tz = -sz, sx
        pts = [(sx * q + tx * q * side, y, sz * q + tz * q * side) for q, y, side in ((lo, y0, -1), (lo, y0, 1), (hi, y1, 1), (hi, y1, -1))]
        m.poly(pts, mat, [c, c, tc, tc], facing=(sx, 0.2 if lo > hi else 0.0, sz))
    if top:
        m.poly([(-hi, y1, -hi), (hi, y1, -hi), (hi, y1, hi), (-hi, y1, hi)], mat, tc, facing=(0, 1, 0))


def reliquary(p):
    m, s = p.hard, p.soft
    # The plinth: a base, a die with a sunk panel on each face, a cap.
    frustum(m, 0.4, 0.4, 0.0, 0.1, STONE, stone(0.6), top_colour=stone(0.75))
    frustum(m, 0.4, 0.345, 0.1, 0.15, STONE, stone(0.8))
    frustum(m, 0.345, 0.345, 0.15, 0.43, STONE, stone(0.78), top=False, top_colour=stone(0.9))
    frustum(m, 0.345, 0.4, 0.43, 0.48, STONE, stone(0.62), top=False)
    frustum(m, 0.4, 0.4, 0.48, 0.54, STONE, stone(0.95))
    for k, (at, out) in enumerate(((lambda u, y, w: (u, y, -0.345 - w), (0, 0, -1)), (lambda u, y, w: (-0.345 - w, y, -u), (-1, 0, 0)),
                                   (lambda u, y, w: (-u, y, 0.345 + w), (0, 0, 1)), (lambda u, y, w: (0.345 + w, y, u), (1, 0, 0)))):
        for u0, u1 in ((-0.27, -0.01), (0.01, 0.27)):
            blind_arch(m, lambda u, y, w, at=at: at(u, y, w + 0.004), out, u0, u1, 0.18, 0.25, 0.15, 0.4, stone(0.78), mat=STONE, back=stone(0.4), deep=0.002, n=3,
                       sides=False)
        # Rust from the grille's feet has run down the stone.
        for u in (-0.36, 0.36, random.uniform(-0.2, 0.2)):
            q = at(u * 0.93, 0.47, 0.058 if abs(u) > 0.3 else 0.004)
            dress.run(m, (q[0], q[1], q[2]), (out[0], out[2]), 0.07, random.uniform(0.2, 0.4), dress.RUST, 0.55, seed=k + u)

    # The shrine: a house of copper gilt, dulled and handled: arcaded sides, a pitched roof, a crest along its ridge.
    # Its long side is to -X, the way the crypt is come into.
    def gilt(k=1.0):
        return rgba((0.9, 0.86, 0.8), k * random.uniform(0.85, 1.1))

    hx, hz, yb, ye, yr = 0.13, 0.28, 0.575, 0.8, 0.96
    m.box((-hx - 0.02, 0.54, -hz - 0.02), (hx + 0.02, yb, hz + 0.02), GILT, gilt(0.6), faces="xXzZY")
    for sx in (-1, 1):
        at = (lambda u, y, w, sx=sx: (sx * (hx + w), y, u))
        for i in range(3):
            u0 = -hz + 0.015 + i * (2.0 * hz - 0.03) / 3.0
            u1 = u0 + (2.0 * hz - 0.03) / 3.0
            blind_arch(m, at, (sx, 0, 0), u0 + 0.035, u1 - 0.035, yb + 0.035, yb + 0.09, 0.07, ye - 0.012, gilt(1.0), mat=GILT, back=gilt(0.16), deep=0.008, n=3,
                       sides=False)
            m.poly([at(u0 - 0.035, yb, 0.0), at(u0 + 0.035, yb, 0.0), at(u0 + 0.035, ye, 0.0), at(u0 - 0.035, ye, 0.0)], GILT, gilt(1.0), facing=(sx, 0, 0))
        m.poly([at(hz - 0.05, yb, 0.0), at(hz, yb, 0.0), at(hz, ye, 0.0), at(hz - 0.05, ye, 0.0)], GILT, gilt(1.0), facing=(sx, 0, 0))
        m.poly([at(-hz, yb, 0.0), at(hz, yb, 0.0), at(hz, yb + 0.035, 0.0), at(-hz, yb + 0.035, 0.0)], GILT, gilt(0.9), facing=(sx, 0, 0))
        m.poly([at(-hz, ye - 0.012, 0.0), at(hz, ye - 0.012, 0.0), at(hz, ye, 0.0), at(-hz, ye, 0.0)], GILT, gilt(1.0), facing=(sx, 0, 0))
        # The roof's slope, in plates; rubbed pale along the eaves where it is lifted.
        for i in range(4):
            z0, z1 = -hz - 0.012 + i * (2.0 * hz + 0.024) / 4.0, -hz - 0.012 + (i + 1) * (2.0 * hz + 0.024) / 4.0
            k = random.uniform(0.75, 1.0)
            m.poly([(sx * (hx + 0.016), ye - 0.006, z0 + 0.002), (sx * (hx + 0.016), ye - 0.006, z1 - 0.002), (0.0, yr, z1 - 0.002), (0.0, yr, z0 + 0.002)], GILT,
                   [gilt(k * 1.2), gilt(k * 1.2), gilt(k * 0.9), gilt(k * 0.9)], facing=(sx, 0.8, 0))
    for sz in (-1, 1):
        # The gable ends: one arch each, a dark stone set over it.
        m.poly([(-hx, yb, sz * hz), (hx, yb, sz * hz), (hx, ye, sz * hz), (0.0, yr - 0.008, sz * hz), (-hx, ye, sz * hz)], GILT, gilt(0.9), facing=(0, 0, sz))
        at = (lambda u, y, w, sz=sz: (u, y, sz * (hz + w)))
        blind_arch(m, lambda u, y, w, at=at: at(u, y, w + 0.006), (0, 0, sz), -0.075, 0.075, yb + 0.012, yb + 0.1, 0.1, ye, gilt(1.0), mat=GILT, back=gilt(0.16),
                   deep=0.003, n=3, sides=False)
        m.poly([(math.cos(math.tau * i / 6) * 0.014, ye + 0.05 + math.sin(math.tau * i / 6) * 0.014, sz * (hz + 0.004)) for i in range(6)], PAINT, (0.012, 0.012, 0.02, 1.0),
               facing=(0, 0, sz))
    # The crest, pierced, and its three knobs; four feet.
    crest = [(-hz - 0.012, yr - 0.004)]
    for i in range(8):
        z0 = -hz + i * 2.0 * hz / 8.0
        crest += [(z0 + 0.008, yr + 0.03), (z0 + 0.03, yr + 0.042), (z0 + 0.052, yr + 0.03)]
    crest += [(hz + 0.012, yr - 0.004)]
    props.slab(m, crest, "x", -0.004, 0.004, gilt(0.85), mat=GILT)
    for z in (-hz - 0.004, 0.0, hz + 0.004):
        s.tube([(0.0, yr + 0.02, z), (0.0, yr + 0.05, z), (0.0, yr + 0.072, z), (0.0, yr + 0.09, z)], [0.008, 0.012, 0.022, 0.006], 6, GILT, gilt(1.0), caps=True)

    # The grille: iron bars on a frame, a door in the side toward -X with its lock; rusted.
    def iron(k=1.0):
        r = random.random()
        c = (lerp(IRON_C[0], props.RUST_C[0], r * 0.4), lerp(IRON_C[1], props.RUST_C[1], r * 0.4), lerp(IRON_C[2], props.RUST_C[2], r * 0.4))
        return rgba(c, k * 0.8)

    g, y0, y1 = 0.37, 0.54, 1.08
    for sx in (-1, 1):
        for sz in (-1, 1):
            beam(m, (sx * g, y0, sz * g), (sx * g, y1 + 0.03, sz * g), 0.026, 0.026, iron(), IRON, end_shade=1.0)
    n = 9
    for k in range(4):
        ax, az = ((1, 0), (0, 1), (-1, 0), (0, -1))[k]     # along the side
        ox, oz = az, -ax                                      # out of it
        def at(u, y, w=0.0):
            return (ax * u + ox * (g + w), y, az * u + oz * (g + w))
        for y in (y0 + 0.012, y0 + 0.2, y1 - 0.012):
            beam(m, at(-g, y), at(g, y), 0.008, 0.03, iron(), IRON, ends="", end_shade=1.0, up=(0, 1, 0))
        for i in range(n):
            u = -g + (i + 1) * 2.0 * g / (n + 1)
            lean = random.uniform(-0.004, 0.004)
            beam(m, at(u, y0), at(u + lean, y1), 0.012, 0.012, iron(), IRON, ends="", end_shade=1.0, roll=math.pi * 0.25)
    for i in range(n):
        u = -g + (i + 1) * 2.0 * g / (n + 1)
        beam(m, (u, y1, -g), (u, y1, g), 0.012, 0.012, iron(), IRON, ends="", end_shade=1.0, roll=math.pi * 0.25)
    for z in (-g, 0.0, g):
        beam(m, (-g, y1, z), (g, y1, z), 0.03, 0.008, iron(), IRON, ends="", end_shade=1.0)
    # The door's frame, its two hinges, the lock.
    for z in (-0.19, 0.19):
        beam(m, (-g - 0.006, y0 + 0.2, z), (-g - 0.006, y1 - 0.012, z), 0.03, 0.01, iron(), IRON, end_shade=1.0)
    for y in (y0 + 0.3, y1 - 0.1):
        m.tube([(-g - 0.012, y - 0.03, 0.2), (-g - 0.012, y + 0.03, 0.2)], [0.012, 0.012], 5, IRON, iron(), caps=True)
    m.box((-g - 0.04, y0 + 0.36, -0.235), (-g - 0.004, y0 + 0.46, -0.15), IRON, iron(0.9))
    m.poly([(-g - 0.0405, y0 + 0.39, -0.2), (-g - 0.0405, y0 + 0.39, -0.188), (-g - 0.0405, y0 + 0.425, -0.19), (-g - 0.0405, y0 + 0.425, -0.198)], DARK, BLACK, facing=(-1, 0, 0))
    # Wax where candles have been stood on the cap, against the bars.
    for x, z in ((-0.385, 0.3), (-0.385, -0.31), (0.1, -0.385)):
        props.candle(s, (x, 0.54, z), h=random.uniform(0.02, 0.05), r=0.012, drips=1)


# --------------------------------------------------------------- bell and rope

BELL = [(0.0, 0.6), (0.035, 0.6), (0.075, 0.565), (0.11, 0.54), (0.125, 0.548), (0.14, 0.52), (0.25, 0.445), (0.4, 0.385), (0.6, 0.345), (0.7, 0.336), (0.715, 0.348),
        (0.73, 0.335), (0.76, 0.334), (0.775, 0.345), (0.79, 0.33), (0.83, 0.31), (0.87, 0.24), (0.9, 0.11)]


def bell(p):
    m, s = p.hard, p.soft

    def bronze(k=1.0):
        return rgba((0.85, 0.8, 0.68), k)

    # The bell: darker to the crown, greened in streaks; its mouth and inside, seen from below.
    def skin(u, v):
        j = min(int(round(v * (len(BELL) - 1))), len(BELL) - 1)
        y, r = BELL[j]
        a = u * math.tau
        return (math.cos(a) * r, y, math.sin(a) * r)

    def patina(u, v):
        k = lerp(1.1, 0.7, v) * (0.85 + 0.25 * fbm(u * 9.0, v * 2.0, 1.0, 3, 2.0))
        green = smoothstep(0.1, 0.6, fbm(u * 14.0, v * 1.5, 1.0, 2, 6.0))
        return (0.85 * k * (1.0 - 0.3 * green), 0.8 * k, 0.68 * k * (1.0 - 0.1 * green), 1.0)

    props.sheet(s, skin, 16, len(BELL) - 1, BRONZE, patina, flip=True)
    inner = [(0.0, 0.6), (0.02, 0.55), (0.1, 0.5), (0.3, 0.4), (0.6, 0.31), (0.8, 0.27), (0.86, 0.0)]

    def inside(u, v):
        j = min(int(round(v * (len(inner) - 1))), len(inner) - 1)
        y, r = inner[j]
        a = u * math.tau
        return (math.cos(a) * r, y, math.sin(a) * r)

    props.sheet(s, inside, 16, len(inner) - 1, BRONZE, lambda u, v: bronze(lerp(0.5, 0.08, v)))
    m.poly([(math.cos(math.tau * i / 8) * 0.1, 0.9, math.sin(math.tau * i / 8) * 0.1) for i in range(8)], BRONZE, bronze(0.6), facing=(0, 1, 0))
    # The canons, strapped to the headstock.
    m.box((-0.07, 0.9, -0.09), (0.07, 1.02, 0.09), BRONZE, bronze(0.6), faces="xXzZ")
    for z in (-0.13, 0.13):
        props.ring(s, (0.0, 0.94, z), (0, 0, 1), r=0.07, thick=0.022, colour=bronze(0.6), mat=BRONZE, sides=8)
    # The headstock: an oak beam along Z, iron straps round it down to the canons, a gudgeon in each end.
    plank(m, (-0.12, 1.02, -0.8), (0.12, 1.27, 0.8), tone(OAK_DARK), along="z")
    for z in (-0.6, -0.14, 0.14, 0.6):
        beam(m, (0.0, 1.145, z - 0.025), (0.0, 1.145, z + 0.025), 0.256, 0.266, IRON_C, IRON, ends="", end_shade=1.0)
        if abs(z) < 0.3:
            for sx in (-1, 1):
                beam(m, (sx * 0.124, 1.02, z), (sx * 0.075, 0.92, z), 0.05, 0.008, IRON_C, IRON, up=(sx, 0.4, 0), end_shade=1.0)
                props.nail(m, (sx * 0.128, 1.2, z), (sx, 0, 0), r=0.014)
    for sz in (-1, 1):
        m.tube([(0.0, 1.13, sz * 0.78), (0.0, 1.13, sz * 0.98)], [0.03, 0.03], 7, IRON, IRON_C, caps=True)
        # What carries it: a bearing block between two hangers, which go up to the bell floor's beams (at Z +-0.9, 2.24 m over the bell's foot).
        beam(m, (-0.42, 1.05, sz * 0.9), (0.42, 1.05, sz * 0.9), 0.16, 0.16, tone(OAK_DARK))
        m.box((-0.05, 1.13, sz * 0.9 - 0.06), (0.05, 1.175, sz * 0.9 + 0.06), IRON, IRON_C, faces="xXzZY")
        for sx in (-1, 1):
            beam(m, (sx * 0.34, 0.9, sz * 0.9), (sx * 0.34, 2.26, sz * 0.9), 0.12, 0.14, tone(OAK_DARK))
            beam(m, (sx * 0.34, 1.05, sz * 0.9 - sz * 0.075), (sx * 0.34, 1.05, sz * 0.9 + sz * 0.11), 0.03, 0.03, tone(OAK), end_shade=0.8)
            beam(m, (sx * 0.3, 1.2, sz * 0.9), (sx * 0.06, 1.72, sz * 0.9), 0.07, 0.08, tone(OAK_DARK), up=(0, 0, 1))
        beam(m, (-0.34, 1.76, sz * 0.9), (0.34, 1.76, sz * 0.9), 0.1, 0.1, tone(OAK_DARK), ends="")
    # The clapper, hanging plumb; the rope is made fast to its flight.
    iron = rgba((0.42, 0.4, 0.38))
    s.tube([(0.0, 0.86, 0.0), (0.0, 0.8, 0.0), (0.0, 0.3, 0.0), (0.0, 0.2, 0.0), (0.0, 0.13, 0.0), (0.0, 0.06, 0.0), (0.0, 0.03, 0.0), (0.0, -0.08, 0.0)],
           [0.012, 0.02, 0.024, 0.045, 0.085, 0.07, 0.028, 0.02], 8, IRON, iron, caps=True)
    props.ring(s, (0.0, -0.1, 0.0), (1, 0, 0), r=0.03, thick=0.009, colour=iron, sides=8)


def bell_rope(p):
    """From the clapper's ring (8.5 m over the scene's origin) to the tower
    floor (0.75 m under it): hemp, dark and hard where hands take it, two
    knots to grip, its end frayed, a turn of it on the floor."""
    s = p.soft
    hemp = (0.085, 0.068, 0.042)
    floor = -0.75
    pts, cols, radii = [], [], []
    n = 52
    for i in range(n + 1):
        y = lerp(8.52, floor + 0.03, (i / n) ** 0.8)
        hang = smoothstep(8.5, 6.0, y)
        low = smoothstep(1.4, -0.75, y)
        # It hangs in a slow bend, as a rope that has been coiled does, and its foot is drawn aside to the turn on the floor.
        x = 0.06 * fbm(y, 0.0, 0.35, 2, 3.0) * hang + 0.035 * math.sin(y * 1.9) * hang * (1.0 - low) + 0.16 * low * low
        z = 0.06 * fbm(y, 5.0, 0.3, 2, 8.0) * hang + 0.03 * math.sin(y * 1.3 + 1.0) * hang * (1.0 - low) - 0.07 * low * low
        handled = smoothstep(1.6, 1.0, y) * smoothstep(-0.5, 0.1, y)
        k = (0.85 if i % 2 else 1.1) * lerp(1.0, 0.5, handled) * lerp(0.6, 1.0, smoothstep(8.5, 5.0, y))
        pts.append((x, y, z))
        cols.append(rgba(hemp, k))
        radii.append(0.02 * lerp(1.0, 0.88, handled))
    s.tube(pts, radii, 6, CLOTH, cols, caps=True)
    # The hitch on the clapper's ring.
    s.tube([(0.0, 8.44, 0.0), (0.0, 8.47, 0.0), (0.0, 8.52, 0.0), (0.0, 8.55, 0.0)], [0.022, 0.042, 0.04, 0.015], 6, CLOTH, rgba(hemp, 0.6), caps=True)

    def at(y):
        for a, b in zip(pts, pts[1:]):
            if b[1] <= y <= a[1]:
                t = (a[1] - y) / max(a[1] - b[1], 1e-6)
                return (lerp(a[0], b[0], t), y, lerp(a[2], b[2], t))
        return pts[-1]

    # Two knots to grip, pulled hard and out of shape: each a lump with a turn of the rope across it.
    for y, big in ((0.74, 1.0), (0.22, 1.25)):
        c = at(y)
        s.tube([(c[0], y - 0.05 * big, c[2]), (c[0] + 0.012, y - 0.02, c[2] - 0.006), (c[0] - 0.01, y + 0.025 * big, c[2] + 0.008), (c[0], y + 0.055 * big, c[2])],
               [0.022, 0.04 * big, 0.036 * big, 0.022], 6, CLOTH, rgba(hemp, 0.5), caps=True)
        s.tube([(c[0] - 0.04 * big, y - 0.03, c[2] + 0.012), (c[0] - 0.01, y, c[2] + 0.04 * big), (c[0] + 0.04 * big, y + 0.03, c[2] + 0.012)], [0.016, 0.018, 0.016], 5,
               CLOTH, rgba(hemp, 0.62), caps=True)
    # On the floor: a turn of it, and the end, frayed out to nothing.
    foot = pts[-1]
    turn = []
    for i in range(15):
        a = i / 14.0 * math.tau * 1.15
        r = 0.21 + 0.05 * math.sin(a * 2.0) - 0.03 * i / 14.0
        turn.append((foot[0] + 0.21 - math.cos(a) * r, floor + 0.026 + (0.03 if i == 0 else 0.0) + (0.03 if 11 <= i <= 12 else 0.0), foot[2] - 0.03 - math.sin(a) * r))
    s.tube([foot] + turn, [0.02] * (len(turn) + 1), 6, CLOTH, [rgba(hemp, 0.8 if i % 2 else 1.05) for i in range(len(turn) + 1)])
    end, before = turn[-1], turn[-2]
    dx, dz = end[0] - before[0], end[2] - before[2]
    d = math.hypot(dx, dz) or 1.0
    dx, dz = dx / d, dz / d
    for i in range(5):
        a = (i - 2) * 0.22 + random.uniform(-0.05, 0.05)
        length = random.uniform(0.09, 0.17)
        ex, ez = dx * math.cos(a) - dz * math.sin(a), dx * math.sin(a) + dz * math.cos(a)
        s.tube([end, (end[0] + ex * length * 0.5, floor + 0.016, end[2] + ez * length * 0.5), (end[0] + ex * length, floor + 0.01, end[2] + ez * length)],
               [0.008, 0.006, 0.002], 4, CLOTH, rgba(hemp, random.uniform(0.9, 1.3)))


# ---------------------------------------------------------------- carved saint

# The head, about the point it turns on (the scene's `Head`, 1.7 m up): heights from the neck's foot to the crown, and its girth at each.
HEAD_Y = [-0.17, -0.13, -0.105, -0.09, -0.075, -0.06, -0.052, -0.046, -0.04, -0.03, -0.015, 0.0, 0.012, 0.024, 0.036, 0.048, 0.062, 0.08, 0.1, 0.114, 0.121]
HEAD_R = [0.05, 0.045, 0.047, 0.057, 0.068, 0.076, 0.079, 0.081, 0.083, 0.086, 0.089, 0.091, 0.092, 0.092, 0.092, 0.091, 0.088, 0.079, 0.057, 0.03, 0.002]
SAINT = (0.56, 0.54, 0.5)


def carved_saint_head(p):
    """A saint's head in worn stone, its face nearly weathered away: a
    brow, two sockets, the line of a mouth. Round on a round neck, so it
    sits right however far it is turned."""
    s = p.soft
    nv = len(HEAD_Y) - 1

    def angle(u):
        t = u * 2.0 - 1.0
        return math.pi * math.copysign(abs(t) ** 1.45, t)

    def marks(a, y):
        b = abs(a)
        socket = math.exp(-(((b - 0.4) / 0.17) ** 2 + ((y - 0.02) / 0.017) ** 2))
        mouth = math.exp(-((y + 0.046) / 0.0045) ** 2) * smoothstep(0.4, 0.22, b)
        return socket, mouth

    def shape(u, v):
        j = int(round(v * nv))
        y, r = HEAD_Y[j], HEAD_R[j]
        a = angle(u)
        b = abs(a)
        socket, mouth = marks(a, y)
        face = smoothstep(1.5, 0.7, b)
        d = -0.017 * socket - 0.004 * mouth
        d += 0.008 * math.exp(-((y - 0.048) / 0.012) ** 2) * smoothstep(1.1, 0.5, b)                       # the brow
        d += 0.011 * math.exp(-(a / 0.11) ** 2) * smoothstep(0.05, 0.03, y) * smoothstep(-0.035, -0.012, y)  # what is left of the nose
        d += 0.006 * math.exp(-(a / 0.3) ** 2) * math.exp(-((y + 0.082) / 0.02) ** 2)                      # the chin
        d += 0.008 * math.exp(-((y - 0.066) / 0.018) ** 2) * (1.0 - 0.4 * face)                            # the ring of hair round the tonsure
        d += 0.006 * (1.0 - face) * smoothstep(-0.05, -0.02, y) * smoothstep(0.09, 0.06, y)                # and over the ears
        d -= 0.012 * face * smoothstep(-0.03, -0.09, y) * smoothstep(0.25, 0.9, b) * smoothstep(-0.11, -0.09, y)  # the jaw, narrower than the skull
        d += 0.0025 * fbm(a * 2.5, y * 28.0, 1.0, 2, 4.0)
        r += d
        return (math.sin(a) * r * 0.9, y, -math.cos(a) * r * (1.07 if math.cos(a) > 0.0 else 1.0))

    def colour(u, v):
        j = int(round(v * nv))
        y = HEAD_Y[j]
        a = angle(u)
        socket, mouth = marks(a, y)
        k = (0.92 + 0.14 * fbm(a * 2.0, y * 20.0, 1.0, 3, 7.0)) * lerp(0.8, 1.04, smoothstep(-0.12, 0.1, y))
        # Rain has run from the sockets down the cheeks.
        k *= 1.0 - 0.28 * math.exp(-((abs(a) - 0.4) / 0.1) ** 2) * smoothstep(0.02, 0.0, y) * smoothstep(-0.1, -0.03, y)
        k *= 1.0 - 0.3 * math.exp(-((y - 0.036) / 0.01) ** 2) * smoothstep(1.0, 0.5, abs(a))
        k *= max(1.0 - 0.8 * min(socket * 1.2, 1.0) - 0.75 * mouth, 0.1)
        return rgba(SAINT, k)

    props.sheet(s, shape, 24, nv, STONE, colour, flip=True)


def saint(p, kind):
    """A saint in a monk's habit, two thirds the height of a man, on a
    plinth; without its head (the scene sets carved_saint_head on it).
    `kind`: "pray", hands together; "book", a book held to the breast;
    "staff", a tau staff in one hand, the other on the breast."""
    m, s = p.hard, p.soft
    frustum(m, 0.25, 0.25, 0.0, 0.09, STONE, stone(0.55), top_colour=stone(0.7))
    frustum(m, 0.25, 0.205, 0.09, 0.14, STONE, stone(0.75))
    frustum(m, 0.205, 0.205, 0.14, 0.47, STONE, stone(0.7), top=False, top_colour=stone(0.86))
    frustum(m, 0.205, 0.245, 0.47, 0.53, STONE, stone(0.6), top=False)
    frustum(m, 0.245, 0.245, 0.53, 0.6, STONE, stone(0.92))
    rows = [(0.6, 0.19, 0.155, 0.12), (0.64, 0.182, 0.148, 0.115), (0.8, 0.166, 0.13, 0.105), (0.98, 0.155, 0.12, 0.1), (1.14, 0.15, 0.115, 0.1), (1.28, 0.16, 0.12, 0.105),
            (1.4, 0.176, 0.12, 0.11), (1.47, 0.18, 0.106, 0.1), (1.515, 0.142, 0.088, 0.086), (1.545, 0.088, 0.076, 0.07), (1.562, 0.07, 0.065, 0.062)]
    nv = len(rows) - 1
    seed = {"pray": 1.0, "book": 2.0, "staff": 3.0}[kind]

    def folds(a, y):
        depth = 0.075 * smoothstep(1.32, 0.62, y)
        return depth, math.cos(7.0 * a + 0.7 * math.sin(3.0 * a + seed) + seed * 2.0)

    def robe(u, v):
        y, rx, rf, rb = rows[int(round(v * nv))]
        a = (u - 0.5) * math.tau
        depth, wave = folds(a, y)
        k = 1.0 + depth * wave + 0.012 * fbm(a * 2.0, y * 3.0, 1.0, 2, seed)
        return (math.sin(a) * rx * k, y, -math.cos(a) * (rf if math.cos(a) > 0.0 else rb) * k)

    def worn(u, v):
        y = rows[int(round(v * nv))][0]
        a = (u - 0.5) * math.tau
        depth, wave = folds(a, y)
        k = (0.84 + 0.2 * fbm(a * 2.0, y * 3.0, 1.0, 3, seed + 5.0)) * lerp(0.7, 1.0, smoothstep(0.6, 1.05, y)) * (1.0 - 2.6 * depth * max(-wave, 0.0))
        return rgba(SAINT, k)

    props.sheet(s, robe, 24, nv, STONE, worn, flip=True)
    c, shade = rgba(SAINT, 0.95), rgba(SAINT, 0.72)
    # The cowl: its roll round the neck (the head turns in it), its hood down the back.
    props.ring(s, (0.0, 1.556, 0.0), (0, 1, 0), r=0.074, thick=0.026, colour=c, mat=STONE, sides=10)
    s.tube([(0.0, 1.56, 0.075), (0.0, 1.46, 0.105), (0.0, 1.33, 0.11), (0.0, 1.24, 0.1)], [0.05, 0.085, 0.06, 0.012], 7, STONE, [c, c, shade, shade], caps=True, squash=(1.0, 0.5))
    # Toes under the hem.
    for sx in (-1, 1):
        s.tube([(sx * 0.062, 0.615, -0.12), (sx * 0.066, 0.61, -0.175), (sx * 0.068, 0.605, -0.2)], [0.03, 0.03, 0.014], 5, STONE, shade, caps=True, squash=(1.0, 0.6))

    def sleeve(sx, pts, radii, hang=True):
        s.tube([(sx * x, y, z) for x, y, z in pts], radii, 8, STONE, [c] + [rgba(SAINT, 0.86)] * (len(pts) - 1), caps=True)
        if hang:
            # The sleeve's mouth, hanging wide from the wrist.
            x, y, z = pts[-2]
            s.tube([(sx * x, y, z), (sx * (x - 0.004), y - 0.07, z + 0.006), (sx * (x - 0.008), y - 0.13, z + 0.012), (sx * (x - 0.01), y - 0.15, z + 0.014)],
                   [radii[-2] * 0.9, radii[-2] * 0.95, radii[-2] * 0.8, radii[-2] * 0.45], 8, STONE, [rgba(SAINT, 0.86), shade, shade, shade], caps=True, squash=(1.0, 0.5))

    if kind == "pray":
        for sx in (-1, 1):
            sleeve(sx, [(0.135, 1.475, 0.0), (0.192, 1.3, -0.02), (0.168, 1.2, -0.075), (0.075, 1.27, -0.145), (0.022, 1.325, -0.16)], [0.046, 0.058, 0.06, 0.05, 0.034])
        s.tube([(0.0, 1.31, -0.165), (0.0, 1.38, -0.176), (0.0, 1.43, -0.181), (0.0, 1.45, -0.182)], [0.03, 0.03, 0.022, 0.008], 6, STONE, c, caps=True, squash=(0.55, 1.0))
    elif kind == "book":
        for sx in (-1, 1):
            sleeve(sx, [(0.135, 1.475, 0.0), (0.192, 1.29, -0.02), (0.165, 1.17, -0.08), (0.1, 1.185, -0.15), (0.075, 1.2, -0.165)], [0.046, 0.058, 0.06, 0.05, 0.036])
            s.tube([(sx * 0.085, 1.18, -0.175), (sx * 0.07, 1.22, -0.2), (sx * 0.05, 1.235, -0.203)], [0.026, 0.024, 0.012], 5, STONE, c, caps=True)
        b = props.Placed(m, (0.0, 1.27, -0.16), 0.0, 1.0, math.radians(-12.0))
        b.box((-0.085, -0.1, -0.03), (0.085, 0.11, 0.03), STONE, rgba(SAINT, 0.9))
        b.box((-0.075, -0.09, -0.036), (0.075, 0.1, -0.03), STONE, rgba(SAINT, 0.7), faces="xXyYz")
    else:
        sleeve(1, [(0.135, 1.475, 0.0), (0.2, 1.3, -0.03), (0.215, 1.19, -0.09), (0.23, 1.23, -0.125)], [0.046, 0.058, 0.058, 0.038])
        sleeve(-1, [(0.135, 1.475, 0.0), (0.192, 1.3, -0.02), (0.16, 1.2, -0.08), (0.06, 1.29, -0.135), (0.02, 1.32, -0.14)], [0.046, 0.058, 0.06, 0.05, 0.036])
        s.tube([(-0.03, 1.31, -0.148), (0.03, 1.34, -0.15), (0.06, 1.35, -0.14)], [0.03, 0.028, 0.012], 5, STONE, c, caps=True, squash=(1.0, 0.5))
        s.tube([(0.236, 0.6, -0.125), (0.236, 1.2, -0.127), (0.236, 1.76, -0.125)], [0.018, 0.017, 0.016], 6, STONE, [shade, c, c], caps=True)
        s.tube([(0.17, 1.765, -0.125), (0.236, 1.775, -0.125), (0.302, 1.765, -0.125)], [0.014, 0.019, 0.014], 6, STONE, c, caps=True)
        s.tube([(0.236, 1.2, -0.125), (0.236, 1.26, -0.125)], [0.036, 0.036], 6, STONE, c, caps=True)


def carved_saint(p):
    saint(p, "pray")


def carved_saint_b(p):
    saint(p, "book")


def carved_saint_c(p):
    saint(p, "staff")


# ------------------------------------------------------------------ crypt rail

def crypt_rail(p):
    """The rail round the crypt stair's well, in the church scene's own
    space (game/world/abbey/areas/church.tscn: CryptRailS and CryptRailE
    are its collision): oak posts, a hand rail worn pale, square balusters
    set cornerwise; one gone, one newer than the rest."""
    m = p.hard
    y0, z, xe = 0.05, -34.1, 24.1
    posts = [(18.06, z), (19.27, z), (20.48, z), (21.69, z), (22.9, z), (xe, z), (xe, -34.77), (xe, -35.43)]
    for x, zz in posts:
        lean = random.uniform(-0.006, 0.006)
        beam(m, (x, y0, zz), (x + lean, y0 + 0.97, zz), 0.1, 0.1, tone(OAK_DARK), ends="")
        beam(m, (x + lean, y0 + 0.97, zz), (x + lean, y0 + 1.03, zz), 0.1, 0.1, tone(OAK_DARK), ends="b", taper=0.45)
    count = 0
    for (xa, za), (xb, zb) in zip(posts, posts[1:]):
        along = (1.0, 0.0) if abs(xb - xa) > abs(zb - za) else (0.0, -1.0)
        a = (xa + along[0] * 0.05, za + along[1] * 0.05)
        b = (xb - along[0] * 0.05, zb - along[1] * 0.05)
        length = math.hypot(b[0] - a[0], b[1] - a[1])
        sag = random.uniform(-0.004, 0.004)
        beam(m, (a[0], y0 + 0.868, a[1]), (b[0], y0 + 0.868 + sag, b[1]), 0.085, 0.062, tone(OAK, 0.08), ends="")
        beam(m, (a[0], y0 + 0.16, a[1]), (b[0], y0 + 0.16, b[1]), 0.06, 0.06, tone(OAK_DARK), ends="")
        n = max(int(round(length / 0.15)) - 1, 1)
        for i in range(n):
            count += 1
            if count == 17:
                continue
            t = (i + 1.0) / (n + 1.0)
            x, zz = lerp(a[0], b[0], t), lerp(a[1], b[1], t)
            colour = tone(props.PINE, 0.05) if count == 29 else tone(OAK_DARK, 0.2)
            beam(m, (x, y0 + 0.19, zz), (x + random.uniform(-0.004, 0.004), y0 + 0.838, zz), 0.036, 0.036, colour, ends="", roll=math.pi * 0.25)


# ------------------------------------------------------- abbot's seat, lectern

SEAT_ARM = [(-0.17, 0.14), (0.4, 0.14), (0.4, 1.12), (0.3, 1.1), (0.16, 0.97), (0.02, 0.91), (-0.1, 0.93), (-0.19, 0.89), (-0.2, 0.81), (-0.17, 0.72)]


def abbot_seat(p):
    """The abbot's seat in the chapter house: a high-backed oak chair on a
    step, its back (+Z) to the wall. 0.94 m wide, 0.9 m deep with the
    step, 1.8 m to its gable (it stands under the chapter house's painted panel)."""
    m, s = p.hard, p.soft
    w = 0.47
    # The step.
    boards(m, (-w, 0.1, -0.45), (w, 0.14, 0.45), "x", "z", 4, OAK, uneven=0.002, ragged=0.004)
    for z in (-0.44, 0.44):
        plank(m, (-w + 0.01, 0.0, z - 0.012), (w - 0.01, 0.1, z + 0.012), tone(OAK_DARK), along="x")
    for x in (-w + 0.012, w - 0.012):
        plank(m, (x - 0.012, 0.0, -0.43), (x + 0.012, 0.1, 0.43), tone(OAK_DARK), along="z")
    # The seat: a boarded box between two shaped arms, the board worn pale, a flat cushion left on it.
    for sx in (-1, 1):
        props.slab(m, SEAT_ARM, "x", sx * w - (0.06 if sx > 0 else 0.0), sx * w + (0.06 if sx < 0 else 0.0), tone(OAK_DARK, 0.06))
        beam(m, (sx * (w - 0.03), 0.925, -0.2), (sx * (w - 0.03), 0.925, 0.12), 0.08, 0.03, tone(OAK, 0.06), ends="a")
    at = (lambda u, y, q: (u, y, -0.15 - q))
    for u0, u1 in ((-0.39, -0.02), (0.02, 0.39)):
        blind_arch(m, at, (0, 0, -1), u0, u1, 0.2, 0.36, 0.2, 0.585, tone(OAK_DARK, 0.08), back=rgba(OAK_DARK, 0.42), deep=0.02, n=3, sides=False)
    for u0, u1 in ((-0.41, -0.39), (-0.02, 0.02), (0.39, 0.41)):
        face(m, [at(u0, 0.14, 0.0), at(u1, 0.14, 0.0), at(u1, 0.585, 0.0), at(u0, 0.585, 0.0)], (0, 0, -1), tone(OAK_DARK, 0.08))
    face(m, [at(-0.41, 0.14, 0.0), at(0.41, 0.14, 0.0), at(0.41, 0.2, 0.0), at(-0.41, 0.2, 0.0)], (0, 0, -1), tone(OAK_DARK, 0.08), grain="x")
    boards(m, (-0.41, 0.585, -0.18), (0.41, 0.62, 0.4), "x", "z", 2, OAK, uneven=0.002)
    props.tick(s, -0.3, 0.3, -0.13, 0.33, 0.618, 0.05, colour=(0.026, 0.014, 0.011), lumps=0.2, seed=41.0, edge=0.22, hollow=(0.5, 0.45, 0.022))
    # The back: two posts with finials, a panel with a blind arch in it, a gable over.
    for sx in (-1, 1):
        beam(m, (sx * 0.425, 0.14, 0.41), (sx * 0.425, 1.52, 0.41), 0.09, 0.08, tone(OAK_DARK), ends="")
        fin = [(sx * 0.425 + a * 0.13, 1.52 + b * 0.2) for a, b in ((0.3, 0.0), (0.2, 0.13), (0.5, 0.3), (0.56, 0.5), (0.3, 0.6), (0.34, 0.78), (0.13, 0.9), (0.0, 1.0),
                                                             (-0.13, 0.9), (-0.34, 0.78), (-0.3, 0.6), (-0.56, 0.5), (-0.5, 0.3), (-0.2, 0.13), (-0.3, 0.0))]
        props.slab(m, fin, "z", 0.375, 0.445, tone(OAK_DARK, 0.06))
    face_boards(m, (-0.38, 0.4), (0.38, 0.4), 0.62, 0.95, (0, 0, -1), 4, OAK_DARK)
    face(m, [(-0.47, 0.14, 0.45), (0.47, 0.14, 0.45), (0.47, 1.52, 0.45), (-0.47, 1.52, 0.45)], (0, 0, 1), rgba(OAK_DARK, 0.6))
    back = (lambda u, y, q: (u, y, 0.385 - q))
    blind_arch(m, back, (0, 0, -1), -0.38, 0.38, 0.95, 1.02, 0.42, 1.46, tone(OAK_DARK, 0.08), back=rgba(OAK_DARK, 0.42), deep=0.02, n=5, sides=False)
    beam(m, (-0.38, 0.95, 0.39), (0.38, 0.95, 0.39), 0.03, 0.05, tone(OAK_DARK), ends="")
    gable = [(-0.4, 1.44), (0.4, 1.44), (0.4, 1.5), (0.05, 1.72), (0.035, 1.78), (0.0, 1.8), (-0.035, 1.78), (-0.05, 1.72), (-0.4, 1.5)]
    props.slab(m, gable, "z", 0.36, 0.44, tone(OAK_DARK, 0.06), grain="p")
    # A cross cut in the gable.
    for lo, hi in (((-0.011, 1.52, 0.356), (0.011, 1.65, 0.36)), ((-0.045, 1.595, 0.356), (0.045, 1.615, 0.36))):
        m.box(lo, hi, WOOD, rgba(OAK_DARK, 0.35), faces="z")


def lectern(p):
    """The reader's desk in the refectory: an oak lectern 0.6 m square and
    1.3 m high, the reader standing at -Z; the book left open on it."""
    m, s = p.hard, p.soft
    h = 0.27
    plank(m, (-0.3, 0.0, -0.3), (0.3, 0.07, 0.3), tone(OAK_DARK), along="x")
    for sx in (-1, 1):
        for sz in (-1, 1):
            beam(m, (sx * h, 0.07, sz * h), (sx * h, 1.0, sz * h), 0.06, 0.06, tone(OAK_DARK), ends="")
    # Panelled toward the hall (+Z) and at the sides; open to the reader, with a shelf.
    for at, out in (((lambda u, y, q: (-u, y, h + 0.012 + q)), (0, 0, 1)), ((lambda u, y, q: (h + 0.012 + q, y, u)), (1, 0, 0)), ((lambda u, y, q: (-h - 0.012 - q, y, -u)), (-1, 0, 0))):
        for u0, u1 in ((-0.24, -0.005), (0.005, 0.24)):
            blind_arch(m, at, out, u0, u1, 0.14, 0.62, 0.18, 0.93, tone(OAK_DARK, 0.08), back=rgba(OAK_DARK, 0.42), deep=0.022, n=3, sides=False)
        for y0, y1 in ((0.07, 0.14), (0.93, 1.0)):
            face(m, [at(-0.24, y0, 0.0), at(0.24, y0, 0.0), at(0.24, y1, 0.0), at(-0.24, y1, 0.0)], out, tone(OAK_DARK, 0.08), grain="x" if out[0] == 0 else "z")
    face(m, [(-0.24, 0.07, h - 0.012), (0.24, 0.07, h - 0.012), (0.24, 1.0, h - 0.012), (-0.24, 1.0, h - 0.012)], (0, 0, -1), rgba(OAK_DARK, 0.5))
    for sx in (-1, 1):
        face(m, [(sx * (h - 0.012), 0.07, -0.24), (sx * (h - 0.012), 0.07, 0.24), (sx * (h - 0.012), 1.0, 0.24), (sx * (h - 0.012), 1.0, -0.24)], (-sx, 0, 0), rgba(OAK_DARK, 0.5))
    plank(m, (-0.24, 0.5, -0.26), (0.24, 0.525, 0.26), tone(OAK_DARK), along="x")
    plank(m, (-0.24, 0.07, -0.26), (0.24, 0.09, 0.26), tone(OAK_DARK, 0.05), along="x")
    beam(m, (-0.24, 0.965, -h), (0.24, 0.965, -h), 0.04, 0.07, tone(OAK_DARK), ends="")
    # The desk: its cheeks, the sloping board, the ledge.
    slope = 0.26 / 0.6

    def top(z):
        return 1.03 + (z + 0.3) * slope

    for sx in (-1, 1):
        props.slab(m, [(-0.3, 0.98), (0.3, 0.98), (0.3, top(0.3) - 0.01), (-0.3, 1.02)], "x", sx * 0.3 - (0.03 if sx > 0 else 0.0), sx * 0.3 + (0.03 if sx < 0 else 0.0),
                   tone(OAK_DARK), grain="p")
    plank(m, (-0.27, 0.98, 0.275), (0.27, top(0.3) - 0.02, 0.3), tone(OAK_DARK), along="x")
    plank(m, (-0.3, 0.975, -0.3), (0.3, 1.0, 0.3), tone(OAK_DARK), along="x")
    n = (0.0, 1.0, -slope)
    beam(m, (-0.31, top(0.0) - 0.014, 0.0), (0.31, top(0.0) - 0.014, 0.0), 0.66, 0.028, tone(OAK, 0.06), up=n)
    beam(m, (-0.31, top(-0.3) + 0.012, -0.302), (0.31, top(-0.3) + 0.012, -0.302), 0.022, 0.045, tone(OAK_DARK), ends="")
    tilt = -math.atan(slope)
    open_book(m, (0.02, top(-0.1) + 0.002, -0.1), 0.05, tilt, w=0.46, d=0.32)
    # The marker hanging from it; a pricket on the cheek, its candle burnt to a stub.
    m.poly([(0.05, top(-0.26) + 0.03, -0.262), (0.066, top(-0.26) + 0.03, -0.262), (0.068, top(-0.3) - 0.1, -0.318), (0.052, top(-0.3) - 0.1, -0.318)], PAINT,
           (0.04, 0.012, 0.009, 1.0), facing=(0, 0.3, -1))
    beam(m, (0.3, 1.16, 0.12), (0.37, 1.16, 0.12), 0.012, 0.012, IRON_C, IRON, end_shade=1.0)
    s.tube([(0.37, 1.15, 0.12), (0.37, 1.165, 0.12)], [0.03, 0.036], 6, IRON, IRON_C, caps=True)
    props.candle(s, (0.37, 1.165, 0.12), h=0.04, r=0.013, drips=2)


BUILDERS = {
    "choir_stalls": choir_stalls, "choir_stalls_b": choir_stalls_b, "choir_stalls_c": choir_stalls_c,
    "altar": altar, "tomb_open": tomb_open, "reliquary": reliquary, "bell": bell, "bell_rope": bell_rope,
    "carved_saint": carved_saint, "carved_saint_b": carved_saint_b, "carved_saint_c": carved_saint_c, "carved_saint_head": carved_saint_head,
    "crypt_rail": crypt_rail, "abbot_seat": abbot_seat, "lectern": lectern,
}

if __name__ == "__main__":
    props.run(BUILDERS)
