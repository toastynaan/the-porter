"""A cart horse of the 1420s: a plain bay cob in a collar, the kind between
a carter's shafts. Low-poly, coloured by vertex (no texture), shaded per
vertex like the game's people (Look and Feel, "Characters").

It faces -Z; the origin is on the ground under the middle of its body. It is
made of parts that turn about their joints, so a script can walk it
(game/world/road/horse_gait.gd):

    Body                    the barrel, with the harness on it
      Neck                  neck, head, ears and mane, about the withers
      Tail                  about the dock
      LegFL, LegFR          forearms, about the shoulders ...
        ShinFL, ShinFR      ... and cannons and hooves, about the knees
      LegHL, LegHR          thighs, about the hips ...
        ShinHL, ShinHR      ... and cannons and hooves, about the hocks

Materials: horse_hide (everything hide and hair), horse_tack (collar, pad,
straps).

Run: tools/build.sh chr_horse
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter

BAY = porter.srgb(0.3, 0.2, 0.14)
BAY_LIGHT = porter.srgb(0.37, 0.26, 0.18)
BAY_DARK = porter.srgb(0.18, 0.12, 0.09)
BLACK = porter.srgb(0.07, 0.06, 0.06)
HOOF = porter.srgb(0.16, 0.14, 0.13)
LEATHER = porter.srgb(0.75, 0.75, 0.75)
# Joints: (x is given for the left; the right is mirrored).
SHOULDER = (0.2, 1.12, -0.58)
KNEE = (0.2, 0.6, -0.6)
HIP = (0.21, 1.14, 0.6)
HOCK = (0.21, 0.64, 0.8)
WITHERS = (0.0, 1.3, -0.62)
DOCK = (0.0, 1.34, 0.9)


def body():
    m = porter.Mesh("Body")
    spine = [(0.0, 1.2, 0.95), (0.0, 1.17, 0.72), (0.0, 1.12, 0.35), (0.0, 1.08, -0.1), (0.0, 1.11, -0.5),
             (0.0, 1.16, -0.8), (0.0, 1.2, -0.95)]
    radii = [0.18, 0.36, 0.4, 0.42, 0.4, 0.33, 0.18]
    shade = [BAY, BAY, BAY_LIGHT, BAY_LIGHT, BAY, BAY, BAY_DARK]
    m.tube(spine, radii, 8, "horse_hide", shade, caps=True, squash=(0.86, 1.0))
    # The collar: a padded ring round the base of the neck, tilted back.
    ring = []
    for k in range(11):
        a = math.tau * k / 10.0
        ring.append((math.sin(a) * 0.27, 1.25 + math.cos(a) * 0.37, -0.8 + math.cos(a) * 0.14))
    m.tube(ring, [0.05] * 11, 5, "horse_tack", LEATHER)
    # A pad on the back, a band under the belly, and the breeching round the quarters.
    m.box((-0.2, 1.43, -0.38), (0.2, 1.5, -0.12), "horse_tack", LEATHER, faces="xXzZyY")
    for x0, x1 in ((-0.38, -0.35), (0.35, 0.38)):
        m.box((x0, 0.72, -0.3), (x1, 1.46, -0.21), "horse_tack", LEATHER, faces="xXzZyY")
    m.box((-0.37, 0.68, -0.3), (0.37, 0.72, -0.21), "horse_tack", LEATHER, faces="xXzZyY")
    return m.build(smooth=True)


def neck(parent):
    m = porter.Mesh("Neck")
    m.tube([(0.0, 1.24, -0.68), (0.0, 1.5, -0.98), (0.0, 1.72, -1.22), (0.0, 1.84, -1.36)], [0.28, 0.21, 0.165, 0.135], 7,
           "horse_hide", [BAY, BAY, BAY, BAY_DARK], squash=(0.66, 1.0))
    # The head: from the poll down the face to the muzzle.
    m.tube([(0.0, 1.9, -1.33), (0.0, 1.82, -1.46), (0.0, 1.62, -1.7), (0.0, 1.47, -1.86), (0.0, 1.42, -1.9)],
           [0.1, 0.155, 0.12, 0.092, 0.065], 6, "horse_hide", [BAY_DARK, BAY, BAY, BAY_DARK, BLACK], caps=True, squash=(0.7, 1.0))
    for side in (-1, 1):  # ears
        m.poly([(side * 0.05, 1.93, -1.36), (side * 0.11, 1.95, -1.33), (side * 0.085, 2.07, -1.35)], "horse_hide", BAY_DARK,
               facing=(side * 0.3, 0.0, -1.0))
        m.poly([(side * 0.05, 1.93, -1.36), (side * 0.11, 1.95, -1.33), (side * 0.085, 2.07, -1.35)], "horse_hide", BLACK,
               facing=(-side * 0.3, 0.0, 1.0))
    # The mane: a ragged dark crest down the neck, and a forelock.
    crest = [(0.0, 1.97, -1.33), (0.0, 1.9, -1.22), (0.0, 1.72, -1.02), (0.0, 1.53, -0.82), (0.0, 1.43, -0.66)]
    for a, b in zip(crest, crest[1:]):
        for side in (-1, 1):
            m.poly([a, b, (side * 0.14, b[1] - 0.26, b[2] - 0.05), (side * 0.12, a[1] - 0.24, a[2] - 0.05)], "horse_hide", BLACK,
                   facing=(side, 0.3, 0.0))
    return m.build(smooth=True, origin=WITHERS, parent=parent)


def tail(parent):
    m = porter.Mesh("Tail")
    m.tube([(0.0, 1.34, 0.9), (0.0, 1.22, 1.02), (0.0, 0.9, 1.06), (0.0, 0.58, 1.02), (0.0, 0.46, 1.0)], [0.05, 0.075, 0.09, 0.07, 0.02],
           5, "horse_hide", BLACK, squash=(0.8, 1.0))
    return m.build(smooth=True, origin=DOCK, parent=parent)


def leg(name, joint, lower, side, hind, parent):
    """One leg: the upper part about its joint, the cannon and hoof hung from it."""
    jx, jy, jz = joint[0] * side, joint[1], joint[2]
    lx, ly, lz = lower[0] * side, lower[1], lower[2]
    up = porter.Mesh("Leg" + name)
    if hind:
        up.tube([(jx, jy + 0.12, jz - 0.05), (jx, jy - 0.2, jz - 0.02), (lx, ly + 0.08, lz - 0.04), (lx, ly - 0.04, lz)],
                [0.19, 0.17, 0.09, 0.07], 6, "horse_hide", [BAY, BAY, BAY_DARK, BAY_DARK], squash=(0.62, 1.0))
    else:
        up.tube([(jx, jy + 0.14, jz + 0.02), (jx, jy - 0.18, jz), (lx, ly + 0.06, lz), (lx, ly - 0.04, lz)],
                [0.15, 0.12, 0.075, 0.065], 6, "horse_hide", [BAY, BAY, BAY_DARK, BAY_DARK], squash=(0.7, 1.0))
    upper = up.build(smooth=True, origin=(jx, jy, jz), parent=parent)
    lo = porter.Mesh("Shin" + name)
    foot_z = lz - (0.22 if hind else -0.02)
    lo.tube([(lx, ly + 0.02, lz), (lx, 0.3, foot_z + (0.05 if hind else 0.0)), (lx, 0.14, foot_z), (lx, 0.1, foot_z - 0.02), (lx, 0.0, foot_z - 0.05)],
            [0.06, 0.048, 0.055, 0.07, 0.085], 6, "horse_hide", [BAY_DARK, BLACK, BLACK, HOOF, HOOF], caps=True)
    lo.build(smooth=True, origin=(lx, ly, lz), parent=upper)
    return upper


def main():
    porter.reset(9)
    b = body()
    neck(b)
    tail(b)
    for name, joint, lower, side, hind in (("FL", SHOULDER, KNEE, -1, False), ("FR", SHOULDER, KNEE, 1, False),
                                           ("HL", HIP, HOCK, -1, True), ("HR", HIP, HOCK, 1, True)):
        leg(name, joint, lower, side, hind, b)
    porter.export("chr_horse")


if __name__ == "__main__":
    main()
