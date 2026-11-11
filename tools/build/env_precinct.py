"""The rest of the precinct (every night): its wall, its ground, and the
buildings that stand apart from the cloister: the porter's cell and the
guesthouse in the outer court, the charnel house, the infirmary and the
mill. The model is in the abbey's own coordinates and is laid over the
greybox (abbey.tscn's Grounds, outer_court.tscn, graveyard_infirmary.tscn),
which still stops people and shapes the navmesh but is no longer drawn.

The walls are read from those scenes, as the ranges' are (env_ranges.py).
The precinct wall's face to the lane is the lane's own model, so it is not
made here.

`env_precinct`:
- Walls: the precinct wall inside (and outside on its north, east and
  south), with its squints and the gate's arch, under a coping; the five
  buildings inside and out, plaster or rubble within.
- Ceilings and Roofs: every building is open to a timber roof under clay
  tiles; a chimney on the guesthouse and the infirmary.
- Floors: flags in the buildings, earth in the charnel house.
- Ground: read from the ground blocks. Trodden earth in the outer court
  with a flagged path from the gate; gravel between the ranges and the mill
  race; grass in the graveyard and round the infirmary; grass under the
  orchard and tilled rows in the kitchen garden.

Run: tools/build.sh env_precinct
"""
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
import city_parts as cp
import env_ranges as rg
from porter import fbm, lerp, smoothstep

cl = rg.cl
pale = cl.pale
F = rg.F

rg.SCENES = ("outer_court", "graveyard_infirmary", "../abbey")
rg.BORROWED = ()
rg.SKIP = (("z", -40, -1),)
rg.ROOMS = {
    "cell": (-40, -32, -12, -4, 0, "plaster"),
    "guest": (-36, -24, -24, -16, 0, "plaster"),
    "charnel": (32, 40, -24, -16, 0, "rubble"),
    "infirmary": (24, 36, -4, 4, 0, "plaster"),
    "mill": (24, 32, 8, 16, 0, "rubble"),
}
# Each building's roof: (ridge along, from, to, the ridge's place across, ridge height, what stands at each end: a room, or None for the precinct wall's far side).
ROOFS = {
    "cell": ("x", -40.0, -32.0, -8.0, 8.0),
    "guest": ("x", -36.0, -24.0, -20.0, 8.0),
    "charnel": ("z", -24.0, -16.0, 36.0, 7.8),
    "infirmary": ("x", 24.0, 36.0, 0.0, 8.0),
    "mill": ("x", 24.0, 32.0, 12.0, 8.0),
}


def zone(x, z):
    """What the ground is at a point."""
    if x < -20.0:
        on_path = (abs(z + 2.0) < 1.3 and x < -24.7) or (abs(x + 26.0) < 1.3 and -14.0 < z < -0.7) or (abs(z + 14.0) < 1.3 and x > -27.3)
        return "path" if on_path else "court"
    if z > 20.0:
        return "beds" if 0.0 <= x < 22.0 and 24.0 < z < 36.0 else "grass"
    if 4.0 < z < 16.5 and x < 22.0:
        return "yard"
    return "grass"


GROUND = {
    "court": ("gravel_path", (0.5, 0.42, 0.34)),
    "path": ("flags_worn", (0.8, 0.78, 0.74)),
    "yard": ("gravel_path", (0.72, 0.68, 0.6)),
    "grass": ("grass_leafy", (0.8, 0.86, 0.66)),
    "beds": ("grave_earth", (0.62, 0.52, 0.42)),
}


def ground(m):
    text = open(os.path.join(rg.ROOT, "game/world/abbey/abbey.tscn")).read()
    y = 0.012
    for block in text.split("\n\n"):
        name = re.match(r'\[node name="(Ground_\d+)"', block)
        tr = re.search(r"transform = Transform3D\(([^)]*)\)", block)
        size = re.search(r"size = Vector3\(([^)]*)\)", block)
        if not name or not tr or not size or name.group(1) == "Ground_8":
            continue
        v = [float(q) for q in tr.group(1).split(",")]
        s = [float(q) for q in size.group(1).split(",")]
        x0, x1, z0, z1 = v[9] - s[0] * 0.5, v[9] + s[0] * 0.5, v[11] - s[2] * 0.5, v[11] + s[2] * 0.5
        xs, zs = cp.steps(x0, x1, 1.3), cp.steps(z0, z1, 1.3)
        for xa, xb in zip(xs, xs[1:]):
            for za, zb in zip(zs, zs[1:]):
                kind = zone((xa + xb) * 0.5, (za + zb) * 0.5)
                mat, c = GROUND[kind]
                pts = [(xa, y, za), (xb, y, za), (xb, y, zb), (xa, y, zb)]
                cols = []
                for p in pts:
                    k = 0.72 + 0.5 * fbm(p[0], p[2], 0.12, 3, 2.0)
                    if kind == "beds":
                        k *= 0.8 + 0.3 * (0.5 + 0.5 * math.sin(p[0] * math.pi / 0.65))
                    cols.append(cp.rgba(c, k))
                m.poly(pts, mat, cols, facing=(0, 1, 0))


