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
- Dressing (`dressing`, with dress.py): a hooded figure in a niche at the
  day stair's head, a stone reader in the refectory's niche, a skull over
  the chapter house's door; lockers and a walled-up door in the
  undercroft; the kitchen's hearth hood; soot, damp, cracks, fallen
  plaster, webs; moss on the roofs. Nothing of it is solid underfoot.

`walls` also makes each wall's top and free ends, and prints an audit:
every piece's two faces are made or left out on purpose.

Run: tools/build.sh env_ranges
"""
import inspect
import math
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
import city_parts as cp
import env_church as ch
import env_crypt as cr
import dress
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


def high(tint, eave, top=0.45):
    """A gable's tint: the room's, going dark with smoke and damp up to the ridge."""
    def t(x, y, z):
        # (Read a metre under the wall's head, so the gable's foot is the wall's own tone: plaster darkens at each floor's foot.)
        c = tint(x + 0.37 * (y - eave), eave - 1.0, z)
        k = lerp(1.0, top, smoothstep(eave + 0.2, eave + 3.8, y))
        return (c[0] * k, c[1] * k, c[2] * k, c[3])
    t.mat = getattr(tint, "mat", "stone_cloister")
    return t


def seam(m, axis, w, c, half, eave, facing, tint):
    """A thin strip over the joint between a wall's head and the gable on it (their pieces don't share corners, and the
    dark behind showed through as dots)."""
    def at(q, y):
        return (w + facing * 0.004, y, c + q) if axis == "x" else (c + q, y, w + facing * 0.004)

    qs = cp.steps(-half + 2 * F, half - 2 * F, 1.0)
    for qa, qb in zip(qs, qs[1:]):
        pts = [at(qa, eave - 0.03), at(qb, eave - 0.03), at(qb, eave + 0.03), at(qa, eave + 0.03)]
        m.poly(pts, getattr(tint, "mat", "stone_cloister"), [tint(p[0], eave - 1.0, p[2]) for p in pts], facing=(facing, 0, 0) if axis == "x" else (0, 0, facing))


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


def free_end(ps, along, line, at, level, d):
    """Whether the wall piece's end toward `d` (-1 or 1) stands free: no piece carries on from it and no wall crosses it."""
    if any(a == along and l == line and t == at + 4 * d and lv == level for a, l, t, lv, k, o in ps):
        return False
    other, e = ("z" if along == "x" else "x"), at + 2 * d
    return not any(a == other and l == e and lv == level and abs(t - line) <= 2 for a, l, t, lv, k, o in ps)


def walls(m, tints, outside, recesses=None):
    """Every wall piece's two faces, its core, its top and its free ends.
    `recesses`: {(along, line, level, side): [(centre, half width, foot,
    head), ...]}: blind openings in one face, as deep as the wall's middle
    (its dark core is their back)."""
    ps = pieces()
    have = {(a, l, at, lv) for a, l, at, lv, k, o in ps}
    recesses = recesses or {}
    made, left, caps, ends = set(), {}, 0, 0
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
        # Its top, where nothing stands on it: a wall is two faces, and from
        # a taller room one looks down between them.
        if (along, line, at, level + 1) not in have:
            y = base + 4.0
            pts = [(a0, y, line - F), (a1, y, line - F), (a1, y, line + F), (a0, y, line + F)] if along == "x" else [(line - F, y, a0), (line - F, y, a1), (line + F, y, a1),
                                                                                                                   (line + F, y, a0)]
            m.poly(pts, "stone_rubble", (0.2, 0.2, 0.19, 1.0), facing=(0, 1, 0))
            caps += 1
        # Its end, where it stands free (the corner posts of the greybox are not read).
        for d in (-1, 1):
            if free_end(ps, along, line, at, level, d):
                w = at + d * (2.0 + F)
                a, b = ((w, line - F), (w, line + F)) if along == "x" else ((line - F, w), (line + F, w))
                cp.panel(m, a, b, base, base + 4.0, (d, 0, 0) if along == "x" else (0, 0, d), getattr(outside, "mat", "stone_cloister"), outside, 1.6, 1.2)
                ends += 1
    for (along, line, level, s, cls), items in groups.items():
        if (cls == "cloister" and level == 0) or (along, line, s) in SKIP:
            why = "the cloister's own back wall" if cls == "cloister" else "SKIP"
            left[why] = left.get(why, 0) + len(items)
            made.update((along, line, at, level, s) for at, kind in items)
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
            cuts += [c for c in recesses.get((along, line, level, s), ()) if ua < c[0] - c[1] and c[0] + c[1] < ub]
            ch.face(t, sl, ua, ub, ya, yb, tint, cuts)
            made.update((along, line, at, level, s) for at, kind in run)
    # The audit: every piece's two faces are made, or left out on purpose.
    missing = []
    for along, line, at, level, kind, only in ps:
        for s in (1, -1):
            if only and s != only:
                left["the church's side"] = left.get("the church's side", 0) + 1
            elif (along, line, at, level, s) not in made:
                missing.append((along, line, at, level, s))
    print("walls: %d pieces, %d faces made or left on purpose (%s), %d tops, %d free ends, %d faces MISSING %s" % (
        len(ps), len(made), ", ".join("%s: %d" % kv for kv in sorted(left.items())), caps, ends, len(missing), missing or ""))


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


def open_roof(m, axis, a0, a1, c, half, eave, ridge, trusses, braced=False, plate=2 * F - 0.02):
    """A roof seen from below: boards, rafters, purlins, and a truss at each
    of `trusses`. `plate`: how far inside `half` the side walls' inner faces
    stand; a board there shuts the eaves from the wall's head up to the
    roof's boards, so nothing shows over the wall (None: no board)."""
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
        if plate:
            q, top = s * (half - plate), eave - drop + plate * (ridge - eave) / half
            for wa, wb in zip(cp.steps(a0, a1, 4.0), cp.steps(a0, a1, 4.0)[1:]):
                m.poly([at(wa, q, eave - 0.03), at(wb, q, eave - 0.03), at(wb, q, top), at(wa, q, top)], BOARDS, (0.2, 0.185, 0.17, 1.0),
                       facing=(0, 0, -s) if axis == "x" else (-s, 0, 0))
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


