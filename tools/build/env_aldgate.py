"""Aldgate (night 0, the road in): the city's east gate as the wagon comes to
it at dusk, and as the porter sees it close behind him from inside.

In its own space the wall runs along x and the country is at -z (the
model's front); the road goes through at x = 0. The origin is on the road
under the middle of the wall. tools/build/env_city_wall.py makes the wall
that joins it at x = -9 and 9, in the same space.

- Two round towers of rubble with bands of old tile (London's wall is
  ragstone laced with Roman tile), battered at the foot, corbelled out
  under their battlements. The north tower has a stair turret up its
  back, under a pointed cap, taller than everything else.
- Between them the gate itself, in cut stone: a pointed archway in two
  orders with a hood mould, the portcullis drawn up into it with its teeth
  showing, the oak doors folded back inside, a ribbed vault over the
  passage. Over the arch the city's shield, a weathered saint under a
  canopy, and the windows of the chamber over the gate, candles lit.
- A tiled roof over the chamber, behind the battlements.

Collision: the towers, the turret, the two sides of the passage, and the
wall over it. The road through stays clear (5.4 m wide, 3.4 m to the
springing, 5.6 m to the point).

Run: tools/build.sh env_aldgate
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
import city_parts as cp
from city_parts import rgba

# The passage: half its width, the height the arch springs at, its rise.
HALF, SPRING, RISE = 2.7, 3.4, 2.2
# The outer order of the arch, a step wider.
OUTER_HALF, OUTER_RISE = 3.05, 2.45
# The gate between the towers: x from, x to, z from (outside), z to (inside), height of its walk.
BLOCK = (-4.4, 4.4, -2.8, 3.8, 11.0)
# The towers: how far each side of the road, z, radius, height of their walk.
TOWER_X, TOWER_Z, TOWER_R, TOWER_TOP = 6.9, -0.8, 3.1, 14.5
# The stair turret behind the north tower.
TURRET = (8.5, 1.1, 1.15, 17.6, 20.4)
SIDES = 24

ASHLAR = "stone_blocks"
RUBBLE = "stone_rubble"
PALE = (0.9, 0.89, 0.86)
SOOT = (0.4, 0.39, 0.38)


def gate(m):
    x0, x1, z0, z1, top = BLOCK
    tint = cp.stone_tint(0.0, top + 1.0, seed=1.0)
    dark = lambda x, y, z: tuple(c * (0.62 - 0.2 * porter.smoothstep(2.0, 5.5, y)) for c in tint(x, y, z)[:3]) + (1.0,)
    # The front, with the outer order of the arch; its soffit; the inner order a step back.
    cp.arch_wall(m, z0, x0, x1, 0.0, top, OUTER_HALF, SPRING, OUTER_RISE, (0, 0, -1), ASHLAR, tint)
    cp.vault(m, z0, z0 + 0.45, OUTER_HALF, SPRING, OUTER_RISE, ASHLAR, tint, step=0.5)
    cp.arch_wall(m, z0 + 0.45, -3.4, 3.4, 0.0, 6.3, HALF, SPRING, RISE, (0, 0, -1), ASHLAR, tint)
    cp.arch_band(m, z0, OUTER_HALF, SPRING, OUTER_RISE, 0.34, 0.08, (0, 0, -1), ASHLAR, PALE, y0=0.0)
    # The passage: its walls and vault, dark with a hundred years of smoke, and two ribs across it.
    cp.vault(m, z0 + 0.45, z1, HALF, SPRING, RISE, ASHLAR, dark)
    for z in (-0.2, 1.9):
        cp.vault(m, z, z + 0.32, HALF - 0.12, SPRING, RISE - 0.1, ASHLAR, dark, step=0.4)
        cp.arch_band(m, z, HALF - 0.12, SPRING, RISE - 0.1, 0.14, 0.0, (0, 0, -1), ASHLAR, SOOT, y0=0.0)
        cp.arch_band(m, z + 0.32, HALF - 0.12, SPRING, RISE - 0.1, 0.14, 0.0, (0, 0, 1), ASHLAR, SOOT, y0=0.0)
    # A small door in the passage wall, to the tower stair.
    m.poly([(-HALF + 0.02, 0.0, 2.3), (-HALF + 0.02, 0.0, 3.1), (-HALF + 0.02, 1.75, 3.1), (-HALF + 0.02, 2.05, 2.7),
            (-HALF + 0.02, 1.75, 2.3)], "window_dark", facing=(1, 0, 0))
    # The back, toward the city, and the sides (mostly behind the towers).
    cp.arch_wall(m, z1, x0, x1, 0.0, top, HALF, SPRING, RISE, (0, 0, 1), ASHLAR, tint)
    cp.arch_band(m, z1, HALF, SPRING, RISE, 0.3, 0.07, (0, 0, 1), ASHLAR, PALE, y0=0.0)
    cp.panel(m, (x0, z0), (x0, z1), 0.0, top, (-1, 0, 0), ASHLAR, tint)
    cp.panel(m, (x1, z0), (x1, z1), 0.0, top, (1, 0, 0), ASHLAR, tint)
    # String courses, and the corbel course the front parapet stands out on.
    for y, deep in ((6.3, 0.09), (9.9, 0.07)):
        cp.block(m, (x0, y, z0 - deep), (x1, y + 0.2, z0), ASHLAR, PALE, faces="zyY")
        cp.block(m, (x0, y, z1), (x1, y + 0.2, z1 + deep), ASHLAR, PALE, faces="ZyY")
    cp.block(m, (x0, top - 0.42, z0 - 0.3), (x1, top, z0), ASHLAR, cp.STONE_DARK, faces="zy")
    x = x0 + 0.2
    while x < x1 - 0.3:
        cp.block(m, (x, top - 0.85, z0 - 0.26), (x + 0.3, top - 0.42, z0), ASHLAR, cp.STONE, faces="xXzy")
        x += 0.74
    cp.battlements(m, (x0, z0 - 0.3), (x1, z0 - 0.3), top, (0, 0, -1), ASHLAR, tint, width=1.1, gap=0.75)
    cp.battlements(m, (x0, z1), (x1, z1), top, (0, 0, 1), ASHLAR, tint, width=1.1, gap=0.75)
    # The chamber's roof behind the battlements, and the leads round it.
    m.poly([(x0, top, z0 - 0.3), (x1, top, z0 - 0.3), (x1, top, z1), (x0, top, z1)], ASHLAR, rgba(cp.STONE_DARK), facing=(0, 1, 0))
    cp.gable_roof(m, x0 + 0.3, x1 - 0.3, z0 + 0.5, z1 - 0.6, top + 0.15, top + 3.5, "roof_tiles", (0.8, 0.78, 0.76), over=0.12,
                  sag=0.12)
    for x, s in ((x0 + 0.3, -1), (x1 - 0.3, 1)):
        m.poly([(x, top, z0 + 0.5), (x, top, z1 - 0.6), (x, top + 3.5, (z0 + z1 - 0.1) * 0.5)], RUBBLE, rgba(cp.STONE_DARK),
               facing=(s, 0, 0))
    # The chamber over the gate: its windows to the country and to the city. Candles are lit in it.
    for cx, glass in ((-2.55, "window_candle"), (2.55, "window_dark")):
        for dx in (-0.36, 0.36):
            cp.lancet(m, (cx + dx, z0), 7.35, 0.5, 1.55, (0, 0, -1), glass)
    for cx in (-2.3, 2.3):
        for dx in (-0.36, 0.36):
            cp.lancet(m, (cx + dx, z1), 7.1, 0.5, 1.55, (0, 0, 1), "window_candle")
    cp.lancet(m, (0.0, z1), 7.5, 0.34, 1.0, (0, 0, 1), "window_dark")
    # The city's shield over the point of the arch: a red cross on white, faded.
    zf = z0 - 0.07
    white = porter.srgb(0.62, 0.6, 0.54)
    red = porter.srgb(0.42, 0.1, 0.08)
    m.poly([(-0.36, 7.38, zf), (0.36, 7.38, zf), (0.36, 6.95, zf), (0.0, 6.56, zf), (-0.36, 6.95, zf)], "painted", white,
           facing=(0, 0, -1))
    m.poly([(-0.42, 7.44, zf + 0.03), (0.42, 7.44, zf + 0.03), (0.42, 6.93, zf + 0.03), (0.0, 6.48, zf + 0.03), (-0.42, 6.93, zf + 0.03)],
           ASHLAR, rgba(cp.STONE_DARK), facing=(0, 0, -1))
    m.poly([(-0.07, 6.66, zf - 0.012), (0.07, 6.66, zf - 0.012), (0.07, 7.38, zf - 0.012), (-0.07, 7.38, zf - 0.012)], "painted", red,
           facing=(0, 0, -1))
    m.poly([(-0.36, 7.0, zf - 0.012), (0.36, 7.0, zf - 0.012), (0.36, 7.14, zf - 0.012), (-0.36, 7.14, zf - 0.012)], "painted", red,
           facing=(0, 0, -1))
    # A saint on a bracket under a little stone canopy, worn featureless by the weather.
    cp.block(m, (-0.34, 7.62, z0 - 0.42), (0.34, 7.76, z0), ASHLAR, cp.STONE_DARK, faces="xXzyY")
    figure = [(0.0, 7.76), (0.0, 7.8), (0.0, 8.5), (0.0, 8.86), (0.0, 9.02), (0.0, 9.08), (0.0, 9.2), (0.0, 9.3), (0.0, 9.36)]
    radii = [0.22, 0.24, 0.2, 0.23, 0.17, 0.08, 0.115, 0.1, 0.03]
    grey = [rgba(cp.STONE_DAMP, 1.0 + 0.5 * i / 8.0) for i in range(9)]
    m.tube([(x, y, z0 - 0.2) for x, y in figure], radii, 7, ASHLAR, grey, caps=True, squash=(1.0, 0.72))
    for s in (-1, 1):
        m.poly([(0.0, 10.1, z0 - 0.46), (s * 0.5, 9.62, z0 - 0.46), (s * 0.5, 9.62, z0), (0.0, 10.1, z0)], ASHLAR, rgba(cp.STONE),
               facing=(s, 1, 0))
        m.poly([(0.0, 10.1, z0 - 0.46), (s * 0.5, 9.62, z0 - 0.46), (s * 0.5, 9.5, z0 - 0.46), (0.0, 9.96, z0 - 0.46)], ASHLAR,
               rgba(cp.STONE_DARK), facing=(0, 0, -1))
        m.poly([(0.0, 9.96, z0 - 0.46), (s * 0.5, 9.5, z0 - 0.46), (s * 0.5, 9.5, z0), (0.0, 9.96, z0)], ASHLAR, rgba(SOOT),
               facing=(-s, -1, 0))


def portcullis(m):
    """Drawn up into the arch: only its lower bars and their iron teeth show."""
    z = BLOCK[2] + 0.62
    oak = (0.34, 0.32, 0.3, 1.0)
    iron = (0.5, 0.5, 0.52, 1.0)
    x = -2.4
    while x < 2.41:
        top = cp.arch_height(HALF, SPRING, RISE, x) + 0.05
        foot = 4.3
        if top > foot + 0.2:
            cp.block(m, (x - 0.055, foot, z - 0.055), (x + 0.055, top, z + 0.055), "wood_cart", oak, faces="xXzZ")
            for pts, facing in (([(x - 0.07, foot, z - 0.07), (x + 0.07, foot, z - 0.07), (x, foot - 0.3, z)], (0, -0.3, -1)),
                                ([(x - 0.07, foot, z + 0.07), (x + 0.07, foot, z + 0.07), (x, foot - 0.3, z)], (0, -0.3, 1)),
                                ([(x - 0.07, foot, z - 0.07), (x - 0.07, foot, z + 0.07), (x, foot - 0.3, z)], (-1, -0.3, 0)),
                                ([(x + 0.07, foot, z - 0.07), (x + 0.07, foot, z + 0.07), (x, foot - 0.3, z)], (1, -0.3, 0))):
                m.poly(pts, "iron_cart", iron, facing=facing)
        x += 0.48
    for y in (4.62, 5.12):
        w = 0.0
        while cp.arch_height(HALF, SPRING, RISE, w + 0.05) > y + 0.12 and w < HALF:
            w += 0.05
        cp.block(m, (-w, y, z - 0.07), (w, y + 0.11, z + 0.07), "wood_cart", oak, faces="zZyY")


def doors(m):
    """The oak doors, folded back against the passage walls for the day."""
    oak = (0.5, 0.48, 0.45, 1.0)
    iron = (0.55, 0.55, 0.56, 1.0)
    for s in (-1, 1):
        xa, xb = s * (HALF - 0.05), s * (HALF - 0.17)
        lo, hi = (min(xa, xb), 0.06, -1.55), (max(xa, xb), 4.7, 1.0)
        cp.block(m, lo, hi, "wood_medieval", oak, faces="xXzZY")
        face = xb - s * 0.012
        for y in (0.7, 2.3, 3.9):
            m.poly([(face, y, -1.5), (face, y, 0.75), (face, y + 0.13, 0.75), (face, y + 0.13, -1.5)], "iron_cart", iron,
                   facing=(-s, 0, 0))
        # Its planks: thin dark lines down it.
        z = -1.2
        while z < 0.95:
            m.poly([(face, 0.1, z), (face, 0.1, z + 0.025), (face, 4.66, z + 0.025), (face, 4.66, z)], "window_dark",
                   facing=(-s, 0, 0))
            z += 0.36


def tower(m, cx, turret, seed):
    cz, r, top = TOWER_Z, TOWER_R, TOWER_TOP
    tint = cp.stone_tint(0.0, top + 1.8, seed=seed)
    cp.drum(m, cx, cz, [-2.2, 2.6, top - 1.1, top - 0.5, top], [r + 0.6, r, r, r + 0.34, r + 0.34], SIDES, RUBBLE, tint)
    # Bands of tile through the rubble, and string courses of cut stone.
    tile = cp.flat_tint((0.8, 0.74, 0.7))
    for y in (3.7, 5.5, 8.4, 11.3):
        cp.drum(m, cx, cz, [y, y + 0.17], [r + 0.025, r + 0.025], SIDES, "tile_course", tile)
    for y in (6.5, 10.1):
        cp.drum(m, cx, cz, [y - 0.04, y, y + 0.18, y + 0.22], [r, r + 0.09, r + 0.09, r], SIDES, ASHLAR, cp.flat_tint(PALE))
    cp.disc(m, cx, cz, top, r + 0.3, SIDES, ASHLAR, cp.STONE_DARK)
    cp.ring_battlements(m, cx, cz, top, r + 0.34, SIDES, ASHLAR, tint, broken=(3,) if seed > 2.5 else (8,))
    # Arrow loops, looking down the road and along the wall.
    for a, y in ((-90, 4.6), (-90, 11.8), (-140, 8.0), (-40, 8.0)):
        ang = math.radians(a if cx > 0 else -180 - a)
        ang = round(ang / (math.tau / SIDES) - 0.5) * (math.tau / SIDES) + math.pi / SIDES
        rr = r * math.cos(math.pi / SIDES)
        cp.loop(m, (cx + math.cos(ang) * rr, cz + math.sin(ang) * rr), y, 1.1, (math.cos(ang), 0, math.sin(ang)), width=0.11, cross=False)
    if turret:
        tx, tz, tr, t_eave, t_point = TURRET
        tt = cp.stone_tint(0.0, t_eave, seed=seed + 4.0)
        cp.drum(m, tx, tz, [-1.0, t_eave - 0.5, t_eave - 0.25, t_eave], [tr, tr, tr + 0.14, tr + 0.14], 12, RUBBLE, tt)
        cp.cone(m, tx, tz, t_eave, t_point, tr + 0.14, 12, "roof_slates", (0.75, 0.76, 0.8), over=0.16, tile=1.2)
        for a, y, lit in ((-70, 15.6, True), (160, 12.0, False), (20, 8.5, False), (-70, 5.0, False)):
            ang = math.radians(a)
            c = (tx + math.cos(ang) * tr * 0.97, tz + math.sin(ang) * tr * 0.97)
            if lit:
                cp.lancet(m, c, y, 0.3, 0.85, (math.cos(ang), 0, math.sin(ang)), "window_candle", frame=0.1, proud=0.06)
            else:
                cp.loop(m, c, y, 0.9, (math.cos(ang), 0, math.sin(ang)), proud=0.06, cross=False)
    else:
        # The south tower's upper room, lit: whoever keeps the gate at night.
        ang = math.radians(-180 + 62)
        ang = round(ang / (math.tau / SIDES) - 0.5) * (math.tau / SIDES) + math.pi / SIDES
        rr = r * math.cos(math.pi / SIDES)
        cp.lancet(m, (cx + math.cos(ang) * rr, cz + math.sin(ang) * rr), 10.9, 0.42, 1.2, (math.cos(ang), 0, math.sin(ang)),
                  "window_candle", frame=0.12)


def prism(name, cx, cz, r, y0, y1, sides=10):
    c = porter.Mesh(name + "-colonly")
    ring = [(cx + math.cos(math.tau * i / sides) * r, cz + math.sin(math.tau * i / sides) * r) for i in range(sides)]
    for i in range(sides):
        (xa, za), (xb, zb) = ring[i], ring[(i + 1) % sides]
        c.poly([(xa, y0, za), (xb, y0, zb), (xb, y1, zb), (xa, y1, za)], ASHLAR, facing=(xa + xb - 2 * cx, 0, za + zb - 2 * cz))
    c.poly([(x, y1, z) for x, z in ring], ASHLAR, facing=(0, 1, 0))
    c.build()


def main():
    porter.reset(31)
    m = porter.Mesh("Gate")
    gate(m)
    m.build()
    t = porter.Mesh("Towers")
    tower(t, TOWER_X, True, 2.0)
    tower(t, -TOWER_X, False, 3.0)
    t.build()
    f = porter.Mesh("Fittings")
    portcullis(f)
    doors(f)
    f.build()
    x0, x1, z0, z1, top = BLOCK
    prism("TowerN", TOWER_X, TOWER_Z, TOWER_R + 0.15, -1.0, TOWER_TOP + 1.8)
    prism("TowerS", -TOWER_X, TOWER_Z, TOWER_R + 0.15, -1.0, TOWER_TOP + 1.8)
    prism("Turret", TURRET[0], TURRET[1], TURRET[2], -1.0, TURRET[3], 8)
    for name, lo, hi in (("PierN", (HALF, -1.0, z0), (x1, top + 1.0, z1)), ("PierS", (x0, -1.0, z0), (-HALF, top + 1.0, z1)),
                         ("Over", (-HALF, SPRING + RISE, z0), (HALF, top + 1.0, z1))):
        c = porter.Mesh(name + "-colonly")
        c.box(lo, hi, ASHLAR)
        c.build()
    porter.export("env_aldgate")


if __name__ == "__main__":
    main()
