"""The sailor at the gate on night 2 (and a shape in an alley on the road in):
lean, weathered; a short coat of tarred cloth, loose hose, a cap, a sea
bundle on his shoulder.

The look is *(mine)*, from the design's words. Put together from the people's
kit (tools/build/people_kit.py).

Run: tools/build.sh chr_sailor
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import people_kit

SPEC = {
    "name": "sailor",
    "seed": 107,
    "about": "The sailor at the gate on night 2 (and a shape in an alley on the road in): lean, weathered; a short coat of tarred cloth, loose hose, a cap, a sea bundle on his shoulder (tools/build/chr_sailor.py).",
    "body": "lean",
    "skin": "weathered",
    "face": "sharp",
    "eyes": "grey",
    "hair": ("black", "cropped"),
    "beard": "short",
    "age": 0.5,
    "wear": [
        ("hose", {"color": "tan"}),
        ("shoes", {"color": "brown"}),
        ("tunic", {"color": (0.2, 0.22, 0.25), "hem": 0.8, "belt": "leather"}),
        ("bundle", {}),
    ],
    "headwear": [
        ("cap", {"color": "woad"}),
    ],
}

if __name__ == "__main__":
    people_kit.build(SPEC)
