"""Shared parts for the abbey's props (tools/build/prop_abbey_*.py): sawn
timber with its grain running the right way, turned legs, iron straps and
nails, cloth, straw ticks, pots, books, candles.

A prop is a `Prop`: a hard-edged mesh (`hard`: timber, iron, stone) and a
smooth one (`soft`: cloth, pots, wax), written as art/models/prop_<name>.glb.
It stands on the floor at its origin, in the game's space (x right, y up),
sized to the collision its scene already has (game/world/props/prop_<name>.tscn).

Timber uses the material `wood_prop`, which is laid on by each face's own
UVs (not by the world's axes, as walls are), so a board's grain runs along
the board and a door keeps its grain as it swings. Its vertex colour is the
wood's tone: `OAK` and darker.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
from dress import Placed  # noqa: F401  (props build through it)

WOOD = "wood_prop"
IRON = "iron_cart"
CLOTH = "cloth"
PAINT = "painted"
# Tones, as vertex colours. Timber is darkened by its texture, so its tones look pale here;
# cloth, wax, clay and straw have none. Their numbers are linear light, and the lantern is
# strong up close: 0.02 is dark cloth, 0.03 undyed wool, 0.06 pale linen, 0.13 the palest
# thing there is (wax). Anything brighter glows; anything redder than leather turns orange.
OAK = (0.62, 0.54, 0.45)
OAK_DARK = (0.4, 0.34, 0.28)
PINE = (0.7, 0.62, 0.48)
IRON_C = (0.5, 0.48, 0.46, 1.0)
RUST_C = (0.42, 0.3, 0.22, 1.0)
WAX = (0.13, 0.105, 0.06)
STRAW = (0.055, 0.045, 0.026)
UNDYED = (0.032, 0.028, 0.023)   # undyed wool, a monk's blanket
RUSSET = (0.035, 0.018, 0.012)
CLAY = (0.04, 0.025, 0.017)
LINEN = (0.06, 0.053, 0.04)    # a bolster, a shroud, an altar cloth gone grey
PARCHMENT = (0.09, 0.08, 0.055)
LEATHER = (0.025, 0.016, 0.011)
# Texture repeats per metre of timber.
GRAIN = 0.8


def rgba(c, k=1.0):
    return (c[0] * k, c[1] * k, c[2] * k, 1.0)


def tone(base=OAK, spread=0.14):
    """`base`, a little lighter or darker: no two boards alike."""
    return rgba(base, 1.0 + random.uniform(-spread, spread))


def _v(a, b):
    return (b[0] - a[0], b[1] - a[1], b[2] - a[2])


def _add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k, a[2] + b[2] * k)


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _norm(a):
    n = math.sqrt(_dot(a, a)) or 1.0
    return (a[0] / n, a[1] / n, a[2] / n)


def frame(a, b, up=None, roll=0.0):
    """The length from `a` to `b`, and three unit directions: along it, to
    its side, and up from it. `up` picks which way is up (it is squared to
    the length); without it, up is the world's, or +z for an upright."""
    ahead = _v(a, b)
    length = math.sqrt(_dot(ahead, ahead))
    ahead = _norm(ahead)
    if up is None:
        up = (0.0, 1.0, 0.0) if abs(ahead[1]) < 0.9 else (0.0, 0.0, 1.0)
    k = _dot(up, ahead)
    u2 = _norm((up[0] - ahead[0] * k, up[1] - ahead[1] * k, up[2] - ahead[2] * k))
    u1 = _cross(ahead, u2)
    if roll:
        c, s = math.cos(roll), math.sin(roll)
        u1, u2 = _add((u1[0] * c, u1[1] * c, u1[2] * c), u2, s), _add((u2[0] * c, u2[1] * c, u2[2] * c), u1, -s)
    return length, ahead, u1, u2


