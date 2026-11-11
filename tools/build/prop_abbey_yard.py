"""The props of the graveyard, the charnel house and the gardens, the small
things the porter picks up, and the proofs he finds on the last night. Each
is its own model (art/models/prop_<name>.glb), sized to the collision its
scene already has (game/world/props/prop_<name>.tscn), standing on the
ground at its origin:

- grave, grave_plain, grave_sunk, grave_slab, grave_stone, grave_fresh: a
  grave 2 m long (along x, head to the west, -x): a grassed mound with a
  wooden cross leaning; a mound and no marker; a sunken one, its turf
  fallen in; a stone slab cracked across; a small discoid stone, tilted;
  fresh dark earth. The scene shows one of the six by where it stands.
- charnel_bones: the charnel house's stack: thigh-bone ends with rows of
  skulls through it, a timber bay left open in it (the hiding place), a
  row of skulls along its top. Faces -z.
- garden_bed, garden_bed_cabbage, garden_bed_leeks, garden_bed_beans: a
  dug bed 1.2 x 4 m (along z) in plank edging, in November: bare ridged
  earth; cabbage stumps; leek and onion tops; bean poles pulled and left.
- churchyard_cross: a stone cross on three steps, 3.5 m high.
- item_stone, item_cup, item_bone, item_apple, item_bread: what he picks
  up, each about the origin its placeholder mesh has in
  game/nights/night_base.tscn.
- cult_masks, hoof_soles, purse_chest, relic_hand, cult_book: the last
  night's proofs (game/nights/night6.tscn).

`skull` is a better skull than dress.skull, with the same arguments.

Run: tools/build.sh prop_abbey_yard   (one prop: ... -- grave_slab)
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
import props
from porter import fbm, lerp, smoothstep
from props import IRON, IRON_C, OAK, OAK_DARK, PAINT, PINE, WOOD, beam, boards, plank, rgba, tone

STONE = "stone_church"
DARK = "window_dark"
BLACK = (0.0, 0.0, 0.0, 1.0)
# Bone seen from arm's length (dress.BONE was tuned for niches seen from metres away).
BONE = (0.12, 0.105, 0.075)
PIT = (0.006, 0.005, 0.004, 1.0)


# ---------------------------------------------------------------- bones

def _sup(v, e):
    return math.copysign(abs(v) ** e, v)


def skull(m, p, yaw=0.0, scale=1.0, jaw=True, seed=0.0, colour=BONE, tilt=0.0, back=True, face_only=False):
    """A skull standing on `p`, looking along `yaw` (0: toward +z): a
    braincase, brow, sockets, the nasal opening, cheekbones, upper teeth
    (some lost), and with `jaw` its jaw. About 215 triangles, 280 with the
    jaw. `tilt` tips it back. `back=False` leaves out what a skull in a
    row never shows (its base, the back of its head, what is under its
    cheekbones): about 140. `face_only` is a skull set in a stack with
    others over it: its face and brow, about 105. Goes in a smooth mesh."""
    rng = random.Random(int(seed * 7919.0) + int(p[0] * 1310.0) + int(p[2] * 710.0) + int(p[1] * 97.0))
    k = rng.uniform(0.62, 1.05)
    t = props.Placed(m, p, yaw, scale, tilt)
    y0 = 0.045 if jaw else 0.0

    def tint(x, y, z, mul=1.0):
        s = k * mul * (0.84 + 0.22 * fbm(x * 21.0 + seed, z * 21.0 + y * 17.0, 1.0, 2, seed)) * lerp(0.62, 1.0, smoothstep(-0.02, 0.1, y))
        low = 1.0 - smoothstep(0.0, 0.11, y)
        return (colour[0] * s, colour[1] * s * (1.0 - 0.06 * low), colour[2] * s * (1.0 - 0.14 * low), 1.0)

    def shade(c, mul):
        return (c[0] * mul, c[1] * mul, c[2] * mul, 1.0)

    # The braincase: rings from its base to its crown (height, middle, half-width, how far forward, how far back).
    rows = ((0.02, -0.04, 0.04, 0.03, 0.05), (0.052, -0.03, 0.066, 0.035, 0.076), (0.104, -0.015, 0.073, 0.097, 0.094), (0.14, -0.02, 0.068, 0.087, 0.088),
            (0.166, -0.025, 0.047, 0.058, 0.06))
    n = 10

    def round_at(row, a):
        _y, cz, rx, rf, rb = row
        c, s = math.cos(a), math.sin(a)
        return rx * _sup(s, 0.85), cz + (rf if c >= 0.0 else rb) * _sup(c, 0.75)

    rings = []
    for i, row in enumerate(rows):
        y = row[0]
        ring = []
        for j in range(n):
            a = math.tau * j / n
            c = math.cos(a)
            x, z = round_at(row, a)
            # Behind the face it is in the dark.
            ring.append(t.vert(x, y0 + y, z, tint(x, y, z, 0.1 if (i < 2 and c > 0.3) else 1.0)))
        rings.append(ring)
    whole = back and not face_only
    for i in range(len(rows) - 1):
        if (i == 0 and not whole) or (i == 1 and face_only):
            continue
        for j in range(n):
            if not whole and math.cos(math.tau * (j + 0.5) / n) < (-0.1 if face_only else -0.35):
                continue
            j1 = (j + 1) % n
            t.face((rings[i][j], rings[i][j1], rings[i + 1][j1], rings[i + 1][j]), PAINT)
    top = t.vert(0.0, y0 + 0.178, -0.025, tint(0.0, 0.178, -0.025))
    for j in range(n):
        if not face_only or math.cos(math.tau * (j + 0.5) / n) > 0.5:
            t.face((rings[-1][j], rings[-1][(j + 1) % n], top), PAINT)
    if whole:
        t.face(tuple(reversed(rings[0])), PAINT)

    # The face is one skin over named points, so it shades as bone and not as facets. Heights are from the teeth's tips.
    def fy(y):
        return 0.014 + (y - 0.014) * 0.82

    pts = {
        "t0": (0.0, 0.126, 0.074), "t1": (0.036, 0.129, 0.064), "t2": (0.063, 0.118, 0.044),
        "o1": (0.013, 0.11, 0.084), "o2": (0.036, 0.118, 0.083), "o3": (0.057, 0.108, 0.07), "o4": (0.059, 0.086, 0.066), "o5": (0.038, 0.073, 0.076),
        "o6": (0.015, 0.083, 0.083), "c1": (0.069, 0.082, 0.054), "c2": (0.055, 0.06, 0.065), "c3": (0.036, 0.054, 0.076),
        "n0": (0.0, 0.089, 0.093), "n1": (0.009, 0.083, 0.088), "n2": (0.014, 0.055, 0.084), "n3": (0.0, 0.045, 0.09),
        "a0": (0.0, 0.014, 0.086), "am": (0.018, 0.014, 0.082), "a1": (0.031, 0.014, 0.07), "a2": (0.033, 0.014, 0.026),
        "cl": (0.066, 0.067, 0.056), "e0": (0.071, 0.079, -0.006), "e1": (0.07, 0.067, -0.006), "cb": (0.036, 0.054, 0.026),
    }
    pts = {name: (q[0], fy(q[1]), q[2]) for name, q in pts.items()}
    # The brow hangs from the braincase's own edge.
    (xa, za), (xb, zb) = round_at(rows[2], math.tau / n), round_at(rows[2], math.tau * 2.0 / n)
    pts["t0"], pts["t1"], pts["t2"] = (0.0, rows[2][0], round_at(rows[2], 0.0)[1]), (xa, rows[2][0], za), (lerp(xa, xb, 0.45), rows[2][0], lerp(za, zb, 0.45))
    ids = {}

    def vid(name, s):
        x, y, z = pts[name]
        key = (name, s if x else 1.0)
        if key not in ids:
            ids[key] = t.vert(x * s, y0 + y, z, tint(x * s, y, z))
        return ids[key]

    def skin(names, facing=(0.3, 0.0, 1.0)):
        for s in (1.0, -1.0):
            q = [(pts[nm][0] * s, pts[nm][1], pts[nm][2]) for nm in names]
            nx = ny = nz = 0.0
            for i in range(len(q)):
                a, b = q[i], q[(i + 1) % len(q)]
                nx += (a[1] - b[1]) * (a[2] + b[2])
                ny += (a[2] - b[2]) * (a[0] + b[0])
                nz += (a[0] - b[0]) * (a[1] + b[1])
            order = [vid(nm, s) for nm in names]
            if nx * facing[0] * s + ny * facing[1] + nz * facing[2] < 0.0:
                order.reverse()
            t.face(tuple(order), PAINT)

    def face(names_or_pts, mul=1.0, facing=(0.3, 0.0, 1.0), cols=None):
        q0 = [pts[v] if isinstance(v, str) else (v[0], fy(v[1]), v[2]) for v in names_or_pts]
        for s in (1.0, -1.0):
            q = [(x * s, y0 + y, z) for x, y, z in q0]
            cx, cy, cz = (sum(v[i] for v in q0) / len(q0) for i in range(3))
            t.poly(q, PAINT, cols or tint(cx, cy, cz, mul), facing=(facing[0] * s, facing[1], facing[2]))

    # Brow, the bridge of the nose, the socket's outer rim, cheekbone, upper jaw.
    skin(["t0", "t1", "o2", "o1"], (0.1, 0.4, 1.0))
    skin(["t1", "t2", "o3", "o2"], (0.5, 0.4, 1.0))
    skin(["t0", "o1", "o6", "n1", "n0"])
    skin(["t2", "o3", "o4", "c1"], (1.0, 0.0, 0.7))
    skin(["o4", "c1", "c2"], (0.6, -0.2, 1.0))
    skin(["o4", "c2", "c3", "o5"], (0.3, -0.1, 1.0))
    skin(["n1", "o6", "o5", "c3", "n2"])
    skin(["n2", "c3", "a1", "am"], (0.5, 0.0, 1.0))
    skin(["n3", "n2", "am", "a0"], (0.1, 0.0, 1.0))
    # The cheekbone's arch back to the ear, the hollow of the temple behind it; and what shows only when it is picked up or
    # lies on its side: the side of the upper jaw, under the arch and the cheekbone, the palate, the back of the cheek.
    if not face_only:
        skin(["c1", "cl", "e1", "e0"], (1.0, 0.0, 0.0))
        face(["c1", "e0", (0.061, 0.078, -0.006), (0.058, 0.08, 0.05)], 0.9, (0.0, 1.0, 0.0))
    face(["t2", "c1", "e0"], 0.14, (1.0, 0.0, 0.2))
    if whole:
        skin(["c3", "a1", "a2", "cb"], (1.0, 0.0, 0.0))
        face(["cl", "e1", (0.061, 0.066, -0.006), (0.056, 0.064, 0.056)], 0.45, (0.0, -1.0, 0.0))
        face(["c2", "c3", "cb", (0.056, 0.062, 0.03)], 0.4, (0.0, -1.0, 0.0))
        face(["a0", "am", "a1", "a2", (0.0, 0.014, 0.026)], 0.3, (0.0, -1.0, 0.0))
        face(["o4", "c1", "c2", "c3", "o5"], 0.1, (0.0, 0.0, -1.0))
    # The sockets and the nose: pits into the dark.
    rim = ["o1", "o2", "o3", "o4", "o5", "o6"]
    ob, nb = (0.034, 0.095, 0.056), (0.0, 0.066, 0.058)
    for i in range(6):
        a = pts[rim[i]]
        edge = tint(a[0], a[1], a[2], 0.2)
        face([rim[i], rim[(i + 1) % 6], ob], cols=[edge, edge, PIT], facing=(0.0, 0.0, 1.0))
    for a, b in (("n0", "n1"), ("n1", "n2"), ("n2", "n3")):
        edge = tint(0.0, 0.05, 0.08, 0.16)
        face([a, b, nb], cols=[edge, edge, PIT], facing=(0.0, 0.0, 1.0))

    # Teeth along an arc of (x, z) points: `count` to a stretch, some lost.
    def teeth(arc, counts, y_top, y_tip, lost, inset):
        for s in (1.0, -1.0):
            for (xa, za), (xb, zb), count in zip(arc, arc[1:], counts):
                for i in range(count):
                    if rng.random() < lost:
                        continue
                    f0, f1 = (i + 0.1) / count, (i + 0.9) / count
                    g0, g1 = f0 + 0.08 / count, f1 - 0.08 / count
                    out = (s * (xa + xb) * 0.5, 0.0, (za + zb) * 0.5 - 0.02)
                    c = tint(xa, 0.1, za, rng.uniform(1.0, 1.25))
                    t.poly([(s * lerp(xa, xb, f0), y0 + y_top, lerp(za, zb, f0)), (s * lerp(xa, xb, f1), y0 + y_top, lerp(za, zb, f1)),
                            (s * lerp(xa, xb, g1), y0 + y_tip, lerp(za, zb, g1) - inset), (s * lerp(xa, xb, g0), y0 + y_tip, lerp(za, zb, g0) - inset)], PAINT, c, facing=out)
            # What shows between them.
            for (xa, za), (xb, zb) in zip(arc, arc[1:]):
                out = (s * (xa + xb) * 0.5, 0.0, (za + zb) * 0.5 - 0.02)
                t.poly([(s * xa * 0.86, y0 + y_top, za - 0.006), (s * xb * 0.86, y0 + y_top, zb - 0.004), (s * xb * 0.86, y0 + y_tip, zb - 0.004), (s * xa * 0.86, y0 + y_tip, za - 0.006)],
                       PAINT, PIT, facing=out)

    teeth(((0.0, 0.0865), (0.018, 0.0825), (0.031, 0.0705), (0.0335, 0.03))[:3 if face_only else 4], (2, 2, 2), 0.014, 0.001, 0.22, 0.002)
    if not jaw:
        return

    # The jaw: chin, body, and the branch up to its hinge under the cheekbone. Its inside shows from behind, darker.
    jp = {"j0": (0.0, -0.044, 0.08), "j1": (0.018, -0.044, 0.074), "j2": (0.036, -0.042, 0.046), "b1": (0.046, -0.04, 0.004),
          "k0": (0.0, -0.015, 0.0815), "k1": (0.02, -0.015, 0.0755), "k2": (0.037, -0.015, 0.048), "b2": (0.046, -0.014, 0.008),
          "r2": (0.049, -0.044, -0.028), "r3": (0.057, 0.05, -0.03), "r4": (0.054, 0.042, -0.006)}
    jid = {}

    def jv(name, s, inner):
        x, y, z = jp[name]
        key = (name, s if x else 1.0, inner)
        if key not in jid:
            jid[key] = t.vert(x * s, y0 + y, z, tint(x * s, y + 0.06, z, 0.3 if inner else 0.95))
        return jid[key]

    for names in (("j0", "j1", "k1", "k0"), ("j1", "j2", "k2", "k1"), ("j2", "b1", "b2", "k2"), ("b1", "r2", "r3", "r4", "b2")):
        for s in (1.0, -1.0):
            order = [jv(nm, s, False) for nm in names]
            t.face(tuple(order if s > 0.0 else reversed(order)), PAINT)
            order = [jv(nm, s, True) for nm in names]
            t.face(tuple(reversed(order) if s > 0.0 else order), PAINT)
    for s in (1.0, -1.0):
        c = tint(0.03, 0.0, 0.03, 0.4)
        t.poly([(x * s, y0 - 0.044, z) for x, z in ((0.0, 0.08), (0.018, 0.074), (0.036, 0.046), (0.046, 0.004), (0.049, -0.028), (0.039, -0.028), (0.036, 0.0), (0.026, 0.038), (0.012, 0.062),
                                                  (0.0, 0.067))], PAINT, c, facing=(0.0, -1.0, 0.0))
        t.poly([(0.046 * s, y0 - 0.014, 0.008), (0.054 * s, y0 + 0.042, -0.006), (0.046 * s, y0 + 0.04, -0.006), (0.038 * s, y0 - 0.014, 0.008)], PAINT, tint(0.05, 0.05, 0.0, 0.75), facing=(0.0, 0.2, 1.0))
        t.poly([(0.049 * s, y0 - 0.044, -0.028), (0.057 * s, y0 + 0.05, -0.03), (0.049 * s, y0 + 0.048, -0.03), (0.041 * s, y0 - 0.044, -0.028)], PAINT, tint(0.05, 0.05, 0.0, 0.6), facing=(0.0, 0.0, -1.0))
    teeth(((0.0, 0.082), (0.02, 0.076), (0.037, 0.0485), (0.0455, 0.012)), (2, 2, 2), -0.015, -0.003, 0.25, -0.002)


def long_bone(m, a, b, r=0.015, colour=BONE, sides=6, k=1.0, head=True, seed=0.0):
    """A thigh bone from its knee end `a` to its hip end `b`, `r` its
    shaft's radius. With `head`, the ball of the hip on its neck and the
    knee's two knuckles; without, a plainer bone for a heap."""
    length, ahead, u1, u2 = props.frame(a, b)
    prof = ((0.0, 1.5), (0.03, 2.15), (0.085, 1.9), (0.17, 1.2), (0.36, 0.98), (0.68, 0.95), (0.85, 1.12), (0.93, 1.55), (1.0, 1.1))
    if not head:
        prof = ((0.0, 1.7), (0.06, 2.0), (0.2, 1.1), (0.8, 1.0), (0.94, 1.6), (1.0, 1.2))

    def at(f, side=0.0, up=0.0):
        # A thigh bone bows a little forward.
        bow = math.sin(f * math.pi) * length * 0.025
        return tuple(a[i] + ahead[i] * length * f + u1[i] * side + u2[i] * (up + bow) for i in range(3))

    def col(f, mul=1.0):
        s = k * mul * (0.82 + 0.25 * fbm(f * 7.0 + seed, seed * 3.0, 1.0, 2, seed))
        return (colour[0] * s, colour[1] * s, colour[2] * s * 0.95, 1.0)

    m.tube([at(f) for f, _r in prof], [r * q for _f, q in prof], sides, PAINT, [col(f, 0.8 if q > 1.4 else 1.0) for f, q in prof], caps=True, squash=(1.18, 0.9))
    if head:
        # The ball of the hip, off to one side on its neck; the knee's two knuckles.
        m.tube([at(0.93, 0.0), at(0.975, r * 1.5, r * 0.3), at(1.02, r * 2.6, r * 0.5), at(1.045, r * 3.3, r * 0.6)], [r * 1.0, r * 1.0, r * 1.45, r * 0.7], sides, PAINT, col(0.95), caps=True)
        for s in (-1.0, 1.0):
            m.tube([at(0.05, s * r * 1.05, -r * 0.5), at(0.0, s * r * 1.1, -r * 0.9), at(-0.035, s * r * 1.05, -r * 0.7)], [r * 1.0, r * 1.15, r * 0.6], 5, PAINT, col(0.02, 0.9), caps=True)


