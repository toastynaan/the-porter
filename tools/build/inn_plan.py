"""The Cross Keys' plan, shared by the two scripts that build it
(env_inn.py: the outside; env_inn_rooms.py: the inside), so its windows and
openings are in the same places on both sides of its walls.

Everything is in the inn's own space (game/world/street/env_inn.tscn):
the street front faces -z, the origin is on the ground at the middle of the
front, x runs along the lane (-6..6) and the house runs back to z = 10. The
scene's hidden Blocks are its collision and are not to be moved: walls 0.3 m
thick inside the box below, floors at 0, 3 and 6 m.

Who builds what:
- The inside (env_inn_rooms.py) builds everything seen from within, out to
  the walls' inner faces (`INNER`): floors, ceilings, the inner faces with
  a recess for every window in `WINDOWS`, stairs, hearth, counter.
- The outside (env_inn.py) builds everything from the inner faces outward:
  the walls' thickness at the two real openings (the reveals of `DOOR` and
  `PORTER_WINDOW`), the frame, the jetties, the windows' panes as the
  street sees them, the roof.
"""

# The box: outer faces of the ground floor's walls.
X0, X1 = -6.0, 6.0
Z0, Z1 = 0.0, 10.0
WALL = 0.3
# The walls' inner faces: (x0, x1, z0, z1).
INNER = (X0 + WALL, X1 - WALL, Z0 + WALL, Z1 - WALL)

# Floors: the top of each storey's floor, and its ceiling (the underside of
# the slab above). The roof space over the top storey is not entered.
FLOORS = (0.0, 3.0, 6.0)
CEILINGS = (2.8, 5.8, 8.6)
EAVES = 8.8
# The roof: a gable to the street, its ridge running back along z.
RIDGE = 12.0

# The two openings that are really open (collision has a hole there).
# The street door: (x0, x1, y0, y1) in the front wall.
DOOR = (-0.6, 0.6, 0.0, 2.3)
# The porter's window at the top front right, which he looks out of toward
# the abbey gate (night 0): (x0, x1, y0, y1) in the front wall. Nothing may
# narrow the view through it: the outside's opening must be wider than this
# and splayed, however deep the wall is drawn there.
PORTER_WINDOW = (3.6, 4.4, 7.0, 7.9)
# Where he stands to look out (the scene's `TopWindow` marker).
PORTER_STANDS = (4.0, 6.0, 0.9)

# The stairs' wells, which the inside keeps open: (x0, x1, z0, z1).
STAIR_UP_1 = (-5.7, -4.5, 4.0, 8.6)    # ground floor to the first
STAIR_UP_2 = (-4.5, -3.3, 4.0, 8.6)    # first floor to the second
# The porter's room on the second floor: (x0, x1, z0, z1), its door in its
# back wall at x 2.5..3.5.
PORTER_ROOM = (1.5, 5.7, 0.3, 4.5)

# Windows that are not open: glazed, never seen through. Outside, each is a
# pane object of its own named as below (the scene lights the ones in its
# `lit_windows`; curfew puts them out). Inside, each is a shallow recess
# with a frame and dark glass in the same place.
# (name, wall, along, sill, width, height): `wall` is "front" (z = 0),
# "left" (x = -6) or "right" (x = 6); `along` is the window's middle, x on
# the front wall and z on a side wall; `sill` is its foot's height.
WINDOWS = (
    ("Window0_0", "front", -3.2, 0.95, 2.2, 1.35),
    ("Window0_1", "front", 3.2, 0.95, 2.2, 1.35),
    ("Window1_0", "front", -3.5, 3.85, 1.9, 1.3),
    ("Window1_1", "front", 0.0, 3.85, 1.9, 1.3),
    ("Window1_2", "front", 3.5, 3.85, 1.9, 1.3),
    ("Window2_0", "front", -2.4, 6.95, 1.6, 1.1),
    ("WindowLeft0_0", "left", 2.2, 1.0, 1.5, 1.2),
    ("WindowLeft1_0", "left", 2.2, 3.9, 1.5, 1.2),
    ("WindowRight0_0", "right", 2.6, 1.0, 1.5, 1.2),
    ("WindowRight1_0", "right", 5.0, 3.9, 1.5, 1.2),
)
# The outside may add panes that have no inside (a gable window into the
# roof space), named Window3_<n>.