def dull(c, k):
    """A cloth's colour gone dark and brown with age."""
    g = (c[0] + c[1] + c[2]) / 3.0
    return (lerp(c[0], g * 1.1, 0.3) * k, lerp(c[1], g, 0.3) * k, lerp(c[2], g * 0.85, 0.3) * k)


def hanging(m, along, line, s, a0, a1, y0, y1, colours, seed=0.0, dim=0.4, ragged=0.24, down=0):
    """A paned cloth hung on a wall: `line` is the wall's middle, s the side
    it hangs on. Old: dark (`dim`), its foot ragged. `down` (1 or -1): that
    end has come off its rod and hangs."""
    v = line + s * (F + 0.035)
    n = max(int(round((a1 - a0) / 0.55)), 1)
    colours = [dull(c, dim) for c in colours]

    def at(w, y, lift=0.0):
        return (w, y, v + s * lift) if along == "x" else (v + s * lift, y, w)

    def rnd(i, k):
        return (math.sin(i * 7.3 + seed * 1.7 + k * 3.1) * 43758.5453) % 1.0

    def fall(w):
        t = (w - a0) / (a1 - a0)
        return smoothstep(0.3, 1.0, t if down > 0 else 1.0 - t) ** 2 if down else 0.0

    out = (0, 0, s) if along == "x" else (s, 0, 0)
    for i in range(n):
        wa, wb = lerp(a0, a1, i / n), lerp(a0, a1, (i + 1) / n)
        c = colours[i % 2]
        k = 0.85 + 0.25 * rnd(i, 0)
        top, foot = cp.rgba(c, k), cp.rgba(c, k * 0.6)
        torn = 0.55 if rnd(i, 5) > 0.86 else 0.0
        fa = y0 + ragged * rnd(i, 1) ** 2 + torn * rnd(i, 3) - 0.7 * fall(wa)
        fb = y0 + ragged * rnd(i, 2) ** 2 + torn - 0.7 * fall(wb)
        ta, tb = y1 - 0.14 - 1.3 * fall(wa), y1 - 0.14 - 1.3 * fall(wb)
        m.poly([at(wa, fa, 0.05 * fall(wa)), at(wb, fb, 0.05 * fall(wb)), at(wb, tb), at(wa, ta)], "painted", [foot, foot, top, top], facing=out)
        m.poly([at(wa, ta), at(wb, tb), at(wb, tb + 0.14), at(wa, ta + 0.14)], "painted", cp.rgba(colours[2], 0.9), facing=out)
    rod = line + s * (F + 0.06)
    p, q = ((a0 - 0.1, y1 + 0.03, rod), (a1 + 0.1, y1 + 0.03, rod)) if along == "x" else ((rod, y1 + 0.03, a0 - 0.1), (rod, y1 + 0.03, a1 + 0.1))
    m.tube([p, q], [0.018, 0.018], 5, "iron_cart", (0.1, 0.1, 0.1, 1.0))


def on_wall(p, out, proud=0.008):
    """A wall's own frame at `p` on its face: (along, up) to a point just proud of it."""
    ox, oz = out
    return lambda u, v: (p[0] - oz * u + ox * proud, p[1] + v, p[2] + ox * u + oz * proud)


def rim(m, hole, y0, y1, mat, color):
    """The sides of a hole in a floor (x0, x1, z0, z1), looking into it."""
    x0, x1, z0, z1 = hole
    for x, k in ((x0, 1), (x1, -1)):
        m.poly([(x, y0, z0), (x, y0, z1), (x, y1, z1), (x, y1, z0)], mat, color, facing=(k, 0, 0))
    for z, k in ((z0, 1), (z1, -1)):
        m.poly([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], mat, color, facing=(0, 0, k))


def bare(m, g, p, out, w, h, tint, seed):
    """A patch where the plaster has fallen and the rubble shows, damp round it."""
    rng = random.Random(seed)
    at = on_wall(p, out, 0.01)
    n = 16
    ring = [(math.cos(math.tau * i / n) * w * 0.5 * rng.uniform(0.45, 1.0), math.sin(math.tau * i / n) * h * 0.5 * rng.uniform(0.5, 1.0)) for i in range(n)]
    mid = at(0.0, 0.0)
    for (ua, va), (ub, vb) in zip(ring, ring[1:] + ring[:1]):
        pts = [mid, at(ua, va), at(ub, vb)]
        cols = [cp.rgba(tint(*q), 1.0) for q in pts]
        m.poly(pts, getattr(tint, "mat", "stone_rubble"), cols, facing=(out[0], 0, out[1]))
    dress.patch(g, p, out, w * 1.9, h * 1.7, dress.DARK, 0.42, seed)


def crosses(g, p, out, w, h, count, seed):
    """Small crosses scratched over and over into one patch of wall."""
    rng = random.Random(seed)
    at = on_wall(p, out, 0.012)
    c = (0.03, 0.028, 0.025, 0.85)
    for _ in range(count):
        u, v = rng.gauss(0.0, w * 0.22), rng.gauss(0.0, h * 0.22)
        size, tilt = rng.uniform(0.07, 0.17), rng.uniform(-0.3, 0.3)
        du, dv = math.sin(tilt), math.cos(tilt)
        for cu, cv, eu, ev, half in ((u, v, du, dv, size * 0.5), (u + du * size * 0.2, v + dv * size * 0.2, dv, -du, size * 0.3)):
            t = 0.005
            pts = [at(cu - eu * half - ev * t, cv - ev * half + eu * t), at(cu - eu * half + ev * t, cv - ev * half - eu * t),
                   at(cu + eu * half + ev * t, cv + ev * half - eu * t), at(cu + eu * half - ev * t, cv + ev * half + eu * t)]
            g.poly(pts, dress.GRIME, c, facing=(out[0], 0, out[1]))