# ---------------------------------------------------------------- what he picks up

def lump(m, centre, radii, mat, colour, nu=7, nv=5, rough=0.2, seed=0.0, freq=9.0, flat=0.0):
    """A closed lump about `centre`: a ball of `radii` (x, y, z) pushed in
    and out by noise. `colour` is one colour or colour(x, y, z, n) with `n`
    the unit direction out. `flat` presses its underside flat that far up."""
    def f(u, v):
        a, b = u * math.tau, (v - 0.5) * math.pi
        n = (math.cos(b) * math.cos(a), math.sin(b), math.cos(b) * math.sin(a))
        q = 1.0 + rough * fbm(n[0] * freq + seed * 3.1, n[2] * freq + n[1] * freq * 0.7, 1.0, 2, seed)
        y = n[1] * radii[1] * q
        if flat:
            y = max(y, -radii[1] * (1.0 - flat))
        return (centre[0] + n[0] * radii[0] * q, centre[1] + y, centre[2] + n[2] * radii[2] * q), n

    def c(u, v):
        if not callable(colour):
            return colour
        pt, n = f(u, v)
        return colour(pt[0], pt[1], pt[2], n)

    props.sheet(m, lambda u, v: f(u, v)[0], nu, nv, mat, c, flip=True)


def item_stone(p):
    # A flint out of the abbey's own walls: knapped faces black, the rind pale.
    def c(x, y, z, n):
        rind = n[0] * 0.5 + n[1] * 0.6 - n[2] * 0.3 + 0.5 * fbm(n[0] * 1.6, n[2] * 1.6 + n[1], 1.0, 2, 4.0)
        k = 0.8 + 0.4 * fbm(x * 60.0, z * 60.0, 1.0, 2, 1.0)
        return (0.07 * k, 0.066 * k, 0.057 * k, 1.0) if rind > 0.1 else (0.011 * k, 0.011 * k, 0.013 * k, 1.0)

    lump(p.hard, (0.0, -0.024, 0.0), (0.05, 0.036, 0.037), PAINT, c, nu=8, nv=5, rough=0.42, seed=3.0, freq=1.3, flat=0.3)


def item_cup(p):
    # Turned ash, 9 cm high: a foot ring, the lathe's lines, a worn lip. Its inside is real: it is picked up and thrown.
    prof = ((0.0, 0.0), (0.03, 0.0), (0.031, 0.006), (0.026, 0.011), (0.03, 0.03), (0.037, 0.06), (0.0395, 0.086), (0.038, 0.09), (0.0355, 0.087), (0.032, 0.05),
            (0.026, 0.02), (0.0, 0.016))
    sides = 12
    c0 = rgba(PINE, 0.9)

    def f(u, v):
        i = min(int(v * (len(prof) - 1)), len(prof) - 2)
        q = v * (len(prof) - 1) - i
        r, y = lerp(prof[i][0], prof[i + 1][0], q), lerp(prof[i][1], prof[i + 1][1], q)
        return (math.cos(u * math.tau) * r, y - 0.04, math.sin(u * math.tau) * r)

    def c(u, v):
        inside = v > 7.5 / (len(prof) - 1)
        k = (0.3 if inside else 1.0) * (0.9 + 0.12 * math.sin(v * 43.0)) * (0.86 + 0.2 * fbm(u * 9.0, v * 3.0, 1.0, 2, 2.0))
        return (c0[0] * k, c0[1] * k, c0[2] * k, 1.0)

    props.sheet(p.soft, f, sides, len(prof) - 1, WOOD, c, uv=(0.25, 0.35), flip=True)


def item_bone(p):
    # A thigh bone, long in the ground: it lies as it was turned up.
    long_bone(p.soft, (-0.15, -0.027, 0.012), (0.15, -0.031, -0.012), r=0.0125, k=0.8, seed=2.0)


def item_apple(p):
    # A windfall: a small green-yellow apple, russeted, one side gone brown where it fell.
    def f(u, v):
        a, b = u * math.tau, (v - 0.5) * math.pi
        r = 0.037 * (1.0 + 0.06 * math.sin(a * 5.0 + 1.0) * math.cos(b)) * (1.0 + 0.05 * fbm(math.cos(a) * 2.0, math.sin(a) * 2.0 + b, 1.0, 2, 5.0))
        # Dimpled at the stalk and the eye.
        y = math.sin(b) * 0.033 * (1.0 - 0.3 * abs(math.sin(b)) ** 6)
        return (math.cos(b) * math.cos(a) * r + 0.003, y - 0.019, math.cos(b) * math.sin(a) * r)

    def c(u, v):
        a, b = u * math.tau, (v - 0.5) * math.pi
        blush = smoothstep(0.1, 0.9, 0.5 + 0.5 * math.cos(a - 0.6)) * smoothstep(-0.6, 0.5, b)
        bruise = smoothstep(0.55, 0.9, math.cos(a - 3.4) * math.cos(b + 0.5))
        k = 0.85 + 0.25 * fbm(u * 14.0, v * 9.0, 1.0, 2, 6.0)
        base = [lerp(0.07, 0.075, blush) * k, lerp(0.075, 0.035, blush) * k, lerp(0.022, 0.016, blush) * k]
        return tuple(lerp(base[i], (0.028, 0.019, 0.011)[i], bruise) for i in range(3)) + (1.0,)

    props.sheet(p.soft, f, 9, 6, PAINT, c, flip=True)
    p.soft.tube([(0.003, 0.004, 0.0), (0.006, 0.014, 0.002), (0.012, 0.021, 0.003)], [0.0022, 0.0018, 0.0016], 4, PAINT, (0.02, 0.014, 0.009, 1.0), caps=True)


def item_bread(p):
    # A round maslin loaf, the baker's cross cut in its top, flour in the cut.
    def f(u, v):
        a = u * math.tau
        r = 0.098 * (1.0 + 0.05 * fbm(math.cos(a) * 1.5, math.sin(a) * 1.5, 1.0, 2, 7.0))
        prof = ((0.0, 0.0), (0.78, 0.0), (1.0, 0.022), (0.97, 0.048), (0.8, 0.07), (0.45, 0.085), (0.0, 0.09))
        i = min(int(v * (len(prof) - 1)), len(prof) - 2)
        q = v * (len(prof) - 1) - i
        rr, y = lerp(prof[i][0], prof[i + 1][0], q) * r, lerp(prof[i][1], prof[i + 1][1], q)
        x, z = math.cos(a) * rr, math.sin(a) * rr
        # The cross cut opens as the loaf rises.
        cut = max(math.exp(-(x / 0.012) ** 2), math.exp(-(z / 0.012) ** 2)) * smoothstep(0.5, 0.75, v) * (1.0 - smoothstep(0.0, 0.085, max(abs(x), abs(z))) * 0.6)
        return (x, y * (1.0 + 0.1 * fbm(x * 9.0, z * 9.0, 1.0, 2, 8.0)) - cut * 0.012 - 0.045, z)

    def c(u, v):
        pt = f(u, v)
        cut = max(math.exp(-(pt[0] / 0.011) ** 2), math.exp(-(pt[2] / 0.011) ** 2)) * smoothstep(0.5, 0.75, v)
        k = (0.75 + 0.35 * fbm(pt[0] * 16.0, pt[2] * 16.0, 1.0, 2, 9.0)) * lerp(0.55, 1.0, smoothstep(0.0, 0.5, v))
        crust = (0.048 * k, 0.034 * k, 0.019 * k)
        crumb = (0.085, 0.07, 0.045)
        return tuple(lerp(crust[i], crumb[i], cut * 0.8) for i in range(3)) + (1.0,)

    props.sheet(p.soft, f, 16, 6, PAINT, c, flip=True)


# ---------------------------------------------------------------- the graveyard

# The precinct's grass and dug earth (tools/build/env_precinct.py, GROUND), so a grave sits in its ground.
TURF = (0.8, 0.86, 0.66)
EARTH = (0.62, 0.52, 0.42)
GRASS_C = porter.srgb(0.4, 0.46, 0.24)
STALK_C = porter.srgb(0.46, 0.41, 0.27)
GREY_WOOD = (0.44, 0.43, 0.4)


def blade(m, x, y, z, yaw, lean, height, width, col, tip_k=1.25):
    """One flat blade of grass or leaf (the growth material bends it in the wind by its UV's height)."""
    c, s = math.cos(yaw), math.sin(yaw)
    ax, az = -s * width * 0.5, c * width * 0.5
    tx, tz = x + c * lean * height, z + s * lean * height
    root = (col[0] * 0.45, col[1] * 0.45, col[2] * 0.45, 1.0)
    tip = (col[0] * tip_k, col[1] * tip_k, col[2] * tip_k, 1.0)
    a = m.vert(x - ax, y - 0.03, z - az, root, (0.0, 0.0))
    b = m.vert(x + ax, y - 0.03, z + az, root, (1.0, 0.0))
    v = m.vert(tx, y + height, tz, tip, (0.5, height))
    m.face((a, b, v), "growth")


def tuft(m, x, y, z, size, col=None, count=(5, 8)):
    """Long grass gone to seed: what grows against a marker nobody scythes round."""
    n = random.randint(*count)
    for i in range(n):
        yaw = math.tau * i / n + random.uniform(-0.5, 0.5)
        q = random.uniform(0.0, 1.0)
        c = col or tuple(lerp(GRASS_C[k], STALK_C[k], q) * random.uniform(0.75, 1.1) for k in range(3))
        blade(m, x + math.cos(yaw) * 0.04, y, z + math.sin(yaw) * 0.04, yaw, random.uniform(0.1, 0.7), size * random.uniform(0.5, 1.0), random.uniform(0.025, 0.045) * (0.7 + size), c)