def beam(m, a, b, w, d=None, colour=None, mat=WOOD, up=None, roll=0.0, ends="ab", end_shade=0.6, taper=1.0):
    """A squared timber from `a` to `b` (the middles of its ends), `w` wide
    (to its side) and `d` deep (up from it). Its grain runs along it. `ends`
    names the ends that get a face; `taper` narrows the `b` end."""
    d = w if d is None else d
    c = rgba(colour) if colour and len(colour) == 3 else (colour or tone())
    length, ahead, u1, u2 = frame(a, b, up, roll)
    u0, v0 = random.random(), random.random()

    def corner(p, s1, s2, k):
        return (p[0] + u1[0] * s1 * w * 0.5 * k + u2[0] * s2 * d * 0.5 * k, p[1] + u1[1] * s1 * w * 0.5 * k + u2[1] * s2 * d * 0.5 * k,
                p[2] + u1[2] * s1 * w * 0.5 * k + u2[2] * s2 * d * 0.5 * k)

    ring = ((-1, -1), (1, -1), (1, 1), (-1, 1))
    across = 0.0
    for i in range(4):
        (s1, s2), (t1, t2) = ring[i], ring[(i + 1) % 4]
        width = w if i % 2 == 0 else d
        pts = [corner(a, s1, s2, 1.0), corner(a, t1, t2, 1.0), corner(b, t1, t2, taper), corner(b, s1, s2, taper)]
        uu0, uu1 = u0 + across * GRAIN, u0 + (across + width) * GRAIN
        uvs = [(uu0, v0), (uu1, v0), (uu1, v0 + length * GRAIN), (uu0, v0 + length * GRAIN)]
        n = ((s1 + t1) * 0.5, (s2 + t2) * 0.5)
        facing = (u1[0] * n[0] + u2[0] * n[1], u1[1] * n[0] + u2[1] * n[1], u1[2] * n[0] + u2[2] * n[1])
        # The underside a little darker, the top a little lighter: it reads as light from above even in the dark.
        k = 1.0 + 0.08 * facing[1]
        m.poly(pts, mat, (c[0] * k, c[1] * k, c[2] * k, 1.0), uvs=uvs, facing=facing)
        across += width
    dark = (c[0] * end_shade, c[1] * end_shade, c[2] * end_shade, 1.0)
    for name, p, way, k in (("a", a, -1.0, 1.0), ("b", b, 1.0, taper)):
        if name in ends:
            pts = [corner(p, s1, s2, k) for s1, s2 in ring]
            uvs = [(u0 + (s1 * 0.5 + 0.5) * w * GRAIN, v0 + (s2 * 0.5 + 0.5) * d * GRAIN * 0.3) for s1, s2 in ring]
            m.poly(pts, mat, dark, uvs=uvs, facing=(ahead[0] * way, ahead[1] * way, ahead[2] * way))


def plank(m, lo, hi, colour=None, along=None, mat=WOOD, ends="ab", end_shade=0.6):
    """A board filling the box `lo`..`hi`. Its grain runs along its longest
    side, or along `along` ("x", "y" or "z")."""
    size = [hi[i] - lo[i] for i in range(3)]
    k = "xyz".index(along) if along else size.index(max(size))
    mid = [(lo[i] + hi[i]) * 0.5 for i in range(3)]
    a, b = list(mid), list(mid)
    a[k], b[k] = lo[k], hi[k]
    if k == 0:
        w, d = size[2], size[1]
    elif k == 2:
        w, d = size[0], size[1]
    else:
        w, d = size[0], size[2]
    beam(m, tuple(a), tuple(b), w, d, colour, mat, ends=ends, end_shade=end_shade)


def boards(m, lo, hi, along, across, n, colour=OAK, gap=0.003, uneven=0.003, ragged=0.0, spread=0.14, mat=WOOD):
    """`n` boards side by side filling the box `lo`..`hi`: their grain runs
    along `along`, and they are laid side by side along `across` (each "x",
    "y" or "z"). Their widths differ; `uneven` steps each a little proud of
    the next (on the box's third axis); `ragged` leaves their ends unlevel."""
    ia, ic = "xyz".index(along), "xyz".index(across)
    it = 3 - ia - ic
    cuts = [0.0] + sorted(random.uniform(0.25, 0.75) + i for i in range(n - 1)) + [float(n)]
    cuts = [c / n for c in cuts]
    for i in range(n):
        a, b = list(lo), list(hi)
        a[ic] = lo[ic] + (hi[ic] - lo[ic]) * cuts[i] + (gap * 0.5 if i else 0.0)
        b[ic] = lo[ic] + (hi[ic] - lo[ic]) * cuts[i + 1] - (gap * 0.5 if i < n - 1 else 0.0)
        step = random.uniform(-uneven, uneven)
        a[it] += step
        b[it] += step
        if ragged:
            a[ia] += random.uniform(0.0, ragged)
            b[ia] -= random.uniform(0.0, ragged)
        plank(m, tuple(a), tuple(b), tone(colour, spread), along=along, mat=mat)


