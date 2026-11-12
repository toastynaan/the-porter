"""The small things of the Cross Keys (night 0, and any dusk the porter
goes in), to make its rooms warm and lived in. Each is its own model
(art/models/prop_inn_<name>.glb) with a scene of its own
(game/world/props/prop_inn_<name>.tscn); game/world/street/env_inn.tscn
sets them out under its `Dressing` node.

Each stands on the floor at its origin, its front toward -z. Those that go
against a wall (`pegs`, `pegs_room`, `broom`, `boots`, `hanging`) have the
wall at z = 0 and stand out from it toward -z; `hanging` hangs from the
ceiling of the taproom (2.8 m).

The taproom:
- tankard: a staved oak ale cup, 15 cm high (game/world/props/tankard.tscn).
- rushes, rushes_strip: rushes and straw strewn on the boards, with a
  little meadowsweet in them: a patch, and a strip along a wall.
- sheepskin: a fleece on the flags before the fire.
- hearth_basket: a withy basket of logs, a bundle of kindling and a pail of
  water, by the hearth.
- pot: an iron pot of pottage on its three legs, warming at the hearth's
  edge, a ladle in it.
- dog: the house's dog asleep, curled nose to tail.
- trencher: a board with a loaf, a wedge of cheese and a knife.
- jug_cups: a jug and two cups.
- hanging: a ham, a string of onions and bunches of herbs from the beams.
- cask_side: a cask on its side, chocked, with sacks against it.
- broom: a besom leant on a wall.
- pegs: a peg board inside the door: a hat, a hood, a satchel.
- boots: a pair of boots and a staff at the stair's foot.
The porter's room:
- chest: a small iron-strapped chest, a blanket folded on it.
- washstand: a stool with a basin, a jug by it.
- pegs_room: two pegs with a linen towel and a straw hat.
The loft:
- bundle: a lodger's blanket roll, his scrip and shoes.
- pack: a lodger's sack, his staff and hat.
- pallet: a straw pallet on the floor, slept on (the loft, and the top
  floor outside the porter's room).

No collision here: the scenes give a hidden Block to those big enough to
walk into.

Run: tools/build.sh prop_inn   (one: ... -- inn_dog)
"""
import math
import os
import random
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import env_inn_rooms as rooms
import prop_abbey_stores as st
import props
from porter import fbm, lerp, smoothstep
from props import CLOTH, IRON, IRON_C, OAK, OAK_DARK, PAINT, PINE, WOOD, beam, plank, rgba, tone

TAU = math.tau
BLACK_IRON = (0.42, 0.4, 0.38, 1.0)
STAVE = (0.5, 0.42, 0.33)
BARK = (0.26, 0.22, 0.18)
FLEECE = (0.1, 0.09, 0.068)
CRUST = (0.045, 0.03, 0.016)
CORD = (0.07, 0.055, 0.035)
FELT = (0.026, 0.022, 0.018)
WALL = rooms.Wall("z", 0.0, -1)


def staved(m, at, profile, staves, colour, inside=0.007, floor=0.02, rim=True):
    """A staved vessel (a cup, a pail) standing on `at`: `profile` is
    (height, radius) pairs up its outside; each stave its own tone; open,
    with its inside drawn down to `floor`."""
    x0, y0, z0 = at
    for i in range(staves):
        a0, a1 = TAU * i / staves + 0.003, TAU * (i + 1) / staves - 0.003
        c = tone(colour, 0.16)
        u0 = random.random()
        for (ya, ra), (yb, rb) in zip(profile, profile[1:]):
            pts = [(x0 + math.cos(a1) * ra, y0 + ya, z0 + math.sin(a1) * ra), (x0 + math.cos(a0) * ra, y0 + ya, z0 + math.sin(a0) * ra),
                   (x0 + math.cos(a0) * rb, y0 + yb, z0 + math.sin(a0) * rb), (x0 + math.cos(a1) * rb, y0 + yb, z0 + math.sin(a1) * rb)]
            mid = (a0 + a1) * 0.5
            uvs = [(u0 + 0.03, ya * 2.0), (u0, ya * 2.0), (u0, yb * 2.0), (u0 + 0.03, yb * 2.0)]
            m.poly(pts, WOOD, c, uvs=uvs, facing=(math.cos(mid), 0.0, math.sin(mid)))
    top, r_top = profile[-1]
    ri = r_top - inside
    n = staves
    # The rim, the inside, and its floor in shadow.
    for i in range(n):
        a0, a1 = TAU * i / n, TAU * (i + 1) / n
        mid = (a0 + a1) * 0.5
        if rim:
            m.poly([(x0 + math.cos(a0) * ri, y0 + top, z0 + math.sin(a0) * ri), (x0 + math.cos(a1) * ri, y0 + top, z0 + math.sin(a1) * ri),
                    (x0 + math.cos(a1) * r_top, y0 + top, z0 + math.sin(a1) * r_top), (x0 + math.cos(a0) * r_top, y0 + top, z0 + math.sin(a0) * r_top)], WOOD,
                   rgba(colour, 1.1), facing=(0, 1, 0))
        rb = profile[0][1] - inside
        m.poly([(x0 + math.cos(a0) * ri, y0 + top, z0 + math.sin(a0) * ri), (x0 + math.cos(a1) * ri, y0 + top, z0 + math.sin(a1) * ri),
                (x0 + math.cos(a1) * rb, y0 + floor, z0 + math.sin(a1) * rb), (x0 + math.cos(a0) * rb, y0 + floor, z0 + math.sin(a0) * rb)], WOOD,
               [rgba(colour, 0.6), rgba(colour, 0.6), rgba(colour, 0.25), rgba(colour, 0.25)], facing=(-math.cos(mid), 0.0, -math.sin(mid)))
    rb = profile[0][1] - inside
    m.poly([(x0 + math.cos(TAU * i / n) * rb, y0 + floor, z0 + math.sin(TAU * i / n) * rb) for i in range(n)], WOOD, rgba(colour, 0.2), facing=(0, 1, 0))
    m.poly([(x0 + math.cos(TAU * i / n) * profile[0][1], y0 + 0.001, z0 + math.sin(TAU * i / n) * profile[0][1]) for i in range(n)], WOOD, rgba(colour, 0.5),
           facing=(0, -1, 0))


