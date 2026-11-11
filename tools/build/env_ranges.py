"""The three ranges round the cloister (every night): the east range
(slype, chapter house, day stair, warming room, undercroft, the dormitory
over them, the latrine block), the south range (refectory, kitchen,
bakehouse) and the west range (granary, parlour, stores). The model is in
the abbey's own coordinates and is laid over the greybox (dormitory.tscn,
south_range.tscn, cellar.tscn), which still stops people and shapes the
navmesh but is no longer drawn.

The walls are read from those scenes: every 4 m wall piece (plain, with a
door, with a window) gets a face on each side, inside or outside as it
falls, with a surround to each opening. The windows stay open holes, since
people and hunters see through them. The walls shared with the church are
added by hand.

`env_ranges`:
- Walls: outside in the cloister's stone; inside in plaster, cut stone or
  rubble by room. Gables where a roof ends.
- Ceilings: under the dormitory, low vaults (the slype a tunnel, the
  chapter house ribbed, the warming room and undercroft groined) and
  boarded ceilings; everywhere else the roof is open: boards, rafters,
  purlins and a truss every 4 m.
- Floors: tiles in the refectory and chapter house, flags below, boards
  in the dormitory.
- Roofs: clay tile; three chimney stacks.
- Fittings: oak panelling and paned hangings in the refectory, hangings
  and a rush runner down the dormitory, a runner on the day stair, a
  blind arcade and a painted panel in the chapter house, iron brackets.

Run: tools/build.sh env_ranges
"""
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
import city_parts as cp
import env_church as ch
import env_crypt as cr
from mathutils import Vector
from porter import fbm, lerp, smoothstep

cl = ch.cl
pale = cl.pale
F = 0.42
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCENES = ("dormitory", "south_range", "cellar")
OAK = "wood_medieval"
BOARDS = "wood_boards"

# Rooms: name -> (x0, x1, z0, z1, level, style). The rectangles are the
# walls' middles.
ROOMS = {
    "slype": (12, 20, -28, -24, 0, "ashlar"),
    "chapter": (12, 20, -24, -16, 0, "ashlar"),
    "stairhall": (12, 20, -16, -12, 0, "plaster"),
    "warming": (12, 20, -12, -4, 0, "ashlar"),
    "undercroft": (12, 20, -4, 12, 0, "rubble"),
    "latrine0": (12, 20, 12, 20, 0, "rubble"),
    "dorm": (12, 20, -28, 12, 1, "plaster"),
    "latrine1": (12, 20, 12, 20, 1, "rubble"),
    "refectory": (-12, 12, -4, 4, 0, "plaster"),
    "kitchen": (-20, -12, -4, 4, 0, "rubble"),
    "bakehouse": (-20, -12, 4, 12, 0, "rubble"),
    "granary": (-20, -12, -28, -16, 0, "rubble"),
    "parlour": (-20, -12, -16, -12, 0, "plaster"),
    "stores": (-20, -12, -12, -4, 0, "rubble"),
}
# Walls that are the church's (its south wall), seen from the ranges only:
# (x, level, kind).
BORROWED = ((14, 0, "wall"), (18, 0, "wall"), (-18, 0, "wall"), (-14, 0, "wall"), (14, 1, "wall"), (18, 1, "wall_door"))
# Faces not to make: (along, line, side). env_precinct.py uses these three.
SKIP = ()


def plaster(seed):
    def tint(x, y, z):
        base = y - 4.0 * math.floor(y / 4.0 + 0.001)
        k = (0.86 + 0.16 * fbm(x + z, y, 0.25, 3, seed)) * lerp(0.78, 1.0, smoothstep(0.0, 1.1, base))
        return (k, k * 0.98, k * 0.94, 1.0)
    tint.mat = "plaster_abbey"
    return tint


def styled(style, seed):
    if style == "plaster":
        return plaster(seed)
    if style == "ashlar":
        t = cp.stone_tint(0.0, 5.0, clean=(0.8, 0.78, 0.74), seed=seed, worn=0.0)
        t.mat = "stone_church"
        return t
    t = cp.stone_tint(0.0, 5.0, clean=(0.76, 0.74, 0.7), seed=seed, worn=0.3)
    t.mat = "stone_rubble"
    return t


