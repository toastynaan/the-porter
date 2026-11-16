"""Will Fuller, the traveller on the carter's wagon on night 0: a wool
merchant from Colchester, forty-one, lean and road-worn, "a merchant by his
good wet cloak" (game/chapters/night0/dialogue/traveller_road.talk). A tall
felt hat, its brim peaked in front and turned up behind; a belted gown to the
knee under a travelling cloak, hose, ankle boots, a purse; a pack on his
back with a blanket rolled on it. Muted colours *(mine)*.

His body on his skeleton, with the clips he moves by: standing (idle,
talk, walk) and seated on the wagon's bed, his back to the load, knees up
(sit: his forearms on his knees; sit_talk) (chr_traveller.glb); his head
(chr_traveller_head.glb). How the models are made: tools/build/people.py
and tools/build/rig.py.

Run: tools/build.sh chr_traveller
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import people
import porter
from people import WHITE, grey, tube, box, bend, mirror, add

SPEC = {
    "name": "traveller",
    "seed": 41,
    "height": 1.0,
    "breadth": 0.93,
    "skin": (0.66, 0.53, 0.46),
    "hair": (0.2, 0.15, 0.11),
    "grey_hair": 0.3,
    "beard": 0.36,
    "beard_color": (0.24, 0.19, 0.15),
    "hairline": 0.238,
    "age_lines": 0.5,
    "flush": 0.45,
    "head": {"width": 0.96, "jaw": 0.92, "chin": 1.05, "nose": 1.08, "nose_width": 0.95, "cheek": 1.2, "brow": 1.0},
    # On the wagon's bed: the seat's origin is 6 cm above its boards.
    "clips": {
        "sit": {"from": "Sitting_Idle_Loop", "seat": 0.0, "ankle": (0.12, 0.025, -0.37), "knee": (0.0, 1.0, -0.3),
                "wrist": (0.07, 0.37, -0.42), "elbow": (0.6, -0.4, 0.2)},
        "sit_talk": {"from": "Sitting_Talking_Loop", "seat": 0.0, "ankle": (0.12, 0.025, -0.37), "knee": (0.0, 1.0, -0.3)},
    },
    "colors": {
        "garment": (0.27, 0.29, 0.33),
        "cloak": (0.24, 0.25, 0.2),
        "hose": (0.23, 0.19, 0.16),
        "hat": (0.22, 0.18, 0.15),
        "boots": (0.28, 0.2, 0.14),
        "leather": (0.31, 0.22, 0.15),
        "hands": (0.66, 0.5, 0.41),
        "linen": (0.62, 0.58, 0.5),
        "pack": (0.4, 0.35, 0.27),
        "under": (0.33, 0.29, 0.25),
        "wood": (0.35, 0.26, 0.18),
        "metal": (0.4, 0.38, 0.35),
    },
    "swatches": {
        "garment": {"folds": 0.35, "hem": 0.22, "hem_color": (0.16, 0.14, 0.12)},
        "cloak": {"folds": 0.45, "hem": 0.3, "blotch": 0.16, "hem_color": (0.12, 0.11, 0.09)},
        "hose": {"hem": 0.3, "hem_color": (0.17, 0.14, 0.11)},
        "hat": {"blotch": 0.12, "weave": 0.03},
        "boots": {"wear": 0.4, "hem": 0.35, "hem_color": (0.15, 0.12, 0.09)},
        "leather": {"wear": 0.5, "blotch": 0.15},
        "hands": {"blotch": 0.1, "weave": 0.03},
        "linen": {"folds": 0.2},
        "pack": {"folds": 0.2, "wear": 0.3},
        "under": {"folds": 0.3},
        "wood": {"stripes": 0.4},
        "metal": {"wear": 0.6},
    },
}
MAT = "chr_traveller"


def gown(m, top=1.5, hem=0.56):
    """His gown from the collar to below the knee, belted; its hem turned in."""
    k = SPEC["breadth"]
    rings = [(top, (0.064, 0.062, 0.064)), (1.47, (0.13, 0.087, 0.087)), (1.41, (0.19, 0.1, 0.1)), (1.3, (0.172, 0.108, 0.1)),
             (1.15, (0.152, 0.1, 0.09)), (1.06, (0.146, 0.098, 0.088)), (0.95, (0.168, 0.11, 0.104)),
             (0.78, (0.198, 0.128, 0.124)), (hem, (0.222, 0.142, 0.138)), (hem + 0.035, (0.205, 0.128, 0.124))]
    cols = [grey(0.8), grey(0.9), WHITE, WHITE, grey(0.92), grey(0.85), WHITE, grey(0.95), grey(0.9), grey(0.35)]
    tube(m, MAT, [(0.0, y, 0.012) for y, _ in rings], [(r[0] * k, r[1] * k, r[2] * k) for _, r in rings], 10, "garment", cols)
    belt(m, 1.07, 0.15 * k, 0.1 * k, 0.09 * k)


def belt(m, y, rx, rf, rb):
    tube(m, MAT, [(0.0, y + 0.022, 0.012), (0.0, y - 0.022, 0.012)], [(rx + 0.007, rf + 0.007, rb + 0.007)] * 2, 10, "leather",
         [WHITE, grey(0.8)])
    box(m, MAT, (0.0, y, 0.012 - rf - 0.009), (0.04, 0.045, 0.012), "metal", grey(0.9))
    # The purse at his right hip, and a knife's sheath behind it.
    box(m, MAT, (rx * 0.8, y - 0.085, 0.012 - rf * 0.55), (0.075, 0.1, 0.035), "leather", grey(0.85), yaw=-0.5)
    tube(m, MAT, [(rx * 0.95, y - 0.02, 0.05), (rx * 0.97, y - 0.2, 0.06)], [0.016, 0.01], 4, "leather", [WHITE, grey(0.7)],
         caps=(False, True))


def cloak(m, rings, arc=(0.95, 2.0 * math.pi - 0.95)):
    """The travelling cloak, open in front, from the shoulders."""
    tube(m, MAT, [(0.0, y, z) for y, z, _ in rings], [r for _, _, r in rings], 9, "cloak",
         [grey(0.85)] + [WHITE] * (len(rings) - 2) + [grey(0.8)], arc=arc, inner=0.45)
    # A clasp at the throat.
    box(m, MAT, (0.0, rings[0][0] - 0.035, rings[0][1] - rings[0][2][1] - 0.004), (0.026, 0.016, 0.008), "metal", grey(0.5))


def pack(m, at, yaw=0.0, straps=True):
    """His pack: a canvas bag, flap down, a blanket rolled across its top."""
    x, y, z = at
    box(m, MAT, (x, y, z), (0.28, 0.33, 0.13), "pack", grey(0.8), top_shade=1.1, yaw=yaw)
    # The flap over its front (away from his back).
    box(m, MAT, (x + math.sin(yaw) * 0.078, y + 0.08, z + math.cos(yaw) * 0.078), (0.3, 0.14, 0.012), "leather", grey(0.85), yaw=yaw)
    c, s = math.cos(yaw), math.sin(yaw)
    tube(m, MAT, [(x - 0.19 * c, y + 0.23, z + 0.19 * s), (x + 0.19 * c, y + 0.23, z - 0.19 * s)], [0.055, 0.055], 6, "under",
         [grey(0.85), grey(0.85)], caps=(True, True))
    if straps:
        for sx in (-1, 1):
            tube(m, MAT, [(sx * 0.09, y + 0.15, z - 0.07), (sx * 0.12, 1.455, 0.06), (sx * 0.125, 1.43, -0.08),
                          (sx * 0.115, 1.3, -0.118), (sx * 0.13, 1.18, -0.105)], [0.012] * 5, 4, "leather",
                         [grey(0.8)] * 5)


def body():
    m = porter.Mesh("Body")
    gown(m)
    m.tag = "cloak"
    cloak(m, [(1.52, 0.012, (0.077, 0.072, 0.077)), (1.47, 0.02, (0.17, 0.12, 0.125)), (1.405, 0.03, (0.235, 0.13, 0.15)),
              (1.12, 0.04, (0.255, 0.13, 0.18)), (0.86, 0.04, (0.27, 0.13, 0.2)), (0.62, 0.04, (0.28, 0.13, 0.21)),
              (0.655, 0.04, (0.265, 0.12, 0.198))])
    m.tag = "bone:spine_03"
    pack(m, (0.0, 1.19, 0.29))
    m.tag = None
    b = m.build(smooth=True)
    arms = {side: {"cuff": "garment"} for side in (-1, 1)}
    people.standing_limbs(SPEC, b, arms, {"boot_top": 0.15})


def hat(spec, head):
    """A tall felt hat: a high crown tapering to a small top that leans a
    little back, its brim peaked over his brow and turned up behind (a
    bycocket) *(mine)*."""
    m = porter.Mesh("Hat")
    rows = people.head_rows(spec)
    base = 0.232
    cols = 12
    rings = []
    # The crown: (height, grow out from the head's line at the band).
    for i, (h, grow) in enumerate(((base, 0.012), (0.262, 0.012), (0.305, 0.0), (0.345, -0.02), (0.372, -0.036))):
        ring = []
        for c in range(cols + 1):
            th = -math.pi + 2.0 * math.pi * c / cols
            x, _, z = people.head_point(rows, th, min(h, 0.25))
            d = math.hypot(x, z - 0.004)
            sc = (d + grow) / max(d, 1e-4)
            # Its top leans a little back.
            lean = 0.016 * max(0.0, (h - 0.26) / 0.11)
            ring.append(m.vert(x * sc, h, 0.004 + lean + (z - 0.004) * sc, grey(0.72 + 0.06 * i),
                               people.uv("hat", c / cols, 0.9 - 0.2 * i)))
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for c in range(cols):
            m.face((r0[c], r1[c], r1[c + 1], r0[c + 1]), MAT)
    top = m.vert(0.0, 0.378, 0.02, WHITE, people.uv("hat", 0.5, 0.0))
    for c in range(cols):
        m.face((rings[-1][c], top, rings[-1][c + 1]), MAT)
    # The brim: peaked out over his brow, turned up against the crown behind.
    inner_top, outer_top, inner_bot, outer_bot = [], [], [], []
    for c in range(cols + 1):
        th = -math.pi + 2.0 * math.pi * c / cols
        x, _, z = people.head_point(rows, th, base)
        d = math.hypot(x, z - 0.004)
        ox, oz = x / d, (z - 0.004) / d
        x, z = x + ox * 0.012, z + oz * 0.012
        back = max(0.0, (abs(th) - 1.2) / (math.pi - 1.2))
        peak = max(0.0, 1.0 - abs(th) / 0.9)
        w = 0.034 + 0.024 * peak - 0.004 * back
        up = math.radians(-6.0 + 78.0 * back ** 0.8)
        ex, ez, ey = x + ox * w * math.cos(up), z + oz * w * math.cos(up), base + w * math.sin(up) - 0.004 * peak
        uvo = people.uv("hat", c / cols, 0.95)
        uvi = people.uv("hat", c / cols, 0.8)
        inner_top.append(m.vert(x, base + 0.004, z, grey(0.6), uvi))
        outer_top.append(m.vert(ex, ey + 0.004, ez, grey(0.95), uvo))
        inner_bot.append(m.vert(x, base - 0.004, z, grey(0.45), uvi))
        outer_bot.append(m.vert(ex + ox * 0.004, ey - 0.002, ez + oz * 0.004, grey(0.75), uvo))
    for c in range(cols):
        m.face((inner_top[c], inner_top[c + 1], outer_top[c + 1], outer_top[c]), MAT)
        m.face((inner_bot[c], outer_bot[c], outer_bot[c + 1], inner_bot[c + 1]), MAT)
        m.face((outer_top[c], outer_top[c + 1], outer_bot[c + 1], outer_bot[c]), MAT)
    m.build(smooth=True, parent=head)


if __name__ == "__main__":
    people.build(SPEC, lambda s: body(), hat)
