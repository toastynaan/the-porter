# Abbey layout (greybox)

The abbey is one walled square, 80 × 80 m, on a 4 m kit grid. Every building opens off the cloister, and every area is within a minute's walk of the garth (the farthest, the west end of the mill race, is 59 s at 1.4 m/s). This drawing stands in for the design doc's missing map.

![Abbey layout](abbey-layout.png)

## Areas

| Area | Where | What's in it | Hiding spots |
| --- | --- | --- | --- |
| Outer court | West strip | Gate (west wall: an iron grille under a stone porch; open by day with Cole at it, barred once the porter takes it after supper), the porter's bench beside it, porter's cell, guesthouse, well, woodpile | Under the cot, behind the woodpile |
| Church | North | Bell tower (west end, 12 m), nave, choir, altar (east end); crypt under the choir | Under the altar cloth, the open tomb |
| Cloister | Centre | Garth (24 m square with walks) inside arcades, a garden in it with a basin at the middle; one open bay a side | Behind the piers |
| Dormitory (east range) | East of the cloister | Slype, chapter house, day stair, warming room, undercroft; dormitory upstairs; latrine block at the south end | Under three of the beds (north end, middle, south end) |
| South range | South of the cloister | Refectory, kitchen, bakehouse with the oven | The oven (bones inside) |
| Cellar (west range) | West of the cloister | Granary (hidden stair), outer parlour passage, stores (cloister door locked) | Grain sacks |
| Graveyard and infirmary | East and south-east | Graves, two yews, charnel house, infirmary, mill, mill race, fishpond | In the bone pile, under a sick bed in the infirmary |
| Gardens | South, beyond the mill race | The orchard (12 apple trees) on the west side, the kitchen beds on the east | None |

## The lane outside the gate

`areas/street.tscn`, outside the west wall, baked into the navmesh (its `Ground`, `Houses` and `GatePorch` nodes are in `nav_source`) so visitors can walk up it and in through the gate. A 6 m lane runs the length of the wall with a gutter down the middle. On its far side is a row of timber houses: gable ends to the lane, upper floors jutting 0.5 m per storey, lit and dark windows, a lantern outside each (`StreetLanterns`). The inn stands opposite the gate. Two alleys end out of sight. At each end the lane turns west into fog. The gate porch holds a lantern over the grille. Three squints, barred slits at eye level, look through the wall between lane and abbey: from the porter's cell (z −6) and from the outer court north and south of the gate (z 6 and 14) (`game/world/kit/wall_squint.tscn`; `docs/prologue.md`). The inn, the Cross Keys, can be entered: a taproom, stairs to a loft of beds, and the porter's room at the top front right with one window over the wall toward the court (`game/world/street/env_inn.tscn`). Before the lane, night 0's road comes in from the west (`game/world/road/env_road.tscn`: fields, the white chapel, the city wall and Aldgate, close houses), far outside the abbey's square. The porch's flagstone apron runs on under the gateway into the court, so the threshold is floor and the navmesh joins the lane to the court (until M6 it stopped at the wall, and visitors couldn't path through). Beyond are rooftops and spires (`Skyline`: meshes only, no collision or shadows; it keeps inside the city wall the road in passes through at x = -118, and clear of that road). Debug key G steps out into the lane and back. `tools/street_shots.sh` renders it.

## The cloister as built (first look, 2026-11-11)

