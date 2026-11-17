"""Kit, Ralph the chandler's daughter, who sells candles at the gate: small,
quick, young (her age is mine: a girl of fourteen or so). Fair hair loose to
her collar, a tan kirtle and an apron, a basket of candles.

The look is *(mine)*, from the design's words. Put together from the people's
kit (tools/build/people_kit.py).

Run: tools/build.sh chr_kit
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import people_kit

SPEC = {
    "name": "kit",
    "seed": 89,
    "about": "Kit, Ralph the chandler's daughter, who sells candles at the gate: small, quick, young (her age is mine: a girl of fourteen or so). Fair hair loose to her collar, a tan kirtle and an apron, a basket of candles (tools/build/chr_kit.py).",
    "body": ("woman_slight", {"height": 0.85}),
    "skin": "fair",
    "face": "soft",
    "eyes": "blue",
    "hair": ("fair", "long"),
    "age": 0.0,
    "freckles": 0.6,
    "wear": [
        ("shoes", {"color": "brown"}),
        ("kirtle", {"color": "tan", "hem": 0.12}),
        ("apron", {}),
    ],
    "holds": {"r": ("basket", {"candles": True})},
}

if __name__ == "__main__":
    people_kit.build(SPEC)
