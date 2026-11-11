"""Under the abbey (every night): the crypt under the choir, the passage
under the nave and the foot of the hidden stair under the granary. The
model is in the abbey's own coordinates and is laid over the greybox
(church.tscn and cellar.tscn), which still stops people and shapes the
navmesh but is no longer drawn. Floors are at -4 m; the floors of the
church and the granary overhead are the limit, 3.7 m up.

`env_crypt`:
- Crypt: a vessel 15.2 m by 5.5 m under four low groin vaults with heavy
  ribs, on stub columns against the walls. A tomb recess in each bay of
  the south wall; a niche in the east wall behind the reliquary. North of
  it, behind a wall, the stair down from the choir in its own well; an
  arched alcove at each end of that wall, the east one at the stair's foot.
- Passage: a round tunnel vault 32 m long with an arch every 4 m on
  pilasters, rubble walls, a doorway into the crypt.
- Under the granary: the passage turns south under a groin vault and runs
  3.4 m to the foot of the hidden stair, which climbs in a well of its own
  beside a walled-up arch.
- Floor: damp flags.
- Fittings: iron brackets with burnt-out torches along the walls.
- Dressing (with tools/build/dress.py): ossuary niches in the passage, two
  of them empty; a hooded figure in a niche at the passage's west end and
  one facing the foot of the crypt's stair; effigies on two tombs, the lid
  of a third pushed askew; crosses scratched into the walled-up arch; soot,
  rust, damp, salt, cobwebs, wet flags. None of it has collision: all of it
  is inside a wall's thickness or within 0.12 m of a wall's face.

The walls this adds (the crypt's stair wall, the wall beside the hidden
stair) are solid as blocks in church.tscn and cellar.tscn.

Run: tools/build.sh env_crypt
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
import city_parts as cp
import dress
import env_church as ch
from porter import fbm, lerp, smoothstep

cl = ch.cl
pale = cl.pale
STONE = "stone_church"
ROUGH = "stone_rubble"
IRON = "iron_cart"
F = 0.42
FLOOR, CEIL = -4.0, -0.3
# The crypt's vessel: its north side (the stair wall's face), its vault.
VESSEL_N = -33.9
CSPRING, CRISE = -2.5, 2.0
# The alcoves north of it, and the arches into them.
ALCOVE = (-34.89, 0.69, -2.0)
INTO = (1.5, -2.7, 1.2)
# The passage's vault: half its width, its springing.
PHALF, PSPRING = 1.58, -2.1
# The stone draws dark (by the stills, about as dark as dress.SOOT), and a
# stain is a lit face laid over it, so it must be darker still to show as
# one: dress.py's SOOT and DARK hardly show, its GREEN and RUST read as
# paint, its BONE glows. These are the stains' colours down here.
SOOT = (0.0, 0.0, 0.0)
WET = (0.004, 0.004, 0.004)
MOSS = (0.012, 0.02, 0.009)
RUSTY = (0.1, 0.04, 0.014)
SALT = (0.1, 0.098, 0.09)
DUST = (0.17, 0.17, 0.16)
# How much the film over a niche of bones darkens them.
BONE_DIM = 0.78
N = 8
TS = [-math.cos(math.pi * i / (2 * N)) for i in range(2 * N + 1)]

CRYPT_W = lambda u, y, v: (12.0 + v, y, -32.0 - u)  # v > 0: the crypt, v < 0: the passage


def round_crown(spring, rise):
    """A round (or flattened) arch's height, `tt` of the way from its middle to its edge."""
    return lambda tt: spring + rise * math.sqrt(max(1.0 - min(abs(tt), 1.0) ** 2, 0.0))


def barrel(m, axis, a0, a1, c, half, crown, mat, tint, step=1.0):
    """A tunnel vault along `axis` from a0 to a1, its middle at `c` across."""
    def at(w, t):
        q = c + half * t
        return (w, crown(t), q) if axis == "x" else (q, crown(t), w)

    ws = cp.steps(a0, a1, step)
    for ta, tb in zip(TS, TS[1:]):
        for wa, wb in zip(ws, ws[1:]):
            pts = [at(wa, ta), at(wb, ta), at(wb, tb), at(wa, tb)]
            mid = at((wa + wb) * 0.5, (ta + tb) * 0.5)
            axis_pt = at((wa + wb) * 0.5, 0.0)
            m.poly(pts, mat, [tint(*p) for p in pts], facing=(axis_pt[0] - mid[0], crown(1.0) - 0.4 - mid[1], axis_pt[2] - mid[2]))


def groin(m, ua, ub, va, vb, crown, mat, tint, ribs=False, wall_ribs=()):
    """A groin vault over ua..ub (x) by va..vb (z): two tunnels crossing."""
    cu, hu, cv, hv = (ua + ub) * 0.5, (ub - ua) * 0.5, (va + vb) * 0.5, (vb - va) * 0.5
    low = (cu, crown(1.0) - 1.0, cv)

    def web(pts):
        out = [pts[0]]
        for p in pts[1:]:
            if math.dist(p, out[-1]) > 1e-6:
                out.append(p)
        if len(out) > 2 and math.dist(out[0], out[-1]) < 1e-6:
            out.pop()
        if len(out) >= 3:
            mx, my, mz = (sum(p[i] for p in out) / len(out) for i in range(3))
            m.poly(out, mat, [tint(*p) for p in out], facing=(low[0] - mx, low[1] - my, low[2] - mz))

    for ta, tb in zip(TS, TS[1:]):
        for s in (-1, 1):
            web([(cu + s * hu * abs(ta), crown(ta), cv + hv * ta), (cu + s * hu, crown(ta), cv + hv * ta),
                 (cu + s * hu, crown(tb), cv + hv * tb), (cu + s * hu * abs(tb), crown(tb), cv + hv * tb)])
            web([(cu + hu * ta, crown(ta), cv + s * hv * abs(ta)), (cu + hu * ta, crown(ta), cv + s * hv),
                 (cu + hu * tb, crown(tb), cv + s * hv), (cu + hu * tb, crown(tb), cv + s * hv * abs(tb))])
    if not ribs:
        return
    same = cl.Turned(m, lambda x, y, z: (x, y, z))
    c = pale(0.62)
    for s in (-1, 1):
        cl.rib(same, [(cu + hu * tt, crown(tt), cv + s * hv * tt) for tt in TS], 0.24, 0.2, c)
    for name in wall_ribs:
        fixed = {"v0": va + 0.06, "v1": vb - 0.06}[name]
        cl.rib(same, [(cu + hu * tt, crown(tt), fixed) for tt in TS], 0.12, 0.12, c)
    top = crown(0.0)
    m.tube([(cu, top - 0.3, cv), (cu, top - 0.24, cv), (cu, top - 0.1, cv), (cu, top, cv)], [0.08, 0.24, 0.28, 0.28], 8, STONE, pale(0.55), caps=True)


