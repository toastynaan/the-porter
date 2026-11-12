"""The Cross Keys' beds: a solid oak box bed of the 1420s, as an inn keeps
for paying guests (the porter's room, and the open loft's row). Each is its
own model (art/models/prop_<name>.glb), 0.9 m wide and 2 m long, its head
at -z, standing on the floor at its origin; the scene
(game/world/props/prop_inn_bed.tscn) shows one of the three:

- inn_bed: made: a straw tick in the box, a rough wool coverlet with a
  linen sheet turned down over it, a bolster, a blanket folded at the foot.
- inn_bed_slept: a lodger's, slept in: the coverlet thrown down the bed,
  the tick hollowed, the bolster pushed aside.
- inn_bed_taken: made, and claimed for the night: a cloak thrown over its
  foot, a pair of shoes beside it.

The frame: four square posts (the head pair 1.05 m high, the foot pair
0.62 m), a boarded headboard under a shaped top rail, a lower boarded
footboard, deep side boards pegged into the posts, the box's floor of
boards 0.12 m up. No collision: the scene's hidden Block is that.

Run: tools/build.sh prop_inn_bed   (one: ... -- inn_bed_slept)
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import props
from props import OAK, OAK_DARK, PAINT, WOOD, beam, boards, plank, rgba, tone

W, L = 0.45, 1.0          # half its width, half its length
POST = 0.1
HEAD, FOOT = 1.05, 0.62   # the posts' heights
SIDE = (0.13, 0.43)       # the side boards' foot and top
BOX = 0.3                 # the box's floor of boards, which the tick lies on
FRAME = (0.36, 0.3, 0.24)  # oak gone dark with age and hands
WOAD = (0.018, 0.021, 0.026)   # a coverlet dyed with woad long ago, gone grey
TICK = (0.046, 0.04, 0.03)     # the tick's coarse canvas
RUST = (0.028, 0.019, 0.013)   # a russet coverlet, faded


def peg(m, p, n, r=0.011):
    """A trenail's end, flush in a post's face: a dark round."""
    props.nail(m, p, n, r=r, proud=0.002, colour=rgba(FRAME, 0.55), mat=WOOD)


def cap(m, x, y, z, w):
    """A post's top, cut to a low pyramid."""
    c = tone(FRAME, 0.05)
    apex = (x, y + w * 0.45, z)
    pts = [(x - w * 0.5, y, z - w * 0.5), (x + w * 0.5, y, z - w * 0.5), (x + w * 0.5, y, z + w * 0.5), (x - w * 0.5, y, z + w * 0.5)]
    for i in range(4):
        a, b = pts[i], pts[(i + 1) % 4]
        m.poly([a, b, apex], WOOD, c, facing=((a[0] + b[0]) * 0.5 - x, 0.6, (a[2] + b[2]) * 0.5 - z))


def frame(p):
    m = p.hard
    x, z = W - POST * 0.5, L - POST * 0.5
    for sx in (-1, 1):
        for sz, h in ((-1, HEAD), (1, FOOT)):
            beam(m, (sx * x, 0.0, sz * z), (sx * x, h, sz * z), POST, POST, tone(FRAME, 0.06), ends="a")
            cap(m, sx * x, h, sz * z, POST)
        # The side board, deep and pegged through the posts at each end.
        plank(m, (sx * W - (0.035 if sx > 0 else 0.0), SIDE[0], -z + POST * 0.5), (sx * W + (0.035 if sx < 0 else 0.0), SIDE[1], z - POST * 0.5), tone(FRAME, 0.1),
              along="z")
        # A moulded edge along its top.
        beam(m, (sx * (W - 0.012), SIDE[1] + 0.012, -z + POST * 0.5), (sx * (W - 0.012), SIDE[1] + 0.012, z - POST * 0.5), 0.045, 0.024, tone(FRAME, 0.05), ends="")
        for zz in (-z, z):
            for y in (SIDE[0] + 0.07, SIDE[1] - 0.07):
                peg(m, (sx * W, y, zz), (sx, 0, 0))
    # The headboard: three boards on end between the posts, a rail at their foot, a shaped rail over them.
    inner = x - POST * 0.5
    boards(m, (-inner, SIDE[0], -z - 0.016), (inner, 0.9, -z + 0.016), "y", "x", 3, FRAME, gap=0.006, uneven=0.003, spread=0.1)
    beam(m, (-inner, SIDE[0] + 0.05, -z + 0.03), (inner, SIDE[0] + 0.05, -z + 0.03), 0.05, 0.1, tone(FRAME, 0.05), ends="")
    top = [(-inner, 0.88), (inner, 0.88), (inner, 0.95)]
    for i in range(1, 12):
        t = i / 12.0
        top.append((inner - t * 2.0 * inner, 0.95 + 0.06 * math.sin(math.pi * t) + 0.012 * math.sin(math.pi * t * 3.0)))
    top.append((-inner, 0.95))
    props.slab(m, top, "z", -z - 0.026, -z + 0.026, tone(FRAME, 0.04), grain="p")
    for sx in (-1, 1):
        peg(m, (sx * (inner - 0.03), 0.92, -z + 0.027), (0, 0, 1), r=0.009)
    # The footboard: lower, two boards, a rail capping them.
    boards(m, (-inner, SIDE[0], z - 0.016), (inner, 0.52, z + 0.016), "x", "y", 2, FRAME, gap=0.006, uneven=0.003, spread=0.1)
    beam(m, (-inner, 0.545, z), (inner, 0.545, z), 0.05, 0.05, tone(FRAME, 0.05), ends="")
    # The box's floor, between the side boards: dark, as it shows past the tick.
    boards(m, (-W + 0.035, BOX - 0.025, -z + POST * 0.5), (W - 0.035, BOX, z - POST * 0.5), "x", "z", 7, OAK_DARK, gap=0.01, uneven=0.003)
    # The space under it, shut in by the boards: a dark floor (there is nothing to see).
    m.poly([(-W, 0.004, -z), (W, 0.004, -z), (W, 0.004, z), (-W, 0.004, z)], PAINT, (0.006, 0.005, 0.004, 1.0), facing=(0, 1, 0))


