"""The people of The Porter: one low-poly human, dressed per character, with
a head cut in flat planes whose face the game paints (Look and Feel,
"Characters"; the locked PSX character style: low poly, hand-painted
textures at 256 px with nearest filtering, per-vertex shading; the heads
after the user's reference heads of 2026-11-16: docs/systems/faces.md,
"The face").

These are the builders: the head, tubes of cloth, limbs, the texture, the
build. What a person is put together from (builds, skins, faces, clothes,
headwear) is the people's kit, tools/build/people_kit.py: a character
script (tools/build/chr_<name>.py) is a spec on that. build() writes to
art/models/:

    chr_<name>.png          the character's texture: a 256 px atlas, painted
                            here (a swatch of 64 px for each cloth, leather,
                            wood...; the top-left 128 px, once the head's,
                            is only his skin)
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
                            chr_<name>_face, whose shader paints the skin,
                            the hair, the beard, and the eyes, brows, mouth
                            and throat the FaceRig moves) and what he wears
                            on it

He is made standing at rest, as his skeleton stands: arms hanging straight
at his sides, legs straight (joints(): where the joints are).

Materials are names only, linked on import to game/people/materials/<name>.tres
(tools/build/link_imports.py): chr_<name> (the atlas, per-vertex shading)
and chr_<name>_face (the head, painted by its shader).

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
## The atlas: x, y (from the top), width, height in pixels. The top-left
## 128 px was the head's and is only skin now (the face shader paints the
## head); each cloth (leather, wood...) a part asks for with swatch() takes
## the next 64 px cell of the twelve.
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

## The head is cut in flat planes, as a low-poly head is: a flat face, a
## cheek plane each side turning back from it, flat sides, a jaw with an
## edge to it, a wedge of a nose. Rings up the head from the neck pivot,
## each of seven points from the middle of the face round his right side to
## the middle of the back (his left side mirrors them): the middle of the
## face, the inner face, the face's corner (where the front turns to the
## cheek), the cheek's back (where it turns to the side), the ear line, the
## back's corner, the middle of the back. A point is (x, y, z); front is -z.
## A ring isn't level: the jaw's edge rises from the chin to the ear. One
## average man's head; a spec scales it (head_rows).
HEAD = [
    # The neck: its foot, its top.
    [(0, -.035, -.046), (.022, -.035, -.045), (.042, -.035, -.034), (.054, -.035, -.010), (.055, -.035, .020), (.038, -.035, .056), (0, -.035, .062)],
    [(0, .035, -.046), (.021, .035, -.045), (.039, .035, -.034), (.050, .035, -.010), (.051, .035, .020), (.036, .035, .054), (0, .035, .060)],
    # Under the jaw, where it meets the neck.
    [(0, .070, -.054), (.020, .070, -.053), (.037, .072, -.040), (.050, .076, -.016), (.053, .082, .018), (.039, .072, .056), (0, .070, .062)],
    # The jaw's edge: the chin, flat in front, back and up to its corner under the ear.
    [(0, .083, -.094), (.018, .083, -.093), (.035, .088, -.072), (.053, .098, -.032), (.062, .112, .006), (.046, .100, .060), (0, .096, .070)],
    # Under the lip.
    [(0, .102, -.097), (.020, .102, -.0965), (.043, .104, -.087), (.060, .113, -.040), (.067, .128, .010), (.049, .122, .067), (0, .120, .079)],
    # The mouth.
    [(0, .126, -.097), (.022, .126, -.0965), (.048, .127, -.090), (.066, .132, -.041), (.071, .142, .011), (.051, .140, .073), (0, .140, .087)],
    # The nose's foot and the cheekbones.
    [(0, .150, -.097), (.022, .150, -.0965), (.050, .150, -.091), (.072, .152, -.040), (.074, .157, .012), (.053, .157, .079), (0, .157, .095)],
    # Under the eyes; the top of their sockets; the brow over them.
    [(0, .172, -.0945), (.022, .172, -.094), (.051, .172, -.089), (.073, .172, -.040), (.075, .172, .012), (.054, .172, .081), (0, .172, .098)],
    [(0, .198, -.0945), (.022, .198, -.094), (.052, .198, -.089), (.074, .198, -.040), (.076, .198, .012), (.055, .198, .083), (0, .198, .101)],
    [(0, .212, -.0975), (.022, .212, -.0975), (.052, .212, -.092), (.074, .212, -.040), (.076, .212, .012), (.055, .212, .084), (0, .212, .102)],
    # The forehead, the crown, the top.
    [(0, .243, -.090), (.022, .243, -.0895), (.050, .243, -.083), (.071, .243, -.036), (.073, .243, .014), (.053, .243, .082), (0, .243, .100)],
    [(0, .272, -.070), (.020, .272, -.069), (.042, .272, -.062), (.059, .272, -.028), (.061, .272, .014), (.044, .272, .070), (0, .272, .086)],
    [(0, .294, -.040), (.012, .294, -.039), (.025, .294, -.034), (.035, .294, -.016), (.036, .294, .010), (.026, .294, .042), (0, .294, .052)],
]
NECK_FOOT, NECK, UNDER, JAW, LOW, MOUTH, CHEEK, EYE, SOCKET, BROW, FOREHEAD, CROWN, TOP_RING = range(13)
HEAD_TOP = 0.303
## Where the face is on every head (the face shader's layout, face.gdshader).
EYE_AT = (0.031, 0.184)
EYE_SIZE = (0.0042, 0.0066)
MOUTH_Y = 0.126
MOUTH_HALF = 0.0145
## The face shader's hair_style, by the kit's HAIR_STYLES.
HAIR_STYLE = {"cropped": 0, "bowl": 1, "tonsure": 2, "balding": 3, "bald": 4, "long": 5}
## Two of the head's planes meeting at more than this many degrees keep a
## hard edge between them (the face's corners, the jaw, the nose); less,
## and they shade as one.
HEAD_EDGE = 30.0
## How far each cut stands off the skull, m.
HAIR_BULK = {"cropped": 0.009, "bowl": 0.012, "tonsure": 0.008, "balding": 0.006, "bald": 0.0, "long": 0.009}


def head_rows(spec):
    """The head's rings for this person: width, jaw, chin, cheek and brow
    scaled; `jowl` fills out under the jaw and the neck (a fat face)."""
    hs = spec.get("head", {})
    w = hs.get("width", 1.0)
    jaw = hs.get("jaw", 1.0)
    chin = hs.get("chin", 1.0)
    brow = hs.get("brow", 1.0)
    cheek = hs.get("cheek", 1.0)
    jowl = hs.get("jowl", 0.0)
    rows = []
    for i, ring in enumerate(HEAD):
        out = []
        for c, (x, y, z) in enumerate(ring):
            x *= w if i > UNDER else 1.0 + (w - 1.0) * 0.5
            # The jaw: wider or narrower from the chin to its corner.
            if i in (JAW, LOW) and 1 <= c <= 4:
                x *= jaw
            if i == MOUTH and 2 <= c <= 4:
                x *= 0.5 + 0.5 * jaw
            # The chin: further out, and longer.
            if i in (JAW, LOW) and c <= 2:
                z = -0.064 + (z + 0.064) * chin
            if i in (UNDER, JAW) and c <= 1:
                y -= 0.03 * (chin - 1.0)
            # A heavy brow stands out over deeper sockets.
            if i == BROW and c <= 2:
                z -= 0.0035 * (brow - 1.0)
            if i in (EYE, SOCKET) and c in (1, 2):
                z += 0.0012 * (brow - 1.0)
            # Hollow cheeks fall in under the cheekbones.
            if i == MOUTH and c in (2, 3):
                x -= 0.0035 * (cheek - 1.0)
            if i == CHEEK and c == 3:
                x += 0.002 * (cheek - 1.0)
            if i <= UNDER:
                x *= 1.0 + jowl * 0.26
                z *= 1.0 + jowl * 0.22 if z < 0.0 else 1.0
            if i == JAW and 2 <= c <= 4:
                x *= 1.0 + jowl * 0.12
                y -= 0.005 * jowl if c < 4 else 0.0
            if i == LOW and c in (2, 3):
                x *= 1.0 + jowl * 0.07
            out.append((x, y, z))
        rows.append(out)
    return rows


def _up_column(rows, col, h):
    """Where column `col` of the head's rings is at height `h`: (x, z)."""
    pts = [r[col] for r in rows]
    if h <= pts[0][1]:
        return pts[0][0], pts[0][2]
    for a, b in zip(pts, pts[1:]):
        if h <= b[1]:
            t = (h - a[1]) / max(b[1] - a[1], 1e-6)
            return a[0] + (b[0] - a[0]) * t, a[2] + (b[2] - a[2]) * t
    return pts[-1][0], pts[-1][2]