def hoop(m, at, y, r, wide=0.012, colour=BLACK_IRON, mat=IRON, n=12):
    x0, y0, z0 = at
    for i in range(n):
        a0, a1 = TAU * i / n, TAU * (i + 1) / n
        mid = (a0 + a1) * 0.5
        m.poly([(x0 + math.cos(a0) * r, y0 + y - wide * 0.5, z0 + math.sin(a0) * r), (x0 + math.cos(a1) * r, y0 + y - wide * 0.5, z0 + math.sin(a1) * r),
                (x0 + math.cos(a1) * r, y0 + y + wide * 0.5, z0 + math.sin(a1) * r), (x0 + math.cos(a0) * r, y0 + y + wide * 0.5, z0 + math.sin(a0) * r)], mat, colour,
               facing=(math.cos(mid), 0.0, math.sin(mid)))


def strands(m, n, place, colour=props.STRAW, long=(0.14, 0.3), wide=(0.005, 0.011), lift=0.006, rng=None, bright=(0.9, 1.7)):
    """`n` stalks lying about: `place(rng)` gives each one's (x, z), or None to skip it."""
    rng = rng or random.Random(1)
    made = tries = 0
    while made < n and tries < n * 20:
        tries += 1
        at = place(rng)
        if at is None:
            continue
        x, z = at
        a = rng.uniform(0.0, math.pi)
        length, w = rng.uniform(*long), rng.uniform(*wide)
        dx, dz = math.cos(a) * length * 0.5, math.sin(a) * length * 0.5
        px, pz = -math.sin(a) * w, math.cos(a) * w
        y = 0.004 + rng.uniform(0.0, lift)
        bend = rng.uniform(-0.02, 0.02)
        k = rng.uniform(*bright)
        c = (colour[0] * k, colour[1] * k, colour[2] * k * 0.92, 1.0)
        mx, mz = x + px * bend * 40.0, z + pz * bend * 40.0
        m.poly([(x - dx - px, y, z - dz - pz), (mx - px, y + 0.004, mz - pz), (mx + px, y + 0.006, mz + pz), (x - dx + px, y + 0.002, z - dz + pz)], PAINT, c, facing=(0, 1, 0))
        m.poly([(mx - px, y + 0.004, mz - pz), (x + dx - px, y, z + dz - pz), (x + dx + px, y + 0.002, z + dz + pz), (mx + px, y + 0.006, mz + pz)], PAINT, c, facing=(0, 1, 0))
        made += 1


def sprig_flower(m, x, z, rng):
    """Meadowsweet strewn with the rushes: a stalk and a cream head."""
    a = rng.uniform(0.0, TAU)
    length = rng.uniform(0.12, 0.2)
    tip = (x + math.cos(a) * length, 0.012, z + math.sin(a) * length)
    m.tube([(x, 0.008, z), tip], [0.003, 0.003], 3, PAINT, (0.03, 0.035, 0.016, 1.0))
    for _ in range(4):
        q = (tip[0] + rng.uniform(-0.025, 0.025), 0.014 + rng.uniform(0.0, 0.01), tip[2] + rng.uniform(-0.025, 0.025))
        m.tube([q, (q[0], q[1] + 0.012, q[2])], [0.012, 0.006], 5, PAINT, (0.1, 0.092, 0.07, 1.0), caps=True)


# ---------------------------------------------------------------- the taproom

def tankard(p):
    """A staved oak cup bound with two iron hoops, its handle a stave left long. 15 cm high, 6 cm across at the foot."""
    profile = [(0.0, 0.059), (0.006, 0.06), (0.15, 0.0545)]
    staved(p.hard, (0.0, 0.0, 0.0), profile, 11, STAVE, inside=0.007, floor=0.02)
    hoop(p.hard, (0.0, 0.0, 0.0), 0.024, 0.0605, wide=0.012)
    hoop(p.hard, (0.0, 0.0, 0.0), 0.124, 0.0565, wide=0.012)
    beam(p.hard, (0.055, 0.137, 0.0), (0.086, 0.137, 0.0), 0.022, 0.016, tone(STAVE, 0.05), up=(0, 1, 0))
    beam(p.hard, (0.083, 0.144, 0.0), (0.083, 0.05, 0.0), 0.022, 0.014, tone(STAVE, 0.05), up=(1, 0, 0))
    beam(p.hard, (0.086, 0.054, 0.0), (0.057, 0.044, 0.0), 0.022, 0.014, tone(STAVE, 0.05), up=(0, 1, 0))


