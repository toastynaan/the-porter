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

The walls this adds (the crypt's stair wall, the wall beside the hidden
stair) are solid as blocks in church.tscn and cellar.tscn.

Run: tools/build.sh env_crypt
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
import city_parts as cp
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


def torch(m, x, y, z, ox, oz):
    """An iron bracket on the wall and a burnt-out torch in it."""
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


def crypt(m, v, fit):
    ccrown = round_crown(CSPRING, CRISE)
    tint = cp.stone_tint(FLOOR, CEIL + 2.0, clean=(0.74, 0.72, 0.68), seed=5.0, worn=0.0)
    tint.mat = STONE
    web = lambda x, y, z: cp.rgba((0.8, 0.79, 0.75), lerp(1.0, 0.6, smoothstep(CSPRING, CSPRING + CRISE, y)) * (0.9 + 0.14 * fbm(x, z, 0.5, 2, 3.0)))
    edges = [12.0 + F, 16.2, 20.0, 23.8, 28.0 - F]
    centres = [(a + b) * 0.5 for a, b in zip(edges, edges[1:])]

    # The south wall: a tomb recess in each bay.
    t = cl.Turned(m, ch.SOUTH)
    half, spring, rise, deep = 1.05, -3.2, 0.8, 0.34
    for (xa, xb), xc in zip(zip(edges, edges[1:]), centres):
        uc = -xc
        cp.arch_wall(t, F, -xb, -xa, FLOOR, CEIL, half, spring, rise, (0, 0, 1), STONE, tint, cx=uc)
        reveal(t, F - deep, F, half, spring, rise, STONE, lambda x, y, z: pale(0.5), cx=uc, y0=FLOOR, step=0.5)
        shape = [(uc + half, FLOOR)] + cp.arch_profile(half, spring, rise, 8, uc) + [(uc - half, FLOOR)]
        t.poly([(x, y, F - deep) for x, y in shape], STONE, pale(0.36), facing=(0, 0, 1))
        cp.arch_band(t, F, half, spring, rise, 0.12, 0.05, (0, 0, 1), STONE, pale(0.7), cx=uc)
        # The tomb: a chest, its lid, a cross cut in relief.
        t.box((uc - 0.9, FLOOR, F - deep + 0.02), (uc + 0.9, FLOOR + 0.52, F - 0.03), STONE, pale(0.55), top_color=pale(0.7), faces="xXZ")
        t.box((uc - 0.96, FLOOR + 0.52, F - deep + 0.01), (uc + 0.96, FLOOR + 0.62, F + 0.02), STONE, pale(0.78), faces="xXZyY")
        t.box((uc - 0.6, FLOOR + 0.62, F - 0.19), (uc + 0.6, FLOOR + 0.64, F - 0.14), STONE, pale(0.9), faces="xXzZY")
        t.box((uc + 0.25, FLOOR + 0.62, F - 0.28), (uc + 0.3, FLOOR + 0.64, F - 0.05), STONE, pale(0.9), faces="xXzZY")

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
    cp.panel(t, (-4.0 + F, F), (-34.2 + 32.0, F), FLOOR, CEIL, (0, 0, 1), STONE, tint, 1.6, 1.2)

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
    wall(m, (16.5, -34.2), (24.0, -34.2), FLOOR, 0.056, (0, -1), tint)
    wall(m, (12.0 + F, -36.0 + F), (28.0 - F, -36.0 + F), FLOOR, CEIL, (0, 1), tint)
    wall(m, (16.5, -36.0 + F), (24.0, -36.0 + F), CEIL, 0.056, (0, 1), tint)
    wall(m, (16.2, -36.0 + F), (16.2, -34.2), FLOOR, CEIL, (-1, 0), tint)
    # The alcoves: a tunnel vault each; the east one opens to the well through an arch.
    c, ahalf, aspring = ALCOVE
    acrown = round_crown(aspring, ahalf)
    barrel(v, "x", edges[0], 16.2, c, ahalf, acrown, STONE, web, 0.8)
    barrel(v, "x", 24.0, edges[4], c, ahalf, acrown, STONE, web, 0.8)
    cp.arch_wall(m, 24.0, -36.0 + F, -34.2, FLOOR, 0.056, ahalf, aspring, ahalf, (-1, 0, 0), STONE, tint, cx=c, along="z")

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
    for z, oz in ((zb, -1), (za, 1)):
        torch(fit, 20.0, FLOOR + 1.95, z + oz * 0.3, 0, oz)
    for u in (-0.75, 2.45):
        torch(fit, 28.0 - F, FLOOR + 1.95, -32.0 + u, -1, 0)