def mound(m, length, width, height, mat=None, colour=TURF, k=0.7, seed=0.0, lumps=0.25, hollow=None, nu=14, nv=7, sharp=0.6):
    """A grave's mound about the origin, `length` along x: turf or earth,
    out of true. `hollow` (x, z, half-length, half-width, depth) is where
    it has fallen in. Returns its height at (x, z)."""
    def h(x, z):
        u, v = x / (length * 0.5), z / (width * 0.5)
        a = abs(u) ** 2.6 + abs(v) ** 2.2
        y = height * max(0.0, 1.0 - a) ** sharp * (1.0 + lumps * fbm(x, z, 2.6, 3, seed)) * (1.0 + 0.18 * fbm(x, z, 0.9, 2, seed + 7.0))
        if hollow:
            y -= hollow[4] * math.exp(-((x - hollow[0]) / hollow[2]) ** 2 - ((z - hollow[1]) / hollow[3]) ** 2)
        return max(y, 0.0) - 0.006

    def f(u, v):
        x, z = (u - 0.5) * length, (v - 0.5) * width
        return (x, h(x, z), z)

    def c(u, v):
        x, z = (u - 0.5) * length, (v - 0.5) * width
        q = k * (0.86 + 0.3 * fbm(x, z, 1.7, 3, seed + 3.0))
        if hollow:
            q *= 1.0 - 0.6 * math.exp(-((x - hollow[0]) / hollow[2]) ** 2 - ((z - hollow[1]) / hollow[3]) ** 2)
        return rgba(colour, q)

    props.sheet(m, f, nu, nv, mat or "grass_leafy", c, flip=True)
    return h


def litter(m, seed, count=10, rx=1.15, rz=0.6):
    """A few of the yews' and the orchard's leaves blown against a grave's foot."""
    rng = random.Random(seed)
    for _ in range(count):
        a = rng.uniform(0.0, math.tau)
        x, z = math.cos(a) * rx * rng.uniform(0.85, 1.05), math.sin(a) * rz * rng.uniform(0.85, 1.1)
        r, turn = rng.uniform(0.035, 0.065), rng.uniform(0.0, math.tau)
        q = rng.uniform(0.45, 0.9)
        pts = [(x + math.cos(turn + math.tau * i / 4) * r * (1.0 if i % 2 else 0.55), 0.021 + (rng.uniform(0.0, 0.012) if i == 0 else 0.0), z + math.sin(turn + math.tau * i / 4) * r * (1.0 if i % 2 else 0.55))
               for i in range(4)]
        m.poly(pts, PAINT, (0.21 * q, rng.uniform(0.13, 0.2) * q, 0.108 * q, 1.0), facing=(0, 1, 0))


def wooden_cross(m, foot, lean=(0.1, 0.0), height=0.95, span=0.5, turn=0.0):
    """A grave's cross of two weathered boards, pegged, standing at `foot`
    and leaning `lean` (toward +x, toward +z). Its face looks along x."""
    up = props._norm((lean[0], 1.0, lean[1]))
    a = (foot[0] - up[0] * 0.15, foot[1] - 0.15, foot[2] - up[2] * 0.15)
    b = tuple(foot[i] + up[i] * height for i in range(3))
    side = props._norm((math.sin(turn), -lean[1], math.cos(turn)))
    grey = tone(GREY_WOOD, 0.12)
    beam(m, a, b, 0.032, 0.078, grey, up=side)
    c = tuple(foot[i] + up[i] * height * 0.7 + (0.026 if i == 0 else 0.0) for i in range(3))
    drop = 0.035   # the arm has slipped on its peg
    beam(m, (c[0] - side[0] * span * 0.5, c[1] - side[1] * span * 0.5 + drop, c[2] - side[2] * span * 0.5), (c[0] + side[0] * span * 0.5, c[1] + side[1] * span * 0.5 - drop, c[2] + side[2] * span * 0.5),
         0.026, 0.07, tone(GREY_WOOD, 0.12))
    props.nail(m, (c[0] + 0.014, c[1], c[2]), (1, 0, 0), r=0.012, colour=rgba(GREY_WOOD, 0.5), mat=WOOD)


def graved(p, yaw, shift):
    """The space a grave is built in: turned and moved a little, so a row of them is not ruled."""
    return props.Placed(p.hard, (shift[0], 0.0, shift[1]), yaw), props.Placed(p.soft, (shift[0], 0.0, shift[1]), yaw)


def grave(p):
    hard, soft = graved(p, 0.05, (0.02, -0.03))
    h = mound(soft, 1.95, 0.86, 0.26, seed=1.0)
    wooden_cross(hard, (-0.84, h(-0.84, 0.02), 0.02), lean=(-0.16, 0.2), height=0.92)
    for x, z, s in ((-0.86, 0.14, 0.34), (-0.9, -0.12, 0.3), (-0.7, 0.3, 0.2), (0.5, -0.36, 0.22), (0.86, 0.1, 0.2)):
        tuft(hard, x, max(h(x, z), 0.01) + 0.03, z, s)
    litter(hard, 11, 9)


def grave_plain(p):
    hard, soft = graved(p, -0.07, (-0.05, 0.04))
    h = mound(soft, 1.8, 0.8, 0.19, seed=2.0, lumps=0.35, sharp=0.75)
    # Nothing marks it but the grass nobody cuts, and the stump of a stake.
    beam(hard, (-0.82, 0.0, -0.05), (-0.86, 0.24, -0.02), 0.045, 0.04, tone(GREY_WOOD, 0.1), taper=0.7)
    for x, z, s in ((-0.8, 0.1, 0.36), (-0.6, -0.28, 0.26), (0.1, 0.34, 0.24), (0.7, -0.2, 0.3), (0.4, 0.0, 0.2), (-0.2, -0.1, 0.22)):
        tuft(hard, x, max(h(x, z), 0.01) + 0.03, z, s)
    litter(hard, 12, 12)


def grave_sunk(p):
    hard, soft = graved(p, 0.03, (0.04, 0.02))
    hole = (0.28, 0.03, 0.42, 0.2, 0.3)
    h = mound(soft, 1.9, 0.9, 0.2, seed=3.0, hollow=hole, nu=18, nv=9, lumps=0.2)
    # Where the turf has gone in: a ragged dark mouth, earth at its lip.
    pts = []
    for i in range(11):
        a = math.tau * i / 11
        r = 1.0 + 0.3 * fbm(math.cos(a) * 2.0, math.sin(a) * 2.0, 1.0, 2, 5.0)
        pts.append((hole[0] + math.cos(a) * 0.34 * r, math.sin(a) * 0.15 * r + hole[1]))
    hard.poly([(x, max(h(x, z), 0.0) + 0.035, z) for x, z in pts], DARK, BLACK, facing=(0, 1, 0))
    for i in range(11):
        (xa, za), (xb, zb) = pts[i], pts[(i + 1) % 11]
        q = random.uniform(0.5, 0.8)
        out = 1.35
        hard.poly([(xa, max(h(xa, za), 0.0) + 0.036, za), (xb, max(h(xb, zb), 0.0) + 0.036, zb),
                   (hole[0] + (xb - hole[0]) * out, h(hole[0] + (xb - hole[0]) * out, zb * out) + 0.012, zb * out), (hole[0] + (xa - hole[0]) * out, h(hole[0] + (xa - hole[0]) * out, za * out) + 0.012, za * out)],
                  "grave_earth", [rgba(EARTH, q * 0.45)] * 2 + [rgba(EARTH, q)] * 2, facing=(0, 1, 0))
    wooden_cross(hard, (-0.86, h(-0.86, -0.04), -0.04), lean=(0.34, -0.12), height=0.78, span=0.44, turn=0.12)
    for x, z, s in ((-0.84, 0.12, 0.28), (-0.5, 0.36, 0.22), (0.86, -0.1, 0.26), (0.2, -0.4, 0.2)):
        tuft(hard, x, max(h(x, z), 0.01) + 0.03, z, s)
    litter(hard, 13, 8)


def worn(k=1.0, green=0.0):
    """Weathered stone cut from one block (material `stone_worn`): grey, `green` where moss has it."""
    q = k * random.uniform(0.92, 1.06)
    return (lerp(0.125, 0.045, green) * q, lerp(0.12, 0.058, green) * q, lerp(0.105, 0.032, green) * q, 1.0)


def grave_slab(p):
    hard, soft = graved(p, -0.04, (0.0, 0.03))
    mound(soft, 2.0, 0.9, 0.06, seed=4.0, lumps=0.5, sharp=0.4, nv=5, nu=10)
    # A coffin-shaped slab, a cross cut in relief down its length, broken across where the ground went from under it.
    crack = [(-0.34, 0.2), (-0.16, 0.27), (-0.05, 0.17), (0.12, 0.23), (0.31, 0.12)]   # (across, along): from one long edge to the other

    def half_width(x):
        return lerp(0.31, 0.215, (x + 0.9) / 1.8)

    for part in (0, 1):
        t = props.Placed(hard, (0.0, 0.09 if part == 0 else 0.1, 0.0 if part == 0 else 0.012), 0.0 if part == 0 else 0.035)

        def at(x, y, z, part=part):
            # The foot half has dropped at the break and tipped.
            return (x, y - (max(0.0, 0.9 - x) * 0.1 + z * 0.05 if part else (x + 0.9) * 0.012), z)

        edge = [(lerp(-half_width(al), half_width(al), (ac + 0.34) / 0.65), al) for ac, al in crack]
        if part == 0:
            outline = [(-0.9, -0.31), (-0.9, 0.31)] + [(al, ac) for ac, al in reversed(edge)]
            gap = -0.02
        else:
            outline = [(0.9, 0.215), (0.9, -0.215)] + [(al, ac) for ac, al in edge]
            gap = 0.02
        outline = [(x + (gap if abs(x) < 0.5 else 0.0), z) for x, z in outline]
        top = [at(x, 0.0, z) for x, z in outline]
        t.poly(top, "stone_worn", [worn(1.0, 0.5 * smoothstep(-0.1, 0.5, fbm(q[0] * 3.0, q[2] * 3.0, 1.0, 2, 2.0))) for q in top], facing=(0, 1, 0))
        n = len(outline)
        for i in range(n):
            (xa, za), (xb, zb) = outline[i], outline[(i + 1) % n]
            inner = abs(xa) < 0.5 and abs(xb) < 0.5
            c = worn(0.35) if inner else worn(0.75, 0.6)
            mid = ((xa + xb) * 0.5, (za + zb) * 0.5)
            out = (gap, 0.0, 0.0) if inner else (mid[0] * 0.2, 0.0, mid[1]) if abs(mid[1]) > 0.15 else (mid[0], 0.0, 0.0)
            t.poly([at(xa, 0.0, za), at(xb, 0.0, zb), at(xb, -0.13, zb), at(xa, -0.13, za)], "stone_worn", c, facing=out)
        # The cross: its shaft, its arms near the head, a stepped foot.
        for (a0, a1, w) in ((-0.76, 0.66, 0.036), (-0.63, -0.55, 0.17), (0.6, 0.68, 0.11), (0.68, 0.78, 0.16)):
            lo, hi = (max(a0, -0.9), min(a1, 0.2 - 0.07)) if part == 0 else (max(a0, 0.2 + 0.09), a1)
            if hi - lo < 0.02:
                continue
            w0, w1 = min(w, half_width(lo) - 0.04), min(w, half_width(hi) - 0.04)
            pts = [(lo, -w0), (hi, -w1), (hi, w1), (lo, w0)]
            t.poly([at(x, 0.022, z) for x, z in pts], "stone_worn", worn(1.15), facing=(0, 1, 0))
            for i in range(4):
                (xa, za), (xb, zb) = pts[i], pts[(i + 1) % 4]
                t.poly([at(xa, 0.022, za), at(xb, 0.022, zb), at(xb, 0.0, zb), at(xa, 0.0, za)], "stone_worn", worn(0.55), facing=((xa + xb) * 0.5 - (lo + hi) * 0.5, 0.0, (za + zb) * 0.5))
    # Black in the break.
    hard.poly([(0.08, 0.04, -0.3), (0.36, 0.04, -0.3), (0.36, 0.04, 0.3), (0.08, 0.04, 0.3)], DARK, BLACK, facing=(0, 1, 0))
    for x, z, s in ((-0.94, 0.2, 0.24), (-0.3, -0.36, 0.22), (0.5, 0.3, 0.24), (0.95, -0.05, 0.2), (0.2, 0.3, 0.16)):
        tuft(hard, x, 0.05, z, s)
    litter(hard, 14, 8, rx=1.05, rz=0.5)


def grave_stone(p):
    hard, soft = graved(p, 0.08, (-0.03, -0.02))
    h = mound(soft, 1.85, 0.82, 0.16, seed=5.0, lumps=0.3, sharp=0.7)
    # A discoid head-marker, a cross on its face worn nearly flat; it has tilted back and to one side.
    t = props.Placed(hard, (-0.9, -0.08, 0.03), math.pi * 0.5 + 0.16, 1.0, -0.2)
    outline = [(-0.085, 0.0), (0.085, 0.0), (0.075, 0.3)]
    for i in range(9):
        a = -0.62 + (math.pi + 1.24) * i / 8.0
        r = 0.185 * (1.0 + 0.05 * fbm(math.cos(a) * 2.0, math.sin(a) * 2.0, 1.0, 2, 6.0))
        outline.append((math.cos(a) * r - 0.012, 0.42 + math.sin(a) * r))
    outline.append((-0.075, 0.3))
    props.slab(t, outline, "z", -0.045, 0.045, worn(0.95, 0.25), mat="stone_worn", edge_shade=0.8)
    for lo, hi in (((-0.11, 0.4, 0.045), (0.09, 0.44, 0.055)), ((-0.03, 0.31, 0.045), (0.012, 0.53, 0.055))):
        t.box(lo, hi, "stone_worn", worn(1.15), faces="xXyYZ")
    for x, z, s in ((-0.95, 0.16, 0.3), (-0.92, -0.14, 0.34), (-0.6, 0.3, 0.2), (0.6, -0.3, 0.24), (0.8, 0.2, 0.2)):
        tuft(hard, x, max(h(x, z), 0.01) + 0.03, z, s)
    litter(hard, 15, 10)


