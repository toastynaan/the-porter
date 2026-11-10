"""Masonry and roofs shared by the city's build scripts (the wall, Aldgate,
the houses inside it, the skyline): faces cut into small pieces so each
vertex can carry its own grime, round towers, pointed arches, battlements.

Everything takes a porter.Mesh and works in the game's space (metres, +Y
up). Stone, plaster and timber are mapped by the materials themselves (in
world space), so only roofs and glass are given UVs here.
"""
import math

from porter import fbm, lerp, smoothstep

# Vertex colours multiply the material's own. Stone: clean, damp at the foot
# (darker and greener), and the dark that runs down from a parapet.
STONE = (0.86, 0.85, 0.82)
STONE_DAMP = (0.42, 0.47, 0.4)
STONE_DARK = (0.5, 0.5, 0.5)


def rgba(c, k=1.0):
    return (c[0] * k, c[1] * k, c[2] * k, 1.0)


def stone_tint(foot, top, clean=STONE, damp=STONE_DAMP, seed=0.0):
    """How a stone face is stained, as a function of a point on it: rising
    damp from `foot`, streaks down from `top`, and slow blotches."""
    def tint(x, y, z):
        along = x + z
        rise = 1.8 + 1.3 * fbm(along, seed, 0.11, 2, 3.0 + seed)
        wet = 1.0 - smoothstep(0.1, max(rise, 0.5), y - foot)
        run = fbm(along * 1.3, y * 0.07, 1.0, 2, 5.0 + seed)
        streak = smoothstep(top - 3.2, top - 0.2, y) * smoothstep(-0.1, 0.5, run)
        blot = 0.88 + 0.16 * fbm(along, y, 0.09, 3, 9.0 + seed)
        k = blot * (1.0 - 0.38 * streak)
        return (lerp(clean[0], damp[0], wet * 0.9) * k, lerp(clean[1], damp[1], wet * 0.9) * k,
                lerp(clean[2], damp[2], wet * 0.9) * k, 1.0)
    return tint


def flat_tint(c, k=1.0):
    c = rgba(c, k)
    return lambda x, y, z: c


def steps(a, b, step):
    """From a to b in pieces no longer than `step`."""
    n = max(int(math.ceil(abs(b - a) / step - 1e-6)), 1)
    return [a + (b - a) * i / n for i in range(n + 1)]


def panel(m, a, b, y0, y1, out, mat, tint, step=2.0, rise=1.2, lean=0.0, top=None):
    """An upright face from (x, z) `a` to `b`, between heights y0 and y1, cut
    into pieces `step` along and `rise` up, each vertex tinted by
    tint(x, y, z). `lean` pushes its foot outward by that much (a battered
    wall). `top` (a function of the distance along, 0..1) gives a top edge
    that isn't level."""
    length = math.hypot(b[0] - a[0], b[1] - a[1])
    if length < 1e-5 or y1 - y0 < 1e-5:
        return
    us = steps(0.0, 1.0, step / length)
    n = math.hypot(out[0], out[2]) or 1.0
    ox, oz = out[0] / n, out[2] / n

    def point(u, v):
        hi = top(u) if top else y1
        y = y0 + (hi - y0) * v
        push = lean * (1.0 - v)
        x, z = a[0] + (b[0] - a[0]) * u + ox * push, a[1] + (b[1] - a[1]) * u + oz * push
        return (x, y, z)

    vs = steps(0.0, 1.0, rise / (y1 - y0))
    for i in range(len(us) - 1):
        for j in range(len(vs) - 1):
            pts = [point(us[i], vs[j]), point(us[i + 1], vs[j]), point(us[i + 1], vs[j + 1]), point(us[i], vs[j + 1])]
            m.poly(pts, mat, [tint(*p) for p in pts], facing=(ox, 0.25 * lean, oz))