def passage(m, v, fit):
    pcrown = round_crown(PSPRING, PHALF)
    tint = cp.stone_tint(FLOOR, CEIL + 1.0, clean=(0.72, 0.7, 0.66), seed=17.0, worn=0.5)
    web = lambda x, y, z: cp.rgba((0.74, 0.72, 0.68), lerp(1.0, 0.62, smoothstep(PSPRING, PSPRING + PHALF, y)) * (0.86 + 0.2 * fbm(x, z, 0.5, 2, 6.0)))
    zn, zs, xw, xe = -32.0 + F, -28.0 - F, -20.0 + F, -16.0 - F
    wall(m, (xw, zn), (12.0 - F, zn), FLOOR, CEIL, (0, 1), tint)
    wall(m, (xe, zs), (12.0 - F, zs), FLOOR, CEIL, (0, -1), tint)
    wall(m, (xw, zn), (xw, -25.0), FLOOR, CEIL, (1, 0), tint)
    wall(m, (xe, zs), (xe, -25.0), FLOOR, CEIL, (-1, 0), tint)
    # The hidden stair's well, and the walled-up arch beside its foot.
    wall(m, (xw, -25.0), (xw, -19.0), FLOOR, 0.056, (1, 0), tint)
    wall(m, (-18.2, -25.0), (-18.2, -19.0), FLOOR, 0.056, (-1, 0), tint)
    wall(m, (-18.2, -25.0), (xe, -25.0), FLOOR, CEIL, (0, -1), tint)
    cx = (-18.2 + xe) * 0.5
    cp.arch_band(m, -25.0, 0.62, FLOOR + 1.5, 0.62, 0.14, 0.06, (0, 0, -1), STONE, pale(0.62), cx=cx, y0=FLOOR)
    shape = [(cx + 0.62, FLOOR)] + cp.arch_profile(0.62, FLOOR + 1.5, 0.62, 8, cx) + [(cx - 0.62, FLOOR)]
    m.poly([(x, y, -25.02) for x, y in shape], STONE, pale(0.5), facing=(0, 0, -1))
    cp.arch_wall(m, -25.0, xw, xe, FLOOR, CEIL, PHALF, PSPRING, PHALF, (0, 0, 1), ROUGH, tint, cx=-18.0)

    barrel(v, "x", xe, 12.0 - F, -30.0, PHALF, pcrown, ROUGH, web)
    barrel(v, "z", zs, -25.0, -18.0, PHALF, pcrown, ROUGH, web)
    groin(v, xw, xe, zn, zs, pcrown, ROUGH, web)
    for x in [xe + 0.2] + [-12.0 + 4.0 * i for i in range(6)] + [12.0 - F - 0.2]:
        ring(m, "x", x, -30.0, PHALF, pcrown, PSPRING)
    ring(m, "z", zs + 0.2, -18.0, PHALF, pcrown, PSPRING)
    ring(m, "z", -25.2, -18.0, PHALF, pcrown, PSPRING)
    for i, x in enumerate((-14.0, -6.0, 2.0, 10.0)):
        z, oz = (zn, 1) if i % 2 == 0 else (zs, -1)
        torch(fit, x, FLOOR + 1.9, z, 0, oz)
    torch(fit, xe, FLOOR + 1.9, -26.6, -1, 0)


def build():
    porter.reset(523)
    cl.STONE = STONE
    crypt_m, pass_m, fit, floor = porter.Mesh("Crypt"), porter.Mesh("Passage"), porter.Mesh("Fittings"), porter.Mesh("Floor")
    vaults = porter.Mesh("Vaults")
    crypt(crypt_m, vaults, fit)
    passage(pass_m, vaults, fit)
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
    porter.export("env_crypt")


if __name__ == "__main__":
    build()