def head_point(rows, theta, h):
    """A point on the head's skin at angle `theta` round it from the front
    (+ toward his right) and height `h`: on its planes, before the nose, the
    ears and the hair's bulk are added. What is worn on the head is made
    from this."""
    h = min(max(h, rows[0][0][1]), rows[-1][0][1])
    ring = [_up_column(rows, c, h) for c in range(7)]
    a = min(abs(theta), math.pi)
    s, c = math.sin(a), math.cos(a)
    best = ring[0] if a < 1.5 else ring[-1]
    for (x0, z0), (x1, z1) in zip(ring, ring[1:]):
        dx, dz = x1 - x0, z1 - z0
        den = s * dz + c * dx
        if abs(den) < 1e-9:
            continue
        u = (-x0 * c - z0 * s) / den
        if -1e-6 <= u <= 1.0 + 1e-6 and (x0 * dz - z0 * dx) / den > 0.0:
            best = (x0 + dx * u, z0 + dz * u)
            break
    return math.copysign(best[0], theta), h, best[1]


def _along(x, a, b):
    return min(max((x - a) / (b - a), 0.0), 1.0)


def hair_line(spec, aa):
    """How far down the hair comes at `aa` round the head from the front (0)
    to the back (pi). The face shader paints it (face.gdshader, hair_line:
    the same line); here it says where the hair's bulk is."""
    top = spec.get("hairline", 0.236)
    style = spec.get("hair_style", "cropped")
    mix = lambda a, b, t: a + (b - a) * t
    if style == "bowl":
        return mix(top - 0.014, 0.203, _along(aa, 0.8, 1.0))
    if style == "tonsure":
        return mix(top - 0.008, 0.203, _along(aa, 0.75, 1.0))
    y = mix(top, top + 0.006, _along(aa, 0.0, 0.42))
    y = mix(y, top - 0.006, _along(aa, 0.42, 0.7))
    y = mix(y, 0.2, _along(aa, 0.7, 1.16))
    y = mix(y, 0.168, _along(aa, 1.16, 1.26))
    y = mix(y, 0.207, _along(aa, 1.48, 1.6))
    y = mix(y, 0.152, _along(aa, 1.95, 2.12))
    return mix(y, 0.13, _along(aa, 2.12, math.pi))


