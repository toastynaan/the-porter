"""A two-wheeled cart of the 1420s, the kind a carter drove into London: a
plank bed between ladder sides, a headboard, two tall spoked wheels on one
axle, and a pair of shafts for one horse. The carter's wagon on the road in
(night 0) and the cart with the body on it are both this cart.

It faces -Z (the shafts and the horse in front); the origin is on the ground
under the middle of the bed. The bed's top is 0.81 m up, where the scenes'
seats and floor already are. The wheels are their own objects (WheelL,
WheelR), turning about the axle, so a script can roll them.

Materials: wood_cart (the planks and frame), iron_cart (tyres, hub bands).

Run: tools/build.sh prop_cart
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
from mathutils import Vector

BED_HALF = 0.72       # half the bed's width
BED_Z = (-1.35, 1.3)   # its front and back
BED_TOP = 0.81
AXLE_Z = 0.15
WHEEL_R = 0.62
WHEEL_X = 0.9
WOOD = (0.86, 0.84, 0.8, 1.0)
WORN = (0.62, 0.6, 0.56, 1.0)
DARK = (0.4, 0.38, 0.36, 1.0)


def beam(m, a, b, w, h, color=WOOD):
    """A squared timber from `a` to `b` (x, y, z), `w` wide and `h` deep."""
    va, vb = Vector(a), Vector(b)
    along = vb - va
    length = along.length
    side = along.cross(Vector((0.0, 1.0, 0.0)))
    side = side.normalized() if side.length > 1e-5 else Vector((1.0, 0.0, 0.0))
    up = side.cross(along).normalized()
    side *= w * 0.5
    up *= h * 0.5
    corners = ((-1, -1), (1, -1), (1, 1), (-1, 1))
    r0 = [va + side * i + up * j for i, j in corners]
    r1 = [vb + side * i + up * j for i, j in corners]
    mid = (va + vb) * 0.5
    for k in range(4):
        t = (k + 1) % 4
        quad = [r0[k], r0[t], r1[t], r1[k]]
        out = sum(quad, Vector()) / 4.0 - mid
        m.poly([tuple(p) for p in quad], "wood_cart", color, [(0.0, 0.0), (0.1, 0.0), (0.1, length), (0.0, length)], facing=tuple(out))
    m.poly([tuple(p) for p in r0], "wood_cart", DARK, facing=tuple(-along))
    m.poly([tuple(p) for p in r1], "wood_cart", DARK, facing=tuple(along))


def body(m):
    z0, z1 = BED_Z
    # The bed: planks side by side, none quite like the next.
    planks = 6
    for i in range(planks):
        x0 = -BED_HALF + i * (2 * BED_HALF / planks)
        x1 = x0 + 2 * BED_HALF / planks - 0.012
        shade = 0.74 + 0.16 * ((i * 37) % 5) / 4.0
        sag = 0.006 * ((i * 53) % 3)
        m.box((x0, BED_TOP - 0.05 - sag, z0), (x1, BED_TOP - sag, z1 + 0.02 * ((i * 29) % 3)), "wood_cart",
              (shade * 0.6, shade * 0.58, shade * 0.55, 1.0), (shade, shade * 0.98, shade * 0.94, 1.0), faces="xXzZyY")
    # The frame under it: two long sole pieces and three cross pieces.
    for x in (-BED_HALF + 0.1, BED_HALF - 0.1):
        beam(m, (x, BED_TOP - 0.11, z0 - 0.05), (x, BED_TOP - 0.11, z1 + 0.05), 0.09, 0.12, WORN)
    for z in (z0 + 0.1, AXLE_Z, z1 - 0.1):
        beam(m, (-BED_HALF - 0.04, BED_TOP - 0.2, z), (BED_HALF + 0.04, BED_TOP - 0.2, z), 0.09, 0.09, DARK)
    # The axle, standing out to the wheels.
    beam(m, (-WHEEL_X - 0.1, WHEEL_R, AXLE_Z), (WHEEL_X + 0.1, WHEEL_R, AXLE_Z), 0.11, 0.11, DARK)
    for x in (-BED_HALF + 0.1, BED_HALF - 0.1):
        beam(m, (x, WHEEL_R + 0.03, AXLE_Z), (x, BED_TOP - 0.16, AXLE_Z), 0.1, 0.12, DARK)
    # Ladder sides: a top rail and a mid rail on uprights that lean out a little.
    for side in (-1, 1):
        x = side * (BED_HALF - 0.03)
        out = side * 0.1
        for i in range(6):
            z = z0 + 0.08 + i * (z1 - z0 - 0.16) / 5.0
            beam(m, (x, BED_TOP - 0.02, z), (x + out, BED_TOP + 0.5, z), 0.045, 0.045, WORN)
        beam(m, (x + out, BED_TOP + 0.48, z0 - 0.06), (x + out, BED_TOP + 0.48, z1 + 0.1), 0.06, 0.06)
        beam(m, (x + out * 0.5, BED_TOP + 0.24, z0), (x + out * 0.5, BED_TOP + 0.24, z1), 0.04, 0.05, WORN)
    # The headboard, three planks, and the carter's seat board across behind it.
    for i in range(3):
        y = BED_TOP + 0.02 + i * 0.17
        m.box((-BED_HALF + 0.02, y, z0 - 0.02), (BED_HALF - 0.02, y + 0.16, z0 + 0.02), "wood_cart", WORN, WOOD, faces="xXzZyY")
    m.box((-BED_HALF - 0.06, BED_TOP + 0.27, z0 + 0.22), (BED_HALF + 0.06, BED_TOP + 0.31, z0 + 0.52), "wood_cart", WORN, WOOD, faces="xXzZyY")
    # The shafts: from under the bed forward and up to the horse's shoulder.
    for side in (-1, 1):
        beam(m, (side * 0.5, BED_TOP - 0.12, z0 + 0.3), (side * 0.43, BED_TOP + 0.1, z0 - 1.0), 0.07, 0.08)
        beam(m, (side * 0.43, BED_TOP + 0.1, z0 - 1.0), (side * 0.4, BED_TOP + 0.26, z0 - 2.45), 0.065, 0.07)
    # A stake at the headboard's corner, with an arm to hang a lantern from.
    beam(m, (BED_HALF - 0.02, BED_TOP, z0 + 0.03), (BED_HALF + 0.02, BED_TOP + 1.12, z0 + 0.03), 0.05, 0.05, WORN)
    beam(m, (BED_HALF + 0.02, BED_TOP + 1.08, z0 + 0.03), (BED_HALF + 0.02, BED_TOP + 1.08, z0 + 0.2), 0.035, 0.035, DARK)
    # A prop leg under the front, for when the horse is out of the shafts.
    beam(m, (0.0, BED_TOP - 0.2, z0 + 0.12), (0.0, 0.34, z0 - 0.08), 0.06, 0.06, DARK)


def wheel(name, x):
    """A spoked wheel in the plane of y and z, about its hub."""
    m = porter.Mesh(name)
    half = 0.04
    sides = 14
    felloe = 0.085  # how deep the wooden rim is
    for k in range(sides):
        a0 = math.tau * k / sides
        a1 = math.tau * (k + 1) / sides
        ring = lambda r, a: (math.cos(a) * r, math.sin(a) * r)
        (oy0, oz0), (oy1, oz1) = ring(WHEEL_R, a0), ring(WHEEL_R, a1)
        (iy0, iz0), (iy1, iz1) = ring(WHEEL_R - felloe, a0), ring(WHEEL_R - felloe, a1)
        mid = (math.cos((a0 + a1) * 0.5), math.sin((a0 + a1) * 0.5))
        # The iron tyre, the rim's two faces, and its inside.
        m.poly([(x - half, WHEEL_R + oy0, AXLE_Z + oz0), (x + half, WHEEL_R + oy0, AXLE_Z + oz0),
                (x + half, WHEEL_R + oy1, AXLE_Z + oz1), (x - half, WHEEL_R + oy1, AXLE_Z + oz1)], "iron_cart",
               (0.5, 0.5, 0.5, 1.0), facing=(0, mid[0], mid[1]))
        for s in (-1, 1):
            m.poly([(x + s * half, WHEEL_R + oy0, AXLE_Z + oz0), (x + s * half, WHEEL_R + oy1, AXLE_Z + oz1),
                    (x + s * half, WHEEL_R + iy1, AXLE_Z + iz1), (x + s * half, WHEEL_R + iy0, AXLE_Z + iz0)], "wood_cart",
                   WORN, facing=(s, 0, 0))
        m.poly([(x - half, WHEEL_R + iy0, AXLE_Z + iz0), (x + half, WHEEL_R + iy0, AXLE_Z + iz0),
                (x + half, WHEEL_R + iy1, AXLE_Z + iz1), (x - half, WHEEL_R + iy1, AXLE_Z + iz1)], "wood_cart", DARK,
               facing=(0, -mid[0], -mid[1]))
    for k in range(10):
        a = math.tau * k / 10 + 0.1
        cy, cz = math.cos(a), math.sin(a)
        beam(m, (x, WHEEL_R + cy * 0.09, AXLE_Z + cz * 0.09), (x, WHEEL_R + cy * (WHEEL_R - felloe + 0.01), AXLE_Z + cz * (WHEEL_R - felloe + 0.01)),
             0.045, 0.05, WOOD)
    # The hub: a short fat drum, banded.
    m.tube([(x - 0.11, WHEEL_R, AXLE_Z), (x - 0.07, WHEEL_R, AXLE_Z), (x + 0.07, WHEEL_R, AXLE_Z), (x + 0.11, WHEEL_R, AXLE_Z)],
           [0.07, 0.1, 0.1, 0.07], 8, "wood_cart", DARK, caps=True)
    return m.build(origin=(x, WHEEL_R, AXLE_Z))


def main():
    porter.reset(3)
    m = porter.Mesh("Cart")
    body(m)
    m.build()
    wheel("WheelL", -WHEEL_X)
    wheel("WheelR", WHEEL_X)
    porter.export("prop_cart")


if __name__ == "__main__":
    main()