def rushes(p):
    """A patch of strewn rushes and straw, 2.4 x 1.4 m, thick in the middle and thinning out."""
    rng = random.Random(5)

    def place(r):
        x, z = r.uniform(-1.2, 1.2), r.uniform(-0.7, 0.7)
        d = (x / 1.2) ** 2 + (z / 0.7) ** 2
        return (x, z) if d < 1.0 and r.random() < 1.0 - d ** 0.7 else None

    strands(p.hard, 380, place, rng=rng)
    strands(p.hard, 60, place, colour=(0.035, 0.034, 0.018), long=(0.2, 0.36), rng=rng)
    for _ in range(7):
        at = place(rng)
        if at:
            sprig_flower(p.soft, at[0], at[1], rng)


def rushes_strip(p):
    """Rushes along a wall's foot (the wall at z = 0): a strip 1.8 m long."""
    rng = random.Random(9)

    def place(r):
        x, z = r.uniform(-0.9, 0.9), -r.uniform(0.0, 0.55) ** 1.3
        return (x, z) if r.random() < 1.0 - abs(x / 0.9) ** 3 else None

    strands(p.hard, 200, place, rng=rng)
    strands(p.hard, 30, place, colour=(0.035, 0.034, 0.018), long=(0.2, 0.34), rng=rng)
    for _ in range(3):
        at = place(rng)
        if at:
            sprig_flower(p.soft, at[0], at[1], rng)


def sheepskin(p):
    """A fleece, its legs and neck ragged, about 1.1 x 0.75 m."""
    lobes = ((0.0, 0.1, 0.18), (0.75, 0.13, 0.13), (-0.75, 0.12, 0.13), (math.pi - 0.75, 0.14, 0.13), (math.pi + 0.8, 0.12, 0.13), (math.pi, 0.06, 0.12))

    def radius(a):
        r = 1.0 / math.sqrt((math.cos(a) / 0.5) ** 2 + (math.sin(a) / 0.33) ** 2)
        for at, size, width in lobes:
            d = math.atan2(math.sin(a - at), math.cos(a - at))
            r += size * math.exp(-(d / width) ** 2)
        return r * (1.0 + 0.07 * fbm(math.cos(a) * 3.0, math.sin(a) * 3.0, 1.0, 3, 2.0))

    def f(u, v):
        a = u * TAU
        r = radius(a) * v
        x, z = math.cos(a) * r, math.sin(a) * r
        y = 0.04 * (1.0 - v ** 3) * (1.0 + 0.35 * fbm(x, z, 11.0, 3, 4.0)) + 0.004
        return (x, y, z)

    def c(u, v):
        a = u * TAU
        x, z = math.cos(a) * v, math.sin(a) * v
        return rgba(FLEECE, (0.7 + 0.35 * fbm(x, z, 6.0, 3, 1.0)) * (1.0 - 0.3 * v ** 4))

    props.sheet(p.soft, f, 36, 6, CLOTH, c)
    # Tufts standing out of the wool.
    rng = random.Random(3)
    for _ in range(40):
        a, v = rng.uniform(0.0, TAU), rng.uniform(0.0, 0.85)
        x, y, z = f(a / TAU, v)
        p.soft.tube([(x, y - 0.004, z), (x + rng.uniform(-0.02, 0.02), y + 0.018, z + rng.uniform(-0.02, 0.02))], [0.016, 0.004], 4, CLOTH, rgba(FLEECE, rng.uniform(0.8, 1.15)))


