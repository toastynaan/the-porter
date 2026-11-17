"""Margery, a neighbour with her basket, who hurries home before dark. Stout,
ruddy; a russet kirtle, an apron, a kerchief over her hair, a basket on her
arm.

The look is *(mine)*, from the design's words. Put together from the people's
kit (tools/build/people_kit.py).

Run: tools/build.sh chr_lane_woman
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import people_kit

SPEC = {
    "name": "lane_woman",
    "seed": 95,
    "about": "Margery, a neighbour with her basket, who hurries home before dark. Stout, ruddy; a russet kirtle, an apron, a kerchief over her hair, a basket on her arm (tools/build/chr_lane_woman.py).",
    "body": "woman_stout",
    "skin": "ruddy",
    "face": "round",
    "eyes": "brown",
    "hair": ("brown", "cropped"),
    "age": 0.6,
    "wear": [
        ("shoes", {}),
        ("kirtle", {"color": "russet"}),
        ("apron", {}),
    ],
    "headwear": ["kerchief"],
    "holds": {"l": "basket"},
}

if __name__ == "__main__":
    people_kit.build(SPEC)