def ring(m, axis, w, c, half, crown, spring, width=0.4, depth=0.13):
    """An arch across a tunnel at `w` along it, on a pilaster each side."""
    same = cl.Turned(m, lambda x, y, z: (x, y, z))
    pts = [((w, crown(t), c + half * t) if axis == "x" else (c + half * t, crown(t), w)) for t in TS]
    cl.rib(same, pts, width, depth, pale(0.66))
    for s in (-1, 1):
        q0, q1 = sorted((c + s * half, c + s * (half - depth)))
        lo, hi = ((w - width * 0.5, FLOOR, q0), (w + width * 0.5, spring, q1)) if axis == "x" else ((q0, FLOOR, w - width * 0.5), (q1, spring, w + width * 0.5))
        m.box(lo, hi, STONE, pale(0.6), top_color=pale(0.7))
        e = 0.05
        q0, q1 = sorted((c + s * half, c + s * (half - depth - e)))
        lo, hi = ((w - width * 0.5 - e, spring - 0.16, q0), (w + width * 0.5 + e, spring, q1)) if axis == "x" else (
            (q0, spring - 0.16, w - width * 0.5 - e), (q1, spring, w + width * 0.5 + e))
        m.box(lo, hi, STONE, pale(0.72))


def stub(m, x, z, top):
    """A short stout column against a wall, with a block of a cap."""
    c = pale(0.66)
    m.tube([(x, FLOOR, z), (x, FLOOR + 0.22, z), (x, FLOOR + 0.3, z), (x, top - 0.34, z)], [0.3, 0.3, 0.22, 0.22], 10, STONE, c, caps=True)
    m.tube([(x, top - 0.34, z), (x, top - 0.26, z), (x, top - 0.1, z), (x, top, z)], [0.22, 0.26, 0.36, 0.36], 4, STONE, pale(0.74), caps=True)


def reveal(t, v0, v1, half, spring, rise, mat, tint, cx=0.0, y0=0.0, step=1.6):
    """cp.vault for an arch below ground: it turns its faces by heights it
    takes to be above zero, so it is built 10 m up and set down."""
    up = cl.Turned(t, lambda x, y, z: (x, y - 10.0, z))
    cp.vault(up, v0, v1, half, spring + 10.0, rise, mat, tint, cx=cx, y0=y0 + 10.0, step=step)


def wall(m, a, b, y0, y1, out, tint):
    cp.panel(m, a, b, y0, y1, (out[0], 0, out[1]), getattr(tint, "mat", ROUGH), tint, 1.6, 1.2)


def torch(m, x, y, z, ox, oz, soot=True):
    """An iron bracket on the wall and a burnt-out torch in it, with the
    soot its flame left on the wall above (`soot`: on a flat wall)."""
    c = (0.09, 0.09, 0.1, 1.0)
    tip = (x + ox * 0.26, y, z + oz * 0.26)
    m.tube([(x, y - 0.12, z), (x + ox * 0.14, y - 0.08, z + oz * 0.14), tip], [0.016, 0.016, 0.016], 4, IRON, c)
    m.tube([(x, y + 0.14, z), tip], [0.012, 0.012], 4, IRON, c)
    rim = [(tip[0] + math.cos(math.tau * i / 8) * 0.05, tip[1], tip[2] + math.sin(math.tau * i / 8) * 0.05) for i in range(9)]
    m.tube(rim, [0.012] * 9, 4, IRON, c)
    foot = (tip[0] - ox * 0.07, y - 0.34, tip[2] - oz * 0.07)
    head = (tip[0] + ox * 0.09, y + 0.42, tip[2] + oz * 0.09)
    neck = tuple(lerp(foot[i], head[i], 0.68) for i in range(3))
    m.tube([foot, neck], [0.02, 0.026], 6, "wood_medieval", (0.3, 0.26, 0.22, 1.0), caps=True)
    m.tube([neck, tuple(lerp(neck[i], head[i], 0.5) for i in range(3)), head], [0.04, 0.055, 0.03], 6, "wood_medieval", (0.05, 0.045, 0.04, 1.0), caps=True)
    if soot:
        soot_up(m, [(x + ox * dress.PROUD, y + 0.3 + 1.4 * i / 7.0, z + oz * dress.PROUD) for i in range(8)], (oz, 0.0, -ox), (x + ox, y + 1.0, z + oz))


def soot_up(m, pts, across, toward, width=0.6, strength=0.9):
    """The black a flame leaves on the stone over it, as dress.soot but
    black enough to show on dark stone, and for a surface that need not be
    a flat wall: `pts` climb it from the flame, `across` is the level
    direction over it, `toward` a point it faces."""
    us = [width * (i / 6.0 - 0.5) * 1.6 for i in range(7)]
    n = len(pts) - 1

    def alpha(u, j):
        t = j / n
        spread = width * (0.45 + 0.55 * t)
        return max(0.0, strength * (1.0 - t) ** 1.1 * max(0.0, 1.0 - (u / spread) ** 2) * (0.3 + 0.7 * smoothstep(0.0, 0.14, t)))

    for j in range(n):
        for ua, ub in zip(us, us[1:]):
            corners = [(ua, j), (ub, j), (ub, j + 1), (ua, j + 1)]
            cols = [SOOT + (alpha(u, k),) for u, k in corners]
            if max(c[3] for c in cols) < 0.01:
                continue
            quad = [tuple(pts[k][i] + across[i] * u for i in range(3)) for u, k in corners]
            mid = [sum(q[i] for q in quad) / 4.0 for i in range(3)]
            m.poly(quad, dress.GRIME, cols, facing=tuple(toward[i] - mid[i] for i in range(3)))


def barrel_soot(m, x, y, z, ox, oz, half, spring):
    """The soot over a torch at (x, y, z) on the wall of a round tunnel vault."""
    r = half - dress.PROUD
    a0 = math.asin(min((y + 0.3 - spring) / half, 0.9))
    pts = []
    for i in range(8):
        a = a0 + 1.4 / half * i / 7.0
        pts.append((x + ox * half - ox * r * math.cos(a), spring + r * math.sin(a), z + oz * half - oz * r * math.cos(a)))
    soot_up(m, pts, (oz, 0.0, -ox), (x + ox * half, spring, z + oz * half))


