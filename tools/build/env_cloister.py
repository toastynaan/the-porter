"""The abbey's cloister (every night): its arcades, the vaults over its
walks, and the garden in the garth. Both models are in the abbey's own
coordinates and are laid over the greybox (game/world/abbey/areas/
cloister.tscn), which still stops people and shapes the navmesh but is no
longer drawn. The plan is the greybox's: arcades on x = -8 and 8, z = -24
and -8, four bays of 4 m a side, one bay a side open to the garth; walks
3.2 m wide behind them; the ranges' walls at x = -12 and 12, z = -28 and -4.

`env_cloister_arcade`:
- Arcade: each bay a pointed arch in two orders under a hood mould, on
  piers with a buttress to the garth. A closed bay stands on a low wall and
  holds tracery: two cusped lights and a quatrefoil. The open bay is clear.
- Vault: a rib vault over every bay of the walks and the four corners,
  springing at 2.7 m and 4.55 m at the crown (the greybox's flat roof was
  at 3.9), on shafts against the piers and corbels on the back walls.
- BackWalls: the ranges' walls as the walks see them, with a surround to
  each door and window that is in the greybox.
- Floor: worn flags. Roof: lead, nearly flat, behind the arcade's parapet.
- Dressing and Figures (drawn only; tools/build/dress.py): a niche at the
  end of two walks with a hooded figure in it (one stands facing the
  wall), a walled-up doorway at the end of a third, two small figures on
  the parapet over the garth, three abbots' grave slabs in the east walk,
  leaves blown in, damp, runs, a few cobwebs, a crack, one light of
  tracery broken.

`env_cloister_garth`: gravel walks round and across the garth, a paved
round at the middle with a conduit basin, four beds edged in clipped box
(herbs and a yew, a lawn for the hawthorn, late flowers and a yew, a
lawn), and what still grows there in late autumn: the planted beds are
mostly bare earth and dead stalks, the hawthorn's leaves lie under it, the
basin has a scum and a stain. Only the basin and the yews are solid, as
blocks in cloister.tscn.

Run: tools/build.sh env_cloister
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
import city_parts as cp
import dress
from mathutils import Vector
from porter import fbm, lerp, smoothstep, srgb

STONE = "stone_cloister"
WEB = "stone_cloister"
PALE = (0.95, 0.93, 0.88)

# The arcade: bay centres along a side, the main arch (half its width, its
# springing, its rise), the inner order, the wall's top.
BAYS = (-6.0, -2.0, 2.0, 6.0)
HALF, SPRING, RISE = 1.6, 1.9, 1.8
INNER, INNER_RISE = 1.44, 1.66
WALL_TOP = 5.0
# The walks' vault: its springing and rise; the back wall's face (2 cm
# proud of the greybox wall behind it).
VSPRING, VRISE = 2.7, 1.85
BACK = -3.58
# A side's own space: u along it, v out into the garth (the arcade's middle
# at v = 0, the walk at v < 0). Each maps it into the abbey's, and names its
# open bay (u) and what is cut through its back wall (u, "door" or "window")
# or into it (a recess: three of the four walks end on a blank wall, and
# each has one: "niche", "niche_turned" where the figure faces the wall,
# "blind" for a doorway walled up).
SIDES = {
    "N": (lambda u, y, v: (u, y, -24.0 + v), -2.0, ((-10.0, "door"), (10.0, "door"))),
    "S": (lambda u, y, v: (-u, y, -8.0 - v), -2.0,
          ((2.0, "door"), (6.0, "window"), (-2.0, "window"), (-6.0, "window"), (-10.0, "niche_turned"), (10.0, "blind"))),
    "W": (lambda u, y, v: (-8.0 + v, y, -16.0 - u), 2.0, ((6.0, "door"), (-2.0, "door"), (-10.0, "door"), (10.0, "niche"))),
    "E": (lambda u, y, v: (8.0 - v, y, -16.0 + u), 2.0,
          ((-10.0, "door"), (-2.0, "door"), (2.0, "door"), (10.0, "door"), (-6.0, "window"), (6.0, "window"))),
}
# A recess: half its width, its foot, its springing, its rise, its depth
# (the walls are 0.8 m thick: 0.3 is as deep as one can go).
NICHE = (0.42, 0.5, 2.0, 0.55, 0.3)
RECESS = {"niche": NICHE, "niche_turned": NICHE, "blind": (0.6, 0.0, 1.55, 0.7, 0.2)}
# Fallen leaves, against dress.leaves' own colours (orange-red): browner.
LEAF = (1.0, 1.0, 1.0)
# The one bay whose tracery has lost a cusp and a spur: (side, bay).
BROKEN = ("W", -6.0)


class Turned:
    """A mesh seen from a side's own space: what is built through it lands
    in the abbey's."""

    def __init__(self, mesh, place):
        self.mesh = mesh
        self.place = place

    def vert(self, x, y, z, color=(1.0, 1.0, 1.0, 1.0), uv=(0.0, 0.0)):
        p = self.place(x, y, z)
        return self.mesh.vert(p[0], p[1], p[2], color, uv)

    def face(self, indices, mat):
        self.mesh.face(indices, mat)

    quad = porter.Mesh.quad
    poly = porter.Mesh.poly
    tube = porter.Mesh.tube
    box = porter.Mesh.box


def pale(k=1.0):
    return cp.rgba(PALE, k)


def bar(t, pts, width, v0, v1, color, closed=False):
    """A bar of cut stone following `pts` (u, y), `width` across, from v0 to
    v1 through the wall: tracery."""
    n = len(pts)

    def normal(i):
        a = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        b = pts[(i + 1) % n] if (closed or i < n - 1) else pts[i]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy) or 1.0
        return (-dy / length, dx / length)

    h = width * 0.5
    left = [(p[0] + normal(i)[0] * h, p[1] + normal(i)[1] * h) for i, p in enumerate(pts)]
    right = [(p[0] - normal(i)[0] * h, p[1] - normal(i)[1] * h) for i, p in enumerate(pts)]
    for i in range(n if closed else n - 1):
        j = (i + 1) % n
        nl = normal(i)
        for v, f in ((v1, 1), (v0, -1)):
            t.poly([(left[i][0], left[i][1], v), (left[j][0], left[j][1], v), (right[j][0], right[j][1], v), (right[i][0], right[i][1], v)],
                   STONE, color, facing=(0, 0, f))
        for side, f in ((left, 1), (right, -1)):
            t.poly([(side[i][0], side[i][1], v0), (side[j][0], side[j][1], v0), (side[j][0], side[j][1], v1), (side[i][0], side[i][1], v1)],
                   STONE, color, facing=(nl[0] * f, nl[1] * f, 0))


