# The prologue and the lane (M12)

Night 0 at the Cross Keys and day 1's tour, the squints, and the lane at dusk on every night: its people, what they say, the curfew bell and the watchman. The rules are `docs/systems/mechanics.md`'s ("Night 0 and day 1", "The lane at dusk"); the story is the design doc's. Numbers marked *mine* are starting values to tune.

## Night 0, the Cross Keys (`game/chapters/night0/night0.tscn`)

The clock starts at 16:30 and runs at 150 s an hour *(mine)*, so the ride is grey dusk turning dark, and midnight comes about 19 minutes in. Rain until 19:00. The Director's beats:

| Beat | What happens | Ends when |
| --- | --- | --- |
| `Ride` (the start bell) | On rails: the carter's wagon drives itself from the fields past the white chapel, over the drawbridge and through Aldgate, along the close street to the bridge over the brook, a minute and a half or so. As it comes over the bridge's crown the night goes dark over 2.5 s *(mine)* with the wagon still rolling; 1.2 s later it comes up again in the lane, the wagon rolling its last ten metres to the abbey gate. If he is still talking at the crown the wagon crawls on (0.5 m/s, 9 m at most *mine*) and the dark waits until he's done. **The road and the lane are two places that are never shown together:** the abbey, the lane and their people are hidden for the ride, and in the dark the road scene and its people are removed (`RideBeat.road`, `road_folk`, `lane_world`). So the road doesn't have to join the lane, and neither is drawn while he is in the other. For the first 8 s nobody speaks. Then the traveller beside him turns to him and asks where he's bound (`n0_traveller_road`); he can talk to the traveller again at any time. The ride's cues play as the wagon passes them (below). About 22 s in the carter pulls in toward the ditch and stops ("Easy, easy. Let him by.", unless they are talking); a cart with four bodies under sacking comes on down the road. Any talk goes on until it is 8 m off *(mine)*; then the traveller breaks off whatever he was saying, with no parting line: "Whoa. Look at that." The cart creaks by close on his side. The porter's view goes to the bodies and follows them by for 3.6 s *(mine)*, narrowed (moving the mouse lets go), and the traveller speaks about them (`n0_traveller`: pilgrims, seven this month on this road, all bound for the abbey; nobody saw them come out; what people say, he won't tell). The ride reveals nothing of what or who is behind the deaths: no demon, no men, no robbery as the wagon goes on. At Aldgate the wagon stops, and the traveller breaks off any talk to greet the warden. The warden asks in or out, then walks up to the back of the wagon, on the porter's side, holds his lantern up beside his own face, close to the porter's, and talks to him (`n0_warden`: where he's bound; the new porter is told to shut his gate at the curfew bell). Then he lowers it and walks back to his place, saying they're good to go. At the gate it waits until nobody's talking; the carter sets him down beside it (`n0_carter`) and drives off down the lane | He's in the lane |
| `Arrive` | The gate is shut and barred, a lantern over it, and Cole isn't at it. He knocks (the `KnockGate` duty); nobody comes; the duty flame goes to Mab, whose first words send him to the Keys (`n0_mab`) | Mab has spoken to him |
| `Inn` | The flame goes to Agnes by the fire; the bed answer gives him the room at the top | `n0_room`, or midnight |
| `Window` | The bed in his room is wanted. Lying down: the cry, and he's at the window over the abbey wall. In the court a man with a lantern is killed by the well by a figure in a black habit, its back to the window, and dragged off toward the cellar. His notes say what he saw, or, if he'd drunk enough to see double, that he isn't sure (`window_killing`, `window_killing_drunk`). At midnight, if he isn't in bed, Agnes sends him up and it plays the same | The body is gone |
| `Sleep` | "Lie down again. Sleep, if you can." | He sleeps: day 1 |

**The ride's cues** (`RideCues` in `night0.tscn`, each a `RideCue`): markers beside the road, counted from the nearest point of the road, so moving one moves its moment. Each can say lines, have someone start a talk with him (`talk`, `talker`), play a sound, set the wagon's pace, stop it for a while, and turn people nearby to watch it. Their lines and talks wait while the porter is talking, and are dropped once the wagon is `keep` metres past; a cue with `cut_in` breaks off his talk instead, and drops the lines still waiting.

| Cue | Where | What |
| --- | --- | --- |
| `Fields` | 22 m on (about 8 s) | The traveller turns to him: bound for the city? Pace 2.6 m/s *(mine)* |
| `WhiteChapel` | The chapel, 39 m on | Its bell rings for Vespers; the carter means to be in before the gate shuts |
| `Whoa` | 6 m before the pull-over | The carter: easy, let him by. He pulls in to let the cart by. The line is dropped if they are talking; the traveller's own "Whoa. Look at that." breaks off the talk as the cart comes close (`RideBeat`, not a cue) |
| `Wall` | 12 m short of Aldgate | The city wall, a lantern in the arch. Pace 2 m/s |
| `Aldgate` | The warden, outside the arch | The wagon stops and the traveller breaks off any talk to greet the warden (`cut_in`). The warden asks in or out and the carter answers; with "Let's have a look at you" he walks up beside the porter (`inspector`, 1.2 m/s *mine*), holds his lantern up to his face and talks to him (`talk`, `n0_warden`), lowers it and walks back to his place saying they're good to go (`parting_lines`); sets `n0_past_aldgate`, so the traveller opens on the warden after; 1 s more, then on at 3.2 m/s |
| `Shutters` | The first houses | Shutters bang closed above as the wagon passes |
| `Doorway` | A woman in a doorway | She watches it go by and crosses herself |
| `Dog` | Farther in | A dog barks behind a door; the traveller says they bar their doors early since the pilgrims |
| `Bridge` | Ten metres short of the bridge | The carter: over the brook, and your lane's the next turning. Pace 2.2 m/s. The last words of the road: the night goes dark from the crown (`Marks/DarkAt`) |
| `Lane` | In the lane, just after the light comes back (`Marks/LightAt`) | The traveller: that wall's your abbey; bar your door at night |

The wagon speeds up and slows down at 1.2 m/s² *(mine)*, and its rumble fades as it slows. The body cart starts 40 m past the pull-over and comes on at 2 m/s *(mine)*, waiting 9 m off until the wagon has pulled in. Paused, the ride waits.

The killing (`WindowKilling`) is an implied death that feeds nothing (it's before the six nights). The victim's lantern is lit now (every `DeathScene` with `lantern`): the struggle is shapes against its light, then it falls, rolls and burns low on the ground.

**The Cross Keys** (`game/world/street/env_inn.tscn`): three storeys, enterable. The taproom has the hearth, the counter, tables and benches; the stairs at the back left go up to an open loft of beds, and on to the top floor, where the porter's room is at the front right with one window toward the abbey. On night 0 Hob and Agnes are inside, with Jankin, Walter, Roger and Ralph drinking. The taproom's talk is heard while the Keys is open.

**Drinking:** an ale is an answer in Hob's or Agnes's talk (`[drink]`), and each ends the talk. +1 an ale, 5 at most, 1 lost an hour, cleared by sleep. What he sees (`DoseDriver`, the post shader's `drunk`):

| Drink | You see |
| --- | --- |
| Over 0.5 | A softer focus: 0.5 + 0.15 source pixels of blur an ale *(mine)* |
| Over 2 | The double image, drifting with the view, growing to full at 5 *(mine: it starts as the third ale wears in)* |
| Any | A slow drift of the view; no palette shift |

Three ales or more in a night (`drank`) and he wakes with a headache: a 0.9-pixel blur until noon *(mine)*.

**The squint scare** (`SquintScare`, night 0 only, once): after the curfew bell, passing outside the south squint within about 4.6 m, alone (nobody of the lane within 12 m *mine*), a shape stands just inside it while its spot is out of his view: the Saint's figure, still. He has seen it once he has looked at the slit from within 3.5 m with a clear line through it; once he looks away it's gone for good (`n0_squint_scare`). If he walks on without seeing it (8 m off), it goes and can come again. The animals go quiet while it's there.

## The look of the road in (first pass: the fields)

The ride's first stretch, from the fields to the foot of the city wall, has its real look. (The wall, Aldgate and the street inside it came next: the section after this one. The lane, its bends and the people are still greybox.)

- **The sky** (`game/core/render/sky.gdshader`, driven by `Daylight`): at night the one flat moonlight blue the game has always had; with daylight in it, a low deck of rain cloud drifting over; at dusk a strip of last light along the horizon where the sun went down, pale straw at the rim going to slate, barred with cloud. It is a cold light: purple and rose are kept for the drugged look. Every night's dusk has it, not only this one.
- **The sun sets behind the wagon.** The porter rides facing back, so he watches the day go over the road he came by, and the city ahead is the dark he is carried into. Night 0's dusk is brighter than the abbey's (`Daylight` on `night0.tscn`: sky 1.0, ambient 1.5, sun 0.7 *mine*), and is all but gone by the lane.
- **Distance** (`RoadAir`, `game/world/road/road_air.gd`): out in the fields far things fade into the sky they stand against (depth fog from 14 m, whole at 230 m, taking the sky's own colour *mine*). It thins inside the wall and is gone by the turn into the lane; the abbey's nights don't have it.
- **The ground** (`env_road_fields`): the road two carts wide, with ruts that wander and hold long uneven pools; a grass verge and a wet ditch each side; open fields in ridge and furrow with rain standing in the furrows. All the water lies level and carries the sky, so the last light runs down the ruts.
- **The white chapel** stands 17 m south of the road in a walled yard, limewashed, candles lit inside for Vespers behind leaded glass.
- **Trees** stand bare along the road and out in the fields: elms, oaks, hawthorns, pollard willows by the ditches (35 of them, `tools/build/road_dressing.py`). A band of far woods closes the horizon.
- **Rooks** wheel over the great oak north of the road, and low over the road far back, against the light (`Rooks`).
- **Ground mist** lies thin over the fields near the wagon (a `FogVolume` in `env_road.tscn`).
- **The wagon** is a real cart and a bay horse that walks or trots in step with the ground; the carter's lantern hangs on a stake at the headboard. The cart that passes carries four bodies under sacking, three side by side and one laid across them. Both carts jolt and sway over the road on springs (`CartJolt`: each wheel runs over its own ruts and stones; the bed tips about the horse's back). The seats are on the bed, so the porter, the traveller and the carter jolt with it, and the porter's view rolls and pitches with his seat (80% of it *mine*; Less motion takes the tilt away and leaves a third of the jolt).
- **The abbey's cat** keeps to the abbey on night 0 (it was following the wagon through the fields).

Fixed with it: the lane's skyline (the city's far roofs, towers and a second city wall, `Skyline` in `street.tscn`) stood across the road in: the wagon drove through four of its blocks, and its far rows stood in the fields outside Aldgate. Everything of it outside the wall, and the two blocks in the roadway, are gone; the city behind the wall keeps its nearer rows and two spires.

`tools/shots/intro_shots.sh` takes stills along the road to `art/_review/intro/` (the wagon stood at set places and hours); `tools/shots/intro_film.sh` films the first half-minute as it plays.

## The look of the road in (second pass: the wall, Aldgate, the street inside)

From the foot of the wall to the end of the first street. The turn, the lane and the people are still greybox.

- **The city against the sky.** The east is no longer one dark: a cold pale break lies low in the cloud behind the city while there is daylight left (`Daylight.sky_break` on `night0.tscn`, 2.2 *mine*; the sky shader's `break_*`), so the wall, the gate's towers, the church towers and St Paul's stand black against it. It is cold on purpose: the warm light is behind him, and every warm thing ahead is a fire or a candle. Other nights have no break.
- **The wall** (`env_city_wall`): ragstone rubble laced with bands of old red tile, 8 m to its walk, battlements with merlons missing, half-round bastions, a stretch to the north fallen to half its height. One bastion has a candle in a slit.
- **The city ditch** lies along the wall's foot, 11 m wide with black water in it (part of `env_road_fields`); the road crossed on a causeway between low parapets (now a drawbridge: the fifth pass). Three trees that stood there moved back from it.
- **Aldgate** (`env_aldgate`): two round towers and the gate between them, a pointed arch with the portcullis drawn up into it and the doors folded back, a vaulted passage 6.6 m long. Candles are lit in the chamber over the arch and in the south tower. The road through is 5.4 m wide (it was 6).
- **The warden's post:** a watch fire in an iron basket at the foot of the south tower (`WatchFire`), throwing the wagon's shadow up the gate; a lantern on the north jamb by the warden, another in the passage.
- **The gibbet** hangs from the south tower over the ditch, in the fire's light: a cage with what is left of a man. Nobody speaks of it. *(Mine: the city showing the road what it does. Take `Gibbet` out of `env_road.tscn` if it is too much.)*
- **Rooks** wheel about the gate's towers.
- **Looking back from under the arch** he sees the road he came by and the last light, framed by the vault and the portcullis's teeth. Then the gate is the tower at the end of the street behind him, its windows lit.
- **The street inside** (`Houses` in `env_road.tscn`): sixteen timber houses close on both sides (twelve since the brook: the fifth pass), no two alike standing together, an alley between two of them on each side. Upper floors jut out until the roofs nearly meet. Windows are lit behind horn and cloth, and now and then somebody passes behind one. Three houses carry a lantern on a bracket. The woman in the doorway stands in an open, lit door.
- **The street's ground** (`env_aldgate_street`): wet cobbles, mud down the cart track, a kennel with water in it. Lanterns and windows lie along it in pieces.
- **The skyline** (`env_city_skyline`): roofs and parish churches behind the wall; far off, more towers and St Paul's. The far ones are put away once the wagon nears the lane (`RoadCity.far_until_x`), so the abbey's sky on night 0 is the one it has every night.

Fixed with it: a plaster wall stood across the road at the end of the street (the lane's `FarEnd`, which closes its bend on other nights), and the wagon drove through it. It and the lane's greybox city blocks west of the bend are in the group `road_in_hides`; `RoadCity` clears them on night 0.

`tools/shots/intro_shots.sh` now takes 25 stills, 13 of them of the wall, the gate and the street.

## The look of the road in (third pass: the rain, and the wall, gate and street in detail)

The second pass read as one stone and one house, and its rain as a few white scratches. This pass is about difference: between the wall and the gate, between one house and the next, between a lit wet surface and a dark dry one.

**Rain** (`Weather`, every rainy night, not only this one):

- It is GPU particles now: 16,000 drops *(mine)* born in a slab 12 m over the camera, falling at 11.5 m/s on a gusting wind (`rain_fall.gdshader`).
- **It stops at roofs.** The drops land on a height field of whatever is under the sky round the camera, so it is dry in the gate's passage, under a jetty, indoors.
- **It splashes** where it lands: a small crown of spray on the cobbles, the roofs, the wagon.
- **It shows where light is** (`rain_drop.gdshader`): faint against the sky, gold near a lantern or a fire, brightest with the light behind it. Drops within 2 m of the eye are not drawn.
- **Standing water is struck:** rings open in the puddles of the street and the fields (`rings()` in the two ground shaders).
- **Eaves drip:** lines of heavy drops off the street's eaves and the gate's parapets (`Drips` in `env_road.tscn`, `game/world/weather/drips.gd`).

**Surfaces** (`game/world/materials/real/surface.gdshader`, one shader behind the city's stone, plaster, timber and roofs):

- Each material is two surfaces: the wall as built, and what shows where it has failed. Rubble goes to mossed stone, cut stone to rubble where the facing fell, limewash to bare daub, grey plaster to the brick under it, brown oak to silver, red tile to mossed tile. The second shows in ragged patches of its own, and wherever the model asks for it (a vertex's alpha).
- Long walls are uneven in tone, moss comes up from the ground and lies on ledges, and rain darkens and shines what faces the sky and streaks what does not.
- Ten more Poly Haven textures (cut stone, mossed stone, old brick, ochre, clay and worn plaster, boards, silvered wood, two roofs), in `art/credits.csv`.

**The wall** gains buttresses of cut stone, arrow slits, and north of the gate a mason's scaffold of lashed poles with a ladder, against a stretch mended in new pale stone *(mine: it is always being mended)*.

**Aldgate** is cut stone now, against the wall's rubble. Added: a timber hoarding round the south tower's top, the scaffold's putlog holes left open in both towers, two sodden banners and lead spouts on the front, a boarded shelter for the watch by the north tower, three heads on pikes over the arch *(mine, with the gibbet: delete `pikes()` from `env_aldgate.py`'s `main` if it is too much)*, and three fire baskets on brackets (`Cressets` in `env_road.tscn`): one each side of the arch, one on the city face.

**The street:**

- Eight houses now (`env_house_timber_a` … `_h`), no two finished alike: limewash, ochre wash, or grey plaster gone to the brick; frames brown, silver or tarred black; tile, mossed tile, plain tile or slate. New: a merchant's house of cut stone under a timber gable (g) and a narrow four-floor house (h). Some have a brick chimney, a pentice roof over the shop, an oriel window, a floor nogged with brick.
- Things stand about (`Clutter` in `env_road.tscn`, from `tools/build/prop_street.py`): casks and a wash tub, crates and sacks, a handcart tipped on its shafts, a stall shut for the night, stacked firewood, a stone trough and pump, benches, a ladder, posts at the gate corner. All of it is out of the wagon's way and can be moved or deleted by hand.

**What it costs.** Triangles: the gate 6,100 (was 5,300), the wall 9,300 (was 7,900), a house 700 to 1,350, all the street's clutter together 2,900. The whole view from the gate to the end of the street is about 65,000. The surface shader reads thirteen textures a pixel where the old materials read six.

Still greybox: the turn, the lane, the people.

## The look of the road in (fourth pass: the fields, the chapel, the trees, the wagon)

The fields were bare beside the gate and the street. This pass fills them, and puts small lights out in the dark.

- **Fixed: the chapel had no west wall.** The nave's west end was left open each side of the tower, so the inside of the roof showed. The porch's walls were also one-sided.
- **The white chapel** is limewash over rubble now (`plaster_lime`: the wash has fallen in patches and moss climbs it). Added: a door ajar with candlelight in the gap, a lantern in the porch, a sanctus bell on the east gable, a cross on the tower, two yews in the yard, and south of the chancel a row of fresh mounds with no markers and one grave dug and left open with the spade in its heap *(mine: the autumn's dead, and nobody says of what)*.
- **What grows** (`env_road_growth`): dead grass in tufts on the verges and ditch banks, reeds at the water in the ditches and thick along the city ditch, docks and thistles in the fields. It bends in the wind (`growth.gdshader`).
- **Hedges** along the road in broken lengths and down the edges of the furlongs away from it, with gates in two of the gaps; a fold of wattle hurdles in the north field.
- **People's places, each with a light or a shape:** a cot with one lit window and its hayricks south of the road, another far to the north; a post mill on the western rise with its sails turning, black against the last light; a wayside shrine by the road with a candle somebody still lights; three scarecrows *(mine)*.
- **On the road:** a mile stone, planks over the ditch to the chapel's gate, a wrecked cart wheel on the verge.
- **Trees:** 63, up from 35. New: dead oaks (`prop_tree_snag`), one by the road; more thorns and pollard willows down the ditches and in the hedges; two small copses. The elms carry rooks' nests.
- **The wagon** carries a load amidships, clear of the three seats: a chest under a roped canvas, a cask, sacks. The cart itself gains side boards and a tailboard, iron straps, a bucket slung under the tail, a coil of rope, mud under the bed.

Everything in the fields is stood on the ground by `tools/build/road_dressing.py` from its two lists (`TREES`, `DRESSING`): change the lists and run it, since it puts back anything moved by hand.

**What it costs.** The grass is 42,000 triangles in five lengths of road. A length of hedge is 500, the mill 650, a cot 340. The trees are the heavy thing, as before: an elm is 10,000 triangles and an oak 9,000, and there are 26 of them; Godot's own mesh LODs thin the far ones.

## The look of the road in (fifth pass: the drawbridge, the alleys, the brook and its bridge)

**Aldgate's drawbridge** (`env_aldgate_bridge`). The causeway is gone: the city ditch runs through under the road, and reaches in to the foot of the arch.

- **The leaf** lies lowered from the gate's sill to a stone pier: oak boards, iron straps, a kerb each side.
- **What lifts it:** two beams standing out of slots over the arch, a chain from each tip down to the leaf's outer corners, a spare length hanging, ropes back to the wall, and beside each beam a toothed wheel on the gate's face with its shaft, pinion and crank.
- **The fixed span** runs on from the pier to the bank on a trestle of three piles, with posts and rails. One length of rail is gone. A lantern hangs from a tall post at the bridgehead.
- **Stone:** the sill, the bay's sides, the pier with its cutwaters, the bank's abutment and wing walls, rocks along the water, and a raised frame round the arch that the leaf shuts into.
- The towers' lower arrow loops are crosses now. The warden stands on the leaf.

**The alleys** (`env_alley_a`, `_b`, in the gaps between two houses on each side of the street, now 2.1 m wide):

- **South:** a room built across it from house to house, and at its end a wall with a low door and a lit window.
- **North:** washing lines, a lean-to, and at its end an archway into a lit yard.
- Each has a dim lantern at its mouth and a brighter one at its far end, so whoever is in it is a shape against the light.
- **The people in them** (`RoadFolk/Alleys` in `night0.tscn`, each a `Lurker`, `game/people/lurker.gd`) are never met. *All mine:*
  - one in the south alley's mouth who steps back under the room as the wagon comes near;
  - two at its far end bent over something long under sacking, who straighten and turn;
  - one standing in the north alley's archway, who turns to keep facing the wagon;
  - one there with their face to the wall, rocking;
  - one at the foot of the steps to the brook, at the water, watching the wagon cross.
- They are the greybox figures, like everyone else: shapes in the dark. Each can be moved, given another `act`, or deleted.

**The brook and its bridge** (`env_city_brook`):

- The street ends at black water 8 m wide between rubble walls. The street has six houses a side now.
- **The bridge:** one low arch of cut stone, hump-backed (0.8 m at the crown), cobbled, a parapet each side between six stone piers. Each pier carries an iron standard and a horn lantern (`BridgeLamps`, `prop_lantern_hung`). *(Mine: the picture this follows has gas lamps; these are what 1420 had.)*
- **The brook** runs away north and south between houses with their fronts to the water, 26 m each way, to a house built over it on an arch with a lit window. Mist lies on it. Steps go down to it by the bridge; mooring posts stand in it.
- **The water** (`water_brook.gdshader`) is a moving near-mirror: the lanterns lie on it in broken streaks, and the rain rings it.
- **This is where the night goes dark** (the `Ride` beat above). He is looking back from the crown: the bridge's lanterns, the whole street, and Aldgate at the end of it.

**Beyond the bridge** the street runs on 15 m and turns south between houses, with a house across its end, so nothing shows past it. The wagon is on it only as the night goes dark. Nothing of the lane is cleared for the road any more (`road_in_hides` is unused): the lane isn't shown until the road is gone.

**The gate's back corners** have a buttress each, out to the first house, closing the gap that showed what lies behind the houses.

**What it costs.** The drawbridge 5,000 triangles, the brook and its bridge 3,500, an alley 1,000, twelve more houses along the brook about 12,000. Lights: six on the bridge, four in the alleys, one at the bridgehead, none of them casting shadows.

`tools/shots/intro_shots.sh` now takes 42 stills: four of the drawbridge, three of the alleys, six of the brook and its bridge.

## The look of the lane (first pass: the houses, the ground, the wall, the ends)

The lane outside the abbey gate, on every night. Its plan is unchanged: every door, alley, squint and walking route is where it was, and its navigation was not rebaked.

- **The houses** (`env_house_lane_*.tscn`, nine kinds over the lane's fourteen plots): seven new ones built for the lane (`LANE` in `env_house_timber.py`), exactly 5 or 6 m wide so they stand shoulder to shoulder, and two of the street's. New in them: ground floors of rubble or cut stone with round-headed doors and a step, deep jetties on heavy curved braces, grey-blue and ochre plaster beside the limewash. The lane still hangs each house's lantern (`StreetLanterns`). The curfew still darkens their windows and sends people in at their doors.
- **The ground** (`env_lane_ground`): cobbles down the lane, round both bends and up the two alleys, mud down the cart track, a kennel with water in it. The greybox blocks under it are still what is walked on and what footsteps sound on; they are no longer drawn (`Block.shown`).
- **The precinct wall** has a face of rubble on the lane's side (`env_lane_wall`, laid over the greybox wall, which still stops people): a plinth, a weathered coping, eight buttresses of cut stone. The gate's porch and the three squints are left clear. The porch is cut stone now.
- **The bends** at each end have houses in place of the blocks: four across the lane's end, three along the bend, two at the east corner.
- **The ends** (`env_lane_end.tscn`, four of them: straight on at each end of the lane, and at the far end of each bend): a house built across the street on an archway. The passage under it is dark. Through it the street goes on: house fronts, lit windows, two lanterns, a church tower against the sky. A wall that isn't seen stops him a pace inside the arch. *(Mine: where each looks to, and that all four are the same piece.)*

**What it costs.** A lane house 650 to 1,500 triangles, the ground 7,500, the wall's face 1,600, an end 1,600. Each end has two small lights; nothing else adds a light.

Still greybox: the Cross Keys, the abbey gate's leaves, the far skyline, the people.

`tools/shots/lane_shots.sh` takes 16 stills of the lane on night 1 to `art/_review/lane/`.

## The squints (`Squint`, `game/world/kit/wall_squint.tscn`)

Three, in the precinct wall along the lane: the porter's cell (z −6), the outer court's north (z 6) and south (z 14) *(mine)*. Each is a barred slit a hand's width by a forearm's height (0.18 × 0.5 m) at eye level, splayed to 0.4 m at both faces so an eye at the bars sees a sliver of the other side *(the splay is mine)*.

**Peeking:** E at a squint puts his eye 0.12 m from the bars *(mine)*, from whichever side he's on. The view is held within 25° of straight through; E again and he steps back. A hunter sees him through it only by the usual sight rules, so only up close and with his light.

## Day 1, the tour (`game/chapters/day1/day1.tscn`)

8:00, overcast, flat grey daylight (day 1's `Daylight`: sky 1.4, ambient 1.7, a shadowless sun 0.6 *mine*).

| Beat | What happens |
| --- | --- |
| `Morning` (the start bell) | He wakes in his room at the Keys; with a headache, Agnes calls up the stair about it. Across the lane the gate stands open and Cole keeps it. Crossing into the court he sees fresh sand raked over the ground by the well (`d1_saw_sand`) |
| `Tour` | Thomas, leading the blind Anselm, walks him to six stops and he tries each: the gate's bar, the ledger in his cell, the candle clock (reading it), the bell rope, a door on the round, and a guesthouse bed. By the well he can ask about the sand: "A beast slaughtered for the kitchen", Thomas's first lie (a note). Then the guesthouse key. Thomas leaves; Anselm grips his sleeve: "Don't let them in after the bell," and "The old porter locked the guests in at night" (`d1_anselm_warned`). On a replay (once the game is finished) the tour can be skipped |
| `Nap` | His cell and the cot; he sleeps to dusk: night 1 |

The tour's lines are DRAFT, in `tour_beat.gd`.

## The lane at dusk (`night_base.tscn`, every night)

While the gate stands open at dusk: Hob and Agnes at the Keys' door, Kit selling candles, Gib lighting the lanterns, Mab by the gate, the carter and Margery passing. Each has a dusk conversation (`game/chapters/common/lane/`) with a branch for each night 1 to 6; the first talk of a night carries what the lane says about the night before (who died, whom he turned away, the rules that would have saved them: `docs/systems/abbey.md`, "The rules for saving people"), a later talk the same night a short line and that night's questions. The Keys is open: an ale every night. Night 3 keeps its own Mab, carter and Margery (`game/chapters/night3/dialogue/`).

**The curfew bell** (`Curfew`) at 21:00: the bell, low; the lane's people out in it walk to the nearest house door (at most 30 s *mine*) and go in, while those indoors stay; the Keys shuts its door; the lane's lit windows go dark one by one through the next hour. Then Gib walks the lane between its ends with his lantern, calling the hour from ten to five ("Ten of the clock, and a cold night.") with a voice from where he is. A night that stops him (`silence()`) stops the calls: something has happened. A night picked up from a save after the bell starts with the lane already empty.

## Talk

`docs/systems/dialogue.md` has the new parts: jumps that test flags (`-> point [if flag]`), `[if night=N]`, and `[drink]`. Night 0's conversations are in `game/chapters/night0/dialogue/` (the traveller on the road and at the body cart, the warden at Aldgate, the carter, Mab, Hob, Agnes, Jankin, Walter, Roger, Ralph, Kit, Gib, Margery), all DRAFT.

## Sounds

New placeholders (`tools/build/sfx_placeholders.py`): the wagon rumbling (wheels, axle, hooves), the taproom's talk, the watchman's call. The curfew bell is the abbey bell pitched down.

## Tests and tools

- **Test a scene** (debug builds only; `SceneSelect`, `game/core/ui/menus/scene_select.gd`): the title has a "Test a scene" entry. Pick a chapter, then one of its beats, and the chapter starts at that beat with no card, as a fresh game. From the command line: `-- --from=night0:Arrive`. The beats are read from the chapter's scene, so a new beat is listed as soon as it exists.
  - The beats before the one picked are not played. Each is asked to leave things as it would have (`NightBeat.skipped()`), and the clock is put at the latest hour any of them was due.
  - Night 0's do it properly: from `Arrive` he stands in the lane where the carter sets him down, with the road and the wagon gone; from `Inn`, Mab has sent him on; from `Window`, Agnes has given him the room.
  - Every other beat's `skipped()` does nothing yet, so what an earlier beat would have set up (a flag, a key, a body) may be missing. Add a `skipped()` to a beat when a later one needs what it leaves.
  - `test_scene_select` covers it.

- **`test_prologue`:** from New Game, the ride at its own pace: about two minutes with the cues' lines; the wagon's bed jolting and swaying, and his view with it; talking to the traveller, cut short with no parting line by his own "Whoa" as the cart with four bodies comes by the pulled-in wagon and passes close; paused, the wagon and the clock wait; the stop at Aldgate, the traveller breaking off a talk to greet the warden, and the warden walking up, holding his lantern up to the porter's face and talking to him, and walking back; at the gate the wagon waits for a talk to end, the carter's word, set down by the barred gate with nobody at it, and the wagon driving off down the lane; the knock and Mab; Agnes's room; ales blurring, doubling and wearing off; the curfew emptying the lane but not the Keys; Gib's call; the squint scare seen through the slit and gone; lying down and the killing through the window, the body dragged off, the drunk note; sleep; day 1's headache until noon, the open gate, the sand, the tour's six stops, the lie, the key, Anselm's warning, the nap to night 1's dusk; the tour skipped on a replay.
- **`test_lane`:** Hob's dusk lines on night 2 with the merchant dead and alive; drink's numbers; peeking from the cell (25°, a hunter seeing him only up close with a light); no scare before the bell; the bell, the shut Keys, the lane emptying, the windows going dark, Gib calling and silenced; the scare once; sleep clearing the drink and the headache.
- **`test_flow`** plays night 0 and day 1 in full (`NightPilot.play_night0`, `play_day1`).
- **`tools/m12_shots.sh`:** stills to `art/_review/m12/`.
