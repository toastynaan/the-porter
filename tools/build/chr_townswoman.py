"""A woman of the city in her doorway on the road in (night 0): a plain dark
kirtle, a white coif.

The look is *(mine)*, from the design's words. Put together from the people's
kit (tools/build/people_kit.py).

Run: tools/build.sh chr_townswoman
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import people_kit

SPEC = {
    "name": "townswoman",
    "seed": 104,
    "about": "A woman of the city in her doorway on the road in (night 0): a plain dark kirtle, a white coif (tools/build/chr_townswoman.py).",
    "body": "woman",
    "skin": "fair",
    "face": "soft",
    "eyes": "brown",
    "hair": ("brown", "cropped"),
    "age": 0.35,
    "wear": [
        ("shoes", {}),
        ("kirtle", {"color": (0.24, 0.21, 0.23)}),
    ],
    "headwear": [
        ("coif", {"color": "white"}),
    ],
}

if __name__ == "__main__":
    people_kit.build(SPEC)
