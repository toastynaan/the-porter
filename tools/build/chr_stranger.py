"""A hooded stranger in a black habit, the cowl up and his face far back in its
shadow: a cultist in a dead brother's place.

The look is *(mine)*, from the design's words. Put together from the people's
kit (tools/build/people_kit.py).

Run: tools/build.sh chr_stranger
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import people_kit

SPEC = {
    "name": "stranger",
    "seed": 113,
    "about": "A hooded stranger in a black habit, the cowl up and his face far back in its shadow: a cultist in a dead brother's place (tools/build/chr_stranger.py).",
    "body": "average",
    "skin": "pale",
    "face": "plain",
    "eyes": "dark",
    "hair": ("dark", "tonsure"),
    "age": 0.4,
    "face_shade": 0.28,
    "wear": [
        ("shoes", {"color": "brown"}),
        ("habit", {"hood": "up"}),
    ],
    "headwear": ["cowl"],
}

if __name__ == "__main__":
    people_kit.build(SPEC)
