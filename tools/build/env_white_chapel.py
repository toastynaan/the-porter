"""The white chapel in the fields (night 0, the road in: "past the white
chapel"): a small limewashed chapel of the kind that stood by a road
outside a city gate, with its yard.

In its own space the nave runs along x: the tower at the west end (-x), the
chancel at the east (+x), and the road side is -z, where the porch and the
yard's gate are. The origin is the middle of the nave's floor.

- A nave and a lower chancel under steep slate roofs; a square west tower
  with a low pyramid cap and louvred belfry openings; a gabled north porch;
  corner buttresses; a stone plinth.
- Lancet windows. The glass is its own material (window_candle): candles
  are lit inside for Vespers.
- New this autumn, south of the chancel: a row of fresh mounds with no
  markers, and one grave dug and left open with the spade in its heap.
- The yard: a low rubble wall with a timber gate, a preaching cross on
  steps, grave mounds with leaning wooden markers and a few stone slabs.

Walls are limewash over rubble (plaster_white), darkened by damp at the foot
and under the eaves through vertex colour. Collision: the three blocks of
the building.

Run: tools/build.sh env_white_chapel
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter

# The nave, chancel and tower: x from, x to, half width, wall height, ridge height.
NAVE = (-5.0, 5.0, 3.2, 4.3, 7.9)
CHANCEL = (5.0, 10.0, 2.6, 3.6, 6.4)
TOWER = (-8.6, -5.0, 1.8, 10.6, 12.6)
# The yard, about the origin: x from, x to, z from, z to (the gate is in the -z side).
YARD = (-21.0, 17.0, -8.5, 11.5)
GATE_X = (2.0, 4.4)

LIME = "plaster_lime"
CUT = "stone_ashlar"
DAMP = (0.5, 0.56, 0.5, 1.0)
CLEAN = (0.92, 0.92, 0.9, 1.0)
EAVE = (0.66, 0.67, 0.68, 1.0)
STONE = (0.8, 0.8, 0.78, 1.0)
DARK_STONE = (0.55, 0.56, 0.55, 1.0)


def wall(m, a, b, y0, y1, out, mat="plaster_lime"):
    """A wall face from (x, z) `a` to `b`, in three bands up it: damp at the
    foot, clean, shadowed under the eaves."""
    foot = min(y0 + 0.9, y1)
    eave = max(y1 - 0.6, foot)
    for lo, hi, c_lo, c_hi in ((y0, foot, DAMP, CLEAN), (foot, eave, CLEAN, CLEAN), (eave, y1, CLEAN, EAVE)):
        if hi - lo < 1e-4:
            continue
        m.poly([(a[0], lo, a[1]), (b[0], lo, b[1]), (b[0], hi, b[1]), (a[0], hi, a[1])], mat,
               [c_lo, c_lo, c_hi, c_hi], facing=out)


def block(m, x0, x1, half, y0, y1, ends="xX", mat="plaster_lime"):
    """Four walls round a rectangle (x0..x1 by -half..half)."""
    wall(m, (x0, -half), (x1, -half), y0, y1, (0, 0, -1), mat)
    wall(m, (x0, half), (x1, half), y0, y1, (0, 0, 1), mat)
    if "x" in ends:
        wall(m, (x0, -half), (x0, half), y0, y1, (-1, 0, 0), mat)
    if "X" in ends:
        wall(m, (x1, -half), (x1, half), y0, y1, (1, 0, 0), mat)


def gable_roof(m, x0, x1, half, eave_y, ridge_y, over=0.3, gables="xX"):
    """A pitched roof with its ridge along x, slates, and the gable walls under it."""
    run = half + over
    drop = (ridge_y - eave_y) * over / half
    slope = math.hypot(run, ridge_y - eave_y + drop)
    for side in (-1, 1):
        pts = [(x0 - over, eave_y - drop, side * run), (x1 + over, eave_y - drop, side * run),
               (x1 + over, ridge_y, 0.0), (x0 - over, ridge_y, 0.0)]
        length = x1 - x0 + 2 * over
        m.poly(pts, "roof_slates", (0.85, 0.85, 0.86, 1.0),
               [(0.0, 0.0), (length / 3.0, 0.0), (length / 3.0, slope / 3.0), (0.0, slope / 3.0)], facing=(0, 1, side * 0.5))
        # The underside, so the overhang isn't see-through.
        m.poly(pts, "roof_slates", (0.3, 0.3, 0.3, 1.0), facing=(0, -1, -side * 0.5))
    for end, x in (("x", x0), ("X", x1)):
        if end in gables:
            m.poly([(x, eave_y, -half), (x, eave_y, half), (x, ridge_y, 0.0)], LIME, [EAVE, EAVE, CLEAN],
                   facing=(-1 if end == "x" else 1, 0, 0))


def lancet(m, centre, y0, width, height, out, glow=True, proud=0.04):
    """A pointed window on a wall: a stone surround and the glass in it.
    `centre` is (x, z) on the wall's face; `out` the way the wall looks."""
    ox, oz = out[0], out[2]
    ax, az = -oz, ox  # along the wall

    def shape(w, h, lift, off):
        hw = w * 0.5
        spring = y0 + lift + h - w * 0.9
        return [(centre[0] + ax * -hw + ox * off, y0 + lift, centre[1] + az * -hw + oz * off),
                (centre[0] + ax * hw + ox * off, y0 + lift, centre[1] + az * hw + oz * off),
                (centre[0] + ax * hw + ox * off, spring, centre[1] + az * hw + oz * off),
                (centre[0] + ox * off, y0 + lift + h, centre[1] + oz * off),
                (centre[0] + ax * -hw + ox * off, spring, centre[1] + az * -hw + oz * off)]

    m.poly(shape(width + 0.34, height + 0.3, -0.12, proud), CUT, DARK_STONE, facing=out)
    # The glass: UV 0..1 across it and up it, for its leading.
    m.poly(shape(width, height, 0.0, proud + 0.02), "window_candle" if glow else "window_dark",
           uvs=[(0.0, 0.0), (1.0, 0.0), (1.0, 1.0 - 0.9 * width / height), (0.5, 1.0), (0.0, 1.0 - 0.9 * width / height)], facing=out)