def local(m, a, out):
    """A wall's own space from the point (x, z) `a` on its face: x along
    it, y the abbey's, z out of it. Returns it and its tint-space."""
    n = math.hypot(out[0], out[1])
    ox, oz = out[0] / n, out[1] / n
    return dress.Placed(m, (a[0], 0.0, a[1]), math.atan2(ox, oz)), (lambda x, y, z: (a[0] + x * oz + z * ox, y, a[1] - x * ox + z * oz))


def recess(t, c, half, sill, spring, rise, deep, back=0.14, black=False, band=True, ledge=True):
    """An arched recess `deep` into a wall's face (z = 0 in its own space),
    its middle at `c` along it: its sides darkening inward, its back, its
    sill, a band round it."""
    fade = lambda x, y, z: pale(lerp(back, 0.55, smoothstep(-deep, 0.0, z)))
    reveal(t, -deep, 0.0, half, spring, rise, STONE, fade, cx=c, y0=sill, step=deep)
    shape = [(c + half, sill)] + cp.arch_profile(half, spring, rise, 8, c) + [(c - half, sill)]
    t.poly([(x, y, -deep) for x, y in shape], "window_dark" if black else STONE, pale(back), facing=(0, 0, 1))
    t.poly([(c - half, sill, -deep), (c + half, sill, -deep), (c + half, sill, 0.0), (c - half, sill, 0.0)], STONE,
           [pale(back), pale(back), pale(0.6), pale(0.6)], facing=(0, 1, 0))
    if band:
        cp.arch_band(t, 0.0, half, spring, rise, 0.1, 0.04, (0, 0, 1), STONE, pale(0.62), cx=c, y0=sill)
    if ledge:
        t.box((c - half - 0.1, sill - 0.09, 0.0), (c + half + 0.1, sill, 0.06), STONE, pale(0.68), faces="xXZyY")


def niched(m, a, b, y0, y1, out, tint, niches):
    """wall() from a to b with arched recesses in it. Each of `niches` is
    ((x, z) of its middle, half, sill, spring, rise, deep, then recess()'s
    options). Returns the wall's own space and each recess's middle in it."""
    ox, oz = out
    if (b[0] - a[0]) * oz - (b[1] - a[1]) * ox < 0.0:
        a, b = b, a
    t, world = local(m, a, out)
    mat = getattr(tint, "mat", ROUGH)
    tl = lambda x, y, z: tint(*world(x, y, z))
    length = math.hypot(b[0] - a[0], b[1] - a[1])
    spots = sorted((((at[0] - a[0]) * oz - (at[1] - a[1]) * ox, i, rest) for i, (at, *rest) in enumerate(niches)))
    u, mids = 0.0, [0.0] * len(niches)
    for c, i, (half, sill, spring, rise, deep, *opts) in spots:
        m0, m1 = max(c - half - 0.25, u), min(c + half + 0.25, length)
        cp.panel(t, (u, 0.0), (m0, 0.0), y0, y1, (0, 0, 1), mat, tl, 1.6, 1.2)
        cp.panel(t, (m0, 0.0), (m1, 0.0), y0, sill, (0, 0, 1), mat, tl, 1.6, 1.2)
        cp.arch_wall(t, 0.0, m0, m1, sill, y1, half, spring, rise, (0, 0, 1), mat, tl, cx=c)
        recess(t, c, half, sill, spring, rise, deep, *opts)
        u, mids[i] = m1, c
    cp.panel(t, (u, 0.0), (length, 0.0), y0, y1, (0, 0, 1), mat, tl, 1.6, 1.2)
    return t, mids


def onto(t, mesh):
    """The wall's own space `t` (from local() or niched()), for another mesh."""
    return dress.Placed(mesh, t.origin, math.atan2(t.s, t.c))


def dust_web(m, corner, a, b, size, seed=0):
    """An old web across a corner, grey with dust: a ragged veil between the
    edge directions `a` and `b`, thick at the corner and thinning out, on a
    few threads. (dress.cobweb draws a whole clean orb web.)"""
    rng = random.Random(seed)
    unit = lambda v: tuple(q / (math.sqrt(sum(k * k for k in v)) or 1.0) for q in v)
    a, b = unit(a), unit(b)
    n = 7
    tips = []
    for i in range(n):
        f = i / (n - 1.0)
        d = unit(tuple(lerp(a[k], b[k], f) for k in range(3)))
        r = size * (rng.uniform(0.5, 1.0) if 0 < i < n - 1 else 1.0)
        tips.append((corner[0] + d[0] * r, corner[1] + d[1] * r - 0.14 * r * math.sin(math.pi * f), corner[2] + d[2] * r))
    grey = DUST
    for p, q in zip(tips, tips[1:]):
        m.poly([corner, p, q], dress.WEB, [grey + (0.4,), grey + (rng.uniform(0.03, 0.16),), grey + (rng.uniform(0.03, 0.16),)])
    for i in (0, 3, 6):
        tip = tips[i]
        m.poly([corner, (tip[0], tip[1] + 0.004, tip[2]), (tip[0], tip[1] - 0.004, tip[2])], dress.WEB, grey + (0.32,))


def web_in(t, c, half, spring, rise, seed, side=-1, face=0.0, size=None):
    """A web across an upper corner of a recess in the wall face at z = `face`."""
    dust_web(t, (c + side * (half + 0.02), spring + rise * 0.8, face - 0.04), (-side, 0.12, 0.0), (-side * 0.1, -1.0, 0.0), size or half * 1.25, seed)


