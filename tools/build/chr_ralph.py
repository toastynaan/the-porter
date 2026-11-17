"""Ralph the chandler, who makes the abbey's candles: short and heavy, grey,
going bald. A brown tunic under a bibbed apron stained with wax, a coif, a
bundle of tapers in his hand.

The look is *(mine)*, from the design's words. Put together from the people's
kit (tools/build/people_kit.py).

Run: tools/build.sh chr_ralph
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import people_kit

SPEC = {
    "name": "ralph",
    "seed": 86,
    "about": "Ralph the chandler, who makes the abbey's candles: short and heavy, grey, going bald. A brown tunic under a bibbed apron stained with wax, a coif, a bundle of tapers in his hand (tools/build/chr_ralph.py).",
    "body": "short_heavy",
    "skin": "fair",
    "face": "broad",
    "eyes": "brown",
    "hair": ("grey", "balding"),
    "age": 0.65,
    "wear": [
        ("hose", {"color": "grey"}),
        ("shoes", {}),
        ("tunic", {"color": "brown", "belt": None}),
        ("apron", {"color": "tan", "top": 1.3}),
    ],
    "headwear": ["coif"],
    "holds": {"l": "candles"},
}

if __name__ == "__main__":
    people_kit.build(SPEC)
