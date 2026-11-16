"""Lambert, the warden at Aldgate on night 0 (game/chapters/night0/dialogue/warden.talk):
a gatekeeper, blunt and tired, solid; the city's man. A dark cloak over a
leather jerkin, thrown back off his right shoulder so the lantern arm is
free, its hood down round his neck; a dark felt cap; a short grizzled
beard; dark hose and boots to the calf. A tall staff in his left hand. His
lantern, horn panes in an iron frame, and his staff are models of their own
(chr_warden_lantern.glb, chr_warden_staff.glb, each with its origin where
his hand holds it): the scene puts them in his hands, and his arms follow
them wherever the ride lifts them (PersonModel). Muted colours *(mine)*.

His body on his skeleton, with the clips he moves by (idle, talk, walk:
chr_warden.glb), and his head in its cap (chr_warden_head.glb). He is put
together from the people's kit (tools/build/people_kit.py).

Run: tools/build.sh chr_warden
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import people_kit

SPEC = {
    "name": "warden",
    "seed": 63,
    "body": ("big", {"height": 1.02, "frame": 1.1, "girth": 0.25, "limb": 1.0, "shoulders": 1.0}),
    "skin": ("weathered", {"skin": (0.63, 0.5, 0.43), "hands": (0.6, 0.47, 0.4), "lip": (0.42, 0.28, 0.25)}),
    "face": ("broad", {"nose": 1.1, "brow": 1.5}),
    "eyes": (0.27, 0.26, 0.25),
    "brow_size": (0.018, 0.0034),
    "hair": ((0.26, 0.23, 0.2), "cropped"),
    "grey": 0.55,
    "beard": "full",
    "beard_color": (0.3, 0.27, 0.24),
    "age": 0.8,
    "flush": 0.6,
    "fists": ("l", "r"),
    "wear": [
        ("hose", {"color": (0.19, 0.18, 0.17)}),
        ("boots", {"color": (0.22, 0.16, 0.11), "top": 0.3}),
        ("tunic", {"color": (0.2, 0.2, 0.22), "collar_only": True}),
        ("jerkin", {"color": (0.31, 0.22, 0.15), "belt": {"cloth": "dark", "hung": ["purse", "keys"]}}),
        ("cloak", {"color": (0.16, 0.17, 0.19), "hem": 0.34, "thrown": True, "hood": True, "clasp": False}),
    ],
    "headwear": [("cap", {"color": (0.15, 0.14, 0.14)})],
    # The lantern hangs 0.18 m below his hand; the staff is held 1 m up it.
    "props": ["lantern", ("staff", {"grip": 1.0})],
}

if __name__ == "__main__":
    people_kit.build(SPEC)
