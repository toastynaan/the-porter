"""The props of the outer court and the porter's cell, and the plain
furniture that is used all over the abbey. Each is its own model
(art/models/prop_<name>.glb), sized to the collision its scene already has
(game/world/props/prop_<name>.tscn), standing on the floor at its origin:

- cot: the porter's cot, a plank bed on posts with room under it.
- bed, bed_slept, bed_bare: a low straw bed in a board frame, made; left
  in a hurry; stripped (the scene shows one of the three by where it stands).
- bed_raised: a bed on legs you can hide under, its blanket hanging.
- desk: the porter's desk, open to his side, with his ink and tallies.
- ledger: the gate ledger, shut.
- stool: three legs through a round seat.
- bench: a plank on two slab ends, a stretcher wedged through them.
- table, table_set, table_jug: a trestle table, bare; with a bowl and cup
  left on it; with a jug and a heel of bread.
- gate_bar: the oak bar of the gate.
- well: the court well: a stone kerb, a windlass under a little roof.
- woodpile: split logs stacked between stakes.
- door: an oak door leaf of planks on ledges, hung on strap hinges
  (objects `HingeLeft` and `HingeRight`; game/world/door/door.gd shows one).
- candle: a tallow stub in a clay dish.
- lamp: a hanging oil lamp, a dish in an iron ring on chains.

Run: tools/build.sh prop_abbey_court   (one prop: ... -- bench)
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
import props
from props import IRON, IRON_C, OAK, OAK_DARK, PAINT, PINE, WOOD, beam, boards, plank, rgba, tone

STONE = "stone_church"


def bedstead(p, wide, top, head, foot, post=0.07, colour=OAK_DARK):
    """A bed frame on four posts, `wide` across and 2 m long, its slats'
    top at `top`; the head posts (at -z) rise to `head`, the others to `foot`."""
    m = p.hard
    x, z = wide * 0.5 - post * 0.5, 1.0 - post * 0.5
    for sx in (-1, 1):
        beam(m, (sx * x, 0.0, -z), (sx * x, head, -z), post, post, tone(colour))
        beam(m, (sx * x, 0.0, z), (sx * x, foot, z), post, post, tone(colour))
        beam(m, (sx * x, top - 0.075, -z + post * 0.5), (sx * x, top - 0.075, z - post * 0.5), 0.04, 0.11, tone(colour), ends="")
        for zz in (-z, z):
            props.nail(m, (sx * (x + post * 0.5), top - 0.075, zz), (sx, 0, 0), r=0.012, colour=rgba(colour, 0.6), mat=WOOD)
    for zz in (-z, z):
        beam(m, (-x + post * 0.5, top - 0.075, zz), (x - post * 0.5, top - 0.075, zz), 0.04, 0.11, tone(colour), ends="")
    boards(m, (-x + post * 0.5, head - 0.3, -z - 0.012), (x - post * 0.5, head - 0.04, -z + 0.012), "x", "y", 2, colour)
    boards(m, (-x + 0.02, top - 0.03, -z + post * 0.5), (x - 0.02, top, z - post * 0.5), "x", "z", 9, colour, gap=0.012, uneven=0.004, ragged=0.01)


def cot(p):
    bedstead(p, 0.8, 0.44, 0.78, 0.52)
    props.tick(p.soft, -0.35, 0.35, -0.93, 0.93, 0.435, 0.085, seed=1.0)
    props.blanket(p.soft, -0.37, 0.37, -0.2, 0.95, 0.525, drop=0.13, colour=props.RUSSET, rumple=0.014, seed=2.0)
    props.heap(p.soft, (0.06, 0.52, -0.3), 0.3, 0.2, 0.09, colour=props.RUSSET, seed=3.0)
    # His cloak rolled for a pillow.
    props.tick(p.soft, -0.27, 0.27, -0.92, -0.62, 0.5, 0.1, colour=(0.018, 0.017, 0.016), lumps=0.4, seed=4.0, edge=0.3)


def bed_frame(p, colour=OAK_DARK):
    m = p.hard
    for sx in (-1, 1):
        plank(m, (sx * 0.45 - (0.035 if sx > 0 else 0.0), 0.05, -0.97), (sx * 0.45 + (0.035 if sx < 0 else 0.0), 0.31, 0.97), tone(colour), along="z")
        for sz, h in ((-1, 0.64), (1, 0.36)):
            beam(m, (sx * 0.415, 0.0, sz * 0.965), (sx * 0.415, h, sz * 0.965), 0.07, 0.07, tone(colour))
    boards(m, (-0.38, 0.05, 0.955), (0.38, 0.33, 0.985), "x", "y", 2, colour)
    boards(m, (-0.38, 0.05, -0.985), (0.38, 0.6, -0.955), "x", "y", 4, colour)


def bed(p):
    bed_frame(p)
    props.tick(p.soft, -0.41, 0.41, -0.95, 0.95, 0.24, 0.2, seed=5.0)
    props.blanket(p.soft, -0.455, 0.455, -0.52, 0.99, 0.455, drop=0.2, seed=6.0, rumple=0.012)
    props.tick(p.soft, -0.34, 0.34, -0.93, -0.63, 0.41, 0.11, colour=props.LINEN, lumps=0.3, seed=7.0, edge=0.3)


def bed_slept(p):
    bed_frame(p)
    props.tick(p.soft, -0.41, 0.41, -0.95, 0.95, 0.24, 0.2, seed=8.0, hollow=(0.45, 0.42, 0.07))
    props.blanket(p.soft, -0.455, 0.455, 0.35, 0.99, 0.45, drop=0.2, seed=9.0, rumple=0.03)
    props.heap(p.soft, (0.12, 0.42, 0.2), 0.36, 0.3, 0.14, seed=10.0, folds=0.4)
    # The bolster pushed off its place, half over the side.
    b = props.Placed(p.soft, (-0.2, 0.0, -0.74), 0.5)
    props.tick(b, -0.3, 0.3, -0.14, 0.14, 0.42, 0.1, colour=props.LINEN, lumps=0.3, seed=11.0, edge=0.3)


def bed_bare(p):
    bed_frame(p)
    props.tick(p.soft, -0.41, 0.41, -0.95, 0.95, 0.24, 0.19, seed=12.0, lumps=0.4, hollow=(0.5, 0.5, 0.05))
    # The blanket folded at the foot; straw out of a split seam.
    props.tick(p.soft, -0.3, 0.3, 0.5, 0.86, 0.41, 0.07, colour=props.UNDYED, lumps=0.1, seed=13.0, edge=0.08)
    for _ in range(26):
        x, z = random.uniform(-0.36, -0.1), random.uniform(-0.3, 0.2)
        a, length = random.uniform(0.0, math.tau), random.uniform(0.06, 0.16)
        y = 0.435 + random.uniform(0.0, 0.02)
        p.hard.poly([(x, y, z), (x + math.cos(a) * length, y + random.uniform(0.0, 0.03), z + math.sin(a) * length),
                     (x + math.cos(a) * length - math.sin(a) * 0.006, y, z + math.sin(a) * length + math.cos(a) * 0.006)], PAINT,
                    rgba(props.STRAW, random.uniform(0.7, 1.2)), facing=(0, 1, 0))


def bed_raised(p):
    bedstead(p, 0.9, 0.36, 0.8, 0.5)
    props.tick(p.soft, -0.4, 0.4, -0.93, 0.93, 0.355, 0.1, seed=14.0)
    props.blanket(p.soft, -0.455, 0.455, -0.5, 0.99, 0.46, drop=0.2, seed=15.0, rumple=0.012)
    props.tick(p.soft, -0.33, 0.33, -0.92, -0.63, 0.43, 0.1, colour=props.LINEN, lumps=0.3, seed=16.0, edge=0.3)


def desk(p):
    m = p.hard
    boards(m, (-0.62, 0.76, -0.32), (0.62, 0.8, 0.32), "x", "z", 3, OAK, ragged=0.006)
    for sx in (-1, 1):
        for sz in (-1, 1):
            beam(m, (sx * 0.555, 0.0, sz * 0.255), (sx * 0.555, 0.76, sz * 0.255), 0.07, 0.07, tone(OAK_DARK))
        # The ends, boarded.
        boards(m, (sx * 0.555 - 0.012, 0.1, -0.22), (sx * 0.555 + 0.012, 0.74, 0.22), "y", "z", 3, OAK_DARK)
    # The back, boarded; the porter's side open, with a rail and a shelf.
    boards(m, (-0.52, 0.1, 0.243), (0.52, 0.74, 0.267), "y", "x", 7, OAK_DARK)
    beam(m, (-0.52, 0.69, -0.255), (0.52, 0.69, -0.255), 0.035, 0.1, tone(OAK_DARK), ends="")
    beam(m, (-0.52, 0.1, -0.255), (0.52, 0.1, -0.255), 0.035, 0.07, tone(OAK_DARK), ends="")
    boards(m, (-0.52, 0.36, -0.25), (0.52, 0.385, 0.243), "x", "z", 2, OAK_DARK)
    plank(m, (-0.52, 0.07, -0.25), (0.52, 0.095, 0.243), tone(OAK_DARK, 0.05), along="x")
    # On the shelf: a small coffer, rolls, a spare lantern horn.
    plank(m, (-0.42, 0.385, -0.12), (-0.14, 0.55, 0.1), tone(OAK), along="x")
    props.strap(m, (-0.35, 0.385, -0.12), (-0.35, 0.55, -0.12), (0, 0, -1), width=0.03, nails=2)
    props.strap(m, (-0.21, 0.385, -0.12), (-0.21, 0.55, -0.12), (0, 0, -1), width=0.03, nails=2)
    for i in range(4):
        z = -0.1 + i * 0.05 + random.uniform(-0.01, 0.01)
        y = 0.385 + 0.02 + (0.036 if i == 3 else 0.0)
        zz = z - (0.075 if i == 3 else 0.0)
        p.soft.tube([(0.1, y, zz), (0.42 + random.uniform(-0.03, 0.02), y, zz + random.uniform(-0.02, 0.02))], [0.02, 0.02], 7, PAINT, rgba(props.PARCHMENT, random.uniform(0.8, 1.1)), caps=True)
    # On the top, clear of the ledger (x 0.18..0.42) and the candle (x -0.4): an inkhorn in its block, a quill, a penknife, tally sticks.
    plank(m, (-0.13, 0.8, 0.14), (-0.03, 0.83, 0.24), tone(OAK_DARK), along="x")
    props.pot(p.soft, (-0.08, 0.83, 0.19), [(0.0, 0.012), (0.03, 0.02), (0.05, 0.021)], colour=(0.1, 0.085, 0.07), sides=7)
    q = props.Placed(m, (0.02, 0.803, 0.21), 0.5)
    q.poly([(0.0, 0.0, 0.0), (0.2, 0.004, 0.0), (0.21, 0.006, 0.012), (0.08, 0.004, 0.02)], PAINT, (0.1, 0.095, 0.08, 1.0), facing=(0, 1, 0))
    q.poly([(0.0, 0.0, 0.0), (0.2, 0.004, 0.0), (0.21, 0.006, -0.008), (0.1, 0.004, -0.012)], PAINT, (0.08, 0.075, 0.065, 1.0), facing=(0, 1, 0))
    q.box((-0.05, 0.0, -0.002), (0.0, 0.003, 0.002), PAINT, (0.09, 0.085, 0.07, 1.0))
    for i in range(3):
        a = props.Placed(m, (-0.52 + i * 0.03, 0.8, -0.2 + i * 0.012), 1.3 + i * 0.12)
        plank(a, (-0.11, 0.0, -0.009), (0.11, 0.012, 0.009), tone(PINE), along="x")
    k = props.Placed(m, (-0.2, 0.8, -0.22), -0.3)
    plank(k, (-0.05, 0.0, -0.007), (0.01, 0.012, 0.007), tone(OAK_DARK), along="x")
    k.poly([(0.01, 0.006, -0.006), (0.08, 0.006, -0.001), (0.01, 0.006, 0.006)], IRON, IRON_C, facing=(0, 1, 0))


def ledger(p):
    props.book(p.hard, (0.0, 0.0, 0.0), 0.0, 0.25, 0.35, 0.06)
    # The marker hanging out of it.
    p.hard.poly([(0.03, 0.034, 0.167), (0.045, 0.034, 0.167), (0.048, 0.004, 0.2), (0.033, 0.004, 0.2)], PAINT, (0.045, 0.012, 0.009, 1.0), facing=(0, 1, 1))
    p.hard.poly([(0.03, 0.034, 0.167), (0.045, 0.034, 0.167), (0.048, 0.004, 0.2), (0.033, 0.004, 0.2)], PAINT, (0.03, 0.009, 0.007, 1.0), facing=(0, -1, -1))


def stool(p):
    m = p.hard
    c = tone(OAK)
    seat = [(math.cos(math.tau * i / 10) * 0.18, math.sin(math.tau * i / 10) * 0.18) for i in range(10)]
    props.slab(m, seat, "y", 0.405, 0.45, c)
    for i in range(3):
        a = math.tau * i / 3 + 0.5
        top, foot = (math.cos(a) * 0.1, 0.454, math.sin(a) * 0.1), (math.cos(a) * 0.19, 0.0, math.sin(a) * 0.19)
        props.turned(m, foot, top, [(0.0, 0.019), (0.5, 0.024), (0.88, 0.021), (1.0, 0.017)], tone(OAK_DARK), sides=6)


def bench(p):
    m = p.hard
    boards(m, (-1.0, 0.405, -0.19), (1.0, 0.45, 0.19), "x", "z", 2, OAK, ragged=0.012, uneven=0.002)
    end = [(-0.16, 0.0), (-0.055, 0.0), (0.0, 0.13), (0.055, 0.0), (0.16, 0.0), (0.145, 0.405), (-0.145, 0.405)]
    for sx in (-1, 1):
        props.slab(m, end, "x", sx * 0.77 - 0.02, sx * 0.77 + 0.02, tone(OAK_DARK))
        # The stretcher's end through the slab, and the wedge that holds it.
        beam(m, (sx * 0.845, 0.185, 0.0), (sx * 0.83, 0.33, 0.0), 0.022, 0.03, tone(OAK), up=(0, 0, 1))
    beam(m, (-0.88, 0.25, 0.0), (0.88, 0.25, 0.0), 0.03, 0.085, tone(OAK_DARK))


def trestle_table(p):
    m = p.hard
    boards(m, (-1.0, 0.705, -0.45), (1.0, 0.75, 0.45), "x", "z", 3, OAK, ragged=0.015, uneven=0.003)
    for sx in (-1, 1):
        x = sx * 0.68
        plank(m, (sx * 0.52 - 0.04, 0.672, -0.4), (sx * 0.52 + 0.04, 0.705, 0.4), tone(OAK_DARK), along="z")
        for sz in (-1, 1):
            beam(m, (x, 0.0, sz * 0.37), (x, 0.69, sz * 0.09), 0.05, 0.065, tone(OAK_DARK), up=(sx, 0, 0))
        beam(m, (x, 0.655, -0.26), (x, 0.655, 0.26), 0.055, 0.06, tone(OAK_DARK))
        beam(m, (x + sx * 0.028, 0.27, -0.29), (x + sx * 0.028, 0.27, 0.29), 0.022, 0.07, tone(OAK_DARK))
    beam(m, (-0.78, 0.36, 0.0), (0.78, 0.36, 0.0), 0.035, 0.08, tone(OAK_DARK))


def bowl(p, at, r=0.085):
    props.pot(p.soft, at, [(0.0, r * 0.45), (r * 0.25, r * 0.85), (r * 0.5, r)], colour=(0.045, 0.033, 0.022), sides=9)


def cup(p, at):
    props.pot(p.soft, at, [(0.0, 0.028), (0.045, 0.034), (0.09, 0.038)], colour=(0.04, 0.034, 0.026), sides=7)


def spoon(m, at, yaw):
    s = props.Placed(m, at, yaw)
    plank(s, (-0.09, 0.0, -0.006), (0.03, 0.008, 0.006), tone(PINE, 0.05), along="x")
    s.poly([(0.03, 0.004, -0.014), (0.07, 0.004, -0.018), (0.085, 0.004, 0.0), (0.07, 0.004, 0.018), (0.03, 0.004, 0.014)], WOOD, rgba(PINE, 0.9), facing=(0, 1, 0))


def table_set(p):
    trestle_table(p)
    bowl(p, (-0.42, 0.75, -0.22))
    spoon(p.hard, (-0.24, 0.752, -0.26), 0.7)
    cup(p, (-0.6, 0.75, -0.06))
    bowl(p, (0.5, 0.75, 0.2))
    # One cup on its side.
    c = props.Placed(p.soft, (0.3, 0.788, 0.28), 0.4, tilt=math.pi * 0.5)
    props.pot(c, (0.0, 0.0, 0.0), [(0.0, 0.028), (0.045, 0.034), (0.09, 0.038)], colour=(0.04, 0.034, 0.026), sides=7)


def table_jug(p):
    trestle_table(p)
    props.pot(p.soft, (0.3, 0.75, 0.05), [(0.0, 0.06), (0.05, 0.085), (0.13, 0.09), (0.19, 0.06), (0.23, 0.045), (0.26, 0.055)], colour=props.CLAY, sides=10)
    p.soft.tube([(0.355, 0.99, 0.05), (0.42, 0.97, 0.05), (0.43, 0.9, 0.05), (0.385, 0.85, 0.05)], [0.012, 0.012, 0.012, 0.012], 5, PAINT, rgba(props.CLAY))
    # A heel of bread and the knife.
    props.tick(p.soft, -0.02, 0.14, 0.2, 0.33, 0.75, 0.06, colour=(0.045, 0.03, 0.016), lumps=0.3, seed=21.0, edge=0.35)
    k = props.Placed(p.hard, (-0.12, 0.752, 0.24), 0.9)
    plank(k, (-0.07, 0.0, -0.008), (0.02, 0.014, 0.008), tone(OAK_DARK), along="x")
    k.poly([(0.02, 0.006, -0.008), (0.14, 0.006, -0.002), (0.02, 0.006, 0.008)], IRON, IRON_C, facing=(0, 1, 0))
    cup(p, (0.55, 0.75, -0.2))


def gate_bar(p):
    m = p.hard
    beam(m, (0.0, 0.07, -1.7), (0.0, 0.07, 1.7), 0.14, 0.14, rgba(OAK_DARK))
    for z in (-1.6, -0.55, 0.55, 1.6):
        beam(m, (0.0, 0.07, z - 0.03), (0.0, 0.07, z + 0.03), 0.152, 0.152, IRON_C, IRON, ends="", end_shade=1.0)
    # The handle he lifts it by, on the court's side.
    beam(m, (0.076, 0.07, -0.02), (0.076, 0.07, 0.02), 0.012, 0.05, IRON_C, IRON, up=(1, 0, 0), end_shade=1.0)
    props.ring(m, (0.09, 0.03, 0.0), (1, 0, 0), r=0.05, thick=0.007)


def well(p):
    m = p.hard
    n = 14
    # The kerb: two courses of blocks and a capping course, worn and green at the foot.
    for course, (y0, y1, r0, r1, turn) in enumerate(((0.0, 0.36, 0.56, 0.79, 0.0), (0.36, 0.68, 0.56, 0.79, 0.5), (0.68, 0.8, 0.53, 0.82, 0.2))):
        for i in range(n):
            a0, a1 = math.tau * (i + turn) / n + 0.006, math.tau * (i + 1 + turn) / n - 0.006
            k = random.uniform(0.82, 1.08)
            jut = random.uniform(-0.008, 0.008)

            def pt(a, r, y):
                return (math.cos(a) * (r + (jut if r > 0.6 else -jut)), y, math.sin(a) * (r + (jut if r > 0.6 else -jut)))

            foot = (0.5 * k, 0.5 * k, 0.47 * k, 0.45 if course == 0 else 1.0)
            top = (0.62 * k, 0.6 * k, 0.56 * k, 1.0)
            am = (a0 + a1) * 0.5
            out = (math.cos(am), 0.0, math.sin(am))
            m.poly([pt(a0, r1, y0), pt(a1, r1, y0), pt(a1, r1, y1), pt(a0, r1, y1)], STONE, [foot, foot, top, top], facing=out)
            deep = (0.2 * k, 0.2 * k, 0.19 * k, 1.0) if course < 2 else top
            m.poly([pt(a0, r0, y0), pt(a1, r0, y0), pt(a1, r0, y1), pt(a0, r0, y1)], STONE, [deep, deep, top, top], facing=(-out[0], 0.0, -out[2]))
            if course != 1:
                m.poly([pt(a0, r0, y1), pt(a1, r0, y1), pt(a1, r1, y1), pt(a0, r1, y1)], STONE, top, facing=(0, 1, 0))
            if course == 2:
                m.poly([pt(a0, r0, y0), pt(a1, r0, y0), pt(a1, r1, y0), pt(a0, r1, y0)], STONE, foot, facing=(0, -1, 0))
    # The shaft: black a little way down. (The court's ground runs under the kerb, so the dark is a lid, not a depth.)
    m.poly([(math.cos(math.tau * i / n) * 0.57, 0.14, math.sin(math.tau * i / n) * 0.57) for i in range(n)], "window_dark", (0.0, 0.0, 0.0, 1.0), facing=(0, 1, 0))
    # The windlass: two posts on the kerb, the barrel between them, its crank, the rope, the bucket.
    for sx in (-1, 1):
        beam(m, (sx * 0.68, 0.78, 0.0), (sx * 0.68, 2.2, 0.0), 0.11, 0.11, tone(OAK_DARK))
        beam(m, (sx * 0.68, 0.8, 0.34), (sx * 0.68, 1.3, 0.05), 0.06, 0.06, tone(OAK_DARK))
        beam(m, (sx * 0.68, 0.8, -0.34), (sx * 0.68, 1.3, -0.05), 0.06, 0.06, tone(OAK_DARK))
        beam(m, (sx * 0.68, 2.2, -0.6), (sx * 0.68, 2.2, 0.6), 0.09, 0.09, tone(OAK_DARK))
        for sz in (-1, 1):
            beam(m, (sx * 0.68, 2.2, sz * 0.58), (sx * 0.68, 2.62, 0.0), 0.07, 0.07, tone(OAK_DARK), up=(sx, 0, 0))
    beam(m, (-0.9, 2.62, 0.0), (0.9, 2.62, 0.0), 0.08, 0.08, tone(OAK_DARK))
    # The roof's boards, weathered grey, one slipped.
    for sz in (-1, 1):
        for i in range(5):
            t0, t1 = i / 5.0, (i + 1) / 5.0 + 0.04
            slip = 0.07 if (sz > 0 and i == 1) else 0.0
            lo = (-0.98 + random.uniform(-0.02, 0.02), 2.68 - (0.5 + slip) * t1, sz * (0.02 + (0.7 + slip) * t1))
            hi = (0.98 + random.uniform(-0.02, 0.02), 2.68 - (0.5 + slip) * t0, sz * (0.02 + (0.7 + slip) * t0))
            mid0, mid1 = (lo[0], (lo[1] + hi[1]) * 0.5, (lo[2] + hi[2]) * 0.5), (hi[0], (lo[1] + hi[1]) * 0.5, (lo[2] + hi[2]) * 0.5)
            beam(m, mid0, mid1, math.hypot(hi[1] - lo[1], hi[2] - lo[2]), 0.02, tone((0.42, 0.42, 0.4), 0.12), up=(0.0, 0.7, sz * 0.5))
    props.turned(p.soft, (-0.63, 1.5, 0.0), (0.63, 1.5, 0.0), [(0.0, 0.05), (0.06, 0.075), (0.94, 0.075), (1.0, 0.05)], tone(OAK), sides=10)
    beam(m, (0.63, 1.5, 0.0), (0.9, 1.5, 0.0), 0.022, 0.022, IRON_C, IRON, end_shade=1.0)
    beam(m, (0.89, 1.5, 0.0), (0.89, 1.27, 0.12), 0.022, 0.022, IRON_C, IRON, end_shade=1.0)
    beam(m, (0.89, 1.27, 0.12), (1.04, 1.27, 0.12), 0.03, 0.03, tone(OAK), end_shade=0.8)
    coil = [(-0.2 + 0.4 * i / 40.0, 1.5 + math.sin(i * 0.9) * 0.086, math.cos(i * 0.9) * 0.086) for i in range(41)]
    props.rope(p.soft, coil, r=0.011)
    props.rope(p.soft, [(0.2, 1.5, 0.086), (0.19, 1.3, 0.09), (0.18, 1.19, 0.1)], r=0.011)
    # The bucket hangs just over the kerb's edge, where he left it.
    b = props.Placed(m, (0.18, 0.9, 0.1), 0.3)
    staves = 9
    for i in range(staves):
        a0, a1 = math.tau * i / staves, math.tau * (i + 1) / staves
        c = tone(OAK, 0.2)
        b.poly([(math.cos(a0) * 0.1, 0.0, math.sin(a0) * 0.1), (math.cos(a1) * 0.1, 0.0, math.sin(a1) * 0.1), (math.cos(a1) * 0.125, 0.24, math.sin(a1) * 0.125), (math.cos(a0) * 0.125, 0.24, math.sin(a0) * 0.125)],
               WOOD, c, uvs=[(0.0, 0.0), (0.06, 0.0), (0.06, 0.2), (0.0, 0.2)], facing=(math.cos((a0 + a1) * 0.5), 0.0, math.sin((a0 + a1) * 0.5)))
        for y, r in ((0.04, 0.106), (0.19, 0.122)):
            b.poly([(math.cos(a0) * r, y, math.sin(a0) * r), (math.cos(a1) * r, y, math.sin(a1) * r), (math.cos(a1) * r, y + 0.022, math.sin(a1) * r), (math.cos(a0) * r, y + 0.022, math.sin(a0) * r)],
                   IRON, IRON_C, facing=(math.cos((a0 + a1) * 0.5), 0.0, math.sin((a0 + a1) * 0.5)))
    b.poly([(math.cos(math.tau * i / staves) * 0.12, 0.2, math.sin(math.tau * i / staves) * 0.12) for i in range(staves)], "window_dark", (0.0, 0.0, 0.0, 1.0), facing=(0, 1, 0))
    b.poly([(math.cos(math.tau * i / staves) * 0.1, 0.0, math.sin(math.tau * i / staves) * 0.1) for i in range(staves)], WOOD, rgba(OAK, 0.5), facing=(0, -1, 0))
    bail = [(math.cos(math.pi * i / 8) * 0.125, 0.24 + math.sin(math.pi * i / 8) * 0.06, 0.0) for i in range(9)]
    b.tube(bail, [0.005] * 9, 4, IRON, IRON_C)


def woodpile(p):
    m = p.hard
    bark = (0.26, 0.22, 0.18)
    for sx in (-1, 1):
        for z in (-0.32, 0.32):
            beam(m, (sx * 0.97, 0.0, z), (sx * (0.97 + 0.03), 1.48, z), 0.06, 0.06, tone(OAK_DARK))
    for row, (z0, z1) in enumerate(((-0.6, -0.02), (0.02, 0.6))):
        y = 0.0
        layer = 0
        while y < 1.3:
            x = -0.92 + random.uniform(0.0, 0.05)
            # The top layers thin out toward one end, as a pile that is being used does.
            stop = 0.92 if y < 1.0 else random.uniform(-0.2, 0.6)
            tallest = 0.0
            while x < stop:
                r = random.uniform(0.055, 0.085)
                if x + 2 * r > 0.93:
                    break
                sides = random.choice((3, 3, 4))
                a = random.uniform(0.0, math.tau)
                cx, cy = x + r, y + r * 0.82
                e0, e1 = z0 + random.uniform(-0.03, 0.03) * (1 if row == 0 else 0.3), z1 + random.uniform(-0.03, 0.03) * (0.3 if row == 0 else 1)
                ringp = [(cx + math.cos(a + math.tau * i / sides) * r * 1.12, cy + math.sin(a + math.tau * i / sides) * r * 0.95) for i in range(sides)]
                c = tone(bark, 0.25)
                pale = tone((0.52, 0.44, 0.32), 0.3)
                for i in range(sides):
                    (xa, ya), (xb, yb) = ringp[i], ringp[(i + 1) % sides]
                    # One face of a split log is bark; the split faces are pale.
                    face = c if i == 0 else rgba(pale, 0.62)
                    m.poly([(xa, ya, e0), (xb, yb, e0), (xb, yb, e1), (xa, ya, e1)], WOOD, face,
                           uvs=[(0.0, 0.0), (0.12, 0.0), (0.12, 0.5), (0.0, 0.5)], facing=((xa + xb) * 0.5 - cx, (ya + yb) * 0.5 - cy, 0.0))
                for e, way in ((e0, -1), (e1, 1)):
                    m.poly([(xx, yy, e) for xx, yy in ringp], WOOD, pale, uvs=[(0.5 + (xx - cx), 0.5 + (yy - cy) * 0.2) for xx, yy in ringp], facing=(0, 0, way))
                tallest = max(tallest, r)
                x += 2 * r * 1.08
            y += tallest * 1.72 if tallest else 0.14
            layer += 1
    # A few that have rolled off, and the chips.
    for x, z, a in ((0.3, -0.78, 0.2), (-0.5, -0.74, -0.4), (0.62, 0.8, 0.1)):
        f = props.Placed(m, (x, 0.0, z), a)
        r = 0.07
        ringp = [(math.cos(math.tau * i / 3 + 0.5) * r, r * 0.6 + math.sin(math.tau * i / 3 + 0.5) * r * 0.9) for i in range(3)]
        for i in range(3):
            (ya, za), (yb, zb) = ringp[i], ringp[(i + 1) % 3]
            f.poly([(-0.28, za, ya), (-0.28, zb, yb), (0.28, zb, yb), (0.28, za, ya)], WOOD, tone(bark, 0.2) if i == 0 else rgba(PINE, 0.6),
                   uvs=[(0.0, 0.0), (0.12, 0.0), (0.12, 0.5), (0.0, 0.5)], facing=(0.0, (za + zb) * 0.5 - r * 0.6, (ya + yb) * 0.5))
        for e, way in ((-0.28, -1), (0.28, 1)):
            f.poly([(e, zz, yy) for yy, zz in ringp], WOOD, tone(PINE, 0.1), facing=(way, 0, 0))


def door_leaf(m):
    """The leaf about its own middle, 0.88 x 1.98 m, hinged at -x. Its +z
    face (ledges, strap hinges) is the room's side while it is shut; its -z
    face (planks, nail heads) shows through the doorway, and to the room
    when it stands open."""
    w, h = 0.44, 0.99
    boards(m, (-w, -h, -0.04), (w, h, 0.0), "y", "x", 5, OAK_DARK, gap=0.004, uneven=0.0025, spread=0.16)
    for y in (-0.7, 0.02, 0.72):
        plank(m, (-w + 0.02, y - 0.075, 0.0), (w - 0.02, y + 0.075, 0.03), tone(OAK_DARK), along="x")
        for i in range(5):
            x = -w + 0.088 + i * 0.176
            for dy in (-0.035, 0.035):
                props.nail(m, (x + random.uniform(-0.012, 0.012), y + dy, -0.04), (0, 0, -1), r=0.012)
    for y in (-0.7, 0.72):
        props.strap(m, (-w, y, 0.03), (0.2, y, 0.03), (0, 0, 1), width=0.055, nails=4, taper=0.45)
        m.tube([(-w - 0.012, y - 0.06, 0.02), (-w - 0.012, y + 0.06, 0.02)], [0.016, 0.016], 6, IRON, IRON_C, caps=True)
    # The ring he pulls it by, on both faces, and the lock's plate.
    for z, n in ((0.0, 1.0), (-0.04, -1.0)):
        props.strap(m, (0.3, 0.02, z), (0.3, 0.12, z), (0, 0, n), width=0.05, nails=0)
        props.ring(m, (0.3, 0.035, z + n * 0.014), (0, 0, n), r=0.05, thick=0.006)
    props.strap(m, (0.34, -0.2, -0.04), (0.34, -0.08, -0.04), (0, 0, -1), width=0.07, nails=0)
    m.poly([(0.332, -0.16, -0.0465), (0.348, -0.16, -0.0465), (0.345, -0.12, -0.0465), (0.335, -0.12, -0.0465)], "window_dark", (0.0, 0.0, 0.0, 1.0), facing=(0, 0, -1))


def door(p):
    door_leaf(p.part("HingeLeft"))
    door_leaf(props.Mirror(p.part("HingeRight")))


def candle(p):
    props.pot(p.soft, (0.0, 0.0, 0.0), [(0.0, 0.034), (0.012, 0.056), (0.024, 0.062)], colour=props.CLAY, sides=9, dark_inside=False)
    p.soft.poly([(math.cos(math.tau * i / 9) * 0.05, 0.009, math.sin(math.tau * i / 9) * 0.05) for i in range(9)], PAINT, rgba(props.CLAY, 0.6), facing=(0, 1, 0))
    props.candle(p.soft, (0.0, 0.009, 0.0), h=0.172, r=0.014, lean=0.03)


def lamp(p):
    """A hanging oil lamp about its flame's foot: a clay dish in an iron
    ring on three chains from a hook. It hangs wherever the scene puts it."""
    m = p.hard
    n = 10
    for i in range(n):
        a0, a1 = math.tau * i / n, math.tau * (i + 1) / n
        out = (math.cos((a0 + a1) * 0.5), 0.0, math.sin((a0 + a1) * 0.5))
        for r, way in ((0.078, 1.0), (0.072, -1.0)):
            m.poly([(math.cos(a0) * r, -0.012, math.sin(a0) * r), (math.cos(a1) * r, -0.012, math.sin(a1) * r), (math.cos(a1) * r, 0.012, math.sin(a1) * r), (math.cos(a0) * r, 0.012, math.sin(a0) * r)],
                   IRON, IRON_C, facing=(out[0] * way, 0.0, out[2] * way))
    for i in range(3):
        a = math.tau * i / 3 + 0.4
        foot = (math.cos(a) * 0.075, 0.01, math.sin(a) * 0.075)
        sag = (math.cos(a) * 0.045, 0.16, math.sin(a) * 0.045)
        m.tube([foot, sag, (0.0, 0.3, 0.0)], [0.0035, 0.0035, 0.0035], 4, IRON, IRON_C)
    props.ring(m, (0.0, 0.325, 0.0), (1, 0, 0), r=0.025, thick=0.004)
    m.tube([(0.0, 0.35, 0.0), (0.0, 0.52, 0.0)], [0.004, 0.004], 4, IRON, IRON_C)
    props.pot(p.soft, (0.0, -0.045, 0.0), [(0.0, 0.03), (0.02, 0.058), (0.05, 0.072)], colour=(0.03, 0.022, 0.017), sides=10, dark_inside=False)
    p.soft.poly([(math.cos(math.tau * i / 10) * 0.066, 0.0, math.sin(math.tau * i / 10) * 0.066) for i in range(10)], PAINT, (0.012, 0.01, 0.006, 1.0), facing=(0, 1, 0))
    p.soft.tube([(0.04, -0.002, 0.0), (0.05, 0.012, 0.0)], [0.004, 0.003], 4, PAINT, (0.05, 0.045, 0.035, 1.0))


BUILDERS = {
    "cot": cot, "bed": bed, "bed_slept": bed_slept, "bed_bare": bed_bare, "bed_raised": bed_raised, "desk": desk, "ledger": ledger, "stool": stool,
    "bench": bench, "table": trestle_table, "table_set": table_set, "table_jug": table_jug, "gate_bar": gate_bar, "well": well, "woodpile": woodpile,
    "door": door, "candle": candle, "lamp": lamp,
}

if __name__ == "__main__":
    props.run(BUILDERS)