def monk(m, p, yaw=0.0, height=1.75, colour=(0.47, 0.46, 0.43), bowed=0.0):
    """A standing hooded figure in stone, its hands in its sleeves and
    nothing in its hood, on `p` and facing `yaw` (0: toward +z). As
    dress.figure, with shoulders and a cowl, so it reads as a man."""
    c = colour + (1.0,)
    dark = tuple(q * 0.55 for q in colour) + (1.0,)
    mid = tuple(q * 0.8 for q in colour) + (1.0,)
    t = dress.Placed(m, p, yaw, height / 1.75)
    t.tube([(0, 0.0, 0), (0, 0.05, 0), (0, 0.6, 0), (0, 1.15, 0), (0, 1.36, 0), (0, 1.45, 0), (0, 1.5, 0)], [0.29, 0.285, 0.25, 0.235, 0.25, 0.19, 0.09], 10, STONE,
           [dark, dark, mid, c, c, c, c], squash=(1.0, 0.62))
    # The cowl's cape over the shoulders.
    t.tube([(0, 1.2, 0.005), (0, 1.3, 0.005), (0, 1.47, 0.0)], [0.272, 0.268, 0.16], 10, STONE, [dark, c, c], squash=(1.0, 0.66))
    # The hood, leaning with the head.
    lean = bowed * 0.1
    t.tube([(0, 1.43, 0.0), (0, 1.5, lean * 0.3), (0, 1.6, lean * 0.8), (0, 1.7, lean * 0.9), (0, 1.77, lean * 0.6 - 0.02), (0, 1.8, lean * 0.4 - 0.04)],
           [0.1, 0.12, 0.128, 0.108, 0.056, 0.01], 10, STONE, c, caps=True, squash=(1.0, 1.05))
    zf, yf = 0.128 * 1.05 + lean * 0.8 - 0.012, 1.585 - bowed * 0.035
    t.poly([(math.cos(math.tau * i / 10) * 0.066, yf + math.sin(math.tau * i / 10) * 0.105, zf + 0.012 * abs(math.sin(math.tau * i / 10))) for i in range(10)], "window_dark",
           (0.0, 0.0, 0.0, 1.0), facing=(0, 0, 1))
    # The arms, the hands lost in the sleeves.
    t.tube([(-0.232, 1.33, 0.02), (-0.262, 1.08, 0.07), (-0.09, 0.98, 0.165), (0.09, 0.98, 0.165), (0.262, 1.08, 0.07), (0.232, 1.33, 0.02)],
           [0.07, 0.085, 0.076, 0.076, 0.085, 0.07], 6, STONE, [c, mid, mid, mid, mid, c])
    # The sleeves' ends hanging from the wrists.
    t.tube([(0, 1.0, 0.15), (0, 0.82, 0.14), (0, 0.6, 0.115)], [0.125, 0.11, 0.07], 6, STONE, [mid, mid, dark], caps=True, squash=(1.0, 0.42))


def scratches(t, cx, cy, z, half_w, half_h, count=46, seed=7):
    """A small cross scratched into the stone, over and over, in one patch."""
    rng = random.Random(seed)

    def stroke(a, b, w, col):
        dx, dy = b[0] - a[0], b[1] - a[1]
        k = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / k * w, dx / k * w
        t.poly([(a[0] - nx, a[1] - ny, z), (a[0] + nx, a[1] + ny, z), (b[0] + nx * 0.5, b[1] + ny * 0.5, z), (b[0] - nx * 0.5, b[1] - ny * 0.5, z)], dress.GRIME, col,
               facing=(0, 0, 1))

    for _ in range(count):
        x = cx + max(-1.0, min(1.0, rng.gauss(0.0, 0.42))) * half_w
        y = cy + max(-1.0, min(1.0, rng.gauss(0.0, 0.42))) * half_h
        h, lean = rng.uniform(0.05, 0.13), rng.gauss(0.0, 0.16)
        k = rng.uniform(0.17, 0.27)
        col = (k, k * 0.97, k * 0.9, rng.uniform(0.45, 0.9))
        up, over = (math.sin(lean), math.cos(lean)), (math.cos(lean), -math.sin(lean))
        stroke((x, y), (x + up[0] * h, y + up[1] * h), 0.0032, col)
        mx, my, arm = x + up[0] * h * 0.66, y + up[1] * h * 0.66, h * rng.uniform(0.24, 0.36)
        stroke((mx - over[0] * arm, my - over[1] * arm), (mx + over[0] * arm, my + over[1] * arm), 0.0032, col)


def cheek(m, axis, q0, q1, w0, w1, wtop, inner):
    """The stone beside a greybox stair that is narrower than its well: it
    fills q0..q1 across, from the stair's foot at w0 up along its nosings
    to its top at w1."""
    rise, steps_n = 4.05, 16
    y0, y1 = FLOOR + rise / steps_n, FLOOR + rise
    at = (lambda q, y, w: (w, y, q)) if axis == "x" else (lambda q, y, w: (q, y, w))
    c = pale(0.5)
    m.poly([at(q0, y0, w0), at(q1, y0, w0), at(q1, y1, wtop), at(q0, y1, wtop)], STONE, [pale(0.42), pale(0.42), pale(0.6), pale(0.6)], facing=(0, 1, 0))
    m.poly([at(q0, y1, wtop), at(q1, y1, wtop), at(q1, y1, w1), at(q0, y1, w1)], STONE, pale(0.6), facing=(0, 1, 0))
    front = at(0.0, 0.0, w0 - w1)
    m.poly([at(q0, FLOOR, w0), at(q1, FLOOR, w0), at(q1, y0, w0), at(q0, y0, w0)], STONE, c, facing=front)
    side = at(inner - (q0 + q1) * 0.5, 0.0, 0.0)
    m.poly([at(inner, FLOOR, w0), at(inner, y0, w0), at(inner, y1, wtop), at(inner, y1, w1), at(inner, FLOOR, w1)], STONE, c, facing=side)


def wet(dr, x, z, rx, rz, seed):
    """Flags left wet where water stands and dries: a dark patch, darkest in
    its middle. (The `water_still` material shows black down here, with no
    sky to mirror: a pool of it reads as a hole in the floor.)"""
    y = FLOOR + 0.059
    rim = []
    for i in range(12):
        a = math.tau * i / 12
        k = 0.7 + 0.5 * fbm(math.cos(a) * 0.8 + seed, math.sin(a) * 0.8, 1.0, 2, seed)
        rim.append((math.cos(a) * rx * k, math.sin(a) * rz * k))
    core, mid, dry = WET + (0.62,), WET + (0.5,), WET + (0.0,)
    for (ax, az), (bx, bz) in zip(rim, rim[1:] + rim[:1]):
        a, b, a2, b2 = (x + ax * 0.55, z + az * 0.55), (x + bx * 0.55, z + bz * 0.55), (x + ax, z + az), (x + bx, z + bz)
        dr.poly([(x, y, z), (a[0], y, a[1]), (b[0], y, b[1])], dress.GRIME, [core, mid, mid], facing=(0, 1, 0))
        dr.poly([(a[0], y, a[1]), (b[0], y, b[1]), (b2[0], y, b2[1]), (a2[0], y, a2[1])], dress.GRIME, [mid, mid, dry, dry], facing=(0, 1, 0))


def iron_ring(m, dr, x, y, z, ox, oz):
    """A ring hanging from a staple in the wall, and the rust under it."""
    c = (0.08, 0.075, 0.07, 1.0)
    ax, az = -oz, ox
    m.tube([(x - ax * 0.03, y, z - az * 0.03), (x - ax * 0.03 + ox * 0.04, y, z - az * 0.03 + oz * 0.04), (x + ax * 0.03 + ox * 0.04, y, z + az * 0.03 + oz * 0.04),
            (x + ax * 0.03, y, z + az * 0.03)], [0.009] * 4, 4, IRON, c)
    loop = [(x + ax * math.sin(math.tau * i / 10) * 0.075 + ox * 0.022, y - 0.07 + math.cos(math.tau * i / 10) * 0.075, z + az * math.sin(math.tau * i / 10) * 0.075 + oz * 0.022)
            for i in range(11)]
    m.tube(loop, [0.011] * 11, 4, IRON, c)
    dress.run(dr, (x, y - 0.02, z), (ox, oz), 0.16, 1.0, RUSTY, 0.75, seed=x)
    dress.patch(dr, (x, y - 0.06, z), (ox, oz), 0.3, 0.3, RUSTY, 0.45, seed=x)


