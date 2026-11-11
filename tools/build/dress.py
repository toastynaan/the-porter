"""Dressing shared by the abbey's build scripts: what makes a clean wall
look old and a dark room look wrong. Stains, soot, damp and cracks are thin
faces laid just proud of a surface in the `grime` material, which darkens
what is behind it by the vertex colour's alpha. Cobwebs are the same in the
`cobweb` material. Bones, skulls, standing figures and effigies are solid
and take a stone or bone colour.

Every function takes a mesh `m` (a porter.Mesh, or a proxy such as
env_cloister.Turned) and works in that mesh's own space: y is up. A wall's
`out` is the horizontal direction it faces, (ox, oz), in that space.

None of this has collision. Keep solid things inside a wall's thickness,
against a wall, or above head height.
"""
import math
import random

import porter
from porter import fbm, lerp, smoothstep

GRIME = "grime"
WEB = "cobweb"
BONE = (0.36, 0.32, 0.24)
SOOT = (0.02, 0.02, 0.02)
RUST = (0.2, 0.09, 0.04)
GREEN = (0.07, 0.11, 0.05)
DARK = (0.05, 0.045, 0.04)
PROUD = 0.008


class Placed:
    """A mesh seen from a point and a heading: what is built through it in
    its own space (x right, y up, z toward the viewer it faces) lands at
    `origin`, turned `yaw` radians about y."""

    def __init__(self, mesh, origin, yaw=0.0, scale=1.0, tilt=0.0):
        self.mesh, self.origin, self.scale = mesh, origin, scale
        self.c, self.s = math.cos(yaw), math.sin(yaw)
        self.tc, self.ts = math.cos(tilt), math.sin(tilt)

    def vert(self, x, y, z, color=(1.0, 1.0, 1.0, 1.0), uv=(0.0, 0.0)):
        # Tilt about x (a lean back or forward), then turn about y.
        y, z = y * self.tc - z * self.ts, y * self.ts + z * self.tc
        x, y, z = x * self.scale, y * self.scale, z * self.scale
        o = self.origin
        return self.mesh.vert(o[0] + x * self.c + z * self.s, o[1] + y, o[2] - x * self.s + z * self.c, color, uv)

    def face(self, indices, mat):
        self.mesh.face(indices, mat)

    quad = porter.Mesh.quad
    poly = porter.Mesh.poly
    tube = porter.Mesh.tube
    box = porter.Mesh.box


def _wall(p, out, proud=PROUD):
    """A point's frame on a wall: the direction along it, and a function
    from (along, up) offsets to a point just proud of the wall."""
    n = math.hypot(out[0], out[1]) or 1.0
    ox, oz = out[0] / n, out[1] / n
    ax, az = -oz, ox

    def at(u, v):
        return (p[0] + ax * u + ox * proud, p[1] + v, p[2] + az * u + oz * proud)
    return at, (ox, 0.0, oz)


def _sheet(m, at, facing, us, vs, alpha, colour, mat=GRIME):
    """A grid of faces through at(u, v), each vertex's alpha from alpha(u, v)."""
    for ua, ub in zip(us, us[1:]):
        for va, vb in zip(vs, vs[1:]):
            corners = [(ua, va), (ub, va), (ub, vb), (ua, vb)]
            cols = [(colour[0], colour[1], colour[2], max(0.0, min(1.0, alpha(u, v)))) for u, v in corners]
            if max(c[3] for c in cols) < 0.01:
                continue
            m.poly([at(u, v) for u, v in corners], mat, cols, facing=facing)


def soot(m, p, out, width=0.5, height=1.3, strength=0.95):
    """The black a flame leaves on the wall over it. `p` is on the wall's
    face where the flame is (or was)."""
    at, facing = _wall(p, out)
    us = [width * (i / 4.0 - 0.5) * 1.6 for i in range(5)]
    vs = [height * j / 5.0 for j in range(6)]

    def alpha(u, v):
        t = v / height
        spread = width * (0.35 + 0.65 * t)
        return strength * (1.0 - t) ** 0.9 * max(0.0, 1.0 - (u / spread) ** 2) * (0.4 + 0.6 * smoothstep(0.0, 0.08, t))
    _sheet(m, at, facing, us, vs, alpha, SOOT)


