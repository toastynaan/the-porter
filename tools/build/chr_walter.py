"""Walter the pardoner, a relic-seller (Look and Feel, "Characters": plump;
oily, cheerful; a coloured cloak, the only saturated colour on any
character; a box of "relics"). A scarlet cloak over a dark gown, a felt cap,
his box on a strap at his hip, a purse.

The look is *(mine)*, from the design's words. Put together from the people's
kit (tools/build/people_kit.py).

Run: tools/build.sh chr_walter
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import people_kit

SPEC = {
    "name": "walter",
    "seed": 80,
    "about": "Walter the pardoner, a relic-seller (Look and Feel, 'Characters': plump; oily, cheerful; a coloured cloak, the only saturated colour on any character; a box of 'relics'). A scarlet cloak over a dark gown, a felt cap, his box on a strap at his hip, a purse (tools/build/chr_walter.py).",
    "body": "plump",
    "skin": ("fair", {"flush": 0.75}),
    "face": "round",
    "brows": "arched",
    "eyes": "hazel",
    "hair": ("dark", "bowl"),
    "age": 0.45,
    "wear": [
        ("hose", {"color": "dark"}),
        ("shoes", {}),
        ("gown", {"color": "dark", "belt": {"hung": ["purse"]}}),
        ("relic_box", {}),
        ("cloak", {"color": "scarlet", "hem": 0.5}),
    ],
    "headwear": [
        ("cap", {"color": "madder"}),
    ],
}

if __name__ == "__main__":
    people_kit.build(SPEC)
