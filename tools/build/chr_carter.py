"""Hamo, the carter who brings the porter in on night 0
(game/chapters/night0/dialogue/carter.talk):
a working man, weathered, gruff, in a hurry to be home before dark. A hood
of undyed wool with a shoulder cape, its face open; a russet tunic to the
knee, belted, a knife; grey hose bound with cloth from the ankle to the
calf; low shoes. A whip. Muted colours *(mine)*.

His body on his skeleton, with the clips he moves by: standing (idle, talk,
walk) and seated on the wagon's board behind its headboard, his feet on the
bed, driving (sit) (chr_carter.glb). The whip (Whip) is made up in his right
fist as he drives, and the reins (Reins) run from his fists there out to the
horse's collar; the game shows both only as he sits (PersonModel). His head in the hood
(chr_carter_head.glb). How the models are made: tools/build/people.py and
tools/build/rig.py.

Run: tools/build.sh chr_carter
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import people
import porter
import rig
from people import WHITE, grey, tube, box, bend, mirror, add, lerp3

SPEC = {
    "name": "carter",
    "seed": 52,
    "height": 0.98,
    "breadth": 1.06,
    "skin": (0.64, 0.5, 0.42),
    "hair": (0.27, 0.23, 0.19),
    "grey_hair": 0.45,
    "beard": 0.55,
    "beard_color": (0.3, 0.27, 0.23),
    "hairline": 0.228,
    "age_lines": 0.9,
    "flush": 0.85,
    "head": {"width": 1.02, "jaw": 1.06, "chin": 0.95, "nose": 1.15, "nose_width": 1.2, "cheek": 1.0, "brow": 1.2},
    # On the board, 0.25 m above the seat's origin; his feet on the bed, 6 cm
    # below it.
    "clips": {
        "sit": {"from": "Driving_Loop", "seat": 0.25, "ankle": (0.13, 0.02, -0.4), "knee": (0.0, 1.0, -0.5)},
    },
    "colors": {
        "garment": (0.34, 0.25, 0.18),
        "cloak": (0.36, 0.32, 0.26),
        "hose": (0.25, 0.24, 0.22),
        "hat": (0.36, 0.32, 0.26),
        "boots": (0.24, 0.18, 0.13),
        "leather": (0.28, 0.2, 0.14),
        "hands": (0.62, 0.47, 0.39),
        "linen": (0.55, 0.51, 0.44),
        "pack": (0.4, 0.35, 0.27),
        "under": (0.32, 0.29, 0.24),
        "wood": (0.38, 0.28, 0.19),
        "metal": (0.38, 0.36, 0.33),
    },
    "swatches": {
        "garment": {"folds": 0.35, "hem": 0.3, "wear": 0.4, "hem_color": (0.15, 0.12, 0.09)},
        "cloak": {"folds": 0.25, "blotch": 0.16, "wear": 0.3},
        "hose": {"hem": 0.35, "hem_color": (0.16, 0.13, 0.1)},
        "hat": {"folds": 0.3, "blotch": 0.16, "wear": 0.3},
        "boots": {"wear": 0.4, "hem": 0.5, "hem_color": (0.14, 0.11, 0.08)},
        "leather": {"wear": 0.5, "blotch": 0.15},
        "hands": {"blotch": 0.14, "weave": 0.04},
        "linen": {"folds": 0.2},
        "pack": {"folds": 0.2},
        "under": {"folds": 0.4, "hem": 0.3, "hem_color": (0.2, 0.17, 0.13)},
        "wood": {"stripes": 0.5},
        "metal": {"wear": 0.6},
    },
}
MAT = "chr_carter"


def tunic(m, rings, belt_y):
    k = SPEC["breadth"]
    cols = [grey(0.8), grey(0.9), WHITE, WHITE, grey(0.92), grey(0.85), WHITE, grey(0.95), grey(0.9), grey(0.35)][:len(rings)]
    cols[-1] = grey(0.35)
    tube(m, MAT, [(0.0, y, z) for y, z, _ in rings], [(r[0] * k, r[1] * k, r[2] * k) for _, _, r in rings], 10, "garment", cols)
    rx, rf = 0.158 * k, 0.112 * k
    z = [z for y, z, _ in rings if abs(y - belt_y) < 0.2][0]
    tube(m, MAT, [(0.0, belt_y + 0.018, z), (0.0, belt_y - 0.018, z)], [(rx + 0.008, rf + 0.008, 0.094 * k + 0.008)] * 2, 10, "leather",
         [WHITE, grey(0.8)])
    # A knife at his left hip.
    tube(m, MAT, [(-rx * 0.9, belt_y - 0.01, z - 0.04), (-rx * 0.95, belt_y - 0.2, z - 0.07)], [0.017, 0.011], 4, "leather",
         [WHITE, grey(0.7)], caps=(False, True))
    tube(m, MAT, [(-rx * 0.88, belt_y + 0.06, z - 0.03), (-rx * 0.9, belt_y - 0.01, z - 0.04)], [0.011, 0.012], 4, "wood",
         [WHITE, WHITE], caps=(True, False))


def cape(m, neck_y, z):
    """The hood's shoulder cape, round his neck and over his shoulders."""
    k = SPEC["breadth"]
    tube(m, MAT, [(0.0, neck_y + 0.05, z), (0.0, neck_y + 0.0, z + 0.004), (0.0, neck_y - 0.05, z + 0.01),
                  (0.0, neck_y - 0.16, z + 0.02), (0.0, neck_y - 0.145, z + 0.02)],
         [(0.072, 0.07, 0.074), (0.15 * k, 0.11, 0.115), (0.225 * k, 0.135, 0.14), (0.25 * k, 0.15, 0.155),
          (0.235 * k, 0.14, 0.145)], 12, "cloak", [grey(0.8), WHITE, WHITE, grey(0.85), grey(0.4)])