def slab(m, lo, hi, mat, tint, faces="xXzZY", step=2.5):
    """A box whose sides are panels (tinted, cut small) and whose top and
    bottom are single faces."""
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    if "x" in faces:
        panel(m, (x0, z0), (x0, z1), y0, y1, (-1, 0, 0), mat, tint, step)
    if "X" in faces:
        panel(m, (x1, z0), (x1, z1), y0, y1, (1, 0, 0), mat, tint, step)
    if "z" in faces:
        panel(m, (x0, z0), (x1, z0), y0, y1, (0, 0, -1), mat, tint, step)
    if "Z" in faces:
        panel(m, (x0, z1), (x1, z1), y0, y1, (0, 0, 1), mat, tint, step)
    for name, y, up in (("y", y0, -1), ("Y", y1, 1)):
        if name in faces:
            pts = [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)]
            m.poly(pts, mat, [tint(*p) for p in pts], facing=(0, up, 0))


def block(m, lo, hi, mat, color, faces="xXzZyY"):
    """A plain box of one colour (a beam, a merlon, a step)."""
    c = color if len(color) == 4 else rgba(color)
    m.box(lo, hi, mat, c, faces=faces)


def arch_profile(half, spring, rise, n=8, cx=0.0):
    """The points of a pointed arch from its right-hand springing over the
    apex to its left: two arcs struck from the springing line."""
    e = (rise * rise - half * half) / (2.0 * half)
    r = half + e
    top = math.atan2(rise, e)
    right = [(cx - e + r * math.cos(top * i / n), spring + r * math.sin(top * i / n)) for i in range(n + 1)]
    left = [(2 * cx - x, y) for x, y in reversed(right[:-1])]
    return right + left


def arch_height(half, spring, rise, x, cx=0.0):
    """How high the arch's opening is at x (0 outside it)."""
    d = abs(x - cx)
    if d >= half:
        return 0.0
    e = (rise * rise - half * half) / (2.0 * half)
    r = half + e
    return spring + math.sqrt(max(r * r - (d + e) ** 2, 0.0))


def arch_wall(m, z, x0, x1, y0, y1, half, spring, rise, out, mat, tint, cx=0.0, along="x", n=8):
    """An upright face with a pointed archway through it. The face lies at
    `z` and runs x0..x1 (or, with along="z", lies at x = `z` and runs along
    z); the arch is `half` wide each side of cx, springs at `spring` and
    rises `rise` more."""
    def at(u, y):
        return (u, y, z) if along == "x" else (z, y, u)

    def flat(u0, u1, ya, yb):
        a, b = ((u0, z), (u1, z)) if along == "x" else ((z, u0), (z, u1))
        panel(m, a, b, ya, yb, out, mat, tint, 1.6, 1.2)

    apex = spring + rise
    over = min(apex + 0.25, y1)
    flat(x0, cx - half, y0, over)
    flat(cx + half, x1, y0, over)
    if y1 > over:
        flat(x0, x1, over, y1)
    prof = arch_profile(half, spring, rise, n, cx)
    for (xa, ya), (xb, yb) in zip(prof, prof[1:]):
        pts = [at(xa, ya), at(xb, yb), at(xb, over), at(xa, over)]
        m.poly(pts, mat, [tint(*p) for p in pts], facing=out)


def vault(m, z0, z1, half, spring, rise, mat, tint, cx=0.0, along="x", n=8, walls=True, y0=0.0, step=1.6):
    """The inside of an archway from z0 to z1: its two walls up to the
    springing and the pointed vault over them."""
    def at(u, y, w):
        return (u, y, w) if along == "x" else (w, y, u)

    prof = arch_profile(half, spring, rise, n, cx)
    if walls:
        prof = [(cx + half, y0)] + prof + [(cx - half, y0)]
    ws = steps(z0, z1, step)
    for (xa, ya), (xb, yb) in zip(prof, prof[1:]):
        inward = (cx - (xa + xb) * 0.5, (spring * 0.6) - (ya + yb) * 0.5, 0.0)
        facing = inward if along == "x" else (0.0, inward[1], inward[0])
        ys = steps(0.0, 1.0, 1.2 / max(abs(yb - ya), 1.2))
        for wa, wb in zip(ws, ws[1:]):
            for ta, tb in zip(ys, ys[1:]):
                p = [at(lerp(xa, xb, ta), lerp(ya, yb, ta), wa), at(lerp(xa, xb, tb), lerp(ya, yb, tb), wa),
                     at(lerp(xa, xb, tb), lerp(ya, yb, tb), wb), at(lerp(xa, xb, ta), lerp(ya, yb, ta), wb)]
                m.poly(p, mat, [tint(*q) for q in p], facing=facing)