def wash(g, at, facing, loop, colour, strength, seed, inner=None):
    """Old paint on a wall, most of it gone: the shape `loop` ((u, v)
    points), or the band between `inner` and `loop`."""
    def col(u, v):
        return (colour[0], colour[1], colour[2], strength * smoothstep(0.15, 0.6, fbm(u * 2.2, v * 2.2, 1.0, 3, seed)))

    n = len(loop)
    if inner:
        for i in range(n):
            q = [loop[i], loop[(i + 1) % n], inner[(i + 1) % n], inner[i]]
            g.poly([at(u, v) for u, v in q], dress.GRIME, [col(u, v) for u, v in q], facing=facing)
        return
    cu, cv = sum(q[0] for q in loop) / n, sum(q[1] for q in loop) / n
    for i in range(n):
        q = [(cu, cv), loop[i], loop[(i + 1) % n]]
        g.poly([at(u, v) for u, v in q], dress.GRIME, [col(u, v) for u, v in q], facing=facing)


def hood(m, x0, x1, n0, n1, zw, s, depth, y0, y1, tint):
    """A stone hood over a hearth against the wall face z = zw (looking s):
    its lip from x0 to x1 at y0, `depth` out, drawing in to n0..n1 at y1."""
    mat = getattr(tint, "mat", "stone_rubble")
    zf, zb, ym = zw + s * depth, zw + s * 0.26, y0 + 0.3

    def col(p):
        # Sooted from the lip up.
        return cp.rgba(tint(*p), lerp(0.28, 0.75, smoothstep(y0, y1, p[1])))

    def quad(pts, facing):
        m.poly(pts, mat, [col(q) for q in pts], facing=facing)

    quad([(x0, y0, zf), (x1, y0, zf), (x1, ym, zf), (x0, ym, zf)], (0, 0, s))
    quad([(x0, ym, zf), (x1, ym, zf), (n1, y1, zb), (n0, y1, zb)], (0, 0.5, s))
    for xa, na, k in ((x0, n0, -1), (x1, n1, 1)):
        quad([(xa, y0, zw), (xa, y0, zf), (xa, ym, zf), (xa, ym, zw)], (k, 0, 0))
        quad([(xa, ym, zw), (xa, ym, zf), (na, y1, zb), (na, y1, zw)], (k, 0.4, 0))
    m.poly([(x0, y0, zw), (x1, y0, zw), (x1, y0, zf), (x0, y0, zf)], mat, (0.03, 0.03, 0.03, 1.0), facing=(0, -1, 0))
    # Inside it: black.
    m.poly([(x0, ym, zf - s * 0.02), (x1, ym, zf - s * 0.02), (n1, y1, zb - s * 0.02), (n0, y1, zb - s * 0.02)], mat, (0.02, 0.02, 0.02, 1.0), facing=(0, -0.5, -s))


def roof(m, along, lo, hi, a0, a1, eave, ridge, mat, color, over=(0.5, 0.5), ends=(0.5, 0.5), tile=1.8, under=(0.25, 0.25, 0.25)):
    """cp.gable_roof with an overhang of its own for each eave (`over`: the
    low side's and the high side's) and each end (`ends`): lo..hi across,
    a0..a1 along the ridge. An eave that stands over a cloister walk, or
    over a room, stops at the wall (0)."""
    c, cu = (color if len(color) == 4 else cp.rgba(color)), cp.rgba(under)
    mid, half = (lo + hi) * 0.5, (hi - lo) * 0.5
    wa, wb = a0 - ends[0], a1 + ends[1]

    def at(w, q, y):
        return (w, y, q) if along == "x" else (q, y, w)

    for side, ov in ((-1, over[0]), (1, over[1])):
        run, drop = half + ov, (ridge - eave) * ov / half
        slope = math.hypot(run, ridge - eave + drop)
        pts = [at(wa, mid + side * run, eave - drop), at(wb, mid + side * run, eave - drop), at(wb, mid, ridge), at(wa, mid, ridge)]
        uv = [(wa / tile, 0.0), (wb / tile, 0.0), (wb / tile, slope / tile), (wa / tile, slope / tile)]
        m.poly(pts, mat, c, uv, facing=(0, 1, side * 0.5) if along == "x" else (side * 0.5, 1, 0))
        m.poly(pts, mat, cu, facing=(0, -1, -side * 0.5) if along == "x" else (-side * 0.5, -1, 0))


def moss(m, along, lo, hi, eave, ridge, side, a, b, reach, seed, over=0.5):
    """Moss up from the eaves of one slope of a cp.gable_roof made with the
    same numbers: between `a` and `b` along it, up to `reach` of the slope."""
    mid, half = (lo + hi) * 0.5, (hi - lo) * 0.5
    run, drop = half + over, (ridge - eave) * over / half
    slope = math.hypot(run, ridge - eave + drop)

    def at(w, f):
        q, y = mid + side * run * (1.0 - f), lerp(eave - drop, ridge, f) + 0.035
        return (w, y, q) if along == "x" else (q, y, w)

    ws = cp.steps(a, b, 1.1)
    tops = [reach * (0.55 + 0.6 * fbm(w, seed, 0.35, 2, seed)) for w in ws]
    tops[0] = tops[-1] = 0.03
    for i in range(len(ws) - 1):
        q = [(ws[i], 0.0), (ws[i + 1], 0.0), (ws[i + 1], tops[i + 1]), (ws[i], tops[i])]
        k = 0.7 + 0.25 * fbm(ws[i], seed, 0.9, 2, 3.0)
        m.poly([at(w, f) for w, f in q], "roof_mossy", (k, k, k * 0.95, 1.0), [(w / 1.8, f * slope / 1.8) for w, f in q], facing=(0, 1, 0))


def torch(m, g, x, y, z, ox, oz):
    """A bracket and its burnt-out torch, and the soot over it (unless env_crypt's torch has come to make its own)."""
    cr.torch(m, x, y, z, ox, oz)
    if "soot" not in inspect.getsource(cr.torch):
        dress.soot(g, (x, y + 0.3, z), (ox, oz), 0.5, 1.3, 0.8)