def whip(m, grip, up, length=1.15):
    """A carter's whip: a stock of ash, and a lash hanging from its tip."""
    g = people.Vector(grip)
    u = people.Vector(up).normalized()
    butt = g - u * 0.12
    tip = g + u * length
    tube(m, MAT, [tuple(butt), tuple(g), tuple(tip)], [0.014, 0.012, 0.005], 4, "wood", [grey(0.8), WHITE, WHITE],
         caps=(True, False))
    lash = [tuple(tip)]
    p = tip
    for i in range(5):
        p = p + people.Vector((0.03 - 0.01 * i, -0.13 + 0.01 * i, 0.06 - 0.02 * i))
        lash.append(tuple(p))
    tube(m, MAT, lash, [0.005, 0.005, 0.004, 0.004, 0.003, 0.002], 3, "leather", [WHITE] * 6)


def body():
    m = porter.Mesh("Body")
    kh = SPEC["height"]
    tunic(m, [(1.5 * kh, 0.012, (0.066, 0.064, 0.066)), (1.47 * kh, 0.012, (0.13, 0.088, 0.088)), (1.41 * kh, 0.012, (0.19, 0.105, 0.1)),
              (1.29 * kh, 0.012, (0.178, 0.115, 0.102)), (1.13 * kh, 0.012, (0.163, 0.116, 0.095)), (1.04 * kh, 0.012, (0.158, 0.112, 0.094)),
              (0.93 * kh, 0.012, (0.172, 0.118, 0.108)), (0.75 * kh, 0.012, (0.198, 0.13, 0.124)), (0.52 * kh, 0.012, (0.218, 0.14, 0.135)),
              (0.555 * kh, 0.012, (0.2, 0.126, 0.122))], 1.05 * kh)
    m.tag = "cloak"
    cape(m, 1.47 * kh, 0.012)
    m.tag = None
    b = m.build(smooth=True)
    arms = {-1: {}, 1: {"fist": True}}
    people.standing_limbs(SPEC, b, arms, {"boot_top": 0.05, "wraps": True})


