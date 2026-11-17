"""Cole, a lay brother (Look and Feel, "Characters": a big labourer; weathered,
blank; a brown work tunic, not a habit). He keeps the gate by day. A rope
for a belt, hose, heavy boots.

The look is *(mine)*, from the design's words. Put together from the people's
kit (tools/build/people_kit.py).

Run: tools/build.sh chr_cole
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import people_kit

SPEC = {
    "name": "cole",
    "seed": 101,
    "about": "Cole, a lay brother (Look and Feel, 'Characters': a big labourer; weathered, blank; a brown work tunic, not a habit). He keeps the gate by day. A rope for a belt, hose, heavy boots (tools/build/chr_cole.py).",
    "body": "big",
    "skin": "weathered",
    "face": "heavy",
    "eyes": "dark",
    "hair": ("dark", "cropped"),
    "beard": "stubble",
    "age": 0.45,
    "wear": [
        ("hose", {"color": "undyed"}),
        ("boots", {"top": 0.22}),
        ("tunic", {"color": "brown", "belt": "rope", "wear": 0.5}),
    ],
}

if __name__ == "__main__":
    people_kit.build(SPEC)