def pieces():
    """Every wall piece of the three scenes above ground: (along, line, at, level, kind, only)."""
    out = []
    for scene in SCENES:
        text = open(os.path.join(ROOT, "game/world/abbey/areas", scene + ".tscn")).read()
        kinds = {i: os.path.basename(p)[:-5] for p, i in re.findall(r'path="res://game/world/kit/([^"]+)" id="([^"]+)"', text)}
        for block in text.split("\n\n"):
            m = re.match(r'\[node name="[^"]+"[^\]]*parent="(?:[^"]*/)?Walls"[^\]]*instance=ExtResource\("([^"]+)"\)', block)
            tr = re.search(r"transform = Transform3D\(([^)]*)\)", block)
            if not m or not tr or kinds.get(m.group(1)) == "corner":
                continue
            v = [float(q) for q in tr.group(1).split(",")]
            if v[10] < -0.5:
                continue
            along = "z" if abs(v[0]) < 0.5 else "x"
            line, at = (v[9], v[11]) if along == "z" else (v[11], v[9])
            out.append((along, round(line), round(at), int(round(v[10] / 4.0)), kinds[m.group(1)], 0))
    for x, level, kind in BORROWED:
        out.append(("x", -28, x, level, kind, 1))
    return out


def room_at(x, z, level):
    for name, (x0, x1, z0, z1, lv, style) in ROOMS.items():
        if lv == level and x0 < x < x1 and z0 < z < z1:
            return name
    if abs(x) < 12 and -28 < z < -4:
        return "cloister"
    return "out"


def cut_of(kind, at, base):
    if kind == "wall_door":
        return (at, 0.47, base, base + 2.03)
    if kind == "wall_window":
        return (at, 0.31, base + 1.59, base + 2.81)
    if kind == "wall_gate":
        return (at, 1.5, base, base + 3.4)
    if kind == "wall_squint":
        return (at, 0.09, base + 1.35, base + 1.85)
    return None


def walls(m, tints, outside):
    ps = pieces()
    have = {(a, l, at, lv) for a, l, at, lv, k, o in ps}
    groups = {}
    for along, line, at, level, kind, only in ps:
        for s in (1, -1):
            if only and s != only:
                continue
            # s is the side in the world: toward +z (a wall along x) or +x (along z).
            x, z = (at, line + s) if along == "x" else (line + s, at)
            groups.setdefault((along, line, level, s, room_at(x, z, level)), []).append((at, kind))
    # A core down the middle of every wall, never seen: the faces are one-sided
    # and meet edge to edge at the corners, so without it the sun and moon get
    # in through the cracks and through the backs of the inner faces.
    for along, line, at, level, kind, only in ps:
        if only:
            continue
        base = 4.0 * level
        a0 = at - 2.0 - (0.0 if (along, line, at - 4, level) in have else F)
        a1 = at + 2.0 + (0.0 if (along, line, at + 4, level) in have else F)
        cut = cut_of(kind, at, base)
        rects = [(a0, a1, base, base + 4.0)]
        if cut:
            rects = [(a0, cut[0] - cut[1], base, base + 4.0), (cut[0] + cut[1], a1, base, base + 4.0), (cut[0] - cut[1], cut[0] + cut[1], cut[3], base + 4.0),
                     (cut[0] - cut[1], cut[0] + cut[1], base, cut[2])]
        for ua, ub, ya, yb in rects:
            if ub - ua < 0.01 or yb - ya < 0.01:
                continue
            pts = [(ua, ya, line), (ub, ya, line), (ub, yb, line), (ua, yb, line)] if along == "x" else [(line, ya, ua), (line, ya, ub), (line, yb, ub), (line, yb, ua)]
            for k in (-1, 1):
                m.poly(pts, "stone_rubble", (0.1, 0.1, 0.1, 1.0), facing=(0, 0, k) if along == "x" else (k, 0, 0))
    for (along, line, level, s, cls), items in groups.items():
        if (cls == "cloister" and level == 0) or (along, line, s) in SKIP:
            continue
        items.sort()
        runs = [[items[0]]]
        for it in items[1:]:
            if it[0] - runs[-1][-1][0] == 4:
                runs[-1].append(it)
            else:
                runs.append([it])
        base = 4.0 * level
        ya, yb = base, base + 4.0
        if cls == "cloister":
            ya = 4.8
        tint = outside if cls in ("out", "cloister") else tints[cls]
        if along == "x":
            t, sl, flip = cl.Turned(m, lambda u, y, v, L=line: (u, y, L + v)), s, 1
        else:
            t, sl, flip = cl.Turned(m, lambda u, y, v, L=line: (L - v, y, u)), -s, 1
        for run in runs:
            ua, ub = run[0][0] - 2.0, run[-1][0] + 2.0
            if (along, line, run[0][0] - 4, level) not in have:
                ua -= F
            if (along, line, run[-1][0] + 4, level) not in have:
                ub += F
            cuts = [c for c in (cut_of(kind, at, base) for at, kind in run) if c and c[3] > ya]
            ch.face(t, sl, ua, ub, ya, yb, tint, cuts)


