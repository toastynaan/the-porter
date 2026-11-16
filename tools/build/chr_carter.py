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
(chr_carter_head.glb). He is put together from the people's kit
(tools/build/people_kit.py); the whip and the reins are his own.

Run: tools/build.sh chr_carter
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import people
import people_kit
import porter
import rig
from people import WHITE, grey, lerp3, mirror, swatch, tube

SPEC = {
    "name": "carter",
    "seed": 52,
    "body": ("average", {"height": 0.98, "frame": 1.06}),
    "skin": ("weathered", {"skin": (0.64, 0.5, 0.42), "hands": (0.62, 0.47, 0.39), "lip": (0.5, 0.3, 0.27)}),
    "face": ("plain", {"width": 1.02, "jaw": 1.06, "chin": 0.95, "nose": 1.15, "nose_width": 1.2, "brow": 1.2}),
    "eyes": "grey",
    "brow_size": (0.0175, 0.003),
    "hair": ((0.27, 0.23, 0.19), "cropped"),
    "hairline": 0.228,
    "grey": 0.45,
    "beard": ("stubble", {"beard": 0.55}),
    "beard_color": (0.3, 0.27, 0.23),
    "age": 0.9,
    "flush": 0.85,
    "fists": ("l", "r"),
    "wear": [
        ("hose", {"color": (0.25, 0.24, 0.22)}),
        ("wraps", {"color": (0.32, 0.29, 0.24)}),
        ("shoes", {"color": (0.24, 0.18, 0.13)}),
        ("tunic", {"color": "russet", "belt": {"hung": ["knife"]}}),
        ("cape", {"color": "undyed"}),
    ],
    "headwear": [("hood", {"color": "undyed"})],
    # On the board, 0.25 m above the seat's origin; his feet on the bed, 6 cm
    # below it.
    "clips": {
        "sit": {"from": "Driving_Loop", "seat": 0.25, "ankle": (0.13, 0.02, -0.4), "knee": (0.0, 1.0, -0.5)},
    },
}
MAT = "chr_carter"


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


def driving(spec, skeleton):
    """What he holds as he drives (the sit clip): the whip up in his right
    fist, leaning forward over the horse, bound to his hand; the reins from
    both fists to the horse's collar."""
    swatch("wood", people_kit.CLOTH["wood"], stripes=0.5)
    swatch("leather", people_kit.CLOTH["leather"], wear=0.5, blotch=0.15)
    pose = rig.posed(skeleton, "sit")
    j = people.joints()
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


if __name__ == "__main__":
    people_kit.build(SPEC, posed=driving, keep_apart=("Reins", "Whip"))