def buttress(m, x, z, dx, dz, height):
    """A stepped buttress standing out from a corner, toward (dx, dz)."""
    for width, depth, top in ((0.62, 0.95, height * 0.55), (0.5, 0.6, height)):
        lo = (min(x, x + dx * depth) - (width * 0.5 if dx == 0 else 0.0), 0.0,
              min(z, z + dz * depth) - (width * 0.5 if dz == 0 else 0.0))
        hi = (max(x, x + dx * depth) + (width * 0.5 if dx == 0 else 0.0), top,
              max(z, z + dz * depth) + (width * 0.5 if dz == 0 else 0.0))
        m.box(lo, hi, CUT, DARK_STONE, STONE, faces="xXzZY")


def chapel(m):
    nx0, nx1, nh, nw, nr = NAVE
    cx0, cx1, ch, cw, cr = CHANCEL
    tx0, tx1, th, tw, tr = TOWER
    # A stone plinth under it all, standing a hand proud of the walls.
    for x0, x1, half in ((nx0, nx1, nh), (cx0, cx1, ch), (tx0, tx1, th)):
        m.box((x0 - 0.08, -0.4, -half - 0.08), (x1 + 0.08, 0.45, half + 0.08), CUT, DARK_STONE, STONE,
              faces="xXzZY")
    # (Its west wall too: the tower is narrower than the nave, and the wall shows each side of it.)
    block(m, nx0, nx1, nh, 0.45, nw, ends="xX")
    gable_roof(m, nx0, nx1, nh, nw, nr, gables="xX")
    block(m, cx0, cx1, ch, 0.45, cw, ends="X")
    gable_roof(m, cx0, cx1, ch, cw, cr, gables="X")
    # A weathercock's rod and a cross on the tower's point; a sanctus bell in a cote on the nave's east gable.
    tm = (TOWER[0] + TOWER[1]) * 0.5
    m.tube([(tm, TOWER[4] - 0.1, 0.0), (tm, TOWER[4] + 1.5, 0.0)], [0.035, 0.02], 4, "iron_cart", (0.5, 0.5, 0.5, 1.0))
    m.box((tm - 0.3, TOWER[4] + 1.0, -0.02), (tm + 0.3, TOWER[4] + 1.07, 0.02), "iron_cart", (0.5, 0.5, 0.5, 1.0))
    for z in (-0.42, 0.3):
        m.box((nx1 - 0.2, nr - 0.25, z), (nx1 + 0.2, nr + 0.95, z + 0.12), CUT, DARK_STONE, STONE, faces="xXzZ")
    for s in (-1, 1):
        m.poly([(nx1 - 0.3, nr + 0.9, s * 0.55), (nx1 + 0.3, nr + 0.9, s * 0.55), (nx1 + 0.3, nr + 1.3, 0.0), (nx1 - 0.3, nr + 1.3, 0.0)], CUT,
               STONE, facing=(0, 1, s))
    m.tube([(nx1, nr + 0.75, -0.02), (nx1, nr + 0.55, -0.02), (nx1, nr + 0.3, -0.02)], [0.05, 0.13, 0.17], 6, "iron_cart", (0.45, 0.42, 0.36, 1.0))
    block(m, tx0, tx1, th, 0.45, tw)
    # The tower's string courses and its cap: a low pyramid behind a plain parapet.
    for y in (4.6, 8.2, tw - 0.25):
        m.box((tx0 - 0.07, y, -th - 0.07), (tx1 + 0.07, y + 0.22, th + 0.07), CUT, STONE, faces="xXzZyY")
    mid = (tx0 + tx1) * 0.5
    over = 0.25
    corners = [(tx0 - over, tw, -th - over), (tx1 + over, tw, -th - over), (tx1 + over, tw, th + over), (tx0 - over, tw, th + over)]
    for i in range(4):
        a, b = corners[i], corners[(i + 1) % 4]
        out = ((a[0] + b[0]) * 0.5 - mid, 0.6, (a[2] + b[2]) * 0.5)
        m.poly([a, b, (mid, tr, 0.0)], "roof_slates", (0.8, 0.8, 0.82, 1.0), [(0.0, 0.0), (1.4, 0.0), (0.7, 1.0)], facing=out)
    m.poly(corners, "roof_slates", (0.25, 0.25, 0.25, 1.0), facing=(0, -1, 0))
    # Belfry openings, louvred and dark, high on each face; a slit lower down.
    for out, centre in (((0, 0, -1), (mid, -th)), ((0, 0, 1), (mid, th)), ((-1, 0, 0), (tx0, 0.0))):
        lancet(m, centre, 8.7, 0.7, 1.5, out, glow=False)
        lancet(m, centre, 5.3, 0.28, 0.9, out, glow=False)
    # Windows: two each side of the nave, one each side of the chancel, three at the east end.
    for side in (-1, 1):
        for x in (-1.6, 2.7):
            lancet(m, (x, side * nh), 1.7, 0.62, 2.0, (0, 0, side))
        lancet(m, (7.4, side * ch), 1.5, 0.55, 1.7, (0, 0, side))
    for z, h in ((-0.8, 1.9), (0.0, 2.5), (0.8, 1.9)):
        lancet(m, (cx1, z), 1.5, 0.5, h, (1, 0, 0))
    # Buttresses at the corners.
    for x, z, dx, dz in ((nx1, -nh + 0.3, 0, -1), (nx1, nh - 0.3, 0, 1), (cx1 - 0.3, -ch, 0, -1), (cx1 - 0.3, ch, 0, 1),
                         (tx0 + 0.3, -th, 0, -1), (tx0 + 0.3, th, 0, 1), (tx0, -th + 0.3, -1, 0), (tx0, th - 0.3, -1, 0)):
        buttress(m, x, z, dx, dz, 3.2 if x > tx1 else 4.4)
    # The north porch: gabled, open to the road, the door dark within.
    px0, px1, pz0, pz1 = -4.2, -1.9, -nh - 2.3, -nh
    wall(m, (px0, pz0), (px0, pz1), 0.0, 2.3, (-1, 0, 0))
    wall(m, (px1, pz0), (px1, pz1), 0.0, 2.3, (1, 0, 0))
    wall(m, (px0 + 0.3, pz0), (px0 + 0.3, pz1), 0.0, 2.3, (1, 0, 0))
    wall(m, (px1 - 0.3, pz0), (px1 - 0.3, pz1), 0.0, 2.3, (-1, 0, 0))
    pm = (px0 + px1) * 0.5
    for side, x_out in ((-1, px0 - 0.25), (1, px1 + 0.25)):
        pts = [(x_out, 2.1, pz0 - 0.3), (x_out, 2.1, pz1), (pm, 3.5, pz1), (pm, 3.5, pz0 - 0.3)]
        m.poly(pts, "roof_slates", (0.82, 0.82, 0.84, 1.0), [(0.0, 0.0), (0.9, 0.0), (0.9, 0.6), (0.0, 0.6)], facing=(side, 1, 0))
        m.poly(pts, "roof_slates", (0.25, 0.25, 0.25, 1.0), facing=(-side, -1, 0))
    # Its front: two jambs, the gable over them, and the dark between.
    for x0, x1 in ((px0, px0 + 0.45), (px1 - 0.45, px1)):
        wall(m, (x0, pz0), (x1, pz0), 0.0, 2.3, (0, 0, -1))
    m.poly([(px0, 2.3, pz0), (px1, 2.3, pz0), (pm, 3.4, pz0)], LIME, [EAVE, EAVE, CLEAN], facing=(0, 0, -1))
    # The door at the back of the porch: oak, a hand's width ajar, candlelight in the gap.
    dz = pz1 - 0.04
    m.poly([(px0 + 0.3, 0.0, dz), (px1 - 0.3, 0.0, dz), (px1 - 0.3, 2.3, dz), (px0 + 0.3, 2.3, dz)], "window_dark", facing=(0, 0, -1))
    m.poly([(px0 + 0.5, 0.45, dz - 0.03), (pm + 0.38, 0.45, dz - 0.03), (pm + 0.38, 2.15, dz - 0.03), (px0 + 0.5, 2.15, dz - 0.03)], "wood_boards",
           (0.6, 0.57, 0.52, 1.0), facing=(0, 0, -1))
    m.poly([(pm + 0.4, 0.45, dz - 0.02), (pm + 0.54, 0.45, dz - 0.02), (pm + 0.54, 2.15, dz - 0.02), (pm + 0.4, 2.15, dz - 0.02)], "window_candle",
           uvs=[(0.4, 0.0), (0.5, 0.0), (0.5, 1.0), (0.4, 1.0)], facing=(0, 0, -1))
    m.box((px0 + 0.3, 0.0, pz0), (px1 - 0.3, 0.45, pz1), CUT, DARK_STONE, STONE, faces="zY")


