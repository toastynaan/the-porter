"""The fields outside Aldgate (night 0, the road in): the ground from the far
west to the foot of the city wall, in the road scene's own coordinates
(game/world/road/env_road.tscn; the road runs along x at z = 47).

- The road: two carts wide, flat (the wagon rides it at y = 0), with a
  grass verge and a wet ditch on each side.
- Open fields in ridge and furrow, the medieval plough's long parallel
  ridges, running away from the road to north and south. Rain stands in the
  furrows.
- A low rise on the south side for the white chapel and its yard.

The ground's shader (game/world/materials/real/ground_fields.gdshader) reads
each vertex's colour as masks: red the road's mud, green grass, blue
ploughed soil (the rest is stubble), and alpha standing water. UV is (metres
along the road, metres to the side of its middle), for the wheel ruts.

Run: tools/build.sh env_road_fields
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
from porter import fbm, lerp, smoothstep

ROAD_Z = 47.0
# The road's half width, and where the verge, ditch and field begin, m from its middle.
ROAD_HALF = 3.0
VERGE = 4.3
DITCH = 5.5
DITCH_HALF = 0.95
DITCH_DEPTH = 0.62
BANK = 7.2
# Ridge and furrow: metres from ridge to ridge, and half their height.
RIDGE = 7.5
RIDGE_HIGH = 0.24
# The chapel's yard: its middle and half size (the chapel stands at -184, 64.5;
# tools/build/env_white_chapel.py has the yard's wall on these lines).
YARD = (-186.0, 66.0)
YARD_HALF = (19.0, 10.0)
# The yard is level, at this height (the chapel's floor).
YARD_LEVEL = 0.95
# The wall's outer face, where the ground ends.
WALL_X = -119.5
WEST_X = -372.0


def yard_amount(x, z):
    """1 inside the churchyard, falling to 0 over a few metres outside it."""
    dx = max(abs(x - YARD[0]) - YARD_HALF[0], 0.0)
    dz = max(abs(z - YARD[1]) - YARD_HALF[1], 0.0)
    return 1.0 - smoothstep(0.0, 4.0, math.hypot(dx, dz))


def ground(x, z):
    """Height, and the masks (road, grass, soil, water), at a point."""
    d = abs(z - ROAD_Z)
    south = z > ROAD_Z
    # The lie of the land: slow swells, a little higher to the south.
    land = 0.35 + 0.55 * fbm(x, z, 0.012, 3, 1.0) + (0.25 if south else 0.0) * smoothstep(BANK, 30.0, d)
    yard = yard_amount(x, z)
    # Ridge and furrow, in furlongs: each block of strips has its own spacing
    # and lies a little askew of the next. A headland runs along the road.
    furlong = math.floor((x + 400.0) / 62.0)
    spacing = RIDGE * (0.9 + 0.25 * ((furlong * 7919) % 5) / 4.0)
    skew = 0.12 * (((furlong * 104729) % 7) / 3.0 - 1.0)
    phase = math.cos((x + z * skew) * math.tau / spacing)
    edge = min((x + 400.0) % 62.0, 62.0 - (x + 400.0) % 62.0)
    strips = smoothstep(BANK + 2.0, BANK + 9.0, d) * smoothstep(0.0, 3.0, edge) * (1.0 - yard)
    # Some furlongs lie fallow, under grass: their ridges are softer.
    fallow = ((furlong * 31) % 3) == 1
    ridge = phase * RIDGE_HIGH * strips * (0.6 if fallow else 1.0)
    h = land + ridge
    h = lerp(h, YARD_LEVEL, yard)
    # The road and its ditches cut into it.
    field_mix = smoothstep(DITCH + DITCH_HALF, BANK + 1.5, d)
    verge_h = 0.14 + 0.05 * fbm(x, z, 0.3, 2, 2.0)
    h = lerp(verge_h, h, field_mix)
    ditch = 1.0 - smoothstep(0.0, DITCH_HALF, abs(d - DITCH))
    h -= DITCH_DEPTH * ditch * ditch * (3.0 - 2.0 * ditch) * (0.8 + 0.2 * fbm(x, z, 0.08, 2, 3.0))
    road_mix = 1.0 - smoothstep(ROAD_HALF, VERGE, d)
    camber = 0.03 * (1.0 - (d / ROAD_HALF) ** 2) if d < ROAD_HALF else 0.0
    h = lerp(h, camber + 0.012 * fbm(x, z, 0.6, 2, 4.0) * (1.0 if d > 1.0 else 0.3), road_mix)

    # Masks.
    road = 1.0 - smoothstep(ROAD_HALF - 0.3, ROAD_HALF + 0.9, d + 0.35 * fbm(x, z, 0.5, 2, 5.0))
    ploughed = strips * (0.0 if fallow else 1.0) * smoothstep(-0.2, 0.3, fbm(x, z, 0.02, 2, 6.0) + 0.45)
    stubble = strips * (1.0 if fallow else 0.0) * 0.8
    grass = max(1.0 - road - ploughed - stubble, 0.0)
    # Water: the ditch's bottom, and broken pools down the furrows.
    water = smoothstep(0.55, 0.95, ditch)
    pools = smoothstep(0.5, 0.9, -phase) * strips * smoothstep(-0.45, 0.1, fbm(x, z, 0.035, 2, 7.0))
    water = max(water, pools * (0.55 if fallow else 1.0))
    return h, (road, grass, ploughed, water)


def lines(start, stop, step):
    out = []
    v = start
    while v < stop - 1e-6:
        out.append(v)
        v += step
    out.append(stop)
    return out


def main():
    porter.reset()
    xs = lines(WEST_X, -300.0, 4.0)[:-1] + lines(-300.0, WALL_X, 1.0)
    north = [-90.0, -70.0, -54.0, -42.0, -32.0, -24.0, -17.0, -11.0, -6.0, -2.0, 1.0, 4.0, 7.0, 10.0, 13.0, 16.0, 19.0,
             22.0, 25.0, 28.0, 30.5, 33.0, 35.0, 36.5, 38.0]
    near = lines(39.2, 54.8, 0.6)
    south = [56.0, 57.5, 59.0, 61.0, 63.0, 65.0, 67.0, 69.0, 71.0, 73.0, 75.0, 77.5, 80.0, 83.0, 86.5, 90.0, 94.0, 99.0,
             105.0, 112.0, 120.0, 130.0, 142.0, 156.0, 172.0, 190.0]
    zs = north + near + south
    m = porter.Mesh("Fields")
    index = {}
    for i, x in enumerate(xs):
        for j, z in enumerate(zs):
            h, mask = ground(x, z)
            index[(i, j)] = m.vert(x, h, z, mask, (x, z - ROAD_Z))
    for i in range(len(xs) - 1):
        for j in range(len(zs) - 1):
            m.face((index[(i, j)], index[(i, j + 1)], index[(i + 1, j + 1)], index[(i + 1, j)]), "ground_fields")
    m.build(smooth=True)
    # What the wagon and anything else stands on: the road's level.
    c = porter.Mesh("Ground-colonly")
    c.quad((WEST_X, 0.0, -90.0), (WEST_X, 0.0, 190.0), (WALL_X, 0.0, 190.0), (WALL_X, 0.0, -90.0), "ground_fields")
    c.build()
    porter.export("env_road_fields")


if __name__ == "__main__":
    main()
