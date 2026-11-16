"""Lambert, the warden at Aldgate on night 0 (game/chapters/night0/dialogue/warden.talk):
a gatekeeper, blunt and tired, solid; the city's man. A dark cloak over a
leather jerkin, thrown back off his right shoulder so the lantern arm is
free, its hood down round his neck; a dark felt cap; a short grizzled
beard; dark hose and boots to the calf. A tall staff in his left hand. His
lantern, horn panes in an iron frame, and his staff are models of their own
(chr_warden_lantern.glb, chr_warden_staff.glb, each with its origin where
his hand holds it): the scene puts them in his hands, and his arms follow
them wherever the ride lifts them (PersonModel). Muted colours *(mine)*.

His body on his skeleton, with the clips he moves by (idle, talk, walk:
chr_warden.glb), and his head in its cap (chr_warden_head.glb). How the
models are made: tools/build/people.py and tools/build/rig.py.

Run: tools/build.sh chr_warden
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import people
import porter
from people import WHITE, grey, tube, box, mirror, add

SPEC = {
    "name": "warden",
    "seed": 63,
    "height": 1.02,
    "breadth": 1.1,
    "skin": (0.63, 0.5, 0.43),
    "hair": (0.26, 0.23, 0.2),
    "grey_hair": 0.55,
    "beard": 0.9,
    "beard_volume": 1.0,
    "moustache": 1.0,
    "beard_top": 0.004,
    "beard_color": (0.3, 0.27, 0.24),
    "hairline": 0.236,
    "age_lines": 0.8,
    "flush": 0.6,
    "head": {"width": 1.05, "jaw": 1.1, "chin": 1.0, "nose": 1.1, "nose_width": 1.25, "cheek": 1.1, "brow": 1.5},
    "colors": {
        "garment": (0.2, 0.2, 0.22),
        "cloak": (0.16, 0.17, 0.19),
        "hose": (0.19, 0.18, 0.17),
        "hat": (0.15, 0.14, 0.14),
        "boots": (0.22, 0.16, 0.11),
        "leather": (0.31, 0.22, 0.15),
        "hands": (0.6, 0.47, 0.4),
        "linen": (0.55, 0.51, 0.44),
        "pack": (0.4, 0.35, 0.27),
        "under": (0.16, 0.17, 0.19),
        "wood": (0.33, 0.24, 0.16),
        "metal": (0.26, 0.25, 0.24),
    },
    "swatches": {
        "garment": {"folds": 0.25},
        "cloak": {"folds": 0.5, "hem": 0.25, "blotch": 0.14, "hem_color": (0.1, 0.09, 0.08)},
        "hose": {"hem": 0.3, "hem_color": (0.12, 0.1, 0.08)},
        "hat": {"blotch": 0.1, "weave": 0.03},
        "boots": {"wear": 0.5, "hem": 0.35, "hem_color": (0.12, 0.1, 0.08)},
        "leather": {"wear": 0.6, "blotch": 0.2},
        "hands": {"blotch": 0.12, "weave": 0.04},
        "linen": {"folds": 0.2},
        "pack": {},
        "under": {"folds": 0.4},
        "wood": {"stripes": 0.5},
        "metal": {"wear": 0.5, "blotch": 0.2},
    },
}
MAT = "chr_warden"
KH = SPEC["height"]
KW = SPEC["breadth"]
## From the lantern's middle up to where his hand holds its ring.
LANTERN_RING = 0.18
## Where his hand holds the staff, up from its foot.
STAFF_GRIP = 1.0 * KH


def body():
    m = porter.Mesh("Body")
    rings = [(1.52, (0.066, 0.064, 0.066), "garment"), (1.47, (0.13, 0.09, 0.09), "leather"), (1.41, (0.19, 0.108, 0.104), "leather"),
             (1.28, (0.182, 0.122, 0.106), "leather"), (1.12, (0.172, 0.128, 0.1), "leather"), (1.04, (0.168, 0.124, 0.1), "leather"),
             (0.93, (0.176, 0.122, 0.11), "leather"), (0.76, (0.19, 0.128, 0.12), "leather"), (0.79, (0.178, 0.118, 0.11), "leather")]
    # The jerkin: one tube, its collar the dark wool of his doublet.
    tube(m, MAT, [(0.0, y * KH, 0.012) for y, _, _ in rings], [(r[0] * KW, r[1] * KW, r[2] * KW) for _, r, _ in rings], 10, "leather",
         [grey(0.75), grey(0.9), WHITE, WHITE, grey(0.92), grey(0.85), WHITE, grey(0.9), grey(0.35)])
    tube(m, MAT, [(0.0, 1.53 * KH, 0.012), (0.0, 1.49 * KH, 0.012)], [(0.07, 0.068, 0.07), (0.1, 0.08, 0.08)], 10, "garment",
         [grey(0.85), WHITE])
    tube(m, MAT, [(0.0, 1.07 * KH, 0.012), (0.0, 1.03 * KH, 0.012)], [(0.176 * KW, 0.132 * KW, 0.106 * KW)] * 2, 10, "under",
         [grey(0.5), grey(0.4)])
    box(m, MAT, (0.0, 1.05 * KH, 0.012 - 0.132 * KW - 0.006), (0.045, 0.045, 0.012), "metal", grey(0.9))
    # A purse and a ring of keys at his belt: the gate's.
    box(m, MAT, (0.13 * KW, 0.97 * KH, -0.11), (0.07, 0.09, 0.03), "leather", grey(0.8), yaw=-0.6)
    tube(m, MAT, [(-0.15 * KW, 1.03 * KH, -0.08), (-0.17 * KW, 0.97 * KH, -0.1), (-0.15 * KW, 0.94 * KH, -0.115),
                  (-0.13 * KW, 0.97 * KH, -0.11), (-0.15 * KW, 1.03 * KH, -0.08)], [0.006] * 5, 3, "metal", [WHITE] * 5)
    # The cloak: off his right shoulder, open in front, to the calf.
    m.tag = "cloak"
    crings = [(1.53, 0.012, (0.08, 0.075, 0.08)), (1.48, 0.02, (0.18, 0.125, 0.13)), (1.41, 0.03, (0.25, 0.14, 0.16)),
              (1.1, 0.045, (0.27, 0.15, 0.19)), (0.75, 0.05, (0.3, 0.17, 0.22)), (0.34, 0.05, (0.32, 0.18, 0.24)),
              (0.37, 0.05, (0.305, 0.17, 0.228))]
    tube(m, MAT, [(0.0, y * KH, z) for y, z, _ in crings], [(r[0] * KW, r[1] * KW, r[2] * KW) for _, _, r in crings], 9, "cloak",
         [grey(0.8)] + [WHITE] * 5 + [grey(0.8)], arc=(2.0, 2.0 * math.pi - 1.25), inner=0.4)
    # Its hood, down, bunched behind his neck.
    path = []
    for i in range(7):
        a = 1.25 + (2.0 * math.pi - 2.5) * i / 6.0
        path.append((math.sin(a) * 0.12 * KW, (1.5 - 0.02 * math.cos(a)) * KH, 0.03 - math.cos(a) * 0.1))
    tube(m, MAT, path, [0.03, 0.045, 0.055, 0.06, 0.055, 0.045, 0.03], 6, "cloak", [grey(0.7), WHITE, WHITE, WHITE, WHITE, WHITE, grey(0.7)],
         caps=(True, True))
    b = m.build(smooth=True)
    arms = {-1: {"fist": True}, 1: {"fist": True}}
    people.standing_limbs(SPEC, b, arms, {"boot_top": 0.3})


def staff(spec):
    """His staff: a tall pole of ash. Origin where his hand holds it."""
    m = porter.Mesh("Staff")
    g = STAFF_GRIP
    tube(m, MAT, [(0.0, 0.02 - g, 0.02), (0.0, 0.0, 0.0), (-0.01, 2.05 * KH - g, -0.02)], [0.021, 0.019, 0.017], 5, "wood",
         [grey(0.7), WHITE, WHITE], caps=(True, True))
    m.build(smooth=True)


def lantern(spec):
    """His lantern: an iron frame, horn panes glowing, a cone of a top, a
    ring to hold it by. Origin at its middle (LANTERN_RING below his hand)."""
    m = porter.Mesh("Lantern")
    w, h = 0.062, 0.085
    for sx in (-1, 1):
        for sz in (-1, 1):
            box(m, MAT, (sx * w, 0.0, sz * w), (0.014, 2 * h, 0.014), "metal", grey(0.7))
    box(m, MAT, (0.0, -h - 0.008, 0.0), (2 * w + 0.03, 0.016, 2 * w + 0.03), "metal", grey(0.6))
    box(m, MAT, (0.0, h + 0.006, 0.0), (2 * w + 0.024, 0.012, 2 * w + 0.024), "metal", grey(0.8))
    top = (0.0, h + 0.075, 0.0)
    corners = [(-w - 0.012, h + 0.012, -w - 0.012), (w + 0.012, h + 0.012, -w - 0.012), (w + 0.012, h + 0.012, w + 0.012),
               (-w - 0.012, h + 0.012, w + 0.012)]
    for i in range(4):
        a, b = corners[i], corners[(i + 1) % 4]
        mid = ((a[0] + b[0]) / 2, 0.0, (a[2] + b[2]) / 2)
        m.poly([a, b, top], MAT, [grey(0.6), grey(0.6), WHITE], [people.uv("metal", 0, 1), people.uv("metal", 1, 1),
                                                                  people.uv("metal", 0.5, 0)], facing=(mid[0], 0.5, mid[2]))
    # The ring it is held by.
    ring = [(0.0, h + 0.075, 0.0)]
    for i in range(7):
        a = math.pi * i / 6.0
        ring.append((math.cos(a) * 0.03, h + 0.09 + math.sin(a) * 0.04, 0.0))
    tube(m, MAT, ring[1:], [0.005] * 7, 3, "metal", [WHITE] * 7)
    # The panes, horn scraped thin, lit from within.
    for nrm in ((0, 0, -1), (0, 0, 1), (-1, 0, 0), (1, 0, 0)):
        nx, nz = nrm[0], nrm[2]
        tx, tz = -nz, nx
        pts = [(nx * w + tx * s * w, y, nz * w + tz * s * w) for s, y in ((-1, -h), (1, -h), (1, h), (-1, h))]
        m.poly(pts, "chr_lantern_horn", [WHITE] * 4, [(0, 0), (1, 0), (1, 1), (0, 1)], facing=nrm)
    m.build(smooth=False)


def cap(spec, head):
    """A dark felt cap close on his head, its edge rolled."""
    m = porter.Mesh("Cap")
    rows = people.head_rows(spec)
    cols = 12
    rings = []
    for i, (h, grow) in enumerate(((0.214, 0.012), (0.25, 0.013), (0.282, 0.012), (0.302, 0.004))):
        ring = []
        for c in range(cols + 1):
            th = -math.pi + 2.0 * math.pi * c / cols
            # Down over the ears and the back of the head, up off the brow.
            hh = h - (0.03 * min(1.0, max(0.0, (abs(th) - 0.9) / 0.9)) if i == 0 else 0.0)
            x, _, z = people.head_point(rows, th, min(hh, 0.29))
            d = math.hypot(x, z - 0.004)
            sc = (d + grow) / max(d, 1e-4)
            if i == 3:
                sc *= 0.6
            ring.append(m.vert(x * sc, hh, 0.004 + (z - 0.004) * sc, grey(0.75 + 0.08 * i), people.uv("hat", c / cols, 0.7 - 0.2 * i)))
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for c in range(cols):
            m.face((r1[c], r1[c + 1], r0[c + 1], r0[c]), MAT)
    top = m.vert(0.0, 0.31, 0.006, WHITE, people.uv("hat", 0.5, 0.0))
    for c in range(cols):
        m.face((top, rings[-1][c + 1], rings[-1][c]), MAT)
    # The rolled edge.
    edge = []
    for c in range(cols + 1):
        th = -math.pi + 2.0 * math.pi * c / cols
        hh = 0.214 - 0.03 * min(1.0, max(0.0, (abs(th) - 0.9) / 0.9)) + 0.008
        x, _, z = people.head_point(rows, th, min(hh, 0.29))
        d = math.hypot(x, z - 0.004)
        sc = (d + 0.016) / d
        edge.append((x * sc, hh, 0.004 + (z - 0.004) * sc))
    tube(m, MAT, edge, [0.011] * len(edge), 4, "hat", [grey(0.85)] * len(edge))
    m.build(smooth=True, parent=head)


if __name__ == "__main__":
    people.build(SPEC, lambda s: body(), cap, [("chr_warden_lantern", lantern), ("chr_warden_staff", staff)])