def stack(m, x0, x1, z0, z1, y0, y1, tint):
    """A chimney stack."""
    cp.slab(m, (x0, y0, z0), (x1, y1, z1), "stone_cloister", tint, faces="xXzZY", step=1.2)
    m.box((x0 - 0.07, y1 - 0.3, z0 - 0.07), (x1 + 0.07, y1 - 0.14, z1 + 0.07), "stone_cloister", pale(0.7))
    m.box((x0 + 0.18, y1, z0 + 0.18), (x1 - 0.18, y1 + 0.02, z1 - 0.18), "window_dark", (0, 0, 0, 1), faces="Y")


def dressing(wall_m, fit, dr, roof_m, floor_m, tints):
    """What makes the ranges old and uneasy: three figures, the damp, the webs."""
    stone = (0.4, 0.39, 0.36)
    # 1. At the day stair's head, in the niche the stair climbs toward: a hooded figure.
    dress.figure(fit, (20.0 - F + 0.21, 4.95, -14.0), -math.pi * 0.5, 1.62, "stone_church", stone)
    fit.box((20.0 - F - 0.1, 4.83, -14.6), (20.0 - F, 4.95, -13.4), "stone_church", pale(0.6), faces="xzZyY")
    dress.run(dr, (20.0 - F, 4.83, -14.2), (-1, 0), 0.3, 0.8, dress.DARK, 0.5, 2.0)
    # 2. The refectory's reader, bowed in his niche over the tables: a ledge for the book.
    dress.figure(fit, (10.0, 1.62, 4.0 - F + 0.2), math.pi, 1.5, "stone_church", stone, bowed=1.0)
    fit.box((9.4, 1.52, 4.0 - F - 0.11), (10.6, 1.62, 4.0 - F), "stone_church", pale(0.6), faces="xXzyY")
    # 3. Over the chapter house's door, on the way out: a skull on a bracket.
    x = 12.0 + F
    fit.tube([(x + 0.07, 2.2, -18.0), (x + 0.07, 2.26, -18.0), (x + 0.07, 2.3, -18.0)], [0.03, 0.1, 0.13], 6, "stone_church", pale(0.6), caps=True)
    dress.skull(fit, (x + 0.09, 2.3, -18.0), math.pi * 0.5, 1.15, jaw=False)

    # The undercroft's walled-up door (east, toward the graveyard): its blocking, paler and rougher.
    under = tints["undercroft"]
    block = lambda x, y, z: cp.rgba(under(x, y + 1.7, z + 9.0), 1.25)
    cp.panel(wall_m, (20.0 - F + 0.04, -2.3), (20.0 - F + 0.04, -1.3), 0.0, 2.05, (-1, 0, 0), "stone_rubble", block, 0.5, 0.45)
    floor_m.poly([(20.0 - F, 0.056, -2.3), (20.0 - F + 0.04, 0.056, -2.3), (20.0 - F + 0.04, 0.056, -1.3), (20.0 - F, 0.056, -1.3)], "flags_worn", (0.4, 0.4, 0.38, 1.0),
                 facing=(0, 1, 0))
    dress.crack(dr, (20.0 - F + 0.04, 0.3, -1.9), (-1, 0), 1.5, 4)
    # Webs across the lockers' corners; damp along the undercroft's feet and the slype's.
    for z, k, seed in ((-1.8, -1, 1), (2.0, 1, 2)):
        dress.cobweb(dr, (12.0 + F + 0.02, 2.2, z + 0.55 * k), (0, 0, -k), (0, -1, 0), 0.75, seed)
    dress.cobweb(dr, (12.0 + F + 0.02, 0.75, 2.55), (0, 0, -1), (0, 1, 0), 0.5, 3)
    for xw, ox, za, zb, seed in ((12.0 + F, 1, -1.1, 1.3, 1.0), (20.0 - F, -1, 3.0, 11.5, 2.0), (12.0 + F, 1, 2.7, 11.5, 3.0), (20.0 - F, -1, -3.4, -2.5, 4.0)):
        dress.damp(dr, (xw, za), (xw, zb), 0.056, (ox, 0), 1.3, dress.GREEN, 0.55, seed)
    for zw, oz, seed in ((-28.0 + F, 1, 5.0), (-24.0 - F, -1, 6.0)):
        dress.damp(dr, (12.6, zw), (19.4, zw), 0.056, (0, oz), 1.1, dress.GREEN, 0.5, seed)
    dress.cobweb(dr, (20.0 - F - 0.03, 2.5, -27.5), (0, -1, 0.1), (0, 0.45, 1), 0.9, 4)
    dress.cobweb(dr, (12.0 + F + 0.03, 2.5, -24.5), (0, -1, -0.1), (0, 0.45, -1), 0.8, 5)

    # The hearths. The kitchen's: cheeks on the hearth's block, a hood, the breast up to the roof.
    kit = tints["kitchen"]
    zw = -4.0 + F
    for xa, xb in ((-17.2, -16.95), (-15.05, -14.8)):
        cp.slab(wall_m, (xa, 1.05, zw), (xb, 2.3, -2.3), "stone_rubble", lambda x, y, z: cp.rgba(kit(x, y, z), 0.45), faces="xXZ", step=1.0)
    hood(wall_m, -17.25, -14.75, -16.6, -15.4, zw, 1, 1.3, 2.3, 4.0, kit)
    cp.slab(wall_m, (-16.6, 4.0, zw), (-15.4, 7.5, zw + 0.26), "stone_rubble", lambda x, y, z: cp.rgba(kit(x, y, z), 0.7), faces="xXZ", step=1.2)
    dress.soot(dr, (-16.0, 1.05, zw), (0, 1), 1.9, 1.3, 0.95)
    # The warming room's stands under the vault's springer: soot up the wall and the springer.
    dress.soot(dr, (20.0 - F, 1.05, -8.0), (-1, 0), 1.7, 2.0, 0.9)

    # Plaster. The stair hall: a patch fallen beside the stair, a crack from it, a tide mark.
    hall, parl, ref, dorm = tints["stairhall"], tints["parlour"], tints["refectory"], tints["dorm"]
    rub = cp.stone_tint(0.0, 5.0, clean=(0.6, 0.58, 0.54), seed=13.0, worn=0.0)
    rub.mat = "stone_rubble"
    bare(wall_m, dr, (16.2, 2.7, -12.0 - F), (0, -1), 1.7, 1.2, rub, 3)
    bare(wall_m, dr, (17.1, 2.2, -12.0 - F), (0, -1), 0.7, 0.6, rub, 6)
    dress.crack(dr, (16.0, 0.8, -12.0 - F), (0, -1), 1.6, 7)
    dress.damp(dr, (12.6, -12.0 - F), (19.4, -12.0 - F), 0.056, (0, -1), 0.9, dress.DARK, 0.4, 8.0)
    # The parlour: tide marks, a crack, and by the stores' door somebody's crosses.
    dress.damp(dr, (-19.4, -16.0 + F), (-14.6, -16.0 + F), 0.056, (0, 1), 1.0, dress.DARK, 0.42, 9.0)
    dress.damp(dr, (-17.4, -12.0 - F), (-12.6, -12.0 - F), 0.056, (0, -1), 1.0, dress.DARK, 0.42, 10.0)
    dress.crack(dr, (-18.9, 2.1, -16.0 + F), (0, 1), 1.7, 11)
    crosses(dr, (-14.4, 1.35, -12.0 - F), (0, -1), 1.3, 1.0, 26, 5)
    # The refectory: streaks down from the wall head, a tide mark over the panelling, a crack, and at the east end,
    # over the hanging, what is left of a painting: a seated figure in a pointed oval.
    for xr, line, s, seed in ((-7.3, -4.0, 1, 1.0), (-0.2, -4.0, 1, 2.0), (4.1, -4.0, 1, 3.0), (-4.2, 4.0, -1, 4.0), (0.3, 4.0, -1, 5.0), (4.0, 4.0, -1, 6.0)):
        dress.run(dr, (xr, 4.0, line + s * F), (0, s), 0.5, 1.5 + 0.5 * math.sin(seed), dress.DARK, 0.5, seed)
    dress.damp(dr, (-5.5, -4.0 + F), (-2.8, -4.0 + F), 1.53, (0, 1), 0.9, dress.DARK, 0.4, 12.0)
    dress.damp(dr, (2.6, -4.0 + F), (5.4, -4.0 + F), 1.53, (0, 1), 0.9, dress.DARK, 0.4, 15.0)
    dress.damp(dr, (-1.5, 4.0 - F), (1.3, 4.0 - F), 1.53, (0, -1), 0.8, dress.DARK, 0.4, 13.0)
    dress.damp(dr, (6.5, 4.0 - F), (7.7, 4.0 - F), 1.53, (0, -1), 0.8, dress.DARK, 0.4, 16.0)
    dress.crack(dr, (0.4, 1.6, -4.0 + F), (0, 1), 2.0, 14)
    at = on_wall((12.0 - F - 0.012, 4.0, 0.0), (-1, 0), 0.01)
    oval = lambda hw, hh: [(hw * math.sin(a) * abs(math.sin(a)) ** 0.3, 1.95 - hh * math.cos(a)) for a in [math.tau * i / 20 for i in range(20)]]
    ochre, earth, robe = (0.3, 0.2, 0.08), (0.27, 0.1, 0.06), (0.07, 0.08, 0.11)
    wash(dr, at, (-1, 0, 0), oval(1.0, 1.55), ochre, 0.75, 3.0, oval(0.84, 1.38))
    wash(dr, at, (-1, 0, 0), oval(0.84, 1.38), earth, 0.3, 4.0)
    wash(dr, at, (-1, 0, 0), [(-0.5, 0.75), (0.5, 0.75), (0.42, 1.5), (0.26, 2.2), (-0.26, 2.2), (-0.42, 1.5)], robe, 0.7, 5.0)
    disc = lambda r, v: [(r * math.cos(math.tau * i / 12), v + r * math.sin(math.tau * i / 12)) for i in range(12)]
    wash(dr, at, (-1, 0, 0), disc(0.36, 2.48), ochre, 0.8, 6.0, disc(0.2, 2.48))
    wash(dr, at, (-1, 0, 0), disc(0.19, 2.46), earth, 0.6, 7.0)
    # The dormitory: runs under its windows, stains from the wall head, a crack at each end.
    for along, line, at_, level, kind, only in pieces():
        if kind != "wall_window":
            continue
        for s in (1, -1):
            wx, wz = (at_, line + s) if along == "x" else (line + s, at_)
            cls = room_at(wx, wz, level)
            if cls == "refectory" or (cls == "cloister" and level == 0) or (cls == "out" and level == 1 and (line, at_) == (12, 2)):
                continue
            if cls not in ("out", "cloister", "dorm"):
                continue
            p = (at_, 4.0 * level + 1.59, line + s * F) if along == "x" else (line + s * F, 4.0 * level + 1.59, at_)
            seed = at_ * 0.37 + line
            dress.run(dr, p, (0, s) if along == "x" else (s, 0), 0.5, 0.75 if cls == "cloister" else 1.2 + 0.5 * fbm(at_, line, 1.0, 2, 2.0), dress.DARK if cls == "dorm" else dress.GREEN,
                      0.45 if cls == "dorm" else 0.5, seed)
    for zr, line, s, seed in ((-20.3, 12.0, 1, 1.0), (-8.2, 12.0, 1, 2.0), (4.4, 12.0, 1, 3.0), (-16.2, 20.0, -1, 4.0), (-4.3, 20.0, -1, 5.0), (8.0, 20.0, -1, 6.0)):
        dress.patch(dr, (line + s * F, 7.45, zr), (s, 0), 1.6, 1.1, dress.DARK, 0.45, seed)
        dress.run(dr, (line + s * F, 7.3, zr + 0.2), (s, 0), 0.4, 1.6, dress.DARK, 0.4, seed)
    dress.crack(dr, (14.4, 8.1, -28.0 + F + 0.03), (0, 1), 2.2, 21)
    dress.patch(dr, (17.6, 9.3, -28.0 + F + 0.03), (0, 1), 2.2, 1.6, dress.DARK, 0.5, 22.0)
    dress.crack(dr, (17.9, 6.3, 12.0 - F), (0, -1), 2.4, 23)
    # Webs in its trusses, at the king post's foot, and in the corners at both ends.
    for z, k, seed in ((-24.0, 1, 11), (-16.0, -1, 12), (-8.0, 1, 13), (4.0, -1, 14), (8.0, 1, 15)):
        dress.cobweb(dr, (16.0 + 0.09 * k, 8.26, z), (k, 0, 0), (0, 1, 0), 1.1, seed)
    dress.cobweb(dr, (20.0 - F - 0.02, 7.95, -28.0 + F + 0.05), (-1, 0.1, 0), (0, 0.1, 1), 1.3, 16, sag=0.25)
    dress.cobweb(dr, (12.0 + F + 0.02, 7.95, 12.0 - F - 0.02), (1, 0.1, 0), (0, 0.1, -1), 1.2, 17, sag=0.25)
    # And in the refectory's, the granary's and the latrine's corners.
    dress.cobweb(dr, (-0.12, 4.26, 0.09), (0, 0, 1), (0, 1, 0), 1.0, 18)
    dress.cobweb(dr, (-12.0 + F + 0.02, 3.95, -4.0 + F + 0.02), (1, 0.1, 0), (0, 0.1, 1), 1.1, 19, sag=0.25)
    dress.cobweb(dr, (-20.0 + F + 0.02, 3.95, -28.0 + F + 0.05), (1, 0.1, 0), (0, 0.1, 1), 1.3, 20, sag=0.25)
    dress.cobweb(dr, (-15.91, 4.26, -24.0), (1, 0, 0), (0, 1, 0), 1.0, 21)
    dress.cobweb(dr, (12.0 + F + 0.02, 3.6, 20.0 - F - 0.02), (1, 0, 0), (0, -1, 0), 0.9, 22)
    dress.cobweb(dr, (20.0 - F - 0.02, 3.6, 12.0 + F + 0.02), (0, 0, 1), (0, -1, 0), 0.8, 23)
    dress.damp(dr, (12.6, 20.0 - F), (19.4, 20.0 - F), 0.0, (0, -1), 1.5, dress.GREEN, 0.6, 24.0)

    # The roofs: moss up from the eaves where the sun doesn't dry them.
    moss(roof_m, "z", 11.6, 20.4, 8.0, 12.0, 1, -20.0, -3.0, 0.3, 1.0)
    moss(roof_m, "z", 11.6, 20.4, 8.0, 12.0, 1, 5.0, 18.0, 0.36, 2.0)
    moss(roof_m, "z", 11.6, 20.4, 8.0, 12.0, -1, -26.0, -12.0, 0.25, 3.0)
    moss(roof_m, "x", -4.4, 4.4, 4.0, 8.0, -1, -10.0, 9.0, 0.4, 4.0, over=0.0)
    moss(roof_m, "z", -20.4, -11.6, 4.0, 8.0, 1, -26.0, -8.0, 0.35, 5.0, over=0.0)
    moss(roof_m, "z", -20.4, -11.6, 4.0, 8.0, -1, -6.0, 11.0, 0.3, 6.0)


