# Playing The Porter

How to play the whole game from the title to an ending, what to try, and where each system is written down. Everything you see and hear is a placeholder (grey figures, generated sounds), and every line is a DRAFT for you to rewrite.

## Start

- Open the project in Godot 4.8 and press **F5**. The title screen: New Game, Continue (after a save), Chapters (after you finish once), How to Play, Settings, Quit.
- **New Game** plays the eight chapters in order, each opened by its chronicle card: night 0, day 1, nights 1 to 6. A whole run is about 4 to 5 hours.
- **Chapters** (after you've finished once) starts any chapter with the state a typical playthrough would have reached.
- To play one chapter from the editor, open its scene in `game/nights/` and press **F6**.

## Controls

| Action | Keyboard and mouse | Gamepad |
| --- | --- | --- |
| Move, look | WASD, mouse | Left stick, right stick |
| Run, crouch | Shift, Ctrl | Left stick click, B |
| Lean | Z, C | LB, RB |
| Use (talk, doors, duties, peek at a squint, pick up, throw) | E or left click | A |
| Lock a door (with its key) | R | Y |
| Cover the lantern, hold your breath | F or right click, Space | LT, RT |
| Look back | Q | right stick click |
| Ledger (L again: your notes), satchel | L, I | View, D-pad down |
| Answers | 1–4, or arrows (or the wheel) and E | D-pad and A |
| Pause | Esc | Menu |

## What a night asks of you

Each night from 1 to 5 runs from dusk to Lauds on the candle clock in your cell (3 minutes an in-game hour): talk to the brothers and the lane while the light lasts, supper at the bell, take the gate from Cole, bar it, open the ledger, answer the knocks (admit, turn away, or send for the prior), ring Matins and count the brothers, walk the round, keep watch (doze on the bench), give Cole the gate at Lauds, sleep. A faint flame marks what the current duty needs; things you can use get a thin outline. From night 3 each night breaks the routine.

## Things to try

- **Night 0:** drink three ales and see the killing from the window through the double image; walk the lane alone after nine and look into the south squint.
- **Night 1:** lock the guesthouse once the merchant is in bed (R at its door), or don't, and see who's in the fishpond at Lauds.
- **Night 2:** at dusk ask Hob to keep Jankin in; turn the sailor away after the bell, or let him in, and watch the lane toward midnight through the grille.
- **Night 3:** look at the bread before you eat it; go down to the crypt light; hide in the oven and hold your breath.
- **Night 4:** warn the pilgrim at his bed to bar his door; get close enough to a hunter in the fog to see his face.
- **Night 5:** reach Thomas, or Simon. Let Roger's sergeant wait inside the gate, or don't. Show the prior two kinds of proof at dawn, or six notes.
- **Night 6:** drink the wine or refuse it; open the gate (for whom?); take the proof from the crypt passage; take the book or free the victim before Matins; or burn it all.
- **Throughout:** the lane's people at dusk tell you what would have saved last night's dead. Your ledger's second page (L, L) holds every clue you've noticed. Ring the bell out of hours and see who comes.

## Routes to the seven endings

Each is decided on night 6 (`docs/night6.md`); `test_endings` plays a route to each and checks its chronicle.

| Ending | One way to get it |
| --- | --- |
| The New Faith | Drink Thomas's wine at dusk, then get caught by a hunter |
| The Demon | Arrive at night 6 drugged (eat the bread, take the remedy, drink the wine: Dose 75+), and when "the demon" corners you with a light after 22:30, strike it |
| The Rising | Let at least two of the five preventable deaths happen (leave the guesthouse unlocked on night 1, turn the sailor away after the bell on night 2, don't warn the night-4 guest, save Thomas, leave the sergeant outside), so the crypt holds eight candles by night 6, and don't stop the rite: the last soul makes nine |
| The Fire | Hold your lantern to the granary's sacks and to the crypt's hangings while the book is still on its stand, then get out |
| The Gate | Make sure the merchant or Roger's sergeant died (so Roger comes), take two kinds of proof from the crypt passage (a mask and a purse, say), and open the gate for him |
| The Witness | Shelter Joan on night 2 or 5 (or let Mab in), let her in when she knocks on night 6, and go out under the wall by the mill race's east end with her behind you |
| The Broken Rite | Take the book from the crypt (or free the victim) before Matins, then get out any other way or hold out to Lauds |

The whole run takes about 4 hours at the clock's normal pace: night 0 about 19 minutes, day 1 about 8, nights 1 to 5 about 30 to 40 each (dozing on the bench skips the waits), night 6 as long as you last. The faster clock setting cuts the nights by a third.

## Where things are written down

| Topic | Doc |
| --- | --- |
| The run's spec, Progress, and decisions to review | `docs/full-game-run.md` |
| Every rule and number | `docs/mechanics.md` (its "Decisions to review" lists the numbers I chose) |
| The frame: chapters, saves, death, menus, settings, HUD | `docs/frame.md` |
| Deaths, bodies, the rite, the notes | `docs/death.md` |
| The drug and the dark | `docs/drug.md` |
| Hunters and the abbey's people | `docs/abbey.md` |
| Night 0, day 1, the lane | `docs/prologue.md` |
| Nights 1 to 5 | `docs/nights.md`, `docs/night3.md` |
| Night 6 and the endings | `docs/night6.md` |
| Writing conversations | `docs/dialogue.md` |
| Scenes, props, characters | `docs/assets.md`, `docs/abbey-layout.md` |

## Checks and stills

- `tools/check.sh` runs every test (about 20 minutes; `test_flow` plays the whole game from New Game).
- `tools/m<N>_shots.sh` renders each milestone's stills to `art/_review/m<N>/`.
- `tools/intro_shots.sh` and `tools/intro_film.sh` render stills and a short film of the road in; `tools/build.sh` rebuilds the real models (`docs/assets.md`).