def grave_fresh(p):
    hard, soft = graved(p, -0.02, (0.03, 0.0))
    # Dug this month: dark earth heaped high, clods rolled off it, the turf not yet laid back. No marker.
    h = mound(soft, 1.95, 0.88, 0.33, mat="grave_earth", colour=EARTH, k=0.55, seed=6.0, lumps=0.4, nu=16, nv=8, sharp=0.55)
    for _ in range(11):
        a = random.uniform(0.0, math.tau)
        x, z = math.cos(a) * random.uniform(0.75, 1.02), math.sin(a) * random.uniform(0.34, 0.5)
        r = random.uniform(0.03, 0.05)
        lump(soft, (x, max(h(x, z), 0.0) + r * 0.2, z), (r * random.uniform(0.9, 1.5), r * 0.6, r), "grave_earth", rgba(EARTH, random.uniform(0.5, 0.62)), nu=6, nv=3, rough=0.35, seed=x)
    # The sods cut off it, stacked at its foot and going yellow.
    for i in range(3):
        s = props.Placed(hard, (0.8 + i * 0.015, 0.0, -0.28 + i * 0.01), 0.3 + i * 0.25)
        s.box((-0.16, 0.012 + i * 0.05, -0.12), (0.16, 0.06 + i * 0.05, 0.12), "grave_earth", rgba(EARTH, 0.4), faces="xXzZ")
        s.box((-0.16, 0.012 + i * 0.05, -0.12), (0.16, 0.062 + i * 0.05, 0.12), "grass_leafy", rgba((0.8, 0.8, 0.5), 0.6), faces="Y")


# ---------------------------------------------------------------- the kitchen garden

def bed_frame(p, seed):
    """The edging of a dug bed 1.2 x 4 m: boards on edge, held by pegs driven outside them. Returns nothing."""
    m = p.hard
    rng = random.Random(seed)
    for sx in (-1, 1):
        z = -2.0
        for length in (rng.uniform(1.8, 2.2), None):
            z1 = 2.0 if length is None else z + length
            top = rng.uniform(0.13, 0.165)
            x = sx * 0.59 + rng.uniform(-0.01, 0.01)
            lean = rng.uniform(-0.012, 0.02) * sx
            beam(m, (x, top * 0.5, z + 0.004), (x + rng.uniform(-0.012, 0.012), top * 0.5 + rng.uniform(-0.012, 0.012), z1 - 0.004), 0.024, top + 0.02, tone(GREY_WOOD, 0.14), up=(lean * 6.0, 1.0, 0.0))
            for zz in (z + 0.25, z1 - 0.25, (z + z1) * 0.5):
                peg(m, (sx * 0.618 + rng.uniform(-0.004, 0.004), zz + rng.uniform(-0.1, 0.1)), rng.uniform(0.17, 0.25), rng)
            z = z1
    for sz in (-1, 1):
        top = rng.uniform(0.12, 0.16)
        beam(m, (-0.575, top * 0.5, sz * 1.988), (0.575, top * 0.5 + rng.uniform(-0.01, 0.01), sz * 1.988), 0.024, top + 0.02, tone(GREY_WOOD, 0.14))
        for xx in (-0.4, 0.4):
            peg(m, (xx + rng.uniform(-0.05, 0.05), sz * 2.016), rng.uniform(0.17, 0.24), rng, along_x=False)


def peg(m, at, top, rng, along_x=True):
    lean = rng.uniform(-0.05, 0.05)
    beam(m, (at[0], 0.0, at[1]), (at[0] + (lean if along_x else 0.0), top, at[1] + (0.0 if along_x else lean)), 0.034, 0.034, tone(OAK_DARK, 0.15), taper=0.8, ends="b", roll=rng.uniform(-0.3, 0.3))


def bed_earth(p, seed, rows=3, ridge=0.035, rough=0.02, k=0.9, along=True):
    """The bed's soil inside its boards: dug in `rows` ridges (along the bed, or across it), clods and all. Returns its height at (x, z)."""
    def h(x, z):
        wave = math.cos(x / 1.15 * rows * math.tau) if along else math.cos(z / 4.0 * rows * math.tau)
        edge = smoothstep(0.0, 0.1, 0.575 - abs(x)) * smoothstep(0.0, 0.14, 1.975 - abs(z))
        return 0.06 + edge * (0.04 + ridge * wave + rough * fbm(x, z, 5.0, 3, seed) + 0.015 * fbm(x, z, 1.1, 2, seed + 4.0))

    def f(u, v):
        x, z = lerp(-0.578, 0.578, u), lerp(-1.976, 1.976, v)
        return (x, h(x, z), z)

    def c(u, v):
        x, z = lerp(-0.578, 0.578, u), lerp(-1.976, 1.976, v)
        wave = math.cos(x / 1.15 * rows * math.tau) if along else math.cos(z / 4.0 * rows * math.tau)
        return rgba(EARTH, k * (0.82 + 0.14 * wave + 0.22 * fbm(x, z, 2.2, 3, seed + 1.0)))

    props.sheet(p.soft, f, 12 if along else 6, 12 if along else 28, "grave_earth", c, flip=True)
    return h


def garden_bed(p):
    # Dug over for the winter and left rough. The gardener's line is still pegged down its middle.
    bed_frame(p, 21)
    h = bed_earth(p, 1.0, rows=7, ridge=0.03, rough=0.035, along=False)
    m = p.hard
    for z in (-1.7, 1.62):
        beam(m, (0.03, 0.04, z), (0.045, 0.3, z + 0.02), 0.022, 0.022, tone(PINE, 0.1), taper=0.7)
    props.rope(p.soft, [(0.04, 0.26, -1.69), (0.045, 0.19, -0.6), (0.05, 0.17, 0.4), (0.045, 0.26, 1.63)], r=0.004, colour=(0.2, 0.17, 0.11), sides=3)
    for _ in range(7):
        x, z = random.uniform(-0.45, 0.45), random.uniform(-1.8, 1.8)
        r = random.uniform(0.04, 0.07)
        lump(p.soft, (x, h(x, z) + r * 0.3, z), (r * 1.2, r * 0.7, r), "grave_earth", rgba(EARTH, random.uniform(0.5, 0.75)), nu=5, nv=3, rough=0.3, seed=x)


CABBAGE = (0.03, 0.05, 0.03)
ROT = (0.045, 0.04, 0.02)


def leaf(m, x, y, z, yaw, length, width, colour, droop=0.3, mat=PAINT):
    """A big leaf lying out from a stalk, seen from both sides."""
    c, s = math.cos(yaw), math.sin(yaw)
    pts = [(x, y + 0.02, z), (x + c * length * 0.5 - s * width, y + 0.03 * (1.0 - droop), z + s * length * 0.5 + c * width), (x + c * length, y - droop * length * 0.3 + 0.012, z + s * length),
           (x + c * length * 0.5 + s * width, y + 0.025 * (1.0 - droop), z + s * length * 0.5 - c * width)]
    k = random.uniform(0.7, 1.15)
    col = [rgba(colour, k * 0.6), rgba(colour, k), rgba(colour, k * 0.8), rgba(colour, k)]
    m.poly(pts, mat, col, facing=(0, 1, 0))
    m.poly(pts, mat, [rgba(colour, k * 0.4)] * 4, facing=(0, -1, 0))


def garden_bed_cabbage(p):
    # The cabbages cut: stumps in two rows, their outer leaves left to rot, two heads not worth the cutting.
    bed_frame(p, 22)
    h = bed_earth(p, 2.0, rows=2, ridge=0.022, rough=0.02)
    i = 0
    for sx in (-1, 1):
        z = -1.7 + (0.2 if sx > 0 else 0.0)
        while z < 1.8:
            x = sx * 0.29 + random.uniform(-0.04, 0.04)
            y = h(x, z)
            i += 1
            if i in (3, 10):
                lump(p.soft, (x, y + 0.11, z), (0.1, 0.085, 0.1), PAINT, lambda px, py, pz, n: rgba(CABBAGE, 0.7 + 0.5 * fbm(px * 30.0, pz * 30.0, 1.0, 2, 3.0)), nu=7, nv=4, rough=0.25, seed=z, freq=3.0)
                for j in range(5):
                    leaf(p.hard, x, y + 0.05, z, j * 1.3 + random.uniform(-0.3, 0.3), random.uniform(0.16, 0.22), 0.07, CABBAGE, droop=0.5)
            elif i != 7:
                top = random.uniform(0.07, 0.16)
                lean = (random.uniform(-0.04, 0.04), random.uniform(-0.04, 0.04))
                p.soft.tube([(x, y - 0.02, z), (x + lean[0], y + top, z + lean[1])], [0.02, 0.016], 5, PAINT, [rgba(ROT, 0.7), rgba((0.07, 0.065, 0.04))], caps=True)
                for j in range(random.randint(1, 3)):
                    leaf(p.hard, x, y + 0.012, z, random.uniform(0.0, math.tau), random.uniform(0.14, 0.24), random.uniform(0.05, 0.08), ROT if random.random() < 0.7 else CABBAGE, droop=0.1)
            z += random.uniform(0.4, 0.52)


LEEK = (0.035, 0.06, 0.045)
ONION = (0.1, 0.085, 0.04)


def garden_bed_leeks(p):
    # Leeks standing through the winter in two rows; the third row was onions, lifted, their tops left lying.
    bed_frame(p, 23)
    h = bed_earth(p, 3.0, rows=3, ridge=0.03, rough=0.015)
    for x0 in (-0.38, 0.0):
        z = -1.75
        while z < 1.8:
            x = x0 + random.uniform(-0.025, 0.025)
            if random.random() < 0.85:
                y = h(x, z)
                p.soft.tube([(x, y - 0.02, z), (x, y + 0.07, z)], [0.014, 0.011], 4, PAINT, [(0.09, 0.085, 0.065, 1.0), rgba(LEEK, 1.2)])
                fan = random.uniform(0.0, math.pi)
                for j in range(4):
                    side = -1.0 if j % 2 else 1.0
                    blade(p.hard, x, y + 0.08, z, fan + (0.0 if side > 0 else math.pi) + random.uniform(-0.25, 0.25), random.uniform(0.25, 0.8), random.uniform(0.16, 0.3), 0.04,
                          tuple(c * random.uniform(0.8, 1.15) for c in LEEK), 1.1)
            z += random.uniform(0.2, 0.27)
    for _ in range(16):
        x, z = 0.38 + random.uniform(-0.08, 0.08), random.uniform(-1.8, 1.8)
        leaf(p.hard, x, h(x, z) + 0.004, z, random.uniform(0.0, math.tau), random.uniform(0.18, 0.3), 0.012, ONION, droop=0.0)
    # One onion missed.
    lump(p.soft, (0.36, h(0.36, 0.7) + 0.02, 0.7), (0.035, 0.03, 0.035), PAINT, rgba((0.07, 0.045, 0.02)), nu=6, nv=3, rough=0.1)


def garden_bed_beans(p):
    # The beans are over: the poles pulled and laid down the bed in a heap, the haulm brown on them, two left standing crossed.
    bed_frame(p, 24)
    h = bed_earth(p, 4.0, rows=2, ridge=0.02, rough=0.025)
    hazel = (0.3, 0.26, 0.2)
    for i in range(7):
        x = -0.3 + i * 0.07 + random.uniform(-0.05, 0.05)
        z0 = random.uniform(-1.85, -1.3)
        length = random.uniform(2.3, 2.9)
        skew = random.uniform(-0.12, 0.12)
        a = (x, h(x, z0) + 0.03 + i * 0.012, z0)
        b = (x + skew * 2.0, h(x + skew, z0 + length * 0.9) + 0.035 + (i % 3) * 0.025, min(z0 + length, 1.93))
        p.soft.tube([a, tuple((a[k] + b[k]) * 0.5 + (0.01 if k == 1 else 0.0) for k in range(3)), b], [0.017, 0.014, 0.009], 5, WOOD, rgba(hazel, random.uniform(0.8, 1.15)), caps=True)
        for _ in range(4):
            f = random.uniform(0.1, 0.95)
            q = tuple(lerp(a[k], b[k], f) for k in range(3))
            blade(p.hard, q[0], q[1] + 0.02, q[2], random.uniform(0.0, math.tau), random.uniform(0.8, 1.6), random.uniform(0.08, 0.16), 0.05, tuple(c * random.uniform(0.6, 1.0) for c in STALK_C), 0.9)
    for (x0, z0), (x1, z1) in (((0.34, 0.9), (0.2, 1.5)), ((0.38, 1.6), (0.24, 0.85))):
        p.soft.tube([(x0, 0.0, z0), ((x0 + x1) * 0.5, 0.75, (z0 + z1) * 0.5), (x1, 1.45, z1)], [0.018, 0.014, 0.009], 5, WOOD, rgba(hazel, random.uniform(0.8, 1.1)), caps=True)
    props.rope(p.soft, [(0.3, 0.86, 1.2), (0.27, 0.9, 1.24), (0.3, 0.92, 1.21), (0.33, 0.88, 1.18), (0.3, 0.86, 1.2)], r=0.005, colour=(0.2, 0.17, 0.11), sides=3)
    for _ in range(18):
        x, z = random.uniform(-0.45, 0.45), random.uniform(-1.8, 1.8)
        leaf(p.hard, x, h(x, z) + 0.004, z, random.uniform(0.0, math.tau), random.uniform(0.06, 0.12), 0.035, ROT, droop=0.0)


# ---------------------------------------------------------------- the churchyard cross

