# Placeholder assets (M7)

Everything in the world is a placeholder: boxes, cylinders and the greybox figure, in the shared materials. Each kind of thing lives in one scene, so a real model replaces it in one place and every copy in the world changes with it. Swap them in any order.

## How the world is put together

| Layer | What | Where | To replace it |
| --- | --- | --- | --- |
| Kit | Walls, arches, doorways, windows, corners and the gate wall, on the 4 m grid | `game/world/kit/` | Open the kit piece and swap its mesh; every wall made from it changes |
| Doors | Door leaves, including the gate's grille | `game/world/door/door.tscn` | Same |
| Surfaces | Floors, roofs, stairs, rails, hearths, water: sized `Block`s | `game/world/materials/*.tres` | Replace the material (a tiling texture); every surface that uses it changes |
| Props | One scene per kind of thing | `game/world/props/prop_*.tscn` | Open the scene, replace its `Block` children with the model and its collision |
| Houses | One scene per house type in the lane | `game/world/street/env_*.tscn` | Same; keep the `Window*` and `Door*` node names, which `lit_windows` uses |
| Characters | One scene per person | `game/characters/chr_*.tscn` | Replace `Figure` (and the prop) with the model; keep the `Face` marker |

**Rules for every placeholder scene**
- The origin is on the floor at the middle of the footprint, and the front faces -Z. The scene's `editor_description` says what the thing is, its size and which way it faces.
- Names follow the Look and Feel's asset pipeline: `env_` for buildings, `prop_` for props, `chr_` for characters.
- The root is in the `placeholder` group, so a tool can list what is left to replace.
- A placeholder's `Block`s are its collision. A model brings its own (meshes with Godot's `-colonly` suffix, or a StaticBody3D). Keep solid what was solid: the hunters' paths and the hiding spots depend on it.
- After changing anything solid, rebake the navmesh (`tools/bake_nav.sh`) and run `tools/check.sh`. The walk test goes through every area, including the gardens.

## Props

