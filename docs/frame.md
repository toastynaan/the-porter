# The game's frame (M8)

How the game holds together from the title screen to the last chronicle: chapters, saves, death, menus, settings, the almost-no HUD, the porter's body and his satchel. The rules come from `docs/full-game-run.md` and `docs/mechanics.md`; numbers marked *mine* are starting values to tune.

## Play it

Press F5. The game opens on the title: **New Game**, **Continue** (once there is a save), **Chapters** (once you've finished the game), **How to Play**, **Settings**, **Quit**. Menus take the mouse, the keyboard (arrows and Enter) or a gamepad.

New Game plays the chapters in order, each opened by its card: night 0 (the Cross Keys), day 1 (the tour), then nights 1 to 6. Night 0, day 1 (`docs/prologue.md`) and nights 1 to 3 (`docs/nights.md`) are built in full so far; nights 4 to 6 are stubs that wake you at dusk, let the night go by and send you to your cot (M14 and M15 build them). When night 6 ends, the ending's chronicle closes the game and you're back at the title with Chapters open.

## Chapters

`game/flow/chapters.tres` lists the chapters (`Chapter` resources): an id, the night number, the card's heading and title, the chronicle's paragraph for the card, and the scene. Edit the cards there.

| Chapter | Card | Scene |
| --- | --- | --- |
| Night 0 | The evening before: The Cross Keys | `game/nights/night0.tscn` |
| Day 1 | The first day: The Tour | `game/nights/day1.tscn` |
| Night 1 | The first night: The New Porter | `game/nights/night1.tscn` |
| Night 2 | The second night: The Bell | `game/nights/night2.tscn` |
| Night 3 | The third night: The Oven | `game/nights/night3.tscn` |
| Night 4 | The fourth night: Edwin | `game/nights/night4.tscn` (stub) |
| Night 5 | The fifth night: The Granary | `game/nights/night5.tscn` (stub) |
| Night 6 | The sixth night: The Hunt | `game/nights/night6.tscn` (stub) |

The card is a chronicle page: the heading in small capitals, the title in blackletter, a decorated initial in old-blood red, and a few lines in the chronicler's voice. It goes on when you press E, or by itself after 14 s *(mine)*. The chronicle's dates put night 0 on the eve of Saint Martin, 10 November 1424 *(mine)*, so day 1 is Martinmas and night 6 is the 16th.

**Chapter select** starts any chapter with the state a typical playthrough would have reached: each night's Director holds that state (`start_dose`, `start_flags`, `start_suspicion`, `start_count`), the same state the night uses when it's played on its own.

## Every night shares one scene

`game/nights/night_base.tscn` holds what every night shares: the abbey, the brothers and the lane's people at their places, the duties, lamps and marks, the candle clock, the gate and the bell, the hunter and the demon. Each night inherits it and adds its own `Director` and beats, its conversations (overriding each `Talker`'s `conversation`) and its own things. Night 3 is `night3.tscn`: the base, the Director's eleven beats, the thirteen conversations and the spawn for its quiet save.

## What carries over

Everything the porter has goes on into the next night (`GameState`): Suspicion, the story flags, the keys, the ledger and its notes, the satchel, what each person thinks of him, the rite's count, and how many times he's been caught. Dose halves over a day's sleep (`sleep_through_the_day`). The night's own flags (`night_started`, `gate_taken`, `gate_barred`, `matins_late`, `hungry`, `woke_in_infirmary`) are cleared when the next chapter begins (`GameState.NIGHT_FLAGS`). Flags a night sets for itself are named `n<night>_...`.

## Saves

| Save | When | What loads it |
| --- | --- | --- |
| The bell save, one slot (`user://bell_save.tres`) | At every bell: the start bell as a night loads, and Matins | Continue, and death if there's no newer quiet save |
| The quiet save (`user://bell_save_quiet.tres`) | As a beat marked `quiet` starts: just before each designed chase and set piece. On night 3, just before the crypt | Death only. The next bell clears it |

A save is a snapshot of the whole state (`GameState.snapshot()`) and the name of the beat to pick up at. The night starts again at the beat whose `bell` matches, and the porter at the `bell_spawn` marker of the same name. Captures never go down on a load.

## Being caught, and dying

- **One capture is forgiving:** the first, if it comes on night 1 or 2. You wake in the infirmary with +40 Dose, and the cult has taken everything in your satchel but the keys. The hunters go back to their rounds.
- **Every other capture kills you**, and so does fire, smoke or the Saint (`CaptureFlow.die`). Night 3's chase now kills on the first capture.
- **Your death** is short and first-person. The view turns to the hunter. A cord pulls the head up and back, shaking, as the screen dims; a blade is one quick dark-red flash and the head knocked back. Then the view drops to the floor and rolls over 0.7 s, goes black for 2 s, and the night picks up at the latest save. Hunters kill with a cord by default (`Hunter.weapon`). *(timings mine)*

## Menus