def cusp(t, a, b, tip, v0, v1, color):
    """A spur of tracery: from `a` and `b` on a bar in to a point."""
    for v, f in ((v1, 1), (v0, -1)):
        t.poly([(a[0], a[1], v), (b[0], b[1], v), (tip[0], tip[1], v)], STONE, color, facing=(0, 0, f))
    mid = ((a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5)
    for p in (a, b):
        out = (p[0] - mid[0], p[1] - mid[1], 0.0)
        t.poly([(p[0], p[1], v0), (tip[0], tip[1], v0), (tip[0], tip[1], v1), (p[0], p[1], v1)], STONE, color, facing=out)


def tracery(t, u0, broken=False):
    """Two cusped lights on a middle shaft, and a quatrefoil over them.
    `broken`: one cusp and one spur have fallen out."""
    v0, v1 = -0.09, 0.09
    c = pale(0.92)
    lift = 0.68
    t.box((u0 - 0.065, lift, v0), (u0 + 0.065, 1.95, v1), STONE, c, faces="xXzZ")
    t.box((u0 - 0.11, lift, v0 - 0.04), (u0 + 0.11, lift + 0.14, v1 + 0.04), STONE, c, faces="xXzZY")
    t.box((u0 - 0.11, 1.85, v0 - 0.04), (u0 + 0.11, 1.97, v1 + 0.04), STONE, c)
    for s in (-1, 1):
        cx = u0 + s * 0.72
        prof = cp.arch_profile(0.66, 1.95, 1.0, 6, cx)
        bar(t, prof, 0.085, v0, v1, c)
        heart = (cx, 2.2)
        for i in (3, 9):
            if broken and s > 0 and i == 3:
                continue
            p = prof[i]
            d = math.hypot(heart[0] - p[0], heart[1] - p[1])
            tip = (p[0] + (heart[0] - p[0]) / d * 0.2, p[1] + (heart[1] - p[1]) / d * 0.2)
            half = lambda a, b: ((a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5)
            cusp(t, half(prof[i - 1], p), half(prof[i + 1], p), tip, v0 + 0.02, v1 - 0.02, c)
    # The quatrefoil: a ring with four spurs.
    yc, r = 2.93, 0.4
    ring = [(u0 + math.cos(math.tau * i / 16) * r, yc + math.sin(math.tau * i / 16) * r) for i in range(16)]
    bar(t, ring, 0.08, v0, v1, c, closed=True)
    for k in range(4):
        if broken and k == 2:
            continue
        a = math.tau * (k + 0.5) / 4
        da = 0.2
        cusp(t, (u0 + math.cos(a - da) * (r - 0.03), yc + math.sin(a - da) * (r - 0.03)),
             (u0 + math.cos(a + da) * (r - 0.03), yc + math.sin(a + da) * (r - 0.03)),
             (u0 + math.cos(a) * 0.2, yc + math.sin(a) * 0.2), v0 + 0.02, v1 - 0.02, c)
    # Its ties to the arch over it.
    for a in (math.radians(90),):
        p0 = (u0 + math.cos(a) * r, yc + math.sin(a) * r)
        p1 = (u0 + math.cos(a) * (r + 0.42), yc + math.sin(a) * (r + 0.42))
        bar(t, [p0, p1], 0.08, v0, v1, c)


def bay(t, u0, is_open, tint, first, last, broken=False):
    """One bay of the arcade."""
    g0, g1 = (-7.6 if first else u0 - 2.0), (7.6 if last else u0 + 2.0)
    w0, w1 = (-8.4 if first else u0 - 2.0), (8.4 if last else u0 + 2.0)
    cp.arch_wall(t, 0.4, g0, g1, 0.0, WALL_TOP, HALF, SPRING, RISE, (0, 0, 1), STONE, tint, cx=u0)
    cp.arch_wall(t, -0.4, w0, w1, 0.0, WALL_TOP, HALF, SPRING, RISE, (0, 0, -1), STONE, tint, cx=u0)
    for va, vb in ((0.2, 0.4), (-0.4, -0.2)):
        cp.vault(t, va, vb, HALF, SPRING, RISE, STONE, tint, cx=u0, step=0.4)
    apex = SPRING + RISE
    cp.arch_wall(t, 0.2, u0 - HALF, u0 + HALF, 0.0, apex, INNER, SPRING, INNER_RISE, (0, 0, 1), STONE, tint, cx=u0)
    cp.arch_wall(t, -0.2, u0 - HALF, u0 + HALF, 0.0, apex, INNER, SPRING, INNER_RISE, (0, 0, -1), STONE, tint, cx=u0)
    cp.vault(t, -0.2, 0.2, INNER, SPRING, INNER_RISE, STONE, tint, cx=u0, step=0.4)
    cp.arch_band(t, 0.4, HALF, SPRING, RISE, 0.13, 0.06, (0, 0, 1), STONE, pale(0.9), cx=u0)
    cp.arch_band(t, -0.4, HALF, SPRING, RISE, 0.1, 0.04, (0, 0, -1), STONE, pale(0.8), cx=u0)
    # Imposts where the arch springs.
    for s in (-1, 1):
        a, b = sorted((u0 + s * (HALF - 0.07), u0 + s * (HALF + 0.03)))
        t.box((a, SPRING - 0.17, -0.46), (b, SPRING - 0.02, 0.46), STONE, pale(0.86))
        a, b = sorted((u0 + s * (INNER - 0.06), u0 + s * (INNER + 0.02)))
        t.box((a, SPRING - 0.15, -0.25), (b, SPRING - 0.03, 0.25), STONE, pale(0.86))
    if is_open:
        # A worn step through to the garth.
        t.box((u0 - INNER, 0.0, -0.4), (u0 + INNER, 0.07, 0.62), "flags_worn", (0.8, 0.8, 0.78, 1.0), faces="xXZY")
        return
    cp.slab(t, (u0 - HALF, 0.0, -0.4), (u0 + HALF, 0.6, 0.4), STONE, tint, faces="zZ", step=1.0)
    k = 0.8 + 0.1 * math.sin(u0 * 1.7)
    t.box((u0 - HALF, 0.58, -0.46), (u0 + HALF, 0.68, 0.46), STONE, pale(k), faces="zZyY")
    tracery(t, u0, broken)


def buttress(t, u, tint):
    for y0, y1, out in ((0.0, 2.2, 0.55), (2.2, 3.7, 0.32)):
        cp.slab(t, (u - 0.3, y0, 0.4), (u + 0.3, y1, 0.4 + out), STONE, tint, faces="xXZ", step=1.0)
        back = 0.32 if y0 == 0.0 else 0.0
        t.poly([(u - 0.3, y1, 0.4 + out), (u + 0.3, y1, 0.4 + out), (u + 0.3, y1 + 0.32, 0.4 + back), (u - 0.3, y1 + 0.32, 0.4 + back)], STONE,
               pale(0.82), facing=(0, 1, 1))
        for s in (-1, 1):
            t.poly([(u + s * 0.3, y1, 0.4 + out), (u + s * 0.3, y1 + 0.32, 0.4 + back), (u + s * 0.3, y1 + 0.32, 0.4), (u + s * 0.3, y1, 0.4)],
                   STONE, pale(0.7), facing=(s, 0, 0))
    # A plinth round its foot.
    t.box((u - 0.36, 0.0, 0.4), (u + 0.36, 0.3, 1.01), STONE, cp.rgba(cp.STONE_DAMP, 1.5), faces="xXZ")
    t.poly([(u - 0.36, 0.3, 1.01), (u + 0.36, 0.3, 1.01), (u + 0.3, 0.38, 0.95), (u - 0.3, 0.38, 0.95)], STONE, pale(0.7), facing=(0, 1, 1))


def shaft(t, u, v, top):
    """A thin shaft against a pier, with its base and its cap, for the vault's ribs."""
    c = pale(0.82)
    t.tube([(u, 0.0, v), (u, 0.16, v), (u, 0.22, v), (u, top - 0.26, v), (u, top - 0.2, v), (u, top - 0.04, v), (u, top, v)],
           [0.13, 0.13, 0.085, 0.085, 0.1, 0.17, 0.18], 8, STONE, c, caps=True)


def corbel(t, u, v):
    t.tube([(u, VSPRING - 0.5, v), (u, VSPRING - 0.32, v), (u, VSPRING - 0.06, v), (u, VSPRING, v)], [0.03, 0.1, 0.19, 0.2], 6, STONE,
           pale(0.8), caps=True)


def crown(tt):
    """How high the vault is, `tt` of the way from a bay's middle (0) to its edge (1)."""
    return VSPRING + cp.arch_height(1.0, 0.0, VRISE, min(abs(tt), 0.99999))


def rib(t, pts, width, depth, color):
    """A rib under the vault along `pts` (points on its surface)."""
    ps = [Vector(p) for p in pts]
    run = ps[-1] - ps[0]
    side = Vector((run.z, 0.0, -run.x)).normalized() * (width * 0.5)
    hang = []
    for i, p in enumerate(ps):
        tan = (ps[min(i + 1, len(ps) - 1)] - ps[max(i - 1, 0)]).normalized()
        n = tan.cross(side).normalized()
        if n.y > 0.0:
            n = -n
        hang.append(n * depth)
    for i in range(len(ps) - 1):
        a, b = ps[i], ps[i + 1]
        ha, hb = hang[i], hang[i + 1]
        t.poly([tuple(a - side + ha), tuple(a + side + ha), tuple(b + side + hb), tuple(b - side + hb)], STONE, color, facing=tuple(ha + hb))
        for s in (-1, 1):
            t.poly([tuple(a + side * s - ha * 0.2), tuple(a + side * s + ha), tuple(b + side * s + hb), tuple(b + side * s - hb * 0.2)], STONE,
                   color, facing=tuple(side * s))


def vault_bay(t, ua, ub, va, vb, wall_ribs):
    """A rib vault over ua..ub by va..vb: two pointed tunnels crossing, ribs
    on its diagonals, a boss at the crown. `wall_ribs` names the edges that
    are against a wall ("u0", "u1", "v0", "v1")."""
    cu, hu, cv, hv = (ua + ub) * 0.5, (ub - ua) * 0.5, (va + vb) * 0.5, (vb - va) * 0.5
    n = 8
    ts = [-1.0 + i / n for i in range(2 * n + 1)]

    def shade(p):
        k = lerp(1.15, 0.8, smoothstep(VSPRING, VSPRING + VRISE, p[1])) * (0.92 + 0.1 * fbm(p[0], p[2], 0.4, 2, 4.0))
        return (k, k * 0.99, k * 0.96, 1.0)

    def web(pts):
        out = [pts[0]]
        for p in pts[1:]:
            if math.dist(p, out[-1]) > 1e-6:
                out.append(p)
        if len(out) > 2 and math.dist(out[0], out[-1]) < 1e-6:
            out.pop()
        if len(out) >= 3:
            t.poly(out, WEB, [shade(p) for p in out], facing=(0, -1, 0))

    for ta, tb in zip(ts, ts[1:]):
        for s in (-1, 1):
            # The cells against the ends (the tunnel along u), then against the sides.
            web([(cu + s * hu * abs(ta), crown(ta), cv + hv * ta), (cu + s * hu, crown(ta), cv + hv * ta),
                 (cu + s * hu, crown(tb), cv + hv * tb), (cu + s * hu * abs(tb), crown(tb), cv + hv * tb)])
            web([(cu + hu * ta, crown(ta), cv + s * hv * abs(ta)), (cu + hu * ta, crown(ta), cv + s * hv),
                 (cu + hu * tb, crown(tb), cv + s * hv), (cu + hu * tb, crown(tb), cv + s * hv * abs(tb))])
    c = pale(0.78)
    for s in (-1, 1):
        rib(t, [(cu + hu * tt, crown(tt), cv + s * hv * tt) for tt in ts], 0.13, 0.15, c)
    for name, fixed, lo in (("u0", ua, True), ("u1", ub, True), ("v0", va, False), ("v1", vb, False)):
        if name not in wall_ribs:
            continue
        inset = 0.045 if name.endswith("0") else -0.045
        if lo:
            rib(t, [(fixed + inset, crown(tt), cv + hv * tt) for tt in ts], 0.09, 0.1, c)
        else:
            rib(t, [(cu + hu * tt, crown(tt), fixed + inset) for tt in ts], 0.09, 0.1, c)
    top = crown(0.0)
    t.tube([(cu, top - 0.3, cv), (cu, top - 0.24, cv), (cu, top - 0.12, cv), (cu, top, cv)], [0.06, 0.17, 0.2, 0.2], 8, STONE, pale(0.7), caps=True)


def recess(t, uc, kind, tint, top):
    """A pointed recess in a back wall, in the wall's thickness: a niche
    with a sill for a figure, or a doorway long walled up, its blocking
    set back from the face."""
    half, foot, spring, rise, depth = RECESS[kind]
    deep = BACK - depth
    cp.arch_wall(t, BACK, uc - half, uc + half, foot, top, half, spring, rise, (0, 0, 1), STONE, tint, cx=uc)
    shade = lambda x, y, z: tuple(q * 0.62 for q in tint(x, y, z)[:3]) + (1.0,)
    cp.vault(t, deep, BACK, half, spring, rise, STONE, shade, cx=uc, y0=foot, step=depth)
    prof = [(uc + half, foot)] + cp.arch_profile(half, spring, rise, 8, uc) + [(uc - half, foot)]
    c = pale(0.84)
    if kind == "blind":
        # The blocking: rubble, darker than the wall, and the old threshold under it.
        dark = lambda x, y, z: tuple(q * 0.5 for q in tint(x, y, z)[:3]) + (1.0,)
        for (xa, ya), (xb, yb) in zip(prof[1:], prof[2:-1]):
            pts = [(xa, ya, deep), (xb, yb, deep), (xb, foot, deep), (xa, foot, deep)]
            t.poly(pts, "stone_rubble", [dark(*q) for q in pts], facing=(0, 0, 1))
        t.poly([(uc - half, 0.058, deep), (uc + half, 0.058, deep), (uc + half, 0.058, BACK + 0.02), (uc - half, 0.058, BACK + 0.02)], "flags_worn",
               (0.5, 0.5, 0.48, 1.0), facing=(0, 1, 0))
        cp.arch_band(t, BACK, half, spring, rise, 0.13, 0.05, (0, 0, 1), STONE, c, cx=uc, y0=0.0)
        return
    back = [(x, y, deep) for x, y in prof]
    t.poly(back, STONE, [shade(*q)[:3] + (1.0,) for q in back], facing=(0, 0, 1))
    t.poly([(uc - half, foot, deep), (uc + half, foot, deep), (uc + half, foot, BACK), (uc - half, foot, BACK)], STONE, pale(0.7), facing=(0, 1, 0))
    t.box((uc - half - 0.1, foot - 0.13, BACK), (uc + half + 0.1, foot, BACK + 0.08), STONE, c, faces="xXZyY")
    cp.arch_band(t, BACK, half, spring, rise, 0.1, 0.05, (0, 0, 1), STONE, c, cx=uc, y0=foot)


def back_wall(t, cuts, tint):
    """A range's wall as the walk sees it, left open at its doors and
    windows, each with its reveal back to the wall's middle (where the
    face of the room behind takes over) and, under a door, the floor
    through the wall."""
    top = WALL_TOP - 0.2
    mid = BACK - 0.42

    def seg(ua, ub, ya, yb):
        cp.panel(t, (ua, BACK), (ub, BACK), ya, yb, (0, 0, 1), STONE, tint, 1.6, 1.2)
        if ya == 0.0 and ub - ua > 0.05:
            t.box((ua, 0.0, BACK), (ub, 0.3, BACK + 0.06), STONE, cp.rgba(cp.STONE_DAMP, 1.5), faces="xXZ")
            t.poly([(ua, 0.3, BACK + 0.06), (ub, 0.3, BACK + 0.06), (ub, 0.36, BACK), (ua, 0.36, BACK)], STONE, pale(0.7), facing=(0, 1, 1))

    u = -11.58
    for uc, kind in sorted(cuts):
        if kind in RECESS:
            half, foot = RECESS[kind][:2]
            seg(u, uc - half, 0.0, top)
            if foot > 0.0:
                seg(uc - half, uc + half, 0.0, foot - 0.13)
            recess(t, uc, kind, tint, top)
            u = uc + half
            continue
        hw, y0, y1 = (0.47, 0.0, 2.03) if kind == "door" else (0.31, 1.59, 2.81)
        seg(u, uc - hw, 0.0, top)
        if y0 > 0.0:
            seg(uc - hw, uc + hw, 0.0, y0)
        seg(uc - hw, uc + hw, y1, top)
        u = uc + hw
        c = pale(0.84)
        fw = 0.14 if kind == "door" else 0.1
        for s in (-1, 1):
            a, b = sorted((uc + s * hw, uc + s * (hw + fw)))
            t.box((a, y0, BACK), (b, y1, BACK + 0.07), STONE, c, faces="xXZ")
        t.box((uc - hw - fw, y1, BACK), (uc + hw + fw, y1 + fw, BACK + 0.07), STONE, c, faces="xXZyY")
        # The reveal: jambs and soffit (and a window's sill) back to the wall's middle.
        dark = pale(0.6)
        for s in (-1, 1):
            a = uc + s * hw
            t.poly([(a, y0, mid), (a, y1, mid), (a, y1, BACK), (a, y0, BACK)], STONE, dark, facing=(-s, 0, 0))
        t.poly([(uc - hw, y1, mid), (uc + hw, y1, mid), (uc + hw, y1, BACK), (uc - hw, y1, BACK)], STONE, dark, facing=(0, -1, 0))
        if kind == "window":
            t.poly([(uc - hw, y0, mid), (uc + hw, y0, mid), (uc + hw, y0, BACK), (uc - hw, y0, BACK)], STONE, pale(0.8), facing=(0, 1, 0))
        else:
            # (The ranges floor theirs too, in the same flags at the same height: the two can't be told apart.)
            t.poly([(uc - hw, 0.056, mid - 0.42), (uc + hw, 0.056, mid - 0.42), (uc + hw, 0.056, BACK - 0.02), (uc - hw, 0.056, BACK - 0.02)], "flags_worn",
                   (0.6, 0.6, 0.58, 1.0), facing=(0, 1, 0))
        if kind == "door":
            # A blind arch over the lintel.
            cp.arch_band(t, BACK, hw + fw, y1 + fw, 0.62, 0.12, 0.07, (0, 0, 1), STONE, c, cx=uc, n=6)
            head = [(x, y, BACK + 0.012) for x, y in cp.arch_profile(hw + fw, y1 + fw, 0.62, 6, uc)]
            t.poly(head, STONE, pale(0.5), facing=(0, 0, 1))
        else:
            t.box((uc - hw - fw, y0 - 0.1, BACK), (uc + hw + fw, y0, BACK + 0.1), STONE, c, faces="xXZyY")
    seg(u, 11.58, 0.0, top)


def grave_slab(m, x0, x1, z, width, seed, worn):
    """An abbot's grave slab in a walk's floor, head to the west (x0): dark
    marble, a long cross on steps cut in it and gone pale with dust, `worn`
    (0..1) by feet. Flat."""
    y, za, zb = 0.063, z - width * 0.5, z + width * 0.5
    nx, nz = 8, 3
    for i in range(nx):
        for j in range(nz):
            pts = [(lerp(x0, x1, (i + di) / nx), y, lerp(za, zb, (j + dj) / nz)) for di, dj in ((0, 0), (1, 0), (1, 1), (0, 1))]
            cols = []
            for q in pts:
                k = 0.05 + 0.025 * fbm(q[0] * 2.0, q[2] * 2.0, 1.0, 2, seed) + 0.02 * worn
                cols.append((k, k, k * 1.08, 1.0))
            m.poly(pts, "painted", cols, facing=(0, 1, 0))
    cut = (0.3, 0.29, 0.26, 0.5 * (1.0 - 0.65 * worn))
    joint = (0.01, 0.01, 0.012, 0.8)

    def line(a, b, w, col):
        dx, dz = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dz) or 1.0
        px, pz = -dz / n * w * 0.5, dx / n * w * 0.5
        m.poly([(a[0] - px, y + 0.004, a[1] - pz), (a[0] + px, y + 0.004, a[1] + pz), (b[0] + px, y + 0.004, b[1] + pz), (b[0] - px, y + 0.004, b[1] - pz)],
               dress.GRIME, col, facing=(0, 1, 0))

    for a, b in (((x0, za), (x1, za)), ((x1, za), (x1, zb)), ((x1, zb), (x0, zb)), ((x0, zb), (x0, za))):
        line(a, b, 0.03, joint)
    head, foot = x0 + 0.24, x1 - 0.26
    line((head, z), (foot, z), 0.034, cut)
    line((head + 0.3, z - 0.21), (head + 0.3, z + 0.21), 0.034, cut)
    for k, half in enumerate((0.24, 0.17, 0.1)):
        line((foot - k * 0.07, z - half), (foot - k * 0.07, z + half), 0.034, cut)


class Dimmed:
    """A mesh that takes its colours times `k` and its faces bigger by
    `grow`: dress.leaves lays small leaves that glow orange-red under the
    lantern; these are old, brown and wet."""

    def __init__(self, mesh, k=(1.0, 1.0, 1.0), grow=1.0):
        self.mesh, self.k, self.grow = mesh, k, grow

    def vert(self, x, y, z, color=(1.0, 1.0, 1.0, 1.0), uv=(0.0, 0.0)):
        return self.mesh.vert(x, y, z, (color[0] * self.k[0], color[1] * self.k[1], color[2] * self.k[2], color[3]), uv)

    def face(self, indices, mat):
        self.mesh.face(indices, mat)

    def poly(self, points, mat, color=(1.0, 1.0, 1.0, 1.0), uvs=None, facing=None):
        cx, cz = sum(q[0] for q in points) / len(points), sum(q[2] for q in points) / len(points)
        points = [(cx + (q[0] - cx) * self.grow, q[1], cz + (q[2] - cz) * self.grow) for q in points]
        return porter.Mesh.poly(self, points, mat, color, uvs, facing)


def turf_or_gravel(x, z):
    """How high the garth's ground is at (x, z): the beds' domed turf, the
    paved round, the gravel."""
    qx, qz = abs(x), abs(z - MID_Z)
    inside = min(qx - AXIS, qz - AXIS, RING - qx, RING - qz, math.hypot(qx, qz) - ROUND)
    if inside > 0.0:
        return 0.035 + 0.06 * smoothstep(0.0, 1.4, inside) + 0.015 * fbm(x, z, 0.8, 2, 3.0)
    return 0.03 if math.hypot(qx, qz) < ROUND else 0.014


def dressing():
    """What age and neglect have done to the cloister, and who stands in
    it. Stains and webs are thin faces just proud of the stone; nothing
    here is solid, so nothing stands in a walking path below 2.3 m: the
    figures are in the walls' thickness or on the parapet."""
    d, fig = porter.Mesh("Dressing"), porter.Mesh("Figures")
    rng = random.Random(41)
    wet = {"N": 0.3, "S": 0.6, "W": 0.45, "E": 0.45}
    statue = (0.6, 0.58, 0.53)
    for i, (name, (place, open_u, cuts)) in enumerate(SIDES.items()):
        t, f = Turned(d, place), Turned(fig, place)
        for uc, kind in cuts:
            if kind in ("niche", "niche_turned"):
                # A hooded figure in the niche at the walk's end. One of the two has its back to the walk.
                foot, away = NICHE[1], kind == "niche_turned"
                dress.figure(f, (uc, foot, BACK - (0.07 if away else 0.12)), math.pi if away else 0.0, 1.62, colour=statue, bowed=0.8)
            elif kind == "blind":
                # The wall has moved over the walled-up door.
                dress.crack(t, (uc + 0.12, RECESS[kind][2] + RECESS[kind][3] + 0.1, BACK), (0, 1), 1.7, seed=5)
                dress.damp(t, (uc - 0.58, BACK - RECESS[kind][4]), (uc + 0.58, BACK - RECESS[kind][4]), 0.06, (0, 1), 1.0, dress.DARK, 0.6, seed=3.0)
            elif kind == "window":
                dress.run(t, (uc + rng.uniform(-0.15, 0.15), 1.49, BACK), (0, 1), 0.36, rng.uniform(0.8, 1.1), dress.DARK, 0.5, seed=uc + i)
        for u0 in BAYS:
            if u0 == open_u:
                continue
            # Green at the low wall's foot on the garth's side (most on the side that never sees the sun).
            dress.damp(t, (u0 - 1.62, 0.4), (u0 + 1.62, 0.4), 0.02, (0, 1), 0.56, dress.GREEN, wet[name], seed=i * 10.0 + u0)
        # Runs down the garth's face from under the string course, clear of the arches.
        for u0 in rng.sample(BAYS, 3):
            du = rng.choice((-1, 1)) * rng.uniform(1.0, 1.4)
            room = 4.2 - cp.arch_height(HALF, SPRING, RISE, abs(du)) - 0.15
            dress.run(t, (u0 + du, 4.2, 0.4), (0, 1), rng.uniform(0.25, 0.4), min(room, rng.uniform(0.8, 1.3)), dress.DARK, 0.55, seed=u0 + i)
    # The two on the parapet, over the garth: hooded, looking down (from the
    # garth they stand against the sky over the west and south ranges' roofs).
    for name, u in (("W", 4.0), ("S", -4.0)):
        dress.figure(Turned(fig, SIDES[name][0]), (u, WALL_TOP + 0.13, 0.12), 0.0, 1.5, colour=statue, bowed=1.0)
        dress.run(Turned(d, SIDES[name][0]), (u, WALL_TOP, 0.4), (0, 1), 0.4, 0.75, dress.DARK, 0.6, seed=u)
    # Cobwebs, small and tucked away (dress.cobweb is a neat fan: in the
    # open it looks hung there): where a rib meets the wall in three
    # places, in the heads of two lights, and one across the niche of the
    # figure that faces the wall, which nobody has touched.
    for name, u, side in (("N", 4.0, 1), ("E", -4.0, -1), ("W", -8.4, 1)):
        dress.cobweb(Turned(d, SIDES[name][0]), (u + side * 0.06, 2.72, BACK + 0.03), (0.0, 0.9, 0.42), (side, 0.25, 0.0), 0.5, seed=int(u) + 9)
    for name, u0, s in (("N", 6.0, 1), BROKEN + (1,)):
        dress.cobweb(Turned(d, SIDES[name][0]), (u0 + s * 0.72, 2.9, 0.0), (-0.3, -0.9, 0.0), (0.7, -0.6, 0.0), 0.3, seed=int(u0) + s, sag=0.1)
    dress.cobweb(Turned(d, SIDES["S"][0]), (-10.0 - NICHE[0], NICHE[2] + 0.1, BACK - 0.02), (0.0, -1.0, 0.0), (0.9, -0.25, 0.0), 0.6, seed=23, sag=0.2)

    # Three abbots' slabs in the east walk's floor, between the two doors.
    grave_slab(d, 9.05, 11.0, -17.0, 0.8, 3.0, 0.5)
    grave_slab(d, 8.95, 11.05, -16.05, 0.86, 7.0, 0.15)
    grave_slab(d, 9.1, 10.95, -15.12, 0.78, 11.0, 0.85)

    # Leaves blown in from the garth (the hawthorn is in its north-east bed):
    # along the low walls, through the open bays, heaped in the north-east
    # corner, and at the feet of the two niches, where nobody sweeps.
    y, leaf = 0.066, Dimmed(d, LEAF, 1.0)
    dress.leaves(leaf, 0.4, 7.6, -25.2, -24.44, y, 90, 1, toward=(0, 1))
    dress.leaves(leaf, -3.5, -0.5, -25.9, -24.44, y, 45, 2, toward=(0, 1))
    dress.leaves(leaf, -3.3, -0.7, -24.4, -23.4, 0.08, 22, 3)
    dress.leaves(leaf, 8.6, 11.52, -27.5, -24.6, y, 120, 4, toward=(1, -1))
    dress.leaves(leaf, 8.44, 9.2, -24.0, -15.6, y, 80, 5, toward=(-1, 0))
    dress.leaves(leaf, 9.2, 10.8, -5.3, -4.5, y, 34, 6, toward=(0, 1))
    dress.leaves(leaf, -11.5, -10.7, -26.9, -25.1, y, 30, 7, toward=(-1, 0))
    dress.leaves(leaf, -11.2, -8.8, -5.2, -4.5, y, 26, 8, toward=(0, 1))
    dress.leaves(leaf, -10.55, -9.45, -4.5, -4.25, 0.07, 14, 11, toward=(0, 1))
    dress.leaves(leaf, 0.5, 7.5, -23.56, -22.9, 0.024, 80, 9, toward=(0, -1))
    dress.leaves(leaf, 6.9, 7.56, -23.4, -15.0, 0.024, 80, 10, toward=(1, 0))
    d.build()
    fig.build(smooth=True)


def arcade():
    porter.reset(301)
    stone, vault, walls = porter.Mesh("Arcade"), porter.Mesh("Vault"), porter.Mesh("BackWalls")
    edges = (-8.4, -4.0, 0.0, 4.0, 8.4)
    for i, (name, (place, open_u, cuts)) in enumerate(SIDES.items()):
        t = Turned(stone, place)
        tint = cp.stone_tint(0.0, WALL_TOP, seed=30.0 + i * 7.0, worn=0.3)
        for k, u0 in enumerate(BAYS):
            bay(t, u0, u0 == open_u, tint, k == 0, k == len(BAYS) - 1, (name, u0) == BROKEN)
        for u in (-4.0, 0.0, 4.0):
            buttress(t, u, cp.stone_tint(0.0, 4.0, seed=50.0 + i * 3.0 + u, worn=0.9))
            shaft(t, u, -0.48, VSPRING)
        # A string course under the parapet, and its coping.
        t.box((-7.6, 4.2, 0.4), (7.6, 4.33, 0.47), STONE, pale(0.78), faces="Zy")
        t.poly([(-7.6, 4.33, 0.47), (7.6, 4.33, 0.47), (7.6, 4.4, 0.4), (-7.6, 4.4, 0.4)], STONE, pale(0.86), facing=(0, 1, 1))
        t.box((-8.47, WALL_TOP, -0.47), (8.47, WALL_TOP + 0.13, 0.48), STONE, pale(0.8), faces="zZyY")
        v = Turned(vault, place)
        for ua, ub in zip(edges, edges[1:]):
            vault_bay(v, ua, ub, BACK, -0.4, ("v0", "v1"))
        for u in edges:
            rib(v, [(u, crown(tt), lerp(BACK, -0.4, (tt + 1.0) * 0.5)) for tt in [-1.0 + k / 8 for k in range(17)]], 0.2, 0.17, pale(0.74))
            corbel(v, u, BACK + 0.02)
        back_wall(Turned(walls, place), cuts, cp.stone_tint(0.0, WALL_TOP, seed=70.0 + i * 5.0, worn=0.25))
    # The four corners: a square bay each, and a shaft on the arcade's corner pier.
    same = Turned(vault, lambda x, y, z: (x, y, z))
    for sx in (-1, 1):
        for sz in (-1, 1):
            xa, xb = sorted((sx * 8.4, sx * 11.58))
            za, zb = sorted((-16.0 + sz * 8.4, -16.0 + sz * 11.58))
            vault_bay(same, xa, xb, za, zb, ("u0" if sx < 0 else "u1", "v0" if sz < 0 else "v1"))
            corbel(same, sx * 11.5, -16.0 + sz * 11.5)
            shaft(Turned(stone, lambda x, y, z: (x, y, z)), sx * 8.47, -16.0 + sz * 8.47, VSPRING)
    stone.build()
    vault.build(smooth=True)
    walls.build()

    # The walks' flags: paler down the middle, where feet have gone.
    floor = porter.Mesh("Floor")
    for ix in range(-12, 12):
        for iz in range(-28, -4):
            x0, z0 = float(ix), float(iz)
            if -8.0 <= x0 and x0 + 1.0 <= 8.0 and -24.0 <= z0 and z0 + 1.0 <= -8.0:
                continue
            pts = [(max(x0, -11.6), 0.056, max(z0, -27.6)), (min(x0 + 1.0, 11.6), 0.056, max(z0, -27.6)),
                   (min(x0 + 1.0, 11.6), 0.056, min(z0 + 1.0, -4.4)), (max(x0, -11.6), 0.056, min(z0 + 1.0, -4.4))]
            cols = []
            for p in pts:
                mid = abs(max(abs(p[0]), abs(p[2] + 16.0)) - 10.0)
                k = lerp(0.95, 0.7, smoothstep(0.3, 1.5, mid)) * (0.9 + 0.12 * fbm(p[0], p[2], 0.35, 2, 8.0))
                cols.append((k, k, k * 0.97, 1.0))
            floor.poly(pts, "flags_worn", cols, facing=(0, 1, 0))
    floor.build()

    # The roof: lead, falling a little to the arcade; and where it runs
    # into the lower ranges (west and south), an upstand.
    roof = porter.Mesh("Roof")
    inner, outer, lo, hi = 8.4, 11.6, 4.9, 5.22
    corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    for (ax, az), (bx, bz) in zip(corners, corners[1:] + corners[:1]):
        steps = 6
        for k in range(steps):
            fa, fb = k / steps, (k + 1) / steps

            def at(f, r, y):
                return (lerp(ax, bx, f) * r, y, -16.0 + lerp(az, bz, f) * r)
            pts = [at(fa, inner, lo), at(fb, inner, lo), at(fb, outer, hi), at(fa, outer, hi)]
            # (Old lead, dull: at 0.8 it was the brightest thing in the abbey from the dormitory's windows.)
            cols = [(0.42 + 0.18 * fbm(p[0], p[2], 0.3, 2, 2.0),) * 3 + (1.0,) for p in pts]
            roof.poly(pts, "lead_roof", cols, facing=(0, 1, 0))
    tint = cp.stone_tint(4.0, 5.5, seed=90.0, worn=0.6)
    cp.slab(roof, (-12.4, 3.95, -28.0), (-11.6, 5.45, -3.6), STONE, tint, faces="xXZY", step=2.0)
    cp.slab(roof, (-12.4, 3.95, -4.4), (12.0, 5.45, -3.6), STONE, tint, faces="XzZY", step=2.0)
    roof.build()
    dressing()
    porter.export("env_cloister_arcade")


# --- the garth ---------------------------------------------------------

MID_Z = -16.0
# Half the garth; the walk round it starts here; half an axial walk; the paved round.
REACH, RING, AXIS, ROUND = 7.6, 5.9, 0.9, 2.7
BOX = (0.42, 0.52, 0.26)
BOX_DARK = (0.2, 0.27, 0.14)
# The yew material is near black: these multiply it up.
YEW = (3.2, 4.0, 2.6)
HERB = srgb(0.42, 0.47, 0.4)
STALK = srgb(0.34, 0.3, 0.2)
GRASS = srgb(0.3, 0.36, 0.18)
PETAL = srgb(0.95, 0.93, 0.84)


def hedge(m, a, b, width=0.38, height=0.42, step=0.45):
    """Clipped box from (x, z) `a` to `b`: flat-topped, a little uneven."""
    length = math.hypot(b[0] - a[0], b[1] - a[1])
    n = max(int(round(length / step)), 1)
    ux, uz = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    px, pz = -uz, ux
    shape = ((-0.5, 0.0), (-0.52, 0.72), (-0.36, 1.0), (0.36, 1.0), (0.52, 0.72), (0.5, 0.0))
    rings = []
    for i in range(n + 1):
        d = length * i / n
        cx, cz = a[0] + ux * d, a[1] + uz * d
        ring = []
        for k, (sx, sy) in enumerate(shape):
            j = 0.035 * fbm(cx * 3.0 + k, cz * 3.0, 1.0, 2, 6.0)
            x, z = cx + px * sx * (width + j), cz + pz * sx * (width + j)
            y = sy * (height + 0.05 * fbm(cx, cz, 0.9, 2, 12.0)) + (j if sy > 0 else 0.0)
            shade = lerp(0.5, 1.0, sy) * (0.85 + 0.3 * fbm(cx * 2.0, cz * 2.0 + k, 1.0, 2, 3.0))
            col = tuple(lerp(BOX_DARK[c], BOX[c], sy) * shade / lerp(0.5, 1.0, sy) for c in range(3)) + (1.0,)
            ring.append(m.vert(x, y, z, col))
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(len(shape) - 1):
            m.face((r0[k], r0[k + 1], r1[k + 1], r1[k]), "box_hedge")
    for ring, flip in ((rings[0], False), (rings[-1], True)):
        m.face(tuple(ring) if flip else tuple(reversed(ring)), "box_hedge")


def blade(m, x, y, z, yaw, lean, height, width, col, tip_k=1.25):
    """One flat blade (the growth material bends it in the wind by its UV's height)."""
    c, s = math.cos(yaw), math.sin(yaw)
    ax, az = -s * width * 0.5, c * width * 0.5
    tx, tz = x + c * lean * height, z + s * lean * height
    root = (col[0] * 0.45, col[1] * 0.45, col[2] * 0.45, 1.0)
    tip = (col[0] * tip_k, col[1] * tip_k, col[2] * tip_k, 1.0)
    a = m.vert(x - ax, y - 0.03, z - az, root, (0.0, 0.0))
    b = m.vert(x + ax, y - 0.03, z + az, root, (1.0, 0.0))
    t = m.vert(tx, y + height, tz, tip, (0.5, height))
    m.face((a, b, t), "growth")
    return tx, y + height, tz


def tuft(m, x, z, size, col, count=(7, 10), y=0.04):
    n = random.randint(*count)
    for i in range(n):
        yaw = math.tau * i / n + random.uniform(-0.5, 0.5)
        blade(m, x + math.cos(yaw) * 0.05, y, z + math.sin(yaw) * 0.05, yaw, random.uniform(0.1, 0.7), size * random.uniform(0.5, 1.0),
              random.uniform(0.025, 0.05) * (0.7 + size), tuple(c * random.uniform(0.75, 1.1) for c in col))


def flower(m, x, z, height, heads=0.12):
    """What is left of a flower in November: a dead stalk or two, some
    broken over, a browned head still on a few."""
    for _ in range(random.randint(1, 3)):
        yaw = random.uniform(0.0, math.tau)
        lean = random.uniform(0.02, 0.25) if random.random() < 0.7 else random.uniform(0.5, 1.1)
        k = random.uniform(0.55, 1.0)
        tx, ty, tz = blade(m, x + random.uniform(-0.05, 0.05), 0.04, z + random.uniform(-0.05, 0.05), yaw, lean,
                           height * random.uniform(0.6, 1.0) / (1.0 + lean), 0.03, (STALK[0] * k, STALK[1] * k, STALK[2] * k), 1.0)
        if random.random() < heads:
            r = random.uniform(0.02, 0.035)
            k = random.uniform(0.16, 0.34)
            col = (PETAL[0] * k, PETAL[1] * k, PETAL[2] * k, 1.0)
            ids = [m.vert(tx + dx * r, ty + 0.01, tz + dz * r, col, (0.5, ty)) for dx, dz in ((-1, 0), (0, -1), (1, 0), (0, 1))]
            m.face(tuple(ids), "growth")


def yew(m, x, z, height, radius):
    """A clipped yew: a cone, grown a little out of true."""
    rows, sides = 6, 10
    rings = []
    for r in range(rows + 1):
        f = r / rows
        y = 0.12 + (height - 0.12) * f
        rad = radius * (1.0 - f) ** 0.8 * (1.0 if r else 0.82)
        ring = []
        for k in range(sides):
            a = math.tau * k / sides + f * 0.6
            j = 1.0 + 0.12 * fbm(x + math.cos(a) * 2.0, y * 1.5 + z, 1.2, 2, 8.0)
            shade = lerp(0.45, 1.1, f) * (0.8 + 0.4 * fbm(a * 1.5 + x, y * 2.0, 1.0, 2, 3.0))
            ring.append(m.vert(x + math.cos(a) * rad * j, y, z + math.sin(a) * rad * j, (YEW[0] * shade, YEW[1] * shade, YEW[2] * shade, 1.0)))
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(sides):
            n = (k + 1) % sides
            m.face((r0[k], r1[k], r1[n], r0[n]), "yew")
    m.tube([(x, 0.0, z), (x, 0.2, z)], [0.07, 0.06], 6, "bark", (0.5, 0.45, 0.4, 1.0))


def ring_wall(m, y0, y1, r0, r1, sides, tint, cx=0.0, cz=MID_Z):
    """A band round the basin from radius r0 at y0 to r1 at y1. Its outside
    is on the right of that line as it is drawn: going up it faces out,
    going down it faces in, going inward at one height it faces up."""
    for i in range(sides):
        a, b = math.tau * i / sides, math.tau * (i + 1) / sides
        pts = [(cx + math.cos(a) * r0, y0, cz + math.sin(a) * r0), (cx + math.cos(b) * r0, y0, cz + math.sin(b) * r0)]
        if r1 > 1e-4:
            pts += [(cx + math.cos(b) * r1, y1, cz + math.sin(b) * r1), (cx + math.cos(a) * r1, y1, cz + math.sin(a) * r1)]
        else:
            pts.append((cx, y1, cz))
        mid = (a + b) * 0.5
        m.poly(pts, STONE, [tint(*p) for p in pts], facing=(math.cos(mid) * (y1 - y0), r0 - r1, math.sin(mid) * (y1 - y0)))


def basin(m):
    """The conduit at the middle: an eight-sided basin on a step, a shaft
    and a bowl in it, the water standing still."""
    tint = cp.stone_tint(0.0, 0.9, seed=5.0, worn=1.0)
    clean = lambda x, y, z: pale(0.78 + 0.1 * fbm(x * 2.0, z * 2.0 + y, 1.0, 2, 4.0))
    ring_wall(m, 0.0, 0.14, 1.66, 1.66, 8, tint)
    ring_wall(m, 0.14, 0.14, 1.66, 1.2, 8, clean)
    ring_wall(m, 0.14, 0.2, 1.3, 1.24, 8, tint)
    ring_wall(m, 0.2, 0.66, 1.2, 1.2, 8, tint)
    ring_wall(m, 0.66, 0.7, 1.2, 1.27, 8, clean)
    ring_wall(m, 0.7, 0.79, 1.27, 1.27, 8, clean)
    ring_wall(m, 0.79, 0.79, 1.27, 0.93, 8, clean)
    ring_wall(m, 0.79, 0.4, 0.93, 0.98, 8, tint)
    cp.disc(m, 0.0, MID_Z, 0.6, 0.98, 8, "water_still", (1, 1, 1))
    ring_wall(m, 0.5, 0.7, 0.3, 0.26, 8, tint)
    ring_wall(m, 0.7, 1.38, 0.19, 0.17, 8, tint)
    ring_wall(m, 0.7, 0.7, 0.26, 0.19, 8, clean)
    ring_wall(m, 1.38, 1.5, 0.17, 0.3, 8, clean)
    ring_wall(m, 1.5, 1.62, 0.3, 0.62, 8, tint)
    ring_wall(m, 1.62, 1.72, 0.62, 0.66, 8, clean)
    ring_wall(m, 1.72, 1.72, 0.66, 0.56, 8, clean)
    ring_wall(m, 1.72, 1.6, 0.56, 0.5, 8, tint)
    cp.disc(m, 0.0, MID_Z, 1.67, 0.56, 8, "water_still", (1, 1, 1))
    ring_wall(m, 1.6, 2.02, 0.09, 0.07, 8, clean)
    ring_wall(m, 2.02, 2.1, 0.07, 0.14, 8, clean)
    ring_wall(m, 2.1, 2.42, 0.14, 0.0, 8, clean)


def garth():
    porter.reset(311)
    ground = porter.Mesh("Ground")
    # Gravel under everything.
    step = 0.95
    n = int(round(2 * REACH / step))
    for i in range(n):
        for j in range(n):
            pts = []
            for di, dj in ((0, 0), (1, 0), (1, 1), (0, 1)):
                x, z = -REACH + 2 * REACH * (i + di) / n, MID_Z - REACH + 2 * REACH * (j + dj) / n
                pts.append((x, 0.014, z))
            cols = []
            for p in pts:
                k = 0.8 + 0.25 * fbm(p[0], p[2], 0.3, 3, 2.0)
                edge = smoothstep(REACH - 0.9, REACH, max(abs(p[0]), abs(p[2] - MID_Z)))
                cols.append((k * lerp(1.0, 0.55, edge), k * lerp(1.0, 0.62, edge), k * lerp(1.0, 0.5, edge), 1.0))
            ground.poly(pts, "gravel_path", cols, facing=(0, 1, 0))
    # The paved round.
    for r0, r1 in ((0.0, 1.0), (1.0, 2.0), (2.0, ROUND)):
        for k in range(20):
            a, b = math.tau * k / 20, math.tau * (k + 1) / 20
            pts = [(math.cos(a) * r0, 0.03, MID_Z + math.sin(a) * r0), (math.cos(b) * r0, 0.03, MID_Z + math.sin(b) * r0),
                   (math.cos(b) * r1, 0.03, MID_Z + math.sin(b) * r1), (math.cos(a) * r1, 0.03, MID_Z + math.sin(a) * r1)]
            if r0 == 0.0:
                pts = pts[1:]
            cols = [(0.72 + 0.2 * fbm(p[0], p[2], 0.5, 2, 6.0),) * 3 + (1.0,) for p in pts]
            ground.poly(pts, "flags_worn", cols, facing=(0, 1, 0))
    # The four beds: turf, a little domed.
    t_in = math.atan2(AXIS, RING)
    t_arc = math.atan2(AXIS, math.sqrt(ROUND * ROUND - AXIS * AXIS))
    angles = sorted(set([t_in, t_arc, math.pi / 4, math.pi / 2 - t_arc, math.pi / 2 - t_in]
                        + [lerp(t_in, math.pi / 2 - t_in, k / 14) for k in range(15)]))
    hedges = porter.Mesh("Hedges")
    for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        def bed(qx, qz, sx=sx, sz=sz):
            return sx * qx, MID_Z + sz * qz

        # The two planted beds (herbs, flowers) are dug earth inside their edging; the other two are lawn.
        planted = sx == sz

        def turf(qx, qz, sx=sx, sz=sz):
            x, z = bed(qx, qz)
            inside = min(qx - AXIS, qz - AXIS, RING - qx, RING - qz, math.hypot(qx, qz) - ROUND)
            y = 0.035 + 0.06 * smoothstep(0.0, 1.4, inside) + 0.015 * fbm(x, z, 0.8, 2, 3.0)
            k = 0.78 + 0.3 * fbm(x, z, 0.25, 3, 5.0)
            return (x, y, z), (k, k, k * 0.95, 1.0), inside

        rows = 6
        for a, b in zip(angles, angles[1:]):
            def span(th, f):
                r_in = max(ROUND, AXIS / max(math.sin(th), 1e-6), AXIS / max(math.cos(th), 1e-6))
                r_out = RING / max(math.cos(th), math.sin(th))
                r = lerp(r_in, r_out, f)
                return turf(r * math.cos(th), r * math.sin(th))
            for k in range(rows):
                quad = []
                for q in (span(a, k / rows), span(b, k / rows), span(b, (k + 1) / rows), span(a, (k + 1) / rows)):
                    if not quad or math.dist(q[0], quad[-1][0]) > 1e-4:
                        quad.append(q)
                if len(quad) > 2 and math.dist(quad[0][0], quad[-1][0]) < 1e-4:
                    quad.pop()
                if len(quad) > 2:
                    bare = planted and sum(q[2] for q in quad) / len(quad) > 0.5
                    cols = [(q[1][0] * 0.5, q[1][0] * 0.47, q[1][0] * 0.42, 1.0) if bare else q[1] for q in quad]
                    ground.poly([q[0] for q in quad], "grave_earth" if bare else "grass_leafy", cols, facing=(0, 1, 0))
        # Its box edging: the two outer sides, the two inner, and round the paved middle.
        e = 0.2
        reach = math.sqrt((ROUND + e) ** 2 - (AXIS + e) ** 2)
        hedge(hedges, bed(AXIS + e, RING - e), bed(RING - e, RING - e))
        hedge(hedges, bed(RING - e, RING - e), bed(RING - e, AXIS + e))
        hedge(hedges, bed(reach, AXIS + e), bed(RING - e, AXIS + e))
        hedge(hedges, bed(AXIS + e, reach), bed(AXIS + e, RING - e))
        ta = math.atan2(AXIS + e, reach)
        arc = [lerp(ta, math.pi / 2 - ta, k / 7) for k in range(8)]
        for a, b in zip(arc, arc[1:]):
            hedge(hedges, bed((ROUND + e) * math.cos(a), (ROUND + e) * math.sin(a)), bed((ROUND + e) * math.cos(b), (ROUND + e) * math.sin(b)))
    # The herb bed (north-west): a knot of low box. The flower bed (south-east): a cross of it.
    knot = [(3.4, 1.7), (5.1, 3.4), (3.4, 5.1), (1.7, 3.4)]
    for a, b in zip(knot, knot[1:] + knot[:1]):
        hedge(hedges, (-a[0], MID_Z - a[1]), (-b[0], MID_Z - b[1]), 0.3, 0.3)
    for a, b in (((1.5, 3.4), (2.6, 3.4)), ((4.2, 3.4), (5.5, 3.4)), ((3.4, 1.5), (3.4, 2.6)), ((3.4, 4.2), (3.4, 5.5))):
        hedge(hedges, (a[0], MID_Z + a[1]), (b[0], MID_Z + b[1]), 0.3, 0.3)
    ground.build(smooth=True)
    hedges.build(smooth=True)

    stone = porter.Mesh("Basin")
    basin(stone)
    stone.build()

    yews = porter.Mesh("Yews")
    yew(yews, -3.4, MID_Z - 3.4, 2.5, 0.62)
    yew(yews, 3.4, MID_Z + 3.4, 2.2, 0.58)
    yews.build(smooth=True)

    growth = porter.Mesh("Growth")
    random.seed(17)

    def in_bed(qx, qz):
        return AXIS + 0.45 < qx < RING - 0.45 and AXIS + 0.45 < qz < RING - 0.45 and math.hypot(qx, qz) > ROUND + 0.45

    # Herbs in the knot, grey-green and low; dead stalks among them.
    for _ in range(170):
        qx, qz = random.uniform(1.2, 5.6), random.uniform(1.2, 5.6)
        if not in_bed(qx, qz) or math.hypot(qx - 3.4, qz - 3.4) < 0.75:
            continue
        if random.random() < 0.6:
            col = tuple(lerp(HERB[c], GRASS[c], random.uniform(0.0, 0.5)) for c in range(3))
            if random.random() < 0.45:
                col = tuple(lerp(col[c], STALK[c], random.uniform(0.5, 0.9)) for c in range(3))
            tuft(growth, -qx, MID_Z - qz, random.uniform(0.2, 0.42), col)
        if random.random() < 0.45:
            flower(growth, -qx, MID_Z - qz, random.uniform(0.4, 0.75), 0.0)
    # The flower bed: what is left standing in November, a browned head still on a few.
    for _ in range(210):
        qx, qz = random.uniform(1.2, 5.6), random.uniform(1.2, 5.6)
        if not in_bed(qx, qz) or math.hypot(qx - 3.4, qz - 3.4) < 0.75:
            continue
        flower(growth, qx, MID_Z + qz, random.uniform(0.35, 0.8))
        if random.random() < 0.25:
            tuft(growth, qx, MID_Z + qz, random.uniform(0.15, 0.3), tuple(lerp(GRASS[c], STALK[c], random.uniform(0.2, 0.8)) for c in range(3)), (4, 6))
    # The two lawns: longer grass against the box, where the scythe doesn't reach.
    for sx, sz in ((1, -1), (-1, 1)):
        for _ in range(150):
            qx, qz = random.uniform(1.15, 5.65), random.uniform(1.15, 5.65)
            edge = min(qx - AXIS, qz - AXIS, RING - qx, RING - qz, math.hypot(qx, qz) - ROUND)
            if edge < 0.42 or edge > 0.42 + abs(random.gauss(0.0, 0.3)):
                continue
            tuft(growth, sx * qx, MID_Z + sz * qz, random.uniform(0.15, 0.32), GRASS, (5, 8))
    # Weeds in the gravel at the foot of the arcade and of the basin's step.
    for _ in range(190):
        along, s, d = random.uniform(-REACH, REACH), random.choice((-1, 1)), REACH - abs(random.gauss(0.0, 0.16)) - 0.02
        x, z = (along, s * d) if random.random() < 0.5 else (s * d, along)
        if fbm(x, z, 0.4, 2, 7.0) < -0.1:
            continue
        tuft(growth, x, MID_Z + z, random.uniform(0.1, 0.26), tuple(lerp(GRASS[c], STALK[c], random.uniform(0.0, 0.7)) for c in range(3)), (4, 7), 0.02)
    growth.build()

    # What the season has left: the hawthorn's leaves under it (it stands at
    # (4.5, -20.4) in cloister.tscn) and blown across the gravel, a scum
    # round the basin's edge with leaves caught in it, stains down the
    # basin's sides and green at its foot.
    litter = porter.Mesh("Litter")
    leaf = Dimmed(litter, LEAF, 1.0)
    rng = random.Random(29)
    for k in range(420):
        r, a = 3.3 * rng.random() ** 0.9, rng.uniform(0.0, math.tau)
        x, z = 4.5 + math.cos(a) * r - 0.3 * r, -20.4 + math.sin(a) * r * 0.9
        if abs(x) > REACH - 0.05 or abs(z - MID_Z) > REACH - 0.05 or math.hypot(x, z - MID_Z) < 1.7:
            continue
        on_turf = turf_or_gravel(x, z) > 0.031
        dress.leaves(leaf, x, x, z, z, turf_or_gravel(x, z) + (0.03 if on_turf else 0.01), 1, 100 + k)
    for k in range(26):
        r, a = rng.uniform(0.4, 0.88), rng.uniform(0.0, math.tau) if k % 3 else rng.uniform(0.2, 1.4)
        dress.leaves(leaf, math.cos(a) * r, math.cos(a) * r, MID_Z + math.sin(a) * r, MID_Z + math.sin(a) * r, 0.607, 1, 400 + k)
    n = 28
    for i in range(n):
        ring = []
        for a in (math.tau * i / n, math.tau * (i + 1) / n):
            # (0.93 is the rim's inner edge at its top: the film runs under it to the basin's wall.)
            reach = 0.1 + 0.3 * max(fbm(math.cos(a) * 1.3, math.sin(a) * 1.3, 1.0, 2, 14.0) + 0.25, 0.0) + (0.22 if 0.2 < a < 1.4 else 0.0)
            ring.append((a, reach))
        (a0, w0), (a1, w1) = ring
        pts = [(math.cos(a0) * 0.97, 0.604, MID_Z + math.sin(a0) * 0.97), (math.cos(a1) * 0.97, 0.604, MID_Z + math.sin(a1) * 0.97),
               (math.cos(a1) * (0.93 - w1), 0.604, MID_Z + math.sin(a1) * (0.93 - w1)), (math.cos(a0) * (0.93 - w0), 0.604, MID_Z + math.sin(a0) * (0.93 - w0))]
        scum = (0.13, 0.15, 0.08)
        litter.poly(pts, dress.GRIME, [scum + (0.75,), scum + (0.75,), scum + (0.0,), scum + (0.0,)], facing=(0, 1, 0))
    face = 1.2 * math.cos(math.pi / 8)
    for k in range(8):
        a, b, mid = math.tau * k / 8, math.tau * (k + 1) / 8, math.tau * (k + 0.5) / 8
        out = (math.cos(mid), math.sin(mid))
        dress.damp(litter, (math.cos(a) * 1.2, MID_Z + math.sin(a) * 1.2), (math.cos(b) * 1.2, MID_Z + math.sin(b) * 1.2), 0.2, out, 0.3, dress.GREEN, 0.6,
                   seed=k * 3.0)
        if k in (0, 3, 5, 6):
            off = rng.uniform(-0.25, 0.25)
            dress.run(litter, (out[0] * face - out[1] * off, 0.66, MID_Z + out[1] * face + out[0] * off), out, rng.uniform(0.22, 0.34), 0.46,
                      dress.GREEN if k % 2 else dress.DARK, 0.7, seed=k)
    litter.build()
    porter.export("env_cloister_garth")


if __name__ == "__main__":
    arcade()
    garth()
