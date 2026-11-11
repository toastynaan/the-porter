"""The abbey church (every night): the nave and choir under one tall rib
vault, its windows, its roof, and the bell tower at its west end. The model
is in the abbey's own coordinates and is laid over the greybox (game/world/
abbey/areas/church.tscn), which still stops people and shapes the navmesh
but is no longer drawn. The plan is the greybox's: one vessel 48 m by 7.2 m
inside (x = -20 to 28, z = -36 to -28), twelve bays of 4 m; the tower on the
8 m square west of it. What changes is the height: the vault springs at
11.2 m and its crown is at 16 m (the greybox's ceiling was at 8).

`env_church`:
- Walls: both faces of every wall. Inside, a blind arcade along the foot, a
  string course under the windows, and a tall two-light window in every
  bay (short ones high up where the east range stands against the south
  wall). Outside, buttresses between the bays, hood moulds, a parapet.
- Windows: their tracery, leaded glass and saddle bars; the great east
  window of four lights; the belfry's louvres.
- Vault: a rib vault over each bay, on triple shafts from the floor.
- Floor: worn flags down the nave, two-coloured tiles in the choir.
- Roof: lead, steep, behind the parapet; the east gable and its cross.
- Tower: its walls inside (to the bell floor at 12 m) and out (to 30 m),
  the belfry stage, battlements and a short lead spire.
- Fittings: the rood beam and its cross, and three iron coronas hung from
  the vault, their candles unlit.

Run: tools/build.sh env_church
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
import city_parts as cp
import env_cloister as cl
from porter import fbm, lerp, smoothstep

STONE = "stone_church"
OUTER = "stone_cloister"
GLASS = "glass_church"
IRON = "iron_cart"
OAK = "wood_medieval"
# A wall's faces stand this far from its middle (2 cm proud of the greybox).
F = 0.42
# The vault; the walls' tops inside (hidden over the vault) and outside (the
# parapet); the roof's eaves and ridge; the tower's top.
VSPRING, VRISE = 11.2, 4.8
IN_TOP, OUT_TOP = 16.2, 17.2
EAVE, RIDGE = 16.6, 21.8
TOWER_IN, TOWER_TOP = 11.9, 30.0
# Windows: (sill, springing, half width, rise).
TALL = (5.6, 11.4, 1.05, 2.0)
SHORT = (9.4, 11.4, 1.05, 2.0)
EAST = (4.6, 10.2, 2.3, 3.4)
BELFRY = (23.2, 26.2, 1.0, 1.5)
DOOR = (0.47, 0.0, 2.03)

# Each wall's own space: u along it, v through it (the faces at v = F and
# -F). Each is a turn, so faces keep their handedness.
NORTH = lambda u, y, v: (u, y, -36.0 + v)          # v > 0: inside
SOUTH = lambda u, y, v: (-u, y, -28.0 - v)         # v > 0: inside
EAST_W = lambda u, y, v: (28.0 - v, y, -32.0 + u)  # v > 0: inside
WEST_W = lambda u, y, v: (-20.0 + v, y, -32.0 - u) # v > 0: the nave, v < 0: the tower
TOWER_W = lambda u, y, v: (-28.0 + v, y, -32.0 - u) # v > 0: inside the tower

pale = cl.pale


def crown(tt):
    return VSPRING + cp.arch_height(1.0, 0.0, VRISE, min(abs(tt), 0.99999))


def vault_bay(t, ua, ub, va, vb, wall_ribs):
    """A rib vault over ua..ub by va..vb (as the cloister's, at the church's height)."""
    cu, hu, cv, hv = (ua + ub) * 0.5, (ub - ua) * 0.5, (va + vb) * 0.5, (vb - va) * 0.5
    n = 10
    ts = [-1.0 + i / n for i in range(2 * n + 1)]

    def shade(p):
        k = lerp(1.0, 0.62, smoothstep(VSPRING, VSPRING + VRISE, p[1])) * (0.92 + 0.1 * fbm(p[0], p[2], 0.4, 2, 4.0))
        return (k, k * 0.99, k * 0.96, 1.0)

    def web(pts):
        out = [pts[0]]
        for p in pts[1:]:
            if math.dist(p, out[-1]) > 1e-6:
                out.append(p)
        if len(out) > 2 and math.dist(out[0], out[-1]) < 1e-6:
            out.pop()
        if len(out) >= 3:
            t.poly(out, STONE, [shade(p) for p in out], facing=(0, -1, 0))

    for ta, tb in zip(ts, ts[1:]):
        for s in (-1, 1):
            web([(cu + s * hu * abs(ta), crown(ta), cv + hv * ta), (cu + s * hu, crown(ta), cv + hv * ta),
                 (cu + s * hu, crown(tb), cv + hv * tb), (cu + s * hu * abs(tb), crown(tb), cv + hv * tb)])
            web([(cu + hu * ta, crown(ta), cv + s * hv * abs(ta)), (cu + hu * ta, crown(ta), cv + s * hv),
                 (cu + hu * tb, crown(tb), cv + s * hv), (cu + hu * tb, crown(tb), cv + s * hv * abs(tb))])
    c = pale(0.7)
    for s in (-1, 1):
        cl.rib(t, [(cu + hu * tt, crown(tt), cv + s * hv * tt) for tt in ts], 0.18, 0.2, c)
    for name, fixed, lo in (("u0", ua, True), ("u1", ub, True), ("v0", va, False), ("v1", vb, False)):
        if name not in wall_ribs:
            continue
        inset = 0.05 if name.endswith("0") else -0.05
        if lo:
            cl.rib(t, [(fixed + inset, crown(tt), cv + hv * tt) for tt in ts], 0.1, 0.12, c)
        else:
            cl.rib(t, [(cu + hu * tt, crown(tt), fixed + inset) for tt in ts], 0.1, 0.12, c)
    top = crown(0.0)
    t.tube([(cu, top - 0.42, cv), (cu, top - 0.34, cv), (cu, top - 0.16, cv), (cu, top, cv)], [0.08, 0.26, 0.3, 0.3], 8, STONE, pale(0.6), caps=True)


def shafts(t, u, s, top=VSPRING):
    """Three shafts against the wall for the vault to spring from: bases,
    two rings and a cap."""
    c = pale(0.8)
    for du, dv, r in ((0.0, 0.14, 0.12), (-0.17, 0.05, 0.075), (0.17, 0.05, 0.075)):
        v = s * (F + dv)
        t.tube([(u + du, 0.0, v), (u + du, 0.3, v), (u + du, 0.42, v), (u + du, top - 0.5, v)], [r * 1.5, r * 1.5, r, r], 8, STONE, c, caps=True)
    v = s * (F + 0.1)
    for y in (5.5, 8.4):
        t.tube([(u, y - 0.07, v), (u, y, v), (u, y + 0.07, v)], [0.19, 0.25, 0.19], 8, STONE, c, squash=(1.5, 1.0))
    t.tube([(u, top - 0.5, v), (u, top - 0.42, v), (u, top - 0.12, v), (u, top - 0.08, v), (u, top, v)], [0.17, 0.2, 0.3, 0.34, 0.34], 8, STONE,
           pale(0.84), caps=True, squash=(1.35, 1.0))


def face(t, s, ua, ub, ya, yb, tint, cuts=()):
    """A wall's face at v = s * F from ua to ub, left open at `cuts`
    (centre, half width, foot, head), each with its reveal back to the
    wall's middle and a plain surround."""
    v, out = s * F, (0, 0, s)
    u = ua
    for uc, hw, y0, y1 in sorted(cuts):
        y0c, y1c = max(y0, ya), min(y1, yb)
        cp.panel(t, (u, v), (uc - hw, v), ya, yb, out, getattr(tint, "mat", STONE), tint, 1.6, 1.2)
        cp.panel(t, (uc - hw, v), (uc + hw, v), ya, y0c, out, getattr(tint, "mat", STONE), tint, 1.6, 1.2)
        cp.panel(t, (uc - hw, v), (uc + hw, v), y1c, yb, out, getattr(tint, "mat", STONE), tint, 1.6, 1.2)
        u = uc + hw
        c = pale(0.6)
        for a, b, n in ((uc - hw, uc - hw, (1, 0, 0)), (uc + hw, uc + hw, (-1, 0, 0))):
            t.poly([(a, y0c, 0.0), (a, y1c, 0.0), (a, y1c, v), (a, y0c, v)], STONE, c, facing=n)
        t.poly([(uc - hw, y1c, 0.0), (uc + hw, y1c, 0.0), (uc + hw, y1c, v), (uc - hw, y1c, v)], STONE, c, facing=(0, -1, 0))
        if y0c > ya:
            t.poly([(uc - hw, y0c, 0.0), (uc + hw, y0c, 0.0), (uc + hw, y0c, v), (uc - hw, y0c, v)], STONE, pale(0.8), facing=(0, 1, 0))
        # The surround.
        c = pale(0.86)
        fw = 0.14 if y1 - y0 > 1.6 else 0.09
        fz = sorted((v, v + s * 0.07))
        zf = "Z" if s > 0 else "z"
        for k in (-1, 1):
            a, b = sorted((uc + k * hw, uc + k * (hw + fw)))
            t.box((a, y0c, fz[0]), (b, y1c, fz[1]), STONE, c, faces="xX" + zf)
        t.box((uc - hw - fw, y1c, fz[0]), (uc + hw + fw, y1c + fw, fz[1]), STONE, c, faces="xXyY" + zf)
        if y1 - y0 > 1.6:
            cp.arch_band(t, v, hw + fw, y1c + fw, 0.62, 0.12, 0.07, out, STONE, c, cx=uc, n=6)
            head = [(x, y, v + s * 0.012) for x, y in cp.arch_profile(hw + fw, y1c + fw, 0.62, 6, uc)]
            t.poly(head, STONE, pale(0.5), facing=out)
    cp.panel(t, (u, v), (ub, v), ya, yb, out, getattr(tint, "mat", STONE), tint, 1.6, 1.2)


