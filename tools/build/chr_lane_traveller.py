"""A traveller in the lane at dusk: lean, road-worn, a stranger passing
through. A hood and cape, a dark tunic, a pack on his back.

The look is *(mine)*, from the design's words. Put together from the people's
kit (tools/build/people_kit.py).

Run: tools/build.sh chr_lane_traveller
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import people_kit

SPEC = {
    "name": "lane_traveller",
    "seed": 116,
    "about": "A traveller in the lane at dusk: lean, road-worn, a stranger passing through. A hood and cape, a dark tunic, a pack on his back (tools/build/chr_lane_traveller.py).",
    "body": "lean",
    "skin": "weathered",
    "face": "narrow",
    "eyes": "hazel",
    "hair": ("brown", "cropped"),
    "beard": "stubble",
    "age": 0.45,
    "wear": [
        ("hose", {"color": "brown"}),
        ("boots", {}),
        ("tunic", {"color": (0.24, 0.23, 0.2)}),
        ("cape", {"color": "moss"}),
        ("pack", {}),
    ],
    "headwear": [
        ("hood", {"color": "moss"}),
    ],
}

if __name__ == "__main__":
    people_kit.build(SPEC)