def build():
    porter.reset(733)
    cl.STONE = "stone_church"
    wall_m, roof_m, ceil_m, floor_m, ground_m = (porter.Mesh(n) for n in ("Walls", "Roofs", "Ceilings", "Floors", "Ground"))
    outside = cp.stone_tint(0.0, 5.0, seed=63.0, worn=0.6)
    outside.mat = "stone_rubble"
    tints = {name: rg.styled(r[5], 31.0 + 2.0 * i) for i, (name, r) in enumerate(rg.ROOMS.items())}
    rg.walls(wall_m, tints, outside)

    # The precinct wall's coping.
    cope = pale(0.62)
    # (Not where the porter's cell and the charnel house stand against it: their gables are there.)
    for x0, x1, z0, z1 in ((-40.5, 40.5, -40.5, -39.5), (-40.5, 40.5, 39.5, 40.5), (-40.5, -39.5, -40.5, -12.4), (-40.5, -39.5, -3.6, 40.5),
                           (39.5, 40.5, -40.5, -24.4), (39.5, 40.5, -15.6, 40.5)):
        wall_m.box((x0, 4.0, z0), (x1, 4.14, z1), "stone_cloister", cope)
        cx, cz = (x0 + x1) * 0.5, (z0 + z1) * 0.5
        along_x = x1 - x0 > 2.0
        a, b = ((x0, 4.3, cz), (x1, 4.3, cz)) if along_x else ((cx, 4.3, z0), (cx, 4.3, z1))
        for s in (-1, 1):
            e0 = (x0, 4.14, cz + s * 0.5) if along_x else (cx + s * 0.5, 4.14, z0)
            e1 = (x1, 4.14, cz + s * 0.5) if along_x else (cx + s * 0.5, 4.14, z1)
            wall_m.poly([e0, e1, b, a], "stone_cloister", cope, facing=(0, 1, s) if along_x else (s, 1, 0))

    tile = (0.85, 0.8, 0.76)
    gable_tint = cp.stone_tint(4.0, 8.0, seed=71.0, worn=0.5)
    gable_tint.mat = "stone_rubble"
    for name, (axis, a0, a1, c, ridge) in ROOFS.items():
        if axis == "x":
            cp.gable_roof(roof_m, a0, a1, c - 4.4, c + 4.4, 4.0, ridge, "roof_tiles", tile, along="x", over=0.5)
        else:
            cp.gable_roof(roof_m, c - 4.4, c + 4.4, a0, a1, 4.0, ridge, "roof_tiles", tile, along="z", over=0.5)
        mid = (a0 + a1) * 0.5
        rg.open_roof(ceil_m, axis, a0 + F, a1 - F, c, 4.4, 4.0, ridge, [mid] if a1 - a0 < 10 else [a0 + 4.0, a1 - 4.0])
        rg.gable(wall_m, axis, a0 + F, c, 4.4, 4.0, ridge, 1, tints[name])
        rg.gable(wall_m, axis, a1 - F, c, 4.4, 4.0, ridge, -1, tints[name])
        rg.gable(wall_m, axis, a0 - F, c, 4.4, 4.0, ridge, -1, gable_tint)
        rg.gable(wall_m, axis, a1 + F, c, 4.4, 4.0, ridge, 1, gable_tint)
        r = rg.ROOMS[name]
        rect = (r[0] + F, r[1] - F, r[2] + F, r[3] - F)
        if name == "charnel":
            ys = 0.056
            pts = [(rect[0], ys, rect[2]), (rect[1], ys, rect[2]), (rect[1], ys, rect[3]), (rect[0], ys, rect[3])]
            floor_m.poly(pts, "grave_earth", [cp.rgba((0.5, 0.44, 0.38), 0.8 + 0.3 * fbm(p[0], p[2], 0.4, 2, 1.0)) for p in pts], facing=(0, 1, 0))
        else:
            rg.floor(floor_m, rect, 0.056, "flags", 40.0 + len(name))
    st = cp.stone_tint(4.0, 9.0, seed=75.0, worn=0.5)
    rg.stack(roof_m, -24.5, -23.5, -20.6, -19.4, 4.0, 8.8, st)
    rg.stack(roof_m, 35.5, 36.5, -0.6, 0.6, 4.0, 8.8, st)
    # Thresholds.
    for along, line, at, level, kind, only in rg.pieces():
        if kind in ("wall_door", "wall_gate"):
            hw = 0.47 if kind == "wall_door" else 1.5
            r = (at - hw, at + hw, line - F, line + F) if along == "x" else (line - F, line + F, at - hw, at + hw)
            floor_m.poly([(r[0], 0.056, r[2]), (r[1], 0.056, r[2]), (r[1], 0.056, r[3]), (r[0], 0.056, r[3])], "flags_worn", (0.6, 0.6, 0.58, 1.0),
                         facing=(0, 1, 0))
    ground(ground_m)

    wall_m.build()
    roof_m.build()
    ceil_m.build()
    floor_m.build()
    ground_m.build()
    porter.export("env_precinct")


if __name__ == "__main__":
    build()