def hearth_basket(p):
    """By the hearth (0.9 x 0.45 m, its back to the wall at +z): a basket of logs, kindling, a pail of water."""
    hard, soft = p.hard, p.soft
    # The basket: big, no handle, logs stood up in it.
    st.basket(soft, (-0.2, 0.0, 0.0), 0.22, 0.36, handle=False, colour=(0.07, 0.054, 0.03))
    rng = random.Random(4)
    for i in range(7):
        a = TAU * i / 7 + rng.uniform(-0.2, 0.2)
        d = 0.09 if i else 0.0
        foot = (-0.2 + math.cos(a) * d, 0.06, math.sin(a) * d)
        lean = 0.06 + 0.04 * d / 0.09
        top = (foot[0] + math.cos(a) * lean, 0.48 + rng.uniform(0.0, 0.1), foot[2] + math.sin(a) * lean)
        r = rng.uniform(0.04, 0.055)
        hard.tube([foot, top], [r, r * 0.95], 5, WOOD, rgba(BARK, rng.uniform(0.85, 1.15)))
        hard.poly([(top[0] + math.cos(TAU * k / 5) * r * 0.95, top[1], top[2] + math.sin(TAU * k / 5) * r * 0.95) for k in range(5)], WOOD, rgba(PINE, 0.7),
                  facing=(top[0] - foot[0], top[1] - foot[1], top[2] - foot[2]))
    # The kindling, a bundle of sticks tied twice, lying before them.
    for i in range(14):
        a, d = rng.uniform(0.0, TAU), rng.uniform(0.0, 0.045)
        y, z = 0.05 + math.sin(a) * d, -0.15 + math.cos(a) * d
        hard.tube([(-0.5 + rng.uniform(0.0, 0.05), y, z), (0.0 - rng.uniform(0.0, 0.06), y + rng.uniform(-0.01, 0.01), z + rng.uniform(-0.02, 0.02))],
                  [0.008, 0.007], 4, WOOD, rgba(BARK, rng.uniform(0.9, 1.3)))
    for x in (-0.38, -0.14):
        props.rope(soft, [(x, 0.05 + 0.055 * math.sin(a), -0.15 + 0.055 * math.cos(a)) for a in [TAU * k / 8 for k in range(9)]], r=0.006, colour=CORD)
    # The pail, water standing in it, a rope for a handle.
    at = (0.27, 0.0, 0.02)
    staved(hard, at, [(0.0, 0.12), (0.26, 0.14)], 12, STAVE, inside=0.01, floor=0.03)
    hoop(hard, at, 0.05, 0.124, wide=0.02, colour=rgba((0.3, 0.24, 0.16)), mat=WOOD)
    hoop(hard, at, 0.22, 0.138, wide=0.02, colour=rgba((0.3, 0.24, 0.16)), mat=WOOD)
    hard.poly([(at[0] + math.cos(TAU * k / 12) * 0.128, 0.2, at[2] + math.sin(TAU * k / 12) * 0.128) for k in range(12)], "window_dark", (0.0, 0.0, 0.0, 1.0),
              facing=(0, 1, 0))
    props.rope(soft, [(at[0] - 0.14, 0.22, at[2]), (at[0] - 0.12, 0.33, at[2] - 0.04), (at[0], 0.37, at[2] - 0.06), (at[0] + 0.12, 0.33, at[2] - 0.04), (at[0] + 0.14, 0.22, at[2])],
               r=0.007, colour=CORD)


def pot(p):
    """An iron pot of pottage on its legs (0.36 m across), a ladle in it."""
    top = st.cauldron(p.hard, p.soft, (0.0, 0.08, 0.0), r=0.17, h=0.24)
    del top
    n = 12
    p.soft.poly([(math.cos(TAU * k / n) * 0.148, 0.29, math.sin(TAU * k / n) * 0.148) for k in range(n)], PAINT, (0.04, 0.026, 0.012, 1.0), facing=(0, 1, 0))
    # The ladle: a wooden one, its bowl under the pottage, its handle on the rim.
    p.hard.tube([(-0.03, 0.27, 0.02), (0.1, 0.36, 0.06), (0.25, 0.45, 0.1)], [0.012, 0.011, 0.01], 5, WOOD, rgba(PINE, 0.85))


def dog(p):
    """The house dog, asleep, curled with its head laid over its haunch: about 0.6 m across."""
    m = p.soft
    coat = (0.058, 0.04, 0.025)
    R = 0.19

    def ring(a, r, y):
        a = math.radians(a)
        return (math.cos(a) * r, y, math.sin(a) * r)

    def col(t, k=1.0):
        return rgba(coat, k * (0.85 + 0.3 * fbm(t * 4.0, 1.0, 1.0, 2, 5.0)))

    # The body, round the curl from the rump to the shoulders.
    angles = (205, 240, 290, 340, 30, 75, 105)
    radii = [0.09, 0.115, 0.125, 0.128, 0.12, 0.1, 0.075]
    heights = [0.1, 0.12, 0.125, 0.125, 0.12, 0.105, 0.09]
    m.tube([ring(a, R, y) for a, y in zip(angles, heights)], radii, 9, CLOTH, [col(i / 6.0) for i in range(7)], caps=True, squash=(1.0, 0.85))
    # The haunch, raised over the rump.
    m.tube([ring(215, R * 0.85, 0.13), ring(245, R * 1.05, 0.15), ring(270, R * 1.15, 0.1)], [0.08, 0.1, 0.06], 8, CLOTH, col(0.3, 0.95), caps=True)
    # Forepaws out before the chest, under the chin.
    for d in (0.0, 0.05):
        m.tube([ring(95 + d * 200, R * 0.95, 0.03), ring(125 + d * 150, R * 0.62, 0.028), ring(150 + d * 100, R * 0.5, 0.026)], [0.03, 0.026, 0.024], 6, CLOTH,
               col(0.5 + d, 0.85), caps=True)
    # The head, laid across the haunch: neck, skull, a long muzzle, a dark nose.
    neck = ring(110, R * 0.98, 0.1)
    skull = ring(150, R * 0.92, 0.17)
    muzzle = ring(178, R * 0.98, 0.165)
    nose = ring(194, R * 1.03, 0.155)
    m.tube([neck, skull, muzzle, nose], [0.068, 0.068, 0.04, 0.02], 8, CLOTH, [col(0.8), col(0.9), rgba(coat, 0.8), rgba(coat, 0.25)], caps=True, squash=(1.0, 0.85))
    # The ears, flopped down each side of the skull.
    for side in (-1.0, 1.0):
        e = ring(146, R * 0.92 + side * 0.055, 0.205)
        tip = ring(152, R * 0.92 + side * 0.09, 0.13)
        back = ring(136, R * 0.92 + side * 0.06, 0.2)
        for k, facing in ((0.6, (0.0, 1.0, 0.0)), (0.4, (0.0, -1.0, 0.0))):
            m.poly([e, back, tip], CLOTH, rgba(coat, k), facing=(facing[0] + side * 0.6, facing[1], facing[2]))
    # The tail, round the outside of the curl.
    m.tube([ring(200, R * 1.05, 0.08), ring(185, R * 1.45, 0.04), ring(160, R * 1.55, 0.03), ring(135, R * 1.45, 0.03)], [0.035, 0.03, 0.022, 0.012], 6, CLOTH,
           col(0.1, 0.8), caps=True)


