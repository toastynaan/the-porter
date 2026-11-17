"""Agnes, Hob's wife, who keeps the Cross Keys with him: sharp, motherly. A
dark wool kirtle and an apron, a wimple and veil, a cloth over her shoulder
for the tables.

The look is *(mine)*, from the design's words. Put together from the people's
kit (tools/build/people_kit.py).

Run: tools/build.sh chr_agnes
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import people_kit

SPEC = {
    "name": "agnes",
    "seed": 74,
    "about": "Agnes, Hob's wife, who keeps the Cross Keys with him: sharp, motherly. A dark wool kirtle and an apron, a wimple and veil, a cloth over her shoulder for the tables (tools/build/chr_agnes.py).",
    "body": ("woman", {"girth": 0.3}),
    "skin": "fair",
    "face": "sharp",
    "eyes": "grey",
    "hair": ("brown", "cropped"),
    "age": 0.5,
    "wear": [
        ("shoes", {}),
        ("kirtle", {"color": (0.2, 0.16, 0.14)}),
        ("apron", {}),
        ("shoulder_cloth", {}),
    ],
    "headwear": ["wimple"],
}

if __name__ == "__main__":
    people_kit.build(SPEC)
