# The prologue and the lane (M12)

Night 0 at the Cross Keys and day 1's tour, the squints, and the lane at dusk on every night: its people, what they say, the curfew bell and the watchman. The rules are `docs/mechanics.md`'s ("Night 0 and day 1", "The lane at dusk"); the story is the design doc's. Numbers marked *mine* are starting values to tune.

## Night 0, the Cross Keys (`game/nights/night0.tscn`)

The clock starts at 16:30 and runs at 150 s an hour *(mine)*, so the ride is grey dusk turning dark, and midnight comes about 19 minutes in. Rain until 19:00. The Director's beats:

| Beat | What happens | Ends when |
| --- | --- | --- |
| `Ride` (the start bell) | On rails: the carter's wagon drives itself from the fields past the white chapel, through Aldgate, along the close streets and into the lane, about two minutes. The porter sits at the back, can look about, and turns with the wagon. As it sets off the traveller beside him turns to him and asks where he's bound (`n0_traveller_road`); he can talk to the traveller again at any time. The ride's cues play as the wagon passes them (below). About 15 s in the carter's "Whoa" breaks off any talk, and he pulls in toward the ditch and stops; a cart with a body under sacking creaks by close on his side, and the traveller turns to him about it (`n0_traveller`: who he was, the third pilgrim this month, all bound for the abbey) as the wagon goes on. At Aldgate the wagon stops and the warden looks them over by lantern light. At the gate it waits until nobody's talking; the carter sets him down beside it (`n0_carter`) and drives off down the lane | He's in the lane |
| `Arrive` | The gate is shut and barred, a lantern over it, and Cole isn't at it. He knocks (the `KnockGate` duty); nobody comes; the duty flame goes to Mab, whose first words send him to the Keys (`n0_mab`) | Mab has spoken to him |
| `Inn` | The flame goes to Agnes by the fire; the bed answer gives him the room at the top | `n0_room`, or midnight |
| `Window` | The bed in his room is wanted. Lying down: the cry, and he's at the window over the abbey wall. In the court a man with a lantern is killed by the well by a figure in a black habit, its back to the window, and dragged off toward the cellar. His notes say what he saw, or, if he'd drunk enough to see double, that he isn't sure (`window_killing`, `window_killing_drunk`). At midnight, if he isn't in bed, Agnes sends him up and it plays the same | The body is gone |
| `Sleep` | "Lie down again. Sleep, if you can." | He sleeps: day 1 |

**The ride's cues** (`RideCues` in `night0.tscn`, each a `RideCue`): markers beside the road, counted from the nearest point of the road, so moving one moves its moment. Each can say lines, have someone start a talk with him (`talk`, `talker`), play a sound, set the wagon's pace, stop it for a while, and turn people nearby to watch it. Their lines and talks wait while the porter is talking, and are dropped once the wagon is `keep` metres past; a cue with `cut_in` breaks off his talk instead, and drops the lines still waiting.

| Cue | Where | What |
| --- | --- | --- |
| `Fields` | The start | The traveller turns to him: bound for the city? Pace 2.6 m/s *(mine)* |
| `WhiteChapel` | The chapel, 17 m on | Its bell rings for Vespers; the carter means to be in before the gate shuts |
| `Whoa` | 6 m before the pull-over | The carter's Whoa breaks off any talk (`cut_in`), and he pulls in to let the cart by |
| `Wall` | 12 m short of Aldgate | The city wall, a lantern in the arch. Pace 2 m/s |
| `Aldgate` | The warden, outside the arch | The wagon stops; once nobody's talking, the warden asks in or out, looks at him by lantern light and lets them through; 1 s more, then on at 3.2 m/s |
| `Shutters` | The first houses | Shutters bang closed above as the wagon passes |
| `Doorway` | A woman in a doorway | She watches it go by and crosses herself |
| `Dog` | Farther in | A dog barks behind a door; the traveller says they bar their doors early since the pilgrims |
| `Turn` | The corner into the lane | "Here's your lane, brother." Pace 2.5 m/s |
| `Lane` | Halfway down the lane | The traveller: that wall's your abbey; bar your door at night |

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