def churchyard_cross(p):
    """A preaching cross on three steps, 3.5 m high: the steps hollowed by
    knees, green at the foot, the shaft eight-sided, the head worn until
    its arms are stumps and one is gone."""
    m = p.hard

    def stone(x, y, z, k=1.0):
        q = k * (0.86 + 0.22 * fbm(x * 1.3 + y, z * 1.3 - y, 1.0, 3, 2.0))
        # Green from the ground up and wherever water stands; grey-gold lichen in blotches higher.
        moss = lerp(0.35, 1.0, smoothstep(0.05, 0.9, y + 0.3 * fbm(x * 2.0, z * 2.0 + y, 1.0, 2, 5.0)))
        lichen = smoothstep(0.25, 0.6, fbm(x * 3.1 + 4.0, z * 3.1 + y * 2.4, 1.0, 3, 9.0))
        return (lerp(0.56, 0.6, lichen) * q, lerp(0.55, 0.57, lichen) * q, lerp(0.52, 0.42, lichen) * q, moss)

    def step(half, y0, y1, wear):
        n = 4
        cuts = [-half + 2.0 * half * i / n for i in range(n + 1)]

        def top(x, z):
            # Worn down toward the middle of each edge, where people kneel and climb.
            e = max(abs(x), abs(z)) / half
            mid = 1.0 - min(abs(x), abs(z)) / half
            return y1 - wear * smoothstep(0.55, 1.0, e) * mid ** 2 - 0.006 * (1.0 + fbm(x * 2.0, z * 2.0, 1.0, 2, y1))

        for i in range(n):
            for j in range(n):
                pts = [(cuts[i], cuts[j]), (cuts[i + 1], cuts[j]), (cuts[i + 1], cuts[j + 1]), (cuts[i], cuts[j + 1])]
                q = [(x, top(x, z), z) for x, z in pts]
                m.poly(q, STONE, [stone(v[0], v[1] + 0.25, v[2], 1.0) for v in q], facing=(0, 1, 0))
        for i in range(n):
            for (ax, az), (bx, bz), out in (((cuts[i], -half), (cuts[i + 1], -half), (0, 0, -1)), ((cuts[i], half), (cuts[i + 1], half), (0, 0, 1)),
                                            ((-half, cuts[i]), (-half, cuts[i + 1]), (-1, 0, 0)), ((half, cuts[i]), (half, cuts[i + 1]), (1, 0, 0))):
                q = [(ax, y0, az), (bx, y0, bz), (bx, top(bx, bz), bz), (ax, top(ax, az), az)]
                m.poly(q, STONE, [stone(v[0], v[1], v[2], 0.85) for v in q], facing=out)

    step(0.9, -0.02, 0.22, 0.035)
    step(0.675, 0.2, 0.44, 0.04)
    step(0.45, 0.42, 0.66, 0.03)

    def ring(y, r, sides, turn=0.0, k=1.0, shift=(0.0, 0.0)):
        return [(shift[0] + math.cos(math.tau * (i + turn) / sides) * r, y, shift[1] + math.sin(math.tau * (i + turn) / sides) * r) for i in range(sides)]

    def band(a, b, k=1.0):
        n = len(a)
        for i in range(n):
            q = [a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]]
            mid = ((q[0][0] + q[1][0]) * 0.5, 0.0, (q[0][2] + q[1][2]) * 0.5)
            m.poly(q, STONE, [stone(v[0], v[1], v[2], k) for v in q], facing=(mid[0], (a[0][1] - b[0][1]) * 0.0 + (0.3 if b[0][1] > a[0][1] and abs(b[0][0]) < abs(a[0][0]) else 0.0), mid[2]))

    # The socket stone: square below, its corners cut away to eight sides above.
    sq = [(sx * 0.29, 0.64, sz * 0.29) for sx, sz in ((1, 1), (-1, 1), (-1, -1), (1, -1))]
    sq8 = []
    for i, (x, y, z) in enumerate(sq):
        nx, nz = sq[(i + 1) % 4][0], sq[(i + 1) % 4][2]
        sq8 += [(x, 0.92, z), ((x + nx) * 0.5, 0.92, (z + nz) * 0.5)]
    lo8 = []
    for i, (x, y, z) in enumerate(sq):
        nx, nz = sq[(i + 1) % 4][0], sq[(i + 1) % 4][2]
        lo8 += [(x, 0.64, z), ((x + nx) * 0.5, 0.64, (z + nz) * 0.5)]
    top8 = [(math.cos(math.pi / 4.0 * (i + 0.5)) * 0.235, 1.07, math.sin(math.pi / 4.0 * (i + 0.5)) * 0.235) for i in range(8)]
    # (sq8 starts at the +x+z corner and runs to the next corner; top8's first point sits between the first corner and the first mid.)
    top8 = [(math.cos(math.pi / 4.0 * i + math.pi / 4.0) * 0.2 * (1.0 if i % 2 == 0 else 1.08), 1.07, math.sin(math.pi / 4.0 * i + math.pi / 4.0) * 0.2 * (1.0 if i % 2 == 0 else 1.08)) for i in range(8)]
    band(lo8, sq8, 0.95)
    band(sq8, top8, 1.0)
    m.poly(top8, STONE, [stone(v[0], v[1], v[2]) for v in top8], facing=(0, 1, 0))
    # The shaft, a little off the plumb, and the collar under the head.
    lean = (0.035, -0.02)
    rings = [ring(1.05, 0.135, 8, 0.5), ring(1.3, 0.125, 8, 0.5, shift=(lean[0] * 0.1, lean[1] * 0.1)), ring(2.68, 0.09, 8, 0.5, shift=lean), ring(2.72, 0.13, 8, 0.5, shift=lean), ring(2.8, 0.13, 8, 0.5, shift=lean),
             ring(2.84, 0.09, 8, 0.5, shift=lean)]
    for a, b in zip(rings, rings[1:]):
        band(a, b, 1.0)
    # The head: a cross whose arms have weathered to stumps; the north arm broke off long ago.
    t = props.Placed(m, (lean[0], 2.82, lean[1]), 0.0, 1.36)
    outline = [(-0.07, 0.0), (0.07, 0.0), (0.075, 0.17), (0.1, 0.18), (0.115, 0.2), (0.11, 0.3), (0.09, 0.325), (0.07, 0.33), (0.06, 0.44), (0.035, 0.49), (-0.03, 0.5), (-0.06, 0.45),
               (-0.07, 0.33), (-0.19, 0.335), (-0.235, 0.31), (-0.245, 0.215), (-0.2, 0.18), (-0.075, 0.17)]
    props.slab(t, outline, "z", -0.062, 0.062, worn(1.0, 0.15), mat="stone_worn", edge_shade=0.82)
    # What is left of the figure that was carved on it: a boss worn smooth.
    for z, way in ((0.062, 1.0), (-0.062, -1.0)):
        c = worn(1.1)
        pts = [(math.cos(math.tau * i / 6) * 0.05, 0.255 + math.sin(math.tau * i / 6) * 0.07, z) for i in range(6)]
        for i in range(6):
            t.poly([pts[i], pts[(i + 1) % 6], (0.0, 0.255, z + way * 0.022)], "stone_worn", c, facing=(pts[i][0], pts[i][1] - 0.255, way * 0.5))


# ---------------------------------------------------------------- the charnel house

def bone_end(t, x, y, z, rx, ry, colour, sides=5, turn=0.0, proud=0.012, deep=0.024):
    """The end of a long bone in a stack, looking at +z: a knob that goes dark toward its edge, where the next bone shadows it."""
    apex = t.vert(x, y, z + proud, colour)
    dark = (colour[0] * 0.13, colour[1] * 0.12, colour[2] * 0.11, 1.0)
    ring = [t.vert(x + math.cos(turn + math.tau * i / sides) * rx, y + math.sin(turn + math.tau * i / sides) * ry, z - deep, dark) for i in range(sides)]
    for i in range(sides):
        t.face((apex, ring[i], ring[(i + 1) % sides]), PAINT)


def bone_ends(t, x0, x1, y0, y1, z, rng, sag=None, skip=None):
    """Courses of thigh-bone ends filling a stretch of a stack's face (looking at +z): knees, which are two knuckles, and the balls of hips."""
    y, row = y0 + 0.034, 0
    while y < y1 - 0.024:
        x = x0 + rng.uniform(0.0, 0.03) + (0.035 if row % 2 else 0.0)
        while True:
            knee = rng.random() < 0.18
            w = rng.uniform(0.088, 0.104) if knee else rng.uniform(0.064, 0.088)
            if x + w > x1:
                break
            cx = x + w * 0.5
            cy = y + rng.uniform(-0.007, 0.007) + (sag(cx, y) if sag else 0.0)
            x += w + rng.uniform(0.003, 0.012)
            if skip and skip(cx, cy):
                continue
            # Older and damper toward the floor; some gone brown, some green.
            k = rng.uniform(0.42, 1.0) * lerp(0.7, 1.0, smoothstep(0.0, 0.7, y))
            c = (BONE[0] * k, BONE[1] * k * rng.uniform(0.92, 1.02), BONE[2] * k * rng.uniform(0.75, 1.0), 1.0)
            zz = z + rng.uniform(-0.014, 0.012)
            if knee:
                for s in (-1.0, 1.0):
                    bone_end(t, cx + s * w * 0.235, cy + rng.uniform(-0.004, 0.004), zz, w * 0.27, 0.033, c, 4, rng.uniform(0.3, 1.2))
            else:
                bone_end(t, cx, cy, zz, w * 0.5, 0.035, c, 5, rng.uniform(0.0, 1.2), proud=0.016)
        y += 0.07
        row += 1


def charnel_bones(p):
    """The charnel house's stack, 6 m long against the wall: the ends of
    thigh bones in courses in a timber crib, a row of skulls set through
    it, another along its top. One stretch of the row has fallen in. A
    low bay framed in timber stands open in it: where the sexton kept his
    tools, and where the porter hides. Built looking at +z and turned to
    face -z."""
    hard = props.Placed(p.hard, (0.0, 0.0, 0.0), math.pi)
    soft = props.Placed(p.soft, (0.0, 0.0, 0.0), math.pi)
    rng = random.Random(77)
    front = 0.585
    bay = (-1.6, -0.4)
    row = (0.468, 0.645)    # the skull row's height in the stack
    fall = (1.2, 2.1)       # where it has fallen in

    # What is behind everything: dark.
    for x0, x1, y0, y1, z in ((-3.0, bay[0], 0.0, 1.0, front - 0.03), (bay[1], 3.0, 0.0, 1.0, front - 0.03), (bay[0], bay[1], 0.6, 1.0, front - 0.03)):
        hard.poly([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], DARK, BLACK, facing=(0, 0, 1))
    top = [(-3.0, 0.99, -0.6), (3.0, 0.99, -0.6), (3.0, 0.99, front - 0.02), (-3.0, 0.99, front - 0.02)]
    hard.poly(top, DARK, BLACK, facing=(0, 1, 0))
    # The stack's top: the last course laid along it, in front of the skulls.
    for z in (0.53, 0.455):
        x = -2.9 + rng.uniform(0.0, 0.2)
        while x < 2.5:
            length = rng.uniform(0.36, 0.46)
            r, k = rng.uniform(0.015, 0.019), rng.uniform(0.5, 0.95)
            zz = z + rng.uniform(-0.012, 0.012)
            c = (BONE[0] * k, BONE[1] * k, BONE[2] * k * 0.92, 1.0)
            soft.tube([(x, 1.0 + r, zz), (x + length * 0.5, 1.0 + r * 0.8, zz + rng.uniform(-0.008, 0.008)), (x + length, 1.0 + r, zz + rng.uniform(-0.015, 0.015))], [r * 1.5, r * 0.9, r * 1.6], 4, PAINT,
                      [(c[0] * 0.8, c[1] * 0.8, c[2] * 0.8, 1.0), c, (c[0] * 0.8, c[1] * 0.8, c[2] * 0.8, 1.0)], caps=True)
            x += length + rng.uniform(0.01, 0.05)

    # The crib: posts, a sill board along the foot, boarded ends.
    for x in (-2.955, bay[0] + 0.045, bay[1] - 0.045, 2.955):
        beam(hard, (x, 0.0, front - 0.03), (x + rng.uniform(-0.01, 0.01), 1.04, front - 0.03), 0.09, 0.09, tone(OAK_DARK, 0.1))
    for x0, x1 in ((-2.91, bay[0]), (bay[1], 2.91)):
        plank(hard, (x0, 0.0, front), (x1, 0.15, front + 0.026), tone(OAK_DARK, 0.1), along="x")
    for sx in (-1, 1):
        boards(hard, (min(sx * 2.975, sx * 3.0), 0.0, -0.6), (max(sx * 2.975, sx * 3.0), 1.0, front - 0.075), "z", "y", 5, OAK_DARK, gap=0.012, uneven=0.004, ragged=0.02)
    # The bay: a lintel, boarded sides and roof, black at its back.
    plank(hard, (bay[0], 0.55, front - 0.1), (bay[1], 0.645, front + 0.005), tone(OAK_DARK, 0.08), along="x")
    for x0, x1 in ((bay[0], bay[0] + 0.022), (bay[1] - 0.022, bay[1])):
        boards(hard, (x0, 0.0, -0.6), (x1, 0.55, front - 0.075), "z", "y", 3, (OAK_DARK[0] * 0.7, OAK_DARK[1] * 0.7, OAK_DARK[2] * 0.7), gap=0.006)
    boards(hard, (bay[0] + 0.022, 0.55, -0.6), (bay[1] - 0.022, 0.575, front - 0.1), "z", "x", 5, (OAK_DARK[0] * 0.6, OAK_DARK[1] * 0.6, OAK_DARK[2] * 0.6), gap=0.008, uneven=0.006)
    hard.poly([(bay[0], 0.0, -0.58), (bay[1], 0.0, -0.58), (bay[1], 0.56, -0.58), (bay[0], 0.56, -0.58)], DARK, BLACK, facing=(0, 0, 1))

    def in_fall(x):
        return fall[0] < x < fall[1]

    def sag(x, y):
        # Over the stretch that fell in, the courses above have come down after it.
        if y < row[1]:
            return 0.0
        return -0.085 * math.exp(-((x - (fall[0] + fall[1]) * 0.5) / 0.36) ** 2) * (1.0 - 0.5 * (y - row[1]) / (1.0 - row[1]))

    def skip(x, y):
        return in_fall(x) and row[1] - 0.02 < y < row[1] + 0.05 and abs(x - (fall[0] + fall[1]) * 0.5) < 0.33

    # The courses of bone ends: under the skull row and over it, either side of the bay; and over the bay.
    bone_ends(soft, bay[1] + 0.01, 2.905, 0.15, row[0], front, rng)
    bone_ends(soft, bay[1] + 0.01, 2.905, row[1], 1.0, front, rng, sag, skip)
    bone_ends(soft, -2.905, bay[0] - 0.01, 0.15, row[0], front, rng)
    bone_ends(soft, -2.905, bay[0] - 0.01, row[1], 1.0, front, rng)
    bone_ends(soft, bay[0] + 0.01, bay[1] - 0.01, 0.645, 1.0, front, rng)

    # The row of skulls through the stack.
    def skull_row(x0, x1):
        x = x0 + 0.085
        while x < x1 - 0.07:
            if in_fall(x):
                x += 0.17
                continue
            skull(p.soft, (-x, row[0] + rng.uniform(-0.004, 0.004), -(front - 0.092 + rng.uniform(-0.012, 0.008))), math.pi + rng.uniform(-0.14, 0.14), rng.uniform(0.96, 1.03), jaw=False, seed=x, face_only=True,
                  tilt=rng.uniform(-0.05, 0.05))
            x += rng.uniform(0.153, 0.166)

    skull_row(bay[1] + 0.02, fall[1])
    skull_row(-2.9, bay[0] - 0.02)
    bone_ends(soft, fall[1] + 0.01, 2.905, row[0] - 0.012, row[1] + 0.03, front, rng)
    # Where it fell in: a hole into the stack, two skulls gone back into it and lying as they landed, a bone come down across it.
    hard.poly([(fall[0], row[0], front - 0.3), (fall[1], row[0], front - 0.3), (fall[1], row[1] + 0.06, front - 0.3), (fall[0], row[1] + 0.06, front - 0.3)], DARK, BLACK, facing=(0, 0, 1))
    hard.poly([(fall[0], row[0] + 0.004, front - 0.3), (fall[1], row[0] + 0.004, front - 0.3), (fall[1], row[0] + 0.004, front - 0.03), (fall[0], row[0] + 0.004, front - 0.03)], PAINT, (0.01, 0.009, 0.007, 1.0), facing=(0, 1, 0))
    skull(p.soft, (-(fall[0] + 0.24), row[0] + 0.05, -(front - 0.17)), math.pi + 0.9, 1.0, jaw=False, seed=5.0, tilt=1.25, colour=(BONE[0] * 0.7, BONE[1] * 0.7, BONE[2] * 0.65))
    skull(p.soft, (-(fall[0] + 0.62), row[0] + 0.0, -(front - 0.2)), math.pi - 0.75, 0.97, jaw=False, seed=6.0, tilt=-0.2, colour=(BONE[0] * 0.6, BONE[1] * 0.6, BONE[2] * 0.55))
    long_bone(p.soft, (-(fall[0] + 0.3), row[1] + 0.03, -(front + 0.0)), (-(fall[0] + 0.66), row[0] + 0.05, -(front - 0.3)), r=0.015, k=0.8, sides=5, head=False, seed=3.0)

    # The row along the top: some gone, one turned to the wall.
    x, i = -2.84, 0
    while x < 2.88:
        there = fbm(x * 1.7, 0.0, 1.0, 2, 3.0) > 0.01
        if there:
            wrong = 11 == i
            jaw = i % 5 == 2
            skull(p.soft, (-x, 1.0 + (0.0 if jaw else rng.uniform(0.0, 0.006)), -(0.24 + rng.uniform(-0.03, 0.03))), (0.0 if wrong else math.pi) + rng.uniform(-0.28, 0.28), rng.uniform(0.93, 1.05), jaw=jaw,
                  seed=x + 9.0, back=wrong, tilt=rng.uniform(-0.05, 0.1))
            i += 1
        x += rng.uniform(0.185, 0.225)
    # Long bones laid along the top in front of them, and a few on the floor where they slid off.
    x = -2.9
    while x < 2.5:
        length = rng.uniform(0.36, 0.46)
        if rng.random() < 0.3:
            z = rng.uniform(0.42, 0.5)
            long_bone(p.soft, (-x, 1.035, -z), (-(x + length * 0.96), 1.03 + rng.uniform(0.0, 0.01), -(z + rng.uniform(-0.1, 0.1))), r=rng.uniform(0.013, 0.016), k=rng.uniform(0.6, 0.95), sides=4, head=False, seed=x)
        x += length + rng.uniform(0.02, 0.2)
    for x, z, a in ((1.1, 0.74, 0.3),):
        long_bone(p.soft, (-x, 0.022, -z), (-(x + 0.4 * math.cos(a)), 0.022, -(z + 0.4 * math.sin(a))), r=0.014, k=0.6, sides=5, head=True, seed=x)


