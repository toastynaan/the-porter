"""Jankin, a drunk, a regular at the Cross Keys: harmless, full of stories.
Gangly, flushed; a patched tunic, a coif, a wooden cup in his hand.

The look is *(mine)*, from the design's words. Put together from the people's
kit (tools/build/people_kit.py).

Run: tools/build.sh chr_jankin
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import people_kit

SPEC = {
    "name": "jankin",
    "seed": 77,
    "about": "Jankin, a drunk, a regular at the Cross Keys: harmless, full of stories. Gangly, flushed; a patched tunic, a coif, a wooden cup in his hand (tools/build/chr_jankin.py).",
    "body": "gangly",
    "skin": "ruddy",
    "face": "hooked",
    "brows": "worried",
    "eyes": "blue",
    "hair": ("fair", "cropped"),
    "beard": "stubble",
    "age": 0.5,
    "wear": [
        ("hose", {"color": "undyed"}),
        ("shoes", {"color": "brown"}),
        ("tunic", {"color": (0.3, 0.27, 0.22), "patches": 0.6, "wear": 0.6, "belt": "rope"}),
    ],
    "headwear": ["coif"],
    "holds": {"r": "cup"},
}

if __name__ == "__main__":
    people_kit.build(SPEC)