def slab(m, outline, axis, lo, hi, colour=None, mat=WOOD, grain="q", edge_shade=0.75):
    """A board cut to a shape: `outline` is its outline as (p, q) points,
    and it is `lo`..`hi` thick along `axis`. Across "x" the points are
    (z, y); across "z", (x, y); across "y", (x, z). Its grain runs along q,
    or along p with `grain="p"`. For a bench end with a notch cut in its
    foot, a shaped bracket, a headstone."""
    c = rgba(colour) if colour and len(colour) == 3 else (colour or tone())
    u0, v0 = random.random(), random.random()

    def at(p, q, t):
        return {"x": (t, q, p), "z": (p, q, t), "y": (p, t, q)}[axis]

    def way(p, q, t):
        return {"x": (t, q, p), "z": (p, q, t), "y": (p, t, q)}[axis]

    def uv(p, q):
        return (u0 + p * GRAIN, v0 + q * GRAIN) if grain == "q" else (u0 + q * GRAIN, v0 + p * GRAIN)

    n = len(outline)
    area = sum(outline[i][0] * outline[(i + 1) % n][1] - outline[(i + 1) % n][0] * outline[i][1] for i in range(n))
    turn = 1.0 if area > 0.0 else -1.0
    for t, sign in ((lo, -1.0), (hi, 1.0)):
        m.poly([at(p, q, t) for p, q in outline], mat, c, uvs=[uv(p, q) for p, q in outline], facing=way(0.0, 0.0, sign))
    dark = (c[0] * edge_shade, c[1] * edge_shade, c[2] * edge_shade, 1.0)
    run = 0.0
    for i in range(n):
        (p0, q0), (p1, q1) = outline[i], outline[(i + 1) % n]
        length = math.hypot(p1 - p0, q1 - q0)
        uvs = [(u0 + lo * GRAIN, v0 + run * GRAIN), (u0 + hi * GRAIN, v0 + run * GRAIN), (u0 + hi * GRAIN, v0 + (run + length) * GRAIN), (u0 + lo * GRAIN, v0 + (run + length) * GRAIN)]
        m.poly([at(p0, q0, lo), at(p0, q0, hi), at(p1, q1, hi), at(p1, q1, lo)], mat, dark, uvs=uvs, facing=way((q1 - q0) * turn, -(p1 - p0) * turn, 0.0))
        run += length


def turned(m, a, b, profile, colour=None, sides=8, mat=WOOD, caps=True):
    """A lathe-turned piece from `a` to `b`: `profile` is (how far along,
    0..1; radius) pairs. Goes in the smooth mesh if you want it round."""
    c = rgba(colour) if colour and len(colour) == 3 else (colour or tone())
    pts = [tuple(a[i] + (b[i] - a[i]) * t for i in range(3)) for t, _r in profile]
    m.tube(pts, [r for _t, r in profile], sides, mat, c, caps=caps)


def nail(m, p, n, r=0.011, proud=0.006, colour=IRON_C, mat=IRON):
    """A hammered nail head on a face at `p` whose normal is `n`."""
    n = _norm(n)
    _l, _a, u1, u2 = frame(p, _add(p, n))
    tip = _add(p, n, proud)
    ring = [_add(_add(p, u1, math.cos(math.tau * i / 4) * r), u2, math.sin(math.tau * i / 4) * r) for i in range(4)]
    for i in range(4):
        q0, q1 = ring[i], ring[(i + 1) % 4]
        mid = _v(p, ((q0[0] + q1[0]) * 0.5, (q0[1] + q1[1]) * 0.5, (q0[2] + q1[2]) * 0.5))
        m.poly([q0, q1, tip], mat, colour, facing=_add(mid, n, r))


def strap(m, a, b, n, width=0.045, thick=0.006, nails=3, colour=IRON_C, mat=IRON, taper=1.0):
    """An iron strap lying on a face whose normal is `n`, from `a` to `b`
    (points on the face), nailed along its length."""
    n = _norm(n)
    beam(m, _add(a, n, thick * 0.5), _add(b, n, thick * 0.5), width, thick, colour, mat, up=n, end_shade=1.0, taper=taper)
    for i in range(nails):
        t = (i + 0.5) / nails
        nail(m, _add(tuple(a[k] + (b[k] - a[k]) * t for k in range(3)), n, thick), n, r=min(0.011, width * 0.3), colour=colour, mat=mat)