# ---------------------------------------------------------------- the last night's proofs

SILVER = "silver_dull"
PALE_WOOD = (1.12, 1.05, 0.9)
ANTLER = (0.075, 0.06, 0.04)
HABIT = (0.011, 0.01, 0.011)
SKIN = (0.1, 0.085, 0.062)   # the book's binding: pale, not calf


def antler(m, at, side, height=0.36, broken=False, seed=0.0):
    """A stag's antler lashed to a mask's brow at `at`, branching up and out to `side` (-1 or 1)."""
    rng = random.Random(int(seed * 31.0) + 7)
    k = rng.uniform(0.8, 1.1)

    def pt(dx, dy, dz):
        return (at[0] + side * dx * height, at[1] + dy * height, at[2] + dz * height)

    def col(f):
        q = k * lerp(0.75, 1.5, f)
        return (ANTLER[0] * q, ANTLER[1] * q, ANTLER[2] * q, 1.0)

    beam_pts = [pt(0.0, -0.08, 0.0), pt(0.1, 0.22, 0.07), pt(0.26, 0.55, 0.09), pt(0.33, 0.82, 0.04), pt(0.24, 1.0, 0.0)]
    radii = [0.021, 0.018, 0.015, 0.011, 0.004]
    if broken:
        beam_pts, radii = beam_pts[:3], radii[:2] + [0.014]
    m.tube(beam_pts, radii, 5, PAINT, [col(i / 4.0) for i in range(len(beam_pts))], caps=True)
    tines = [(pt(0.05, 0.1, 0.04), pt(0.06, 0.3, 0.3), pt(0.1, 0.46, 0.36)), (pt(0.2, 0.42, 0.08), pt(0.46, 0.6, 0.14), pt(0.56, 0.78, 0.12))]
    if not broken:
        tines.append((pt(0.32, 0.78, 0.05), pt(0.5, 0.92, 0.06), pt(0.54, 1.04, 0.03)))
    for a, b, c in tines:
        m.tube([a, b, c], [0.012, 0.009, 0.003], 4, PAINT, [col(0.3), col(0.6), col(1.0)], caps=True)


def mask(p, x, top, z, long=0.36, wide=0.1, cracked=False, broken=0, seed=0.0, peg=(0.0, 0.0, 0.0)):
    """One of the cult's faces hanging on its peg: a long face adzed out of
    pale wood, two eye holes and no mouth, a stag's antlers lashed to its
    brow. It hangs by a thong, a little out of true."""
    hard, soft = p.hard, p.soft
    skew = 0.03 * math.sin(seed * 5.0)

    def at(u, v):
        s = u * 2.0 - 1.0
        # Its outline: broad at the brow, long in the cheek, a narrow chin.
        w = wide * (smoothstep(-0.12, 0.14, v) * lerp(1.0, 0.42, smoothstep(0.45, 1.0, v) ** 1.3)) * (1.0 - 0.5 * smoothstep(0.9, 1.0, v))
        swell = 0.045 * (1.0 - abs(s) ** 2.2) * (0.6 + 0.4 * math.sin(min(v * 1.25, 1.0) * math.pi))
        brow = 0.014 * math.exp(-((v - 0.22) / 0.05) ** 2)
        nose = 0.03 * math.exp(-(s / 0.2) ** 2) * smoothstep(0.2, 0.3, v) * (1.0 - smoothstep(0.58, 0.66, v)) * (0.5 + 0.5 * smoothstep(0.25, 0.6, v))
        hollow = -0.012 * math.exp(-((abs(s) - 0.5) / 0.22) ** 2 - ((v - 0.34) / 0.07) ** 2)
        return (x + s * w + skew * v, top - v * long, z + 0.012 + swell + brow + nose + hollow)

    def tint(u, v):
        q = 0.8 + 0.2 * fbm(u * 5.0 + seed, v * 7.0, 1.0, 2, seed) - 0.2 * smoothstep(0.75, 1.0, v)
        return rgba(PALE_WOOD, q)

    props.sheet(hard, at, 6, 9, WOOD, tint, uv=(0.14, 0.34), flip=True)
    # Its edge, the thickness of the wood.
    rim = [at(0.0, j / 9.0) for j in range(10)] + [at(i / 6.0, 1.0) for i in range(1, 7)] + [at(1.0, 1.0 - j / 9.0) for j in range(1, 10)] + [at(1.0 - i / 6.0, 0.0) for i in range(1, 6)]
    cx, cy = x + skew * 0.5, top - long * 0.45
    for i in range(len(rim)):
        a, b = rim[i], rim[(i + 1) % len(rim)]
        hard.poly([a, b, (b[0], b[1], z), (a[0], a[1], z)], WOOD, rgba(PALE_WOOD, 0.5), uvs=[(0.0, 0.0), (0.1, 0.0), (0.1, 0.02), (0.0, 0.02)], facing=((a[0] + b[0]) * 0.5 - cx, (a[1] + b[1]) * 0.5 - cy, 0.0))
    # The eye holes: cut slanting, not quite a pair.
    for s in (-1.0, 1.0):
        u0, v0 = 0.5 + s * 0.24, 0.335 + (0.012 if s > 0 else 0.0)
        hole = []
        for i in range(7):
            a = math.tau * i / 7
            q = at(u0 + math.cos(a) * 0.115, v0 + math.sin(a) * 0.036 + math.cos(a) * s * 0.012)
            hole.append((q[0], q[1], q[2] + 0.003))
        hard.poly(hole, DARK, BLACK, facing=(0, 0, 1))
    if cracked:
        # A crack down it from the brow.
        line = [(0.56, 0.0), (0.585, 0.1), (0.55, 0.2), (0.6, 0.31), (0.57, 0.43), (0.61, 0.52)]
        for (ua, va), (ub, vb) in zip(line, line[1:]):
            a, b = at(ua, va), at(ub, vb)
            wa, wb = 0.005 * (1.0 - va / 0.56), 0.005 * (1.0 - vb / 0.56)
            hard.poly([(a[0] - wa, a[1], a[2] + 0.004), (a[0] + wa, a[1], a[2] + 0.004), (b[0] + wb, b[1], b[2] + 0.004), (b[0] - wb, b[1], b[2] + 0.004)], DARK, BLACK, facing=(0, 0, 1))
    for s in (-1.0, 1.0):
        root = at(0.5 + s * 0.3, 0.07)
        antler(soft, (root[0], root[1], root[2] - 0.01), s, height=long * (1.0 if s > 0 else 0.92), broken=(broken == s), seed=seed + s)
        props.rope(soft, [(root[0] - 0.02, root[1] - 0.008, root[2] + 0.004), (root[0], root[1] - 0.012, root[2] + 0.014), (root[0] + 0.02, root[1] - 0.008, root[2] + 0.004)], r=0.005, colour=props.LEATHER, sides=4)
        # The thong it hangs by.
        hang = at(0.5 + s * 0.2, 0.0)
        props.rope(soft, [(hang[0], hang[1] - 0.01, z + 0.02), ((hang[0] + peg[0]) * 0.5, (hang[1] + peg[1]) * 0.5, z + 0.03), peg], r=0.003, colour=props.LEATHER, sides=3)


