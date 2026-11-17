"""Roger, the town bailiff (design doc, "Outside the gate"; not in the
character table: his look is mine). Lean, pale, hard; a dark gown belted
with a purse and a knife, boots to the calf, a dark cap, a short black
beard.

The look is *(mine)*, from the design's words. Put together from the people's
kit (tools/build/people_kit.py).

Run: tools/build.sh chr_roger
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import people_kit

SPEC = {
    "name": "roger",
    "seed": 83,
    "about": "Roger, the town bailiff (design doc, 'Outside the gate'; not in the character table: his look is mine). Lean, pale, hard; a dark gown belted with a purse and a knife, boots to the calf, a dark cap, a short black beard (tools/build/chr_roger.py).",
    "body": "lean",
    "skin": "pale",
    "face": "square",
    "brows": "stern",
    "eyes": "dark",
    "hair": ("black", "cropped"),
    "beard": "short",
    "age": 0.5,
    "wear": [
        ("hose", {"color": "dark"}),
        ("boots", {"top": 0.3}),
        ("gown", {"color": (0.16, 0.16, 0.18), "belt": {"hung": ["purse", "knife"]}}),
    ],
    "headwear": [
        ("cap", {"color": "black"}),
    ],
}

if __name__ == "__main__":
    people_kit.build(SPEC)