def driving(spec, skeleton):
    """What he holds as he drives (the sit clip): the whip up in his right
    fist, leaning forward over the horse, bound to his hand; the reins from
    both fists to the horse's collar."""
    pose = rig.posed(skeleton, "sit")
    j = people.joints(SPEC)
    fists = {}
    for side, s in ((-1, "l"), (1, "r")):
        wrist, elbow = mirror(j["wrist"], side), mirror(j["elbow"], side)
        ahead = people.Vector(wrist) - people.Vector(elbow)
        fists[side] = rig.carry(pose, skeleton, "hand_" + s, tuple(people.Vector(wrist) + ahead.normalized() * 0.045))
    m = porter.Mesh("Whip")
    whip(m, fists[1], (0.25, 1.0, -0.45), 1.25)
    rig.bind(m.build(smooth=True), skeleton, "hand_r", pose)
    reins(skeleton, fists)


def reins(skeleton, fists):
    """From his fists (driving) out over the headboard to the rings on the
    horse's collar (prop_wagon.tscn: the horse 1.95 m ahead of the carter's
    seat). They hang from nothing that moves: bound to the root."""
    m = porter.Mesh("Reins")
    for side in (-1, 1):
        hand = fists[side]
        ring = (0.27 * side, 0.52, -2.72)
        pts = []
        for i in range(7):
            t = i / 6.0
            p = lerp3(hand, ring, t)
            pts.append((p[0], p[1] - 0.12 * math.sin(t * math.pi), p[2]))
        tube(m, MAT, pts, [0.006] * 7, 3, "leather", [grey(0.8)] * 7)
    rig.bind(m.build(smooth=True), skeleton, "root")


def hood(spec, head):
    """The hood over his head, the face open: a cowl a little off the head,
    its point falling behind."""
    m = porter.Mesh("Hood")
    rows = people.head_rows(spec)
    cols = 12
    heights = [-0.03, 0.04, 0.085, 0.13, 0.18, 0.225, 0.262, 0.295, 0.322]
    pts, uvs = [], []
    for i, h in enumerate(heights):
        ring = []
        for c in range(cols + 1):
            th = -math.pi + 2.0 * math.pi * c / cols
            x, _, z = people.head_point(rows, th, min(max(h, 0.0), 0.29))
            cz = 0.004
            d = math.hypot(x, z - cz)
            grow = 0.024 if h < 0.27 else 0.016
            if h < 0.06:
                grow = 0.03
            # Hanging loose at the jaw: wider at the sides there.
            if 0.06 < h < 0.16 and abs(th) > 1.0:
                grow += 0.012
            sc = (d + grow) / max(d, 1e-4)
            if h > 0.3:
                sc *= 0.62
            ring.append((x * sc, h, cz + (z - cz) * sc))
        pts.append(ring)

    def opening(i, c):
        th = -math.pi + 2.0 * math.pi * (c + 0.5) / cols
        mid = (heights[i] + heights[i + 1]) * 0.5
        return abs(th) < 1.0 and 0.06 < mid < 0.235

    for layer, shade, rev in ((0, 1.0, False), (1, 0.32, True)):
        ids = []
        for i, ring in enumerate(pts):
            row = []
            for c, p in enumerate(ring):
                q = p
                if layer:
                    q = (p[0] * 0.96, p[1], 0.004 + (p[2] - 0.004) * 0.96)
                col = grey(shade * (0.8 + 0.2 * i / len(pts)))
                row.append(m.vert(q[0], q[1], q[2], col, people.uv("hat", c / cols, 1.0 - i / (len(pts) - 1))))
            ids.append(row)
        for i in range(len(pts) - 1):
            for c in range(cols):
                if opening(i, c):
                    continue
                quad = (ids[i + 1][c], ids[i + 1][c + 1], ids[i][c + 1], ids[i][c])
                m.face(tuple(reversed(quad)) if rev else quad, MAT)
    # The point: up off the crown and back.
    tip = m.vert(0.0, 0.31, 0.15, grey(0.75), people.uv("hat", 0.5, 0.0))
    top = len(pts) - 1
    outer = [m.vert(p[0], p[1], p[2], grey(0.9), people.uv("hat", c / cols, 0.0)) for c, p in enumerate(pts[top])]
    for c in range(cols):
        m.face((outer[c + 1], outer[c], tip), MAT)
    m.build(smooth=True, parent=head)


if __name__ == "__main__":
    people.build(SPEC, lambda s: body(), hood, posed=driving, keep_apart=("Reins", "Whip"))
