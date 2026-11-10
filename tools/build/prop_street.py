"""What stands about in the street inside Aldgate at dusk (night 0, the
road in), each its own model (art/models/prop_street_<name>.glb), so the
scene can set them down by hand:

- barrels: three casks, one on its side, and a wash tub.
- crates: two boxes and a heap of sacks.
- handcart: a two-wheeled barrow tipped onto its shafts for the night.
- stall: a trestle stall shut up, its cloth roof sagging with rain.
- firewood: a stack of split logs under a board.
- trough: a stone water trough with a wooden pump over it.
- bench: a plank on two blocks.
- ladder: a ladder leant on a wall.
- posts: three timber posts that keep the carts off a corner.
- cresset: an iron fire basket on a wall bracket (the scene,
  game/world/props/prop_cresset.tscn, gives it flame and light).

Each stands on the ground at its origin; the ones that go against a wall
have their backs at z = 0 and face -z, as the houses do. No collision:
they are out of the wagon's way and nobody walks here.

Run: tools/build.sh prop_street
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter

BOARDS = "wood_boards"
OAK = "wood_frame"
IRON = (0.5, 0.48, 0.46, 1.0)


def wood(k=1.0):
    v = random.uniform(0.62, 0.86) * k
    return (v, v * 0.96, v * 0.9, 1.0)


def barrel(m, x, z, r=0.3, h=0.85, lying=None):
    """A cask: staves bellied in the middle, three hoops. `lying` (an angle) puts it on its side."""
    sides = 10
    prof = [(0.0, r * 0.84), (h * 0.25, r * 0.97), (h * 0.5, r), (h * 0.75, r * 0.97), (h, r * 0.84)]
    shade = wood()

    def at(a, t, rr):
        c, s = math.cos(a) * rr, math.sin(a) * rr
        if lying is None:
            return (x + c, t, z + s)
        ux, uz = math.cos(lying), math.sin(lying)
        return (x + ux * (t - h * 0.5) - uz * c, r + s, z + uz * (t - h * 0.5) + ux * c)

    for (ta, ra), (tb, rb) in zip(prof, prof[1:]):
        for i in range(sides):
            a0, a1 = math.tau * i / sides, math.tau * (i + 1) / sides
            k = 0.85 + 0.15 * ((i * 7) % 3) / 2.0
            c = (shade[0] * k, shade[1] * k, shade[2] * k, 1.0)
            pts = [at(a0, ta, ra), at(a1, ta, ra), at(a1, tb, rb), at(a0, tb, rb)]
            mid = at((a0 + a1) * 0.5, (ta + tb) * 0.5, 1.0)
            centre = at(0.0, (ta + tb) * 0.5, 0.0)
            m.poly(pts, BOARDS, c, facing=(mid[0] - centre[0], mid[1] - centre[1], mid[2] - centre[2]))
    for t, rr in ((h * 0.12, r * 0.92), (h * 0.5, r * 1.012), (h * 0.88, r * 0.92)):
        for i in range(sides):
            a0, a1 = math.tau * i / sides, math.tau * (i + 1) / sides
            pts = [at(a0, t - 0.025, rr + 0.006), at(a1, t - 0.025, rr + 0.006), at(a1, t + 0.025, rr + 0.006), at(a0, t + 0.025, rr + 0.006)]
            mid = at((a0 + a1) * 0.5, t, 1.0)
            centre = at(0.0, t, 0.0)
            m.poly(pts, "iron_cart", IRON, facing=(mid[0] - centre[0], mid[1] - centre[1], mid[2] - centre[2]))
    for t, way in ((h - 0.04, 1), (0.04, -1)):
        if lying is None and way < 0:
            continue
        pts = [at(math.tau * i / sides, t, r * 0.8) for i in range(sides)]
        a, b = at(0.0, t, 0.0), at(0.0, t + way, 0.0)
        m.poly(pts, BOARDS, (shade[0] * 0.6, shade[1] * 0.6, shade[2] * 0.6, 1.0), facing=(b[0] - a[0], b[1] - a[1], b[2] - a[2]))


def crate(m, lo, hi, turn=0.0):
    """A box of boards, turned a little, with battens round its top."""
    cx, cz = (lo[0] + hi[0]) * 0.5, (lo[2] + hi[2]) * 0.5
    c, s = math.cos(turn), math.sin(turn)

    def p(x, y, z):
        dx, dz = x - cx, z - cz
        return (cx + dx * c - dz * s, y, cz + dx * s + dz * c)

    x0, y0, z0 = lo
    x1, y1, z1 = hi
    shade = wood()
    dark = (shade[0] * 0.7, shade[1] * 0.7, shade[2] * 0.7, 1.0)
    for pts, n in (([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)], (0, 0, -1)),
                   ([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], (0, 0, 1)),
                   ([(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)], (-1, 0, 0)),
                   ([(x1, y0, z0), (x1, y0, z1), (x1, y1, z1), (x1, y1, z0)], (1, 0, 0)),
                   ([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], (0, 1, 0))):
        q = [p(*v) for v in pts]
        f = (n[0] * c - n[2] * s, n[1], n[0] * s + n[2] * c)
        m.poly(q, BOARDS, [dark, dark, shade, shade] if n[1] == 0 else shade, facing=f)


def sack(m, x, z, y=0.0, r=0.26, length=0.7, turn=0.0, slump=0.6):
    ux, uz = math.cos(turn), math.sin(turn)
    pts = [(x - ux * length * 0.5, y + r * slump, z - uz * length * 0.5), (x - ux * length * 0.3, y + r * slump, z - uz * length * 0.3),
           (x + ux * length * 0.3, y + r * slump, z + uz * length * 0.3), (x + ux * length * 0.5, y + r * slump, z + uz * length * 0.5)]
    v = random.uniform(0.16, 0.24)
    m.tube(pts, [r * 0.35, r, r, r * 0.3], 7, "sacking", (v, v, v, 1.0), caps=True, squash=(1.0, slump))


def wheel(m, cx, cy, cz, r, axis_x=True):
    """A cart wheel standing in the plane across x (or z): a rim, a hub, eight spokes."""
    def at(a, rr, off):
        u, v = math.cos(a) * rr, math.sin(a) * rr
        return (cx + off, cy + v, cz + u) if axis_x else (cx + u, cy + v, cz + off)

    n = 12
    c = wood(0.8)
    for i in range(n):
        a0, a1 = math.tau * i / n, math.tau * (i + 1) / n
        for off, way in ((-0.035, -1), (0.035, 1)):
            pts = [at(a0, r - 0.07, off), at(a1, r - 0.07, off), at(a1, r, off), at(a0, r, off)]
            m.poly(pts, OAK, c, facing=(way, 0, 0) if axis_x else (0, 0, way))
        pts = [at(a0, r, -0.035), at(a1, r, -0.035), at(a1, r, 0.035), at(a0, r, 0.035)]
        mid = at((a0 + a1) * 0.5, 1.0, 0.0)
        m.poly(pts, "iron_cart", IRON, facing=(mid[0] - cx, mid[1] - cy, mid[2] - cz))
    for i in range(8):
        a = math.tau * i / 8 + 0.2
        m.tube([at(a, 0.06, 0.0), at(a, r - 0.06, 0.0)], [0.022, 0.018], 4, OAK, c)
    m.tube([at(0.0, 0.0, -0.08), at(0.0, 0.0, 0.08)], [0.07, 0.07], 6, OAK, wood(0.6), caps=True)


def build(name, fn):
    porter.reset(sum(ord(ch) for ch in name))
    m = porter.Mesh(name.title().replace("_", ""))
    fn(m)
    m.build()
    porter.export("prop_street_" + name)


def barrels(m):
    barrel(m, -0.35, -0.38)
    barrel(m, 0.34, -0.36, r=0.27, h=0.78)
    barrel(m, 1.2, -0.42, r=0.3, h=0.9, lying=0.25)
    # A wash tub: low and wide, rain standing in it.
    barrel(m, -1.15, -0.5, r=0.42, h=0.4)
    m.poly([(-1.15 + math.cos(math.tau * i / 10) * 0.37, 0.33, -0.5 + math.sin(math.tau * i / 10) * 0.37) for i in range(10)], "window_dark",
           facing=(0, 1, 0))


def crates(m):
    crate(m, (-0.5, 0.0, -0.75), (0.25, 0.55, -0.1), 0.12)
    crate(m, (-0.35, 0.55, -0.68), (0.2, 0.95, -0.18), -0.2)
    crate(m, (0.4, 0.0, -0.6), (0.95, 0.4, -0.08), 0.35)
    sack(m, 1.3, -0.35, turn=0.3)
    sack(m, 1.45, -0.75, turn=1.2)
    sack(m, 1.35, -0.5, y=0.26, turn=0.8, slump=0.5)
    sack(m, -0.9, -0.25, r=0.24, length=0.9, turn=1.45, slump=0.9)


def handcart(m):
    """Tipped forward onto its shafts: the bed slopes down to the ground at -z."""
    tilt = math.radians(-24.0)
    c, s = math.cos(tilt), math.sin(tilt)

    def p(x, y, z):
        # About the axle, at (y 0.42, z 0).
        return (x, 0.42 + y * c - z * s, y * s + z * c)

    def box(lo, hi, mat, col):
        x0, y0, z0 = lo
        x1, y1, z1 = hi
        for pts, n in (([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)], (0, 0, -1)),
                       ([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], (0, 0, 1)),
                       ([(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)], (-1, 0, 0)),
                       ([(x1, y0, z0), (x1, y0, z1), (x1, y1, z1), (x1, y1, z0)], (1, 0, 0)),
                       ([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], (0, 1, 0)),
                       ([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], (0, -1, 0))):
            m.poly([p(*v) for v in pts], mat, col, facing=(n[0], n[1] * c - n[2] * s, n[1] * s + n[2] * c))

    box((-0.45, 0.06, -0.7), (0.45, 0.11, 0.75), BOARDS, wood())
    for x in (-0.45, 0.41):
        box((x, 0.11, -0.7), (x + 0.04, 0.42, 0.75), BOARDS, wood(0.9))
    box((-0.45, 0.11, 0.71), (0.45, 0.42, 0.75), BOARDS, wood(0.9))
    for x in (-0.5, 0.44):
        box((x, 0.0, -1.75), (x + 0.06, 0.06, 0.75), OAK, wood(0.75))
    wheel(m, -0.58, 0.42, 0.0, 0.42)
    wheel(m, 0.58, 0.42, 0.0, 0.42)
    m.tube([(-0.6, 0.42, 0.0), (0.6, 0.42, 0.0)], [0.035, 0.035], 5, OAK, wood(0.6))


def stall(m):
    """Shut for the night: boards up, the cloth over it heavy with rain."""
    w, d, h = 2.4, 1.1, 0.85
    for x in (-w * 0.5 + 0.1, w * 0.5 - 0.1):
        for z in (-d + 0.08, -0.08):
            m.box((x - 0.04, 0.0, z - 0.04), (x + 0.04, 2.05 if z > -0.5 else 1.85, z + 0.04), OAK, wood(0.7), faces="xXzZ")
    m.box((-w * 0.5, h - 0.05, -d), (w * 0.5, h, 0.0), BOARDS, wood())
    # Boards across the front, for the night.
    y = 0.12
    while y < h - 0.1:
        m.box((-w * 0.5 + 0.05, y, -d - 0.02), (w * 0.5 - 0.05, y + 0.2, -d + 0.01), BOARDS, wood(0.85), faces="xXzyY")
        y += 0.23
    # The cloth: stretched from the back posts down to the front ones, sagging between.
    n = 6
    red = porter.srgb(0.3, 0.2, 0.16)
    buff = porter.srgb(0.42, 0.38, 0.3)
    for i in range(n):
        xa, xb = -w * 0.5 - 0.1 + (w + 0.2) * i / n, -w * 0.5 - 0.1 + (w + 0.2) * (i + 1) / n
        sag = lambda x: 0.16 * math.sin(math.pi * (x + w * 0.5 + 0.1) / (w + 0.2))
        col = red if i % 2 == 0 else buff
        for za, zb, ya, yb in ((-d - 0.25, -d * 0.5, 1.8, 1.9), (-d * 0.5, 0.05, 1.9, 2.07)):
            pts = [(xa, ya - sag(xa) * (1.4 if za < -d else 1.0), za), (xb, ya - sag(xb) * (1.4 if za < -d else 1.0), za),
                   (xb, yb - sag(xb) * (1.0 if zb < 0 else 0.3), zb), (xa, yb - sag(xa) * (1.0 if zb < 0 else 0.3), zb)]
            m.poly(pts, "sacking", col, facing=(0, 1, -0.2))
            m.poly(pts, "sacking", (col[0] * 0.4, col[1] * 0.4, col[2] * 0.4, 1.0), facing=(0, -1, 0.2))


def firewood(m):
    random.seed(4)
    rows = 5
    for j in range(rows):
        n = 9 - (j % 2)
        for i in range(n):
            x = -1.0 + 2.0 * (i + 0.5 * (j % 2)) / 8.5 + random.uniform(-0.02, 0.02)
            y = 0.1 + j * 0.2
            r = random.uniform(0.09, 0.115)
            v = random.uniform(0.5, 0.85)
            m.tube([(x, y, -0.62 + random.uniform(-0.03, 0.03)), (x, y, -0.04)], [r, r], 5, "bark", (v, v * 0.95, v * 0.85, 1.0), caps=True)
    for x in (-1.12, 1.08):
        m.box((x, 0.0, -0.4), (x + 0.06, 1.25, -0.32), OAK, wood(0.7), faces="xXzZ")
    roof = [(-1.25, 1.12, -0.85), (1.25, 1.12, -0.85), (1.25, 1.34, 0.0), (-1.25, 1.34, 0.0)]
    m.poly(roof, BOARDS, wood(0.8), facing=(0, 1, -0.3))
    m.poly(roof, BOARDS, wood(0.35), facing=(0, -1, 0.3))


def trough(m):
    stone = (0.8, 0.79, 0.76, 1.0)
    damp = (0.45, 0.5, 0.42, 1.0)
    lo, hi = (-0.9, 0.0, -0.75), (0.9, 0.52, -0.1)
    m.box(lo, hi, "stone_ashlar", damp, top_color=stone, faces="xXzZ")
    for a, b in (((lo[0], hi[1], lo[2]), (hi[0], hi[1], lo[2] + 0.12)), ((lo[0], hi[1], hi[2] - 0.12), (hi[0], hi[1], hi[2])),
                 ((lo[0], hi[1], lo[2] + 0.12), (lo[0] + 0.12, hi[1], hi[2] - 0.12)), ((hi[0] - 0.12, hi[1], lo[2] + 0.12), (hi[0], hi[1], hi[2] - 0.12))):
        m.quad((a[0], a[1], a[2]), (a[0], a[1], b[2]), (b[0], a[1], b[2]), (b[0], a[1], a[2]), "stone_ashlar", stone)
    m.quad((lo[0] + 0.12, hi[1] - 0.07, lo[2] + 0.12), (lo[0] + 0.12, hi[1] - 0.07, hi[2] - 0.12), (hi[0] - 0.12, hi[1] - 0.07, hi[2] - 0.12),
           (hi[0] - 0.12, hi[1] - 0.07, lo[2] + 0.12), "window_dark")
    # The pump: a bored elm trunk, an iron spout, a long handle.
    m.tube([(1.15, 0.0, -0.3), (1.15, 1.5, -0.3)], [0.13, 0.11], 7, OAK, wood(0.8), caps=True)
    m.tube([(1.05, 1.0, -0.33), (0.72, 0.92, -0.4)], [0.035, 0.03], 5, "iron_cart", IRON)
    m.tube([(1.15, 1.42, -0.3), (1.5, 1.55, -0.3), (1.75, 0.85, -0.3)], [0.025, 0.025, 0.02], 4, "iron_cart", IRON)


def bench(m):
    m.box((-0.8, 0.42, -0.42), (0.8, 0.47, -0.08), BOARDS, wood())
    for x in (-0.62, 0.54):
        m.box((x, 0.0, -0.38), (x + 0.08, 0.42, -0.12), BOARDS, wood(0.75), faces="xXzZ")
    # A pail left under it.
    barrel(m, 0.05, -0.25, r=0.14, h=0.26)


def ladder(m):
    for x in (-0.22, 0.22):
        m.tube([(x, 0.0, -0.8), (x, 2.85, -0.04)], [0.032, 0.028], 4, OAK, wood(0.85))
    for i in range(1, 10):
        k = i / 10.0
        m.tube([(-0.22, 2.85 * k, -0.8 + 0.76 * k), (0.22, 2.85 * k, -0.8 + 0.76 * k)], [0.02, 0.02], 4, OAK, wood())


def posts(m):
    for x, z, h, lean in ((-0.7, -0.2, 0.95, 0.04), (0.0, -0.32, 1.05, -0.03), (0.72, -0.18, 0.9, 0.06)):
        m.tube([(x, 0.0, z), (x + lean, h, z + lean * 0.5), (x + lean, h + 0.05, z + lean * 0.5)], [0.11, 0.095, 0.05], 7, OAK, wood(0.7), caps=True)
        ring = [(x + lean * 0.8 + math.cos(math.tau * i / 7) * 0.105, h * 0.82, z + math.sin(math.tau * i / 7) * 0.105) for i in range(8)]
        for a, b in zip(ring, ring[1:]):
            m.poly([a, b, (b[0], b[1] + 0.04, b[2]), (a[0], a[1] + 0.04, a[2])], "iron_cart", IRON, facing=(a[0] + b[0] - 2 * x, 0, a[2] + b[2] - 2 * z))


def cresset():
    """An iron basket on a bracket out from a wall (the wall at z = 0), the
    fire in it. Coals and Flame are their own objects, as on the brazier."""
    porter.reset(21)
    m = porter.Mesh("Cresset")
    out, y = -0.55, 0.0
    m.tube([(0.0, y - 0.55, -0.02), (0.0, y - 0.1, out)], [0.016, 0.016], 4, "iron_cart", IRON)
    m.tube([(0.0, y - 0.1, -0.02), (0.0, y - 0.1, out)], [0.018, 0.018], 4, "iron_cart", IRON)
    for yy, r in ((y - 0.1, 0.12), (y + 0.08, 0.17), (y + 0.24, 0.2)):
        pts = [(math.cos(math.tau * i / 8) * r, yy, out + math.sin(math.tau * i / 8) * r) for i in range(9)]
        for a, b in zip(pts, pts[1:]):
            m.tube([a, b], [0.011, 0.011], 4, "iron_cart", IRON)
    for i in range(8):
        a = math.tau * i / 8
        m.tube([(math.cos(a) * 0.12, y - 0.1, out + math.sin(a) * 0.12), (math.cos(a) * 0.2, y + 0.24, out + math.sin(a) * 0.2)], [0.009, 0.009], 4,
               "iron_cart", IRON)
    m.build()
    c = porter.Mesh("Coals")
    for i in range(9):
        a = random.uniform(0.0, math.tau)
        d = random.uniform(0.0, 0.11)
        s = random.uniform(0.045, 0.07)
        yy = y + 0.1 + (0.12 - d) * 0.6
        heat = random.uniform(0.3, 1.0)
        x, z = math.cos(a) * d, out + math.sin(a) * d
        c.box((x - s, yy - s * 0.7, z - s), (x + s, yy + s * 0.7, z + s), "embers", (heat, heat, heat, 1.0))
    c.build()
    f = porter.Mesh("Flame")
    for i in range(3):
        a = math.pi * i / 3
        dx, dz = math.cos(a) * 0.2, math.sin(a) * 0.2
        f.quad((-dx, y + 0.14, out - dz), (dx, y + 0.14, out + dz), (dx, y + 0.72, out + dz), (-dx, y + 0.72, out - dz), "flame",
               uvs=[(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
    f.build()
    porter.export("prop_street_cresset")


def main():
    for name, fn in (("barrels", barrels), ("crates", crates), ("handcart", handcart), ("stall", stall), ("firewood", firewood),
                     ("trough", trough), ("bench", bench), ("ladder", ladder), ("posts", posts)):
        build(name, fn)
    cresset()


if __name__ == "__main__":
    main()