def window_face(t, s, ua, ub, ya, yb, win, uc, tint, cuts=(), hood=False):
    """A face with a pointed window through it: the wall round it, the
    reveal back to the glass, the sill."""
    sill, spring, half, rise = win
    v, out = s * F, (0, 0, s)
    drop = 0.45 if s > 0 else 0.25
    if ya < sill - drop:
        face(t, s, ua, ub, ya, sill - drop, tint, cuts)
        for a, b in ((ua, uc - half), (uc + half, ub)):
            cp.panel(t, (a, v), (b, v), sill - drop, sill, out, getattr(tint, "mat", STONE), tint, 1.6, 1.2)
    cp.arch_wall(t, v, ua, ub, max(sill, ya), yb, half, spring, rise, out, getattr(tint, "mat", STONE), tint, cx=uc)
    k = 0.78 if s > 0 else 0.6
    jamb = lambda x, y, z: cp.rgba(cl.PALE, k)
    cp.vault(t, s * 0.06, v, half, spring, rise, STONE, jamb, cx=uc, y0=sill, step=0.5)
    # The sill, sloped to shed water outside and to throw light down inside.
    if ya < sill - drop:
        t.poly([(uc - half, sill, s * 0.06), (uc + half, sill, s * 0.06), (uc + half, sill - drop, v), (uc - half, sill - drop, v)], STONE,
               pale(0.9 if s > 0 else 0.66), facing=(0, 1, s))
        for e in (-1, 1):
            t.poly([(uc + e * half, sill, s * 0.06), (uc + e * half, sill, v), (uc + e * half, sill - drop, v)], STONE, pale(k), facing=(-e, 0, 0))
    else:
        t.poly([(uc - half, sill, 0.0), (uc + half, sill, 0.0), (uc + half, sill, v), (uc - half, sill, v)], STONE, pale(0.8), facing=(0, 1, 0))
    if hood:
        cp.arch_band(t, v, half + 0.02, spring, rise, 0.14, 0.08, out, STONE, pale(0.7), cx=uc)
        for k in (-1, 1):
            a, b = sorted((uc + k * (half + 0.02), uc + k * (half + 0.3)))
            lo, hi = sorted((v, v + s * 0.1))
            t.box((a, spring - 0.14, lo), (b, spring, hi), STONE, pale(0.7))