def ring(m, c, n, r=0.05, thick=0.007, colour=IRON_C, mat=IRON, sides=10, hang=None):
    """An iron ring about `c`, lying in the plane whose normal is `n`."""
    n = _norm(n)
    _l, _a, u1, u2 = frame(c, _add(c, n))
    pts = [_add(_add(c, u1, math.cos(math.tau * i / sides) * r), u2, math.sin(math.tau * i / sides) * r) for i in range(sides + 1)]
    m.tube(pts, [thick] * len(pts), 5, mat, colour)


def rope(m, pts, r=0.012, colour=(0.3, 0.25, 0.16), mat=CLOTH, sides=5):
    m.tube(pts, [r] * len(pts), sides, mat, rgba(colour), caps=True)


def sheet(m, f, nu, nv, mat, colour, both=False, uv=(1.0, 1.0), flip=False):
    """A surface: `f(u, v)` gives the point at `u`, `v` (each 0..1), on a
    grid of `nu` by `nv` cells. `colour` is one colour or `colour(u, v)`.
    It faces the way u-then-v turns counter-clockwise (u along x and v
    along z faces down: `flip` turns it over); `both` gives it a back as
    well (cloth seen from under)."""
    def grid():
        ids = []
        for j in range(nv + 1):
            row = []
            for i in range(nu + 1):
                u, v = i / nu, j / nv
                p = f(u, v)
                c = colour(u, v) if callable(colour) else colour
                row.append(m.vert(p[0], p[1], p[2], rgba(c) if len(c) == 3 else c, (u * uv[0], v * uv[1])))
            ids.append(row)
        return ids

    ids = grid()
    for j in range(nv):
        for i in range(nu):
            quad = (ids[j][i], ids[j][i + 1], ids[j + 1][i + 1], ids[j + 1][i])
            m.face(tuple(reversed(quad)) if flip else quad, mat)
    if both:
        flip = not flip
        ids = grid()
        for j in range(nv):
            for i in range(nu):
                quad = (ids[j][i], ids[j][i + 1], ids[j + 1][i + 1], ids[j + 1][i])
                m.face(tuple(reversed(quad)) if flip else quad, mat)


def tick(m, x0, x1, z0, z1, y0, h, colour=STRAW, lumps=0.25, seed=0.0, mat=CLOTH, edge=0.16, hollow=None):
    """A straw-stuffed tick (a mattress, a bolster, a full sack lying down):
    a pillow shape `h` high on `y0`, lumpy. `hollow` (u, v, depth) presses
    the shape of a sleeper into it."""
    def f(u, v):
        e = min(porter.smoothstep(0.0, edge, u) * porter.smoothstep(0.0, edge, 1.0 - u), 1.0) * min(porter.smoothstep(0.0, edge, v) * porter.smoothstep(0.0, edge, 1.0 - v), 1.0)
        x, z = porter.lerp(x0, x1, u), porter.lerp(z0, z1, v)
        y = h * (e ** 0.45) * (1.0 + lumps * porter.fbm(x, z, 4.0, 3, seed))
        if hollow:
            y -= hollow[2] * math.exp(-(((u - hollow[0]) / 0.3) ** 2 + ((v - hollow[1]) / 0.32) ** 2))
        return (x, y0 + max(y, 0.0), z)

    def c(u, v):
        x, z = porter.lerp(x0, x1, u), porter.lerp(z0, z1, v)
        k = 0.8 + 0.25 * porter.fbm(x, z, 2.5, 3, seed + 3.0)
        return rgba(colour, k)

    nu = max(4, int(round(abs(x1 - x0) / 0.14)))
    nv = max(4, int(round(abs(z1 - z0) / 0.14)))
    sheet(m, f, nu, nv, mat, c, flip=True)


