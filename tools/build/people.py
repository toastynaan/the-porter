"""The people of The Porter: one low-poly human, dressed per character, with
a head whose face the game draws (Look and Feel, "Characters"; the locked
PSX character style: low poly, hand-painted textures at 256 px with nearest
filtering, per-vertex shading; docs/systems/faces.md, "The real faces").

These are the builders: the head, tubes of cloth, limbs, the texture, the
build. What a person is put together from (builds, skins, faces, clothes,
headwear) is the people's kit, tools/build/people_kit.py: a character
script (tools/build/chr_<name>.py) is a spec on that. build() writes to
art/models/:

    chr_<name>.png          the character's texture: a 256 px atlas, painted
                            here (the head in the top-left 128 px, a swatch
                            of 64 px for each cloth, leather, wood...)
    chr_<name>.glb          his body on his skeleton (tools/build/rig.py):
                              Skeleton  the bones, named as Unreal's
                                        mannequin (pelvis, spine_01, Head,
                                        upperarm_r, hand_r, thigh_l...)
                                Body    torso, clothes, limbs, what he holds,
                                        bound to the bones (a hand holds 5 cm
                                        past the wrist: game/people/hand_reach.gd)
                              and his clips: idle, talk, walk, and those his
                              spec adds (sit, sit_talk: the seat at the origin)
    chr_<name>_head.glb     the head, its origin at the neck: Head (material
                            chr_<name>_face, whose shader draws the eyes,
                            brows, mouth and throat the FaceRig moves) and
                            what he wears on it

He is made standing at rest, as his skeleton stands: arms hanging straight
at his sides, legs straight (joints(): where the joints are).

Materials are names only, linked on import to game/people/materials/<name>.tres
(tools/build/link_imports.py): chr_<name> (the atlas, per-vertex shading)
and chr_<name>_face (the same atlas and the face).

Space: metres, +Y up, the figure faces -Z, his right hand is +X, feet at the
origin. Vertex colours carry the shading
the texture doesn't (shade under the arms, in folds, at the hem).
"""
import math
import os
import random
import struct
import sys
import zlib

import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
import rig

TEX = 256
## The atlas: x, y (from the top), width, height in pixels. The head has the
## top-left 128 px; each cloth (leather, wood...) a part asks for with
## swatch() takes the next 64 px cell of the twelve.
CELLS = [(128, 0), (192, 0), (128, 64), (192, 64), (0, 128), (64, 128), (128, 128), (192, 128), (0, 192), (64, 192),
         (128, 192), (192, 192)]
REGIONS = {"head": (0, 0, 128, 128)}
## Each swatch's colour and how it is painted (paint_cloth's keywords).
SWATCHES = {}


def swatch(name, color=None, **paint):
    """A swatch of the atlas named `name`, painted `color` (paint_cloth's
    keywords say how: folds, hem, wear...). The first to ask for a name
    sets it; later calls only return the name. Twelve to a character."""
    if name not in REGIONS:
        assert color is not None, "swatch %s has no colour yet" % name
        assert len(SWATCHES) < len(CELLS), "more than %d cloths on one character: %s" % (len(CELLS), name)
        x, y = CELLS[len(SWATCHES)]
        REGIONS[name] = (x, y, 64, 64)
        SWATCHES[name] = (tuple(color[:3]), paint)
    return name


def reset_atlas():
    for k in list(REGIONS):
        if k != "head":
            del REGIONS[k]
    SWATCHES.clear()


WHITE = (1.0, 1.0, 1.0, 1.0)


def grey(v):
    return (v, v, v, 1.0)


def uv(region, s, t):
    """Atlas UV of the point `s` across and `t` down a region (0..1), half a
    texel in from its edges so nearest filtering never reads a neighbour."""
    x, y, w, h = REGIONS[region]
    s = min(max(s, 0.0), 1.0)
    t = min(max(t, 0.0), 1.0)
    return ((x + 0.5 + s * (w - 1)) / TEX, 1.0 - (y + 0.5 + t * (h - 1)) / TEX)


# ---------------------------------------------------------------- the head

## Columns round the head, radians from the front (+ toward his right): close
## together over the face, wide apart behind it.
HEAD_COLS = [-math.pi, -2.2, -1.35, -0.95, -0.62, -0.32, 0.0, 0.32, 0.62, 0.95, 1.35, 2.2, math.pi]
## Rows up the head from the neck pivot: height, half width, front depth,
## back depth, middle z. Front is -z. One average man's head; a spec scales it.
HEAD_ROWS = [
    (-0.035, 0.054, 0.052, 0.056, 0.006),
    (0.035, 0.049, 0.05, 0.054, 0.004),
    (0.07, 0.052, 0.056, 0.06, 0.0),
    (0.083, 0.054, 0.088, 0.07, 0.0),
    (0.102, 0.068, 0.097, 0.078, 0.0),
    (0.126, 0.07, 0.1, 0.086, 0.0),
    (0.152, 0.073, 0.1, 0.095, 0.0),
    (0.184, 0.075, 0.094, 0.1, 0.0),
    (0.208, 0.076, 0.098, 0.102, 0.0),
    (0.243, 0.073, 0.091, 0.1, 0.002),
    (0.272, 0.061, 0.072, 0.086, 0.004),
    (0.294, 0.036, 0.042, 0.052, 0.006),
]
HEAD_TOP = 0.303
## Where the face is on every head (the face shader's layout, face.gdshader).
EYE = (0.032, 0.184)
MOUTH_Y = 0.126
## The superellipse power: below 1 the head is squarer than an ellipse.
HEAD_E = 0.72


def _spow(v, e):
    return math.copysign(abs(v) ** e, v)