| Scene | What | Where it's used |
| --- | --- | --- |
| `prop_bed` | A straw bed, 0.9 × 2 m, 0.45 m high, head at -Z | Guesthouse (6), dormitory (19), infirmary (3) |
| `prop_bed_raised` | A bed on legs you can hide under | Dormitory (3, the hiding spots), infirmary (1, a hiding spot) |
| `prop_cot` | The porter's cot, planks on legs, with room under it | Porter's cell |
| `prop_desk` | Writing desk, 1.2 × 0.6 m | Porter's cell |
| `prop_ledger` | The gate ledger, lying shut | On the desk |
| `prop_stool` | Three-legged stool | Guesthouse, dormitory |
| `prop_bench` | Plank bench, 2 m, sat on facing -Z | Refectory (32), chapter house (3), by the gate |
| `prop_table` | Trestle table, 2 × 0.9 m | Refectory (16), kitchen, infirmary (herbs) |
| `prop_gate_bar` | The oak bar across the gate, on the door layer | The gate |
| `prop_well` | The court well | Outer court |
| `prop_woodpile` | A 2 m stack of split logs | Outer court (3, a hiding spot behind them) |
| `prop_grain_sacks` | A heap of rye sacks | Granary (4, a hiding spot) |
| `prop_barrel` | Ale barrel | Stores (3) |
| `prop_shelves` | Storeroom shelves, 3 m | Stores |
| `prop_choir_stalls` | A 4 m run of stalls | Choir (2 a side) |
| `prop_altar` | High altar with its cloth to the floor | Church (a hiding spot under it) |
| `prop_tomb_open` | Tomb chest with its lid pushed aside | Nave (a hiding spot) |
| `prop_reliquary` | The shrine with the relic | Crypt |
| `prop_bell`, `prop_bell_rope` | The bell, and its rope down to the tower floor | Bell tower |
| `prop_oven` | The bakehouse oven, big enough to crawl into | Bakehouse (a hiding spot) |
| `prop_oven_bones` | Bones in the oven ash (body 3) | In the oven |
| `prop_charnel_bones` | Bones stacked under a row of skulls, with a gap to hide in | Charnel house |
| `prop_grave` | A grave mound, head to the west | Graveyard (30) |
| `prop_mortar` | Thomas's stone mortar | Infirmary |
| `prop_millstone`, `prop_mill_wheel` | The mill | Mill, mill race |
| `prop_tree_apple` | A bare apple tree, about 4 m; only the trunk is solid | Gardens, the orchard (12) |
| `prop_tree_yew` | An old churchyard yew, about 6 m; only the trunk is solid | Graveyard (2) |
| `prop_garden_bed` | A dug vegetable bed, 1.2 × 4 m, walked over | Gardens, the kitchen beds (12) |
| `prop_carved_saint` | A carved saint on a plinth, 1.8 m, stone; its head turns at Dose 50+ (`Carving`) | Cloister (4), nave, choir |
| `prop_sand_patch` | Fresh sand raked over the ground, about 3 m across, a decal | By the well on day 1 |
| `road/prop_wagon` | The carter's open cart and horse, with seats at the back for the porter and the traveller and one for the carter | Night 0's ride |
| `road/prop_body_cart` | A cart with a body under sacking | Night 0's ride, the hook |
| `prop_cult_masks` | The cult's masks and habits on their pegs | The crypt passage, night 6 (proof: a costume) |
| `prop_hoof_soles` | Carved hoof soles on straps, a pair | The crypt passage, night 6 (proof: a costume) |
| `prop_purse_chest` | An iron-bound chest of pilgrims' purses | The crypt passage, night 6 (proof: a purse) |
| `prop_relic_hand` | The silver hand with the relic: a pig's knuckle | The crypt, night 6 (proof: the relic) |
| `prop_cult_book` | The cult's book open on its stand | By the crypt's ring, night 6 (proof: the book; take it and the rite stops) |
| `prop_blood_pool`, `prop_blood_spray`, `prop_drag_marks`, `prop_blood_print` | Blood (old blood, #5A1A14), as decals: a pool on the floor, a spray up a wall, drag marks, a boot print | Wherever a death leaves them (`BloodMarks`, `docs/death.md`) |

`candle.tscn` and `lamp.tscn` in the same folder are lights with scripts, already one scene each. The crypt's ring of twelve rite candles (`RiteCandles` in `night_base.tscn`) is twelve `candle.tscn`.

Windfall apples (`Windfalls` in `night_base.tscn`) are small spheres under a `Pickup`; the false door, the self-lit candle and the hallucinations build their own pieces in code (`docs/drug.md`), and so do night 6's flames (`Fire`). The Hungry Saint is `chr_saint` worn by `HungrySaint` (`game/saint/`).

**Still built in place** (part of a building, or one of a kind): the kitchen and warming-room hearths, the latrine seat, the plank closet over the hidden stair, the crypt rails, the water in the mill race and fishpond, the bends at each end of the lane, and the skyline.

## The lane's houses

| Scene | What | Houses |
| --- | --- | --- |
| `env_house_3storey_narrow` | Three storeys, 5 m along the lane | 7 |
| `env_house_3storey_wide` | Three storeys, 6 m along the lane | 2 |
| `env_house_2storey_narrow` | Two storeys, 5 m | 1 |
| `env_house_2storey_wide` | Two storeys, 6 m | 4 |
| `env_inn` | The Cross Keys opposite the gate, with its sign: three storeys you can enter (taproom, loft of beds, the porter's room at the top with its window toward the abbey), its door, fire and candles | 1 |

Night 0's road is `game/world/road/env_road.tscn` (fields, the white chapel, the city wall and Aldgate, close houses, and the `RidePath` the wagon follows). The squints are `game/world/kit/wall_squint.tscn`, a 4 m wall module with the barred slit.

Each house in `street.tscn` lists its lit windows in `lit_windows` (lit windows show who is awake). The street lanterns are `lamp.tscn`.

## Characters

Each person is one scene in `game/characters/`: the greybox `Figure` (build from the character table), the one prop they're known by, and a `Face` marker the conversation camera looks at. Brothers, visitors and passers-by wear them through a `CharacterLook` node (`look`); the gate's visitors name theirs in their `Visitor` resource.

| Scene | Who | Prop |
| --- | --- | --- |
| `chr_thomas` | Brother Thomas, tall and thin | Herb pouch |
| `chr_osric` | Brother Osric, short and heavy | Ring of cellar keys |
| `chr_ranulf` | Brother Ranulf | Censer on its chain |
| `chr_godric` | Abbot Godric, small and frail | Crosier |
| `chr_hugh` | Prior Hugh, lean | Wax tablet |
| `chr_anselm` | Brother Anselm, hunched | Walking stick |
| `chr_edwin` | Brother Edwin, gangly | Book |
| `chr_cole`, `chr_dunstan` | The lay brothers, big, in brown work tunics | None |
| `chr_choir_brother_a`, `_b`, `_c` | The choir brothers on night 3 | None |
| `chr_choir_brother_dead` | Brother Bede: beside the porter at supper on night 1, hanged in the bell tower on night 2, seen dead in the choir on night 3 | None |
| `chr_stranger` | A hooded stranger in a habit | None |
| `chr_mab` | Mab, small, in rags, face covered | Leper's clapper |
| `chr_walter` | Walter the pardoner, plump, in the only coloured cloak | His box and bag are on VisitorNPC, where they're read |
| `chr_joan` | Joan, slight | Her brother's pilgrim badge |
| `chr_roger` | Roger the bailiff (not in the character table yet) | None |
| `chr_pilgrim` | A pilgrim | Staff and shoulder bag |
| `chr_carter`, `chr_lane_woman` | The carter, and Margery, passing in the lane | Margery's basket |
| `chr_merchant` | The merchant-pilgrim at the gate on night 1: stout, a dark-red cloak | A fat purse, a pilgrim's staff |
| `chr_sailor` | The sailor at the gate on night 2: lean, weathered | A sea bundle |
| `chr_hob` | Hob, who keeps the Cross Keys: big, red-faced, an apron | A jug |
| `chr_agnes` | Agnes, Hob's wife: a dark wool dress | A cloth on her shoulder |
| `chr_jankin` | Jankin, the Keys' drunk: gangly, patched | A cup |
| `chr_gib` | Gib the watchman: old, hunched, a grey cloak | His staff (his lantern is the visitor's) |
| `chr_ralph` | Ralph the chandler: short and heavy | A bundle of candles |
| `chr_kit` | Kit, Ralph's daughter: small, quick | A basket of candles |
| `chr_traveller` | The traveller on the wagon: lean, road-worn | A pack |
| `chr_warden` | The warden at Aldgate on the road in: solid, a dark cloak over a leather jerkin | A tall staff, and a lit lantern |
| `chr_townswoman` | A woman in a doorway on the road in: a plain dark dress | None |
| `chr_cat` | The abbey cat, black, 0.45 m, eyes that catch the light (worn by `game/npc/cat.tscn`) | None |
| `chr_saint` | The Hungry Saint: about 2.6 m, too thin, bent forward, no horns, unshaded black | None |
| `chr_body` | A body: the ragdoll rig (`game/ragdoll`) in the victim's colours, standing until it falls (`Corpse`) | None |

`tools/review.sh cast_brothers res://tools/godot/cast_brothers.tscn` renders the brothers side by side through the lookdev stage; `cast_choir_and_lay` and `cast_town` do the rest.

## Sizes that changed in M7

Some boxes were one long block, which no model could replace. They became modules, and a few sizes were evened out to the prop's:

- The refectory's 16 m tables and benches are 2 m tables and benches, 8 to a row.
- The chapter house's 7 m bench is three 2 m benches; the 6 m woodpile is three 2 m stacks; each side of the choir stalls is two 4 m runs.
- The infirmary beds are 0.45 m high, not 0.5. The kitchen table (1.8 m) and the herb table (1.6 m) are the 2 m table, 0.75 m high; the mortar moved down onto it. The bench by the gate is 2 m (was 1.6), the dormitory stool 0.4 m (was 0.35).
- Houses of one type take the first house's door and windows.