def hair_bulk(spec, x, y, z):
    """How far the hair stands off the skull at a point of it, m: none on
    skin, under a hat or a hood, or on a bald head."""
    style = spec.get("hair_style", "cropped")
    if spec.get("headwear"):
        return 0.0
    aa = abs(math.atan2(x, -z))
    k = _along(y, hair_line(spec, aa), hair_line(spec, aa) + 0.03)
    if style == "tonsure" and y > 0.262:
        k = 0.0
    if style == "balding" and (aa < 1.2 or y > 0.255):
        k = 0.0
    return k * HAIR_BULK.get(style, 0.009)


def head_mesh(spec, name="Head"):
    """The head: rings of flat planes from the neck to the crown, a wedge
    of a nose, ears that stand out, the hair's bulk. Material
    chr_<name>_face, which paints all of it (face.gdshader): the UVs only
    say what a face of it is (x: 0 skin, 1 an ear, 2 the nose). Its planes
    are smooth, with a hard edge wherever two of them meet at more than
    HEAD_EDGE degrees (build_head). Origin at the neck pivot."""
    mat = "chr_%s_face" % spec["name"]
    m = porter.Mesh(name)
    rows = head_rows(spec)
    hs = spec.get("head", {})
    # A face kept in shadow (a stranger deep in his cowl): `face_shade` below 1.
    dim = spec.get("face_shade", 1.0)
    beard = spec.get("beard_volume", 0.0)
    skin, ear, nose = (0.0, 0.0), (1.0, 0.0), (2.0, 0.0)

    def bulked(x, y, z):
        b = hair_bulk(spec, x, y, z)
        if b <= 0.0:
            return x, y, z
        up = _along(y, 0.24, 0.3)
        d = math.hypot(x, z) or 1.0
        return x + x / d * b * (1.0 - 0.5 * up), y + b * 0.9 * up, z + z / d * b * (1.0 - 0.5 * up)

    grid = []
    for i, row in enumerate(rows):
        ring = []
        # Round from the middle of the back by his left, the face, his right.
        for k in range(13):
            c = abs(k - 6)
            x, y, z = row[c]
            x = -x if k < 6 else x
            # A beard builds the jaw out and down.
            if beard and i in (JAW, LOW, MOUTH) and c <= 3:
                grow = beard * (1.0 if i < MOUTH else 0.5) * (1.0 - 0.25 * c / 3.0)
                if i == MOUTH and c <= 1:
                    grow *= 0.2
                x *= 1.0 + grow * 0.22
                z -= grow * 0.012
                y -= grow * 0.012 if i == JAW else 0.0
            x, y, z = bulked(x, y, z)
            ring.append(ring[0] if k == 12 else m.vert(x, y, z, grey(dim), skin))
        grid.append(ring)
    # Each plane as two triangles, cut the same way on both sides of him.
    for r0, r1 in zip(grid, grid[1:]):
        for k in range(12):
            if k < 6:
                m.face((r1[k], r1[k + 1], r0[k + 1]), mat)
                m.face((r1[k], r0[k + 1], r0[k]), mat)
            else:
                m.face((r1[k], r1[k + 1], r0[k]), mat)
                m.face((r1[k + 1], r0[k + 1], r0[k]), mat)
    tx, ty, tz = bulked(0.0, HEAD_TOP, 0.004)
    top = m.vert(tx, max(ty, HEAD_TOP + hair_bulk(spec, 0.0, HEAD_TOP, 0.004)), tz, grey(dim), skin)
    for k in range(12):
        m.face((top, grid[-1][k + 1], grid[-1][k]), mat)
    # The nose: a wedge. A flat ridge from between the brows to the tip, a
    # side each way down to the wings, and under it back to the lip.
    n = hs.get("nose", 1.0)
    nw = hs.get("nose_width", 1.0)
    fz = _up_column(rows, 0, 0.15)[1]

    def surf(x, y, out=0.0):
        return (x, y, head_point(rows, math.atan2(x, 0.095), y)[2] - out)

    tip_x, tip_y, tip_z = 0.006 * nw, 0.1535 - 0.004 * (n - 1.0), fz - 0.023 * n
    wing = 0.0165 * nw
    pt = {
        "bl": surf(-0.0036, 0.2, 0.0015), "br": surf(0.0036, 0.2, 0.0015),
        "tl": (-tip_x, tip_y, tip_z), "tr": (tip_x, tip_y, tip_z),
        "sl": surf(-0.0115 * math.sqrt(nw), 0.184), "sr": surf(0.0115 * math.sqrt(nw), 0.184),
        "wl": surf(-wing, 0.146, 0.0005), "wr": surf(wing, 0.146, 0.0005),
        "un": surf(0.0, 0.1445, 0.001),
    }

    def nose_face(keys, facing, shade):
        m.poly([pt[k] for k in keys], mat, grey(shade * dim), [nose] * len(keys), facing=facing)

    nose_face(("bl", "br", "tr", "tl"), (0.0, 0.3, -1.0), 1.0)
    nose_face(("sl", "bl", "tl"), (-1.0, 0.0, -0.6), 0.97)
    nose_face(("sl", "tl", "wl"), (-1.0, 0.0, -0.6), 0.97)
    nose_face(("br", "sr", "tr"), (1.0, 0.0, -0.6), 0.97)
    nose_face(("sr", "wr", "tr"), (1.0, 0.0, -0.6), 0.97)
    nose_face(("tl", "tr", "un"), (0.0, -1.0, -0.4), 0.74)
    nose_face(("tl", "un", "wl"), (-0.3, -1.0, -0.3), 0.74)
    nose_face(("tr", "wr", "un"), (0.3, -1.0, -0.3), 0.74)
    # Ears: a flat plate each side, standing out and back from the head.
    if hs.get("ears", True):
        x0, z0 = _up_column(rows, 4, 0.176)
        big = hs.get("ear", 1.0)
        for sx in (-1.0, 1.0):
            plate = [(-0.004, 0.176 + 0.02 * big, -0.012), (0.01 * big, 0.176 + 0.024 * big, 0.012 * big),
                     (0.014 * big, 0.176 + 0.012 * big, 0.02 * big), (0.012 * big, 0.176 - 0.014 * big, 0.019 * big),
                     (-0.004, 0.176 - 0.026 * big, -0.008)]
            pts = [(sx * (x0 + p[0]), p[1], z0 + p[2]) for p in plate]
            m.poly(pts, mat, grey(dim), [ear] * 5, facing=(sx, 0.0, -0.8))
            m.poly(pts, mat, grey(0.78 * dim), [ear] * 5, facing=(-sx, 0.0, 0.8))
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
    # The shoulder's cap: a low dome over the joint, level with the trunk's
    # yoke, so the arm grows out of the trunk and doesn't hang off its side.
    top = sh + up * r_sh * 0.6 + inward * r_sh * 0.12
    cap = sh + up * r_sh * 0.36 + inward * r_sh * 0.06
    cuff_r = r_wr * (1.3 if cuff else 1.1)
    pts = [top, cap, sh, sh + (el - sh) * 0.5, el, el + (wr - el) * 0.5, wr]
    radii = [r_sh * 0.45, r_sh * 0.86, r_sh, r_sh * 0.88, r_el, (r_el + cuff_r) * 0.48, cuff_r]
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
                wear=0.0, patches=0.0):
    """A swatch of cloth (or leather, wood): its colour, blotched, a weave or
    grain, folds hanging down (darker streaks across), mud and wet toward
    the hem (the swatch's foot), wear (lighter, at random), and patches
    sewn on (0 none to 1 many: rags)."""
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
    for _ in range(int(round(patches * 7))):
        # A patch: another bit of cloth, its stitches dark round it.
        pw, ph_ = int(rng.integers(9, 20)), int(rng.integers(8, 18))
        px, py = int(rng.integers(0, w - pw)), int(rng.integers(0, h - ph_))
        tone = srgb_arr(base) * float(rng.uniform(0.6, 1.3)) + (rng.random(3) - 0.5) * 0.06
        col[py:py + ph_, px:px + pw] = tone[None, None, :] * (0.92 + 0.16 * rng.random((ph_, pw, 1)))
        col[py, px:px + pw] *= 0.6
        col[py + ph_ - 1, px:px + pw] *= 0.6
        col[py:py + ph_, px] *= 0.6
        col[py:py + ph_, px + pw - 1] *= 0.6
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
    # The head's corner of the atlas is only his skin: the face shader paints the head.
    x, y, w, h = REGIONS["head"]
    img[y:y + h, x:x + w] = srgb_arr(spec["skin"])
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