def head_rows(spec):
    """The head's rows for this person: width, jaw, chin and brow scaled;
    `jowl` fills out under the jaw and the neck (a fat face)."""
    hs = spec.get("head", {})
    w = hs.get("width", 1.0)
    jaw = hs.get("jaw", 1.0)
    chin = hs.get("chin", 1.0)
    brow = hs.get("brow", 1.0)
    jowl = hs.get("jowl", 0.0)
    rows = []
    for i, (h, a, f, b, cz) in enumerate(HEAD_ROWS):
        a *= w
        if i in (3, 4):
            a *= jaw
            f = 0.064 + (f - 0.064) * chin
        if i == 5:
            a *= 0.5 + 0.5 * jaw
        if i <= 3:
            a *= 1.0 + jowl * (0.26 if i < 3 else 0.12)
            f *= 1.0 + jowl * (0.22 if i < 3 else 0.0)
        if i == 8:
            f += 0.004 * (brow - 1.0)
        rows.append((h, a, f, b, cz))
    return rows


def head_point(rows, theta, h):
    """A point on the head's skin at angle `theta` and height `h`, before the
    face's own dents (sockets) and the nose are added."""
    hs = [r[0] for r in rows]
    h = min(max(h, hs[0]), hs[-1])
    k = 0
    while k < len(rows) - 2 and h > hs[k + 1]:
        k += 1
    t = (h - hs[k]) / (hs[k + 1] - hs[k])
    r = [rows[k][j] + (rows[k + 1][j] - rows[k][j]) * t for j in range(5)]
    s, c = math.sin(theta), math.cos(theta)
    x = r[1] * _spow(s, HEAD_E)
    z = r[4] + (-r[2] * abs(c) ** HEAD_E if c >= 0.0 else r[3] * abs(c) ** HEAD_E)
    return x, h, z


def head_u(theta):
    """The head's texture across: the front 1.0 rad each side takes 56% of it."""
    a = abs(theta)
    u = 0.28 * a if a <= 1.0 else 0.28 + 0.22 * (a - 1.0) / (math.pi - 1.0)
    return 0.5 + math.copysign(u, theta)


def head_theta(u):
    d = abs(u - 0.5)
    a = d / 0.28 if d <= 0.28 else 1.0 + (d - 0.28) / 0.22 * (math.pi - 1.0)
    return math.copysign(a, u - 0.5)


def head_v(h):
    """Down the head's texture: 0 at the crown, 1 at the neck's foot."""
    return (HEAD_TOP - h) / (HEAD_TOP - HEAD_ROWS[0][0])


def head_uv(theta, h):
    return uv("head", head_u(theta), head_v(h))


def head_mesh(spec, name="Head"):
    """The head: rows of skin from the neck to the crown, a nose, ears; the
    face's dents (eye sockets under the brow, cheekbones) in the vertices.
    Material chr_<name>_face. Origin at the neck pivot."""
    mat = "chr_%s_face" % spec["name"]
    m = porter.Mesh(name)
    rows = head_rows(spec)
    hs = spec.get("head", {})
    grid = []
    for i, row in enumerate(rows):
        ring = []
        for th in HEAD_COLS:
            x, y, z = head_point(rows, th, row[0])
            a = abs(th)
            # Sockets under the brow; the brow over them; cheekbones; a jaw.
            if i == 7 and a < 0.7:
                z += 0.007 * (1.0 - abs(a - 0.32) / 0.4) if a > 0.05 else 0.002
            if i == 8 and a < 0.7:
                z -= 0.003 * hs.get("brow", 1.0)
            if i == 6 and 0.6 < a < 1.2:
                x *= 1.03
                z -= 0.004 * hs.get("cheek", 1.0)
            if i == 4 and 0.8 < a < 1.6:
                x *= 1.0 + 0.04 * (hs.get("jaw", 1.0) - 0.9)
            beard = spec.get("beard_volume", 0.0)
            if beard and i in (3, 4, 5) and a < 1.6:
                grow = beard * (1.0 if i < 5 else 0.5) * (1.0 - 0.4 * a / 1.6)
                if i == 5 and a < 0.4:
                    grow *= 0.2
                x *= 1.0 + grow * 0.25
                z -= grow * 0.012 if a < 1.2 else 0.0
                y -= grow * 0.01 if i == 3 else 0.0
            shade = 1.0
            if i <= 2:
                shade = 0.5 + 0.08 * i
            elif i == 3:
                shade = 0.9
            elif i == 7 and 0.15 < a < 0.6:
                shade = 0.86
            ring.append(m.vert(x, y, z, grey(shade), head_uv(th, row[0])))
        grid.append(ring)
    for r0, r1 in zip(grid, grid[1:]):
        for k in range(len(HEAD_COLS) - 1):
            m.face((r1[k], r1[k + 1], r0[k + 1], r0[k]), mat)
    top = m.vert(0.0, HEAD_TOP, 0.004, WHITE, head_uv(0.0, HEAD_TOP))
    for k in range(len(HEAD_COLS) - 1):
        m.face((top, grid[-1][k + 1], grid[-1][k]), mat)
    # The nose: a ridge from between the eyes to the tip, its sides down to
    # the wings, and under it. Faces turned by the way they look.
    n = hs.get("nose", 1.0)
    nw = hs.get("nose_width", 1.0)
    fz = head_point(rows, 0.0, 0.15)[2]

    def surf(x, y, out=0.0):
        return (x, y, head_point(rows, math.atan2(x, 0.09), y)[2] - out)

    # Broad at the bridge and the tip, standing out no more than a real
    # nose does at this size (narrower and further, it reads as a wedge).
    wing = 0.017 * nw
    tip_x, tip_y, tip_z = 0.0085 * nw, 0.151 - 0.003 * (n - 1.0), fz - 0.0155 * n
    pt = {
        "bl": surf(-0.0065, 0.186, 0.001), "br": surf(0.0065, 0.186, 0.001),
        "tl": (-tip_x, tip_y, tip_z), "tr": (tip_x, tip_y, tip_z),
        "sl": surf(-0.0155, 0.174), "sr": surf(0.0155, 0.174),
        "wl": (-wing, 0.145, fz - 0.004), "wr": (wing, 0.145, fz - 0.004),
        "un": (0.0, 0.141, fz - 0.009),
    }
    shades = {"bl": 1.0, "br": 1.0, "tl": 1.05, "tr": 1.05, "sl": 0.9, "sr": 0.9, "wl": 0.85, "wr": 0.85, "un": 0.62}

    def nose_face(keys, facing):
        pts = [pt[k] for k in keys]
        m.poly(pts, mat, [grey(shades[k]) for k in keys], [head_uv(math.atan2(p[0], -p[2]), p[1]) for p in pts], facing=facing)

    nose_face(("bl", "br", "tr", "tl"), (0.0, 0.3, -1.0))
    nose_face(("sl", "bl", "tl", "wl"), (-1.0, 0.0, -0.6))
    nose_face(("br", "sr", "wr", "tr"), (1.0, 0.0, -0.6))
    nose_face(("tl", "tr", "un"), (0.0, -1.0, -0.4))
    nose_face(("tl", "un", "wl"), (-0.3, -1.0, -0.3))
    nose_face(("tr", "wr", "un"), (0.3, -1.0, -0.3))
    # Ears: a flat flap each side, back from the cheek.
    if hs.get("ears", True):
        for sx in (-1.0, 1.0):
            x0 = head_point(rows, sx * 1.62, 0.17)[0]
            quad = [(x0 - sx * 0.004, 0.198, 0.004), (x0 + sx * 0.012, 0.192, 0.018), (x0 + sx * 0.01, 0.148, 0.016),
                    (x0 - sx * 0.004, 0.142, 0.002)]
            ids = [m.vert(p[0], p[1], p[2], grey(0.82 if j in (1, 2) else 0.7), head_uv(sx * 1.62, p[1])) for j, p in enumerate(quad)]
            m.face(ids if sx > 0 else list(reversed(ids)), mat)
            ids = [m.vert(p[0], p[1], p[2], grey(0.6), head_uv(sx * 1.62, p[1])) for p in quad]
            m.face(list(reversed(ids)) if sx > 0 else ids, mat)
    return m