def trencher(p):
    """A board with a loaf, a wedge of cheese and a knife on it (0.36 m across)."""
    board = [(math.cos(TAU * i / 12) * 0.18, math.sin(TAU * i / 12) * 0.16) for i in range(12)]
    props.slab(p.hard, board, "y", 0.0, 0.022, tone(OAK, 0.05))
    st.lathe(p.soft, (-0.06, 0.022, 0.0), [(0.0, 0.08), (0.025, 0.088), (0.05, 0.078), (0.07, 0.05), (0.08, 0.02), (0.082, 0.0)], 10, PAINT,
             [rgba(CRUST, 0.7), rgba(CRUST), rgba(CRUST, 1.1), rgba(CRUST, 1.2), rgba(CRUST, 1.1), rgba(CRUST, 0.9)])
    st.cheese(p.soft, (0.09, 0.022, 0.06), r=0.065, h=0.05)
    k = props.Placed(p.hard, (0.06, 0.024, -0.03), -0.5)
    plank(k, (-0.08, 0.0, -0.007), (0.01, 0.013, 0.007), tone(OAK_DARK), along="x")
    k.poly([(0.01, 0.006, -0.008), (0.13, 0.006, -0.002), (0.01, 0.006, 0.008)], IRON, IRON_C, facing=(0, 1, 0))


def jug_cups(p):
    """A jug and two cups (0.35 m across)."""
    st.jug(p.soft, (0.0, 0.0, 0.0), 2.4, 0.0, 0.95)
    for x, z in ((0.15, -0.08), (-0.12, -0.12)):
        props.pot(p.soft, (x, 0.0, z), [(0.0, 0.028), (0.045, 0.034), (0.09, 0.038)], colour=(0.045, 0.035, 0.025), sides=8)


def hanging(p):
    """From the taproom's beams (the ceiling 2.8 m up): a ham, a string of
    onions, three bunches of herbs, each on a cord from an iron hook, all
    above 2 m. 1.2 m along x."""
    soft, hard = p.soft, p.hard
    top = 2.8
    for x in (-0.45, 0.0, 0.35, 0.55, -0.2):
        rooms.hook(hard, x, top, 0.0, 0.05)
    # The ham: a smoked leg hung by its hock.
    y = top - 0.12
    props.rope(soft, [(-0.45, top - 0.07, 0.0), (-0.45, y, 0.0)], r=0.005, colour=CORD)
    ham = (0.032, 0.018, 0.011)
    profile = [(0.0, 0.022), (0.08, 0.035), (0.2, 0.07), (0.34, 0.1), (0.45, 0.1), (0.53, 0.075), (0.58, 0.03)]
    soft.tube([(-0.45 + 0.01 * t, y - d, 0.01 * t) for t, (d, _r) in enumerate(profile)], [r for _d, r in profile], 9, PAINT,
              [rgba(ham, 0.8), rgba(ham, 0.9), rgba(ham), rgba(ham, 1.15), rgba(ham, 1.1), rgba(ham, 0.95), rgba((0.07, 0.055, 0.035))], caps=True, squash=(1.0, 0.8))
    # The onions, plaited on their dried tops.
    props.rope(soft, [(0.0, top - 0.07, 0.0), (0.0, top - 0.6, 0.0)], r=0.008, colour=(0.08, 0.06, 0.03))
    rng = random.Random(6)
    for i in range(9):
        yy = top - 0.18 - i * 0.05
        a = i * 2.2
        c = (0.075, 0.045, 0.02) if i % 4 else (0.04, 0.016, 0.013)
        x, z = math.cos(a) * 0.04, math.sin(a) * 0.04
        soft.tube([(x * 0.4, yy + 0.03, z * 0.4), (x, yy, z), (x * 1.1, yy - 0.04, z * 1.1), (x * 1.0, yy - 0.075, z * 1.0)], [0.006, 0.03, 0.036, 0.008], 7, PAINT,
                  rgba(c, rng.uniform(0.85, 1.15)), caps=True)
    # Herbs, hung head down.
    for x, long, g in ((0.35, 0.3, (0.03, 0.036, 0.018)), (0.55, 0.26, (0.045, 0.04, 0.02)), (-0.2, 0.32, (0.028, 0.032, 0.02))):
        props.rope(soft, [(x, top - 0.07, 0.0), (x, top - 0.16, 0.0)], r=0.004, colour=CORD)
        t = top - 0.16
        soft.tube([(x, t, 0.0), (x, t - 0.05, 0.0), (x + 0.005, t - long * 0.5, 0.0), (x, t - long * 0.9, 0.0), (x, t - long, 0.0)],
                  [0.006, 0.014, 0.045, 0.06, 0.02], 6, PAINT, [rgba(g, 0.7), rgba(g, 0.8), rgba(g), rgba(g, 1.1), rgba(g, 0.8)], caps=True)