def yard(m):
    x0, x1, z0, z1 = YARD
    g0, g1 = GATE_X
    # The wall: rubble, waist high, with a coping; broken for the gate on the road side.
    runs = [((x0, z0), (g0, z0)), ((g1, z0), (x1, z0)), ((x1, z0), (x1, z1)), ((x1, z1), (x0, z1)), ((x0, z1), (x0, z0))]
    for (ax, az), (bx, bz) in runs:
        lo = (min(ax, bx) - 0.22, -0.5, min(az, bz) - 0.22)
        hi = (max(ax, bx) + 0.22, 1.0 + random.uniform(-0.04, 0.04), max(az, bz) + 0.22)
        m.box(lo, hi, "stone_rubble", DARK_STONE, STONE, faces="xXzZY")
        m.box((lo[0] - 0.05, hi[1], lo[2] - 0.05), (hi[0] + 0.05, hi[1] + 0.12, hi[2] + 0.05), CUT, STONE, faces="xXzZyY")
    # The gate: two oak posts, a rail between, a little gabled roof over (a lych gate).
    for x in (g0 + 0.12, g1 - 0.12):
        m.box((x - 0.11, -0.3, z0 - 0.11), (x + 0.11, 2.3, z0 + 0.11), "wood_medieval", (0.6, 0.6, 0.6, 1.0), faces="xXzZY")
    gm = (g0 + g1) * 0.5
    for side, x_out in ((-1, g0 - 0.35), (1, g1 + 0.35)):
        pts = [(x_out, 2.25, z0 - 0.7), (x_out, 2.25, z0 + 0.7), (gm, 3.05, z0 + 0.7), (gm, 3.05, z0 - 0.7)]
        m.poly(pts, "roof_slates", (0.8, 0.8, 0.82, 1.0), [(0.0, 0.0), (0.5, 0.0), (0.5, 0.5), (0.0, 0.5)], facing=(side, 1, 0))
        m.poly(pts, "wood_medieval", (0.35, 0.35, 0.35, 1.0), facing=(-side, -1, 0))
    m.box((g0, 2.2, z0 - 0.06), (g1, 2.36, z0 + 0.06), "wood_medieval", (0.6, 0.6, 0.6, 1.0), faces="xXzZyY")
    # The preaching cross: three steps, a tall shaft, a short head.
    cx, cz = 8.5, -4.6
    for i, half in enumerate((1.1, 0.8, 0.5)):
        m.box((cx - half, 0.24 * i, cz - half), (cx + half, 0.24 * (i + 1), cz + half), CUT, DARK_STONE, STONE, faces="xXzZY")
    m.box((cx - 0.13, 0.72, cz - 0.13), (cx + 0.13, 3.1, cz + 0.13), CUT, STONE, faces="xXzZY")
    m.box((cx - 0.42, 2.55, cz - 0.1), (cx + 0.42, 2.78, cz + 0.1), CUT, STONE, faces="xXzZyY")
    # Graves: low mounds lying east to west, a wooden marker at the head of most, leaning.
    spots = [(x, z) for x in (-18.0, -15.4, -12.8, 12.6, 14.8) for z in (-5.5, -2.0, 1.6, 5.4, 8.8)]
    spots += [(x, 8.6) for x in (-9.6, -6.8, -3.9, -1.0, 2.0, 5.1, 8.3)] + [(x, -6.2) for x in (-9.5, -6.5, 11.5)]
    for gx, gz in spots:
        if random.random() < 0.2 or (5.0 < gx < 14.4 and 3.6 < gz < 7.6):
            # (The second: this autumn's graves are there.)
            continue
        gx += random.uniform(-0.4, 0.4)
        gz += random.uniform(-0.35, 0.35)
        long = random.uniform(1.6, 2.0)
        top = random.uniform(0.12, 0.3)
        pts = [(gx - long * 0.5, 0.0, gz - 0.42), (gx + long * 0.5, 0.0, gz - 0.42), (gx + long * 0.5, 0.0, gz + 0.42), (gx - long * 0.5, 0.0, gz + 0.42)]
        ridge = [(gx - long * 0.35, top, gz), (gx + long * 0.35, top, gz)]
        earth = (0.55, 0.5, 0.42, 1.0)
        m.poly([pts[0], pts[1], ridge[1], ridge[0]], "grave_earth", earth, facing=(0, 1, -1))
        m.poly([pts[3], pts[2], ridge[1], ridge[0]], "grave_earth", earth, facing=(0, 1, 1))
        m.poly([pts[0], pts[3], ridge[0]], "grave_earth", earth, facing=(-1, 1, 0))
        m.poly([pts[1], pts[2], ridge[1]], "grave_earth", earth, facing=(1, 1, 0))
        if random.random() < 0.75:
            # A board on a stake at the west end (the head), tipped by the years.
            hx = gx - long * 0.5 - 0.15
            lean_x, lean_z = random.uniform(-0.16, 0.16), random.uniform(-0.2, 0.2)
            h = random.uniform(0.7, 1.05)
            wood = (random.uniform(0.4, 0.65),) * 3 + (1.0,)
            m.box((hx - 0.03, -0.1, gz - 0.035), (hx + 0.03 + lean_x * 0.2, h, gz + 0.035 + lean_z * 0.2), "wood_medieval", wood, faces="xXzZY")
            m.box((hx - 0.035 + lean_x * 0.1, h - 0.34, gz - 0.2 + lean_z * 0.15), (hx + 0.035 + lean_x * 0.1, h - 0.16, gz + 0.2 + lean_z * 0.15),
                  "wood_medieval", wood, faces="xXzZyY")
        elif random.random() < 0.5:
            m.box((gx - long * 0.45, top * 0.5, gz - 0.3), (gx + long * 0.45, top * 0.5 + 0.1, gz + 0.3), CUT, STONE, faces="xXzZY")