def beam(m, a, b, w, h, color, mat=OAK):
    """A squared timber from a to b, `w` wide and `h` deep."""
    a, b = Vector(a), Vector(b)
    ahead = (b - a).normalized()
    side = ahead.cross(Vector((0, 1, 0)))
    side = side.normalized() if side.length > 1e-4 else Vector((1, 0, 0))
    up = side.cross(ahead)
    for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        n = side * sx + up * sy
        e = (up if sx else side)
        o = side * (sx * w * 0.5) + up * (sy * h * 0.5)
        r = e * ((h if sx else w) * 0.5)
        m.poly([tuple(a + o - r), tuple(a + o + r), tuple(b + o + r), tuple(b + o - r)], mat, color, facing=tuple(n))


def open_roof(m, axis, a0, a1, c, half, eave, ridge, trusses, braced=False):
    """A roof seen from below: boards, rafters, purlins, and a truss at each of `trusses`."""
    def at(w, q, y):
        return (w, y, c + q) if axis == "x" else (c + q, y, w)

    dark, mid = (0.3, 0.28, 0.26, 1.0), (0.4, 0.37, 0.33, 1.0)
    inner = half - 0.3
    drop = 0.08
    for s in (-1, 1):
        ws = cp.steps(a0, a1, 1.0)
        for wa, wb in zip(ws, ws[1:]):
            pts = [at(wa, s * half, eave - drop), at(wb, s * half, eave - drop), at(wb, 0.0, ridge - drop), at(wa, 0.0, ridge - drop)]
            cols = [cp.rgba((0.34, 0.31, 0.28), 0.8 + 0.4 * fbm(p[0], p[2], 0.6, 2, 5.0)) for p in pts]
            m.poly(pts, BOARDS, cols, facing=(0, -1, 0))
        for w in cp.steps(a0 + 0.4, a1 - 0.4, 1.0):
            beam(m, at(w, s * half, eave - drop - 0.07), at(w, 0.0, ridge - drop - 0.07), 0.09, 0.14, dark)
        for f in (0.36, 0.7):
            q, y = s * half * (1.0 - f), lerp(eave, ridge, f) - drop - 0.2
            beam(m, at(a0, q, y), at(a1, q, y), 0.14, 0.16, mid)
    beam(m, at(a0, 0.0, ridge - drop - 0.2), at(a1, 0.0, ridge - drop - 0.2), 0.14, 0.2, mid)
    rise = ridge - eave
    for w in trusses:
        beam(m, at(w, -inner, eave + 0.12), at(w, inner, eave + 0.12), 0.22, 0.26, mid)
        beam(m, at(w, 0.0, eave + 0.25), at(w, 0.0, ridge - 0.3), 0.18, 0.18, mid)
        for s in (-1, 1):
            beam(m, at(w, s * inner, eave + 0.2), at(w, 0.0, ridge - 0.34), 0.18, 0.2, mid)
            beam(m, at(w, s * inner * 0.5, eave + 0.25), at(w, 0.0, eave + rise * 0.55), 0.12, 0.12, dark)
            if braced:
                # A curved brace from the wall up to the tie beam.
                pts = [at(w, s * (inner + 0.02 - 1.3 * (1 - math.cos(a))), eave - 1.3 + 1.3 * math.sin(a) + 0.02) for a in [math.pi * 0.5 * k / 5 for k in range(6)]]
                for p, q in zip(pts, pts[1:]):
                    beam(m, p, q, 0.14, 0.16, dark)


