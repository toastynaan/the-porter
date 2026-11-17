"""Mab, a leper, who begs at the abbey gate every night (Look and Feel,
"Characters": small, wrapped in rags; face covered by cloth; a leper's
clapper). Bent; rags to the shin and a ragged shawl, her head and face wound
in cloth to the eyes, bound feet, the clapper in her hand.

The look is *(mine)*, from the design's words. Put together from the people's
kit (tools/build/people_kit.py).

Run: tools/build.sh chr_mab
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import people_kit

SPEC = {
    "name": "mab",
    "seed": 98,
    "about": "Mab, a leper, who begs at the abbey gate every night (Look and Feel, 'Characters': small, wrapped in rags; face covered by cloth; a leper's clapper). Bent; rags to the shin and a ragged shawl, her head and face wound in cloth to the eyes, bound feet, the clapper in her hand (tools/build/chr_mab.py).",
    "body": ("woman_slight", {"height": 0.88, "stoop": 24.0}),
    "skin": "sallow",
    "face": "gaunt",
    "eyes": "dark",
    "hair": ("grey", "cropped"),
    "age": 0.8,
    "wear": [
        ("wraps", {"color": "undyed"}),
        ("rags", {"color": (0.36, 0.31, 0.24)}),
        ("shawl", {"color": (0.3, 0.27, 0.22)}),
    ],
    "headwear": [
        ("wrap", {"color": (0.4, 0.36, 0.3)}),
    ],
    "holds": {"r": "clapper"},
}

if __name__ == "__main__":
    people_kit.build(SPEC)