def lights(t, cx, sill, spring, half, w, level, c, v0=-0.07, v1=0.07):
    """Tracery in an arch `half` wide: a mullion, two arched lights and an
    eye over them. `level` 2 puts the same again inside each light."""
    h2 = half * 0.5
    t.box((cx - w * 0.5, sill, v0), (cx + w * 0.5, spring, v1), STONE, c, faces="xXzZ")
    r2 = h2 * 1.25
    for s in (-1, 1):
        c2 = cx + s * h2
        prof = cp.arch_profile(h2 - w * 0.4, spring, r2, 6, c2)
        cl.bar(t, prof, w, v0, v1, c)
        if level > 1:
            lights(t, c2, sill, spring - h2 * 0.7, h2 - w * 0.4, w * 0.8, level - 1, c, v0 + 0.015, v1 - 0.015)
            continue
        heart = (c2, spring + r2 * 0.3)
        for i in (3, 9):
            p = prof[i]
            d = math.hypot(heart[0] - p[0], heart[1] - p[1])
            reach = h2 * 0.3
            tip = (p[0] + (heart[0] - p[0]) / d * reach, p[1] + (heart[1] - p[1]) / d * reach)
            mid = lambda a, b: ((a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5)
            cl.cusp(t, mid(prof[i - 1], p), mid(prof[i + 1], p), tip, v0 + 0.02, v1 - 0.02, c)
    r, yc = half * 0.36, spring + half * 0.62
    ring = [(cx + math.cos(math.tau * i / 16) * r, yc + math.sin(math.tau * i / 16) * r) for i in range(16)]
    cl.bar(t, ring, w, v0, v1, c, closed=True)
    foils = 4 if level == 1 else 6
    for k in range(foils):
        a = math.tau * (k + 0.5) / foils
        da = 0.8 / foils
        rr = r - w * 0.4
        cl.cusp(t, (cx + math.cos(a - da) * rr, yc + math.sin(a - da) * rr), (cx + math.cos(a + da) * rr, yc + math.sin(a + da) * rr),
                (cx + math.cos(a) * r * 0.5, yc + math.sin(a) * r * 0.5), v0 + 0.02, v1 - 0.02, c)


def half_at(win, y):
    """Half the window's width at height y."""
    sill, spring, half, rise = win
    if y <= spring:
        return half
    lo, hi = 0.0, half
    for _ in range(24):
        mid = (lo + hi) * 0.5
        if cp.arch_height(half, spring, rise, mid) > y:
            lo = mid
        else:
            hi = mid
    return lo


def glazing(t, uc, win, level=1, louvres=0):
    """What fills a window: tracery, the glass and its iron bars; or, with
    `louvres` (the side they face, 1 or -1), a belfry's boards."""
    sill, spring, half, rise = win
    c = pale(0.74)
    w = 0.1 if level == 1 else 0.13
    lights(t, uc, sill, spring, half, w, level, c)
    shape = [(uc + half, sill)] + cp.arch_profile(half, spring, rise, 8, uc) + [(uc - half, sill)]
    if louvres:
        for k in (-1, 1):
            t.poly([(x, y, 0.0) for x, y in shape], "window_dark", (0, 0, 0, 1), facing=(0, 0, k))
        y = sill + 0.3
        while y < spring + rise - 0.3:
            hw = half_at(win, y)
            pts = [(uc - hw, y, louvres * 0.08), (uc + hw, y, louvres * 0.08), (uc + hw, y - 0.24, louvres * 0.3), (uc - hw, y - 0.24, louvres * 0.3)]
            t.poly(pts, OAK, (0.3, 0.28, 0.26, 1.0), facing=(0, 1, louvres))
            t.poly(pts, OAK, (0.12, 0.11, 0.1, 1.0), facing=(0, -1, -louvres))
            y += 0.32
        return
    top = spring + rise
    for k in (-1, 1):
        cols = []
        for x, y in shape:
            g = lerp(0.5, 1.0, smoothstep(sill, top, y)) * (0.85 + 0.25 * fbm(x * 3.0, y * 3.0, 1.0, 2, 3.0))
            cols.append((g, g, g, 1.0))
        t.poly([(x, y, k * 0.012) for x, y in shape], GLASS, cols, facing=(0, 0, k))
    y = sill + 0.7
    while y < top - 0.3:
        hw = half_at(win, y)
        t.box((uc - hw, y, -0.035), (uc + hw, y + 0.035, 0.035), IRON, (0.12, 0.12, 0.13, 1.0), faces="zZyY")
        y += 0.78


def buttress(t, u, s, y0, stages, tint, width=0.7):
    """A buttress against the face at v = s * F: `stages` are (top, depth)
    going up, each with a sloped set-off."""
    zf = "Z" if s > 0 else "z"
    h = width * 0.5
    foot = y0
    for i, (top, depth) in enumerate(stages):
        lo, hi = sorted((s * F, s * (F + depth)))
        cp.slab(t, (u - h, foot, lo), (u + h, top, hi), getattr(tint, "mat", OUTER), tint, faces="xX" + zf, step=1.2)
        back = stages[i + 1][1] if i + 1 < len(stages) else 0.0
        rise = (depth - back) * 0.9
        t.poly([(u - h, top, s * (F + depth)), (u + h, top, s * (F + depth)), (u + h, top + rise, s * (F + back)), (u - h, top + rise, s * (F + back))],
               STONE, pale(0.74), facing=(0, 1, s))
        for k in (-1, 1):
            t.poly([(u + k * h, top, s * (F + depth)), (u + k * h, top + rise, s * (F + back)), (u + k * h, top, s * (F + back))], STONE, pale(0.6),
                   facing=(k, 0, 0))
        foot = top
    if y0 <= 0.01:
        d = stages[0][1]
        lo, hi = sorted((s * F, s * (F + d + 0.08)))
        t.box((u - h - 0.07, 0.0, lo), (u + h + 0.07, 0.45, hi), STONE, cp.rgba(cp.STONE_DAMP, 1.5), faces="xXY" + zf)


def course(t, s, ua, ub, y, proud=0.07, tall=0.14, k=0.78):
    """A string course along a face."""
    lo, hi = sorted((s * F, s * (F + proud)))
    t.box((ua, y, lo), (ub, y + tall, hi), STONE, pale(k), faces="xXyY" + ("Z" if s > 0 else "z"))


def blind_arcade(t, s, uc):
    """Two shallow arches on the wall's foot."""
    for k in (-1, 1):
        cp.arch_band(t, s * F, 0.72, 2.3, 0.95, 0.1, 0.06, (0, 0, s), STONE, pale(0.84), cx=uc + k * 0.92, y0=0.5)
    lo, hi = sorted((s * F, s * (F + 0.09)))
    t.box((uc - 1.84, 0.0, lo), (uc + 1.84, 0.5, hi), STONE, pale(0.7), faces="xXY" + ("Z" if s > 0 else "z"))


def parapet(m, a, b, out, y0, y1, tint, thick=0.4):
    """The back and the coping of a parapet whose outer face is already made."""
    ox, oz = out
    ia, ib = (a[0] - ox * thick, a[1] - oz * thick), (b[0] - ox * thick, b[1] - oz * thick)
    cp.panel(m, ia, ib, y0, y1, (-ox, 0, -oz), getattr(tint, "mat", STONE), tint, 3.0, 1.5)
    m.poly([(a[0], y1, a[1]), (b[0], y1, b[1]), (ib[0], y1, ib[1]), (ia[0], y1, ia[1])], STONE, pale(0.72), facing=(0, 1, 0))


def corona(m, x, z, y, r):
    """A ring of iron hung on chains, a candle on every spike."""
    c = (0.1, 0.1, 0.11, 1.0)
    ring = [(x + math.cos(math.tau * i / 16) * r, y, z + math.sin(math.tau * i / 16) * r) for i in range(17)]
    m.tube(ring, [0.03] * 17, 5, IRON, c, squash=(1.0, 2.2))
    top = (x, y + 2.2, z)
    for i in range(4):
        a = math.tau * (i + 0.5) / 4
        m.tube([(x + math.cos(a) * r, y, z + math.sin(a) * r), top], [0.012, 0.012], 4, IRON, c)
    m.tube([top, (x, crown(0.0) - 0.3, z)], [0.014, 0.014], 4, IRON, c)
    for i in range(12):
        a = math.tau * i / 12
        px, pz = x + math.cos(a) * r, z + math.sin(a) * r
        m.tube([(px, y, pz), (px, y + 0.06, pz)], [0.045, 0.05], 6, IRON, c, caps=True)
        m.tube([(px, y + 0.06, pz), (px, y + 0.2 + 0.05 * math.sin(i * 2.3), pz)], [0.018, 0.016], 5, "plaster_white", (0.85, 0.8, 0.66, 1.0), caps=True)


def church():
    porter.reset(411)
    cl.STONE = STONE
    walls, glass, vault = porter.Mesh("Walls"), porter.Mesh("Windows"), porter.Mesh("Vault")
    inside = cp.stone_tint(0.0, IN_TOP, seed=11.0, worn=0.0)
    outside = cp.stone_tint(0.0, OUT_TOP, seed=23.0, worn=0.35)
    outside.mat = OUTER
    bays = [-18.0 + 4.0 * i for i in range(12)]

    # The north wall, inside and out.
    t, g = cl.Turned(walls, NORTH), cl.Turned(glass, NORTH)
    for i, x in enumerate(bays):
        ua, ub = (x - 2.0 if i else -20.0 + F), (x + 2.0 if i < 11 else 28.0 - F)
        window_face(t, 1, ua, ub, 0.0, IN_TOP, TALL, x, inside)
        window_face(t, -1, x - 2.0, x + 2.0, 0.0, OUT_TOP, TALL, x, outside, hood=True)
        glazing(g, x, TALL)
        blind_arcade(t, 1, x)
        course(t, 1, ua, ub, TALL[0] - 0.6)
    for x in [-16.0 + 4.0 * i for i in range(11)]:
        shafts(t, x, 1)
        buttress(t, x, -1, 0.0, ((6.2, 1.15), (12.6, 0.7)), cp.stone_tint(0.0, 11.0, seed=31.0 + x, worn=0.8))
    face(t, -1, 28.0, 28.0 + F, 0.0, OUT_TOP, outside)
    course(t, -1, -20.0, 28.0 + F, TALL[0] - 0.4, k=0.7)
    course(t, -1, -20.0, 28.0 + F, OUT_TOP - 1.0, 0.1, 0.18, 0.7)

    # The south wall: the cloister, the west range and the east range stand
    # against its foot outside, so its outer face starts above them.
    t, g = cl.Turned(walls, SOUTH), cl.Turned(glass, SOUTH)
    doors = {10.0: [(10.0,) + DOOR], -10.0: [(-10.0,) + DOOR], -26.0: [(-26.0,) + DOOR], -18.0: [(-18.0, 0.47, 4.0, 6.03)]}
    for i, x in enumerate(bays):
        u = -x
        ua, ub = (u - 2.0 if i < 11 else -28.0 + F), (u + 2.0 if i else 20.0 - F)
        win = TALL if x < 12.0 else SHORT
        foot = 4.8 if x < 12.0 else 8.6
        window_face(t, 1, ua, ub, 0.0, IN_TOP, win, u, inside, doors.get(u, ()))
        window_face(t, -1, u - 2.0, u + 2.0, foot, OUT_TOP, win, u, outside, hood=True)
        glazing(g, u, win)
        if u not in doors and x not in (22.0,):
            blind_arcade(t, 1, u)
        course(t, 1, ua, ub, TALL[0] - 0.6)
    for x in [-16.0 + 4.0 * i for i in range(11)]:
        shafts(t, -x, 1)
        buttress(t, -x, -1, 5.3 if x < 12.0 else 9.0, ((12.6, 0.7),), cp.stone_tint(4.0, 11.0, seed=47.0 + x, worn=0.6))
    face(t, -1, -28.0 - F, -28.0, 0.0, OUT_TOP, outside)
    course(t, -1, -28.0 - F, 20.0, OUT_TOP - 1.0, 0.1, 0.18, 0.7)

    # The east wall and its great window; the gable over it.
    t, g = cl.Turned(walls, EAST_W), cl.Turned(glass, EAST_W)
    window_face(t, 1, -4.0 + F, 4.0 - F, 0.0, IN_TOP, EAST, 0.0, inside)
    window_face(t, -1, -4.0 - F, 4.0 + F, 0.0, OUT_TOP, EAST, 0.0, outside, hood=True)
    glazing(g, 0.0, EAST, level=2)
    course(t, 1, -4.0 + F, 4.0 - F, EAST[0] - 0.6)
    course(t, -1, -4.0 - F, 4.0 + F, EAST[0] - 0.4, k=0.7)
    for u in (-4.0, 4.0):
        buttress(t, u, -1, 0.0, ((6.2, 1.15), (12.6, 0.7)), cp.stone_tint(0.0, 11.0, seed=61.0 + u, worn=0.8))
    gable = [(-4.42, OUT_TOP, -F), (4.42, OUT_TOP, -F), (0.0, RIDGE + 0.7, -F)]
    t.poly(gable, STONE, [outside(*p) for p in gable], facing=(0, 0, -1))
    back = [(-4.42, OUT_TOP, 0.0), (4.42, OUT_TOP, 0.0), (0.0, RIDGE + 0.7, 0.0)]
    t.poly(back, STONE, pale(0.5), facing=(0, 0, 1))
    for k in (-1, 1):
        t.poly([(k * 4.42, OUT_TOP, -F), (0.0, RIDGE + 0.7, -F), (0.0, RIDGE + 0.7, 0.0), (k * 4.42, OUT_TOP, 0.0)], STONE, pale(0.7),
               facing=(k, 1, 0))
    # A small light in the gable, and the cross on its point.
    t.box((-0.16, RIDGE - 3.4, -F - 0.02), (0.16, RIDGE - 2.2, -F - 0.01), "window_dark", (0, 0, 0, 1), faces="z")
    t.box((-0.09, RIDGE + 0.7, -0.3), (0.09, RIDGE + 2.0, -0.12), STONE, pale(0.8))
    t.box((-0.42, RIDGE + 1.4, -0.3), (0.42, RIDGE + 1.58, -0.12), STONE, pale(0.8))

    # The west wall: the nave's side of it, with the door to the tower.
    t = cl.Turned(walls, WEST_W)
    wdoor = [(-2.0,) + DOOR]
    face(t, 1, -4.0 + F, 4.0 - F, 0.0, IN_TOP, inside, wdoor)
    course(t, 1, -4.0 + F, 4.0 - F, TALL[0] - 0.6)
    cp.arch_band(t, F, 2.5, 8.2, 3.4, 0.16, 0.09, (0, 0, 1), STONE, pale(0.82), cx=0.0, y0=TALL[0] - 0.46)
    for u in (-4.0 + F + 0.12, 4.0 - F - 0.12):
        shafts(t, u, 1)
    t = cl.Turned(walls, EAST_W)
    for u in (-4.0 + F + 0.12, 4.0 - F - 0.12):
        shafts(t, u, 1)
    walls.build()
    glass.build()

    # The vault: twelve bays, a heavier rib between each.
    same = cl.Turned(vault, lambda x, y, z: (x, y, z))
    za, zb = -36.0 + F, -28.0 - F
    edges = [-20.0 + F] + [-16.0 + 4.0 * i for i in range(11)] + [28.0 - F]
    for i, (xa, xb) in enumerate(zip(edges, edges[1:])):
        ribs = ["v0", "v1"] + (["u0"] if i == 0 else []) + (["u1"] if i == 11 else [])
        vault_bay(same, xa, xb, za, zb, ribs)
    for x in edges[1:-1]:
        cl.rib(same, [(x, crown(tt), lerp(za, zb, (tt + 1.0) * 0.5)) for tt in [-1.0 + k / 10 for k in range(21)]], 0.3, 0.26, pale(0.66))
    vault.build(smooth=True)

    # The floor: flags worn pale down the middle; in the choir (east of the
    # rood), tiles of two colours. The crypt stair's well is left open.
    floor = porter.Mesh("Floor")
    y = 0.056
    for ix in range(-20, 28):
        for iz in range(-36, -28):
            x0, x1 = max(float(ix), -20.0 + F), min(ix + 1.0, 28.0 - F)
            z0, z1 = max(float(iz), -36.0 + F), min(iz + 1.0, -28.0 - F)
            if 18 <= ix < 24 and iz == -35:
                z0 = -34.2
            elif 18 <= ix < 24 and iz == -36:
                z1 = -35.4
            pts = [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)]
            cols = []
            for p in pts:
                k = lerp(0.92, 0.62, smoothstep(0.4, 3.0, abs(p[2] + 32.0))) * (0.9 + 0.14 * fbm(p[0], p[2], 0.35, 2, 8.0))
                if ix >= 8:
                    k *= 0.62 if (ix + iz) % 2 else 1.0
                cols.append((k, k * (0.93 if ix >= 8 and (ix + iz) % 2 else 1.0), k * 0.96, 1.0))
            floor.poly(pts, "flags_worn", cols, facing=(0, 1, 0))
    # The well's lip.
    lip = (0.5, 0.5, 0.48, 1.0)
    for a, b, n in (((18.0, -35.4), (24.0, -35.4), (0, 0, 1)), ((18.0, -34.2), (24.0, -34.2), (0, 0, -1)), ((24.0, -35.4), (24.0, -34.2), (-1, 0, 0))):
        floor.poly([(a[0], -0.3, a[1]), (b[0], -0.3, b[1]), (b[0], y, b[1]), (a[0], y, a[1])], STONE, lip, facing=n)
    # The tower's floor.
    for ix in range(-28, -20):
        for iz in range(-36, -28):
            x0, x1 = max(float(ix), -28.0 + F), min(ix + 1.0, -20.0 - F)
            z0, z1 = max(float(iz), -36.0 + F), min(iz + 1.0, -28.0 - F)
            pts = [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)]
            cols = [(0.7 * (0.9 + 0.14 * fbm(p[0], p[2], 0.35, 2, 8.0)),) * 3 + (1.0,) for p in pts]
            floor.poly(pts, "flags_worn", cols, facing=(0, 1, 0))
    floor.build()

    # The roof: lead, behind the parapets.
    roof = porter.Mesh("Roof")
    cp.gable_roof(roof, -20.0, 28.0, -36.0, -28.0, EAVE, RIDGE, "lead_roof", (0.8, 0.8, 0.8), along="x", over=0.0)
    parapet(roof, (-20.0, -36.0 - F), (28.0 + F, -36.0 - F), (0, -1), EAVE - 0.3, OUT_TOP, outside)
    parapet(roof, (-20.0, -28.0 + F), (28.0 + F, -28.0 + F), (0, 1), EAVE - 0.3, OUT_TOP, outside)
    roof.build()

    # The tower: inside to the bell floor, outside to the battlements.
    tower = porter.Mesh("Tower")
    tw_in = cp.stone_tint(0.0, TOWER_IN, seed=71.0, worn=0.3)
    tw_out = cp.stone_tint(0.0, TOWER_TOP, seed=83.0, worn=0.6)
    tw_out.mat = OUTER
    slits = lambda us: [(u, 0.3, 9.6, 10.8) for u in us]
    tg = porter.Mesh("TowerWindows")
    sides = (
        # place, the tower's span along it, inside's sign, the cuts inside and out, where its outer face starts
        (NORTH, (-28.0, -20.0), 1, slits((-26.0, -22.0)), 0.0),
        (SOUTH, (20.0, 28.0), 1, slits((22.0, 26.0)), 0.0),
        (TOWER_W, (-4.0, 4.0), 1, slits((2.0,)) + [(-2.0,) + DOOR, (-2.0, 0.3, 9.6, 10.8)], 0.0),
        (WEST_W, (-4.0, 4.0), -1, slits((-2.0, 2.0)) + wdoor, OUT_TOP - 0.6),
    )
    for place, (ua, ub), s, cuts, foot in sides:
        t = cl.Turned(tower, place)
        face(t, s, ua + F, ub - F, 0.0, TOWER_IN, tw_in, cuts)
        outer = [c for c in cuts if not (place is WEST_W and c[2] < foot)]
        face(t, -s, ua - F, ub + F, foot, 22.6, tw_out, [c for c in outer if c[3] > foot])
        mid = (ua + ub) * 0.5
        window_face(t, -s, ua - F, ub + F, 22.6, TOWER_TOP, BELFRY, mid, tw_out, hood=True)
        glazing(cl.Turned(tg, place), mid, BELFRY, louvres=-s)
        # The belfry's window, seen from inside the stage (it is never entered): closed by its boards.
        for y, k in ((8.0, 0.72), (15.0, 0.72), (22.3, 0.72), (TOWER_TOP - 1.0, 0.68)):
            if y > foot:
                course(t, -s, ua - F - 0.02, ub + F + 0.02, y, 0.09, 0.18, k)
        if place is not WEST_W:
            for u in (ua + 0.25, ub - 0.25):
                buttress(t, u, -s, 0.0, ((7.6, 1.0), (14.6, 0.62), (21.9, 0.3)), cp.stone_tint(0.0, 21.0, seed=91.0 + u, worn=0.8), 0.9)
    # The bell floor's boards and beams, from below.
    for i in range(16):
        x0 = -28.0 + F + i * (7.16 / 16)
        k = 0.34 + 0.12 * ((math.sin(i * 12.9898) * 43758.5453) % 1.0)
        tower.box((x0, TOWER_IN, -36.0 + F), (x0 + 7.16 / 16 - 0.01, TOWER_IN + 0.05, -28.0 - F), OAK, (k, k * 0.95, k * 0.9, 1.0), faces="y")
    for z in (-34.4, -32.9, -31.1, -29.6):
        tower.box((-28.0 + F, TOWER_IN - 0.26, z - 0.11), (-20.0 - F, TOWER_IN, z + 0.11), OAK, (0.3, 0.28, 0.26, 1.0), faces="yzZ")
    # Battlements and a short lead spire.
    x0, x1, z0, z1 = -28.0 - F, -20.0 + F, -36.0 - F, -28.0 + F
    top = cp.stone_tint(TOWER_TOP - 2.0, TOWER_TOP + 2.0, seed=97.0, worn=0.6)
    for a, b, out in (((x0, z0), (x1, z0), (0, 0, -1)), ((x1, z0), (x1, z1), (1, 0, 0)), ((x1, z1), (x0, z1), (0, 0, 1)), ((x0, z1), (x0, z0), (-1, 0, 0))):
        cp.battlements(tower, a, b, TOWER_TOP, out, OUTER, top, thick=0.4, wall=0.7, merlon=0.8, width=1.1, gap=0.75)
    lead = [(x0 + 0.4, TOWER_TOP + 0.1, z0 + 0.4), (x1 - 0.4, TOWER_TOP + 0.1, z0 + 0.4), (x1 - 0.4, TOWER_TOP + 0.1, z1 - 0.4), (x0 + 0.4, TOWER_TOP + 0.1, z1 - 0.4)]
    tower.poly(lead, "lead_roof", (0.7, 0.7, 0.7, 1.0), facing=(0, 1, 0))
    cp.spire(tower, -24.0, -32.0, TOWER_TOP + 0.1, TOWER_TOP + 9.0, 2.8, "lead_roof", (0.75, 0.75, 0.75), sides=8)
    tower.tube([(-24.0, TOWER_TOP + 8.9, -32.0), (-24.0, TOWER_TOP + 10.1, -32.0)], [0.03, 0.03], 4, IRON, (0.1, 0.1, 0.1, 1.0))
    tower.box((-24.3, TOWER_TOP + 9.7, -32.02), (-23.7, TOWER_TOP + 9.76, -31.98), IRON, (0.1, 0.1, 0.1, 1.0))
    tower.build()
    tg.build()

    # The fittings.
    fit = porter.Mesh("Fittings")
    oak = (0.36, 0.33, 0.3, 1.0)
    x = 8.0
    fit.box((x - 0.16, 6.6, za), (x + 0.16, 6.96, zb), OAK, oak)
    for z, k in ((za, 1), (zb, -1)):
        fit.box((x - 0.2, 6.25, z), (x + 0.2, 6.6, z + k * 0.3), STONE, pale(0.8))
        # A brace under each end.
        fit.poly([(x - 0.1, 6.6, z + k * 1.1), (x + 0.1, 6.6, z + k * 1.1), (x + 0.1, 5.7, z + k * 0.02), (x - 0.1, 5.7, z + k * 0.02)], OAK, oak,
                 facing=(0, -1, k))
        for sx in (-1, 1):
            fit.poly([(x + sx * 0.1, 6.6, z + k * 1.1), (x + sx * 0.1, 5.7, z + k * 0.02), (x + sx * 0.1, 6.6, z + k * 0.02)], OAK, oak, facing=(sx, 0, 0))
    fit.box((x - 0.07, 6.96, -32.1), (x + 0.07, 9.5, -31.9), OAK, oak)
    fit.box((x - 0.07, 8.5, -32.85), (x + 0.07, 8.7, -31.15), OAK, oak)
    for cx in (-12.0, -2.0, 18.0):
        corona(fit, cx, -32.0, 5.2, 0.95)
    fit.build()
    porter.export("env_church")


if __name__ == "__main__":
    church()
