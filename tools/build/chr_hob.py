"""Hob, who keeps the Cross Keys with Agnes (design doc, "The lane"): the
innkeeper, who hears everything said over the ale. Big, red-faced, going
bald; a tan tunic, a linen apron tied at his waist, an ale jug in his hand.

The look is *(mine)*, from the design's words. Put together from the people's
kit (tools/build/people_kit.py).

Run: tools/build.sh chr_hob
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import people_kit

SPEC = {
    "name": "hob",
    "seed": 71,
    "about": "Hob, who keeps the Cross Keys with Agnes (design doc, 'The lane'): the innkeeper, who hears everything said over the ale. Big, red-faced, going bald; a tan tunic, a linen apron tied at his waist, an ale jug in his hand (tools/build/chr_hob.py).",
    "body": ("big", {"girth": 0.75}),
    "skin": "ruddy",
    "face": "round",
    "eyes": "brown",
    "hair": ("brown", "balding"),
    "beard": "stubble",
    "age": 0.55,
    "wear": [
        ("hose", {"color": "brown"}),
        ("shoes", {}),
        ("tunic", {"color": "tan"}),
        ("apron", {}),
    ],
    "holds": {"r": "jug"},
}

if __name__ == "__main__":
    people_kit.build(SPEC)