def cask_side(p):
    """A cask on its side, chocked, along z (its head at -z; 0.6 x 0.9 m), a full sack leant on it and one on the floor by it."""
    hard, soft = p.hard, p.soft
    rooms.lying_cask(hard, soft, 0.0, 0.305, 0.45, 0.88, tap=False)
    for z in (-0.25, 0.25):
        for sx in (-1, 1):
            props.slab(hard, [(sx * 0.31, 0.0), (sx * 0.16, 0.0), (sx * 0.31, 0.09)], "z", z - 0.04, z + 0.04, tone(OAK_DARK))
    st.Sack(soft, (0.42, 0.0, -0.05), 1.62, 0.32, 0.8, 0.45, 0.26, seed=2.0, droop=0.03)
    st.Sack(soft, (-0.05, 0.0, -0.7), 0.25, 0.0, 0.7, 0.42, 0.22, seed=3.0)


def broom(p):
    """A besom leant on the wall (z = 0): its head on the floor 0.35 m out."""
    hard = p.hard
    foot, top = (0.0, 0.0, -0.36), (0.02, 1.42, -0.03)
    bind = tuple(foot[k] + (top[k] - foot[k]) * 0.2 for k in range(3))
    hard.tube([bind, top], [0.016, 0.014], 5, WOOD, rgba(PINE, 0.8), caps=True)
    rng = random.Random(2)
    for i in range(22):
        a = TAU * i / 22 + rng.uniform(-0.1, 0.1)
        end = (foot[0] + math.cos(a) * rng.uniform(0.06, 0.11), 0.005, foot[2] + math.sin(a) * rng.uniform(0.02, 0.05) - 0.03)
        start = (bind[0] + math.cos(a) * 0.025, bind[1] + 0.06, bind[2] + math.sin(a) * 0.02)
        hard.tube([start, end], [0.006, 0.004], 3, WOOD, rgba(BARK, rng.uniform(0.7, 1.1)))
    for t in (0.0, 0.05):
        q = (bind[0], bind[1] + t, bind[2] + t * 0.24)
        props.ring(p.soft, q, (0.0, 0.97, 0.25), r=0.035, thick=0.006, colour=rgba((0.08, 0.06, 0.03)), mat=CLOTH)


def boot(m, at, yaw, fallen=False, colour=props.LEATHER):
    """An ankle boot of soft leather, standing (or fallen on its side)."""
    b = props.Placed(m, at, yaw, 1.0, (math.pi * 0.5 if fallen else 0.0))
    y = 0.0 if not fallen else -0.05
    props.turned(b, (0.0, y + 0.035, -0.12), (0.0, y + 0.035, 0.13), [(0.0, 0.014), (0.12, 0.038), (0.6, 0.045), (0.85, 0.047), (1.0, 0.032)], colour, sides=7)
    b.tube([(0.0, y + 0.04, 0.06), (0.0, y + 0.17, 0.075), (0.0, y + 0.2, 0.08)], [0.046, 0.044, 0.05], 7, PAINT, rgba(colour, 0.9))
    b.poly([(math.cos(TAU * k / 7) * 0.044, y + 0.195, 0.08 + math.sin(TAU * k / 7) * 0.044) for k in range(7)], PAINT, (0.005, 0.004, 0.003, 1.0), facing=(0, 1, 0))


def staff(m, a, b, colour=PINE):
    m.tube([a, b], [0.018, 0.016], 5, WOOD, rgba(colour, 0.7), caps=True)


def boots(p):
    """A pair of boots by a wall (z = 0), one fallen, and a staff leant over them."""
    boot(p.soft, (-0.08, 0.0, -0.18), 0.2)
    boot(p.soft, (0.15, 0.05, -0.22), -0.9, fallen=True)
    staff(p.hard, (0.32, 0.0, -0.22), (0.12, 1.5, -0.025))


