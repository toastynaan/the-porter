# Assets

Most of the world is still a placeholder: boxes, cylinders and the greybox figure, in the shared materials. Each kind of thing lives in one scene, so a real model replaces it in one place and every copy in the world changes with it. Swap them in any order. The first real ones are on the road in (night 0); how they're made is below, then the placeholders.

## Real assets: how they're made

Every model is built by a script, and every texture is fetched and finished by one, so anything can be changed and made again.

| Step | What | Where |
| --- | --- | --- |
| Textures | `tools/build/tex_fetch.py` downloads the CC0 textures listed in `tools/build/textures.json` from Poly Haven, scales them to 1024 or 512, pulls their colour toward the palette (less saturation, cooler greys), and writes colour, normal and occlusion-roughness maps | `art/tex/tex_<name>_col.jpg`, `_nrm.jpg`, `_orm.jpg`; each credited in `art/credits.csv`. The downloads themselves stay out of the repository (`art/_src/`) |
| Models | `tools/build.sh <name>` runs `tools/build/<name>.py` in Blender. A script works in the game's own space (metres, +Y up, front at -Z) through `tools/build/porter.py`, and writes one model | `art/models/<name>.glb` |
| Materials | A model carries material names only. On import each is linked to the material of the same name, so models share materials and textures | `game/world/materials/real/<name>.tres` (linked by `tools/build/link_imports.py`, which `build.sh` runs) |
| Scenes | A model is placed through a scene of its own, which adds what a model can't carry: lights, scripts, seats | `game/world/props/prop_*.tscn`, `game/world/road/*.tscn`, `game/characters/chr_*.tscn` |

- **Vertex colour** does the grime: materials multiply it in (damp at the foot of a wall, shadow under the eaves, darker twigs). The ground's shader reads it as masks instead.
- **Collision** is an object named `<Name>-colonly` in the model (Godot makes it a collider on import).
- **Look at a model on its own:** `tools/model_shots.sh <name>` renders it from two sides to `art/_review/models/`.
- Close the Godot editor before `tools/build.sh`: it imports with the command-line Godot.

### What's real so far (the road in)