def arch_band(m, z, half, spring, rise, width, proud, out, mat, color, cx=0.0, along="x", n=8, y0=None):
    """A band of stone following an arch (a hood mould, or the voussoirs):
    `width` wide outside the opening, standing `proud` of the face at `z`."""
    def at(u, y, w):
        return (u, y, w) if along == "x" else (w, y, u)

    s = 1.0 if (out[2] if along == "x" else out[0]) > 0 else -1.0
    inner = arch_profile(half, spring, rise, n, cx)
    k = (half + width) / half
    outer = [(cx + (x - cx) * k, spring + (y - spring) * (rise + width) / rise) for x, y in inner]
    if y0 is not None:
        inner = [(cx + half, y0)] + inner + [(cx - half, y0)]
        outer = [(cx + half + width, y0)] + outer + [(cx - half - width, y0)]
    zf = z + s * proud
    c = color if len(color) == 4 else rgba(color)
    for i in range(len(inner) - 1):
        a, b, c2, d = inner[i], inner[i + 1], outer[i + 1], outer[i]
        m.poly([at(a[0], a[1], zf), at(b[0], b[1], zf), at(c2[0], c2[1], zf), at(d[0], d[1], zf)], mat, c, facing=out)
        # Its outer edge, back to the wall.
        mid = (cx - (c2[0] + d[0]) * 0.5, spring - (c2[1] + d[1]) * 0.5)
        edge_out = (-mid[0], -mid[1], 0.0) if along == "x" else (0.0, -mid[1], -mid[0])
        m.poly([at(d[0], d[1], zf), at(c2[0], c2[1], zf), at(c2[0], c2[1], z), at(d[0], d[1], z)], mat, c, facing=edge_out)


def drum(m, cx, cz, ys, radii, sides, mat, tint, arc=(0.0, math.tau), rise=1.3):
    """A round tower's wall: rings at heights `ys` with `radii`, `sides`
    round the whole circle, only the part of it within `arc` (radians,
    0 = +x, turning toward +z). Each stretch between rings is cut again
    every `rise` metres for the tint."""
    a0, a1 = arc
    count = max(int(round(sides * (a1 - a0) / math.tau)), 1)
    angles = [a0 + (a1 - a0) * i / count for i in range(count + 1)]
    for k in range(len(ys) - 1):
        cuts = steps(0.0, 1.0, rise / max(ys[k + 1] - ys[k], 1e-3)) if ys[k + 1] - ys[k] > rise else [0.0, 1.0]
        for ta, tb in zip(cuts, cuts[1:]):
            ya, yb = lerp(ys[k], ys[k + 1], ta), lerp(ys[k], ys[k + 1], tb)
            ra, rb = lerp(radii[k], radii[k + 1], ta), lerp(radii[k], radii[k + 1], tb)
            for i in range(count):
                p = []
                for ang, y, r in ((angles[i], ya, ra), (angles[i + 1], ya, ra), (angles[i + 1], yb, rb), (angles[i], yb, rb)):
                    p.append((cx + math.cos(ang) * r, y, cz + math.sin(ang) * r))
                if ra < 1e-4:
                    p = [p[0], p[2], p[3]]
                elif rb < 1e-4:
                    p = p[:3]
                mid = (angles[i] + angles[i + 1]) * 0.5
                slope = (ra - rb) / max(yb - ya, 1e-3)
                m.poly(p, mat, [tint(*q) for q in p], facing=(math.cos(mid), slope, math.sin(mid)))