def run(m, p, out, width=0.22, length=1.6, colour=DARK, strength=0.6, seed=0.0):
    """A streak down a wall from `p`: water off a sill, rust off an iron,
    wax off a pricket."""
    at, facing = _wall(p, out)
    us = [width * (i / 3.0 - 0.5) for i in range(4)]
    vs = [-length * j / 5.0 for j in range(6)]

    def alpha(u, v):
        t = -v / length
        ragged = 0.6 + 0.4 * fbm(p[0] + p[2] + u * 6.0, v * 1.5, 1.0, 2, seed)
        return strength * (1.0 - t) * ragged * max(0.0, 1.0 - (u / (width * 0.34)) ** 2)
    _sheet(m, at, facing, us, vs, alpha, colour)


def damp(m, a, b, y0, out, height=1.2, colour=GREEN, strength=0.55, seed=0.0):
    """Damp rising from the foot of a wall that runs from (x, z) `a` to `b`."""
    length = math.hypot(b[0] - a[0], b[1] - a[1])
    if length < 0.2:
        return
    at, facing = _wall((a[0], y0, a[1]), out)
    # _wall's "along" may run b to a: measure it.
    p1 = at(1.0, 0.0)
    sign = 1.0 if (p1[0] - a[0]) * (b[0] - a[0]) + (p1[2] - a[1]) * (b[1] - a[1]) > 0 else -1.0
    n = max(int(length / 0.5), 1)
    us = [sign * length * i / n for i in range(n + 1)]
    vs = [height * j / 4.0 for j in range(5)]

    def alpha(u, v):
        top = height * (0.55 + 0.45 * (0.5 + 0.5 * fbm(abs(u) * 0.8, seed, 1.0, 3, seed + 4.0)))
        return strength * max(0.0, 1.0 - v / max(top, 0.05)) * (0.7 + 0.3 * fbm(abs(u) * 3.0, v * 3.0, 1.0, 2, seed))
    _sheet(m, at, facing, us, vs, alpha, colour)


def patch(m, p, out, width=1.0, height=0.8, colour=DARK, strength=0.5, seed=0.0):
    """A blotch on a wall centred on `p`: old damp, a scorch, a place where
    something hung."""
    at, facing = _wall(p, out)
    us = [width * (i / 4.0 - 0.5) for i in range(5)]
    vs = [height * (j / 4.0 - 0.5) for j in range(5)]

    def alpha(u, v):
        r = math.hypot(u / (width * 0.5), v / (height * 0.5))
        edge = 0.75 + 0.35 * fbm(u * 3.0 + p[0], v * 3.0 + p[1], 1.0, 2, seed)
        return strength * max(0.0, 1.0 - (r / edge) ** 2)
    _sheet(m, at, facing, us, vs, alpha, colour)


def crack(m, p, out, length=1.6, seed=0, width=0.014, lean=0.25, strength=0.9):
    """A crack running up a wall from `p`, with a branch or two."""
    at, facing = _wall(p, out, PROUD * 1.5)
    rng = random.Random(seed)

    def line(u, v, n, step, drift):
        pts = [(u, v)]
        for _ in range(n):
            u += rng.uniform(-0.09, 0.09) + drift * step
            v += step * rng.uniform(0.6, 1.2)
            pts.append((u, v))
        return pts

    lines = [line(0.0, 0.0, max(int(length / 0.14), 2), 0.14, rng.uniform(-lean, lean))]
    for _ in range(rng.randint(1, 2)):
        u, v = rng.choice(lines[0][2:-1] or lines[0])
        lines.append(line(u, v, rng.randint(2, 4), 0.11, rng.choice((-1, 1)) * rng.uniform(0.4, 0.9)))
    for pts in lines:
        for i, ((ua, va), (ub, vb)) in enumerate(zip(pts, pts[1:])):
            w = width * (1.0 - 0.7 * i / len(pts))
            cols = [(0.02, 0.02, 0.02, strength)] * 4
            m.poly([at(ua - w, va), at(ua + w, va), at(ub + w * 0.7, vb), at(ub - w * 0.7, vb)], GRIME, cols, facing=facing)