def hat(m, at, yaw=0.0, tilt=0.0, brim=0.17, crown=0.085, high=0.1, colour=FELT):
    """A felt hat, its crown up, standing on `at` (the brim's middle)."""
    h = props.Placed(m, at, yaw, 1.0, tilt)
    n = 12
    rows = [(0.0, brim), (0.01, brim * 0.98), (0.012, crown * 1.15)]
    for (ya, ra), (yb, rb) in zip(rows, rows[1:]):
        for i in range(n):
            a0, a1 = TAU * i / n, TAU * (i + 1) / n
            h.poly([(math.cos(a0) * ra, ya, math.sin(a0) * ra), (math.cos(a1) * ra, ya, math.sin(a1) * ra), (math.cos(a1) * rb, yb, math.sin(a1) * rb),
                    (math.cos(a0) * rb, yb, math.sin(a0) * rb)], CLOTH, rgba(colour, 1.0), facing=(0, 1, 0))
            h.poly([(math.cos(a0) * ra, ya - 0.004, math.sin(a0) * ra), (math.cos(a1) * ra, ya - 0.004, math.sin(a1) * ra), (math.cos(a1) * rb, yb - 0.004, math.sin(a1) * rb),
                    (math.cos(a0) * rb, yb - 0.004, math.sin(a0) * rb)], CLOTH, rgba(colour, 0.6), facing=(0, -1, 0))
    h.tube([(0.0, 0.0, 0.0), (0.0, high * 0.7, 0.0), (0.0, high, 0.0)], [crown * 1.15, crown, crown * 0.8], n, CLOTH, [rgba(colour, 0.9), rgba(colour), rgba(colour, 1.1)], caps=True)
    h.tube([(0.0, 0.01, 0.0), (0.0, 0.03, 0.0)], [crown * 1.17, crown * 1.12], n, CLOTH, (0.012, 0.01, 0.008, 1.0))


def satchel(m, at, yaw=0.0, colour=props.LEATHER, hang=None):
    """A leather scrip, flap down. With `hang` (a point), its strap goes up to that."""
    s = props.Placed(m, at, yaw)
    s.tube([(-0.11, 0.08, 0.0), (-0.1, 0.08, 0.0), (0.1, 0.08, 0.0), (0.11, 0.08, 0.0)], [0.05, 0.08, 0.08, 0.05], 8, PAINT, rgba(colour), caps=True, squash=(0.4, 1.0))
    s.poly([(-0.1, 0.16, -0.035), (0.1, 0.16, -0.035), (0.09, 0.07, -0.042), (-0.09, 0.07, -0.042)], PAINT, rgba(colour, 1.25), facing=(0, 0.2, -1))
    if hang:
        for x in (-0.12, 0.12):
            a = (at[0] + x * math.cos(yaw), at[1] + 0.19, at[2] - x * math.sin(yaw))
            props.rope(m, [a, ((a[0] + hang[0]) * 0.5, (a[1] + hang[1]) * 0.5, (a[2] + hang[2]) * 0.5 - 0.01), hang], r=0.007, colour=(0.04, 0.026, 0.016))


def peg_board(hard, long, y, n):
    """A board on the wall (z = 0) at height `y`, `n` pegs in it; returns their ends."""
    plank(hard, (-long * 0.5, y - 0.06, -0.025), (long * 0.5, y + 0.06, 0.0), tone(rooms.STUD), along="x")
    ends = []
    for i in range(n):
        x = -long * 0.5 + long * (i + 0.5) / n
        a, b = (x, y, -0.025), (x, y + 0.035, -0.13)
        beam(hard, a, b, 0.024, 0.024, tone(rooms.STUD))
        ends.append(b)
    return ends


def pegs(p):
    """A peg board on the wall (z = 0), 1.75 m up: a felt hat, a hood with its long tail, a satchel on its strap."""
    ends = peg_board(p.hard, 0.9, 1.75, 3)
    e = ends[0]
    hat(p.soft, (e[0], e[1] - 0.14, -0.05), 0.0, -math.pi * 0.5)
    rooms.cloak(p.hard, p.soft, WALL, ends[1][0], ends[1][1] - 0.01, (0.034, 0.02, 0.014), 31.0, long=0.62, wide=0.34, peg=False)
    satchel(p.soft, (ends[2][0], 1.25, -0.06), 0.0, hang=(ends[2][0], ends[2][1] + 0.005, ends[2][2] + 0.02))


def towel(m, peg, wide, long, colour=props.LINEN):
    """A linen cloth hung over a peg's end, both halves down the wall (z = 0), one shorter."""
    x, y, z = peg

    def side(front, drop):
        def f(u, v):
            s = (u - 0.5) * wide
            out = (z + 0.01) * (1.0 - v) + (-0.03 if front else -0.012) * v
            wave = 0.008 * math.sin(s * 30.0 + (1.0 if front else 0.0)) * v
            return (x + s, y + 0.012 - v * drop, out + wave + (-0.004 if front else 0.0))

        def c(u, v):
            return rgba(colour, (0.75 + 0.25 * fbm(u * 3.0, v * 4.0, 1.0, 2, 7.0)) * (1.0 if front else 0.7))

        props.sheet(m, f, 4, 5, CLOTH, c, both=True)

    side(False, long)
    side(True, long * 0.7)


def pegs_room(p):
    """Two pegs on the wall (z = 0), 1.7 m up: a linen towel, a straw hat."""
    ends = peg_board(p.hard, 0.6, 1.7, 2)
    towel(p.soft, ends[0], 0.3, 0.5)
    e = ends[1]
    hat(p.soft, (e[0], e[1] - 0.15, -0.05), 0.0, -math.pi * 0.5, brim=0.19, crown=0.08, high=0.09, colour=props.STRAW)


# ---------------------------------------------------------------- the porter's room

