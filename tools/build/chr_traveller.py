"""Will Fuller, the traveller on the carter's wagon on night 0: a wool
merchant from Colchester, forty-one, lean and road-worn, "a merchant by his
good wet cloak" (game/chapters/night0/dialogue/traveller_road.talk). A tall
felt hat, its brim peaked in front and turned up behind; a belted gown to the
knee under a travelling cloak, hose, ankle boots, a purse; a pack on his
back with a blanket rolled on it. Muted colours *(mine)*.

His body on his skeleton, with the clips he moves by: standing (idle,
talk, walk) and seated on the wagon's bed, his back to the load, knees up
(sit: his forearms toward his knees; sit_talk) (chr_traveller.glb); his head
(chr_traveller_head.glb). He is put together from the people's kit
(tools/build/people_kit.py).

Run: tools/build.sh chr_traveller
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import people_kit

SPEC = {
    "name": "traveller",
    "seed": 41,
    "about": "Will Fuller, the traveller on the carter's wagon on the road in through Aldgate (night 0): a wool merchant from "
             "Colchester, forty-one, lean, road-worn. A tall felt hat turned up behind, a belted gown under a good travelling "
             "cloak, a pack on his back (tools/build/chr_traveller.py). Seated on the wagon's bed, knees up (sit, sit_talk), when "
             "`seated` is on, or the Look's `seated`.",
    "body": ("lean", {"height": 1.0, "girth": 0.0}),
    "skin": "fair",
    "face": ("narrow", {"width": 0.96, "jaw": 0.92, "chin": 1.05, "nose_width": 0.95}),
    "eyes": "brown",
    "hair": ("dark", "cropped"),
    "grey": 0.3,
    "beard": "stubble",
    "age": 0.5,
    "lines": 0.5,
    "wear": [
        ("hose", {"color": (0.23, 0.19, 0.16)}),
        ("boots", {"color": (0.28, 0.2, 0.14), "top": 0.15}),
        ("gown", {"color": "slate", "belt": {"hung": ["purse", "knife"]}}),
        ("cloak", {"color": "moss"}),
        "pack",
    ],
    "headwear": [("bycocket", {"color": (0.22, 0.18, 0.15)})],
    # On the wagon's bed: the seat's origin is 6 cm above its boards.
    "clips": {
        "sit": {"from": "Sitting_Idle_Loop", "seat": 0.0, "ankle": (0.12, 0.025, -0.37), "knee": (0.0, 1.0, -0.3),
                "wrist": (0.07, 0.37, -0.42), "elbow": (0.6, -0.4, 0.2)},
        "sit_talk": {"from": "Sitting_Talking_Loop", "seat": 0.0, "ankle": (0.12, 0.025, -0.37), "knee": (0.0, 1.0, -0.3)},
    },
}

if __name__ == "__main__":
    people_kit.build(SPEC)