def gable(m, axis, w, c, half, eave, ridge, facing, tint):
    """The triangle of wall under a roof's end, at `w` along the roof, looking `facing` (1 or -1) along it."""
    def at(q, y):
        return (w, y, c + q) if axis == "x" else (c + q, y, w)

    n = 6
    for i in range(n):
        for s in (-1, 1):
            qa, qb = s * half * i / n, s * half * (i + 1) / n
            pts = [at(qa, eave), at(qb, eave), at(qb, lerp(ridge, eave, (i + 1) / n)), at(qa, lerp(ridge, eave, i / n))]
            m.poly(pts, getattr(tint, "mat", "stone_cloister"), [tint(*p) for p in pts], facing=(facing, 0, 0) if axis == "x" else (0, 0, facing))


def flat_ceiling(m, x0, x1, z0, z1, y, hole=None):
    for xa, xb, za, zb in minus((x0, x1, z0, z1), hole):
        for a, b in zip(cp.steps(za, zb, 0.5), cp.steps(za, zb, 0.5)[1:]):
            k = 0.3 + 0.12 * ((math.sin(a * 12.9898) * 43758.5453) % 1.0)
            m.poly([(xa, y, a), (xb, y, a), (xb, y, b), (xa, y, b)], BOARDS, (k, k * 0.95, k * 0.9, 1.0), facing=(0, -1, 0))
    for z in cp.steps(z0 + 0.5, z1 - 0.5, 1.0):
        if hole and hole[2] - 0.2 < z < hole[3] + 0.2:
            continue
        beam(m, (x0, y - 0.1, z), (x1, y - 0.1, z), 0.16, 0.2, (0.32, 0.3, 0.27, 1.0))


def minus(rect, hole):
    """A rectangle less a hole, as rectangles."""
    x0, x1, z0, z1 = rect
    if not hole:
        return [rect]
    hx0, hx1, hz0, hz1 = hole
    return [r for r in ((x0, x1, z0, hz0), (x0, x1, hz1, z1), (x0, hx0, hz0, hz1), (hx1, x1, hz0, hz1)) if r[1] - r[0] > 0.01 and r[3] - r[2] > 0.01]


def floor(m, rect, y, kind, seed, hole=None):
    for x0, x1, z0, z1 in minus(rect, hole):
        xs = [x0] + [float(q) for q in range(math.floor(x0) + 1, math.ceil(x1))] + [x1]
        zs = [z0] + [float(q) for q in range(math.floor(z0) + 1, math.ceil(z1))] + [z1]
        for xa, xb in zip(xs, xs[1:]):
            for za, zb in zip(zs, zs[1:]):
                pts = [(xa, y, za), (xb, y, za), (xb, y, zb), (xa, y, zb)]
                cols = []
                for p in pts:
                    k = 0.7 + 0.3 * fbm(p[0], p[2], 0.3, 3, seed)
                    if kind == "tiles":
                        odd = (math.floor(xa + 0.5) + math.floor(za + 0.5)) % 2
                        cols.append((k * (0.55 if odd else 0.95), k * (0.4 if odd else 0.9), k * (0.32 if odd else 0.78), 1.0))
                    elif kind == "boards":
                        b = 0.75 + 0.3 * ((math.sin(math.floor(p[0] / 0.01) * 0.0 + math.floor(xa) * 12.9898 + seed) * 43758.5453) % 1.0)
                        cols.append((0.36 * b * k, 0.33 * b * k, 0.3 * b * k, 1.0))
                    else:
                        cols.append((k * 0.8, k * 0.8, k * 0.77, 1.0))
                m.poly(pts, BOARDS if kind == "boards" else "flags_worn", cols, facing=(0, 1, 0))