def chest(p):
    """A small chest, 0.75 x 0.42 m and 0.45 m high, iron-strapped, a blanket folded on it."""
    rooms.chest(p.hard, 0.0, 0.0, 0.0, 0.75, 0.42, 0.45)
    props.tick(p.soft, -0.28, 0.24, -0.17, 0.17, 0.45, 0.06, colour=props.UNDYED, lumps=0.08, seed=3.0, edge=0.08)


def washstand(p):
    """A stool with a basin on it, and a jug by its foot (0.45 m across)."""
    hard = p.hard
    seat = [(math.cos(TAU * i / 10) * 0.18, math.sin(TAU * i / 10) * 0.18) for i in range(10)]
    props.slab(hard, seat, "y", 0.505, 0.55, tone(OAK))
    for i in range(3):
        a = TAU * i / 3 + 0.5
        props.turned(hard, (math.cos(a) * 0.21, 0.0, math.sin(a) * 0.21), (math.cos(a) * 0.1, 0.554, math.sin(a) * 0.1), [(0.0, 0.019), (0.5, 0.024), (0.88, 0.021), (1.0, 0.017)],
                     tone(OAK_DARK), sides=6)
    props.pot(p.soft, (0.0, 0.55, 0.0), [(0.0, 0.07), (0.025, 0.11), (0.07, 0.15), (0.08, 0.155)], colour=props.CLAY, sides=12)
    p.soft.poly([(math.cos(TAU * k / 12) * 0.135, 0.6, math.sin(TAU * k / 12) * 0.135) for k in range(12)], "window_dark", (0.0, 0.0, 0.0, 1.0), facing=(0, 1, 0))
    st.jug(p.soft, (0.24, 0.0, -0.12), 2.0, 0.0, 1.0, colour=(0.03, 0.027, 0.022))


# ---------------------------------------------------------------- the loft

def bundle(p):
    """A lodger's things on the floor (0.7 x 0.4 m): his blanket rolled and corded, his scrip, his shoes."""
    soft = p.soft
    soft.tube([(-0.3, 0.1, 0.05), (-0.25, 0.11, 0.05), (0.2, 0.11, 0.04), (0.26, 0.1, 0.04)], [0.07, 0.105, 0.105, 0.08], 9, CLOTH, rgba(props.UNDYED, 0.9), caps=True,
              squash=(1.0, 0.92))
    for x in (-0.15, 0.1):
        props.rope(soft, [(x, 0.11 + 0.11 * math.sin(a), 0.045 + 0.11 * math.cos(a)) for a in [TAU * k / 8 for k in range(9)]], r=0.007, colour=CORD)
    satchel(soft, (-0.1, 0.0, -0.13), 0.25, colour=(0.03, 0.02, 0.013))
    boot(soft, (0.22, 0.0, -0.16), 1.2)
    boot(soft, (0.33, 0.0, -0.08), 0.9, fallen=True)


def pallet(p):
    """A straw pallet on the floor for a lodger who paid less (0.8 x 1.9 m, its head at -z): a tick, a blanket thrown back, a cloak rolled for a pillow."""
    props.tick(p.soft, -0.38, 0.38, -0.93, 0.93, 0.0, 0.13, colour=(0.046, 0.04, 0.03), lumps=0.25, seed=21.0, edge=0.2, hollow=(0.5, 0.45, 0.04))
    props.blanket(p.soft, -0.4, 0.4, 0.05, 0.88, 0.15, drop=0.12, colour=props.UNDYED, rumple=0.025, seed=22.0, foot=True)
    props.heap(p.soft, (0.05, 0.12, -0.05), 0.36, 0.22, 0.1, colour=props.UNDYED, seed=23.0, folds=0.4)
    props.tick(p.soft, -0.25, 0.25, -0.9, -0.65, 0.1, 0.09, colour=(0.02, 0.019, 0.017), lumps=0.4, seed=24.0, edge=0.3)
    rng = random.Random(25)
    strands(p.hard, 60, lambda r: (r.uniform(-0.6, 0.6), r.uniform(-1.1, 1.1)) if r.random() < 0.6 else None, rng=rng)


def pack(p):
    """A lodger's sack, his staff laid by it and his hat on it (1.4 x 0.5 m)."""
    st.Sack(p.soft, (0.0, 0.0, 0.0), 1.2, 0.0, 0.7, 0.42, 0.24, seed=4.0, droop=0.02)
    staff(p.hard, (-0.7, 0.02, -0.3), (0.75, 0.02, -0.24), colour=OAK)
    hat(p.soft, (0.05, 0.215, 0.02), 0.4, 0.15, brim=0.16, crown=0.08, high=0.09)


BUILDERS = {
    "inn_tankard": tankard, "inn_rushes": rushes, "inn_rushes_strip": rushes_strip, "inn_sheepskin": sheepskin, "inn_hearth_basket": hearth_basket, "inn_pot": pot,
    "inn_dog": dog, "inn_trencher": trencher, "inn_jug_cups": jug_cups, "inn_hanging": hanging, "inn_cask_side": cask_side, "inn_broom": broom, "inn_boots": boots,
    "inn_pegs": pegs, "inn_pegs_room": pegs_room, "inn_chest": chest, "inn_washstand": washstand, "inn_bundle": bundle, "inn_pack": pack, "inn_pallet": pallet,
}

if __name__ == "__main__":
    props.run(BUILDERS)
