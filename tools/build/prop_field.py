"""What stands in the fields and along the road outside Aldgate (night 0,
the road in), each its own model (art/models/prop_field_<name>.glb):

- hedge: ten metres of bare winter hedge, a dark ragged mass with thorn
  shoots standing out of its top. Runs along x.
- fence: three wattle hurdles between stakes, 7 m, one sagging. Along x.
- gate: a five-barred field gate between two posts, hanging open a little.
- shrine: a wayside cross on steps with a little roofed niche, a candle
  burning in it (the scene, prop_field_shrine.tscn, gives it light).
- scarecrow: a pole and a crosspiece in a ragged coat, a sack for a head.
- rick: a round hayrick under a thatched cap, 3.4 m across.
- cot: a field cottage, cob and thatch, 7 by 4.5 m, one window lit, a
  lean-to at its end. Its front faces -z.
- mill: a post mill on its trestle, far off on a rise. The sails are
  their own object (Sails), turning about the windshaft.
- wreck: a cart wheel leaning on a stump and a broken one in the grass.
- bridge: planks over the road's ditch, 2.4 m wide, 3 m long (along z).
- stone: a mile stone, leaning.

They stand on the ground at their origin. Collision on the cot, the rick
and the mill only: nobody walks out here.

Run: tools/build.sh prop_field
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
import city_parts as cp
from porter import fbm

OAK = "wood_frame"
BOARDS = "wood_boards"


def wood(k=1.0):
    v = random.uniform(0.6, 0.85) * k
    return (v, v * 0.96, v * 0.9, 1.0)


def start(name, seed):
    porter.reset(seed)
    return porter.Mesh(name)


def hedge():
    m = start("Hedge", 5)
    n = 20
    length = 10.0
    rings = []
    for i in range(n + 1):
        x = -length * 0.5 + length * i / n
        end = min(i, n - i) / 2.0
        k = min(end, 1.0) * 0.5 + 0.5
        h = (1.5 + 0.5 * fbm(x, 0.0, 0.5, 2, 3.0) + random.uniform(-0.15, 0.2)) * k
        w = (0.75 + 0.2 * fbm(x, 3.0, 0.4, 2, 5.0)) * k
        prof = [(-w, -0.4), (-w * 0.95, h * 0.55), (-w * 0.45, h), (w * 0.4, h * 1.03), (w * 0.95, h * 0.5), (w, -0.4)]
        ring = []
        for j, (z, y) in enumerate(prof):
            shade = 0.3 + 0.5 * max(y, 0.0) / 2.0 + random.uniform(-0.06, 0.06)
            ring.append(m.vert(x + random.uniform(-0.1, 0.1), y, z + random.uniform(-0.08, 0.08), (shade, shade * 0.95, shade * 0.85, 1.0)))
        rings.append((ring, h, w, x))
    for (a, _h, _w, _x), (b, _h2, _w2, _x2) in zip(rings, rings[1:]):
        for j in range(5):
            m.face((a[j], b[j], b[j + 1], a[j + 1]), "hedge")
    # Thorn shoots out of the top and sides: flat spikes, both ways round.
    for _ in range(150):
        i = random.randint(1, n - 1)
        _ring, h, w, x = rings[i]
        x += random.uniform(-0.25, 0.25)
        z = random.uniform(-w, w) * 0.9
        y = h * (1.0 - 0.45 * (abs(z) / max(w, 0.01)) ** 2) - 0.1
        tall = random.uniform(0.35, 1.1)
        lean_x, lean_z = random.uniform(-0.3, 0.3), z * 0.5 + random.uniform(-0.2, 0.2)
        yaw = random.uniform(0.0, math.pi)
        dx, dz = math.cos(yaw) * 0.045, math.sin(yaw) * 0.045
        c = random.uniform(0.25, 0.5)
        col = (c, c * 0.93, c * 0.82, 1.0)
        pts = [(x - dx, y, z - dz), (x + dx, y, z + dz), (x + lean_x * tall, y + tall, z + lean_z * tall)]
        m.poly(pts, "hedge", col)
        m.poly(list(reversed(pts)), "hedge", col)
    m.build()
    porter.export("prop_field_hedge")


def fence():
    m = start("Fence", 6)
    for p in range(3):
        x0 = -3.5 + p * 2.35
        sag = (0.0, 0.0, 0.32)[p]
        for i in range(6):
            x = x0 + i * 2.25 / 5.0
            lean = sag * (i / 5.0)
            m.tube([(x, -0.3, 0.0), (x + lean * 0.3, 1.15 - lean * 0.4, lean)], [0.03, 0.022], 4, OAK, wood(0.8))
        # The weave: withies in and out of the stakes, as flat bands each side.
        y = 0.12
        k = 0
        while y < 0.98:
            c = wood(0.9 if k % 2 else 0.7)
            for s in (-1, 1):
                pts = [(x0 - 0.05, y, s * 0.035), (x0 + 2.3, y - sag * 0.35, s * 0.035 + sag), (x0 + 2.3, y + 0.085 - sag * 0.35, s * 0.035 + sag),
                       (x0 - 0.05, y + 0.085, s * 0.035)]
                m.poly(pts, "hedge", c, facing=(0, 0, s))
            y += 0.095
            k += 1
    m.build()
    porter.export("prop_field_fence")


def gate():
    m = start("Gate", 7)
    for x in (-1.6, 1.6):
        m.tube([(x, -0.4, 0.0), (x + 0.02, 1.45, 0.0), (x + 0.02, 1.5, 0.0)], [0.11, 0.09, 0.04], 6, OAK, wood(0.7), caps=True)
    # It hangs from the west post, swung open a hand's breadth and dropped at the latch.
    ang = math.radians(14.0)
    c, s = math.cos(ang), math.sin(ang)

    def at(u, y):
        return (-1.5 + u * c, y - 0.05 * u / 3.0, u * s)

    for y in (0.25, 0.48, 0.71, 0.94, 1.2):
        a, b = at(0.0, y), at(3.0, y)
        col = wood()
        for sgn in (-1, 1):
            pts = [(a[0], a[1] - 0.045, a[2] + sgn * 0.02), (b[0], b[1] - 0.045, b[2] + sgn * 0.02), (b[0], b[1] + 0.045, b[2] + sgn * 0.02),
                   (a[0], a[1] + 0.045, a[2] + sgn * 0.02)]
            m.poly(pts, BOARDS, col, facing=(-s * sgn, 0, c * sgn))
    for u0, y0, u1, y1 in ((0.0, 0.2, 0.0, 1.3), (3.0, 0.2, 3.0, 1.25), (0.05, 0.25, 2.95, 1.2), (1.5, 0.2, 1.5, 1.25)):
        a, b = at(u0, y0), at(u1, y1)
        m.tube([(a[0], a[1], a[2]), (b[0], b[1], b[2])], [0.04, 0.04], 4, BOARDS, wood(0.8), squash=(1.0, 0.5))
    m.build()
    porter.export("prop_field_gate")


def shrine():
    m = start("Shrine", 8)
    stone = (0.82, 0.81, 0.78, 1.0)
    damp = (0.45, 0.5, 0.42, 1.0)
    for i, half in enumerate((0.85, 0.6, 0.4)):
        m.box((-half, 0.2 * i - 0.2, -half), (half, 0.2 * (i + 1) - 0.2, half), "stone_ashlar", damp, stone, faces="xXzZY")
    m.box((-0.17, 0.4, -0.17), (0.17, 1.55, 0.17), "stone_ashlar", stone, faces="xXzZ")
    # The niche: a little house of stone on the shaft, open to the road (-z), a figure and a candle inside.
    m.box((-0.3, 1.55, -0.24), (0.3, 2.15, 0.24), "stone_ashlar", stone, faces="xXZy")
    for x0, x1 in ((-0.3, -0.2), (0.2, 0.3)):
        m.box((x0, 1.55, -0.24), (x1, 2.15, -0.2), "stone_ashlar", stone, faces="xXz")
    m.poly([(-0.2, 1.6, -0.02), (0.2, 1.6, -0.02), (0.2, 2.15, -0.02), (-0.2, 2.15, -0.02)], "window_dark", facing=(0, 0, -1))
    m.tube([(0.07, 1.6, -0.08), (0.07, 1.74, -0.08), (0.07, 1.98, -0.08), (0.07, 2.06, -0.08)], [0.07, 0.075, 0.05, 0.02], 5, "stone_ashlar",
           (0.6, 0.6, 0.58, 1.0), caps=True)
    m.box((-0.2, 1.55, -0.24), (0.2, 1.6, -0.02), "stone_ashlar", stone, faces="zY")
    for s in (-1, 1):
        pts = [(s * 0.4, 2.1, -0.34), (s * 0.4, 2.1, 0.3), (0.0, 2.48, 0.3), (0.0, 2.48, -0.34)]
        m.poly(pts, "stone_ashlar", (0.6, 0.6, 0.6, 1.0), facing=(s, 1, 0))
        m.poly(pts, "stone_ashlar", (0.3, 0.3, 0.3, 1.0), facing=(-s, -1, 0))
    m.poly([(-0.3, 2.15, -0.24), (0.3, 2.15, -0.24), (0.0, 2.44, -0.24)], "stone_ashlar", stone, facing=(0, 0, -1))
    m.box((-0.03, 2.45, -0.04), (0.03, 2.95, 0.04), "stone_ashlar", stone, faces="xXzZY")
    m.box((-0.2, 2.68, -0.035), (0.2, 2.76, 0.035), "stone_ashlar", stone, faces="xXzZyY")
    m.build()
    # The candle's flame, its own object so the scene can find it.
    f = porter.Mesh("Flame")
    f.box((-0.115, 1.6, -0.13), (-0.085, 1.72, -0.1), "painted", porter.srgb(0.75, 0.7, 0.58))
    for a in (0.0, math.pi / 2):
        dx, dz = math.cos(a) * 0.03, math.sin(a) * 0.03
        f.quad((-0.1 - dx, 1.72, -0.115 - dz), (-0.1 + dx, 1.72, -0.115 + dz), (-0.1 + dx, 1.84, -0.115 + dz), (-0.1 - dx, 1.84, -0.115 - dz), "flame",
               uvs=[(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
    f.build()
    porter.export("prop_field_shrine")


def scarecrow():
    m = start("Scarecrow", 9)
    m.tube([(0.0, -0.4, 0.0), (0.05, 1.2, 0.0), (0.09, 2.1, 0.02)], [0.05, 0.04, 0.035], 5, OAK, wood(0.7))
    m.tube([(-0.85, 1.62, 0.0), (0.07, 1.7, 0.0), (0.95, 1.58, 0.03)], [0.03, 0.035, 0.03], 4, OAK, wood(0.7))
    rag = lambda k=1.0: tuple(c * k for c in porter.srgb(0.2, 0.18, 0.15)[:3]) + (1.0,)
    # The coat: a sack over the crosspiece, hanging in tatters.
    for s in (-1, 1):
        top = [(-0.8, 1.66, s * 0.05), (-0.3, 1.74, s * 0.09), (0.07, 1.76, s * 0.1), (0.45, 1.72, s * 0.09), (0.9, 1.62, s * 0.05)]
        hem = [(-0.82, 1.2, s * 0.03), (-0.34, 0.75, s * 0.13), (0.05, 0.6, s * 0.15), (0.42, 0.82, s * 0.12), (0.88, 1.28, s * 0.03)]
        for i in range(4):
            k = 0.7 + 0.3 * ((i * 3 + (s > 0)) % 3) / 2.0
            ragged = 0.18 * ((i * 7 + (s > 0) * 3) % 4) / 3.0
            pts = [top[i], top[i + 1], (hem[i + 1][0], hem[i + 1][1] + ragged, hem[i + 1][2]), (hem[i][0], hem[i][1] - ragged * 0.5, hem[i][2])]
            m.poly(pts, "sacking", [rag(k), rag(k), rag(k * 0.5), rag(k * 0.5)], facing=(0, 0, s))
    # The head: a stuffed sack, lolling, under a broken hat.
    m.tube([(0.08, 1.78, 0.0), (0.1, 1.86, 0.02), (0.14, 2.02, 0.05), (0.17, 2.14, 0.07)], [0.07, 0.15, 0.16, 0.06], 7, "sacking", rag(1.5), caps=True)
    brim = [(0.17 + math.cos(math.tau * i / 8) * 0.3, 2.13 + 0.05 * math.sin(i * 2.0), 0.07 + math.sin(math.tau * i / 8) * 0.3) for i in range(8)]
    m.poly(brim, "sacking", rag(0.6), facing=(0, 1, 0))
    m.poly(brim, "sacking", rag(0.4), facing=(0, -1, 0))
    m.tube([(0.17, 2.13, 0.07), (0.19, 2.3, 0.08)], [0.14, 0.09], 6, "sacking", rag(0.6), caps=True)
    m.build()
    porter.export("prop_field_scarecrow")


def rick():
    m = start("Rick", 10)
    sides = 12
    straw = lambda x, y, z: tuple(c * (0.75 + 0.3 * fbm(x * 2.0, y * 2.0 + z, 0.6, 2, 2.0)) * (0.55 + 0.45 * min(y / 2.0, 1.0)) for c in (0.8, 0.72, 0.5)) + (1.0,)
    cp.drum(m, 0.0, 0.0, [-0.2, 0.9, 2.0, 2.2], [1.55, 1.75, 1.7, 1.85], sides, "straw", straw)
    cp.drum(m, 0.0, 0.0, [2.15, 3.2, 3.9], [1.9, 0.9, 0.08], sides, "straw", lambda x, y, z: tuple(c * 0.7 for c in straw(x, y, z)[:3]) + (1.0,))
    m.tube([(0.0, 3.8, 0.0), (0.03, 4.25, 0.0)], [0.035, 0.02], 4, OAK, wood(0.6))
    m.build(smooth=True)
    c = porter.Mesh("Rick-colonly")
    c.box((-1.3, 0.0, -1.3), (1.3, 3.0, 1.3), "straw")
    c.build()
    porter.export("prop_field_rick")


def cot():
    m = start("Cot", 11)
    x0, x1, z0, z1, eave, ridge = -3.5, 3.5, 0.0, 4.5, 2.0, 4.7
    tint = lambda x, y, z: tuple(c * (0.8 + 0.25 * fbm(x + z, y, 0.4, 2, 4.0)) * (0.6 + 0.4 * min(max(y, 0.0) / 0.8, 1.0)) for c in (0.82, 0.78, 0.7)) + (1.0,)
    cp.panel(m, (x0, z0), (x1, z0), -0.2, eave, (0, 0, -1), "plaster_daub", tint, 1.8, 1.2)
    cp.panel(m, (x0, z1), (x1, z1), -0.2, eave, (0, 0, 1), "plaster_daub", tint, 1.8, 1.2)
    for x, s in ((x0, -1), (x1, 1)):
        cp.panel(m, (x, z0), (x, z1), -0.2, eave, (s, 0, 0), "plaster_daub", tint, 1.6, 1.2)
        pts = [(x, eave, z0), (x, eave, z1), (x, ridge, (z0 + z1) * 0.5)]
        m.poly(pts, "plaster_daub", [tint(*p) for p in pts], facing=(s, 0, 0))
    # The thatch: thick, low over the walls, sagging along the ridge.
    over = 0.55
    mid = (z0 + z1) * 0.5
    xs = cp.steps(x0 - over, x1 + over, 1.6)
    for xa, xb in zip(xs, xs[1:]):
        ry = lambda x: ridge - 0.22 * math.sin(math.pi * (x - x0 + over) / (x1 - x0 + 2 * over)) + 0.05 * math.sin(x * 2.3)
        for s in (-1, 1):
            edge = mid + s * ((z1 - z0) * 0.5 + over)
            pts = [(xa, eave - 0.45, edge), (xb, eave - 0.45, edge), (xb, ry(xb), mid), (xa, ry(xa), mid)]
            k = 0.5 + 0.12 * math.sin(xa * 1.7 + s)
            m.poly(pts, "straw", [(k * 0.7, k * 0.64, k * 0.48, 1.0)] * 2 + [(k, k * 0.92, k * 0.7, 1.0)] * 2, facing=(0, 1, s * 0.6))
            m.poly(pts, "straw", (0.12, 0.11, 0.09, 1.0), facing=(0, -1, -s * 0.6))
            m.poly([(xa, eave - 0.45, edge), (xb, eave - 0.45, edge), (xb, eave - 0.2, edge - s * 0.02), (xa, eave - 0.2, edge - s * 0.02)], "straw",
                   (0.3, 0.27, 0.2, 1.0), facing=(0, -0.2, s))
    # A door, low, and one window with a light behind its shutter's gaps.
    m.poly([(-0.2, -0.1, z0 - 0.03), (0.75, -0.1, z0 - 0.03), (0.75, 1.65, z0 - 0.03), (-0.2, 1.65, z0 - 0.03)], BOARDS, wood(0.7), facing=(0, 0, -1))
    for x in (-0.26, 0.81):
        m.box((x - 0.06, -0.1, z0 - 0.07), (x + 0.06, 1.75, z0), OAK, wood(0.6), faces="xXz")
    m.box((-0.32, 1.65, z0 - 0.08), (0.87, 1.8, z0), OAK, wood(0.6), faces="xXzy")
    m.build()
    w = porter.Mesh("Window0_0")
    w.poly([(-2.3, 0.95, z0 - 0.03), (-1.5, 0.95, z0 - 0.03), (-1.5, 1.6, z0 - 0.03), (-2.3, 1.6, z0 - 0.03)], "window_candle",
           uvs=[(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)], facing=(0, 0, -1))
    w.build(origin=(-1.9, 1.3, z0))
    e = porter.Mesh("Extras")
    for x in (-2.38, -1.42):
        e.box((x - 0.05, 0.88, z0 - 0.07), (x + 0.05, 1.67, z0), OAK, wood(0.6), faces="xXz")
    for y in (0.88, 1.62):
        e.box((-2.4, y, z0 - 0.07), (-1.4, y + 0.07, z0), OAK, wood(0.6), faces="zyY")
    # The lean-to at the east end: boards under a thatch slope, for the beasts.
    lx0, lx1 = x1, x1 + 2.2
    boards = cp.wood_tint((0.75, 0.7, 0.64), 3.0, 0.25)
    cp.panel(e, (lx0, z0 + 0.6), (lx1, z0 + 0.6), -0.1, 1.5, (0, 0, -1), BOARDS, boards, 2.5, 2.0)
    cp.panel(e, (lx1, z0 + 0.6), (lx1, z1 - 0.3), -0.1, 1.5, (1, 0, 0), BOARDS, boards, 2.5, 2.0)
    cp.panel(e, (lx0, z1 - 0.3), (lx1, z1 - 0.3), -0.1, 1.5, (0, 0, 1), BOARDS, boards, 2.5, 2.0)
    roof = [(lx1 + 0.3, 1.35, z0 + 0.3), (lx1 + 0.3, 1.35, z1), (lx0, 2.3, z1), (lx0, 2.3, z0 + 0.3)]
    e.poly(roof, "straw", (0.42, 0.38, 0.28, 1.0), facing=(1, 1, 0))
    e.poly(roof, "straw", (0.1, 0.1, 0.08, 1.0), facing=(-1, -1, 0))
    # A woodpile and a chopping block by the door.
    for i in range(7):
        e.tube([(1.5 + (i % 4) * 0.22, 0.1 + (i // 4) * 0.2, z0 - 0.75), (1.5 + (i % 4) * 0.22, 0.1 + (i // 4) * 0.2, z0 - 0.1)], [0.1, 0.1], 5, "bark",
               wood(0.8), caps=True)
    e.tube([(2.9, -0.1, z0 - 1.3), (2.9, 0.45, z0 - 1.3)], [0.24, 0.22], 7, "bark", wood(0.8), caps=True)
    e.build()
    c = porter.Mesh("Walls-colonly")
    c.box((x0, 0.0, z0), (x1, ridge, z1), "plaster_daub")
    c.build()
    porter.export("prop_field_cot")


def mill():
    m = start("Mill", 12)
    boards = cp.wood_tint((0.7, 0.67, 0.62), 2.0, 0.3)
    dark = (0.3, 0.29, 0.27, 1.0)
    # The trestle: a great post on cross-trees, four quarter bars up to it.
    m.tube([(0.0, 0.0, 0.0), (0.0, 4.2, 0.0)], [0.35, 0.3], 8, OAK, wood(0.6))
    for a in range(4):
        ang = math.pi / 4 + a * math.pi / 2
        c, s = math.cos(ang), math.sin(ang)
        m.tube([(c * 3.2, 0.25, s * 3.2), (0.0, 0.3, 0.0)], [0.16, 0.16], 4, OAK, wood(0.55))
        m.tube([(c * 2.9, 0.3, s * 2.9), (c * 0.2, 3.2, s * 0.2)], [0.13, 0.13], 4, OAK, wood(0.55))
        m.box((c * 3.2 - 0.35, -0.3, s * 3.2 - 0.35), (c * 3.2 + 0.35, 0.25, s * 3.2 + 0.35), "stone_rubble", (0.6, 0.6, 0.58, 1.0), faces="xXzZY")
    # The buck: a boarded box that turns on the post, its roof a pointed arch; the sails are on its -z face.
    x0, x1, z0, z1, y0, y1 = -1.9, 1.9, -2.3, 2.5, 3.6, 8.0
    cp.slab(m, (x0, y0, z0), (x1, y1, z1), BOARDS, boards, faces="xXzZ", step=2.0)
    m.poly([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], BOARDS, dark, facing=(0, -1, 0))
    prof = [(x0 - 0.15, y1 - 0.1), (x0 * 0.72, y1 + 1.0), (0.0, y1 + 1.55), (x1 * 0.72, y1 + 1.0), (x1 + 0.15, y1 - 0.1)]
    for (xa, ya), (xb, yb) in zip(prof, prof[1:]):
        pts = [(xa, ya, z0 - 0.2), (xb, yb, z0 - 0.2), (xb, yb, z1 + 0.2), (xa, ya, z1 + 0.2)]
        m.poly(pts, BOARDS, [cp.wood_tint((0.5, 0.48, 0.46), 9.0, 0.4)(*p) for p in pts], facing=((xa + xb) * 0.5, 1.0, 0.0))
    for z, s in ((z0, -1), (z1, 1)):
        pts = [(x0, y1, z), (x0 * 0.72, y1 + 1.0, z), (0.0, y1 + 1.5, z), (x1 * 0.72, y1 + 1.0, z), (x1, y1, z)]
        m.poly(pts, BOARDS, [boards(*p) for p in pts], facing=(0, 0, s))
    # The tail pole, down to the ground behind, for turning her into the wind; the ladder beside it.
    m.tube([(0.0, y0 + 0.3, z1), (0.0, 0.6, z1 + 6.5)], [0.13, 0.1], 5, OAK, wood(0.6))
    for x in (-0.55, 0.55):
        m.tube([(x, y0 + 0.2, z1 + 0.05), (x, 0.0, z1 + 3.4)], [0.06, 0.06], 4, OAK, wood(0.7))
    for i in range(1, 11):
        k = i / 11.0
        m.box((-0.55, y0 + 0.2 - (y0 + 0.2) * k - 0.02, z1 + 0.05 + 3.35 * k - 0.1), (0.55, y0 + 0.2 - (y0 + 0.2) * k + 0.02, z1 + 0.05 + 3.35 * k + 0.1),
              BOARDS, wood(0.8), faces="zZyY")
    m.poly([(-0.3, y0 + 1.6, z0 - 0.02), (0.3, y0 + 1.6, z0 - 0.02), (0.3, y0 + 2.3, z0 - 0.02), (-0.3, y0 + 2.3, z0 - 0.02)], "window_dark", facing=(0, 0, -1))
    m.build()
    # The sails: four, on stocks through the windshaft's head; lattice frames, the cloths furled.
    hub = (0.0, 6.9, z0 - 0.75)
    sl = porter.Mesh("Sails")
    sl.tube([(0.0, 6.9, z0 + 0.3), (0.0, 6.9, z0 - 0.9)], [0.2, 0.17], 6, OAK, wood(0.55), caps=True)
    for k in range(4):
        ang = k * math.pi / 2 + 0.3
        c, s = math.cos(ang), math.sin(ang)

        def at(r, w, dz=0.0):
            # r out along the sail, w across it (the trailing side).
            return (hub[0] + c * r - s * w, hub[1] + s * r + c * w, hub[2] - 0.05 + dz)

        a, b = at(0.0, 0.0), at(6.2, 0.0)
        sl.tube([a, b], [0.11, 0.06], 4, OAK, wood(0.6))
        for w in (0.55, 1.15):
            sl.tube([at(1.2, w, -0.08), at(6.1, w, -0.12)], [0.03, 0.03], 3, OAK, wood(0.7))
        r = 1.2
        while r < 6.2:
            sl.tube([at(r, -0.25), at(r, 1.2, -0.12)], [0.025, 0.025], 3, OAK, wood(0.7))
            r += 0.62
    sl.build(origin=hub)
    col = porter.Mesh("Buck-colonly")
    col.box((x0, 0.0, z0), (x1, y1, z1), BOARDS)
    col.build()
    porter.export("prop_field_mill")


def wreck():
    m = start("Wreck", 13)
    m.tube([(0.0, -0.2, 0.0), (0.0, 0.7, 0.0)], [0.26, 0.22], 7, "bark", wood(0.7), caps=True)

    def wheel(centre, axis, up, r, broken):
        ax, ux = axis, up
        side = (ax[1] * ux[2] - ax[2] * ux[1], ax[2] * ux[0] - ax[0] * ux[2], ax[0] * ux[1] - ax[1] * ux[0])
        n = 12
        def at(a, rr, off=0.0):
            ca, sa = math.cos(a) * rr, math.sin(a) * rr
            return tuple(centre[i] + ux[i] * sa + side[i] * ca + ax[i] * off for i in range(3))
        for i in range(n):
            if broken and i in (2, 3, 4):
                continue
            a0, a1 = math.tau * i / n, math.tau * (i + 1) / n
            col = wood(0.75)
            for off in (-0.04, 0.04):
                pts = [at(a0, r - 0.08, off), at(a1, r - 0.08, off), at(a1, r, off), at(a0, r, off)]
                m.poly(pts, OAK, col, facing=tuple(ax[j] * off for j in range(3)))
            pts = [at(a0, r, -0.04), at(a1, r, -0.04), at(a1, r, 0.04), at(a0, r, 0.04)]
            mid = at((a0 + a1) * 0.5, 1.0)
            m.poly(pts, "iron_cart", (0.45, 0.43, 0.42, 1.0), facing=tuple(mid[j] - centre[j] for j in range(3)))
        for i in range(8):
            if broken and i in (1, 2):
                continue
            a = math.tau * i / 8 + 0.2
            m.tube([at(a, 0.07), at(a, r - 0.07)], [0.022, 0.02], 4, OAK, wood(0.8))
        m.tube([at(0.0, 0.0, -0.09), at(0.0, 0.0, 0.09)], [0.08, 0.08], 6, OAK, wood(0.6), caps=True)

    lean = math.radians(18.0)
    wheel((0.0, 0.58, -0.42), (0.0, math.sin(lean), -math.cos(lean)), (0.0, math.cos(lean), math.sin(lean)), 0.62, False)
    wheel((1.5, 0.07, 0.6), (0.08, 1.0, 0.05), (1.0, -0.08, 0.0), 0.62, True)
    m.box((0.9, 0.0, -0.9), (2.6, 0.06, -0.72), BOARDS, wood(0.7))
    m.build()
    porter.export("prop_field_wreck")


def bridge():
    m = start("Bridge", 14)
    for i in range(7):
        x = -1.2 + i * 0.345
        sag = 0.02 * ((i * 5) % 3)
        m.box((x, 0.06 - sag, -1.55 - 0.05 * ((i * 3) % 2)), (x + 0.33, 0.12 - sag, 1.55 + 0.06 * ((i * 7) % 3)), BOARDS, wood(0.85))
    for x in (-1.0, 0.95):
        m.tube([(x, -0.02, -1.5), (x, -0.02, 1.5)], [0.1, 0.1], 5, "bark", wood(0.6), caps=True)
    m.build()
    porter.export("prop_field_bridge")


def stone():
    m = start("Stone", 15)
    pts = [(0.0, -0.3, 0.0), (0.03, 0.3, 0.0), (0.08, 0.72, 0.01), (0.1, 0.84, 0.01)]
    m.tube(pts, [0.2, 0.19, 0.17, 0.08], 6, "stone_rubble", [(0.45, 0.5, 0.42, 1.0), (0.7, 0.7, 0.68, 1.0), (0.8, 0.8, 0.78, 1.0), (0.8, 0.8, 0.78, 1.0)],
           caps=True, squash=(1.0, 0.6))
    m.build()
    porter.export("prop_field_stone")


def main():
    for fn in (hedge, fence, gate, shrine, scarecrow, rick, cot, mill, wreck, bridge, stone):
        fn()


if __name__ == "__main__":
    main()