def disc(m, cx, cz, y, r, sides, mat, color, up=1, arc=(0.0, math.tau)):
    """A flat round floor (or, with up=-1, a ceiling)."""
    a0, a1 = arc
    count = max(int(round(sides * (a1 - a0) / math.tau)), 1)
    pts = [(cx + math.cos(a0 + (a1 - a0) * i / count) * r, y, cz + math.sin(a0 + (a1 - a0) * i / count) * r)
           for i in range(count + (0 if a1 - a0 >= math.tau - 1e-6 else 1))]
    c = color if len(color) == 4 else rgba(color)
    m.poly(pts, mat, c, facing=(0, up, 0))


def ring_battlements(m, cx, cz, y, r, sides, mat, tint, thick=0.45, wall=0.9, merlon=0.95, every=2, arc=(0.0, math.tau),
                     broken=()):
    """A parapet round a tower's top: a low wall `wall` high and `thick`
    through, with a merlon on every `every`th side (`broken` lists merlons
    that have fallen)."""
    a0, a1 = arc
    count = max(int(round(sides * (a1 - a0) / math.tau)), 1)
    angles = [a0 + (a1 - a0) * i / count for i in range(count + 1)]
    ri = r - thick
    for i in range(count):
        aa, ab = angles[i], angles[i + 1]
        top = y + wall + (merlon if i % every == 0 and (i // every) not in broken else 0.0)
        mid = (aa + ab) * 0.5
        o = [(cx + math.cos(a) * r, cz + math.sin(a) * r) for a in (aa, ab)]
        n = [(cx + math.cos(a) * ri, cz + math.sin(a) * ri) for a in (aa, ab)]
        out = (math.cos(mid), 0.0, math.sin(mid))
        for pts, facing in (
                ([(o[0][0], y, o[0][1]), (o[1][0], y, o[1][1]), (o[1][0], top, o[1][1]), (o[0][0], top, o[0][1])], out),
                ([(n[0][0], y, n[0][1]), (n[1][0], y, n[1][1]), (n[1][0], top, n[1][1]), (n[0][0], top, n[0][1])],
                 (-out[0], 0.0, -out[2])),
                ([(o[0][0], top, o[0][1]), (o[1][0], top, o[1][1]), (n[1][0], top, n[1][1]), (n[0][0], top, n[0][1])], (0, 1, 0)),
                ([(o[0][0], y + wall, o[0][1]), (n[0][0], y + wall, n[0][1]), (n[0][0], top, n[0][1]), (o[0][0], top, o[0][1])],
                 (math.sin(mid), 0.0, -math.cos(mid))),
                ([(o[1][0], y + wall, o[1][1]), (n[1][0], y + wall, n[1][1]), (n[1][0], top, n[1][1]), (o[1][0], top, o[1][1])],
                 (-math.sin(mid), 0.0, math.cos(mid)))):
            if facing[1] == 0 and abs(pts[0][1] - pts[2][1]) < 1e-6:
                continue
            m.poly(pts, mat, [tint(*p) for p in pts], facing=facing)


def battlements(m, a, b, y, out, mat, tint, thick=0.5, wall=1.0, merlon=1.0, width=1.4, gap=0.9, skip=None):
    """A parapet along the top of a straight wall from (x, z) `a` to `b`:
    its outer face flush with the line a-b, `thick` back from it. `skip`
    (a function of the distance along in metres) says where the merlons
    have fallen."""
    length = math.hypot(b[0] - a[0], b[1] - a[1])
    if length < 0.3:
        return
    ux, uz = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    n = math.hypot(out[0], out[2])
    ox, oz = out[0] / n, out[2] / n
    count = max(int(round(length / (width + gap))), 1)
    pitch = length / count
    w = pitch * width / (width + gap)

    def piece(d0, d1, y0, y1, ends):
        p = [(a[0] + ux * d0, a[1] + uz * d0), (a[0] + ux * d1, a[1] + uz * d1)]
        q = [(x - ox * thick, z - oz * thick) for x, z in p]
        panel(m, p[0], p[1], y0, y1, (ox, 0, oz), mat, tint, 3.0, 1.5)
        panel(m, q[0], q[1], y0, y1, (-ox, 0, -oz), mat, tint, 3.0, 1.5)
        top = [(p[0][0], y1, p[0][1]), (p[1][0], y1, p[1][1]), (q[1][0], y1, q[1][1]), (q[0][0], y1, q[0][1])]
        m.poly(top, mat, [tint(*t) for t in top], facing=(0, 1, 0))
        if ends:
            for (px, pz), (qx, qz), s in ((p[0], q[0], -1), (p[1], q[1], 1)):
                e = [(px, y0, pz), (qx, y0, qz), (qx, y1, qz), (px, y1, pz)]
                m.poly(e, mat, [tint(*t) for t in e], facing=(ux * s, 0, uz * s))

    piece(0.0, length, y, y + wall, False)
    for i in range(count):
        d0 = i * pitch + (pitch - w) * 0.5
        if skip and skip(d0 + w * 0.5):
            continue
        piece(d0, d0 + w, y + wall, y + wall + merlon, True)


def cone(m, cx, cz, y0, y1, r, sides, mat, color, over=0.0, tile=1.6):
    """A conical roof: its eaves at y0 (radius r + over), its point at y1."""
    c = color if len(color) == 4 else rgba(color)
    r += over
    slope = math.hypot(r, y1 - y0)
    for i in range(sides):
        a, b = math.tau * i / sides, math.tau * (i + 1) / sides
        pa, pb = (cx + math.cos(a) * r, y0, cz + math.sin(a) * r), (cx + math.cos(b) * r, y0, cz + math.sin(b) * r)
        w = math.dist(pa, pb)
        m.poly([pa, pb, (cx, y1, cz)], mat, c, [(0.0, 0.0), (w / tile, 0.0), (w * 0.5 / tile, slope / tile)],
               facing=(math.cos((a + b) * 0.5), 0.6, math.sin((a + b) * 0.5)))
    disc(m, cx, cz, y0, r, sides, mat, (0.2, 0.2, 0.2), up=-1)


def spire(m, cx, cz, y0, y1, r, mat, color, sides=8, tile=1.6):
    """A church spire: a tall thin cone."""
    cone(m, cx, cz, y0, y1, r, sides, mat, color, tile=tile)


def gable_roof(m, x0, x1, z0, z1, eave, ridge, mat, color, along="x", over=0.3, tile=1.8, under=(0.25, 0.25, 0.25), sag=0.0):
    """A pitched roof over the rectangle x0..x1 by z0..z1, its ridge along
    `along` at height `ridge`, eaves at `eave`, overhanging by `over`. The
    undersides are made too. UVs run in tiles `tile` metres wide. `sag`
    lets the ridge dip in the middle (an old roof)."""
    c = color if len(color) == 4 else rgba(color)
    cu = rgba(under)
    if along == "x":
        half = (z1 - z0) * 0.5
        mid = (z0 + z1) * 0.5
        run = half + over
        drop = (ridge - eave) * over / half
        slope = math.hypot(run, ridge - eave + drop)
        xs = steps(x0 - over, x1 + over, (x1 - x0 + 2 * over) / (2 if sag else 1))
        for xa, xb in zip(xs, xs[1:]):
            def ry(x):
                t = (x - (x0 - over)) / (x1 - x0 + 2 * over)
                return ridge - sag * math.sin(math.pi * t)
            for side in (-1, 1):
                pts = [(xa, eave - drop, mid + side * run), (xb, eave - drop, mid + side * run), (xb, ry(xb), mid), (xa, ry(xa), mid)]
                uv = [(xa / tile, 0.0), (xb / tile, 0.0), (xb / tile, slope / tile), (xa / tile, slope / tile)]
                m.poly(pts, mat, c, uv, facing=(0, 1, side * 0.5))
                m.poly(pts, mat, cu, facing=(0, -1, -side * 0.5))
    else:
        half = (x1 - x0) * 0.5
        mid = (x0 + x1) * 0.5
        run = half + over
        drop = (ridge - eave) * over / half
        slope = math.hypot(run, ridge - eave + drop)
        zs = steps(z0 - over, z1 + over, (z1 - z0 + 2 * over) / (2 if sag else 1))
        for za, zb in zip(zs, zs[1:]):
            def ry(z):
                t = (z - (z0 - over)) / (z1 - z0 + 2 * over)
                return ridge - sag * math.sin(math.pi * t)
            for side in (-1, 1):
                pts = [(mid + side * run, eave - drop, za), (mid + side * run, eave - drop, zb), (mid, ry(zb), zb), (mid, ry(za), za)]
                uv = [(za / tile, 0.0), (zb / tile, 0.0), (zb / tile, slope / tile), (za / tile, slope / tile)]
                m.poly(pts, mat, c, uv, facing=(side * 0.5, 1, 0))
                m.poly(pts, mat, cu, facing=(-side * 0.5, -1, 0))


def lancet(m, centre, y0, width, height, out, glass="window_dark", stone="stone_blocks", color=STONE_DARK, proud=0.04,
           frame=0.17):
    """A pointed window on a wall: a stone surround and the glass in it.
    `centre` is (x, z) on the wall's face; `out` the way the wall looks.
    The glass's UV runs 0..1 across and up it."""
    ox, oz = out[0], out[2]
    ax, az = -oz, ox

    def shape(w, h, lift, off):
        hw = w * 0.5
        spring = y0 + lift + h - w * 0.9
        return [(centre[0] + ax * -hw + ox * off, y0 + lift, centre[1] + az * -hw + oz * off),
                (centre[0] + ax * hw + ox * off, y0 + lift, centre[1] + az * hw + oz * off),
                (centre[0] + ax * hw + ox * off, spring, centre[1] + az * hw + oz * off),
                (centre[0] + ox * off, y0 + lift + h, centre[1] + oz * off),
                (centre[0] + ax * -hw + ox * off, spring, centre[1] + az * -hw + oz * off)]

    m.poly(shape(width + frame * 2, height + frame * 1.8, -frame * 0.7, proud), stone, rgba(color), facing=out)
    m.poly(shape(width, height, 0.0, proud + 0.02), glass,
           uvs=[(0.0, 0.0), (1.0, 0.0), (1.0, 1.0 - 0.9 * width / height), (0.5, 1.0), (0.0, 1.0 - 0.9 * width / height)],
           facing=out)


def loop(m, centre, y0, height, out, proud=0.03, width=0.14, cross=True):
    """An arrow loop: a tall dark slit, with a short cross slit."""
    ox, oz = out[0], out[2]
    ax, az = -oz, ox

    def rect(hw, ya, yb):
        return [(centre[0] - ax * hw + ox * proud, ya, centre[1] - az * hw + oz * proud),
                (centre[0] + ax * hw + ox * proud, ya, centre[1] + az * hw + oz * proud),
                (centre[0] + ax * hw + ox * proud, yb, centre[1] + az * hw + oz * proud),
                (centre[0] - ax * hw + ox * proud, yb, centre[1] - az * hw + oz * proud)]

    m.poly(rect(width * 0.5, y0, y0 + height), "window_dark", facing=out)
    if cross:
        m.poly(rect(width * 2.2, y0 + height * 0.55, y0 + height * 0.55 + width), "window_dark", facing=out)
