"""Gib, the night watchman: old, hunched; he lights the lane's lanterns and
walks it after curfew calling the hour. A grey cloak with its hood down over
a grey tunic, a cap, a white beard, a staff in his left hand (his lantern is
the visitor's).

The look is *(mine)*, from the design's words. Put together from the people's
kit (tools/build/people_kit.py).

Run: tools/build.sh chr_gib
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import people_kit

SPEC = {
    "name": "gib",
    "seed": 92,
    "about": "Gib, the night watchman: old, hunched; he lights the lane's lanterns and walks it after curfew calling the hour. A grey cloak with its hood down over a grey tunic, a cap, a white beard, a staff in his left hand (his lantern is the visitor's) (tools/build/chr_gib.py).",
    "body": "hunched",
    "skin": "weathered",
    "face": "gaunt",
    "brows": "bushy",
    "eyes": "grey",
    "hair": ("white", "balding"),
    "beard": "full",
    "age": 1.0,
    "wear": [
        ("hose", {"color": "dark"}),
        ("boots", {}),
        ("tunic", {"color": "grey"}),
        ("cloak", {"color": (0.23, 0.23, 0.22), "hem": 0.5, "hood": True}),
    ],
    "headwear": [
        ("cap", {"color": "dark"}),
    ],
    "props": [
        ("staff", {"hand": "l", "grip": 0.95, "length": 1.75}),
    ],
}

if __name__ == "__main__":
    people_kit.build(SPEC)