def cult_masks(p):
    """A peg board on a wall (its back at z = 0, hanging toward +z, 1.6 m
    long at 1.6 m): three of the cult's faces, and a black habit on the
    last peg. The middle face is cracked from the brow."""
    m = p.hard
    plank(m, (-0.8, 1.555, 0.0), (0.8, 1.665, 0.03), tone(OAK_DARK, 0.08), along="x")
    for x in (-0.72, 0.0, 0.72):
        props.nail(m, (x, 1.61, 0.03), (0, 0, 1), r=0.014)
    pegs = (-0.6, -0.2, 0.2, 0.6)
    for x in pegs:
        beam(m, (x, 1.6, 0.02), (x, 1.635, 0.13), 0.024, 0.024, tone(OAK, 0.1), taper=0.8)
    mask(p, pegs[0] + 0.01, 1.49, 0.03, long=0.37, wide=0.1, seed=1.0, peg=(pegs[0], 1.63, 0.1))
    mask(p, pegs[1], 1.46, 0.03, long=0.4, wide=0.094, cracked=True, seed=2.0, peg=(pegs[1], 1.63, 0.1))
    mask(p, pegs[2] - 0.01, 1.5, 0.03, long=0.35, wide=0.104, broken=1.0, seed=3.3, peg=(pegs[2], 1.63, 0.1))
    # The habit, hung by its hood: black wool, empty, the height of a man.
    x0 = pegs[3]

    def cloth(u, v):
        s = u * 2.0 - 1.0
        w = lerp(0.05, 0.2, smoothstep(0.0, 0.16, v)) + 0.05 * v
        fold = 0.028 * math.cos(s * 9.0 + 1.0) * smoothstep(0.1, 0.5, v) + 0.02 * fbm(s * 2.0, v * 3.0, 1.0, 2, 4.0)
        hem = 1.0 + 0.03 * math.sin(s * 5.0)
        return (x0 + s * w, 1.6 - v * 1.3 * hem, 0.035 + 0.085 * (1.0 - s * s) ** 0.5 * lerp(1.0, 0.75, v) + fold * (1.0 - abs(s) ** 3))

    def black(u, v):
        return rgba(HABIT, 0.8 + 0.5 * fbm(u * 6.0, v * 5.0, 1.0, 2, 2.0) + 0.5 * math.cos((u * 2.0 - 1.0) * 9.0 + 1.0) * 0.3)

    props.sheet(p.soft, cloth, 12, 10, props.CLOTH, black, both=True)
    # The hood, fallen forward as a bowed head falls; nothing in it.
    hood = [(x0, 1.64, 0.1), (x0, 1.6, 0.17), (x0, 1.5, 0.22), (x0, 1.4, 0.21), (x0, 1.33, 0.17)]
    p.soft.tube(hood, [0.03, 0.075, 0.105, 0.1, 0.07], 8, props.CLOTH, [rgba(HABIT, 1.1)] * 5, squash=(1.0, 0.8))
    p.hard.poly([(x0 + math.cos(math.tau * i / 8) * 0.062, 1.335 + math.sin(math.tau * i / 8) * 0.012, 0.17 + math.sin(math.tau * i / 8) * 0.05) for i in range(8)], DARK, BLACK, facing=(0, -1, 0.3))
    # The sleeves hang empty; the rope girdle is looped over the same peg.
    for s in (-1.0, 1.0):
        p.soft.tube([(x0 + s * 0.17, 1.4, 0.1), (x0 + s * 0.215, 1.15, 0.13), (x0 + s * 0.225, 0.86, 0.12)], [0.05, 0.062, 0.075], 6, props.CLOTH, [rgba(HABIT, 1.0), rgba(HABIT, 1.2), rgba(HABIT, 0.9)], squash=(0.8, 1.0))
        p.hard.poly([(x0 + s * 0.225 + math.cos(math.tau * i / 6) * 0.055, 0.858, 0.12 + math.sin(math.tau * i / 6) * 0.07) for i in range(6)], DARK, BLACK, facing=(0, -1, 0))
    props.rope(p.soft, [(x0 - 0.01, 1.63, 0.11), (x0 - 0.06, 1.4, 0.2), (x0 - 0.09, 1.0, 0.19), (x0 - 0.08, 0.7, 0.2)], r=0.009, colour=(0.09, 0.075, 0.05), sides=4)
    props.rope(p.soft, [(x0 + 0.01, 1.63, 0.11), (x0 + 0.04, 1.42, 0.21), (x0 + 0.03, 1.2, 0.2)], r=0.009, colour=(0.09, 0.075, 0.05), sides=4)


def hoof_sole(t, ts):
    """One hoof sole built along x (its toes at +x) through the placed meshes `t` (hard) and `ts` (smooth)."""
    horn = (0.24, 0.19, 0.15)
    top = 0.088
    # The board the boot stands on, cut to a sole.
    sole = [(-0.125, -0.03), (-0.13, 0.0), (-0.125, 0.03), (-0.04, 0.042), (0.06, 0.05), (0.105, 0.04), (0.12, 0.0), (0.105, -0.04), (0.06, -0.05), (-0.04, -0.042)]
    props.slab(t, sole, "y", top, top + 0.016, tone(PINE, 0.08), grain="p")
    # Under it the hoof, carved and stained dark: two toes spreading to the ground, the cleft between them, and a block for the heel.
    for s in (-1.0, 1.0):
        foot = [(-0.03, s * 0.004), (0.07, s * 0.004), (0.12, s * 0.013), (0.136, s * 0.03), (0.118, s * 0.05), (0.055, s * 0.06), (-0.03, s * 0.054)]
        head = [(-0.025 + (x + 0.03) * 0.66, s * 0.007 + (z - s * 0.004) * 0.74) for x, z in foot]
        n = len(foot)
        c = tone(horn, 0.1)
        for i in range(n):
            (xa, za), (xb, zb), (xc, zc), (xd, zd) = foot[i], foot[(i + 1) % n], head[(i + 1) % n], head[i]
            t.poly([(xa, 0.0, za), (xb, 0.0, zb), (xc, top, zc), (xd, top, zd)], WOOD, [rgba(c, 0.7), rgba(c, 0.7), c, c], uvs=[(xa, 0.0), (xb, 0.02), (xc, 0.1), (xd, 0.1)],
                   facing=((xa + xb) * 0.5 - 0.05, 0.25, (za + zb) * 0.5 - s * 0.03))
        t.poly([(x, 0.0, z) for x, z in foot], WOOD, rgba(horn, 0.45), uvs=[(x, z) for x, z in foot], facing=(0, -1, 0))
        # The ground has worn the stain off its edge.
        rim = [(0.05 + (x - 0.05) * 0.82, s * 0.03 + (z - s * 0.03) * 0.72) for x, z in foot]
        t.poly([(x, -0.0015, z) for x, z in rim], PAINT, (0.02, 0.016, 0.012, 1.0), facing=(0, -1, 0))
    plank(t, (-0.118, 0.0, -0.036), (-0.06, top, 0.036), tone(horn, 0.08), along="y")
    # The straps: one over the instep, one round the heel, and the long thong that ties them.
    for x, wide, high in ((0.04, 0.058, 0.07), (-0.075, 0.046, 0.08)):
        y = top + 0.012
        pts = [(x, y - 0.012, -wide), (x - 0.004, y + high * 0.75, -wide * 0.78), (x - 0.008, y + high, 0.0), (x - 0.004, y + high * 0.75, wide * 0.78), (x, y - 0.012, wide)]
        ts.tube(pts, [0.012] * 5, 4, PAINT, rgba(props.LEATHER, 1.3), squash=(1.0, 0.25))
        for z in (-wide, wide):
            props.nail(t, (x, y - 0.004, z * 1.0), (0, 0.2, z), r=0.006)
    ts.tube([(-0.08, top + 0.09, 0.0), (-0.12, top + 0.04, 0.03), (-0.17, 0.03, 0.05), (-0.24, 0.006, 0.02), (-0.29, 0.006, 0.07)], [0.004] * 5, 3, PAINT, rgba(props.LEATHER, 1.2))


def hoof_soles(p):
    """A pair of hoof soles: boards to strap under a boot, a cloven hoof
    carved under each. One stands; the other has been dropped on its side,
    so the hoof shows."""
    hoof_sole(props.Placed(p.hard, (0.09, 0.0, 0.01), -math.pi * 0.5 + 0.12), props.Placed(p.soft, (0.09, 0.0, 0.01), -math.pi * 0.5 + 0.12))
    hoof_sole(props.Placed(p.hard, (-0.1, 0.062, -0.01), -math.pi * 0.5 - 0.3, 1.0, -1.5), props.Placed(p.soft, (-0.1, 0.062, -0.01), -math.pi * 0.5 - 0.3, 1.0, -1.5))


def purse(p, at, yaw=0.0, tilt=0.0, colour=props.LEATHER, size=1.0, badge=False, seed=0.0, pouch=False):
    """A pilgrim's purse: a flat leather pouch for the belt, its flap down
    over the front (toward +z), two loops at its top. With `pouch`, a
    small bag drawn shut with a thong instead."""
    k = 0.85 + 0.5 * ((math.sin(seed * 12.9898) * 43758.5453) % 1.0)
    if pouch:
        t = props.Placed(p.soft, at, yaw, size, tilt)
        prof = ((0.0, 0.014), (0.008, 0.04), (0.03, 0.05), (0.052, 0.04), (0.066, 0.014), (0.072, 0.012))
        t.tube([(0.0, y, 0.0) for y, _r in prof], [r for _y, r in prof], 6, PAINT, [rgba(colour, k * q) for q in (0.7, 0.9, 1.0, 1.0, 0.7, 0.6)], caps=True, squash=(1.0, 0.7))
        # The neck gathered above the thong.
        for i in range(6):
            a0, a1 = math.tau * i / 6, math.tau * (i + 1) / 6
            r = 0.03 if i % 2 else 0.02
            pts = [(math.cos(a0) * 0.012, 0.072, math.sin(a0) * 0.009), (math.cos(a1) * 0.012, 0.072, math.sin(a1) * 0.009), (math.cos((a0 + a1) * 0.5) * r, 0.088 + (0.006 if i % 2 else 0.0), math.sin((a0 + a1) * 0.5) * r * 0.8)]
            t.poly(pts, PAINT, rgba(colour, k * 0.85), facing=(pts[2][0], 0.3, pts[2][2]))
            t.poly(pts, PAINT, rgba(colour, k * 0.4), facing=(-pts[2][0], -0.3, -pts[2][2]))
        t.tube([(0.014, 0.07, 0.0), (0.04, 0.05, 0.01), (0.052, 0.012, 0.02)], [0.0025] * 3, 3, PAINT, rgba((0.07, 0.055, 0.035)))
        return
    t = props.Placed(p.hard, at, yaw, size, tilt)
    body = [(-0.055, 0.1), (-0.06, 0.05), (-0.05, 0.018), (-0.028, 0.002), (0.0, -0.002), (0.028, 0.002), (0.05, 0.018), (0.06, 0.05), (0.055, 0.1)]
    props.slab(t, body, "z", -0.014, 0.014, rgba(colour, k), mat=PAINT, edge_shade=0.7)
    flap = [(-0.057, 0.102), (-0.058, 0.06), (-0.04, 0.042), (0.0, 0.034), (0.04, 0.042), (0.058, 0.06), (0.057, 0.102)]
    props.slab(t, flap, "z", 0.014, 0.02, rgba(colour, k * 0.72), mat=PAINT, edge_shade=0.6)
    for x in (-0.03, 0.03):
        t.box((x - 0.009, 0.1, -0.012), (x + 0.009, 0.125, -0.004), PAINT, rgba(colour, k * 0.8), faces="xXzZY")
    t.box((-0.006, 0.042, 0.02), (0.006, 0.054, 0.025), PAINT, rgba((0.05, 0.04, 0.025)), faces="xXyYZ")
    if badge:
        # A scallop shell in lead, stitched to the flap: Compostela.
        fan = [(0.0, 0.062, 0.0215)] + [(math.sin(a) * 0.021, 0.068 + math.cos(a) * 0.024, 0.0215) for a in (-1.15, -0.6, 0.0, 0.6, 1.15)]
        t.poly(fan, IRON, (0.55, 0.55, 0.55, 1.0), facing=(0, 0, 1))


def purse_chest(p):
    """An iron-bound chest 0.7 m long, its lid thrown back against the
    wall behind it, full to the brim with pilgrims' purses: every kind of
    leather, one with a scallop badge, one that has fallen out."""
    m = p.hard
    w, d, h, th = 0.35, 0.21, 0.36, 0.022
    oak = (OAK_DARK[0] * 0.9, OAK_DARK[1] * 0.9, OAK_DARK[2] * 0.9)
    boards(m, (-w, 0.03, -d), (w, h, -d + th), "x", "y", 2, oak)
    boards(m, (-w, 0.03, d - th), (w, h, d), "x", "y", 2, oak)
    for sx in (-1, 1):
        boards(m, (min(sx * w, sx * (w - th)), 0.03, -d + th), (max(sx * w, sx * (w - th)), h, d - th), "z", "y", 2, oak)
        # Feet: the end boards run down past the bottom.
        plank(m, (min(sx * w, sx * (w - 0.05)), 0.0, -d), (max(sx * w, sx * (w - 0.05)), 0.03, d), tone(oak, 0.08), along="z")
    m.poly([(-w + th, 0.25, -d + th), (w - th, 0.25, -d + th), (w - th, 0.25, d - th), (-w + th, 0.25, d - th)], DARK, BLACK, facing=(0, 1, 0))
    # Iron: bands round it, corner straps, the lock plate with its hasp hanging open.
    for x in (-0.24, 0.0, 0.24):
        props.strap(m, (x, 0.03, -d), (x, h, -d), (0, 0, -1), width=0.04, nails=3, colour=props.RUST_C if x else IRON_C)
        props.strap(m, (x, h, -d), (x, h, -d + th), (0, 1, 0), width=0.04, nails=0)
    for sx in (-1, 1):
        props.strap(m, (sx * w, 0.1, -d), (sx * w, 0.1, d), (sx, 0, 0), width=0.035, nails=3)
        props.strap(m, (sx * w, 0.29, -d), (sx * w, 0.29, d), (sx, 0, 0), width=0.035, nails=3, colour=props.RUST_C)
    props.strap(m, (0.0, 0.2, -d - 0.006), (0.0, 0.31, -d - 0.006), (0, 0, -1), width=0.085, nails=0)
    m.poly([(-0.006, 0.235, -d - 0.0125), (0.006, 0.235, -d - 0.0125), (0.004, 0.265, -d - 0.0125), (-0.004, 0.265, -d - 0.0125)], DARK, BLACK, facing=(0, 0, -1))
    # The lid, thrown back past upright on its hinges.
    lid = props.Placed(m, (0.0, h, d), 0.0, 1.0, 1.82)
    boards(lid, (-w - 0.008, 0.0, -2.0 * d - 0.01), (w + 0.008, 0.026, 0.0), "x", "z", 3, oak)
    for x in (-0.24, 0.0, 0.24):
        props.strap(lid, (x, 0.026, -2.0 * d - 0.01), (x, 0.026, 0.0), (0, 1, 0), width=0.04, nails=3)
        props.strap(lid, (x, 0.0, -2.0 * d - 0.01), (x, 0.0, -2.0 * d + 0.05), (0, -1, 0), width=0.04, nails=1)
    props.strap(lid, (0.0, 0.0, -2.0 * d - 0.012), (0.0, -0.09, -2.0 * d - 0.012), (0, 0, -1), width=0.03, nails=0)
    # The purses, thrown in as they were taken: every tanner's leather, flat pouches and drawn bags.
    leathers = (props.LEATHER, (0.03, 0.021, 0.014), (0.03, 0.027, 0.022), (0.04, 0.03, 0.02), (0.016, 0.012, 0.01), (0.034, 0.02, 0.013))
    rng = random.Random(5)
    i = 0
    for row, z in enumerate((-0.13, -0.045, 0.04, 0.125)):
        x = -0.27 + (0.05 if row % 2 else 0.0)
        while x < 0.29:
            i += 1
            pouch = i % 4 == 0
            y = 0.262 + rng.uniform(0.0, 0.03) + (0.022 if abs(z) < 0.1 else 0.0)
            if pouch:
                purse(p, (x, y, z), rng.uniform(0.0, math.tau), rng.uniform(-0.4, 0.4), leathers[i % len(leathers)], rng.uniform(0.9, 1.1), seed=i, pouch=True)
            else:
                # Flat ones lie on their backs or their faces, or stand on edge against the side.
                tilt = rng.choice((-1.4, -1.5, 1.45, -1.3, -0.5))
                purse(p, (x, y + 0.012 + (0.02 if abs(tilt) < 1.0 else 0.0), z + rng.uniform(-0.02, 0.02)), rng.uniform(0.0, math.tau), tilt, leathers[i % len(leathers)], rng.uniform(0.85, 1.1), badge=(i in (6, 13)), seed=i)
            x += rng.uniform(0.1, 0.125)
    # One hangs over the front where it caught; one lies where it dropped.
    purse(p, (0.16, 0.265, -d - 0.022), math.pi, 0.0, leathers[3], 1.0, seed=31.0)
    purse(p, (-0.2, 0.016, -d - 0.085), 2.6, -1.52, leathers[1], 1.05, badge=True, seed=32.0)