def flags(m, x0, x1, z0, z1, seed):
    """A floor of damp flags, cut small so its stains can vary."""
    y = FLOOR + 0.056
    xs, zs = cp.steps(x0, x1, 1.0), cp.steps(z0, z1, 1.0)
    for xa, xb in zip(xs, xs[1:]):
        for za, zb in zip(zs, zs[1:]):
            pts = [(xa, y, za), (xb, y, za), (xb, y, zb), (xa, y, zb)]
            cols = []
            for p in pts:
                k = 0.42 + 0.3 * fbm(p[0], p[2], 0.3, 3, seed)
                cols.append((k, k, k * 0.97, 1.0))
            m.poly(pts, "flags_worn", cols, facing=(0, 1, 0))


def crypt(m, v, fit, dr, carved):
    ccrown = round_crown(CSPRING, CRISE)
    tint = cp.stone_tint(FLOOR, CEIL + 2.0, clean=(0.74, 0.72, 0.68), seed=5.0, worn=0.0)
    tint.mat = STONE
    web = lambda x, y, z: cp.rgba((0.8, 0.79, 0.75), lerp(1.0, 0.6, smoothstep(CSPRING, CSPRING + CRISE, y)) * (0.9 + 0.14 * fbm(x, z, 0.5, 2, 3.0)))
    edges = [12.0 + F, 16.2, 20.0, 23.8, 28.0 - F]
    centres = [(a + b) * 0.5 for a, b in zip(edges, edges[1:])]

    # The south wall: a tomb recess in each bay.
    t = cl.Turned(m, ch.SOUTH)
    tc, td = cl.Turned(carved, ch.SOUTH), cl.Turned(dr, ch.SOUTH)
    half, spring, rise, deep = 1.05, -3.2, 0.8, 0.34
    figure_c = (0.47, 0.46, 0.43)
    for i, ((xa, xb), xc) in enumerate(zip(zip(edges, edges[1:]), centres)):
        uc = -xc
        kind = ("effigy", "cross", "ajar", "effigy")[i]
        cp.arch_wall(t, F, -xb, -xa, FLOOR, CEIL, half, spring, rise, (0, 0, 1), STONE, tint, cx=uc)
        reveal(t, F - deep, F, half, spring, rise, STONE, lambda x, y, z: pale(0.5), cx=uc, y0=FLOOR, step=0.5)
        shape = [(uc + half, FLOOR)] + cp.arch_profile(half, spring, rise, 8, uc) + [(uc - half, FLOOR)]
        t.poly([(x, y, F - deep) for x, y in shape], STONE, pale(0.36), facing=(0, 0, 1))
        cp.arch_band(t, F, half, spring, rise, 0.12, 0.05, (0, 0, 1), STONE, pale(0.7), cx=uc)
        # The tomb: a chest and its lid. On the lid a cross cut in relief, or
        # an effigy; one lid has been pushed askew, and it is black under it.
        # The recess's own floor, which shows past the chest's ends.
        t.poly([(uc - half, FLOOR + 0.056, F - deep), (uc + half, FLOOR + 0.056, F - deep), (uc + half, FLOOR + 0.056, F), (uc - half, FLOOR + 0.056, F)], "flags_worn",
               (0.3, 0.3, 0.29, 1.0), facing=(0, 1, 0))
        t.box((uc - 0.9, FLOOR, F - deep + 0.02), (uc + 0.9, FLOOR + 0.52, F - 0.03), STONE, pale(0.55), top_color=pale(0.7), faces="xXZ")
        if kind == "ajar":
            t.poly([(uc - 0.9, FLOOR + 0.515, F - deep + 0.02), (uc + 0.9, FLOOR + 0.515, F - deep + 0.02), (uc + 0.9, FLOOR + 0.515, F - 0.03),
                    (uc - 0.9, FLOOR + 0.515, F - 0.03)], "window_dark", (0.0, 0.0, 0.0, 1.0), facing=(0, 1, 0))
            # Swung about its east end: its west end stands 0.1 m out from the wall.
            lid = dress.Placed(t, (uc - 0.96, FLOOR + 0.52, F - deep + 0.01), -0.05)
            lid.box((0.0, 0.0, 0.0), (1.92, 0.1, 0.35), STONE, pale(0.74), faces="xXzZyY")
            lid.box((0.36, 0.1, 0.14), (1.56, 0.12, 0.19), STONE, pale(0.86), faces="xXzZY")
            lid.box((1.21, 0.1, 0.05), (1.26, 0.12, 0.28), STONE, pale(0.86), faces="xXzZY")
            continue
        t.box((uc - 0.96, FLOOR + 0.52, F - deep + 0.01), (uc + 0.96, FLOOR + 0.62, F + 0.02), STONE, pale(0.78), faces="xXZyY")
        if kind == "cross":
            t.box((uc - 0.6, FLOOR + 0.62, F - 0.19), (uc + 0.6, FLOOR + 0.64, F - 0.14), STONE, pale(0.9), faces="xXzZY")
            t.box((uc + 0.25, FLOOR + 0.62, F - 0.28), (uc + 0.3, FLOOR + 0.64, F - 0.05), STONE, pale(0.9), faces="xXzZY")
        else:
            dress.effigy(tc, (uc, FLOOR + 0.62, F - 0.155), math.pi, 1.55, STONE, figure_c)

    # The east wall: a niche behind the reliquary; the east alcove's end.
    t = cl.Turned(m, ch.EAST_W)
    ua, ub, uc = VESSEL_N + 32.0, 4.0 - F, 0.84
    half, sill, spring, rise, deep = 1.15, -3.0, -2.3, 1.0, 0.36
    cp.panel(t, (ua, F), (ub, F), FLOOR, sill, (0, 0, 1), STONE, tint, 1.6, 1.2)
    cp.arch_wall(t, F, ua, ub, sill, CEIL, half, spring, rise, (0, 0, 1), STONE, tint, cx=uc)
    reveal(t, F - deep, F, half, spring, rise, STONE, lambda x, y, z: pale(0.55), cx=uc, y0=sill, step=0.5)
    shape = [(uc + half, sill)] + cp.arch_profile(half, spring, rise, 8, uc) + [(uc - half, sill)]
    t.poly([(x, y, F - deep) for x, y in shape], STONE, pale(0.36), facing=(0, 0, 1))
    t.poly([(uc - half, sill, F - deep), (uc + half, sill, F - deep), (uc + half, sill, F), (uc - half, sill, F)], STONE, pale(0.8), facing=(0, 1, 0))
    t.box((uc - half - 0.1, sill - 0.12, F), (uc + half + 0.1, sill, F + 0.08), STONE, pale(0.8), faces="xXZyY")
    cp.arch_band(t, F, half, spring, rise, 0.14, 0.06, (0, 0, 1), STONE, pale(0.72), cx=uc, y0=sill)
    # The east alcove's end, which the stair comes down facing: a hooded figure in a niche.
    nt, (nc,) = niched(m, (28.0 - F, -36.0 + F), (28.0 - F, -34.2), FLOOR, CEIL, (-1, 0), tint, [((28.0 - F, ALCOVE[0]), 0.38, FLOOR + 0.4, FLOOR + 1.72, 0.38, 0.3, 0.1)])
    monk(onto(nt, carved), (nc, FLOOR + 0.4, -0.15), 0.0, 1.42, figure_c)

    # The west wall: the door to the passage, on both its sides; the west alcove's end.
    t = cl.Turned(m, CRYPT_W)
    door = [(-2.0, 0.47, FLOOR, FLOOR + 2.03)]
    ch.face(t, 1, -4.0 + F, -(VESSEL_N + 32.0), FLOOR, CEIL, tint, door)
    ch.face(t, 1, 34.2 - 32.0, 4.0 - F, FLOOR, CEIL, tint)
    ch.face(t, -1, -4.0 + F, -F, FLOOR, CEIL, tint, door)

    # The stair wall: an arch into the alcove at each end, solid between.
    half, spring, rise = INTO
    for z, s in ((VESSEL_N, 1), (-34.2, -1)):
        x_end = 23.8 if s > 0 else 24.0
        cp.arch_wall(m, z, edges[0], 16.2, FLOOR, CEIL, half, spring, rise, (0, 0, s), STONE, tint, cx=centres[0])
        cp.arch_wall(m, z, x_end, edges[4], FLOOR, CEIL, half, spring, rise, (0, 0, s), STONE, tint, cx=centres[3])
        cp.arch_band(m, z, half, spring, rise, 0.14, 0.05, (0, 0, s), STONE, pale(0.7), cx=centres[0])
        cp.arch_band(m, z, half, spring, rise, 0.14, 0.05, (0, 0, s), STONE, pale(0.7), cx=centres[3])
    for xc in (centres[0], centres[3]):
        reveal(m, -34.2, VESSEL_N, half, spring, rise, STONE, lambda x, y, z: pale(0.6), cx=xc, y0=FLOOR, step=0.4)
    wall(m, (16.2, VESSEL_N), (23.8, VESSEL_N), FLOOR, CEIL, (0, 1), tint)
    # The stair's well, up to the church's floor.
    # (Above the church floor's underside the church's own lip lines the well.)
    wall(m, (16.5, -34.2), (24.0, -34.2), FLOOR, CEIL, (0, -1), tint)
    wall(m, (12.0 + F, -36.0 + F), (28.0 - F, -36.0 + F), FLOOR, CEIL, (0, 1), tint)
    wall(m, (16.2, -36.0 + F), (16.2, -34.2), FLOOR, CEIL, (-1, 0), tint)
    # The stair is narrower than its well: the stone beside it, and the
    # underside of the church's floor where it oversails the well's wall.
    cheek(m, "x", -36.0 + F, -35.4, 24.0, 18.0, 18.375, -35.4)
    m.poly([(18.0, CEIL, -36.0 + F), (24.0, CEIL, -36.0 + F), (24.0, CEIL, -35.4), (18.0, CEIL, -35.4)], STONE, pale(0.4), facing=(0, -1, 0))
    # The alcoves: a tunnel vault each; the east one opens to the well through an arch.
    c, ahalf, aspring = ALCOVE
    acrown = round_crown(aspring, ahalf)
    barrel(v, "x", edges[0], 16.2, c, ahalf, acrown, STONE, web, 0.8)
    barrel(v, "x", 24.0, edges[4], c, ahalf, acrown, STONE, web, 0.8)
    cp.arch_wall(m, 24.0, -36.0 + F, -34.2, FLOOR, CEIL, ahalf, aspring, ahalf, (-1, 0, 0), STONE, tint, cx=c, along="z")

    # The vessel's vault and what it stands on.
    za, zb = VESSEL_N, -28.0 - F
    for xa, xb in zip(edges, edges[1:]):
        groin(v, xa, xb, za, zb, ccrown, STONE, web, ribs=True, wall_ribs=("v0", "v1"))
    same = cl.Turned(v, lambda x, y, z: (x, y, z))
    for x in edges[1:-1]:
        cl.rib(same, [(x, ccrown(tt), lerp(za, zb, (tt + 1.0) * 0.5)) for tt in TS], 0.36, 0.24, pale(0.6))
        stub(m, x, za + 0.04, CSPRING)
        stub(m, x, zb - 0.04, CSPRING)
    for x in (edges[0] + 0.1, edges[4] - 0.1):
        for z in (za + 0.1, zb - 0.1):
            stub(m, x, z, CSPRING)
    # Torches: two on the ribs' feet (their soot up the ribs), two on the east wall.
    rib_at = lambda tt: (20.0, ccrown(tt), lerp(za, zb, (tt + 1.0) * 0.5))
    for z, oz in ((zb, -1), (za, 1)):
        torch(fit, 20.0, FLOOR + 1.95, z + oz * 0.3, 0, oz, soot=False)
        pts = []
        for i in range(8):
            tt = -oz * lerp(0.86, 0.3, i / 7.0)
            pa, p, pb = rib_at(tt - 0.01), rib_at(tt), rib_at(tt + 0.01)
            ty, tz = pb[1] - pa[1], pb[2] - pa[2]
            k = math.hypot(ty, tz) * (-1.0 if tz > 0 else 1.0)
            pts.append((20.0, p[1] + tz / k * 0.25, p[2] - ty / k * 0.25))
        soot_up(dr, pts, (1.0, 0.0, 0.0), (20.0, FLOOR + 1.0, (za + zb) * 0.5), width=0.2)
    for u in (-0.75, 2.45):
        torch(fit, 28.0 - F, FLOOR + 1.95, -32.0 + u, -1, 0)
        dress.run(dr, (28.0 - F, FLOOR + 1.84, -32.0 + u), (-1, 0), 0.14, 0.9, RUSTY, 0.7, seed=u)

    # Iron in the stair wall: a ring on a staple, rust under it.
    iron_ring(fit, dr, centres[1], FLOOR + 1.05, VESSEL_N, 0, 1)
    # Damp at the walls' feet, runs from the wall heads and the niche's sill, salt.
    foot = FLOOR + 0.056
    dress.damp(dr, (16.5, VESSEL_N), (23.5, VESSEL_N), foot, (0, 1), 0.8, colour=MOSS, seed=1.0)
    dress.damp(dr, (28.0 - F, VESSEL_N), (28.0 - F, zb), foot, (-1, 0), 0.8, colour=MOSS, seed=2.0)
    dress.damp(dr, (12.0 + F, VESSEL_N), (12.0 + F, -30.65), foot, (1, 0), 0.8, colour=MOSS, seed=3.0)
    for xa, xb in ((15.4, 17.0), (19.2, 20.8), (23.0, 24.6)):
        dress.damp(dr, (xa, zb), (xb, zb), foot, (0, -1), 0.7, colour=MOSS, seed=xa)
    for x, top, length in ((17.2, -1.1, 1.7), (22.4, -1.0, 2.0), (23.1, -1.4, 1.2)):
        dress.run(dr, (x, top, VESSEL_N), (0, 1), 0.3, length, WET, 0.55, seed=x)
    for z in (-31.75, -30.5):
        dress.run(dr, (28.0 - F, -3.13, z), (-1, 0), 0.26, 0.8, WET, 0.5, seed=z)
    dress.patch(dr, (21.1, FLOOR + 1.3, VESSEL_N), (0, 1), 1.3, 0.9, SALT, 0.4, seed=5.0)
    wet(dr, 22.5, -33.1, 1.0, 0.6, 3.0)
    # The west alcove, where nobody goes: its floor wet, damp higher up its walls, webs in its corners.
    c, ahalf, aspring = ALCOVE
    dress.damp(dr, (12.0 + F, -36.0 + F), (16.2, -36.0 + F), foot, (0, 1), 1.2, strength=0.65, colour=MOSS, seed=6.0)
    dress.damp(dr, (12.0 + F, -36.0 + F), (12.0 + F, -34.2), foot, (1, 0), 1.2, strength=0.65, colour=MOSS, seed=7.0)
    wet(dr, 13.7, c, 1.3, 0.75, 8.0)
    dust_web(dr, (12.0 + F + 0.01, aspring + 0.1, -36.0 + F + 0.01), (1.0, -0.45, 0.03), (0.03, -0.45, 1.0), 0.8, 1)
    dust_web(dr, (12.0 + F + 0.01, aspring + 0.1, -34.21), (1.0, -0.45, -0.03), (0.03, -0.45, -1.0), 0.7, 2)
    # A web in the corner of the recess whose lid is askew.
    web_in(td, -centres[2], 1.05, -3.2, 0.8, 3, side=1, face=F, size=0.7)