[ext_resource type="Shader" path="res://game/people/person.gdshader" id="shader"]
[ext_resource type="Texture2D" path="res://art/models/%s.png" id="atlas"]

[resource]
shader = ExtResource("shader")
shader_parameter/atlas = ExtResource("atlas")
"""
FACE_MATERIAL = """[gd_resource type="ShaderMaterial" format=3]

[ext_resource type="Shader" path="res://game/people/face.gdshader" id="shader"]

[resource]
shader = ExtResource("shader")
"""


def face_look(spec):
    """What the face shader is given for this person (face.gdshader), which
    paints his whole head: his skin and its shadow, how flushed, how
    deep-set his eyes and how lined he is, his marks; his hair, its cut and
    its grey; his beard; where his eyes, brows and mouth are, their size and
    colours (the kit's FACES, BROWS, EYES)."""
    hs = spec.get("head", {})
    skin = spec["skin"]
    hair = spec["hair"]
    iris = spec.get("iris", (0.32, 0.25, 0.17))
    # The eyes are dark ovals with a little of their colour in them; a blind
    # man's are as pale as they are.
    eye = iris if sum(iris) / 3.0 > 0.5 else tuple(0.05 + 0.16 * c for c in iris)
    wide = hs.get("width", 1.0)
    es = hs.get("eye", (1.0, 1.0))
    out = {
        "skin_color": skin,
        "shade_color": spec.get("shade") or (skin[0] * 0.8, skin[1] * 0.68, skin[2] * 0.78),
        "flush": spec.get("flush", 0.5),
        "socket": hs.get("socket", 0.5),
        "lines": round(spec.get("lines", spec.get("age_lines", 0.5)), 3),
        "freckles": spec.get("freckles", 0.0),
        "scar": spec.get("scar", 0.0),
        "hair_color": hair,
        "hair_style": HAIR_STYLE[spec.get("hair_style", "cropped")],
        "hairline": spec.get("hairline", 0.236),
        "grey_hair": spec.get("grey_hair", 0.0),
        "tufts": spec.get("tufts", 1.0),
        "beard_color": spec.get("beard_color", hair),
        "beard": spec.get("beard", 0.0),
        "beard_top": spec.get("beard_top", 0.0),
        "moustache": spec.get("moustache", 0.0),
        "eye_at": (EYE_AT[0] * (1.0 + 0.6 * (wide - 1.0)) * hs.get("eyes_apart", 1.0), EYE_AT[1]),
        "eye_size": (EYE_SIZE[0] * es[0], EYE_SIZE[1] * es[1]),
        "eye_color": eye,
        "brow_color": spec.get("brow_color") or tuple(c * 0.9 for c in hair),
        "mouth_half": MOUTH_HALF * hs.get("mouth", 1.0) * (0.5 + 0.5 * wide),
        "lip_color": spec.get("lip", (0.52, 0.33, 0.29)),
    }
    brows = spec.get("brows")
    if brows:
        out.update({"brow_size": brows["size"], "brow_at": brows["at"], "brow_arch": brows["arch"], "brow_slant": brows["slant"],
                    "brow_taper": brows["taper"]})
    elif spec.get("brow_size"):
        out["brow_size"] = spec["brow_size"]
    return out


def materials(spec):
    """Writes his two materials to game/people/materials/: chr_<name> (the
    atlas, person.gdshader) and chr_<name>_face (his head: face.gdshader
    with face_look()). They are the build's: a change to them goes in his
    spec."""
    name = "chr_" + spec["name"]
    folder = os.path.join(porter.ROOT, "game", "people", "materials")
    os.makedirs(folder, exist_ok=True)
    open(os.path.join(folder, name + ".tres"), "w").write(MATERIAL % name)
    rows = []
    for k, v in face_look(spec).items():
        if isinstance(v, int):
            rows.append("shader_parameter/%s = %d" % (k, v))
        elif isinstance(v, float):
            rows.append("shader_parameter/%s = %s" % (k, round(v, 4)))
        elif len(v) == 2:
            rows.append("shader_parameter/%s = Vector2(%s, %s)" % (k, round(v[0], 4), round(v[1], 4)))
        else:
            rows.append("shader_parameter/%s = Color(%s, %s, %s, 1)" % (k, round(v[0], 3), round(v[1], 3), round(v[2], 3)))
    open(os.path.join(folder, name + "_face.tres"), "w").write(FACE_MATERIAL + "\n".join(rows) + "\n")


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
    whose = "her" if spec.get("sex") == "f" else "his"
    about += " Model is %s body on its skeleton, with %s clips (PersonModel). Feet at the origin, facing -Z. " \
        "Head is %s face (a FaceRig over the head model); Face is where the conversation camera looks. In the game both " \
        "ride on the skeleton's head." % (whose, whose, whose)
    text = SCENE % {"name": name, "node": "".join(w.capitalize() for w in spec["name"].split("_")), "about": about,
                    "ny": neck[1], "nz": neck[2], "fy": neck[1] + 0.17, "fz": neck[2] - 0.1}
    # What his hands hold that is a model of its own (a staff): in the scene,
    # where his hand takes it (PersonModel's right_hand_holds, left_hand_holds).
    for i, prop in enumerate(spec.get("held_props", [])):
        node = prop["name"].capitalize()
        rid = "prop%d" % i
        text = text.replace('\n[node name=', '[ext_resource type="PackedScene" path="res://art/models/%s_%s.glb" id="%s"]\n\n[node name='
                            % (name, prop["name"], rid), 1)
        text = text.replace('script = ExtResource("person_gd")\n', 'script = ExtResource("person_gd")\n%s_hand_holds = NodePath("%s")\n'
                            % ("left" if prop["hand"] == "l" else "right", node), 1)
        at = prop["at"]
        text += '\n[node name="%s" type="Node3D" parent="."]\ntransform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, %.4f, %.4f, %.4f)\n' \
            '\n[node name="Model" parent="%s" instance=ExtResource("%s")]\n' % (node, at[0], at[1], at[2], node, rid)
    open(path, "w").write(text)
    print("wrote game/characters/%s.tscn" % name)


def build_head(spec, head_extra=None):
    """Only his head (and what he wears on it)."""
    name = "chr_" + spec["name"]
    porter.reset(spec.get("seed", 1) + 2)
    h = head_mesh(spec).build(smooth=True)
    h.data.set_sharp_from_angle(angle=math.radians(HEAD_EDGE))
    if head_extra:
        head_extra(spec, h)
    # A big man's head is a little bigger, a slight one's smaller (the head
    # model's own size stays: the face shader measures in it).
    k = spec.get("head_scale", 1.0)
    h.scale = (k, k, k)
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
