"""A pilgrim (Look and Feel, "Characters": staff, shoulder bag, pilgrim badges
on the hat). An undyed gown with a cord and beads, a grey cloak, a scrip at
his hip, a felt hat with his badges, a staff in his right hand.

The look is *(mine)*, from the design's words. Put together from the people's
kit (tools/build/people_kit.py).

Run: tools/build.sh chr_pilgrim
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import people_kit

SPEC = {
    "name": "pilgrim",
    "seed": 110,
    "about": "A pilgrim (Look and Feel, 'Characters': staff, shoulder bag, pilgrim badges on the hat). An undyed gown with a cord and beads, a grey cloak, a scrip at his hip, a felt hat with his badges, a staff in his right hand (tools/build/chr_pilgrim.py).",
    "body": "average",
    "skin": "weathered",
    "face": "plain",
    "eyes": "brown",
    "hair": ("brown", "cropped"),
    "beard": "short",
    "age": 0.5,
    "wear": [
        ("hose", {"color": "grey"}),
        ("boots", {}),
        ("gown", {"color": "undyed", "belt": {"cloth": "rope", "hung": ["rosary"]}}),
        ("scrip", {}),
        ("cloak", {"color": "grey", "hem": 0.7}),
    ],
    "headwear": ["pilgrim_hat"],
    "props": [
        ("staff", {"hand": "r", "grip": 1.05, "length": 1.8}),
    ],
}

if __name__ == "__main__":
    people_kit.build(SPEC)