def blanket(m, x0, x1, z0, z1, y, drop=0.2, colour=UNDYED, rumple=0.02, seed=0.0, mat=CLOTH, foot=True, stripe=None, cell=0.11):
    """A blanket lying over a bed's top (`x0`..`x1`, `z0`..`z1` at height
    `y`), hanging `drop` down both long sides and, with `foot`, down the
    `z1` end, its hem uneven. `stripe` is a second colour woven across it."""
    wide, long = x1 - x0, z1 - z0
    total_u = wide + 2.0 * drop
    total_v = long + (drop if foot else 0.0)

    def f(u, v):
        s, t = u * total_u - drop, v * total_v
        x = x0 + min(max(s, 0.0), wide)
        z = z0 + min(t, long)
        down = max(-s, s - wide, 0.0) + max(t - long, 0.0)
        hem = 1.0 + 0.18 * porter.fbm(x + s, z + t, 3.0, 2, seed + 5.0)
        out = 0.012 + 0.03 * porter.smoothstep(0.0, drop, down) + 0.012 * porter.fbm(s * 2.0, t, 5.0, 2, seed + 9.0)
        px = x + (out if s > wide else -out if s < 0.0 else 0.0)
        pz = z + (out if t > long else 0.0)
        py = y - down * hem + (rumple * (1.0 + porter.fbm(s, t, 6.0, 3, seed)) if down == 0.0 else 0.0)
        return (px, py, pz)

    def c(u, v):
        s, t = u * total_u, v * total_v
        k = 0.82 + 0.22 * porter.fbm(s, t, 3.0, 3, seed + 2.0)
        if stripe and (int(t / 0.09) % 7) in (0, 2):
            return rgba(stripe, k)
        return rgba(colour, k)

    sheet(m, f, max(4, int(round(total_u / cell))), max(4, int(round(total_v / cell))), mat, c, both=True)


def heap(m, p, rx, rz, h, colour=UNDYED, seed=0.0, mat=CLOTH, folds=0.3):
    """Cloth thrown down in a heap at `p`: a blanket pushed back, a habit
    dropped on the floor."""
    def f(u, v):
        a, r = u * math.tau, v
        k = 1.0 + folds * porter.fbm(math.cos(a) * 2.0, math.sin(a) * 2.0, 1.6, 3, seed)
        x, z = p[0] + math.cos(a) * rx * r * k, p[2] + math.sin(a) * rz * r * k
        y = h * (1.0 - r ** 1.6) * (1.0 + folds * porter.fbm(x, z, 9.0, 3, seed + 4.0))
        return (x, p[1] + max(y, 0.0), z)

    def c(u, v):
        return rgba(colour, 0.75 + 0.3 * porter.fbm(u * 6.0, v * 3.0, 1.0, 3, seed + 1.0))

    sheet(m, f, 12, 5, mat, c)


def pot(m, p, profile, colour=CLAY, sides=10, mat=PAINT, dark_inside=True):
    """A turned pot, bowl, jug or cup standing on `p`: `profile` is
    (height, radius) pairs up its outside. Its mouth is closed with a dark
    disc a little way down, which reads as the inside."""
    c = rgba(colour, 1.0 + random.uniform(-0.15, 0.15))
    pts = [(p[0], p[1] + y, p[2]) for y, _r in profile]
    m.tube(pts, [r for _y, r in profile], sides, mat, c)
    m.poly([(p[0] + math.cos(math.tau * i / sides) * profile[0][1], p[1] + 0.001, p[2] + math.sin(math.tau * i / sides) * profile[0][1]) for i in range(sides)], mat, c,
           facing=(0, -1, 0))
    if dark_inside:
        y, r = profile[-1][0] - min(0.02, profile[-1][0] * 0.25), profile[-1][1] * 0.94
        m.poly([(p[0] + math.cos(math.tau * i / sides) * r, p[1] + y, p[2] + math.sin(math.tau * i / sides) * r) for i in range(sides)], mat, rgba(colour, 0.25),
               facing=(0, 1, 0))


def candle(m, p, h=0.14, r=0.013, colour=WAX, lean=0.0, drips=3, mat=PAINT):
    """A tallow candle stub standing on `p`, burnt down and run."""
    c = rgba(colour)
    top = (p[0] + lean * h, p[1] + h, p[2])
    m.tube([p, (p[0] + lean * h * 0.5, p[1] + h * 0.5, p[2]), top], [r * 1.12, r, r * 0.92], 7, mat, [rgba(colour, 0.8), c, c], caps=True)
    m.tube([top, (top[0], top[1] + 0.012, top[2])], [0.0018, 0.0012], 3, mat, (0.02, 0.02, 0.02, 1.0))
    for _ in range(drips):
        a = random.uniform(0.0, math.tau)
        length = random.uniform(0.25, 0.8) * h
        x, z = top[0] + math.cos(a) * r * 0.72, top[2] + math.sin(a) * r * 0.72
        m.tube([(x, top[1] - 0.004, z), (x, top[1] - length * 0.6, z), (x, top[1] - length, z)], [r * 0.3, r * 0.36, r * 0.44], 5, mat, c, caps=True)
    # What has run and set at its foot.
    m.tube([(p[0], p[1], p[2]), (p[0], p[1] + 0.006, p[2])], [r * 2.2, r * 1.3], 7, mat, rgba(colour, 0.85), caps=True)