def relic_hand(p):
    """The saint's hand: a silver reliquary 0.3 m high, a right hand raised
    in blessing on a cuff and a foot, tarnished black in its creases. A
    window in its palm (toward +z) shows the relic, a small bone."""
    m, s = p.hard, p.soft

    def silver(k=1.0):
        # Cold and tarnished, so the lantern does not turn it to gold.
        q = k * random.uniform(0.92, 1.05)
        return (0.22 * q, 0.28 * q, 0.42 * q, 1.0)

    # The foot, six-sided, and the cuff with its two bands.
    prof = ((0.0, 0.072), (0.01, 0.072), (0.018, 0.058), (0.034, 0.04), (0.044, 0.04))
    m.tube([(0.0, y, 0.0) for y, _r in prof], [r for _y, r in prof], 6, SILVER, [silver(0.5), silver(0.9), silver(0.6), silver(0.9), silver(0.5)], caps=True)
    cuff = ((0.044, 0.041), (0.05, 0.046), (0.058, 0.046), (0.062, 0.04), (0.118, 0.036), (0.122, 0.042), (0.132, 0.042), (0.136, 0.034))
    s.tube([(0.0, y, 0.0) for y, _r in cuff], [r for _y, r in cuff], 10, SILVER, [silver(0.6), silver(1.0), silver(1.0), silver(0.5), silver(0.9), silver(1.0), silver(1.0), silver(0.45)], squash=(1.0, 0.72))
    # Stones on the lower band: dull glass, one gone from its setting.
    for i in range(6):
        a = math.tau * (i + 0.5) / 6
        if i == 1:
            continue
        q = (math.cos(a) * 0.046, 0.054, math.sin(a) * 0.046 * 0.72)
        props.nail(m, q, (math.cos(a), 0.0, math.sin(a)), r=0.006, proud=0.004, colour=((0.05, 0.012, 0.012, 1.0), (0.012, 0.03, 0.02, 1.0))[i % 2], mat=PAINT)
    # The hand: wrist and palm, two fingers raised, two folded, the thumb out.
    palm = ((0.136, 0.03), (0.15, 0.03), (0.175, 0.04), (0.215, 0.043), (0.238, 0.04), (0.244, 0.032))
    s.tube([(0.0, y, 0.0) for y, _r in palm], [r for _y, r in palm], 8, SILVER, [silver(0.5)] + [silver(0.95)] * 4 + [silver(0.6)], caps=True, squash=(1.0, 0.42))
    for x, length, bent in ((0.028, 0.068, False), (0.0095, 0.076, False), (-0.0095, 0.07, True), (-0.027, 0.054, True)):
        if bent:
            pts = [(x, 0.238, 0.0), (x, 0.238 + length * 0.42, 0.006), (x, 0.238 + length * 0.52, 0.03), (x, 0.238 + length * 0.2, 0.04)]
        else:
            pts = [(x, 0.238, 0.0), (x, 0.238 + length * 0.45, 0.002), (x * 1.04, 0.238 + length * 0.8, 0.004), (x * 1.06, 0.238 + length, 0.006)]
        s.tube(pts, [0.0095, 0.009, 0.0082, 0.006], 6, SILVER, [silver(0.6), silver(1.0), silver(0.75), silver(1.0)], caps=True)
    s.tube([(0.034, 0.165, 0.004), (0.052, 0.192, 0.012), (0.058, 0.222, 0.016), (0.056, 0.244, 0.018)], [0.012, 0.0105, 0.009, 0.0065], 6, SILVER, [silver(0.6), silver(1.0), silver(0.8), silver(1.0)], caps=True)
    # The window in the palm: a frame, the dark behind the glass, and the bone.
    z = 0.0175
    x0, x1, y0, y1 = -0.016, 0.016, 0.168, 0.218
    m.poly([(x0, y0, z - 0.002), (x1, y0, z - 0.002), (x1, y1, z - 0.002), (0.0, y1 + 0.01, z - 0.002), (x0, y1, z - 0.002)], DARK, BLACK, facing=(0, 0, 1))
    for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (0.0, y1 + 0.01)), ((0.0, y1 + 0.01), (x0, y1)), ((x0, y1), (x0, y0))):
        beam(m, (a[0], a[1], z), (b[0], b[1], z), 0.005, 0.004, silver(1.1), SILVER, up=(0, 0, 1), end_shade=1.0)
    bone = (0.085, 0.07, 0.045, 1.0)
    s.tube([(-0.004, 0.176, z - 0.001), (-0.003, 0.181, z + 0.001), (0.0, 0.192, z), (0.003, 0.203, z + 0.001), (0.004, 0.209, z - 0.001)], [0.0045, 0.006, 0.0036, 0.0055, 0.004], 5, PAINT, bone, caps=True)


def cult_book(p):
    """The cult's book, open on a stand. The model's origin is the top of
    the stand, where the book lies; the stand's feet are 0.8 m below it.
    He reads it from -z. Bound in pale skin; the stub of a torn-out page
    stands at its spine; the page it lies open at has ten candles in a
    ring."""
    m = p.hard
    floor = -0.8
    dark = (OAK_DARK[0] * 0.85, OAK_DARK[1] * 0.85, OAK_DARK[2] * 0.85)
    # The stand: a cross foot, a post braced four ways, a board for the book with a lip at the reader's edge.
    for a, b in (((-0.24, floor + 0.035, 0.0), (0.24, floor + 0.035, 0.0)), ((0.0, floor + 0.04, -0.2), (0.0, floor + 0.04, 0.2))):
        beam(m, a, b, 0.075, 0.07, tone(dark, 0.08))
    beam(m, (0.0, floor + 0.07, 0.0), (0.0, -0.03, 0.0), 0.075, 0.075, tone(dark, 0.08), ends="")
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        beam(m, (dx * 0.19, floor + 0.07, dz * 0.16), (dx * 0.035, floor + 0.3, dz * 0.035), 0.04, 0.04, tone(dark, 0.08), up=(dz, 0, dx))
    boards(m, (-0.24, -0.03, -0.18), (0.24, 0.0, 0.18), "x", "z", 2, dark, uneven=0.0)
    plank(m, (-0.24, -0.03, -0.195), (0.24, 0.012, -0.18), tone(dark, 0.08), along="x")
    for dx in (-1, 1):
        beam(m, (dx * 0.03, -0.14, 0.0), (dx * 0.17, -0.03, 0.0), 0.035, 0.035, tone(dark, 0.08), up=(0, 0, 1))
    # The book: its boards in pale skin, the two blocks of leaves rising from the gutter.
    for sx in (-1, 1):
        lo, hi = (min(sx * 0.008, sx * 0.212), 0.0, -0.155), (max(sx * 0.008, sx * 0.212), 0.009, 0.155)
        m.box(lo, hi, PAINT, rgba(SKIN, random.uniform(0.85, 1.0)), faces="xXzZY")
    m.box((-0.012, 0.0, -0.155), (0.012, 0.007, 0.155), PAINT, rgba(SKIN, 0.6), faces="zZY")
    for i in range(5):
        z = -0.155 + 0.31 * (i + 0.5) / 5
        m.box((-0.014, 0.0, z - 0.007), (0.014, 0.0095, z + 0.007), PAINT, rgba(SKIN, 0.75), faces="zZYxX")
    page_c = (props.PARCHMENT[0] * 1.15, props.PARCHMENT[1] * 1.15, props.PARCHMENT[2] * 1.05)
    surf = {}
    for sx, thick in ((-1.0, 0.036), (1.0, 0.02)):
        def leaf_at(u, v, sx=sx, thick=thick):
            # From the gutter out to the fore-edge: up over the swell of the leaves, then nearly level.
            rise = thick * (1.0 - (1.0 - min(u / 0.3, 1.0)) ** 2.2) - 0.004 * u
            return (sx * (0.004 + u * 0.196), 0.009 + rise + 0.002 * math.sin(v * 3.0 + sx), lerp(-0.146, 0.146, v))

        surf[sx] = leaf_at
        props.sheet(p.soft, leaf_at, 6, 2, PAINT, lambda u, v: rgba(page_c, 0.75 + 0.25 * smoothstep(0.0, 0.3, u) - 0.1 * abs(v - 0.5)), flip=(sx < 0))
        edge = sx * 0.2
        top = leaf_at(1.0, 0.5)[1]
        m.poly([(edge, 0.009, -0.146), (edge, 0.009, 0.146), (edge, top, 0.146), (edge, top, -0.146)], PAINT, rgba(page_c, 0.6), facing=(sx, 0, 0))
        for z, way in ((-0.146, -1), (0.146, 1)):
            pts = [leaf_at(i / 6.0, 0.0 if way < 0 else 1.0) for i in range(7)]
            m.poly([(pts[0][0], 0.009, z), (pts[-1][0], 0.009, z)] + [(q[0], q[1], z) for q in reversed(pts)], PAINT, rgba(page_c, 0.55), facing=(0, 0, way))
        # The writing: black letter in lines, a red initial.
        lines = 13
        for i in range(lines):
            v = 0.1 + 0.8 * (lines - 1 - i) / (lines - 1) if sx < 0 else 0.1 + 0.8 * i / (lines - 1)
            if sx > 0 and 3 <= i <= 9:
                continue
            u0, u1 = (0.2, random.uniform(0.74, 0.88)) if sx > 0 else (0.16, 0.86)
            if sx < 0:
                u0, u1 = 1.0 - random.uniform(0.78, 0.9) + 0.02, 0.84
            a, b = leaf_at(u0, v), leaf_at(u1, v)
            ink = (0.012, 0.01, 0.009, 1.0)
            m.poly([(a[0], a[1] + 0.0012, a[2] - 0.0035), (b[0], b[1] + 0.0012, b[2] - 0.0035), (b[0], b[1] + 0.0012, b[2] + 0.0035), (a[0], a[1] + 0.0012, a[2] + 0.0035)], PAINT, ink, facing=(0, 1, 0))
    # On the right-hand leaf, between the lines: ten candles drawn in a ring.
    at = surf[1.0]
    for i in range(10):
        a = math.tau * i / 10
        u, v = 0.54 + math.cos(a) * 0.2, 0.5 + math.sin(a) * 0.135
        q = at(u, v)
        m.poly([(q[0] - 0.0028, q[1] + 0.0012, q[2] - 0.008), (q[0] + 0.0028, q[1] + 0.0012, q[2] - 0.008), (q[0] + 0.0028, q[1] + 0.0012, q[2] + 0.004), (q[0] - 0.0028, q[1] + 0.0012, q[2] + 0.004)], PAINT,
               (0.012, 0.01, 0.009, 1.0), facing=(0, 1, 0))
        m.poly([(q[0] - 0.003, q[1] + 0.0012, q[2] + 0.006), (q[0] + 0.003, q[1] + 0.0012, q[2] + 0.006), (q[0], q[1] + 0.0012, q[2] + 0.013)], PAINT, (0.07, 0.016, 0.01, 1.0), facing=(0, 1, 0))
    q = surf[-1.0](0.82, 0.86)
    m.poly([(q[0] - 0.012, q[1] + 0.0012, q[2] - 0.014), (q[0] + 0.012, q[1] + 0.0012, q[2] - 0.014), (q[0] + 0.012, q[1] + 0.0012, q[2] + 0.014), (q[0] - 0.012, q[1] + 0.0012, q[2] + 0.014)], PAINT, (0.07, 0.016, 0.01, 1.0),
           facing=(0, 1, 0))
    # The stub of the leaf that was torn out: it stands in the gutter, ragged.
    stub = []
    for i in range(9):
        z = -0.14 + 0.28 * i / 8.0
        stub.append((0.012 + 0.012 * fbm(z * 30.0, 0.0, 1.0, 2, 3.0) + (0.03 if i % 3 == 1 else 0.016), 0.03 + 0.016 * fbm(z * 22.0, 1.0, 1.0, 2, 5.0) + 0.018, z))
    for a, b in zip(stub, stub[1:]):
        for way in (1, -1):
            m.poly([(0.003, 0.016, a[2]), (0.003, 0.016, b[2]), (b[0], b[1], b[2]), (a[0], a[1], a[2])], PAINT, rgba(props.PARCHMENT, 1.0 if way > 0 else 0.7), facing=(-0.4 * way, way, 0))


BUILDERS = {
    "charnel_bones": charnel_bones,
    "grave": grave, "grave_plain": grave_plain, "grave_sunk": grave_sunk, "grave_slab": grave_slab, "grave_stone": grave_stone, "grave_fresh": grave_fresh,
    "garden_bed": garden_bed, "garden_bed_cabbage": garden_bed_cabbage, "garden_bed_leeks": garden_bed_leeks, "garden_bed_beans": garden_bed_beans,
    "churchyard_cross": churchyard_cross,
    "item_stone": item_stone, "item_cup": item_cup, "item_bone": item_bone, "item_apple": item_apple, "item_bread": item_bread,
    "cult_masks": cult_masks, "hoof_soles": hoof_soles, "purse_chest": purse_chest, "relic_hand": relic_hand, "cult_book": cult_book,
}

if __name__ == "__main__":
    props.run(BUILDERS)