def passage(m, v, fit, dr, carved):
    pcrown = round_crown(PSPRING, PHALF)
    tint = cp.stone_tint(FLOOR, CEIL + 1.0, clean=(0.72, 0.7, 0.66), seed=17.0, worn=0.5)
    web = lambda x, y, z: cp.rgba((0.74, 0.72, 0.68), lerp(1.0, 0.62, smoothstep(PSPRING, PSPRING + PHALF, y)) * (0.86 + 0.2 * fbm(x, z, 0.5, 2, 6.0)))
    zn, zs, xw, xe = -32.0 + F, -28.0 - F, -20.0 + F, -16.0 - F
    foot = FLOOR + 0.056
    # The long walls: an ossuary niche in the bays that have no torch, and
    # one in the end bay that the hidden stair comes down facing. Two are
    # empty and black.
    sill, nspring, nhalf, deep = FLOOR + 0.85, FLOOR + 1.3, 0.42, 0.3
    north = [(-18.0, False), (-10.0, False), (-2.0, False), (6.0, True)]
    south = [(-10.0, True), (-2.0, False), (6.0, False)]
    for z, oz, spots, a in ((zn, 1, north, (xw, zn)), (zs, -1, south, (xe, zs))):
        t, mids = niched(m, a, (12.0 - F, z), FLOOR, CEIL, (0, oz), tint, [((x, z), nhalf, sill, nspring, nhalf, deep, 0.1, black) for x, black in spots])
        for (x, black), c in zip(spots, mids):
            if black:
                web_in(onto(t, dr), c, nhalf, nspring, nhalf, int(x) + 20, side=-oz)
            else:
                dress.bones(onto(t, carved), (c - nhalf + 0.03, -deep + 0.02), (c + nhalf - 0.03, -deep + 0.02), sill, (0, 1), rows=2, skulls=True, seed=int(x) + 40 + oz,
                            depth=0.23)
                # dress.BONE is the brightest thing down here by the lantern: a film of dirt across the niche's mouth.
                shape = [(c + nhalf, sill)] + cp.arch_profile(nhalf, nspring, nhalf, 8, c) + [(c - nhalf, sill)]
                onto(t, dr).poly([(px, py, -0.012) for px, py in shape], dress.GRIME, WET + (BONE_DIM,), facing=(0, 0, 1))
        dress.damp(dr, a, (12.0 - F, z), foot, (0, oz), 0.75, colour=MOSS, seed=10.0 + oz)
    # The west end, which closes the passage's whole length: a hooded figure in a niche, its head bowed.
    t, (c,) = niched(m, (xw, zn), (xw, -25.0), FLOOR, CEIL, (1, 0), tint, [((xw, -30.0), 0.42, FLOOR + 0.45, FLOOR + 1.75, 0.42, 0.3, 0.08)])
    monk(onto(t, carved), (c, FLOOR + 0.45, -0.15), 0.0, 1.5, bowed=1.0)
    dress.damp(dr, (xw, zn), (xw, -25.0), foot, (1, 0), 0.4, colour=MOSS, seed=13.0)
    wall(m, (xe, zs), (xe, -25.0), FLOOR, CEIL, (-1, 0), tint)
    dress.damp(dr, (xe, zs), (xe, -25.0), foot, (-1, 0), 0.75, colour=MOSS, seed=14.0)
    for corner, a, b in (((xw + 0.01, PSPRING - 0.02, zn + 0.01), (1.0, -0.45, 0.03), (0.03, -0.45, 1.0)), ((xw + 0.01, PSPRING - 0.02, zs - 0.01), (1.0, -0.45, -0.03), (0.03, -0.45, -1.0))):
        dust_web(dr, corner, a, b, 0.6, int(corner[2]))
    # Runs down from the vault's springing, salt, wet flags.
    for i, (x, length) in enumerate(((-11.2, 1.5), (-7.2, 1.1), (-0.9, 1.7), (3.4, 1.3), (7.3, 1.0), (9.1, 1.6))):
        z, oz = (zn, 1) if i % 2 else (zs, -1)
        dress.run(dr, (x, PSPRING - 0.03, z), (0, oz), 0.3, length, WET, 0.55, seed=x)
    for x, z, oz in ((-13.0, zs, -1), (1.3, zs, -1), (9.0, zn, 1)):
        dress.patch(dr, (x, FLOOR + 1.25, z), (0, oz), 1.3, 0.9, SALT, 0.4, seed=x)
    for x, z, rx, rz in ((-9.3, -30.6, 1.2, 0.7), (2.8, -29.5, 1.0, 0.6), (7.2, -30.9, 0.7, 0.45), (-18.5, -26.7, 0.7, 0.9), (-18.8, -30.5, 0.7, 0.8)):
        wet(dr, x, z, rx, rz, x)
    # The hidden stair's well, and the walled-up arch beside its foot.
    wall(m, (xw, -25.0), (xw, -19.0), FLOOR, CEIL, (1, 0), tint)
    wall(m, (-18.2, -25.0), (-18.2, -19.0), FLOOR, 0.056, (-1, 0), tint)
    # The walled-up arch, its blocking set back a little; and on the
    # blocking, a small cross scratched over and over.
    cx = (-18.2 + xe) * 0.5
    t, (c,) = niched(m, (-18.2, -25.0), (xe, -25.0), FLOOR, CEIL, (0, -1), tint, [((cx, -25.0), 0.62, FLOOR, FLOOR + 1.5, 0.62, 0.09, 0.42, False, True, False)])
    scratches(onto(t, dr), c - 0.06, FLOOR + 1.15, -0.085, 0.46, 0.6)
    # The hidden stair is narrower than its well: the stone beside it. The
    # rim of the granary's floor round the well, and its underside.
    cheek(m, "z", xw, -19.3, -25.0, -19.0, -19.375, -19.3)
    cheek(m, "z", -18.3, -18.2, -25.0, -19.0, -19.375, -18.3)
    lip = pale(0.4)
    m.poly([(xw, CEIL, -25.0), (-18.2, CEIL, -25.0), (-18.2, 0.056, -25.0), (xw, 0.056, -25.0)], STONE, lip, facing=(0, 0, 1))
    m.poly([(-19.4, CEIL, -25.0), (-19.4, CEIL, -19.0), (-19.4, 0.056, -19.0), (-19.4, 0.056, -25.0)], STONE, lip, facing=(1, 0, 0))
    m.poly([(xw, CEIL, -25.0), (-19.4, CEIL, -25.0), (-19.4, CEIL, -19.0), (xw, CEIL, -19.0)], STONE, lip, facing=(0, -1, 0))
    cp.arch_wall(m, -25.0, xw, xe, FLOOR, CEIL, PHALF, PSPRING, PHALF, (0, 0, 1), ROUGH, tint, cx=-18.0)

    barrel(v, "x", xe, 12.0 - F, -30.0, PHALF, pcrown, ROUGH, web)
    barrel(v, "z", zs, -25.0, -18.0, PHALF, pcrown, ROUGH, web)
    groin(v, xw, xe, zn, zs, pcrown, ROUGH, web)
    for x in [xe + 0.2] + [-12.0 + 4.0 * i for i in range(6)] + [12.0 - F - 0.2]:
        ring(m, "x", x, -30.0, PHALF, pcrown, PSPRING)
    ring(m, "z", zs + 0.2, -18.0, PHALF, pcrown, PSPRING)
    ring(m, "z", -25.2, -18.0, PHALF, pcrown, PSPRING)
    # Torches: their soot up the vault, their rust down the wall.
    for i, x in enumerate((-14.0, -6.0, 2.0, 10.0)):
        z, oz = (zn, 1) if i % 2 == 0 else (zs, -1)
        torch(fit, x, FLOOR + 1.9, z, 0, oz, soot=False)
        barrel_soot(dr, x, FLOOR + 1.9, z, 0, oz, PHALF, PSPRING)
        dress.run(dr, (x, FLOOR + 1.79, z), (0, oz), 0.14, 0.9, RUSTY, 0.7, seed=x)
    torch(fit, xe, FLOOR + 1.9, -26.6, -1, 0, soot=False)
    barrel_soot(dr, xe, FLOOR + 1.9, -26.6, -1, 0, PHALF, PSPRING)
    dress.run(dr, (xe, FLOOR + 1.79, -26.6), (-1, 0), 0.14, 0.9, RUSTY, 0.7, seed=5.0)