def build():
    porter.reset(617)
    cl.STONE = "stone_church"
    wall_m, roof_m, ceil_m, vault_m, floor_m, fit, dr = (porter.Mesh(n) for n in ("Walls", "Roofs", "Ceilings", "Vaults", "Floors", "Fittings", "Dressing"))
    outside = cp.stone_tint(0.0, 8.0, seed=41.0, worn=0.4)
    outside.mat = "stone_cloister"
    tints = {name: styled(r[5], 3.0 + 2.0 * i) for i, (name, r) in enumerate(ROOMS.items())}
    # Blind openings: a niche at the day stair's head, the reader's niche in
    # the refectory, two lockers and a walled-up door in the undercroft.
    recesses = {("z", 20, 1, -1): [(-14.0, 0.42, 4.95, 6.72)], ("x", 4, 0, -1): [(10.0, 0.46, 1.62, 3.24)],
                ("z", 12, 0, 1): [(-1.8, 0.55, 0.75, 2.2), (2.0, 0.55, 0.75, 2.2)], ("z", 20, 0, -1): [(-1.8, 0.5, 0.0, 2.05)]}
    walls(wall_m, tints, outside, recesses)

    # Roofs: tile outside, timber inside, gables where they end.
    tile = (0.85, 0.8, 0.76)
    # (Each stops short where it runs into a taller wall, and overhangs its own gables, so no light gets in at the verge.)
    cp.gable_roof(roof_m, 11.6, 20.4, -27.5, 20.4, 8.0, 12.0, "roof_tiles", tile, along="z", over=0.5)
    # The eaves over the cloister's walks stop at the wall (an overhang there hung a slab of tile under the walks' vault):
    # the refectory's north eave, and the west range's east eave as far as the refectory's south wall (past the cloister
    # it would hang inside the refectory's west end). Every other eave and verge keeps its 0.5 m.
    roof(roof_m, "x", -4.4, 4.4, -12.0, 11.5, 4.0, 8.0, "roof_tiles", tile, over=(0.0, 0.5), ends=(0.4, 0.5))
    roof(roof_m, "z", -20.4, -11.6, -27.5, 4.2, 4.0, 8.0, "roof_tiles", tile, over=(0.5, 0.0), ends=(0.5, 0.0))
    roof(roof_m, "z", -20.4, -11.6, 4.2, 12.4, 4.0, 8.0, "roof_tiles", tile, over=(0.5, 0.5), ends=(0.0, 0.5))
    open_roof(ceil_m, "z", -28.0 + F, 20.0 - F, 16.0, 4.4, 8.0, 12.0, [-24.0 + 4.0 * i for i in range(11)], braced=True)
    open_roof(ceil_m, "x", -12.0 + F, 12.0 - F, 0.0, 4.4, 4.0, 8.0, [-8.0, -4.0, 0.0, 4.0, 8.0], braced=True)
    open_roof(ceil_m, "z", -28.0 + F, -4.0 - F, -16.0, 4.4, 4.0, 8.0, [-24.0, -20.0, -8.0])
    open_roof(ceil_m, "z", -4.0 + F, 12.0 - F, -16.0, 4.4, 4.0, 8.0, [0.0, 8.0])
    dorm_t, west_t, kit_t = high(tints["dorm"], 8.0), tints["granary"], tints["kitchen"]
    # (The two north gables stand a hair proud of the church's wall, whose outer face comes down to the roofs' line.)
    gable(wall_m, "z", -28.0 + F + 0.03, 16.0, 4.4, 8.0, 12.0, 1, dorm_t)
    gable(wall_m, "z", 12.0 - F, 16.0, 4.4, 8.0, 12.0, -1, dorm_t)
    gable(wall_m, "z", 12.0 + F, 16.0, 4.4, 8.0, 12.0, 1, tints["latrine1"])
    gable(wall_m, "z", 20.0 - F, 16.0, 4.4, 8.0, 12.0, -1, tints["latrine1"])
    gable(wall_m, "z", 20.0 + F, 16.0, 4.4, 8.0, 12.0, 1, outside)
    gable(wall_m, "x", -12.0 + F, 0.0, 4.4, 4.0, 8.0, 1, high(tints["refectory"], 4.0))
    gable(wall_m, "x", -12.0 - F, 0.0, 4.4, 4.0, 8.0, -1, outside)
    gable(wall_m, "z", -28.0 + F + 0.03, -16.0, 4.4, 4.0, 8.0, 1, west_t)
    for xm, y in ((16.0, 8.0), (-16.0, 4.0)):
        wall_m.poly([(xm - 4.4, y, -28.0 + F - 0.01), (xm + 4.4, y, -28.0 + F - 0.01), (xm + 4.4, y, -28.0 + F + 0.03), (xm - 4.4, y, -28.0 + F + 0.03)], "plaster_abbey",
                    (0.3, 0.29, 0.27, 1.0), facing=(0, -1, 0))
    gable(wall_m, "z", -4.0 - F, -16.0, 4.4, 4.0, 8.0, -1, tints["stores"])
    gable(wall_m, "z", -4.0 + F, -16.0, 4.4, 4.0, 8.0, 1, kit_t)
    gable(wall_m, "z", 12.0 - F, -16.0, 4.4, 4.0, 8.0, -1, tints["bakehouse"])
    gable(wall_m, "z", 12.0 + F, -16.0, 4.4, 4.0, 8.0, 1, outside)
    for axis, w, c, eave, facing, name in (("x", -12.0 + F, 0.0, 4.0, 1, "refectory"), ("x", 12.0 - F - 0.012, 0.0, 4.0, -1, "refectory"),
                                           ("z", -28.0 + F + 0.03, 16.0, 8.0, 1, "dorm"), ("z", 12.0 - F, 16.0, 8.0, -1, "dorm"),
                                           ("z", -16.0 + F, -16.0, 4.0, 1, "parlour"), ("z", -12.0 - F, -16.0, 4.0, -1, "parlour")):
        seam(wall_m, axis, w, c, 4.4, eave, facing, tints[name])
    # The partitions under one roof go up to it (granary / parlour / stores, kitchen / bakehouse).
    for z, north, south in ((-16.0, "granary", "parlour"), (-12.0, "parlour", "stores"), (4.0, "kitchen", "bakehouse")):
        gable(wall_m, "z", z - F, -16.0, 4.4, 4.0, 8.0, -1, high(tints[north], 4.0) if north == "parlour" else tints[north])
        gable(wall_m, "z", z + F, -16.0, 4.4, 4.0, 8.0, 1, high(tints[south], 4.0) if south == "parlour" else tints[south])
    # (The kitchen sees the foot of the refectory's west gable under its own roof: in the kitchen's stone.)
    cp.panel(wall_m, (-12.0 - F - 0.012, -4.0 + F), (-12.0 - F - 0.012, 4.0 - F), 4.0, 4.7, (-1, 0, 0), "stone_rubble", kit_t, 1.6, 1.2)
    # The refectory's east end above its own wall is the east range's wall: plastered on this side, and the dormitory's
    # window that would look into the roof (the roof's block shuts it) is shuttered.
    gable(wall_m, "x", 12.0 - F - 0.012, 0.0, 4.4, 4.0, 8.0, -1, high(tints["refectory"], 4.0))
    wall_m.poly([(12.0 - F - 0.012, 4.0, -4.0 + F), (12.0 - F - 0.012, 4.0, 4.0 - F), (12.0 - F + 0.01, 4.0, 4.0 - F), (12.0 - F + 0.01, 4.0, -4.0 + F)], "plaster_abbey",
                (0.6, 0.59, 0.56, 1.0), facing=(0, -1, 0))
    for k, z in enumerate(cp.steps(1.69, 2.31, 0.21)[:-1]):
        b = 0.2 + 0.05 * (k % 2)
        fit.poly([(12.06, 5.59, z), (12.06, 5.59, z + 0.2), (12.06, 6.81, z + 0.2), (12.06, 6.81, z)], OAK, (b, b * 0.92, b * 0.85, 1.0), facing=(1, 0, 0))
    for y in (5.8, 6.55):
        fit.box((12.06, y, 1.69), (12.1, y + 0.1, 2.31), OAK, (0.17, 0.15, 0.13, 1.0), faces="XyY")
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
    # The day stair's hole: trimmers under the boards, and the floor's thickness.
    trim = (0.2, 0.185, 0.17, 1.0)
    rim(ceil_m, hole, 3.5, 4.026, BOARDS, trim)
    hx0, hx1, hz0, hz1 = hole
    ceil_m.box((hx0 - 0.14, 3.5, hz0 - 0.14), (hx1 + 0.14, 3.7, hz0), BOARDS, trim, faces="xXzy")
    ceil_m.box((hx0 - 0.14, 3.5, hz1), (hx1 + 0.14, 3.7, hz1 + 0.14), BOARDS, trim, faces="xXZy")
    ceil_m.box((hx0 - 0.14, 3.5, hz0), (hx0, 3.7, hz1), BOARDS, trim, faces="xy")
    ceil_m.box((hx1, 3.5, hz0), (hx1 + 0.14, 3.7, hz1), BOARDS, trim, faces="Xy")

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
            # Its edge over the mill race (the race's own wall carries on below).
            floor_m.poly([(rect[0], -0.3, 16.0), (rect[1], -0.3, 16.0), (rect[1], y0, 16.0), (rect[0], y0, 16.0)], "stone_rubble", (0.3, 0.3, 0.29, 1.0), facing=(0, 0, 1))
        elif name == "granary":
            floor(floor_m, rect, y0, "flags", 23.0, (-19.4, -18.2, -25.0, -19.0))
            # The crypt model makes this hole's rim with the well below it (env_crypt.py); only its south end is made here.
            floor_m.poly([(-19.4, -0.3, -19.0), (-18.2, -0.3, -19.0), (-18.2, y0, -19.0), (-19.4, y0, -19.0)], "stone_rubble", (0.3, 0.3, 0.29, 1.0), facing=(0, 0, -1))
        else:
            floor(floor_m, rect, y0, kinds.get(name, "flags"), 5.0 + i)
    # Thresholds through the walls, so no gap shows under a door.
    # (Not under the latrine block's two gates: the mill race runs through them, 1.2 m down, and there is no floor.)
    for along, line, at, level, kind, only in pieces():
        if kind == "wall_gate" and along == "z" and line in (12, 20) and 16 < at < 20:
            continue
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
            if (line, x) != (4.0, 10.0):
                hanging(fit, "x", line, s, x - 1.5, x + 1.5, 1.7, 3.7, (red, green, gold), x)
    hanging(fit, "z", 12.0, -1, -2.6, 2.6, 1.3, 3.8, (blue, red, gold), 3.0)

    # The dormitory: hangings between its windows, a rush runner by the beds' feet.
    for line, s, first in ((12.0, 1, -26), (20.0, -1, -22)):
        for z in range(first, 11, 8):
            if (line, z) == (20.0, -14):
                continue  # the niche at the stair's head
            hanging(fit, "z", line, s, z - 1.2, z + 1.2, 5.3, 7.5, (green, gold, red) if (z // 8) % 2 else (red, blue, gold), z, down=1 if (line, z) == (20.0, 2) else 0)
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
                 cp.rgba(dull(red, 0.34), k * 0.8), facing=(-1, 0, 0))
        fit.poly([(xa2, h1 + 0.006, -14.45), (xb2, h1 + 0.006, -14.45), (xb2, h1 + 0.006, -13.55), (xa2, h1 + 0.006, -13.55)], "painted",
                 cp.rgba(dull(red, 0.34), k), facing=(0, 1, 0))
        for z in (-14.45, -13.63):
            fit.poly([(xa2, h1 + 0.007, z), (xb2, h1 + 0.007, z), (xb2, h1 + 0.007, z + 0.08), (xa2, h1 + 0.007, z + 0.08)], "painted",
                     cp.rgba(dull(gold, 0.34), 0.9), facing=(0, 1, 0))
    hanging(fit, "x", -16.0, 1, 14.0, 18.0, 1.2, 3.3, (red, green, gold), 5.0)

    # The chapter house: a blind arcade round it and a painted panel over the east seats.
    for place, s, us in ((lambda u, y, v: (20.0 - v, y, u), 1, (-22.0, -18.0)), (lambda u, y, v: (u, y, -24.0 + v), 1, (14.0, 18.0)),
                         (lambda u, y, v: (u, y, -16.0 + v), -1, (14.0, 18.0))):
        t = cl.Turned(wall_m, place)
        for u in us:
            ch.blind_arcade(t, s, u)
    px = 20.0 - F - 0.03
    fit.box((px - 0.04, 1.4, -22.95), (px, 2.6, -20.75), OAK, oak, faces="xzZyY")
    for j, c in enumerate((dull(blue, 0.55), dull(red, 0.55), dull(blue, 0.55))):
        za, zb = -22.85 + j * 0.7, -22.85 + (j + 1) * 0.7 - 0.06
        fit.poly([(px - 0.045, 1.5, za), (px - 0.045, 1.5, zb), (px - 0.045, 2.5, zb), (px - 0.045, 2.5, za)], "painted",
                 [cp.rgba(c, 0.7), cp.rgba(c, 0.7), cp.rgba(c, 1.1), cp.rgba(c, 1.1)], facing=(-1, 0, 0))
        zc = (za + zb) * 0.5
        fit.poly([(px - 0.05, 1.6, zc - 0.12), (px - 0.05, 1.6, zc + 0.12), (px - 0.05, 2.2, zc + 0.09), (px - 0.05, 2.35, zc), (px - 0.05, 2.2, zc - 0.09)],
                 "painted", cp.rgba(dull(gold, 0.5), 1.0), facing=(-1, 0, 0))

    # Iron brackets, their torches burnt out, soot over each. (None in a doorway or a window.)
    for x, y, z, ox, oz in ((16.0, 1.9, -28.0 + F, 0, 1), (20.0 - F, 1.9, 0.0, -1, 0), (12.0 + F, 1.9, 8.0, 1, 0), (20.0 - F, 5.9, -12.0, -1, 0),
                            (12.0 + F, 5.9, 0.0, 1, 0), (-17.0, 1.9, -16.0 + F, 0, 1), (-8.0, 2.2, -4.0 + F, 0, 1), (8.0, 2.2, 4.0 - F, 0, -1)):
        torch(fit, dr, x, y, z, ox, oz)

    dressing(wall_m, fit, dr, roof_m, floor_m, tints)

    wall_m.build()
    roof_m.build()
    ceil_m.build()
    vault_m.build(smooth=True)
    floor_m.build()
    fit.build()
    dr.build()
    porter.export("env_ranges")


if __name__ == "__main__":
    build()