The ride's first stretch, from the fields to the foot of the city wall, has its real look. The wall, Aldgate and the streets are still greybox, and so are the people.

- **The sky** (`game/render/sky.gdshader`, driven by `Daylight`): at night the one flat moonlight blue the game has always had; with daylight in it, a low deck of rain cloud drifting over; at dusk a strip of last light along the horizon where the sun went down, pale straw at the rim going to slate, barred with cloud. It is a cold light: purple and rose are kept for the drugged look. Every night's dusk has it, not only this one.
- **The sun sets behind the wagon.** The porter rides facing back, so he watches the day go over the road he came by, and the city ahead is the dark he is carried into. Night 0's dusk is brighter than the abbey's (`Daylight` on `night0.tscn`: sky 1.0, ambient 1.5, sun 0.7 *mine*), and is all but gone by the lane.
- **Distance** (`RoadAir`, `game/world/road/road_air.gd`): out in the fields far things fade into the sky they stand against (depth fog from 14 m, whole at 230 m, taking the sky's own colour *mine*). It thins inside the wall and is gone by the turn into the lane; the abbey's nights don't have it.
- **The ground** (`env_road_fields`): the road two carts wide, with ruts that wander and hold long uneven pools; a grass verge and a wet ditch each side; open fields in ridge and furrow with rain standing in the furrows. All the water lies level and carries the sky, so the last light runs down the ruts.
- **The white chapel** stands 17 m south of the road in a walled yard, limewashed, candles lit inside for Vespers behind leaded glass.
- **Trees** stand bare along the road and out in the fields: elms, oaks, hawthorns, pollard willows by the ditches (35 of them, `tools/build/road_dressing.py`). A band of far woods closes the horizon.
- **Rooks** wheel over the great oak north of the road, and low over the road far back, against the light (`Rooks`).
- **Ground mist** lies thin over the fields near the wagon (a `FogVolume` in `env_road.tscn`).
- **The wagon** is a real cart and a bay horse that walks or trots in step with the ground; the carter's lantern hangs on a stake at the headboard. The cart that passes carries a shape under sacking.
- **The abbey's cat** keeps to the abbey on night 0 (it was following the wagon through the fields).

Fixed with it: the lane's skyline (the city's far roofs, towers and a second city wall, `Skyline` in `street.tscn`) stood across the road in: the wagon drove through four of its blocks, and its far rows stood in the fields outside Aldgate. Everything of it outside the wall, and the two blocks in the roadway, are gone; the city behind the wall keeps its nearer rows and two spires.

`tools/intro_shots.sh` takes stills along the road to `art/_review/intro/` (the wagon stood at set places and hours); `tools/intro_film.sh` films the first half-minute as it plays.

## The squints (`Squint`, `game/world/kit/wall_squint.tscn`)

Three, in the precinct wall along the lane: the porter's cell (z −6), the outer court's north (z 6) and south (z 14) *(mine)*. Each is a barred slit a hand's width by a forearm's height (0.18 × 0.5 m) at eye level, splayed to 0.4 m at both faces so an eye at the bars sees a sliver of the other side *(the splay is mine)*.

**Peeking:** E at a squint puts his eye 0.12 m from the bars *(mine)*, from whichever side he's on. The view is held within 25° of straight through; E again and he steps back. A hunter sees him through it only by the usual sight rules, so only up close and with his light.

## Day 1, the tour (`game/nights/day1.tscn`)