def hanging(m, along, line, s, a0, a1, y0, y1, colours, seed=0.0):
    """A paned cloth hung on a wall: `line` is the wall's middle, s the side it hangs on."""
    v = line + s * (F + 0.035)
    n = max(int(round((a1 - a0) / 0.55)), 1)

    def at(w, y):
        return (w, y, v) if along == "x" else (v, y, w)

    out = (0, 0, s) if along == "x" else (s, 0, 0)
    for i in range(n):
        wa, wb = lerp(a0, a1, i / n), lerp(a0, a1, (i + 1) / n)
        c = colours[i % 2]
        k = 0.85 + 0.25 * ((math.sin(i * 7.3 + seed) * 43758.5453) % 1.0)
        top, foot = cp.rgba(c, k), cp.rgba(c, k * 0.72)
        sag = 0.04 * math.sin(i * 1.9 + seed)
        m.poly([at(wa, y0 + sag), at(wb, y0 + sag), at(wb, y1 - 0.14), at(wa, y1 - 0.14)], "painted", [foot, foot, top, top], facing=out)
    m.poly([at(a0, y1 - 0.14), at(a1, y1 - 0.14), at(a1, y1), at(a0, y1)], "painted", cp.rgba(colours[2], 1.0), facing=out)
    rod = line + s * (F + 0.06)
    p, q = ((a0 - 0.1, y1 + 0.03, rod), (a1 + 0.1, y1 + 0.03, rod)) if along == "x" else ((rod, y1 + 0.03, a0 - 0.1), (rod, y1 + 0.03, a1 + 0.1))
    m.tube([p, q], [0.018, 0.018], 5, "iron_cart", (0.1, 0.1, 0.1, 1.0))


def stack(m, x0, x1, z0, z1, y0, y1, tint):
    """A chimney stack."""
    cp.slab(m, (x0, y0, z0), (x1, y1, z1), "stone_cloister", tint, faces="xXzZY", step=1.2)
    m.box((x0 - 0.07, y1 - 0.3, z0 - 0.07), (x1 + 0.07, y1 - 0.14, z1 + 0.07), "stone_cloister", pale(0.7))
    m.box((x0 + 0.18, y1, z0 + 0.18), (x1 - 0.18, y1 + 0.02, z1 - 0.18), "window_dark", (0, 0, 0, 1), faces="Y")