def build():
    porter.reset(523)
    cl.STONE = STONE
    crypt_m, pass_m, fit, floor = porter.Mesh("Crypt"), porter.Mesh("Passage"), porter.Mesh("Fittings"), porter.Mesh("Floor")
    vaults = porter.Mesh("Vaults")
    # Stains, webs and scratches (thin faces over the stone); carved and laid things (figures, effigies, bones).
    stains, carved = porter.Mesh("Stains"), porter.Mesh("Carved")
    crypt(crypt_m, vaults, fit, stains, carved)
    passage(pass_m, vaults, fit, stains, carved)
    flags(floor, 12.0 + F, 28.0 - F, -36.0 + F, -28.0 - F, 4.0)
    flags(floor, -20.0 + F, 12.0 - F, -32.0 + F, -28.0 - F, 9.0)
    flags(floor, -20.0 + F, -16.0 - F, -28.0 - F, -25.0, 9.0)
    flags(floor, 12.0 - F, 12.0 + F, -30.47, -29.53, 9.0)
    # A lid over it all, never seen: the vaults face down, so without it the
    # sun and the moon would light what stands under them.
    lid = porter.Mesh("Lid")
    for x0, x1, z0, z1 in ((11.0, 29.0, -37.0, -27.0), (-21.0, 12.0, -33.0, -27.0), (-21.0, -15.0, -28.0, -25.0)):
        lid.poly([(x0, CEIL - 0.02, z0), (x1, CEIL - 0.02, z0), (x1, CEIL - 0.02, z1), (x0, CEIL - 0.02, z1)], STONE, pale(0.3), facing=(0, 1, 0))
    lid.build()
    crypt_m.build()
    pass_m.build()
    vaults.build(smooth=True)
    fit.build()
    floor.build()
    stains.build()
    carved.build(smooth=True)
    porter.export("env_crypt")


if __name__ == "__main__":
    build()