8:00, overcast, flat grey daylight (day 1's `Daylight`: sky 1.4, ambient 1.7, a shadowless sun 0.6 *mine*).

| Beat | What happens |
| --- | --- |
| `Morning` (the start bell) | He wakes in his room at the Keys; with a headache, Agnes calls up the stair about it. Across the lane the gate stands open and Cole keeps it. Crossing into the court he sees fresh sand raked over the ground by the well (`d1_saw_sand`) |
| `Tour` | Thomas, leading the blind Anselm, walks him to six stops and he tries each: the gate's bar, the ledger in his cell, the candle clock (reading it), the bell rope, a door on the round, and a guesthouse bed. By the well he can ask about the sand: "A beast slaughtered for the kitchen", Thomas's first lie (a note). Then the guesthouse key. Thomas leaves; Anselm grips his sleeve: "Don't let them in after the bell," and "The old porter locked the guests in at night" (`d1_anselm_warned`). On a replay (once the game is finished) the tour can be skipped |
| `Nap` | His cell and the cot; he sleeps to dusk: night 1 |

The tour's lines are DRAFT, in `tour_beat.gd`.

## The lane at dusk (`night_base.tscn`, every night)

While the gate stands open at dusk: Hob and Agnes at the Keys' door, Kit selling candles, Gib lighting the lanterns, Mab by the gate, the carter and Margery passing. Each has a dusk conversation (`game/dialogue/lane/`) with a branch for each night 1 to 6; the first talk of a night carries what the lane says about the night before (who died, whom he turned away, the rules that would have saved them: `docs/abbey.md`, "The rules for saving people"), a later talk the same night a short line and that night's questions. The Keys is open: an ale every night. Night 3 keeps its own Mab, carter and Margery (`game/dialogue/night3/`).

**The curfew bell** (`Curfew`) at 21:00: the bell, low; the lane's people out in it walk to the nearest house door (at most 30 s *mine*) and go in, while those indoors stay; the Keys shuts its door; the lane's lit windows go dark one by one through the next hour. Then Gib walks the lane between its ends with his lantern, calling the hour from ten to five ("Ten of the clock, and a cold night.") with a voice from where he is. A night that stops him (`silence()`) stops the calls: something has happened. A night picked up from a save after the bell starts with the lane already empty.

## Talk

`docs/dialogue.md` has the new parts: jumps that test flags (`-> point [if flag]`), `[if night=N]`, and `[drink]`. Night 0's conversations are in `game/dialogue/night0/` (the traveller on the road and at the body cart, the carter, Mab, Hob, Agnes, Jankin, Walter, Roger, Ralph, Kit, Gib, Margery), all DRAFT.

## Sounds

New placeholders (`tools/build/sfx_placeholders.py`): the wagon rumbling (wheels, axle, hooves), the taproom's talk, the watchman's call. The curfew bell is the abbey bell pitched down.

## Tests and tools

- **`test_prologue`:** from New Game, the ride at its own pace: about two minutes with the cues' lines; talking to the traveller, cut short with no parting line as the carter pulls in and the body cart passes close; paused, the wagon and the clock wait; the stop at Aldgate and the warden; at the gate the wagon waits for a talk to end, the carter's word, set down by the barred gate with nobody at it, and the wagon driving off down the lane; the knock and Mab; Agnes's room; ales blurring, doubling and wearing off; the curfew emptying the lane but not the Keys; Gib's call; the squint scare seen through the slit and gone; lying down and the killing through the window, the body dragged off, the drunk note; sleep; day 1's headache until noon, the open gate, the sand, the tour's six stops, the lie, the key, Anselm's warning, the nap to night 1's dusk; the tour skipped on a replay.
- **`test_lane`:** Hob's dusk lines on night 2 with the merchant dead and alive; drink's numbers; peeking from the cell (25°, a hunter seeing him only up close with a light); no scare before the bell; the bell, the shut Keys, the lane emptying, the windows going dark, Gib calling and silenced; the scare once; sleep clearing the drink and the headache.
- **`test_flow`** plays night 0 and day 1 in full (`NightPilot.play_night0`, `play_day1`).
- **`tools/m12_shots.sh`:** stills to `art/_review/m12/`.