def build():
    porter.reset(617)
    cl.STONE = "stone_church"
    wall_m, roof_m, ceil_m, vault_m, floor_m, fit = (porter.Mesh(n) for n in ("Walls", "Roofs", "Ceilings", "Vaults", "Floors", "Fittings"))
    outside = cp.stone_tint(0.0, 8.0, seed=41.0, worn=0.4)
    outside.mat = "stone_cloister"
    tints = {name: styled(r[5], 3.0 + 2.0 * i) for i, (name, r) in enumerate(ROOMS.items())}
    walls(wall_m, tints, outside)

    # Roofs: tile outside, timber inside, gables where they end.
    tile = (0.85, 0.8, 0.76)
    # (Each stops short where it runs into a taller wall, and overhangs its own gables, so no light gets in at the verge.)
    cp.gable_roof(roof_m, 11.6, 20.4, -27.5, 20.4, 8.0, 12.0, "roof_tiles", tile, along="z", over=0.5)
    cp.gable_roof(roof_m, -12.0, 11.5, -4.4, 4.4, 4.0, 8.0, "roof_tiles", tile, along="x", over=0.5)
    cp.gable_roof(roof_m, -20.4, -11.6, -27.5, 12.4, 4.0, 8.0, "roof_tiles", tile, along="z", over=0.5)
    open_roof(ceil_m, "z", -28.0 + F, 20.0 - F, 16.0, 4.4, 8.0, 12.0, [-24.0 + 4.0 * i for i in range(11)], braced=True)
    open_roof(ceil_m, "x", -12.0 + F, 12.0 - F, 0.0, 4.4, 4.0, 8.0, [-8.0, -4.0, 0.0, 4.0, 8.0], braced=True)
    open_roof(ceil_m, "z", -28.0 + F, -4.0 - F, -16.0, 4.4, 4.0, 8.0, [-24.0, -20.0, -8.0])
    open_roof(ceil_m, "z", -4.0 + F, 12.0 - F, -16.0, 4.4, 4.0, 8.0, [0.0, 8.0])
    dorm_t, west_t, kit_t = tints["dorm"], tints["granary"], tints["kitchen"]
    gable(wall_m, "z", -28.0 + F, 16.0, 4.4, 8.0, 12.0, 1, dorm_t)
    gable(wall_m, "z", 12.0 - F, 16.0, 4.4, 8.0, 12.0, -1, dorm_t)
    gable(wall_m, "z", 12.0 + F, 16.0, 4.4, 8.0, 12.0, 1, tints["latrine1"])
    gable(wall_m, "z", 20.0 - F, 16.0, 4.4, 8.0, 12.0, -1, tints["latrine1"])
    gable(wall_m, "z", 20.0 + F, 16.0, 4.4, 8.0, 12.0, 1, outside)
    gable(wall_m, "x", -12.0 + F, 0.0, 4.4, 4.0, 8.0, 1, tints["refectory"])
    gable(wall_m, "x", -12.0 - F, 0.0, 4.4, 4.0, 8.0, -1, outside)
    gable(wall_m, "z", -28.0 + F, -16.0, 4.4, 4.0, 8.0, 1, west_t)
    gable(wall_m, "z", -4.0 - F, -16.0, 4.4, 4.0, 8.0, -1, tints["stores"])
    gable(wall_m, "z", -4.0 + F, -16.0, 4.4, 4.0, 8.0, 1, kit_t)
    gable(wall_m, "z", 12.0 - F, -16.0, 4.4, 4.0, 8.0, -1, tints["bakehouse"])
    gable(wall_m, "z", 12.0 + F, -16.0, 4.4, 4.0, 8.0, 1, outside)
    # The east wall of the refectory above its own walls is the east range's.
    st = cp.stone_tint(4.0, 13.0, seed=55.0, worn=0.5)
    stack(roof_m, -16.6, -15.4, -4.4, -3.5, 4.0, 9.4, st)
    stack(roof_m, 19.5, 20.5, -8.6, -7.4, 8.0, 13.6, st)
    stack(roof_m, -20.5, -19.5, 7.4, 8.6, 4.0, 8.6, st)

    # Under the dormitory: vaults and boarded ceilings (its floor is at 3.72).
    web = lambda x, y, z: cp.rgba((0.84, 0.82, 0.78), lerp(1.0, 0.7, smoothstep(1.6, 3.6, y)) * (0.9 + 0.14 * fbm(x, z, 0.5, 2, 3.0)))
    xa, xb = 12.0 + F, 20.0 - F
    same = cl.Turned(vault_m, lambda x, y, z: (x, y, z))
    cr.barrel(vault_m, "x", xa, xb, -26.0, 2.0 - F, cr.round_crown(2.0, 1.58), "stone_church", web)
    crown = cr.round_crown(1.6, 2.0)
    for za, zb in ((-24.0 + F, -20.0), (-20.0, -16.0 - F)):
        cr.groin(vault_m, xa, xb, za, zb, crown, "stone_church", web, ribs=True)
    low = cr.round_crown(1.7, 1.9)

    def arch_at(z, crown_fn):
        cl.rib(same, [(lerp(xa, xb, (tt + 1.0) * 0.5), crown_fn(tt), z) for tt in cr.TS], 0.3, 0.2, pale(0.66))
        for x, k in ((xa, 1), (xb, -1)):
            vault_m.tube([(x + k * 0.1, crown_fn(1.0) - 0.5, z), (x + k * 0.1, crown_fn(1.0) - 0.3, z), (x + k * 0.1, crown_fn(1.0) - 0.05, z),
                          (x + k * 0.1, crown_fn(1.0), z)], [0.04, 0.12, 0.24, 0.26], 6, "stone_church", pale(0.74), caps=True)

    arch_at(-20.0, crown)
    for za, zb in ((-12.0 + F, -8.0), (-8.0, -4.0 - F)):
        cr.groin(vault_m, xa, xb, za, zb, low, "stone_church", web)
    arch_at(-8.0, low)
    edges = [-4.0 + F, 0.0, 4.0, 8.0, 12.0 - F]
    for za, zb in zip(edges, edges[1:]):
        cr.groin(vault_m, xa, xb, za, zb, low, "stone_rubble", web)
    for z in edges[1:-1]:
        arch_at(z, low)
    hole = (13.0, 19.0, -14.8, -13.2)
    flat_ceiling(ceil_m, xa, xb, -16.0 + F, -12.0 - F, 3.7, hole)
    flat_ceiling(ceil_m, xa, xb, 12.0 + F, 20.0 - F, 3.7)

    # Floors.
    y0, y1 = 0.056, 4.026
    inner = lambda r: (r[0] + F, r[1] - F, r[2] + F, r[3] - F)
    kinds = {"refectory": "tiles", "chapter": "tiles"}
    for i, (name, r) in enumerate(ROOMS.items()):
        rect = inner(r)
        if name == "dorm":
            floor(floor_m, rect, y1, "boards", 20.0, hole)
        elif name == "latrine1":
            floor(floor_m, rect, y1, "boards", 21.0)
        elif name == "latrine0":
            floor(floor_m, (rect[0], rect[1], rect[2], 16.0), y0, "flags", 22.0)
        elif name == "granary":
            floor(floor_m, rect, y0, "flags", 23.0, (-19.4, -18.2, -25.0, -19.0))
        else:
            floor(floor_m, rect, y0, kinds.get(name, "flags"), 5.0 + i)
    # Thresholds through the walls, so no gap shows under a door.
    for along, line, at, level, kind, only in pieces():
        if kind in ("wall_door", "wall_gate"):
            hw = 0.47 if kind == "wall_door" else 1.5
            y = y0 if level == 0 else y1
            r = (at - hw, at + hw, line - F, line + F) if along == "x" else (line - F, line + F, at - hw, at + hw)
            floor_m.poly([(r[0], y, r[2]), (r[1], y, r[2]), (r[1], y, r[3]), (r[0], y, r[3])], "flags_worn", (0.6, 0.6, 0.58, 1.0), facing=(0, 1, 0))

    # The refectory: oak panelling, paned hangings.
    red, green, gold, blue = (0.3, 0.07, 0.06), (0.08, 0.17, 0.1), (0.4, 0.3, 0.12), (0.07, 0.1, 0.2)
    oak = (0.34, 0.3, 0.26, 1.0)
    for line, s in ((-4.0, 1), (4.0, -1)):
        z = line + s * F
        for x in range(-10, 11, 4):
            door = (line == -4.0 and x == -2) or (line == 4.0 and x == 2)
            spans = ((x - 2.0, x - 0.7), (x + 0.7, x + 2.0)) if door else ((x - 2.0, x + 2.0),)
            for a, b in spans:
                lo, hi = sorted((z, z + s * 0.05))
                fit.box((a, 0.06, lo), (b, 1.42, hi), OAK, oak, faces="xXY" + ("Z" if s > 0 else "z"))
                lo, hi = sorted((z, z + s * 0.08))
                fit.box((a, 1.42, lo), (b, 1.52, hi), OAK, (0.4, 0.36, 0.31, 1.0), faces="xXyY" + ("Z" if s > 0 else "z"))
                for q in cp.steps(a, b, 0.65)[1:-1]:
                    lo, hi = sorted((z + s * 0.05, z + s * 0.065))
                    fit.box((q - 0.03, 0.06, lo), (q + 0.03, 1.42, hi), OAK, (0.28, 0.25, 0.22, 1.0), faces="xX" + ("Z" if s > 0 else "z"))
        for x in (-10.0, 10.0):
            hanging(fit, "x", line, s, x - 1.5, x + 1.5, 1.7, 3.7, (red, green, gold), x)
    hanging(fit, "z", 12.0, -1, -2.6, 2.6, 1.3, 3.8, (blue, red, gold), 3.0)

    # The dormitory: hangings between its windows, a rush runner by the beds' feet.
    for line, s, first in ((12.0, 1, -26), (20.0, -1, -22)):
        for z in range(first, 11, 8):
            hanging(fit, "z", line, s, z - 1.2, z + 1.2, 5.3, 7.5, (green, gold, red) if (z // 8) % 2 else (red, blue, gold), z)
    rush = lambda x, z: cp.rgba((0.3, 0.25, 0.14), 0.75 + 0.4 * fbm(x * 2.0, z * 0.6, 1.0, 2, 4.0))
    for za, zb in ((-27.0, -15.4), (-12.6, 11.2)):
        for a, b in zip(cp.steps(za, zb, 1.0), cp.steps(za, zb, 1.0)[1:]):
            pts = [(15.3, y1 + 0.012, a), (16.7, y1 + 0.012, a), (16.7, y1 + 0.012, b), (15.3, y1 + 0.012, b)]
            fit.poly(pts, "sacking", [rush(p[0], p[2]) for p in pts], facing=(0, 1, 0))

    # The day stair: a runner up its sixteen steps (stairs.gd: 3.97 m over 6 m from x = 13).
    steps, rise, run = 16, 3.97, 6.0
    for i in range(steps):
        xa2, xb2 = 13.0 + run * i / steps, 13.0 + run * (i + 1) / steps
        h0, h1 = 0.05 + rise * i / steps, 0.05 + rise * (i + 1) / steps
        k = 0.8 + 0.2 * math.sin(i * 1.7)
        fit.poly([(xa2 - 0.006, h0, -14.45), (xa2 - 0.006, h0, -13.55), (xa2 - 0.006, h1, -13.55), (xa2 - 0.006, h1, -14.45)], "painted",
                 cp.rgba(red, k * 0.8), facing=(-1, 0, 0))
        fit.poly([(xa2, h1 + 0.006, -14.45), (xb2, h1 + 0.006, -14.45), (xb2, h1 + 0.006, -13.55), (xa2, h1 + 0.006, -13.55)], "painted",
                 cp.rgba(red, k), facing=(0, 1, 0))
        for z in (-14.45, -13.63):
            fit.poly([(xa2, h1 + 0.007, z), (xb2, h1 + 0.007, z), (xb2, h1 + 0.007, z + 0.08), (xa2, h1 + 0.007, z + 0.08)], "painted",
                     cp.rgba(gold, 0.9), facing=(0, 1, 0))
    hanging(fit, "x", -16.0, 1, 14.0, 18.0, 1.2, 3.3, (red, green, gold), 5.0)

    # The chapter house: a blind arcade round it and a painted panel over the east seats.
    for place, s, us in ((lambda u, y, v: (20.0 - v, y, u), 1, (-22.0, -18.0)), (lambda u, y, v: (u, y, -24.0 + v), 1, (14.0, 18.0)),
                         (lambda u, y, v: (u, y, -16.0 + v), -1, (14.0, 18.0))):
        t = cl.Turned(wall_m, place)
        for u in us:
            ch.blind_arcade(t, s, u)
    px = 20.0 - F - 0.03
    fit.box((px - 0.04, 1.4, -22.95), (px, 2.6, -20.75), OAK, oak, faces="xzZyY")
    for j, c in enumerate((blue, red, blue)):
        za, zb = -22.85 + j * 0.7, -22.85 + (j + 1) * 0.7 - 0.06
        fit.poly([(px - 0.045, 1.5, za), (px - 0.045, 1.5, zb), (px - 0.045, 2.5, zb), (px - 0.045, 2.5, za)], "painted",
                 [cp.rgba(c, 0.7), cp.rgba(c, 0.7), cp.rgba(c, 1.1), cp.rgba(c, 1.1)], facing=(-1, 0, 0))
        zc = (za + zb) * 0.5
        fit.poly([(px - 0.05, 1.6, zc - 0.12), (px - 0.05, 1.6, zc + 0.12), (px - 0.05, 2.2, zc + 0.09), (px - 0.05, 2.35, zc), (px - 0.05, 2.2, zc - 0.09)],
                 "painted", cp.rgba(gold, 1.0), facing=(-1, 0, 0))

    # Iron brackets, their torches burnt out.
    for x, y, z, ox, oz in ((12.0 + F, 1.9, -26.0, 1, 0), (20.0 - F, 1.9, 0.0, -1, 0), (12.0 + F, 1.9, 8.0, 1, 0), (20.0 - F, 5.9, -12.0, -1, 0),
                            (12.0 + F, 5.9, 0.0, 1, 0), (-12.0 - F, 1.9, -14.0, -1, 0), (-6.0, 2.2, -4.0 + F, 0, 1), (6.0, 2.2, 4.0 - F, 0, -1)):
        cr.torch(fit, x, y, z, ox, oz)

    wall_m.build()
    roof_m.build()
    ceil_m.build()
    vault_m.build(smooth=True)
    floor_m.build()
    fit.build()
    porter.export("env_ranges")


if __name__ == "__main__":
    build()