| Model | Built by | What | Scene |
| --- | --- | --- | --- |
| `env_road_fields` | `env_road_fields.py` | The ground outside Aldgate: the road, its verges and wet ditches, open fields in ridge and furrow, the chapel's level yard. 240 by 280 m | In `env_road.tscn`, at the origin |
| `env_road_backdrop` | `env_road_backdrop.py` | The horizon: two ragged bands of far woods round the fields' edges | In `env_road.tscn`, at the origin |
| `env_white_chapel` | `env_white_chapel.py` | The white chapel: nave, chancel, west tower, north porch, lancets with candle-lit leaded glass; its yard with a rubble wall, a gate, a preaching cross and graves | `game/world/road/env_white_chapel.tscn` (adds the candlelight thrown out through the glass) |
| `prop_tree_elm`, `_oak`, `_thorn`, `_pollard` | `prop_trees_bare.py` | Bare winter trees, grown by forking: a tall hedgerow elm, a broad field oak, a wind-bent hawthorn, a pollard willow | `game/world/props/prop_tree_<kind>.tscn` |
| `prop_cart` | `prop_cart.py` | A two-wheeled cart: plank bed, ladder sides, headboard, spoked wheels (their own parts, so they turn), shafts, a stake for a lantern | `game/world/road/prop_cart.tscn` (`CartRoll` turns the wheels and rocks the body) |
| `chr_horse` | `chr_horse.py` | A bay cart horse in a collar, in parts that turn at their joints; coloured by vertex, shaded per vertex | `game/characters/chr_horse.tscn` (`HorseGait` walks or trots it by how far it's carried, 15 poses a second) |
| `prop_shrouded_body` | `prop_shrouded_body.py` | A body under sacking | On `prop_body_cart.tscn` |
| `env_city_wall` | `env_city_wall.py` | London's wall each side of Aldgate, 280 m of it: ragstone rubble laced with bands of old tile, battered at the foot, battlements (merlons fallen here and there), four half-round bastions (a candle in one: an anchorite), a stretch to the north fallen to half its height, the stair to the walk on the city side, the causeway's parapets over the ditch, buttresses of cut stone, arrow slits, and a mason's scaffold against a mended stretch north of the gate | In `env_road.tscn`, where the gate stands |
| `env_aldgate` | `env_aldgate.py` | Aldgate: two round towers, the north one with a stair turret under a pointed cap; between them a pointed archway in two orders, the portcullis drawn up with its teeth showing, oak doors folded back, a ribbed vault; over the arch the city's shield, a worn saint under a canopy, and the chamber's windows with candles lit; a tiled roof behind the battlements; a timber hoarding round the south tower's top, open putlog holes, two banners, lead spouts, three heads on pikes, a boarded shelter for the watch. The gate is cut stone (`stone_ashlar`), the towers rubble. The road through is 5.4 m wide | In `env_road.tscn` |
| `env_city_skyline` | `env_city_skyline.py` | The city behind the wall. `Near`: rows of roofs and five parish churches. `Far`: more towers, and St Paul's with its spire, as flat shapes in the colour of distance | In `env_road.tscn`, at the origin (`RoadCity` hides `Far` near the lane) |
| `env_aldgate_street` | `env_aldgate_street.py` | The ground inside the gate: wet cobbles, mud down the cart track and against the houses, a kennel down the middle. 39 by 7 m, from the gate to the brook | In `env_road.tscn`, at the origin |
| `env_aldgate_bridge` | `env_aldgate_bridge.py` | Aldgate's bridge over the city ditch: the drawbridge's oak leaf to a stone pier, two lifting beams with chains, ropes and toothed wheels on the gate's face, a fixed timber span on a trestle with rails, the stone sill, bay sides, abutment and rocks, the frame the leaf shuts into. 5,000 triangles | In `env_road.tscn`, where the gate is |
| `env_city_brook` | `env_city_brook.py` | The brook across the street and its bridge: a hump-backed arch of cut stone with parapets, six piers with iron standards and horn lanterns, cutwaters; the brook's rubble walls 26 m each way to a house built over it on an arch; steps to the water, mooring posts; the water (`water_brook`). 3,500 triangles | In `env_road.tscn`, at the origin |
| `env_alley_a`, `env_alley_b` | `env_alley.py` | What stands in an alley between two houses: a mud floor with standing rain, yard walls, and (a) a room built across it and an end wall with a door and a lit window, or (b) washing lines, a lean-to and an archway into a yard. 1,000 triangles each | `game/world/street/env_alley_a.tscn`, `_b.tscn` (with their lanterns), placed in `env_road.tscn` |
| `env_house_timber_a` … `_h` | `env_house_timber.py` | Eight houses, no two finished alike (plaster: limewash, ochre, or grey gone to the brick; frame: brown, silver, tarred; roof: tile, mossed tile, plain tile, slate); g is a merchant's house of cut stone under a timber gable, h a narrow four-floor house; some have a brick chimney, a pentice over the shop, an oriel, brick nogging. Timber houses: oak frames (close studding, square panels, chevron braces), limewashed panels, each floor jettied 0.5 m over the one below with the joist ends showing, tiled roofs with the gable or the eaves to the street, shop fronts with stall boards, a hanging sign, an ale-stake, smoke louvres. Each leans its own way. Every window pane and the door are their own objects | `game/world/street/env_house_timber_<a-h>.tscn` (`TimberHouse` lights the panes in `lit_windows`; four carry a lantern on an iron bracket) |
| `prop_street_barrels`, `_crates`, `_handcart`, `_stall`, `_firewood`, `_trough`, `_bench`, `_ladder`, `_posts`, `_cresset` | `prop_street.py` | What stands about in the street: casks and a wash tub; boxes and sacks; a handcart tipped on its shafts; a shut stall under a sagging cloth; stacked firewood; a stone trough and pump; a bench and pail; a ladder; three posts; an iron fire basket on a wall bracket. Wall pieces have their backs at z = 0 and face -z. No collision | The models directly under `Clutter` in `env_road.tscn`; the cresset is `game/world/props/prop_cresset.tscn` (`Brazier`, with `bare` so its own bars throw no shadow) |
| `env_road_growth` | `env_road_growth.py` | Dead grass tufts, reeds and docks on the verges, ditch banks and fields, in five lengths of the road; one material, `growth`, whose shader bends them in the wind | In `env_road.tscn`, at the origin |
| `prop_field_hedge`, `_fence`, `_gate`, `_shrine`, `_scarecrow`, `_rick`, `_cot`, `_mill`, `_wreck`, `_bridge`, `_stone` | `prop_field.py` | What stands in the fields: 10 m of bare hedge; wattle hurdles; a five-barred gate; a wayside cross with a candle in its niche; a scarecrow; a hayrick; a cob-and-thatch cot with a lit window; a post mill (its `Sails` their own object); a wrecked wheel; planks over the ditch; a mile stone | Stood on the ground under `Dressing` in `env_road.tscn` by `road_dressing.py`. Scenes for three: `prop_field_mill.tscn` (`Spin` turns the sails), `prop_field_shrine.tscn` and `prop_field_cot.tscn` (their lights) |
| `prop_tree_snag`, `prop_tree_yew` | `prop_trees_bare.py` | A dead oak with broken limbs; a churchyard yew, the one evergreen (material `yew`) | `prop_tree_snag.tscn`; `prop_tree_yew_real.tscn` (the abbey's yews are still the placeholder `prop_tree_yew.tscn`) |
| `prop_cart_load` | `prop_cart.py` | The carter's load: a chest under a roped canvas, a cask, sacks | In `prop_wagon.tscn` |
| `prop_brazier` | `prop_brazier.py` | A watch fire: an iron fire basket on three legs, coals, flames | `game/world/props/prop_brazier.tscn` (`Brazier`: a light that is never still and throws shadows, and sparks) |
| `prop_gibbet` | `prop_gibbet.py` | A gibbet: a timber arm and an iron cage with a body in it | `game/world/props/prop_gibbet.tscn` (`Sway` swings the cage) |

`tools/build/city_parts.py` holds what the city's scripts share: faces cut small so each vertex carries its own grime, round towers, pointed arches and vaults, battlements, roofs, lancets; `stone_tint` also asks for the second surface in big patches, and `wood_tint` shades boards one by one. The wall and the gate are built in one space (the wall along x, the country at -z), so they share one place in the scene.

`prop_wagon.tscn` (the carter's wagon) and `prop_body_cart.tscn` are now the cart, the horse, and their seats; the wagon has a lantern on its stake. The trees along the road are stood on the ground by `tools/build/road_dressing.py` from its list (`tools/build.sh road_dressing`): change the list, not the scene.

Materials in `game/world/materials/real/`: `ground_fields` (its own shader: mud, grass, ploughed soil and stubble blended by the mesh's masks, wheel ruts, standing water that carries the sky), `plaster_white`, `stone_blocks`, `roof_slates`, `wood_medieval`, `wood_cart`, `iron_cart`, `bark`, `grave_earth`, `sacking`, `horse_hide`, `horse_tack`, `far_dark`, `window_dark`, and `window_candle` (leaded glass with candles behind it, never quite still). For the city: `stone_rubble` (the wall), `tile_course` (its bands of tile), `roof_tiles`, `plaster_daub`, `painted` (flat colour from the vertices: the shield, the signs), `far_city` (unlit, and the fog leaves it alone), `ground_street` (its own shader: cobbles, mud, ruts, standing water), `window_horn` (a lit window of horn or cloth, with somebody passing behind it now and then), `flame` and `embers` (the watch fire). The city's stone, plaster, timber and roofs share one shader, `surface.gdshader`: two surfaces a material (the wall as built, and what shows where it has failed, in patches of its own and where a vertex's alpha asks), uneven tone over a long wall, moss from the ground up, and rain (dark and shining where it faces the sky, streaked where it does not). Its materials: `stone_rubble`, `stone_ashlar` (the gate), `brick_old`, `plaster_daub`, `plaster_ochre`, `plaster_worn`, `wood_frame`, `wood_boards`, and by UV `roof_tiles`, `roof_mossy`, `roof_plain`. `blotch_noise.tres` is the noise they share. Also on the surface shader: `plaster_lime` (the chapel: limewash over rubble). Plain materials for the fields: `hedge`, `straw`, `yew`.

## Placeholders

Everything else is a placeholder, as below.

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
| `road/prop_wagon`, `road/prop_body_cart` | Real now: see "What's real so far" | Night 0's ride |
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

Night 0's road is `game/world/road/env_road.tscn` (fields, the white chapel, the city wall and Aldgate, the street inside it, and the `RidePath` the wagon follows). The street inside Aldgate is made of the six real houses (`env_house_timber_*`), not the lane's four placeholder types above, which are still what the lane and its bends use. A house in the lane's own scene that only stands in for the city on other nights is in the group `road_in_hides`, and is cleared on night 0 (`RoadCity`). The squints are `game/world/kit/wall_squint.tscn`, a 4 m wall module with the barred slit.

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