def straw(p, n, x0, x1, z0, z1, y, seed):
    """Stalks of straw out of the tick's seams and on the floor."""
    rng = random.Random(seed)
    for _ in range(n):
        x, z = rng.uniform(x0, x1), rng.uniform(z0, z1)
        a, long = rng.uniform(0.0, math.tau), rng.uniform(0.05, 0.13)
        yy = y + rng.uniform(0.0, 0.012)
        p.hard.poly([(x, yy, z), (x + math.cos(a) * long, yy + rng.uniform(-0.01, 0.02), z + math.sin(a) * long),
                     (x + math.cos(a) * long - math.sin(a) * 0.005, yy, z + math.sin(a) * long + math.cos(a) * 0.005)], PAINT,
                    rgba(props.STRAW, rng.uniform(0.9, 1.5)), facing=(0, 1, 0))


def tick(p, seed, hollow=None):
    """The straw tick, lying in the box and bulging over its sides."""
    props.tick(p.soft, -W + 0.04, W - 0.04, -L + 0.07, L - 0.07, BOX - 0.01, 0.2, colour=TICK, lumps=0.18, seed=seed, edge=0.14, hollow=hollow)


def bolster(m, x0, x1, z0, z1, y, seed):
    props.tick(m, x0, x1, z0, z1, y, 0.12, colour=props.LINEN, lumps=0.25, seed=seed, edge=0.32)


def inn_bed(p):
    frame(p)
    tick(p, 1.0)
    straw(p, 10, -W + 0.06, W - 0.06, -L + 0.12, -L + 0.2, SIDE[1] + 0.02, 2)
    props.blanket(p.soft, -W - 0.01, W + 0.01, -0.48, L - 0.08, 0.53, drop=0.13, colour=WOAD, rumple=0.014, seed=3.0, foot=False, stripe=props.UNDYED)
    # The sheet turned down over the coverlet's head.
    props.tick(p.soft, -W + 0.005, W - 0.005, -0.56, -0.42, 0.515, 0.035, colour=props.LINEN, lumps=0.2, seed=4.0, edge=0.25)
    bolster(p.soft, -0.37, 0.37, -0.93, -0.64, 0.45, 5.0)
    # A second blanket, folded at the foot.
    props.tick(p.soft, -0.38, 0.38, 0.5, 0.86, 0.545, 0.075, colour=props.UNDYED, lumps=0.08, seed=6.0, edge=0.07)


def inn_bed_slept(p):
    frame(p)
    tick(p, 7.0, hollow=(0.45, 0.4, 0.06))
    props.blanket(p.soft, -W - 0.01, W + 0.01, 0.32, L - 0.08, 0.53, drop=0.13, colour=RUST, rumple=0.03, seed=8.0, foot=False)
    props.heap(p.soft, (0.08, 0.5, 0.18), 0.4, 0.26, 0.13, colour=RUST, seed=9.0, folds=0.4)
    b = props.Placed(p.soft, (-0.12, 0.0, -0.74), 0.4)
    bolster(b, -0.33, 0.33, -0.14, 0.14, 0.44, 10.0)
    straw(p, 14, -W + 0.06, W - 0.06, -0.2, 0.3, 0.5, 11)


def inn_bed_taken(p):
    frame(p)
    tick(p, 12.0)
    props.blanket(p.soft, -W - 0.01, W + 0.01, -0.5, L - 0.08, 0.53, drop=0.13, colour=props.UNDYED, rumple=0.016, seed=13.0, foot=False,
                  stripe=(0.026, 0.02, 0.016))
    bolster(p.soft, -0.36, 0.36, -0.93, -0.64, 0.45, 14.0)
    # A traveller's cloak thrown over the foot, hanging down one side.
    props.blanket(p.soft, -W - 0.02, W + 0.02, 0.35, 0.82, 0.575, drop=0.2, colour=(0.02, 0.019, 0.017), rumple=0.03, seed=15.0, foot=False)
    # His shoes, by the bed's side.
    for i, (x, z, yaw) in enumerate(((W + 0.09, 0.25, 0.15), (W + 0.12, 0.45, -0.35))):
        s = props.Placed(p.soft, (x, 0.0, z), yaw)
        props.turned(s, (0.0, 0.035, -0.12), (0.0, 0.035, 0.13), [(0.0, 0.012), (0.12, 0.035), (0.6, 0.042), (0.85, 0.045), (1.0, 0.03)], props.LEATHER, sides=7)
        s.tube([(0.0, 0.05, 0.05), (0.0, 0.1, 0.07)], [0.04, 0.035], 7, PAINT, rgba(props.LEATHER, 0.9), caps=True)


BUILDERS = {"inn_bed": inn_bed, "inn_bed_slept": inn_bed_slept, "inn_bed_taken": inn_bed_taken}

if __name__ == "__main__":
    props.run(BUILDERS)