All in the manuscript style: parchment pages, blackletter only for titles, EB Garamond for the rest (`game/ui/manuscript.gd`, `game/ui/menus/`).

- **Pause:** Esc or Start. The night stops (the tree pauses, lines wait) and the mouse is free. Resume, Settings, How to Play, Quit to the Title.
- **Settings** apply at once and are saved when you leave the page (`user://settings.cfg`, the `Settings` autoload): field of view 60–90°, look sensitivity, invert look, volume, crouch held or toggled, subtitle size (small, medium, large), a dark band behind subtitles, less motion (no head bob, almost no lantern sway, half the stumble), guidance (the duty flame) and a faster clock (off by default: 2 minutes an hour instead of 3) *(mine)*.
- **How to Play:** the porter's work in four sentences and the controls.

## The almost-no HUD

- **The centre dot** stays. It no longer turns into a hand.
- **The outline:** whatever E would use gets a thin, pale outline while you look at it within reach (2 m). It's drawn over the thing's meshes as a slightly bigger hull (`game/ui/outline.gdshader`), about 2 render pixels thick at any distance. A `Duty` or a `HidingSpot` names the prop it stands for in its `outline` list; a person you can talk to is outlined whole.
- **The duty glyph:** a small, dim candle flame, about 1° across, over the one person or thing the current duty needs: the nearest wanted `Duty` (or anyone a beat adds to the `glyph_targets` group) within 10 m and in clear view. Never during a chase, while hiding or talking, with the ledger or satchel up, or with guidance off (`game/ui/duty_glyph.gd`).

## The porter's body

| Rule | Value | Source |
| --- | --- | --- |
| Crouch (Ctrl, B) | 0.8 m/s, eyes at 1.0 m, no running, body 1.15 m tall; stands again only with headroom; 0.25 s to crouch or stand | mechanics; body and time *mine* |
| Crouched steps | Heard at 2 m | mechanics |
| Crouched sight | A hunter looks for the top of his back (0.12 m under the eyes) and his chest (0.55 m), so anything 1 m high hides him | mechanics; the points *mine* |
| Lean (Z and C, the bumpers) | The view moves 0.4 m aside and tilts 10° over 0.2 s; not while running; stops 0.15 m short of a wall | mechanics; time and clearance *mine* |
| Leaning sight | A hunter looks for the leaning head where it is, so it shows past a corner | mechanics |
| Look on the right stick | 2.6 rad/s at full tilt, times the sensitivity setting | *mine* |

## The ledger

L holds up the ledger at tonight's guests and duties; L again turns to the porter's notes; L a third time puts it away (`docs/death.md`, "The ledger's notes").

## The satchel

Press I (down on the pad) and the porter holds up his satchel like the ledger: his keys, then each thing he carries with its line. Opening one puts the other away. Items are listed in `game/items/items.gd`: evidence (a mask, hoof soles, a purse, the relic, a page of the book, the book), clean food (an apple, Mab's bread) and something to throw (a stone, a bone, a cup). Each kind of proof is named for the Gate ending.

## The gamepad

| Action | Gamepad |
| --- | --- |
| Move, look | Left stick, right stick |
| Run, crouch | Left stick click, B |
| Lean | LB, RB |
| Use, lock | A, Y |
| Cover the lantern, hold your breath | LT, RT |
| Look back | Right stick click |
| Ledger, satchel, pause | View, D-pad down, Menu |

## The clock

Awake, the candle burns at 3 minutes an in-game hour (it was 4); dozing is unchanged.

## Doors and hunters

Hunters and visitors no longer collide with door leaves. They stop at a shut door and open it, and a locked one turns them back, by their own rule (`Hunter._handle_door`), so a leaf swinging open toward one can't pin him against its jamb. (A full playthrough found a hunter wedged that way at the cellar's west door.)

## Tests and tools

- **`test_flow`:** from the title, New Game through every chapter in order with its card (night 0, day 1 and nights 1 to 3 played in full), carry-over and the night's own flags cleared, the chronicle and the title with Chapters, chapter select, pause, death to the quiet save, and Continue from the bell.
- **`test_body`:** crouch speed, eye height and quiet steps; hidden behind a 1 m stall; lean offset and tilt, the head seen past a corner, leaning into a wall; the right stick.
- **`test_frame`:** the outline in reach and not beyond; the glyph for the current duty only, within 10 m and in view, not in a chase, while talking or hiding, or with guidance off; the satchel and the ledger; the settings; the clock's pace.
- **`test_capture`:** the forgiving capture on night 1 (satchel taken, keys kept), death after it, death at once on night 3, and the quiet save.
- **`test_night3_caught`:** on night 3, caught in the chase is death, and death goes back to the quiet save before the crypt, not to Matins.
- **`tools/m8_shots.sh`:** stills of the title, settings, a chapter card, the outline, the glyph, the satchel, pause, crouching, leaning, a death, the chronicle and chapter select to `art/_review/m8/`.