# ------------------------------------------------------------ cloth tubes

def ring_frame(ahead):
    """The frame of a ring across a tube going `ahead`: its front (where
    angle 0 points: forward, or up for a tube that goes forward) and side."""
    ahead = ahead.normalized()
    front = Vector((0.0, 0.0, -1.0))
    front = front - ahead * front.dot(ahead)
    if front.length < 0.35:
        front = Vector((0.0, 1.0, 0.0)) - ahead * ahead.y
    front.normalize()
    side = Vector((1.0, 0.0, 0.0))
    side = side - ahead * side.dot(ahead) - front * side.dot(front)
    if side.length < 0.2:
        side = ahead.cross(front)
    return front, side.normalized()


def tube(m, mat, centers, radii, sides, region, colors=None, arc=None, caps=(False, False), t_range=(0.0, 1.0),
         inner=None, skip=None, s_scale=1.0):
    """A tube through `centers` (x, y, z). Each radius is r, or (half width,
    front depth, back depth). Angle 0 is the ring's front; the UV seam is at
    the back. `arc` (a0, a1) makes an open shell (a cloak) instead; `inner`
    (a shade) gives it an inside, darker. `skip(i, a)` leaves out the quad
    between rings i and i+1 at angle a (a hood's face opening). Returns the
    rings' vertex indices."""
    pts = [Vector(p) for p in centers]
    n = len(pts)
    colors = colors or [WHITE] * n
    colors = [c if len(c) == 4 else (c[0], c[1], c[2], 1.0) for c in colors]
    a0, a1 = arc if arc else (-math.pi, math.pi)
    angles = [a0 + (a1 - a0) * k / sides for k in range(sides + 1)]
    length = [0.0]
    for a, b in zip(pts, pts[1:]):
        length.append(length[-1] + (b - a).length)
    total = max(length[-1], 1e-6)
    out_rings = []

    def ring_points(i):
        ahead = pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]
        front, side = ring_frame(ahead)
        r = radii[i]
        rx, rf, rb = (r, r, r) if not isinstance(r, (tuple, list)) else r
        out = []
        for a in angles:
            c = math.cos(a)
            q = pts[i] + side * (math.sin(a) * rx) + front * (c * (rf if c >= 0.0 else rb))
            out.append(q)
        return out

    all_pts = [ring_points(i) for i in range(n)]
    # Which way round: the first band's faces must look out from the middle.
    probe = all_pts[0][sides // 2] if n > 1 else all_pts[0][0]
    a_, b_, c_ = all_pts[0][sides // 2], all_pts[0][sides // 2 + 1], all_pts[1][sides // 2]
    normal = (b_ - a_).cross(c_ - a_)
    outward = probe - pts[0]
    flip = normal.dot(outward) < 0.0

    def make(layer_shade, reverse):
        rings = []
        for i in range(n):
            t = t_range[0] + (t_range[1] - t_range[0]) * length[i] / total
            col = colors[i]
            if layer_shade is not None:
                col = (col[0] * layer_shade, col[1] * layer_shade, col[2] * layer_shade, 1.0)
            ring = []
            for k, q in enumerate(all_pts[i]):
                s = ((angles[k] - a0) / (a1 - a0)) * s_scale
                ring.append(m.vert(q.x, q.y, q.z, col, uv(region, s, t)))
            rings.append(ring)
        for i in range(n - 1):
            for k in range(sides):
                if skip and skip(i, (angles[k] + angles[k + 1]) * 0.5):
                    continue
                quad = (rings[i][k], rings[i][k + 1], rings[i + 1][k + 1], rings[i + 1][k])
                if flip != reverse:
                    quad = tuple(reversed(quad))
                m.face(quad, mat)
        return rings

    rings = make(None, False)
    if inner is not None:
        make(inner, True)
    if caps[0]:
        c = m.vert(pts[0].x, pts[0].y, pts[0].z, colors[0], uv(region, 0.5, t_range[0]))
        for k in range(sides):
            tri = (rings[0][k], rings[0][k + 1], c)
            m.face(tri if flip else tuple(reversed(tri)), mat)
    if caps[1]:
        c = m.vert(pts[-1].x, pts[-1].y, pts[-1].z, colors[-1], uv(region, 0.5, t_range[1]))
        for k in range(sides):
            tri = (rings[-1][k], rings[-1][k + 1], c)
            m.face(tuple(reversed(tri)) if flip else tri, mat)
    out_rings.extend(rings)
    return out_rings


def box(m, mat, center, size, region, color=WHITE, top_shade=1.0, yaw=0.0):
    """A box `size` (x, y, z) about `center`, turned `yaw` about Y, all of it
    on one region."""
    cx, cy, cz = center
    hx, hy, hz = size[0] / 2, size[1] / 2, size[2] / 2
    cs, sn = math.cos(yaw), math.sin(yaw)

    def p(x, y, z):
        return (cx + x * cs + z * sn, cy + y, cz - x * sn + z * cs)

    up = (color[0] * top_shade, color[1] * top_shade, color[2] * top_shade, 1.0)
    faces = [
        ([(-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz)], (0, 0, -1)),
        ([(hx, -hy, hz), (-hx, -hy, hz), (-hx, hy, hz), (hx, hy, hz)], (0, 0, 1)),
        ([(-hx, -hy, hz), (-hx, -hy, -hz), (-hx, hy, -hz), (-hx, hy, hz)], (-1, 0, 0)),
        ([(hx, -hy, -hz), (hx, -hy, hz), (hx, hy, hz), (hx, hy, -hz)], (1, 0, 0)),
        ([(-hx, hy, -hz), (hx, hy, -hz), (hx, hy, hz), (-hx, hy, hz)], (0, 1, 0)),
        ([(-hx, -hy, hz), (hx, -hy, hz), (hx, -hy, -hz), (-hx, -hy, -hz)], (0, -1, 0)),
    ]
    uvs = [uv(region, 0, 1), uv(region, 1, 1), uv(region, 1, 0), uv(region, 0, 0)]
    for corners, nrm in faces:
        pts = [p(*c) for c in corners]
        cols = [color if c[1] < 0 else up for c in corners]
        d = (math.cos(yaw) * nrm[0] + math.sin(yaw) * nrm[2], nrm[1], -math.sin(yaw) * nrm[0] + math.cos(yaw) * nrm[2])
        m.poly(pts, mat, cols, uvs, facing=d)


# ------------------------------------------------------------- the figure

def joints(spec=None):
    """Where his joints are standing (rig.JOINTS, set when his skeleton is
    made): x given for his right; mirror() for the left."""
    assert rig.JOINTS, "the skeleton is made first (build())"
    return dict(rig.JOINTS)


def bend(a, c, l1, l2, pole):
    """The middle joint of a limb from `a` to `c`, `l1` and `l2` long, bent
    toward `pole` (a direction)."""
    a, c, pole = Vector(a), Vector(c), Vector(pole).normalized()
    d = c - a
    dist = min(d.length, l1 + l2 - 1e-4)
    d.normalize()
    along = (l1 * l1 - l2 * l2 + dist * dist) / (2.0 * dist)
    h = math.sqrt(max(l1 * l1 - along * along, 0.0))
    perp = pole - d * pole.dot(d)
    perp.normalize()
    return tuple(a + d * along + perp * h)


def lerp3(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def add(a, b):
    return tuple(a[i] + b[i] for i in range(3))


def mirror(p, side):
    return (p[0] * side, p[1], p[2])


def arm(m, mat, spec, side, shoulder, elbow, wrist, hand_dir=(0.0, -1.0, 0.0), sleeve="garment", cuff=None,
        fist=False, wide=1.0):
    """An arm, in one piece: the shoulder rounded over and leaning in to the
    trunk, the sleeve down through the elbow (one ring there, which bends
    with both halves: rig.skin) to the wrist, and the hand. `wide` opens the
    sleeve toward the wrist (a habit's); `cuff` turns its end back."""
    kw = spec.get("limb", spec.get("breadth", 1.0))
    r_sh, r_el, r_wr = 0.062 * kw, 0.047 * kw * (1.0 + (wide - 1.0) * 0.5), 0.036 * kw * wide
    sh, el, wr = Vector(shoulder), Vector(elbow), Vector(wrist)
    up = (sh - el).normalized()
    inward = Vector((-float(side), 0.0, 0.0))
    # The shoulder's cap: over the joint and in toward the neck, so the arm
    # grows out of the trunk and doesn't hang off its side.
    top = sh + up * r_sh * 0.46 + inward * r_sh * 1.0
    cap = sh + up * r_sh * 0.36 + inward * r_sh * 0.3
    cuff_r = r_wr * (1.3 if cuff else 1.1)
    pts = [top, cap, sh, sh + (el - sh) * 0.5, el, el + (wr - el) * 0.5, wr]
    radii = [r_sh * 0.5, r_sh * 0.9, r_sh, r_sh * 0.88, r_el, (r_el + cuff_r) * 0.48, cuff_r]
    tube(m, mat, [tuple(q) for q in pts], radii, 6, sleeve,
         [grey(0.82), grey(0.95), WHITE, WHITE, grey(0.82), WHITE, grey(0.85)], caps=(True, False))
    if cuff:
        ahead = (wr - el).normalized()
        tube(m, mat, [tuple(wr - ahead * 0.05), tuple(wr + ahead * 0.004)], [cuff_r * 1.08, cuff_r * 1.16], 6, cuff,
             [grey(0.7), grey(0.95)])
    hand(m, mat, spec, wr, Vector(hand_dir), side, fist)


def hand(m, mat, spec, wrist, ahead, side, fist=False):
    """A mitten of a hand from the wrist `ahead` (palm in), and a thumb."""
    ahead = ahead.normalized()
    k = spec.get("hand", 1.0)
    length = (0.075 if fist else 0.105) * k
    p0 = Vector(wrist) - ahead * 0.01
    p1 = Vector(wrist) + ahead * (length * 0.45)
    p2 = Vector(wrist) + ahead * length
    front, sd = ring_frame(ahead)
    # Flat across the palm: wide one way, thin the other.
    tube(m, mat, [tuple(p0), tuple(p1), tuple(p2)], [(0.022 * k, 0.03 * k, 0.03 * k), (0.026 * k, 0.04 * k, 0.04 * k),
                                                    (0.018 * k, 0.026 * k, 0.026 * k)] if fist else
         [(0.024 * k, 0.019 * k, 0.019 * k), (0.026 * k, 0.045 * k, 0.045 * k), (0.012 * k, 0.034 * k, 0.034 * k)],
         5, "hands", [grey(0.85), WHITE, grey(0.92)], caps=(False, True))
    # The thumb, forward of the palm.
    t0 = Vector(wrist) + ahead * 0.02 + front * 0.02 * k
    t1 = t0 + ahead * 0.035 * k + front * 0.018 * k
    tube(m, mat, [tuple(t0), tuple(t1)], [0.011 * k, 0.008 * k], 3, "hands", [grey(0.85), WHITE], caps=(False, True))


def leg(m, mat, spec, side, hip, knee, ankle, hose="hose", boot_top=0.24, toe=(0.0, 0.0, -1.0), boot="boots",
        wraps=False):
    """A leg in hose from the hip to the ankle, and a boot (or a shoe, with
    `boot_top` low) on the foot pointing along `toe`. `wraps` (a swatch's
    name) binds cloth round the shin. Bare legs and feet are the skin's swatch."""
    kw = spec.get("limb", spec.get("breadth", 1.0))
    hp, kn, an = Vector(hip), Vector(knee), Vector(ankle)
    r_th, r_kn, r_ca, r_an = 0.074 * kw, 0.048 * kw, 0.054 * kw, 0.034 * kw
    calf = kn + (an - kn) * 0.32
    shin = kn + (an - kn) * 0.75
    top = hp + Vector((0.0, 0.06, 0.0))
    tube(m, mat, [tuple(top), tuple(hp), tuple(hp + (kn - hp) * 0.5), tuple(kn), tuple(calf), tuple(shin), tuple(an)],
         [r_th * 0.95, r_th, r_th * 0.84, r_kn, r_ca, r_an * 1.15, r_an], 6, hose,
         [grey(0.7), grey(0.82), grey(0.95), WHITE, WHITE, grey(0.95), grey(0.9)])
    # The boot: from its top down the shin, round the heel and along the foot.
    t = Vector(toe).normalized()
    sole_y = 0.0
    shank = (kn - an).normalized()
    b_top = an + shank * boot_top * (1.0 if boot_top > 0.1 else 0.5)
    heel = Vector((an.x, sole_y + 0.045, an.z)) - t * 0.03
    ball = Vector((an.x + side * 0.004, sole_y + 0.04, an.z)) + t * 0.11
    tip = Vector((an.x + side * 0.008, sole_y + 0.032, an.z)) + t * 0.175
    up_r = r_an * (1.45 if boot_top > 0.1 else 1.2)
    tube(m, mat, [tuple(b_top), tuple(an + shank * 0.02), tuple(heel), tuple(ball), tuple(tip)],
         [up_r, r_an * 1.3, (0.042, 0.045, 0.045), (0.046, 0.04, 0.04), (0.03, 0.026, 0.026)], 6, boot,
         [grey(0.9), WHITE, grey(0.85), WHITE, grey(0.9)], caps=(False, True))
    if wraps:
        # Cloth bound round the shin, over the hose (a carter's leg wraps).
        tube(m, mat, [tuple(an + shank * 0.03), tuple(an + (kn - an) * 0.55)], [r_an * 1.32, r_ca * 1.08], 6,
             wraps if isinstance(wraps, str) else "under", [grey(0.85), WHITE])


def standing_limbs(spec, body, arms, legs):
    """His legs and arms as he stands at rest: LegL, LegR, ArmL, ArmR
    (rig.skin binds them to the bones). `arms` gives each side (-1, 1) a
    dict: fist, sleeve, cuff, wide, grip (where the hand holds, else just
    past the wrist), held (fn(mesh, mat, grip, ahead): what's in the hand,
    made as the hand hangs; bound to the hand). `legs` are leg()'s keywords."""
    mat = "chr_" + spec["name"]
    jt = joints(spec)
    for side, nm in ((-1, "L"), (1, "R")):
        hip, knee, ankle = (mirror(jt[k], side) for k in ("hip", "knee", "ankle"))
        lm = porter.Mesh("Leg" + nm)
        leg(lm, mat, spec, side, hip, knee, ankle, **legs)
        lm.build(smooth=True, origin=hip, parent=body)
        a = arms[side]
        sh, el, wr = (mirror(jt[k], side) for k in ("shoulder", "elbow", "wrist"))
        ahead = (Vector(wr) - Vector(el)).normalized()
        am = porter.Mesh("Arm" + nm)
        arm(am, mat, spec, side, sh, el, wr, hand_dir=tuple(ahead), sleeve=a.get("sleeve", "garment"), cuff=a.get("cuff"),
            fist=a.get("fist", False), wide=a.get("wide", 1.0))
        grip = a.get("grip", tuple(Vector(wr) + ahead * 0.05))
        if a.get("held"):
            am.tag = "bone:hand_" + ("l" if side < 0 else "r")
            a["held"](am, mat, grip, tuple(ahead))
            am.tag = None
        am.build(smooth=True, origin=sh, parent=body)


# ------------------------------------------------------------ the texture

def _noise(rng, w, h, cells):
    """Smooth value noise, 0..1, `cells` across."""
    gw, gh = cells + 2, max(2, int(cells * h / w)) + 2
    g = rng.random((gh, gw))
    ys = np.linspace(0, gh - 2.001, h)
    xs = np.linspace(0, gw - 2.001, w)
    y0, x0 = ys.astype(int), xs.astype(int)
    fy, fx = (ys - y0)[:, None], (xs - x0)[None, :]
    fy, fx = fy * fy * (3 - 2 * fy), fx * fx * (3 - 2 * fx)
    a = g[y0][:, x0]
    b = g[y0][:, x0 + 1]
    c = g[y0 + 1][:, x0]
    d = g[y0 + 1][:, x0 + 1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def srgb_arr(c):
    return np.array(c[:3], dtype=np.float64)


def paint_cloth(img, region, base, rng, blotch=0.12, weave=0.05, folds=0.0, hem=0.0, hem_color=None, stripes=None,
                wear=0.0):
    """A swatch of cloth (or leather, wood): its colour, blotched, a weave or
    grain, folds hanging down (darker streaks across), mud and wet toward
    the hem (the swatch's foot), and wear (lighter, at random)."""
    x, y, w, h = REGIONS[region]
    col = np.tile(srgb_arr(base), (h, w, 1))
    k = 1.0 + (_noise(rng, w, h, 4) - 0.5) * 2.0 * blotch
    k *= 1.0 + (rng.random((h, w)) - 0.5) * 2.0 * weave
    if folds:
        u = np.linspace(0.0, 1.0, w)[None, :]
        ph = rng.random() * 6.28
        f = 0.5 + 0.5 * np.sin(u * 6.28 * 5.0 + ph + 0.6 * np.sin(u * 6.28 * 2.0))
        drift = _noise(rng, w, h, 3)
        k *= 1.0 - folds * (f ** 3) * (0.6 + 0.4 * drift)
        k *= 1.0 + folds * 0.4 * ((1 - f) ** 6)
    if wear:
        k *= 1.0 + wear * np.clip(_noise(rng, w, h, 9) - 0.6, 0, 1) * 2.5
    col = col * k[:, :, None]
    if stripes:
        # Grain: fine streaks along the swatch (wood).
        g = _noise(rng, w * 6, h, 3)[:, ::6]
        col *= (1.0 + (g - 0.5) * stripes)[:, :, None]
    if hem:
        t = np.linspace(0.0, 1.0, h)[:, None]
        m = np.clip((t - (1.0 - hem)) / hem, 0, 1) ** 1.5
        m = m * (0.7 + 0.6 * _noise(rng, w, h, 6))
        hc = srgb_arr(hem_color or (0.2, 0.17, 0.14))
        col = col * (1 - m[:, :, None]) + hc[None, None, :] * m[:, :, None]
    img[y:y + h, x:x + w] = np.clip(col, 0, 1)


def paint_head(img, spec, rng):
    """The head's skin: tone, the flush of the cheeks and nose, the shadow
    under the jaw, age, stubble or beard, the hair. The eyes, brows, mouth
    and throat are drawn over it by the face shader."""
    x0, y0, w, h = REGIONS["head"]
    rows = head_rows(spec)
    skin = srgb_arr(spec["skin"])
    hair = srgb_arr(spec["hair"])
    beard_col = srgb_arr(spec.get("beard_color", spec["hair"]))
    out = np.zeros((h, w, 3))
    tone = _noise(rng, w, h, 5)
    fine = rng.random((h, w))
    hairline = spec.get("hairline", 0.235)
    for j in range(h):
        hh = HEAD_TOP - (j + 0.5) / h * (HEAD_TOP - HEAD_ROWS[0][0])
        for i in range(w):
            th = head_theta((i + 0.5) / w)
            px, py, pz = head_point(rows, th, hh)
            a = abs(th)
            c = skin * (0.94 + 0.12 * tone[j, i])
            # Warm in the cheeks, the nose and the ears; paler on the brow.
            cheek = math.exp(-(((abs(px) - 0.045) / 0.02) ** 2 + ((py - 0.152) / 0.02) ** 2))
            nose = math.exp(-((px / 0.012) ** 2 + ((py - 0.152) / 0.02) ** 2)) if a < 0.6 else 0.0
            ear = math.exp(-(((a - 1.62) / 0.2) ** 2 + ((py - 0.17) / 0.03) ** 2))
            flush = spec.get("flush", 0.5)
            red = (cheek * 0.8 + nose * 0.7 + ear * 0.6) * flush
            c = c * (1 - 0.18 * red) + np.array([0.62, 0.3, 0.24]) * 0.18 * red * 2.0
            if py > 0.215 and a < 0.9:
                c = c * 1.04
            # Under the jaw and the neck: in its own shadow.
            if py < 0.09:
                c = c * (0.78 + 0.22 * max(0.0, min(1.0, (py - 0.0) / 0.09)))
            # Age: lines at the eyes' corners and across the brow.
            age = spec.get("age_lines", 0.0)
            if age and a < 1.1:
                ex = abs(px) - 0.052
                if 0.0 < ex < 0.012 and abs((py - 0.184) - (ex * 0.6 * ((j + i) % 3 - 1))) < 0.0016:
                    c = c * (1 - 0.18 * age)
                if a < 0.6 and abs(py - 0.232) < 0.0012 and abs(px) < 0.03:
                    c = c * (1 - 0.12 * age)
            # Stubble and beard: on the jaw, the chin, the upper lip.
            b = 0.0
            beard = spec.get("beard", 0.0)
            if beard and a < 1.42:
                # Its top: across the upper lip, down to the mouth's corners, up
                # the cheeks to the ears.
                top = float(np.interp(a, [0.0, 0.2, 0.32, 0.9, 1.5, 1.75],
                                      [0.141 + 0.004 * spec.get("moustache", 0.0), 0.139, 0.13, 0.163, 0.2, 0.2]))
                if a > 1.2:
                    top = min(top, 0.2 - (a - 1.2) * 0.3)
                top += spec.get("beard_top", 0.0)
                if 0.06 < py < top:
                    b = beard * min(1.0, (top - py) / 0.012 + 0.6 * (fine[(j * 5) % h, i] - 0.5))
                    if py < 0.085:
                        b *= max(0.0, (py - 0.06) / 0.025)
                    b = max(b, 0.0)
                if b > 0:
                    grain = 0.55 + 0.45 * fine[j, i]
                    c = c * (1 - b * grain) + beard_col * b * grain
            # Form: the sides of the face turn from the light; hollows under
            # the cheekbones; the temples.
            if a > 0.6:
                c = c * (1.0 - 0.14 * min(1.0, (a - 0.6) / 0.9))
            if 0.5 < a < 1.2 and 0.115 < py < 0.15:
                c = c * 0.93
            if 0.75 < a < 1.3 and 0.19 < py < 0.23:
                c = c * 0.94
            # Freckles over the nose and cheeks; a scar along the jaw.
            fr = spec.get("freckles", 0.0)
            if fr and a < 1.1 and 0.14 < py < 0.2 and fine[(j * 3 + 11) % h, (i * 5 + 7) % w] > 1.0 - 0.16 * fr:
                c = c * 0.8 + np.array([0.45, 0.27, 0.18]) * 0.2
            scar = spec.get("scar", 0.0)
            if scar and th > 0.0:
                along = (a - 0.45) / 0.55
                if 0.0 < along < 1.0 and abs(py - (0.104 + 0.03 * along)) < 0.0022:
                    c = c * (1 - 0.5 * scar) + np.array([0.78, 0.66, 0.62]) * 0.5 * scar
            # Hair: above the hairline in front, lower at the sides and back.
            style = spec.get("hair_style", "cropped")
            line = hairline - 0.02 * min(1.0, a / 1.4) - 0.075 * max(0.0, (a - 1.4) / (math.pi - 1.4))
            if a > 1.35 and a < 1.85 and py < 0.21:
                line = 0.21  # round the ear
            if style == "bowl":
                # Cut straight round, above the ears and the nape.
                line = max(line, 0.205 if a > 0.9 else hairline - 0.012)
            grows = py > line - 0.004 * fine[j, i]
            thin = 1.0
            if style == "tonsure":
                # The crown shaved: a ring of hair left round the head.
                grows = grows and py < 0.268 + 0.004 * fine[j, i]
                if a < 0.9:
                    grows = grows and py > hairline + 0.012
            elif style == "balding":
                # Gone from the brow and the crown; left at the sides and back.
                grows = grows and a > 1.05 and py < 0.262
                thin = 0.85
            elif style == "bald":
                thin = 0.14 if grows else 0.0
            if grows and thin > 0.0:
                streak = 0.75 + 0.35 * fine[j, (i * 3) % w] * (0.6 + 0.4 * tone[j, i])
                gr = spec.get("grey_hair", 0.0)
                hc = hair * (1 - gr * fine[(j * 7) % h, i]) + np.array([0.55, 0.53, 0.5]) * gr * fine[(j * 7) % h, i]
                c = c * (1.0 - thin) + hc * streak * thin
            out[j, i] = c
    img[y0:y0 + h, x0:x0 + w] = np.clip(out, 0, 1)


def quantize(img, levels=24):
    """Fewer tones, as a hand-painted texture of the time has."""
    return np.round(img * levels) / levels


def write_png(path, img):
    """An RGB PNG from an array of 0..1 sRGB values (rows from the top)."""
    data = (np.clip(img, 0, 1) * 255.0 + 0.5).astype(np.uint8)
    h, w, _ = data.shape
    raw = b"".join(b"\x00" + data[r].tobytes() for r in range(h))

    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) \
        + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def texture(spec):
    """Paints the atlas: the head, and every swatch the parts asked for."""
    rng = np.random.default_rng(spec.get("seed", 1))
    img = np.zeros((TEX, TEX, 3))
    paint_head(img, spec, rng)
    for region, (color, paint) in SWATCHES.items():
        paint_cloth(img, region, color, rng, **paint)
    img = quantize(img)
    path = os.path.join(porter.MODELS, "chr_%s.png" % spec["name"])
    write_png(path, img)
    print("built chr_%s.png" % spec["name"])


# ---------------------------------------------------------------- export

def _report(name):
    parts = ["%s %d" % (o.name, sum(len(p.vertices) - 2 for p in o.data.polygons)) for o in bpy.data.objects if o.type == "MESH"]
    print("  %s: %s" % (name, ", ".join(parts)))


## A character scene as the build writes it (scene()).
SCENE = """[gd_scene format=3]

[ext_resource type="Script" path="res://game/people/person_model.gd" id="person_gd"]
[ext_resource type="Script" path="res://game/people/face_rig.gd" id="face_gd"]
[ext_resource type="PackedScene" path="res://art/models/%(name)s.glb" id="model"]
[ext_resource type="PackedScene" path="res://art/models/%(name)s_head.glb" id="head"]

[node name="%(node)s" type="Node3D"]
editor_description = "%(about)s"
script = ExtResource("person_gd")

[node name="Model" parent="." instance=ExtResource("model")]

[node name="Head" type="Node3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, %(ny).4f, %(nz).4f)
script = ExtResource("face_gd")

[node name="Model" parent="Head" instance=ExtResource("head")]

[node name="Face" type="Marker3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, %(fy).4f, %(fz).4f)
"""
MATERIAL = """[gd_resource type="ShaderMaterial" format=3]

[ext_resource type="Shader" path="res://game/people/%s.gdshader" id="shader"]
[ext_resource type="Texture2D" path="res://art/models/%s.png" id="atlas"]

[resource]
shader = ExtResource("shader")
shader_parameter/atlas = ExtResource("atlas")
"""


def face_look(spec):
    """What the face shader is given for this person (face.gdshader): how
    deep his lines are, the colours of his eyes, brows and lips, and the
    shape of his brows (the kit's BROWS)."""
    brow = spec.get("brow_color") or tuple(c * 0.9 for c in spec["hair"])
    out = {"lines": round(spec.get("lines", spec.get("age_lines", 0.5)), 3), "iris_color": spec.get("iris", (0.32, 0.25, 0.17)),
           "brow_color": brow, "lip_color": spec.get("lip", (0.52, 0.33, 0.29))}
    brows = spec.get("brows")
    if brows:
        out.update({"brow_size": brows["size"], "brow_at": brows["at"], "brow_arch": brows["arch"], "brow_slant": brows["slant"],
                    "brow_taper": brows["taper"]})
    elif spec.get("brow_size"):
        out["brow_size"] = spec["brow_size"]
    return out


def materials(spec):
    """Writes his two materials to game/people/materials/: chr_<name> (the
    atlas, person.gdshader) and chr_<name>_face (the same, and his face:
    face.gdshader with face_look()). They are the build's: a change to them
    goes in his spec."""
    name = "chr_" + spec["name"]
    folder = os.path.join(porter.ROOT, "game", "people", "materials")
    os.makedirs(folder, exist_ok=True)
    open(os.path.join(folder, name + ".tres"), "w").write(MATERIAL % ("person", name))
    rows = []
    for k, v in face_look(spec).items():
        if isinstance(v, (int, float)):
            rows.append("shader_parameter/%s = %s" % (k, round(float(v), 4)))
        elif len(v) == 2:
            rows.append("shader_parameter/%s = Vector2(%s, %s)" % (k, round(v[0], 4), round(v[1], 4)))
        else:
            rows.append("shader_parameter/%s = Color(%s, %s, %s, 1)" % (k, round(v[0], 3), round(v[1], 3), round(v[2], 3)))
    open(os.path.join(folder, name + "_face.tres"), "w").write(MATERIAL % ("face", name) + "\n".join(rows) + "\n")


def scene(spec):
    """Writes game/characters/chr_<name>.tscn (a PersonModel: Model, Head,
    Face) if there is none, or only a placeholder. A real scene is left as
    it is: what the scene adds by hand (a lantern in his hand) stays."""
    name = "chr_" + spec["name"]
    path = os.path.join(porter.ROOT, "game", "characters", name + ".tscn")
    if os.path.exists(path) and 'groups=["placeholder"]' not in open(path).read():
        return
    neck = rig.JOINTS["neck"]
    about = spec.get("about", "%s (tools/build/%s.py)." % (spec["name"].capitalize(), name)).replace('"', "'")
    about += " Model is his body on its skeleton, with his clips (PersonModel). Feet (or seat) at the origin, facing -Z. " \
        "Head is his face (a FaceRig over the head model); Face is where the conversation camera looks. In the game both " \
        "ride on the skeleton's head."
    text = SCENE % {"name": name, "node": "".join(w.capitalize() for w in spec["name"].split("_")), "about": about,
                    "ny": neck[1], "nz": neck[2], "fy": neck[1] + 0.17, "fz": neck[2] - 0.1}
    open(path, "w").write(text)
    print("wrote game/characters/%s.tscn" % name)


def build_head(spec, head_extra=None):
    """Only his head (and what he wears on it)."""
    name = "chr_" + spec["name"]
    porter.reset(spec.get("seed", 1) + 2)
    h = head_mesh(spec).build(smooth=True)
    if head_extra:
        head_extra(spec, h)
    porter.export(name + "_head")


def build(spec, body, head_extra=None, extras=None, posed=None, keep_apart=(), game=True):
    """Writes the character's models, texture, materials and scene.
    `body(spec)` builds him standing at rest on his skeleton;
    `posed(spec, skeleton)` (if given) adds parts made in one of his clips'
    poses (rig.posed, rig.bind: the carter's reins as he sits), named in
    `keep_apart` if they are to stay apart from his Body.
    `head_extra(spec, head_obj)` adds what he wears on his head; `extras` is
    a list of (glb name, function) for more models (a lantern). The texture
    is painted last, when every part has asked for its swatch. With `game`
    off (the kit's catalogue) no material or scene is written."""
    reset_atlas()
    name = "chr_" + spec["name"]
    porter.reset(spec.get("seed", 1))
    skeleton, library, clips = rig.rig(spec)
    body(spec)
    rig.skin(skeleton, keep_apart)
    rig.clips(spec, skeleton, library, clips)
    if posed:
        posed(spec, skeleton)
    porter.export(name)
    _report(name)
    build_head(spec, head_extra)
    for glb, fn in extras or []:
        porter.reset(spec.get("seed", 1) + 3)
        fn(spec)
        porter.export(glb)
    texture(spec)
    if game:
        materials(spec)
        scene(spec)
