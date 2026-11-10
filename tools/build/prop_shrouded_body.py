"""What lies on the cart that passes on the road in (night 0, the hook): a
body under sacking. Nothing shows but its shape: the head, the shoulders,
the hands folded, the feet making their own small peak at the end.

It lies along z with the head at -z, on the origin's level (set it on the
cart's bed). Material: sacking. Vertex colour darkens the folds.

Run: tools/build.sh prop_shrouded_body
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter

CLOTH = porter.srgb(0.5, 0.44, 0.33)
FOLD = porter.srgb(0.3, 0.26, 0.2)


def main():
    porter.reset(17)
    m = porter.Mesh("ShroudedBody")
    # From the crown of the head to past the feet: where the cloth rises and how wide it lies.
    spine = [(0.0, 0.02, -0.98), (0.0, 0.09, -0.9), (0.0, 0.1, -0.76), (0.0, 0.055, -0.66), (0.0, 0.11, -0.56),
             (0.0, 0.12, -0.25), (0.0, 0.1, 0.08), (0.0, 0.085, 0.42), (0.0, 0.065, 0.7), (0.0, 0.15, 0.87), (0.0, 0.02, 0.97)]
    radii = [0.05, 0.115, 0.12, 0.09, 0.27, 0.25, 0.2, 0.17, 0.13, 0.1, 0.04]
    shade = [FOLD, CLOTH, CLOTH, FOLD, CLOTH, CLOTH, CLOTH, FOLD, FOLD, CLOTH, FOLD]
    m.tube(spine, radii, 8, "sacking", shade, caps=True, squash=(1.0, 0.55))
    # The cloth's edge, lying out flat on the boards either side.
    for side in (-1, 1):
        for a, b in zip(spine[1:-1], spine[2:-1]):
            w0 = 0.34 + 0.05 * ((int(a[2] * 100) * 37) % 3)
            w1 = 0.34 + 0.05 * ((int(b[2] * 100) * 37) % 3)
            m.poly([(side * 0.12, 0.05, a[2]), (side * 0.12, 0.05, b[2]), (side * w1, 0.012, b[2]), (side * w0, 0.012, a[2])],
                   "sacking", [CLOTH, CLOTH, FOLD, FOLD], facing=(0, 1, 0))
    m.build(smooth=True)
    porter.export("prop_shrouded_body")


if __name__ == "__main__":
    main()