def fresh(m):
    """This autumn's dead, east of the porch: a row of new mounds with no
    markers yet, and one grave dug and waiting, the spade left in the heap."""
    earth = (0.42, 0.36, 0.3, 1.0)
    for i, gx in enumerate((6.2, 8.0, 9.9, 11.7)):
        gz = 5.6 + 0.2 * math.sin(i * 2.1)
        if i == 3:
            # The open one: the dark of it, boards along its edge, the heap beside.
            m.poly([(gx - 0.45, 0.02, gz - 1.0), (gx + 0.45, 0.02, gz - 1.0), (gx + 0.45, 0.02, gz + 1.0), (gx - 0.45, 0.02, gz + 1.0)], "window_dark",
                   facing=(0, 1, 0))
            for s in (-1, 1):
                m.box((gx + s * 0.5 - 0.1, 0.0, gz - 1.1), (gx + s * 0.5 + 0.1, 0.05, gz + 1.1), "wood_boards", (0.55, 0.52, 0.48, 1.0), faces="xXzZY")
            hx = gx + 1.5
            ring = [(hx + math.cos(math.tau * k / 7) * (0.85 + 0.2 * math.sin(k * 3.0)), 0.0, gz + math.sin(math.tau * k / 7) * 1.1) for k in range(7)]
            for a, b in zip(ring, ring[1:] + ring[:1]):
                m.poly([a, b, (hx, 0.62, gz)], "grave_earth", earth, facing=((a[0] + b[0]) * 0.5 - hx, 1.0, (a[2] + b[2]) * 0.5 - gz))
            m.tube([(hx - 0.3, 0.35, gz + 0.2), (hx - 0.52, 1.45, gz + 0.32)], [0.022, 0.02], 5, "wood_frame", (0.6, 0.57, 0.52, 1.0))
            m.box((hx - 0.36, 0.1, gz + 0.16), (hx - 0.2, 0.42, gz + 0.2), "iron_cart", (0.5, 0.5, 0.5, 1.0))
            continue
        pts = [(gx - 0.45, 0.0, gz - 0.95), (gx + 0.45, 0.0, gz - 0.95), (gx + 0.45, 0.0, gz + 0.95), (gx - 0.45, 0.0, gz + 0.95)]
        ridge = [(gx, 0.34, gz - 0.65), (gx, 0.34, gz + 0.65)]
        m.poly([pts[0], pts[3], ridge[1], ridge[0]], "grave_earth", earth, facing=(-1, 1, 0))
        m.poly([pts[1], pts[2], ridge[1], ridge[0]], "grave_earth", earth, facing=(1, 1, 0))
        m.poly([pts[0], pts[1], ridge[0]], "grave_earth", earth, facing=(0, 1, -1))
        m.poly([pts[3], pts[2], ridge[1]], "grave_earth", earth, facing=(0, 1, 1))


def main():
    porter.reset(21)
    m = porter.Mesh("Chapel")
    chapel(m)
    m.build()
    y = porter.Mesh("Yard")
    yard(y)
    fresh(y)
    y.build()
    for name, (x0, x1, half, top) in (("Nave", NAVE[:3] + (NAVE[4],)), ("Chancel", CHANCEL[:3] + (CHANCEL[4],)),
                                      ("Tower", TOWER[:3] + (TOWER[3],))):
        c = porter.Mesh(name + "-colonly")
        c.box((x0, 0.0, -half), (x1, top, half), CUT)
        c.build()
    porter.export("env_white_chapel")


if __name__ == "__main__":
    main()
