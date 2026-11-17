"""The people's kit: what every person in The Porter is put together from
(Look and Feel, "Characters": told apart by build, face, one prop, one
sound; docs/systems/assets.md, "The people's kit").

A character script (tools/build/chr_<name>.py) is a spec that picks from
the catalogues here, and one call:

    SPEC = {
        "name": "hob",
        "body": "big",                      # BODIES, or ("big", {"height": 1.0})
        "skin": "ruddy",                    # SKINS
        "face": "broad",                    # FACES, or ("broad", {"nose": 1.2})
        "brows": "heavy",                   # BROWS (each face has its own unless said)
        "eyes": "brown",                    # EYES
        "hair": ("brown", "balding"),       # HAIR colour, HAIR_STYLES
        "beard": "stubble",                 # BEARDS
        "age": 0.6,                         # 0 a youth to 1 very old: lines
        "wear": ["hose", ("shoes", {"color": "brown"}),
                 ("tunic", {"color": "russet", "belt": {"hung": ["purse"]}}),
                 ("apron", {})],            # WEAR, in any order
        "headwear": ["coif"],               # HEADWEAR
        "holds": {"r": "jug"},              # HELD: in a hand, and goes with it
        "props": [("staff", {"hand": "l"})],  # PROPS: models of their own; with a
                                            # hand, the scene puts it in that hand
    }
    people_kit.build(SPEC)

A colour is a name from CLOTH or (r, g, b) as on screen. Everything in a
catalogue can be overridden in the spec, and a spec may add its own parts
(build()'s `posed`: the carter's reins). The builders underneath are
tools/build/people.py (the head, tubes, limbs, the texture) and
tools/build/rig.py (the skeleton and clips). All of the catalogues'
contents are *(mine)*, for review: tools/shots/kit_shots.sh renders them.

Space: metres, +Y up, the figure faces -Z, his right is +X. Heights in
the parts are for a body of height 1.0 (1.75 m) and scale with his.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import people
import porter
import rig
from people import WHITE, Vector, box, grey, lerp3, mirror, swatch, tube

# ------------------------------------------------------------ catalogues

## Cloth, as dyed: muted, as the palette asks (only Walter wears "scarlet").
CLOTH = {
    "black": (0.118, 0.106, 0.098), "dark": (0.18, 0.18, 0.2), "grey": (0.3, 0.3, 0.29), "slate": (0.27, 0.29, 0.33),
    "undyed": (0.36, 0.32, 0.26), "tan": (0.42, 0.35, 0.26), "brown": (0.26, 0.2, 0.15), "russet": (0.34, 0.25, 0.18),
    "moss": (0.24, 0.25, 0.2), "woad": (0.2, 0.26, 0.36), "ochre": (0.47, 0.39, 0.21), "madder": (0.4, 0.17, 0.15),
    "scarlet": (0.54, 0.2, 0.17), "linen": (0.62, 0.58, 0.5), "white": (0.7, 0.67, 0.6), "straw": (0.56, 0.47, 0.28),
    "leather": (0.3, 0.21, 0.14), "wood": (0.35, 0.26, 0.18), "iron": (0.3, 0.29, 0.27), "tin": (0.4, 0.38, 0.35),
}

## Skin: the face, the hands (a little redder), the lips, and how flushed.
SKINS = {
    "pale": {"skin": (0.74, 0.64, 0.57), "hands": (0.72, 0.6, 0.52), "lip": (0.56, 0.38, 0.35), "flush": 0.3},
    "fair": {"skin": (0.68, 0.55, 0.47), "hands": (0.67, 0.52, 0.43), "lip": (0.53, 0.34, 0.3), "flush": 0.45},
    "ruddy": {"skin": (0.68, 0.49, 0.41), "hands": (0.66, 0.46, 0.38), "lip": (0.52, 0.3, 0.27), "flush": 0.95},
    "weathered": {"skin": (0.6, 0.46, 0.37), "hands": (0.58, 0.43, 0.34), "lip": (0.46, 0.29, 0.25), "flush": 0.7},
    "sallow": {"skin": (0.66, 0.58, 0.44), "hands": (0.64, 0.55, 0.41), "lip": (0.5, 0.36, 0.3), "flush": 0.15},
    "olive": {"skin": (0.56, 0.44, 0.32), "hands": (0.54, 0.41, 0.3), "lip": (0.44, 0.28, 0.24), "flush": 0.35},
    "brown": {"skin": (0.42, 0.3, 0.22), "hands": (0.4, 0.28, 0.2), "lip": (0.34, 0.2, 0.17), "flush": 0.25},
    "dark": {"skin": (0.28, 0.2, 0.15), "hands": (0.27, 0.19, 0.14), "lip": (0.25, 0.15, 0.13), "flush": 0.15},
    "ashen": {"skin": (0.56, 0.56, 0.54), "hands": (0.54, 0.54, 0.52), "lip": (0.42, 0.4, 0.42), "flush": 0.0},
}

HAIR = {
    "black": (0.09, 0.08, 0.075), "dark": (0.2, 0.15, 0.11), "brown": (0.3, 0.21, 0.14), "chestnut": (0.38, 0.22, 0.13),
    "red": (0.5, 0.25, 0.12), "fair": (0.55, 0.44, 0.27), "grey": (0.42, 0.4, 0.38), "white": (0.66, 0.64, 0.6),
}
## How the hair is cut (face.gdshader paints it, people.hair_bulk gives it
## its bulk; "long" adds a fall of hair behind).
HAIR_STYLES = ("cropped", "bowl", "tonsure", "balding", "bald", "long")
## Where the hair starts on the brow, by cut (height up the head, m).
HAIRLINE = {"cropped": 0.236, "bowl": 0.226, "tonsure": 0.234, "balding": 0.25, "bald": 0.24, "long": 0.234}

EYES = {
    "brown": (0.32, 0.25, 0.17), "dark": (0.2, 0.15, 0.11), "hazel": (0.38, 0.33, 0.2), "grey": (0.36, 0.4, 0.42),
    "blue": (0.3, 0.4, 0.5), "green": (0.3, 0.4, 0.28), "milky": (0.66, 0.66, 0.62),
}

## Builds, from the character table's words. height: of 1.75 m. frame: how
## broad his bones are. girth: belly and weight (below 0 gaunt, 1 fat).
## shoulders: their width on that frame. limb: how thick arms and legs are
## on it. stoop: degrees his back bends forward. sex: "f" narrows the
## shoulders and waist and widens the hips.
BODIES = {
    "average": {"height": 1.0, "frame": 1.0, "girth": 0.0, "shoulders": 1.0, "limb": 1.0, "stoop": 0.0, "sex": "m"},
    "lean": {"height": 1.02, "frame": 0.93, "girth": -0.3, "shoulders": 1.0, "limb": 0.94, "stoop": 0.0},
    "tall_thin": {"height": 1.08, "frame": 0.88, "girth": -0.5, "shoulders": 0.97, "limb": 0.88, "stoop": 14.0},
    "gangly": {"height": 1.05, "frame": 0.86, "girth": -0.5, "shoulders": 0.93, "limb": 0.8, "stoop": 5.0},
    "short_heavy": {"height": 0.91, "frame": 1.14, "girth": 1.0, "shoulders": 1.0, "limb": 1.15, "stoop": 0.0},
    "plump": {"height": 0.98, "frame": 1.04, "girth": 0.75, "shoulders": 0.97, "limb": 1.06, "stoop": 0.0},
    "big": {"height": 1.06, "frame": 1.2, "girth": 0.3, "shoulders": 1.08, "limb": 1.18, "stoop": 0.0},
    "small_frail": {"height": 0.9, "frame": 0.86, "girth": -0.4, "shoulders": 0.94, "limb": 0.82, "stoop": 12.0},
    "hunched": {"height": 0.96, "frame": 0.95, "girth": -0.1, "shoulders": 0.97, "limb": 0.92, "stoop": 34.0},
    "woman": {"height": 0.93, "frame": 0.9, "girth": 0.0, "shoulders": 1.0, "limb": 0.9, "stoop": 0.0, "sex": "f"},
    "woman_slight": {"height": 0.9, "frame": 0.84, "girth": -0.2, "shoulders": 1.0, "limb": 0.84, "stoop": 0.0, "sex": "f"},
    "woman_stout": {"height": 0.92, "frame": 0.98, "girth": 0.75, "shoulders": 1.0, "limb": 1.02, "stoop": 0.0, "sex": "f"},
}

## Faces: the head's shape (people.head_rows, head_mesh) and what is
## painted on it (people.face_look). Each number is a scale on the plain
## head's: width, jaw, chin, nose (how far it stands out), nose_width, cheek
## (how hollow under the cheekbone), brow (how heavy), jowl (0 none to 1 a
## fat face); socket (0 to 1: how deep the shadow under the brows, deep-set
## eyes), eye (the eyes' width and height), mouth (its width).
FACES = {
    "plain": {"width": 1.0, "jaw": 1.0, "chin": 1.0, "nose": 1.0, "nose_width": 1.0, "cheek": 1.0, "brow": 1.0, "jowl": 0.0,
              "socket": 0.5, "eye": (1.0, 1.0), "mouth": 1.0},
    "narrow": {"width": 0.9, "jaw": 0.86, "chin": 1.08, "nose": 1.1, "nose_width": 0.9, "cheek": 1.2, "eye": (0.95, 1.0),
               "mouth": 0.92},
    "gaunt": {"width": 0.93, "jaw": 0.84, "chin": 1.14, "nose": 1.18, "nose_width": 0.95, "cheek": 2.4, "brow": 1.5, "socket": 0.95,
              "mouth": 0.95},
    "sharp": {"width": 0.95, "jaw": 0.82, "chin": 1.22, "nose": 1.3, "nose_width": 0.8, "cheek": 1.5, "brow": 1.1,
              "eye": (0.95, 0.9), "mouth": 0.9},
    "soft": {"width": 0.99, "jaw": 0.95, "chin": 0.9, "nose": 0.82, "nose_width": 0.95, "cheek": 0.4, "brow": 0.4, "socket": 0.3,
             "eye": (1.12, 1.08)},
    "round": {"width": 1.1, "jaw": 1.2, "chin": 0.86, "nose": 0.9, "nose_width": 1.2, "cheek": 0.4, "brow": 0.7, "jowl": 1.0,
              "socket": 0.35, "eye": (1.05, 0.95), "mouth": 1.12},
    "broad": {"width": 1.08, "jaw": 1.12, "chin": 1.0, "nose": 1.08, "nose_width": 1.3, "cheek": 1.1, "brow": 1.5, "socket": 0.6,
              "mouth": 1.15},
    "square": {"width": 1.03, "jaw": 1.26, "chin": 1.1, "nose": 1.0, "nose_width": 1.05, "cheek": 1.0, "brow": 1.3, "socket": 0.6,
               "mouth": 1.05},
    "heavy": {"width": 1.07, "jaw": 1.28, "chin": 1.14, "nose": 1.15, "nose_width": 1.35, "cheek": 0.9, "brow": 2.2, "jowl": 0.4,
              "socket": 0.8, "eye": (1.0, 0.85), "mouth": 1.15},
    "hooked": {"width": 0.97, "jaw": 0.94, "chin": 1.0, "nose": 1.55, "nose_width": 1.1, "cheek": 1.3, "brow": 1.3, "socket": 0.65,
               "eye": (0.92, 0.95)},
}

## Brows (face.gdshader draws them): size (half length, half thickness,
## m), arch (how far the middle rises, in thicknesses), slant (radians at
## rest: + the inner ends up, a worried look; - down, a stern one), taper
## (how much they thin toward the temples), at (where: from the middle, up
## the head).
BROWS = {
    "plain": {"size": (0.019, 0.0034), "arch": 0.4, "slant": 0.0, "taper": 0.35, "at": (0.034, 0.2005)},
    "thin": {"size": (0.018, 0.0026), "arch": 0.9, "taper": 0.3},
    "arched": {"size": (0.0185, 0.0029), "arch": 2.2, "taper": 0.35, "at": (0.034, 0.201)},
    "straight": {"size": (0.0195, 0.0033), "arch": 0.0, "taper": 0.15},
    "heavy": {"size": (0.0205, 0.0046), "arch": 0.3, "slant": -0.06, "taper": 0.2, "at": (0.034, 0.2)},
    "bushy": {"size": (0.021, 0.0054), "arch": 0.6, "taper": 0.05, "at": (0.034, 0.2015)},
    "stern": {"size": (0.0195, 0.0038), "arch": 0.2, "slant": -0.2, "taper": 0.3},
    "worried": {"size": (0.0185, 0.0031), "arch": 0.5, "slant": 0.2, "taper": 0.35},
    "short": {"size": (0.013, 0.0037), "arch": 0.6, "taper": 0.1, "at": (0.031, 0.2005)},
    "joined": {"size": (0.0245, 0.0038), "arch": 0.4, "taper": 0.3, "at": (0.027, 0.2005)},
}
## The brows a face has unless its spec says ("brows").
FACE_BROWS = {"narrow": "thin", "gaunt": "straight", "sharp": "arched", "soft": "thin", "round": "short", "broad": "heavy",
              "square": "straight", "heavy": "bushy", "hooked": "stern"}

## Beards (face.gdshader paints them: below 0.6 stubble, in strokes; from
## 0.6 one dark shape; beard_volume builds the jaw out).
BEARDS = {
    "none": {"beard": 0.0},
    "stubble": {"beard": 0.36},
    "short": {"beard": 0.7, "beard_volume": 0.4, "moustache": 1.0},
    "full": {"beard": 0.92, "beard_volume": 1.0, "moustache": 1.0, "beard_top": 0.004},
}


def dye(c):
    """A colour by its name in CLOTH (or HAIR), or as given."""
    if isinstance(c, str):
        return CLOTH[c] if c in CLOTH else HAIR[c]
    return tuple(c)


def _pick(table, value):
    """A preset by name, by (name, overrides), or a dict of its own."""
    if isinstance(value, str):
        return dict(table[value])
    if isinstance(value, (tuple, list)):
        out = dict(table[value[0]])
        out.update(value[1])
        return out
    return dict(value or {})


def _entries(items):
    """["hose", ("tunic", {...})] as [(name, options)]."""
    return [(i, {}) if isinstance(i, str) else (i[0], dict(i[1])) for i in items or []]


def resolve(spec):
    """The spec with every name looked up: what people.py and rig.py read
    (height, breadth, limb, girth, stoop, shoulders_wide, hips_wide, head_scale; skin,
    hands_color, lip, flush; head; hair, hair_style, hairline, grey_hair;
    beard...; iris; age_lines, lines)."""
    s = dict(spec)
    body = dict(BODIES["average"])
    body.update(_pick(BODIES, spec.get("body", "average")))
    s["build"] = body
    s["height"] = body["height"]
    s["breadth"] = body["frame"]
    s["limb"] = body["frame"] * body["limb"]
    s["hand"] = 0.92 + 0.08 * body["frame"] * body["limb"]
    s.setdefault("head_scale", round(1.0 + (body["frame"] - 1.0) * 0.5, 3))
    s["girth"] = body["girth"]
    s["sex"] = body.get("sex", "m")
    s["stoop"] = body["stoop"]
    woman = s["sex"] == "f"
    s["shoulders_wide"] = body["frame"] * body["shoulders"] * (0.92 if woman else 1.0)
    s["hips_wide"] = (1.0 + (body["frame"] - 1.0) * 0.5) * (1.08 if woman else 1.0)
    skin = _pick(SKINS, spec.get("skin", "fair"))
    s["skin"] = skin["skin"]
    s["hands_color"] = skin.get("hands", skin["skin"])
    s["lip"] = spec.get("lip", skin.get("lip", (0.52, 0.33, 0.29)))
    s.setdefault("flush", skin.get("flush", 0.5))
    head = dict(FACES["plain"])
    head.update(_pick(FACES, spec.get("face", "plain")))
    head.update(spec.get("head", {}))
    s["head"] = head
    face = spec.get("face", "plain")
    face = face if isinstance(face, str) else face[0] if isinstance(face, (tuple, list)) else "plain"
    brows = dict(BROWS["plain"])
    brows.update(_pick(BROWS, spec.get("brows", FACE_BROWS.get(face, "plain"))))
    if spec.get("brow_size"):
        brows["size"] = spec["brow_size"]
    s["brows"] = brows
    hair = spec.get("hair", ("brown", "cropped"))
    hair = (hair, "cropped") if isinstance(hair, str) or len(hair) == 3 else hair
    # (A hair colour first: "dark" and "grey" are cloths too.)
    s["hair"] = HAIR[hair[0]] if isinstance(hair[0], str) and hair[0] in HAIR else dye(hair[0])
    s["hair_style"] = hair[1]
    s.setdefault("hairline", HAIRLINE[hair[1]])
    s["grey_hair"] = spec.get("grey", 0.0)
    for k, v in _pick(BEARDS, spec.get("beard", "none")).items():
        s[k] = v
    if "beard_color" not in spec:
        g = s["grey_hair"]
        s["beard_color"] = tuple(min(c * 1.15 + 0.02, 1.0) * (1.0 - 0.5 * g) + 0.3 * 0.5 * g for c in s["hair"])
    eyes = spec.get("eyes", "brown")
    s["iris"] = EYES[eyes] if isinstance(eyes, str) else tuple(eyes)
    age = spec.get("age", 0.4)
    s.setdefault("age_lines", age)
    s.setdefault("lines", round(0.25 + 0.7 * age, 3))
    return s


# ------------------------------------------------------------- the body

## The trunk at rest, for a frame of 1.0: height (of a body 1.0 tall), half
## width, depth in front, depth behind. A close garment's surface. The yoke
## carries the garment out from the neck to the shoulders, level with the
## top of the arms.
STATIONS = [
    ("collar", 1.50, 0.064, 0.062, 0.064),
    ("neck", 1.476, 0.096, 0.076, 0.08),
    ("yoke", 1.45, 0.166, 0.092, 0.096),
    ("shoulder", 1.40, 0.192, 0.102, 0.102),
    ("chest", 1.30, 0.172, 0.107, 0.1),
    ("ribs", 1.15, 0.152, 0.1, 0.09),
    ("waist", 1.06, 0.146, 0.098, 0.088),
    ("hip", 0.95, 0.167, 0.11, 0.104),
    ("seat", 0.84, 0.176, 0.114, 0.112),
]
SEAT = 0.84
## What a girth of 1.0 adds at each station: to the half width, front, back.
GIRTH = {"collar": (0.008, 0.008, 0.006), "neck": (0.01, 0.01, 0.008), "yoke": (0.008, 0.012, 0.012),
         "shoulder": (0.01, 0.016, 0.012),
         "chest": (0.022, 0.045, 0.018), "ribs": (0.048, 0.095, 0.026), "waist": (0.07, 0.135, 0.034),
         "hip": (0.06, 0.105, 0.04), "seat": (0.04, 0.05, 0.04)}
## A woman's trunk against a man's of the same frame: width, front depth.
WOMAN = {"neck": (0.95, 1.0), "yoke": (0.92, 1.0), "shoulder": (0.92, 1.0), "chest": (0.95, 1.2), "ribs": (0.92, 1.08), "waist": (0.88, 0.98),
         "hip": (1.07, 1.04), "seat": (1.08, 1.06)}


class Body:
    """His trunk: what garments are cut to. ring(y) is its half width and
    its depth in front and behind at a height (of a body 1.0 tall)."""

    def __init__(self, spec):
        b = spec["build"]
        self.h = b["height"]
        self.frame = b["frame"]
        self.girth = b["girth"]
        self.shoulders = b["shoulders"]
        self.woman = b.get("sex", "m") == "f"
        ## The trunk's middle, behind the feet's line.
        self.z = 0.012
        self.rings = []
        for name, y, rx, rf, rb in STATIONS:
            rx, rf, rb = rx * self.frame, rf * self.frame, rb * self.frame
            if name in ("yoke", "shoulder"):
                rx *= self.shoulders
            gx, gf, gb = GIRTH[name]
            g = self.girth if self.girth > 0.0 else self.girth * 0.22
            rx, rf, rb = rx + gx * g, rf + gf * g, rb + gb * g
            if self.woman and name in WOMAN:
                rx, rf = rx * WOMAN[name][0], rf * WOMAN[name][1]
            self.rings.append((y, (rx, rf, rb)))

    def ring(self, y, ease=0.0):
        rs = self.rings
        if y >= rs[0][0]:
            r = rs[0][1]
        elif y <= rs[-1][0]:
            r = rs[-1][1]
        else:
            for (y0, r0), (y1, r1) in zip(rs, rs[1:]):
                if y1 <= y <= y0:
                    t = (y0 - y) / (y0 - y1)
                    r = tuple(r0[i] + (r1[i] - r0[i]) * t for i in range(3))
                    break
        return (r[0] + ease, r[1] + ease, r[2] + ease)

    def at(self, y, ring, angle, out=0.0):
        """A point on a ring at `angle` round from the front (+ toward his right)."""
        c = math.cos(angle)
        return ((ring[0] + out) * math.sin(angle), y * self.h, self.z - ((ring[1] if c >= 0.0 else ring[2]) + out) * c)


class Kit:
    """One person being dressed: his body, the mesh of his trunk and what
    is on it, and what his limbs will be given."""

    def __init__(self, spec):
        self.spec = spec
        self.body = Body(spec)
        self.mat = "chr_" + spec["name"]
        self.m = porter.Mesh("Body")
        ## The outermost close garment at the waist: a belt goes over it.
        self.ease = 0.0
        self.flare = 0.0
        self.sleeve = None
        self.cuff = None
        self.wide = 1.0
        self.legs = {"hose": "hands", "boot": "hands", "boot_top": 0.03, "wraps": False}


def _shade(y):
    """A garment's vertex shade by height: darker at the collar, under the
    belt and toward the hem."""
    marks = [(1.5, 0.8), (1.476, 0.88), (1.45, 1.0), (1.4, 1.0), (1.3, 1.0), (1.15, 0.92), (1.06, 0.85), (0.95, 1.0), (0.5, 0.94), (0.0, 0.88)]
    for (y0, s0), (y1, s1) in zip(marks, marks[1:]):
        if y1 <= y <= y0:
            return s0 + (s1 - s0) * (y0 - y) / (y0 - y1)
    return marks[0][1] if y > 1.5 else marks[-1][1]


def robe(k, region, top=1.5, hem=0.56, ease=0.0, flare=0.13, sides=10, turn=True, arc=None, inner=None, tag=None):
    """A garment hung on the trunk from `top` to `hem`: it follows the body
    (with `ease` to spare) down to the seat, and below that hangs, flaring
    `flare` m wider for each metre it falls. `arc` makes it a panel (an
    apron, a scapular's front) instead of a tube all round."""
    b = k.body
    ys = [top] + [y for _, y, *_ in STATIONS if hem + 0.05 < y < top - 1e-6]
    y = min(ys[-1], SEAT)
    while y - 0.26 > hem + 0.06:
        y -= 0.26
        ys.append(y)
    ys.append(hem)
    rings, cols = [], []
    for y in ys:
        r = b.ring(max(y, SEAT), ease)
        drop = max(0.0, SEAT - y)
        rings.append((r[0] + flare * drop, r[1] + flare * 0.75 * drop, r[2] + flare * 0.75 * drop))
        cols.append(grey(_shade(y)))
    if turn and arc is None:
        # The hem turned in: what is seen up under it.
        last = rings[-1]
        ys.append(hem + 0.035)
        rings.append((last[0] * 0.93, last[1] * 0.92, last[2] * 0.92))
        cols.append(grey(0.35))
    k.m.tag = tag
    tube(k.m, k.mat, [(0.0, y * b.h, b.z) for y in ys], rings, sides, region, cols, arc=arc, inner=inner)
    k.m.tag = None


# ---------------------------------------------------------------- wear

def tunic(k, color="russet", hem=0.52, belt="leather", cloth="tunic", flare=0.13, ease=0.0, wide=1.0, cuff=False,
          collar_only=False, folds=0.35, mud=0.25, wear=0.3, patches=0.0, ragged=0):
    """A tunic to the thigh or the knee (hem 0.52), belted; longer, a gown
    (hem 0.56 and down). `collar_only`: only its collar and sleeves, for
    under a jerkin. `belt`: a cloth's name, None, or belt()'s keywords.
    `patches` (0 to 1) sews patches on it; `ragged`, that many tatters hang
    from its hem."""
    region = swatch(cloth, dye(color), folds=folds, hem=mud, wear=wear, hem_color=(0.15, 0.12, 0.09), patches=patches)
    if collar_only:
        robe(k, region, top=1.53, hem=1.47, ease=ease, flare=0.0, turn=False)
    else:
        robe(k, region, hem=hem, ease=ease, flare=flare)
        k.ease, k.flare = ease, flare
        if ragged:
            tatters(k, region, hem, ragged, ease=ease, flare=flare)
    k.sleeve, k.wide = region, wide
    k.cuff = region if cuff else None
    if not collar_only:
        _belted(k, belt)


def gown(k, color="slate", hem=0.56, **kw):
    """A gown to below the knee, with a cuff: a merchant's, a townsman's."""
    kw.setdefault("cuff", True)
    kw.setdefault("cloth", "gown")
    tunic(k, color=color, hem=hem, **kw)


def kirtle(k, color="brown", hem=0.05, belt=None, **kw):
    """A woman's kirtle: close to the body, falling full to the ground."""
    kw.setdefault("cloth", "kirtle")
    kw.setdefault("flare", 0.11)
    tunic(k, color=color, hem=hem, belt=belt, **kw)


def habit(k, color="black", hem=0.1, hood="down", scapular=True, belt=None):
    """The Benedictine's black habit: a full tunic to the ankle with wide
    sleeves, the scapular over it front and back, and the cowl: its hood
    down round the neck ("down"), or up (the headwear "cowl" and "up" here)."""
    tunic(k, color=color, hem=hem, belt=belt, cloth="habit", flare=0.1, ease=0.012, wide=1.75, folds=0.45, mud=0.12, wear=0.15)
    region = "habit"
    if scapular:
        for arc in ((-0.72, 0.72), (math.pi - 0.72, math.pi + 0.72)):
            robe(k, region, top=1.47, hem=0.3, ease=0.03, flare=0.1, arc=arc, inner=0.5, sides=4)
    if hood:
        cape(k, color=color, length=0.1, cloth=region)
    if hood == "down":
        hood_down(k, cloth=region)


def tatters(k, region, y, n, ease=0.0, flare=0.13, seed=3):
    """Torn strips hanging from a garment's edge at height `y`."""
    b = k.body
    rng = random.Random(seed + n)
    r = b.ring(max(y, SEAT), ease)
    drop = max(0.0, SEAT - y)
    r = (r[0] + flare * drop, r[1] + flare * 0.75 * drop, r[2] + flare * 0.75 * drop)
    for i in range(n):
        a = 2.0 * math.pi * (i + rng.uniform(-0.3, 0.3)) / n
        wide = rng.uniform(0.1, 0.2)
        long = rng.uniform(0.06, 0.16)
        p0, p1 = b.at(y, r, a - wide), b.at(y, r, a + wide)
        mid = b.at(y, r, a, 0.01)
        tip = (mid[0], mid[1] - long, mid[2])
        out = (math.sin(a), 0.0, -math.cos(a))
        uvs = [people.uv(region, 0.2, 0.9), people.uv(region, 0.5, 0.9), people.uv(region, 0.35, 1.0)]
        k.m.poly([p0, p1, tip], k.mat, [grey(0.8), grey(0.8), grey(0.6)], uvs, facing=out)
        k.m.poly([p0, p1, tip], k.mat, [grey(0.4), grey(0.4), grey(0.3)], uvs, facing=(-out[0], 0.0, -out[2]))


def rags(k, color="tan", hem=0.3):
    """Rags: a patched, torn tunic to the shin, a cord round it (Mab's)."""
    tunic(k, color=color, hem=hem, belt="rope", cloth="rags", wear=0.7, mud=0.45, patches=1.0, ragged=9)


def shawl(k, color="undyed", hem=1.02):
    """A ragged shawl over the shoulders, pulled close."""
    cloak(k, color=color, hem=hem, open=0.45, clasp=False, cloth="shawl")
    tatters(k, "shawl", hem, 7, ease=0.07, flare=0.0, seed=11)


def shoulder_cloth(k, color="linen", cloth="cloth"):
    """A cloth over the left shoulder (an alewife's, for the tables)."""
    b = k.body
    region = swatch(cloth, dye(color), folds=0.3, blotch=0.2, hem=0.3, hem_color=(0.36, 0.32, 0.26))
    x = -b.ring(1.45)[0] * 0.72
    front, back = b.ring(1.28, k.ease), b.ring(1.3, k.ease)
    path = [(x, 1.2 * b.h, b.z - front[1] - 0.012), (x, 1.36 * b.h, b.z - front[1] * 0.9 - 0.01), (x, 1.475 * b.h, b.z - 0.02),
            (x, 1.475 * b.h, b.z + 0.04), (x, 1.36 * b.h, b.z + back[2] * 0.95 + 0.01), (x, 1.26 * b.h, b.z + back[2] + 0.014)]
    k.m.tag = "bone:spine_03"
    tube(k.m, k.mat, path, [(0.05, 0.007, 0.007)] * len(path), 4, region, [grey(0.75), WHITE, WHITE, WHITE, grey(0.9), grey(0.75)],
         caps=(True, True))
    k.m.tag = None


def bundle(k, color="tan", cloth="bundle"):
    """A bundle on his left shoulder, roped (a sailor's sea bag)."""
    b = k.body
    region = swatch(cloth, dye(color), folds=0.3, wear=0.4)
    x = -b.ring(1.45)[0] * 0.8
    y = 1.53 * b.h
    k.m.tag = "bone:spine_03"
    tube(k.m, k.mat, [(x, y - 0.02, b.z - 0.2), (x, y, b.z - 0.08), (x, y, b.z + 0.14), (x, y - 0.03, b.z + 0.26)],
         [0.05, 0.075, 0.08, 0.055], 6, region, [grey(0.8), WHITE, WHITE, grey(0.8)], caps=(True, True))
    k.m.tag = None


def relic_box(k, color="wood"):
    """A box on a strap across the chest, at his right hip (the pardoner's relics)."""
    b = k.body
    wood = swatch("wood", CLOTH["wood"], stripes=0.4)
    leather = swatch("leather", CLOTH["leather"], wear=0.5, blotch=0.15)
    swatch("metal", CLOTH["tin"], wear=0.6)
    hip = b.ring(0.97, k.ease)
    at = b.at(0.97, hip, 1.0, 0.07)
    box(k.m, k.mat, at, (0.2, 0.13, 0.11), wood, grey(0.9), top_shade=1.15, yaw=-1.0)
    box(k.m, k.mat, (at[0], at[1] + 0.02, at[2]), (0.205, 0.02, 0.115), "metal", grey(0.7), yaw=-1.0)
    pts = []
    for i in range(7):
        a = 1.0 - (math.pi * 2.0 - 0.9) * i / 6.0
        y = 1.02 + (1.44 - 1.02) * math.sin(math.pi * i / 6.0)
        pts.append(b.at(y, b.ring(y, k.ease), a, 0.012))
    tube(k.m, k.mat, pts, [0.011] * 7, 4, leather, [grey(0.8)] * 7)


def jerkin(k, color="leather", hem=0.76, cloth="jerkin", belt="dark"):
    """A sleeveless jerkin of leather over the tunic, to the hip."""
    region = swatch(cloth, dye(color), wear=0.6, blotch=0.2)
    robe(k, region, top=1.47, hem=hem, ease=0.012, flare=0.05)
    k.ease = max(k.ease, 0.012)
    _belted(k, belt)


def apron(k, color="linen", top=1.06, hem=0.42, cloth="apron"):
    """An apron over the front, tied at the waist (top 1.06) or with a bib
    (top 1.3)."""
    region = swatch(cloth, dye(color), folds=0.2, blotch=0.16, hem=0.3, hem_color=(0.36, 0.32, 0.26))
    robe(k, region, top=top, hem=hem, ease=k.ease + 0.014, flare=k.flare, arc=(-1.05, 1.05), inner=0.6, sides=6)
    b = k.body
    r = b.ring(1.06, k.ease + 0.016)
    tube(k.m, k.mat, [(0.0, (1.06 + 0.012) * b.h, b.z), (0.0, (1.06 - 0.012) * b.h, b.z)], [r, r], 10, region, [WHITE, grey(0.8)])


def cloak(k, color="moss", hem=0.62, open=0.95, thrown=False, clasp=True, hood=False, cloth="cloak"):
    """A cloak from the shoulders, open in front by `open` radians each
    side; `thrown`, back off his right shoulder; `hood`, with its hood down
    behind his neck."""
    b = k.body
    region = swatch(cloth, dye(color), folds=0.45, hem=0.3, blotch=0.16, hem_color=(0.12, 0.11, 0.09))
    sh = b.ring(1.40)
    ys = [1.52, 1.462, 1.405, 1.12]
    y = 1.12
    while y - 0.36 > hem + 0.08:
        y -= 0.3
        ys.append(y)
    ys += [hem, hem + 0.035]
    rings, zs = [], []
    for i, y in enumerate(ys):
        body = b.ring(y)
        t = porter.smoothstep(1.405, hem, y)
        if i == 0:
            c = b.ring(1.5)
            r = (c[0] + 0.013, c[1] + 0.01, c[2] + 0.013)
        elif i == 1:
            yoke = b.ring(1.45)
            r = (yoke[0] + 0.014, yoke[1] + 0.03, yoke[2] + 0.034)
        else:
            r = (max(sh[0], body[0]) + 0.045 + 0.045 * t, max(sh[1], body[1]) + 0.03, max(sh[2], body[2]) + 0.05 + 0.06 * t)
        if i == len(ys) - 1:
            r = (r[0] * 0.95, r[1] * 0.93, r[2] * 0.95)
        rings.append(r)
        zs.append(b.z + (0.0 if i == 0 else 0.008 if i == 1 else 0.018 + 0.01 * t))
    arc = (2.0, 2.0 * math.pi - 1.25) if thrown else (open, 2.0 * math.pi - open)
    k.m.tag = "cloak"
    tube(k.m, k.mat, [(0.0, y * b.h, z) for y, z in zip(ys, zs)], rings, 9, region,
         [grey(0.85)] + [WHITE] * (len(ys) - 2) + [grey(0.8)], arc=arc, inner=0.45)
    if clasp:
        swatch("metal", CLOTH["tin"], wear=0.6)
        box(k.m, k.mat, (0.0, (ys[0] - 0.035) * b.h, zs[0] - rings[0][1] - 0.004), (0.026, 0.016, 0.008), "metal", grey(0.5))
    k.m.tag = None
    if hood:
        hood_down(k, cloth=region)


def cape(k, color="undyed", length=0.16, cloth="hood"):
    """The shoulder cape of a hood (the headwear "hood" is its other half)."""
    b = k.body
    region = swatch(cloth, dye(color), folds=0.3, blotch=0.16, wear=0.3)
    n, s = b.ring(1.45), b.ring(1.40)
    ys = [1.52, 1.47, 1.42, 1.47 - length, 1.47 - length + 0.015]
    rings = [(0.072, 0.07, 0.074), (n[0] - 0.006, n[1] + 0.024, n[2] + 0.028), (s[0] + 0.04, s[1] + 0.037, s[2] + 0.042),
             (s[0] + 0.064, s[1] + 0.052, s[2] + 0.057), (s[0] + 0.05, s[1] + 0.042, s[2] + 0.047)]
    k.m.tag = "cloak"
    tube(k.m, k.mat, [(0.0, y * b.h, b.z + 0.004 * i) for i, y in enumerate(ys)], rings, 12, region,
         [grey(0.8), WHITE, WHITE, grey(0.85), grey(0.4)])
    k.m.tag = None


def hood_down(k, cloth="cloak"):
    """A hood down, bunched behind the neck."""
    b = k.body
    path = []
    for i in range(7):
        a = 1.25 + (2.0 * math.pi - 2.5) * i / 6.0
        path.append((math.sin(a) * 0.12 * b.frame, (1.5 - 0.02 * math.cos(a)) * b.h, 0.03 - math.cos(a) * 0.1))
    k.m.tag = "bone:spine_03"
    tube(k.m, k.mat, path, [0.03, 0.045, 0.055, 0.06, 0.055, 0.045, 0.03], 6, cloth,
         [grey(0.7), WHITE, WHITE, WHITE, WHITE, WHITE, grey(0.7)], caps=(True, True))
    k.m.tag = None


def hose(k, color="grey", cloth="hose"):
    """Hose on his legs (with no hose, his legs are bare)."""
    k.legs["hose"] = swatch(cloth, dye(color), hem=0.3, hem_color=(0.17, 0.14, 0.11))


def boots(k, color="leather", top=0.15, cloth="boots"):
    """Boots: to the ankle (0.15), to the calf (0.3)."""
    k.legs["boot"] = swatch(cloth, dye(color), wear=0.4, hem=0.35, hem_color=(0.15, 0.12, 0.09))
    k.legs["boot_top"] = top


def shoes(k, color="leather", cloth="boots"):
    """Low shoes."""
    boots(k, color=color, top=0.05, cloth=cloth)


def wraps(k, color="undyed", cloth="wraps"):
    """Cloth bound round the shins, over the hose (a carter's, a labourer's)."""
    k.legs["wraps"] = swatch(cloth, dye(color), folds=0.4, hem=0.3, hem_color=(0.2, 0.17, 0.13))


def pack(k, color="tan", cloth="pack"):
    """A pack on his back: a canvas bag, flap down, a blanket rolled across
    its top, straps over his shoulders."""
    b = k.body
    region = swatch(cloth, dye(color), folds=0.2, wear=0.3)
    leather = swatch("leather", CLOTH["leather"], wear=0.5, blotch=0.15)
    roll = swatch("blanket", CLOTH["undyed"], folds=0.3)
    back = b.ring(1.2)[2]
    x, y, z = 0.0, 1.19 * b.h, b.z + back + 0.17
    m = k.m
    m.tag = "bone:spine_03"
    box(m, k.mat, (x, y, z), (0.28, 0.33, 0.13), region, grey(0.8), top_shade=1.1)
    box(m, k.mat, (x, y + 0.08, z + 0.078), (0.3, 0.14, 0.012), leather, grey(0.85))
    tube(m, k.mat, [(x - 0.19, y + 0.23, z), (x + 0.19, y + 0.23, z)], [0.055, 0.055], 6, roll, [grey(0.85), grey(0.85)],
         caps=(True, True))
    sh = b.ring(1.41)
    for sx in (-1, 1):
        tube(m, k.mat, [(sx * 0.09, y + 0.15, z - 0.07), (sx * 0.12, 1.455 * b.h, 0.06), (sx * 0.125, 1.43 * b.h, b.z - sh[1] + 0.008),
                        (sx * 0.115, 1.3 * b.h, b.z - b.ring(1.3)[1] - 0.012), (sx * 0.13, 1.18 * b.h, b.z - b.ring(1.18)[1] - 0.008)],
             [0.012] * 5, 4, leather, [grey(0.8)] * 5)
    m.tag = None


def scrip(k, color="tan", cloth="scrip"):
    """A pilgrim's scrip: a bag at his left hip on a strap across his chest."""
    b = k.body
    region = swatch(cloth, dye(color), folds=0.2, wear=0.4)
    leather = swatch("leather", CLOTH["leather"], wear=0.5, blotch=0.15)
    hip = b.ring(0.95, k.ease)
    at = b.at(0.93, hip, -1.25, 0.04)
    box(k.m, k.mat, at, (0.06, 0.2, 0.2), region, grey(0.85), top_shade=1.1)
    pts = []
    for i in range(7):
        a = -1.25 + (math.pi * 2.0 - 0.9) * i / 6.0
        y = 1.0 + (1.44 - 1.0) * math.sin(math.pi * i / 6.0)
        pts.append(b.at(y, b.ring(y, k.ease), a, 0.012))
    tube(k.m, k.mat, pts, [0.011] * 7, 4, leather, [grey(0.8)] * 7)


def _belted(k, belt):
    if belt is None:
        return
    opts = {"cloth": belt} if isinstance(belt, str) else dict(belt)
    waist_belt(k, **opts)


def waist_belt(k, y=1.06, cloth="leather", hung=(), buckle=True):
    """A belt at the waist, and what hangs from it (HUNG: purse, knife,
    keys, rosary, pouch). "rope": a knotted cord, its ends hanging."""
    b = k.body
    rope = cloth == "rope"
    if rope:
        region = swatch("rope", CLOTH["undyed"], weave=0.12)
    elif cloth == "leather":
        region = swatch("leather", CLOTH["leather"], wear=0.5, blotch=0.15)
    else:
        region = swatch("belt", dye(cloth), folds=0.2)
    r = b.ring(y, k.ease + (0.004 if rope else 0.007))
    half = 0.009 if rope else 0.022
    tube(k.m, k.mat, [(0.0, (y + half) * b.h, b.z), (0.0, (y - half) * b.h, b.z)], [r, r], 10, region, [WHITE, grey(0.8)])
    front = b.at(y, r, 0.0, 0.006)
    if rope:
        for dx in (-0.012, 0.014):
            tube(k.m, k.mat, [(front[0] + dx, front[1], front[2]), (front[0] + dx * 2.0, front[1] - 0.2, front[2] - 0.006)],
                 [0.008, 0.007], 3, region, [WHITE, grey(0.8)], caps=(False, True))
    elif buckle:
        swatch("metal", CLOTH["tin"], wear=0.6)
        box(k.m, k.mat, front, (0.04, 0.045, 0.012), "metal", grey(0.9))
    for name in hung:
        HUNG[name](k, y, r)


def _purse(k, y, r):
    """A purse at his right hip."""
    region = swatch("leather", CLOTH["leather"], wear=0.5, blotch=0.15)
    box(k.m, k.mat, tuple(c + d for c, d in zip(k.body.at(y, r, 0.75, 0.016), (0.0, -0.085, 0.0))), (0.075, 0.1, 0.035), region,
        grey(0.85), yaw=-0.6)


def _knife(k, y, r):
    """A knife in its sheath at his left hip."""
    region = swatch("leather", CLOTH["leather"], wear=0.5, blotch=0.15)
    wood = swatch("wood", CLOTH["wood"], stripes=0.4)
    a = k.body.at(y, r, -1.3, 0.014)
    tube(k.m, k.mat, [(a[0], a[1] - 0.01, a[2]), (a[0] * 1.04, a[1] - 0.2, a[2] - 0.02)], [0.017, 0.011], 4, region,
         [WHITE, grey(0.7)], caps=(False, True))
    tube(k.m, k.mat, [(a[0] * 0.98, a[1] + 0.06, a[2] + 0.008), (a[0], a[1] - 0.01, a[2])], [0.011, 0.012], 4, wood, [WHITE, WHITE],
         caps=(True, False))


def _keys(k, y, r):
    """A ring of keys at his left."""
    swatch("metal", CLOTH["tin"], wear=0.6)
    a = k.body.at(y, r, -0.7, 0.012)
    tube(k.m, k.mat, [(a[0], a[1] - 0.02, a[2]), (a[0] - 0.02, a[1] - 0.08, a[2] - 0.006), (a[0], a[1] - 0.11, a[2] - 0.01),
                      (a[0] + 0.02, a[1] - 0.08, a[2] - 0.006), (a[0], a[1] - 0.02, a[2])], [0.006] * 5, 3, "metal", [WHITE] * 5)
    for dx in (-0.012, 0.004, 0.016):
        box(k.m, k.mat, (a[0] + dx, a[1] - 0.15, a[2] - 0.012), (0.008, 0.07, 0.004), "metal", grey(0.8), yaw=dx * 20.0)


def _rosary(k, y, r):
    """A string of beads hanging at his right."""
    wood = swatch("wood", CLOTH["wood"], stripes=0.4)
    a = k.body.at(y, r, 1.15, 0.012)
    tube(k.m, k.mat, [(a[0], a[1], a[2]), (a[0] + 0.012, a[1] - 0.16, a[2] - 0.008), (a[0], a[1] - 0.3, a[2] - 0.012),
                      (a[0] - 0.012, a[1] - 0.16, a[2] - 0.004), (a[0], a[1], a[2])], [0.005] * 5, 3, wood, [WHITE] * 5)
    box(k.m, k.mat, (a[0], a[1] - 0.33, a[2] - 0.012), (0.024, 0.036, 0.006), wood, grey(0.9))


def _pouch(k, y, r):
    """A soft pouch at his left front (the infirmarian's herbs)."""
    region = swatch("pouch", CLOTH["tan"], folds=0.3, wear=0.3)
    a = k.body.at(y, r, -0.55, 0.02)
    tube(k.m, k.mat, [(a[0], a[1] - 0.01, a[2]), (a[0], a[1] - 0.05, a[2] - 0.004), (a[0], a[1] - 0.12, a[2] - 0.004)],
         [0.014, 0.036, 0.03], 5, region, [grey(0.8), WHITE, grey(0.85)], caps=(False, True))


HUNG = {"purse": _purse, "knife": _knife, "keys": _keys, "rosary": _rosary, "pouch": _pouch}
WEAR = {"tunic": tunic, "gown": gown, "kirtle": kirtle, "habit": habit, "jerkin": jerkin, "apron": apron, "cloak": cloak,
        "cape": cape, "hose": hose, "boots": boots, "shoes": shoes, "wraps": wraps, "belt": waist_belt, "pack": pack, "scrip": scrip,
        "rags": rags, "shawl": shawl, "shoulder_cloth": shoulder_cloth, "bundle": bundle, "relic_box": relic_box}


# ---------------------------------------------------------- in the hand
# Each is made where his hand hangs at rest (`grip`, the middle of his
# fist) and bound to that hand, so it goes where the hand goes.

def jug(k, m, grip, ahead):
    """An ale jug, carried by its handle."""
    region = swatch("pot", (0.4, 0.27, 0.19), blotch=0.2, wear=0.3)
    x, y, z = grip
    c = (x, y - 0.13, z - 0.03)
    tube(m, k.mat, [(c[0], c[1] - 0.1, c[2]), (c[0], c[1] - 0.06, c[2]), (c[0], c[1] + 0.02, c[2]), (c[0], c[1] + 0.08, c[2]),
                    (c[0], c[1] + 0.11, c[2])], [0.045, 0.066, 0.062, 0.034, 0.04], 6, region,
         [grey(0.7), WHITE, WHITE, grey(0.9), WHITE], caps=(True, True))
    tube(m, k.mat, [(c[0], c[1] + 0.09, c[2] + 0.03), (x, y, z + 0.02), (c[0], c[1] - 0.01, c[2] + 0.06)], [0.009] * 3, 3, region,
         [WHITE] * 3)


def cup(k, m, grip, ahead):
    """A wooden cup, in his fist."""
    wood = swatch("wood", CLOTH["wood"], stripes=0.4)
    x, y, z = grip
    tube(m, k.mat, [(x, y - 0.045, z - 0.01), (x, y + 0.05, z - 0.01)], [0.03, 0.038], 6, wood, [grey(0.8), WHITE], caps=(True, False))
    tube(m, k.mat, [(x, y + 0.05, z - 0.01), (x, y + 0.03, z - 0.01)], [0.036, 0.03], 6, wood, [grey(0.5), grey(0.25)], caps=(False, True))


def basket(k, m, grip, ahead, candles=False, color="straw"):
    """A basket hanging from the hand by its handle (`candles`: tapers in it)."""
    region = swatch("wicker", dye(color), weave=0.2, blotch=0.12, wear=0.2)
    x, y, z = grip
    c = (x, y - 0.27, z - 0.02)
    tube(m, k.mat, [(c[0], c[1] - 0.06, c[2]), (c[0], c[1] - 0.03, c[2]), (c[0], c[1] + 0.07, c[2])], [0.1, 0.125, 0.14], 7, region,
         [grey(0.7), WHITE, WHITE], caps=(True, False))
    tube(m, k.mat, [(c[0], c[1] + 0.07, c[2]), (c[0], c[1] + 0.03, c[2])], [0.135, 0.11], 7, region, [grey(0.55), grey(0.3)],
         caps=(False, True))
    tube(m, k.mat, [(c[0] - 0.135, c[1] + 0.07, c[2]), (c[0] - 0.09, y - 0.03, c[2]), (x, y + 0.005, z), (c[0] + 0.09, y - 0.03, c[2]),
                    (c[0] + 0.135, c[1] + 0.07, c[2])], [0.009] * 5, 3, region, [WHITE] * 5)
    if candles:
        wax = swatch("wax", (0.74, 0.69, 0.55), blotch=0.06)
        for dx, dz, lean in ((-0.06, 0.0, -0.03), (-0.02, 0.04, 0.0), (0.03, -0.03, 0.02), (0.07, 0.02, 0.04), (0.0, -0.05, -0.01)):
            tube(m, k.mat, [(c[0] + dx, c[1], c[2] + dz), (c[0] + dx + lean, c[1] + 0.2, c[2] + dz)], [0.009, 0.007], 3, wax,
                 [grey(0.8), WHITE], caps=(False, True))


def clapper(k, m, grip, ahead):
    """A leper's clapper: three wooden leaves on a handle."""
    wood = swatch("wood", CLOTH["wood"], stripes=0.4)
    x, y, z = grip
    tube(m, k.mat, [(x, y + 0.04, z + 0.02), (x, y - 0.03, z - 0.03)], [0.012, 0.012], 4, wood, [WHITE, WHITE], caps=(True, True))
    for dx in (-0.016, 0.0, 0.016):
        box(m, k.mat, (x + dx, y - 0.1, z - 0.1 - abs(dx) * 0.4), (0.011, 0.15, 0.06), wood, grey(0.9 - abs(dx) * 8.0), yaw=dx * 6.0)


def candles(k, m, grip, ahead):
    """A bundle of tapers, hung by their wicks from the hand."""
    wax = swatch("wax", (0.74, 0.69, 0.55), blotch=0.06)
    x, y, z = grip
    for dx, dz in ((-0.02, 0.0), (0.0, 0.016), (0.02, -0.004), (-0.008, -0.018), (0.012, 0.012)):
        tube(m, k.mat, [(x + dx * 0.3, y - 0.03, z + dz * 0.3), (x + dx, y - 0.34, z + dz)], [0.006, 0.009], 3, wax,
             [WHITE, grey(0.85)], caps=(False, True))


HELD = {"jug": jug, "cup": cup, "basket": basket, "clapper": clapper, "candles": candles}


# ------------------------------------------------------------ headwear

def _ring_pts(rows, h, grow, cols, scale=1.0, lean=0.0):
    """A ring round the head at height `h`, `grow(theta)` m out from the skin."""
    out = []
    for c in range(cols + 1):
        th = -math.pi + 2.0 * math.pi * c / cols
        x, _, z = people.head_point(rows, th, min(max(h, 0.0), 0.29))
        d = math.hypot(x, z - 0.004)
        sc = (d + (grow(th) if callable(grow) else grow)) / max(d, 1e-4) * scale
        out.append((x * sc, h, 0.004 + lean + (z - 0.004) * sc))
    return out


def _shell(spec, head, name, region, heights, grow, opening=None, cols=12, top=None, inner=0.32, crown=0.62, shade=(0.8, 1.0)):
    """A cloth over the head: rings at `heights`, `grow(h, theta)` out from
    the skin, left open where `opening(h, theta)` (the face); `top`, a point
    it closes to (None: left open above). Two-sided where it is open."""
    mat = "chr_" + spec["name"]
    m = porter.Mesh(name)
    rows = people.head_rows(spec)
    pts = [_ring_pts(rows, h, (lambda th, h=h: grow(h, th)), cols, crown if (top is not None and i == len(heights) - 1) else 1.0)
           for i, h in enumerate(heights)]
    n = len(heights)
    layers = ((0, 1.0, False),) if inner is None else ((0, 1.0, False), (1, inner, True))
    for layer, dim, rev in layers:
        ids = []
        for i, ring in enumerate(pts):
            row = []
            for c, p in enumerate(ring):
                q = (p[0] * 0.96, p[1], 0.004 + (p[2] - 0.004) * 0.96) if layer else p
                s = dim * (shade[0] + (shade[1] - shade[0]) * i / max(n - 1, 1))
                row.append(m.vert(q[0], q[1], q[2], grey(s), people.uv(region, c / cols, 1.0 - i / max(n - 1, 1))))
            ids.append(row)
        for i in range(n - 1):
            mid = (heights[i] + heights[i + 1]) * 0.5
            for c in range(cols):
                th = -math.pi + 2.0 * math.pi * (c + 0.5) / cols
                if opening and opening(mid, th):
                    continue
                quad = (ids[i + 1][c], ids[i + 1][c + 1], ids[i][c + 1], ids[i][c])
                m.face(tuple(reversed(quad)) if rev else quad, mat)
    if top is not None:
        tip = m.vert(top[0], top[1], top[2], grey(shade[1] * 0.9), people.uv(region, 0.5, 0.0))
        outer = [m.vert(p[0], p[1], p[2], grey(shade[1]), people.uv(region, c / cols, 0.0)) for c, p in enumerate(pts[-1])]
        for c in range(cols):
            m.face((outer[c + 1], outer[c], tip), mat)
    return m


def hood(spec, head, color="undyed", cloth="hood", deep=0.0, point=True):
    """A hood up over the head, the face open, its point falling behind
    (wear "cape" is its shoulder cape). `deep` (0 to 1) brings it forward
    round the face, as a cowl."""
    region = swatch(cloth, dye(color), folds=0.3, blotch=0.16, wear=0.3)

    def grow(h, th):
        g = 0.024 if h < 0.27 else 0.016
        if h < 0.06:
            g = 0.03
        if 0.06 < h < 0.16 and abs(th) > 1.0:
            g += 0.012
        # A cowl stands off the face all round its opening.
        return g + deep * 0.03 * max(0.0, 1.0 - abs(abs(th) - 1.0) / 0.9)

    half = 1.0 - 0.18 * deep
    m = _shell(spec, head, "Hood", region, [-0.03, 0.04, 0.085, 0.13, 0.18, 0.225, 0.262, 0.295, 0.322], grow,
               opening=lambda mid, th: abs(th) < half and 0.06 < mid < 0.235 + 0.012 * deep,
               top=(0.0, 0.31, 0.15 if point else 0.05))
    m.build(smooth=True, parent=head)


def cowl(spec, head, color="black", cloth="habit"):
    """The habit's hood up: deep, the face far back in it."""
    hood(spec, head, color=color, cloth=cloth, deep=1.0, point=False)


def coif(spec, head, color="linen", cloth="coif"):
    """A linen coif: close over the hair and ears, tied under the chin."""
    region = swatch(cloth, dye(color), folds=0.15, blotch=0.1)
    m = _shell(spec, head, "Coif", region, [0.1, 0.14, 0.185, 0.228, 0.262, 0.29, 0.304], lambda h, th: 0.01,
               opening=lambda mid, th: abs(th) < 1.12 and mid < 0.232, top=(0.0, 0.309, 0.006), inner=None, crown=0.5)
    rows = people.head_rows(spec)
    pts = []
    for th, h in ((-1.25, 0.11), (-0.8, 0.078), (0.0, 0.066), (0.8, 0.078), (1.25, 0.11)):
        x, _, z = people.head_point(rows, th, h)
        pts.append((x * 1.05, h, z * 1.05))
    tube(m, "chr_" + spec["name"], pts, [0.006] * 5, 3, region, [grey(0.85)] * 5)
    m.build(smooth=True, parent=head)


def kerchief(spec, head, color="linen", cloth="kerchief"):
    """A cloth over the hair, tied behind (a working woman's)."""
    region = swatch(cloth, dye(color), folds=0.3, blotch=0.12)
    m = _shell(spec, head, "Kerchief", region, [0.14, 0.185, 0.228, 0.262, 0.29, 0.304], lambda h, th: 0.011 + (0.012 if abs(th) > 2.2 else 0.0),
               opening=lambda mid, th: abs(th) < 1.2 and mid < 0.226, top=(0.0, 0.31, 0.01), inner=None, crown=0.5)
    # Its ends, knotted at the nape and hanging.
    tube(m, "chr_" + spec["name"], [(0.0, 0.155, 0.105), (0.0, 0.12, 0.125), (0.0, 0.03, 0.115)],
         [(0.03, 0.02, 0.02), (0.04, 0.016, 0.016), (0.03, 0.008, 0.008)], 5, region, [grey(0.75), grey(0.9), grey(0.8)], caps=(False, True))
    m.build(smooth=True, parent=head)


def wimple(spec, head, color="white", cloth="wimple"):
    """A wimple and veil: linen round the face, chin and neck, and a veil
    over it falling behind to the shoulders (a wife's, a widow's)."""
    region = swatch(cloth, dye(color), folds=0.25, blotch=0.08)
    m = _shell(spec, head, "Wimple", region, [-0.035, 0.03, 0.075, 0.1, 0.14, 0.185, 0.228, 0.262, 0.29, 0.304],
               lambda h, th: 0.008 if h > 0.03 else 0.014, opening=lambda mid, th: abs(th) < 0.86 and 0.088 < mid < 0.232,
               top=(0.0, 0.309, 0.006), inner=None, crown=0.5)
    m.build(smooth=True, parent=head)
    veil = _shell(spec, head, "Veil", region, [-0.09, -0.02, 0.07, 0.16, 0.24, 0.286, 0.31],
                  lambda h, th: 0.02 + 0.045 * max(0.0, (0.16 - h) / 0.25), opening=lambda mid, th: abs(th) < 1.25 and mid < 0.236,
                  top=(0.0, 0.318, 0.01), inner=0.5, crown=0.5, shade=(0.75, 1.0))
    veil.build(smooth=True, parent=head)


def wrap(spec, head, color="undyed", cloth="wrap"):
    """Cloth wound round the whole head and the face, open only at the eyes
    (Mab the leper's)."""
    region = swatch(cloth, dye(color), folds=0.4, blotch=0.2, wear=0.5, patches=0.4)
    # (It stands off the face over the nose.)
    nose = 0.023 * spec.get("head", {}).get("nose", 1.0)
    m = _shell(spec, head, "Wrap", region, [-0.035, 0.04, 0.085, 0.13, 0.15, 0.166, 0.2, 0.226, 0.262, 0.295, 0.31],
               lambda h, th: 0.012 + (0.01 if h < 0.14 and abs(th) > 0.8 else 0.0) + (0.006 if h < 0.05 else 0.0)
               + (nose * (1.0 if h > 0.14 else 0.4) if 0.12 < h < 0.17 and abs(th) < 0.3 else 0.0),
               opening=lambda mid, th: abs(th) < 0.82 and 0.166 < mid < 0.214, top=(0.0, 0.316, 0.01), inner=0.3, crown=0.55)
    m.build(smooth=True, parent=head)


def _crown(spec, m, region, rings, top, cols=12, lean_from=None):
    """A hat's crown: rings of (height, grow out from the head at the band)."""
    mat = "chr_" + spec["name"]
    rows = people.head_rows(spec)
    ids = []
    for i, (h, grow) in enumerate(rings):
        lean = 0.016 * max(0.0, (h - lean_from) / 0.11) if lean_from is not None else 0.0
        ring = []
        for c in range(cols + 1):
            th = -math.pi + 2.0 * math.pi * c / cols
            x, _, z = people.head_point(rows, th, min(h, 0.25))
            d = math.hypot(x, z - 0.004)
            sc = (d + grow) / max(d, 1e-4)
            ring.append(m.vert(x * sc, h, 0.004 + lean + (z - 0.004) * sc, grey(0.72 + 0.06 * i),
                               people.uv(region, c / cols, 0.9 - 0.8 * i / max(len(rings) - 1, 1))))
        ids.append(ring)
    for r0, r1 in zip(ids, ids[1:]):
        for c in range(cols):
            m.face((r0[c], r1[c], r1[c + 1], r0[c + 1]), mat)
    tip = m.vert(top[0], top[1], top[2], WHITE, people.uv(region, 0.5, 0.0))
    for c in range(cols):
        m.face((ids[-1][c], tip, ids[-1][c + 1]), mat)


def _brim(spec, m, region, base, width, up, cols=12, drop=None):
    """A hat's brim: `width(theta)` m out from the band at height `base`,
    turned up `up(theta)` radians."""
    mat = "chr_" + spec["name"]
    rows = people.head_rows(spec)
    inner_top, outer_top, inner_bot, outer_bot = [], [], [], []
    for c in range(cols + 1):
        th = -math.pi + 2.0 * math.pi * c / cols
        x, _, z = people.head_point(rows, th, base)
        d = math.hypot(x, z - 0.004)
        ox, oz = x / d, (z - 0.004) / d
        x, z = x + ox * 0.012, z + oz * 0.012
        w, a = width(th), up(th)
        ex, ez = x + ox * w * math.cos(a), z + oz * w * math.cos(a)
        ey = base + w * math.sin(a) - (drop(th) if drop else 0.0)
        uvo, uvi = people.uv(region, c / cols, 0.95), people.uv(region, c / cols, 0.8)
        inner_top.append(m.vert(x, base + 0.004, z, grey(0.6), uvi))
        outer_top.append(m.vert(ex, ey + 0.004, ez, grey(0.95), uvo))
        inner_bot.append(m.vert(x, base - 0.004, z, grey(0.45), uvi))
        outer_bot.append(m.vert(ex + ox * 0.004, ey - 0.002, ez + oz * 0.004, grey(0.75), uvo))
    for c in range(cols):
        m.face((inner_top[c], inner_top[c + 1], outer_top[c + 1], outer_top[c]), mat)
        m.face((inner_bot[c], outer_bot[c], outer_bot[c + 1], inner_bot[c + 1]), mat)
        m.face((outer_top[c], outer_top[c + 1], outer_bot[c + 1], outer_bot[c]), mat)


def bycocket(spec, head, color="brown", cloth="hat"):
    """A tall felt hat: a high crown tapering to a small top that leans a
    little back, its brim peaked over the brow and turned up behind."""
    region = swatch(cloth, dye(color), blotch=0.12, weave=0.03)
    m = porter.Mesh("Hat")
    base = 0.232
    _crown(spec, m, region, ((base, 0.012), (0.262, 0.012), (0.305, 0.0), (0.345, -0.02), (0.372, -0.036)), (0.0, 0.378, 0.02),
           lean_from=0.26)
    back = lambda th: max(0.0, (abs(th) - 1.2) / (math.pi - 1.2))
    peak = lambda th: max(0.0, 1.0 - abs(th) / 0.9)
    _brim(spec, m, region, base, lambda th: 0.034 + 0.024 * peak(th) - 0.004 * back(th),
          lambda th: math.radians(-6.0 + 78.0 * back(th) ** 0.8), drop=lambda th: 0.004 * peak(th))
    m.build(smooth=True, parent=head)


def cap(spec, head, color="dark", cloth="hat"):
    """A felt cap close on the head, its edge rolled."""
    region = swatch(cloth, dye(color), blotch=0.1, weave=0.03)
    mat = "chr_" + spec["name"]
    m = porter.Mesh("Cap")
    rows = people.head_rows(spec)
    cols = 12
    low = lambda th: 0.03 * min(1.0, max(0.0, (abs(th) - 0.9) / 0.9))
    rings = []
    for i, (h, grow) in enumerate(((0.214, 0.012), (0.25, 0.013), (0.282, 0.012), (0.302, 0.004))):
        ring = []
        for c in range(cols + 1):
            th = -math.pi + 2.0 * math.pi * c / cols
            # Down over the ears and the back of the head, up off the brow.
            hh = h - (low(th) if i == 0 else 0.0)
            x, _, z = people.head_point(rows, th, min(hh, 0.29))
            d = math.hypot(x, z - 0.004)
            sc = (d + grow) / max(d, 1e-4) * (0.6 if i == 3 else 1.0)
            ring.append(m.vert(x * sc, hh, 0.004 + (z - 0.004) * sc, grey(0.75 + 0.08 * i), people.uv(region, c / cols, 0.7 - 0.2 * i)))
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for c in range(cols):
            m.face((r1[c], r1[c + 1], r0[c + 1], r0[c]), mat)
    top = m.vert(0.0, 0.31, 0.006, WHITE, people.uv(region, 0.5, 0.0))
    for c in range(cols):
        m.face((top, rings[-1][c + 1], rings[-1][c]), mat)
    edge = []
    for c in range(cols + 1):
        th = -math.pi + 2.0 * math.pi * c / cols
        hh = 0.214 - low(th) + 0.008
        x, _, z = people.head_point(rows, th, min(hh, 0.29))
        d = math.hypot(x, z - 0.004)
        sc = (d + 0.016) / d
        edge.append((x * sc, hh, 0.004 + (z - 0.004) * sc))
    tube(m, mat, edge, [0.011] * len(edge), 4, region, [grey(0.85)] * len(edge))
    m.build(smooth=True, parent=head)


def straw(spec, head, color="straw", cloth="hat", brim=0.1, badges=0, turned=False):
    """A wide-brimmed hat, low in the crown: straw, or felt for a pilgrim's
    (`turned`: its brim up in front; `badges`: pewter badges pinned there)."""
    region = swatch(cloth, dye(color), weave=0.14, blotch=0.1, wear=0.3)
    m = porter.Mesh("Hat")
    base = 0.236
    _crown(spec, m, region, ((base, 0.012), (0.268, 0.012), (0.296, 0.002), (0.31, -0.02)), (0.0, 0.316, 0.004))
    front = lambda th: max(0.0, 1.0 - abs(th) / 1.1) ** 0.7
    _brim(spec, m, region, base, lambda th: brim * (1.0 - 0.35 * front(th) if turned else 1.0),
          lambda th: math.radians(-10.0 + (62.0 * front(th) if turned else 0.0)))
    if badges:
        swatch("metal", CLOTH["tin"], wear=0.6)
        rows = people.head_rows(spec)
        for i in range(badges):
            th = (i - (badges - 1) * 0.5) * 0.32
            x, _, z = people.head_point(rows, th, 0.26)
            box(m, "chr_" + spec["name"], (x * 1.16, 0.262 + 0.008 * (i % 2), z * 1.16 - 0.004), (0.02, 0.022, 0.006), "metal", grey(0.9),
                yaw=-th)
    m.build(smooth=True, parent=head)


def pilgrim_hat(spec, head, color="dark", badges=3):
    """A pilgrim's felt hat, the brim turned up in front with his badges on it."""
    straw(spec, head, color=color, brim=0.085, badges=badges, turned=True)


def long_hair(spec, head):
    """Hair to the collar, behind the ears (HAIR_STYLES "long")."""
    region = swatch("hair", spec["hair"], blotch=0.0, weave=0.0)
    m = _shell(spec, head, "Hair", region, [-0.03, 0.03, 0.09, 0.15, 0.21, 0.25],
               lambda h, th: 0.012 + 0.012 * max(0.0, (0.12 - h) / 0.15), opening=lambda mid, th: abs(th) < 1.3, inner=0.5,
               shade=(0.75, 1.0))
    m.build(smooth=True, parent=head)


HEADWEAR = {"hood": hood, "cowl": cowl, "coif": coif, "kerchief": kerchief, "wimple": wimple, "bycocket": bycocket, "cap": cap,
            "straw": straw, "pilgrim_hat": pilgrim_hat, "wrap": wrap}


# --------------------------------------------------------------- props

def staff(spec, grip=1.0, length=2.05):
    """A staff: a tall pole of ash. Origin where his hand holds it, `grip` up from its foot."""
    wood = swatch("wood", CLOTH["wood"], stripes=0.4)
    kh = spec["height"]
    g = grip * kh
    m = porter.Mesh("Staff")
    tube(m, "chr_" + spec["name"], [(0.0, 0.02 - g, 0.02), (0.0, 0.0, 0.0), (-0.01, length * kh - g, -0.02)], [0.021, 0.019, 0.017], 5,
         wood, [grey(0.7), WHITE, WHITE], caps=(True, True))
    m.build(smooth=True)


def lantern(spec):
    """A lantern: an iron frame, horn panes glowing (material
    chr_lantern_horn), a cone of a top, a ring to hold it by. Origin at its
    middle; the ring's top is 0.18 m above."""
    swatch("metal", CLOTH["iron"], wear=0.5, blotch=0.2)
    mat = "chr_" + spec["name"]
    m = porter.Mesh("Lantern")
    w, h = 0.062, 0.085
    for sx in (-1, 1):
        for sz in (-1, 1):
            box(m, mat, (sx * w, 0.0, sz * w), (0.014, 2 * h, 0.014), "metal", grey(0.7))
    box(m, mat, (0.0, -h - 0.008, 0.0), (2 * w + 0.03, 0.016, 2 * w + 0.03), "metal", grey(0.6))
    box(m, mat, (0.0, h + 0.006, 0.0), (2 * w + 0.024, 0.012, 2 * w + 0.024), "metal", grey(0.8))
    top = (0.0, h + 0.075, 0.0)
    corners = [(-w - 0.012, h + 0.012, -w - 0.012), (w + 0.012, h + 0.012, -w - 0.012), (w + 0.012, h + 0.012, w + 0.012),
               (-w - 0.012, h + 0.012, w + 0.012)]
    for i in range(4):
        a, b = corners[i], corners[(i + 1) % 4]
        mid = ((a[0] + b[0]) / 2, 0.0, (a[2] + b[2]) / 2)
        m.poly([a, b, top], mat, [grey(0.6), grey(0.6), WHITE], [people.uv("metal", 0, 1), people.uv("metal", 1, 1),
                                                                 people.uv("metal", 0.5, 0)], facing=(mid[0], 0.5, mid[2]))
    ring = []
    for i in range(7):
        a = math.pi * i / 6.0
        ring.append((math.cos(a) * 0.03, h + 0.09 + math.sin(a) * 0.04, 0.0))
    tube(m, mat, ring, [0.005] * 7, 3, "metal", [WHITE] * 7)
    for nrm in ((0, 0, -1), (0, 0, 1), (-1, 0, 0), (1, 0, 0)):
        nx, nz = nrm[0], nrm[2]
        tx, tz = -nz, nx
        pts = [(nx * w + tx * s * w, y, nz * w + tz * s * w) for s, y in ((-1, -h), (1, -h), (1, h), (-1, h))]
        m.poly(pts, "chr_lantern_horn", [WHITE] * 4, [(0, 0), (1, 0), (1, 1), (0, 1)], facing=nrm)
    m.build(smooth=False)


PROPS = {"staff": staff, "lantern": lantern}


# ---------------------------------------------------------------- build

def _body(spec):
    k = Kit(spec)
    swatch("hands", spec["hands_color"], blotch=0.1, weave=0.03)
    for name, opts in _entries(spec.get("wear")):
        WEAR[name](k, **opts)
    obj = k.m.build(smooth=True)
    fists = spec.get("fists", ())
    holds = {h: (v, {}) if isinstance(v, str) else (v[0], dict(v[1])) for h, v in spec.get("holds", {}).items()}
    arms = {}
    for side, s in ((-1, "l"), (1, "r")):
        arms[side] = {"sleeve": k.sleeve or "hands", "cuff": k.cuff, "wide": k.wide, "fist": s in fists or s in holds}
        if s in holds:
            name, opts = holds[s]
            arms[side]["held"] = lambda m, mat, grip, ahead, fn=HELD[name], o=opts: fn(k, m, grip, ahead, **o)
    people.standing_limbs(spec, obj, arms, k.legs)


def _headwear(spec, head):
    if spec.get("hair_style") == "long":
        long_hair(spec, head)
    for name, opts in _entries(spec.get("headwear")):
        HEADWEAR[name](spec, head, **opts)


def build(spec, posed=None, keep_apart=(), game=True, head_only=False):
    """Builds a person from his spec (the top of this file): his body on
    its skeleton with his clips, his head, a model for each of his props
    (chr_<name>_<prop>.glb), his texture, and, for the game, his materials
    and his scene if he has none. `posed(spec, skeleton)` adds parts made in
    one of his clips' poses. `head_only`: just the head and the texture
    (the catalogue's faces). Returns the spec, resolved."""
    s = resolve(spec)
    if head_only:
        people.reset_atlas()
        swatch("hands", s["hands_color"], blotch=0.1, weave=0.03)
        people.build_head(s, _headwear)
        people.texture(s)
        return s
    extras = []
    held_props = []
    for name, opts in _entries(spec.get("props")):
        hand = opts.pop("hand", None)
        if hand:
            # Where the scene stands it: at his side, a little forward, his hand
            # at its grip (1 m up a staff).
            sx = -1.0 if hand == "l" else 1.0
            held_props.append({"name": name, "hand": hand, "at": (sx * 0.3 * s["breadth"], opts.get("grip", 1.0) * s["height"], -0.2)})
        extras.append(("chr_%s_%s" % (s["name"], name), lambda sp, fn=PROPS[name], o=opts: fn(sp, **o)))
    s["held_props"] = held_props
    people.build(s, _body, _headwear, extras, posed, keep_apart, game)
    return s