def cobweb(m, corner, a, b, size=0.8, seed=0, sag=0.12):
    """A web across a corner: `corner` is the corner's point; `a` and `b`
    are the directions (x, y, z) of the two edges it hangs between."""
    rng = random.Random(seed)

    def unit(v):
        n = math.sqrt(sum(q * q for q in v)) or 1.0
        return tuple(q / n for q in v)

    a, b = unit(a), unit(b)
    spokes = rng.randint(5, 7)
    fs = sorted([0.0, 1.0] + [min(max((i + rng.uniform(-0.3, 0.3)) / (spokes - 1), 0.04), 0.96) for i in range(1, spokes - 1)])

    def point(i, r):
        f = fs[i]
        d = unit(tuple(lerp(a[k], b[k], f) for k in range(3)))
        droop = sag * r * math.sin(math.pi * f)
        return (corner[0] + d[0] * r, corner[1] + d[1] * r - droop, corner[2] + d[2] * r)

    normal = (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
    reach = [size * rng.uniform(0.55, 1.0) for _ in range(spokes)]
    veil, thread = (0.6, 0.6, 0.58, 0.04), (0.7, 0.7, 0.68, 0.26)
    for k in (-1, 1):
        face = tuple(q * k for q in normal)
        for i in range(spokes - 1):
            m.poly([corner, point(i, reach[i]), point(i + 1, reach[i + 1])], WEB, veil, facing=face)
        w = 0.003
        for i in range(spokes):
            tip = point(i, reach[i])
            d = tuple(tip[q] - corner[q] for q in range(3))
            side = unit((normal[1] * d[2] - normal[2] * d[1], normal[2] * d[0] - normal[0] * d[2], normal[0] * d[1] - normal[1] * d[0]))
            m.poly([corner, tuple(tip[q] + side[q] * w for q in range(3)), tuple(tip[q] - side[q] * w for q in range(3))], WEB, thread, facing=face)
        for ring in sorted(rng.uniform(0.25, 0.95) for _ in range(rng.randint(2, 4))):
            for i in range(spokes - 1):
                p, q = point(i, reach[i] * ring), point(i + 1, reach[i + 1] * ring)
                mid = tuple((p[k2] + q[k2]) * 0.5 for k2 in range(3))
                mid = (mid[0], mid[1] - 0.02 * size, mid[2])
                for s, e in ((p, mid), (mid, q)):
                    m.poly([s, e, (e[0], e[1] - w * 2, e[2]), (s[0], s[1] - w * 2, s[2])], WEB, thread, facing=face)


def skull(m, p, yaw=0.0, scale=1.0, jaw=True, seed=0.0, colour=BONE):
    """A skull standing on `p`, looking along `yaw` (0: toward +z)."""
    k = 0.85 + 0.25 * ((math.sin(seed * 12.9898 + p[0] * 3.1 + p[2] * 1.7) * 43758.5453) % 1.0)
    bone = (colour[0] * k, colour[1] * k, colour[2] * k, 1.0)
    dark = (0.02, 0.018, 0.015, 1.0)
    t = Placed(m, p, yaw, scale)
    y0 = 0.045 if jaw else 0.0
    t.tube([(0, y0, -0.01), (0, y0 + 0.03, -0.01), (0, y0 + 0.08, -0.012), (0, y0 + 0.125, -0.012), (0, y0 + 0.16, -0.015), (0, y0 + 0.178, -0.015)],
           [0.045, 0.068, 0.082, 0.08, 0.055, 0.015], 8, "painted", bone, caps=True, squash=(0.88, 1.08))
    # The face: sockets, the nose, the teeth.
    z = 0.078
    for s in (-1, 1):
        t.poly([(s * 0.012, y0 + 0.07, z), (s * 0.05, y0 + 0.066, z - 0.008), (s * 0.052, y0 + 0.1, z - 0.008), (s * 0.016, y0 + 0.104, z)], "painted", dark,
               facing=(0, 0, 1))
    t.poly([(-0.011, y0 + 0.035, z + 0.004), (0.011, y0 + 0.035, z + 0.004), (0.0, y0 + 0.066, z + 0.004)], "painted", dark, facing=(0, 0, 1))
    t.box((-0.036, y0 - 0.002, 0.03), (0.036, y0 + 0.028, z), "painted", bone, faces="xXZy")
    for i in range(5):
        x = -0.03 + i * 0.015
        t.poly([(x - 0.001, y0, z + 0.002), (x + 0.001, y0, z + 0.002), (x + 0.001, y0 + 0.024, z + 0.002), (x - 0.001, y0 + 0.024, z + 0.002)], "painted", dark,
               facing=(0, 0, 1))
    if jaw:
        t.box((-0.034, 0.0, 0.0), (0.034, 0.036, z - 0.006), "painted", bone, faces="xXZyY")


def bones(m, a, b, y0, out, rows=3, skulls=True, seed=0, depth=0.16):
    """A stack of long bones, ends outward, along the back of a niche or a
    shelf from (x, z) `a` to `b`, with a row of skulls on top."""
    rng = random.Random(seed)
    length = math.hypot(b[0] - a[0], b[1] - a[1])
    if length < 0.1:
        return
    n = math.hypot(out[0], out[1]) or 1.0
    ox, oz = out[0] / n, out[1] / n
    ux, uz = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    yaw = math.atan2(ox, oz)
    y = y0
    for row in range(rows):
        d = (row % 2) * 0.045
        while d < length - 0.03:
            r = rng.uniform(0.022, 0.036)
            k = rng.uniform(0.75, 1.1)
            c = (BONE[0] * k, BONE[1] * k, BONE[2] * k, 1.0)
            x, z = a[0] + ux * d, a[1] + uz * d
            stick = rng.uniform(0.6, 1.0) * depth
            m.tube([(x, y + r, z), (x + ox * stick * 0.8, y + r, z + oz * stick * 0.8), (x + ox * stick, y + r, z + oz * stick)], [r * 0.7, r * 0.75, r], 6,
                   "painted", c, caps=True)
            d += r * 2.0 + rng.uniform(0.004, 0.02)
        y += 0.062
    if skulls:
        d = rng.uniform(0.08, 0.14)
        while d < length - 0.08:
            x, z = a[0] + ux * d + ox * depth * 0.45, a[1] + uz * d + oz * depth * 0.45
            skull(m, (x, y, z), yaw + rng.uniform(-0.35, 0.35), rng.uniform(0.9, 1.05), jaw=rng.random() < 0.4, seed=d)
            d += rng.uniform(0.19, 0.3)


def figure(m, p, yaw=0.0, height=1.75, mat="stone_church", colour=(0.52, 0.5, 0.47), hooded=True, bowed=0.0):
    """A standing hooded figure in stone, its hands in its sleeves and
    nothing in its hood: for a niche, a tomb's end, the top of a buttress.
    It stands on `p` and faces `yaw` (0: toward +z). `bowed` leans its head
    forward. (The shape is the crypt's, env_crypt.monk, which read best.)"""
    c = (colour[0], colour[1], colour[2], 1.0)
    dark = (colour[0] * 0.55, colour[1] * 0.55, colour[2] * 0.55, 1.0)
    mid = (colour[0] * 0.8, colour[1] * 0.8, colour[2] * 0.8, 1.0)
    t = Placed(m, p, yaw, height / 1.75)
    t.tube([(0, 0.0, 0), (0, 0.05, 0), (0, 0.6, 0), (0, 1.15, 0), (0, 1.36, 0), (0, 1.45, 0), (0, 1.5, 0)], [0.29, 0.285, 0.25, 0.235, 0.25, 0.19, 0.09], 10, mat,
           [dark, dark, mid, c, c, c, c], squash=(1.0, 0.62))
    # The cowl's cape over the shoulders.
    t.tube([(0, 1.2, 0.005), (0, 1.3, 0.005), (0, 1.47, 0.0)], [0.272, 0.268, 0.16], 10, mat, [dark, c, c], squash=(1.0, 0.66))
    # The hood, leaning with the head.
    lean = bowed * 0.1
    t.tube([(0, 1.43, 0.0), (0, 1.5, lean * 0.3), (0, 1.6, lean * 0.8), (0, 1.7, lean * 0.9), (0, 1.77, lean * 0.6 - 0.02), (0, 1.8, lean * 0.4 - 0.04)],
           [0.1, 0.12, 0.128, 0.108, 0.056, 0.01], 10, mat, c, caps=True, squash=(1.0, 1.05))
    if hooded:
        # The hood's opening: nothing in it.
        zf, yf = 0.128 * 1.05 + lean * 0.8 - 0.012, 1.585 - bowed * 0.035
        t.poly([(math.cos(math.tau * i / 10) * 0.066, yf + math.sin(math.tau * i / 10) * 0.105, zf + 0.012 * abs(math.sin(math.tau * i / 10))) for i in range(10)],
               "window_dark", (0.0, 0.0, 0.0, 1.0), facing=(0, 0, 1))
    # The arms, the hands lost in the sleeves; the sleeves' ends hanging from the wrists.
    t.tube([(-0.232, 1.33, 0.02), (-0.262, 1.08, 0.07), (-0.09, 0.98, 0.165), (0.09, 0.98, 0.165), (0.262, 1.08, 0.07), (0.232, 1.33, 0.02)],
           [0.07, 0.085, 0.076, 0.076, 0.085, 0.07], 6, mat, [c, mid, mid, mid, mid, c])
    t.tube([(0, 1.0, 0.15), (0, 0.82, 0.14), (0, 0.6, 0.115)], [0.125, 0.11, 0.07], 6, mat, [mid, mid, dark], caps=True, squash=(1.0, 0.42))


def effigy(m, p, yaw=0.0, length=1.8, mat="stone_church", colour=(0.62, 0.6, 0.56)):
    """A figure lying on a tomb: `p` is the middle of the slab's top, and
    the head lies toward `yaw` + 90 degrees' right (its local -x)."""
    c = (colour[0], colour[1], colour[2], 1.0)
    shade = (colour[0] * 0.7, colour[1] * 0.7, colour[2] * 0.7, 1.0)
    t = Placed(m, p, yaw, length / 1.8)
    h = 0.11
    t.tube([(0.9, h * 0.8, 0), (0.84, h, 0), (0.3, h, 0), (-0.1, h * 1.1, 0), (-0.42, h * 1.15, 0), (-0.56, h * 1.1, 0)], [0.07, 0.1, 0.13, 0.17, 0.19, 0.12], 8, mat,
           c, caps=True, squash=(1.0, 0.6))
    t.tube([(-0.56, h * 1.2, 0), (-0.62, h * 1.3, 0), (-0.74, h * 1.3, 0), (-0.82, h * 1.2, 0)], [0.07, 0.1, 0.1, 0.04], 8, mat, c, caps=True, squash=(1.0, 0.9))
    t.box((-0.92, 0.0, -0.2), (-0.56, 0.07, 0.2), mat, shade, faces="xXzZY")
    # Hands together on the breast; the feet on a block.
    t.box((-0.3, h * 1.55, -0.035), (-0.14, h * 1.95, 0.035), mat, c, faces="xXzZY")
    t.box((0.86, 0.0, -0.14), (0.96, 0.2, 0.14), mat, shade, faces="xXzZY")


def leaves(m, x0, x1, z0, z1, y, count=60, seed=0, toward=None):
    """Fallen leaves on the ground in a rectangle. `toward` (x, z) heaps
    them up against that side, as wind does in a corner."""
    rng = random.Random(seed)
    for _ in range(count):
        fx, fz = rng.random(), rng.random()
        if toward:
            fx, fz = fx ** (2.2 if toward[0] else 1.0), fz ** (2.2 if toward[1] else 1.0)
            if toward[0] > 0:
                fx = 1.0 - fx
            if toward[1] > 0:
                fz = 1.0 - fz
        x, z = lerp(x0, x1, fx), lerp(z0, z1, fz)
        r, a = rng.uniform(0.038, 0.075), rng.uniform(0.0, math.tau)
        k = rng.uniform(0.5, 1.0)
        # Old, brown and wet: nothing orange, which glows under the lantern.
        c = (0.21 * k, rng.uniform(0.13, 0.2) * k, 0.108 * k, 1.0)
        lift = rng.uniform(0.0, 0.012)
        pts = [(x + math.cos(a + math.tau * i / 4) * r * (1.0 if i % 2 else 0.55), y + (lift if i == 0 else 0.0), z + math.sin(a + math.tau * i / 4) * r * (1.0 if i % 2 else 0.55))
               for i in range(4)]
        m.poly(pts, "painted", c, facing=(0, 1, 0))