The greybox plan is unchanged and is still what stops people and what the navmesh is baked from; it is hidden (`Walls` not visible, the walks' floor and roof blocks `shown = false`) under two models from `tools/build/env_cloister.py`:

- **`Stonework`** (`env_cloister_arcade`): each bay a pointed arch in two orders on piers with a buttress to the garth; closed bays stand on the 0.6 m wall and hold tracery (two cusped lights and a quatrefoil); the open bay on each side is clear, with a worn step. A rib vault over every bay of the walks and the four corners: it springs at 2.7 m and is 4.55 m at the crown (the greybox roof was at 3.9 m). The ranges' walls as the walks see them, with a stone surround to every door and window the greybox has. Flags on the floor, a lead roof behind a parapet (the arcade wall is 5 m).
- **`Garden`** (`env_cloister_garth`): a gravel walk round the garth and two across it, a paved round at the middle with an eight-sided conduit basin (still water, a shaft and bowl), and four beds edged in clipped box: herbs in a knot with a yew (north-west), a lawn with a bare hawthorn (north-east), late flowers with a yew (south-east), a lawn (south-west).
- **`GardenSolids`** (in `nav_source`, not drawn): the basin, the two yews, the hawthorn's trunk and the twelve buttresses. The box edging isn't solid: it is stepped through. The navmesh was rebaked.
- The `Cloister` marker moved from the garth's middle, where the basin now stands, to (0, 0, -13) on the south walk of the garden.

Still greybox and seen from the garth: the east range's upper walls and the ranges' roofs. `tools/cloister_shots.sh` renders it.

## The church as built (first look, 2026-11-11)

The greybox plan is unchanged and is still what stops people and what the navmesh is baked from (no solid was added, so the navmesh is the cloister's bake). Its walls, floors and roofs above ground are hidden (each wall piece not visible, the floor and roof blocks `shown = false`) under one model, `Stonework` (`env_church`, `tools/build/env_church.py`). The crypt is still greybox.

- **Height.** The nave and choir are one vessel, 48 m by 7.2 m inside and 16 m to the vault's crown (the greybox ceiling was at 8). The vault springs at 11.2 m from triple shafts that stand on the floor at every bay. The walls run to 17.2 m outside, with a lead roof behind the parapet (ridge 21.8 m). The `NaveRoof` block moved up to 17.2 m.
- **Walls inside.** Twelve bays of 4 m. A blind arcade along the foot (not in the bays with a door or the night stairs), a string course at 5 m, and above it a two-light traceried window in every bay, sill at 5.6 m and head at 13.4 m. Where the east range stands against the south wall (x over 12) the windows are short and high (sill 9.4 m). The east wall has one window of four lights over the altar; the west wall a blind arch over the tower door.
- **Windows.** Leaded glass that gives off a faint cold light, with iron saddle bars. They are drawn only: the greybox's small window holes are what hunters see through.
- **Floor.** Worn flags in the nave; tiles of two colours in the choir, east of the rood beam at x = 8. The crypt stair's well is open as before.
- **Fittings (drawn only, all above head height).** A rood beam with a cross at 6.6 m; three iron coronas hung at 5.2 m, their candles unlit. No light was added: the sanctuary lamp is still the church's only one.
- **Tower.** The bell room is skinned to its timber ceiling at 12 m. Outside the tower rises to 30 m: buttresses, a louvred belfry stage, battlements and a short lead spire. Nothing above 12 m can be entered.
- **Outside.** Buttresses between the bays on the north and east; on the south they start above the cloister and the ranges. The south wall's outer face starts above the cloister's roof (4.8 m) and above the east range (8.6 m).
- The night stairs, their landing and the crypt stair keep their greybox shapes and take the flags' material.

Still greybox: the stalls, altar, tomb, bell and doors (props). `tools/church_shots.sh` renders it; stills marked `lit` use a lamp the game doesn't have, to judge the stonework.

## Under the abbey as built (first look, 2026-11-11)

The crypt, the passage under the nave and the foot of the hidden stair are one model, `Undercroft` in `church.tscn` (`env_crypt`, `tools/build/env_crypt.py`), laid over the greybox of `church.tscn` and `cellar.tscn`. Their greybox walls and floors are hidden and keep the collision. Floors are at -4 m; nothing is higher than the floors overhead, 3.7 m up.

- **Crypt.** A vessel 15.2 m by 5.5 m under four low groin vaults with heavy ribs (crown 3.5 m), on stub columns against the walls. A tomb recess in each bay of the south wall and a niche in the east wall behind the reliquary, all cut into the walls' thickness.
- **The crypt stair's wall (new, solid).** The stair from the choir used to stand open to the crypt along its south side. It now comes down in its own well behind a wall (`CryptSolids` in `church.tscn`): x = 12.4 to 27.6 at z = -34.05, with an arch at each end. The east arch is the way from the stair's foot into the crypt; the west arch opens on a dead-end alcove 3.8 m long.
- **Passage.** A round tunnel vault 32 m long and 3.4 m high, with an arch on pilasters every 4 m, rubble walls and a doorway into the crypt.
- **Under the granary (new, solid).** The passage turns south under a groin vault and runs 3.4 m to the foot of the hidden stair. The stair climbs in its own well; the dead space east of it (1.8 m by 8.6 m, which led nowhere) is closed by a wall with a walled-up arch (`PassageSolids` in `cellar.tscn`).
- **Fittings (drawn only).** Nine iron brackets with burnt-out torches. No light was added: it is as dark down there as before.
- The navmesh was rebaked for the new walls. Routes and distances are unchanged: both walls only close off drops and dead ends.
- The model has a lid over the vaults, never seen, so the sun and moon don't light what is under them.

`tools/crypt_shots.sh` renders it; stills marked `torches` light the brackets and those marked `lit` use a plain lamp, neither of which the game has.

## The ranges as built (first look, 2026-11-11)

The east, south and west ranges are one model, `Ranges` in `dormitory.tscn` (`env_ranges`, `tools/build/env_ranges.py`), laid over the greybox of `dormitory.tscn`, `south_range.tscn` and `cellar.tscn`. Their walls, floors and roofs are hidden and keep the collision. No solid was added and the navmesh is unchanged.

The build script reads the wall pieces from the three scenes: each plain, door or window piece gets a face on both sides, with a surround to each opening. **After moving, adding or changing a wall piece in one of those scenes, run `tools/build.sh env_ranges`.** The windows stay open holes, since the porter and the hunters see through them.

- **Heights.** A room with nothing over it is open to its roof: the refectory, kitchen, bakehouse, granary, parlour and stores are 4 m to the wall top and 8 m to the ridge; the dormitory, on the upper floor, is 4 m to the wall top and 8 m to the ridge (12 m above ground). Each has boards, rafters, purlins and a truss every 4 m; the refectory's and dormitory's trusses have curved braces.
- **Under the dormitory** (its floor is at 3.72 m): the slype is a tunnel vault; the chapter house has two ribbed bays; the warming room two groined bays; the undercroft four. The stair hall and the latrine's ground floor have boarded ceilings.
- **Walls.** Outside, the cloister's stone. Inside, plaster in the refectory, dormitory, stair hall and parlour; cut stone in the slype, chapter house and warming room; rubble in the undercroft, kitchen, bakehouse, granary, stores and latrines.
- **Floors.** Two-coloured tiles in the refectory and chapter house; flags in the other ground-floor rooms; boards in the dormitory.
- **Roofs.** Clay tile, with a chimney stack over the kitchen hearth, the warming room's hearth and the oven.
- **Fittings (drawn only).** Refectory: oak panelling to 1.5 m, paned cloth hangings. Dormitory: hangings between the windows, a rush runner down the middle. Day stair: a red runner with a gold edge, a hanging on the hall's wall. Chapter house: a blind arcade and a painted panel of three saints. Eight iron brackets with burnt-out torches. No light was added.

Still greybox: every prop (beds, tables, benches, hearths, oven, barrels, doors). `tools/ranges_shots.sh` renders it.

## The precinct as built (first look, 2026-11-11)

Everything outside the church and the ranges is one model, `Precinct` in `outer_court.tscn` (`env_precinct`, `tools/build/env_precinct.py`): the precinct wall, the ground, and the five buildings that stand apart (porter's cell, guesthouse, charnel house, infirmary, mill). The greybox walls, ground blocks, floors and roofs of `abbey.tscn` (`Grounds`), `outer_court.tscn` and `graveyard_infirmary.tscn` are hidden and keep the collision. No solid was added and the navmesh is unchanged.

The build reads the wall pieces and the ground blocks from those scenes, as the ranges' does. **After moving a wall piece or a ground block, run `tools/build.sh env_precinct`.**

- **Precinct wall.** Rubble inside, with its squints and an arch over the gate; its lane face is the lane's own model. The north, east and south outer faces are made too.
- **Buildings.** Each is open to a timber roof under clay tiles, 8 m to the ridge. Plaster inside the cell, guesthouse and infirmary; rubble in the charnel house and mill. Flags underfoot, earth in the charnel house. A chimney stack on the guesthouse and the infirmary.
- **Ground.** Trodden earth in the outer court, with a flagged path from the gate east, then north past the cell to the parlour door. Gravel between the south range and the mill race. Grass in the graveyard, round the infirmary and under the orchard. Tilled rows in the kitchen garden.
- **Water.** The mill race and the fishpond keep their greybox blocks, with the still-water material and flags on their beds and kerbs.

Still greybox: every prop (graves, yews, well, woodpile, beds, the mill wheel, garden beds, the gate's grille and bar, doors).

**How the walls keep the light out** (ranges and precinct): faces are one-sided, so each wall has an unseen core down its middle, each roof overhangs its walls and gables by 0.5 m, and the inside gables follow the roof's slope. Without these the moon lit streaks across the rooms.

`tools/precinct_shots.sh` renders it.

## The dressing pass (2026-11-11)

One pass over all five areas after their first looks, to close gaps and make the place uneasy. The direction is in the Look and Feel ("How the abbey unsettles"). The shared pieces are in `tools/build/dress.py`; each area's build script places its own. Nothing here has collision except the buttress feet, and no light was added.

**Hooded stone figures.** Faceless under the hood, hands in their sleeves. Each stands where a view ends or beside a way the porter must take.
- Cloister: in a niche at the west end of the north walk; in a niche at the south end of the east walk, turned to the wall with a web across it; two on the west and south parapets against the sky.
- Church: on a corbel beside the night stairs' upper door; in a niche over the graveyard door; on the rood beam, two attendants beside a figure on the cross; in the niche north of the east window (the south niche is empty).
- Under the abbey: in a niche at the passage's west end, closing its 32 m view; in a niche facing the foot of the crypt's stair.
- Ranges: in a niche at the head of the day stair; a bowed reader in a niche over the refectory's tables.
- Precinct: in the precinct wall beside the porter's cell door, seen first from the gate; in the north wall at the end of the grave aisle; in the east wall facing the top of the mill race's east steps.

**Bones.** Seven ossuary niches in the passage under the nave (five with bones, two empty). Bones behind iron bars in the charnel house's wall, and a skull and crossed bones in its door head. A skull on a bracket over the chapter house door.

**Tombs.** A wall tomb with an effigy and weepers in the church's north wall (bay x = -10). Effigies on two of the crypt's four tombs; a third tomb's lid is swung askew.

**Walled-up openings.** A doorway at the south end of the cloister's west walk; a postern in the precinct's north wall behind the church (x = 2); a door in the undercroft's east wall; the arch by the hidden stair's foot (first look), now with a small cross scratched into its blocking 46 times.

**One wrong thing a room.** The turned figure in the cloister. The church's middle corona hanging low and crooked on three chains. Crosses scratched in the bell room, by the parlour's stores door, by the last guesthouse bed. A dormitory hanging down at one end. Fallen plaster and a crack in the stair hall.

**Neglect, everywhere.** Soot over every torch bracket and rust under it. Runs under sills. Green damp at outdoor and underground wall feet. Cracks, cobwebs, fallen leaves in corners, grave slabs in the cloister's east walk and the church floor, a broken tracery cusp, four broken panes in the church. Moss, a sagging ridge and slipped tiles on the charnel house. Cart ruts and puddles in the outer court. Ten crows on ridges and wall tops. The garden's herb and flower beds are bare earth and dead stalks.

**Gaps closed.**
- Church: the south wall's outer face east of the dormitory (x = 20.4 to 28.4) was missing from the ground to 8.6 m; it is built, with a surround to the graveyard door, tall windows in bays 22 and 26, and buttresses from the ground. Over the ranges, the south wall's outer face now starts on each roof's line, and the windows there are shorter (sill at 8 m over the west range, 12 m over the dormitory). Thresholds in all five ground-floor doorways.
- Cloister: every door and window in the walks' back walls has its reveal on the cloister side.
- Under the abbey: the slots beside both stairs, the soffits under the church's and granary's floor edges, the floors of the tomb recesses.
- Ranges and precinct: every wall with nothing above it has a top; the three partitions under open roofs (z = -16, -12, 4) run up to the roof; a board shuts the wedge between each wall head and the roof boards; the day stair's and hidden stair's holes have rims; the latrine's floor edge is closed. The west range's and refectory's roofs no longer overhang into the cloister walks (`roof()` in `env_ranges.py` takes an overhang per eave and per end). The build prints an audit of every wall piece.
- Precinct: the gate's reveal runs through the whole wall and its head is square; flags at its threshold; rough grass beyond the north, east and south walls.

**Solids added.** `ChurchButtresses` in `church.tscn` (in `nav_source`, not drawn): 22 blocks under the feet of the church's and tower's ground-level buttresses, 2.6 m high. The navmesh was rebaked.

**For the props pass** (found here, not done): the warming room's hearth sits under a vault springer at z = -8 and should move to a bay centre before it gets a hood; an abbot's seat and a reader's pulpit front; a churchyard cross on steps near (27, -30); the gate's north leaf swings into the porter's cell; the lane-side half of the gate's apron is a plain block.

## Routes

| Route | From → to | Notes |
| --- | --- | --- |
| Night stairs | Dormitory (upper floor, north end) → choir | 22.5 m from the choir to the dormitory's north end |
| Day stair | Cloister east walk → dormitory | 1.6 m wide (widened in M5 so the porter doesn't catch on the floor above) |
| Crypt stair | Choir (north side) → crypt | |
| Hidden stair | Plank closet in the granary → passage under the nave → crypt | The closet door looks like the planks. Hunters use it: 31 m from the granary to the passage |
| Latrine chute | Latrine seat (upper floor) → mill race | Porter only, one way. A hunter goes round: 116 m |
| Under the mill wheel | Mill race west ↔ east of the wheel | Porter only (0.6 m gap). A hunter goes round: 82 m |
| Mill race | Steps at both ends | 1.2 m deep, can't be climbed out of except at the steps |

The porter's keys (design doc, "Tools") lock the guesthouse door and the charnel house door (R, from either side, when shut). A locked door keeps a hunter out. The gate is barred and has no key in the greybox.

Other markers: `WakePoint` in the infirmary (where the first capture wakes you), `BellSpawns/start` by the gate (where a restart from the start bell puts you), and `StalkPoints` in every area (where the demon may stand).

## Dimensions used

Walls 4 × 4 × 0.8 m; doorways 0.9 × 2.0 m; the gate 3.0 × 3.4 m; the church and the east range two pieces high (8 m) and the tower three (12 m) as collision (the church as drawn is 16 m inside and the tower 30 m outside); upper floors at 4 m; the crypt and passage 4 m below ground. Stairs climb 4 m over 6 m.

## Editing

- Each area is a scene in `game/world/abbey/areas/`, built from the kit pieces in `game/world/kit/` (`wall`, `wall_door`, `wall_window`, `wall_arch`, `wall_arch_open`, `wall_gate`, `corner`), `Block`s you resize in the inspector (floors, roofs, stairs, hearths), and props: one scene per kind of thing in `game/world/props/` (beds, benches, graves, trees). `abbey.tscn` puts them together. The lane's houses are one scene per house type in `game/world/street/`. `docs/assets.md` lists every placeholder and how to replace it with a model.
- To add a prop, instance its scene under the area's `Props` node (it's in `nav_source`, so it shapes the navmesh).
- The gate bar is on the door layer, like door leaves: it blocks you but stays out of the navmesh, so the gateway is walkable when the gate is open.
- Doors are `game/world/door/door.tscn`. Turn one 180° to swing it the other way. Set `locked`, give it a `key` the porter holds, or give it the wall's material to hide it.
- A hiding spot is an Area3D with `game/hiding/hiding_spot.gd` and Marker3D children `View` (the camera while hidden), `Exit` and `Check` (where a hunter stands). Set its box `size`, `noise` and `check_chance` in the inspector. See `docs/hunting.md`.
- Stalk points are plain Marker3Ds in the `stalk_point` group.
- After moving walls, floors, stairs or props, rebake the navmesh with `tools/bake_nav.sh` (or the Navigation node's Bake button), then run `tools/check.sh`. The walk test sends the porter through every area, so it catches a doorway or stair that no longer works.
- `tools/topdown.sh` renders the plan view with the navmesh, and `tools/abbey_shots.sh` renders in-game views.