def book(m, p, yaw=0.0, w=0.25, d=0.35, t=0.06, cover=LEATHER, pages=PARCHMENT, clasps=2):
    """A bound book lying shut on `p` (its middle, underneath): boards in
    leather, bands on its spine (at -x), clasps on its fore-edge."""
    b = Placed(m, p, yaw)
    lid = t * 0.14
    c = rgba(cover)
    b.box((-w * 0.5, 0.0, -d * 0.5), (w * 0.5, lid, d * 0.5), PAINT, c)
    b.box((-w * 0.5, t - lid, -d * 0.5), (w * 0.5, t, d * 0.5), PAINT, rgba(cover, 1.1))
    b.box((-w * 0.5 + 0.004, lid, -d * 0.5 + 0.008), (w * 0.5 - 0.008, t - lid, d * 0.5 - 0.008), PAINT, rgba(pages), faces="XzZ")
    b.box((-w * 0.5 - 0.004, 0.0, -d * 0.5), (-w * 0.5 + 0.006, t, d * 0.5), PAINT, rgba(cover, 0.9), faces="xzZyY")
    for i in range(4):
        z = -d * 0.5 + d * (i + 0.5) / 4
        b.box((-w * 0.5 - 0.009, 0.001, z - 0.006), (-w * 0.5 - 0.003, t - 0.001, z + 0.006), PAINT, rgba(cover, 0.75), faces="xzZyY")
    for i in range(clasps):
        z = -d * 0.5 + d * (i + 1.0) / (clasps + 1.0)
        b.box((w * 0.5 - 0.05, t, z - 0.012), (w * 0.5 + 0.004, t + 0.004, z + 0.012), IRON, IRON_C, faces="xXzZY")
        b.box((w * 0.5, t * 0.35, z - 0.012), (w * 0.5 + 0.004, t + 0.004, z + 0.012), IRON, IRON_C, faces="xXzZy")


class Mirror:
    """A mesh seen in a mirror across x = 0: what is built through it comes
    out left-handed for right, with its faces still looking outward."""

    def __init__(self, mesh):
        self.mesh = mesh

    def vert(self, x, y, z, color=(1.0, 1.0, 1.0, 1.0), uv=(0.0, 0.0)):
        return self.mesh.vert(-x, y, z, color, uv)

    def face(self, indices, mat):
        self.mesh.face(tuple(reversed(tuple(indices))), mat)

    quad = porter.Mesh.quad
    poly = porter.Mesh.poly
    tube = porter.Mesh.tube
    box = porter.Mesh.box


class Prop:
    """One prop's model: `hard` (flat-shaded) and `soft` (smooth) meshes,
    and any `part`s that move on their own."""

    def __init__(self, name):
        self.name = name
        seed = sum(ord(ch) * (i + 1) for i, ch in enumerate(name))
        porter.reset(seed)
        title = name.title().replace("_", "")
        self.hard = porter.Mesh(title)
        self.soft = porter.Mesh(title + "Soft")
        self._parts = []

    def part(self, name, origin=None, smooth=False):
        """A mesh of its own in the model, turning about `origin`: a head
        that turns, a lid that lifts."""
        mesh = porter.Mesh(name)
        self._parts.append((mesh, origin, smooth))
        return mesh

    def export(self):
        if self.hard.faces:
            self.hard.build()
        if self.soft.faces:
            self.soft.build(smooth=True)
        for mesh, origin, smooth in self._parts:
            if mesh.faces:
                mesh.build(smooth=smooth, origin=origin)
        return porter.export("prop_" + self.name)


def run(builders):
    """Builds the props named on the command line (after "--"), or all of
    them: `builders` maps a prop's name to a function taking its `Prop`."""
    only = porter.argv()
    for name, fn in builders.items():
        if only and name not in only:
            continue
        prop = Prop(name)
        fn(prop)
        prop.export()
