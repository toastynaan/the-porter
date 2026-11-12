# Hunting, hiding and the demon (M3)

How the hunter, hiding spots, captures and the demon work in the greybox, and every number you can tune. The rules come from the design doc ("Suspicion, chases and hiding", "The demon: Slenderman first, men later"). Numbers marked *default* came from the M2 report and you accepted them. Numbers marked *mine* are placeholders I picked to make the systems work; change any of them.

## Play it

To play night 3, see `docs/night3.md`. To try the hunter and the demon on their own, run `game/dev/encounters/hunt_demo.tscn` (F6 in the editor): the abbey with one hunter on a round of the cloister, church and graveyard, plus the demon stalking you.

| Key | Does |
| --- | --- |
| Mouse, WASD, Shift | Look, walk, run |
| E | Use a door, hide in a spot, climb out |
| R | Lock or unlock a door you hold the key for (guesthouse, charnel house) |
| F / right mouse | Cover the lantern |
| Space | Hold your breath |
| Q | Look back over your shoulder |
| `[` `]` | Dose down or up by 25 (debug) |
| H | Hungry or fed (debug) |
| K | The hunter comes for you now (debug) |
| J | The demon appears now, somewhere you aren't looking (debug) |

## The hunter

`game/hunting/hunter.tscn`. The script is `hunter.gd` (states and movement), with `hunter_senses.gd` (sight and hearing) and `hunter_audio.gd` (his sounds) as child nodes.

| State | What he does |
| --- | --- |
| Patrol | Walks his route's markers in order, waiting at each one (a marker's `wait` metadata, default 3 s), and hums the chant. He opens doors and shuts them behind him |
| Investigate | Walks to a noise or a half-seen glimpse and looks around for 4 s |
| Chase | Runs at you. When he loses sight of you he goes to where he last saw or heard you |
| Search | From Suspicion 30, or for the night's designed chase (`always_search`), he checks the 2 hiding spots nearest where he lost you. A spot used twice tonight is checked first. Below 30 he only looks around |
| Capture | He reaches you |

| Rule | Value | Source |
| --- | --- | --- |
| Sight, lantern uncovered or in candlelight | 20 m, 100° cone | default |
| Sight, in the dark | 2 m | default |
| Time to notice you | 0.3 s close, 1.5 s at 20 m; instant while chasing | mine |
| Hears running, walking, a door | 12 m, 4 m, 10 m; half through a wall | default |
| Hears a gasp, a key turning, breathing | 10 m, 4 m, 2 m | mine |
| A hiding spot creaking (noise × 10 m) | e.g. the oven 6 m | mine |
| Speeds: patrol, investigate, search, chase | 1.2, 1.4, 2.0, 4.0 m/s | default (patrol, chase) |
| On stairs | 70% | default |
| Winded | after 20 s sprinting, stops 4 s and listens (hearing doubled) | default |
| Keeps tracking you after losing sight | 1.5 s | mine |
| Takes hold of you | within 1 m, in clear view | mine |
| Checking a spot | 2.5 s; only spots within 25 m | mine |
| At a locked door | tries it, listens 3 s, gives up | mine |

He can't follow through the mill wheel gap or the latrine chute, and he has no keys. Door leaves don't stop him physically: he stops at a shut one and opens it, and a locked one turns him back, by his own rule (since M8).

Since M11 (`docs/abbey.md`): how many hunters go out on a round, and how they hunt, follows Suspicion's bands (`Hunt`); each has a `wearer`, calls the porter's name from night 4 (`HunterVoice`), can lose his mask (`unmask()`), comes to look at a thrown stone, hears half as far in rain, sees 4 m in fog (but sees a lantern's glow further) and follows prints in snow.

He carries a shuttered lantern on his back (*default*; its 3.5 m light is *mine*), so he shows as a dark shape against its glow: the doc's sober render of the demon, "a lantern behind it". The first time your lantern light touches him, he freezes for 0.5 s (*default*).

## Hiding

`game/hunting/hiding_spot.gd`. Look at the spot and press E. The camera drops to the spot's `View` marker, look is limited to about ±50°, and the lantern goes under the cloak. Press E again to climb out.

When a hunter checks a spot you're in:
- **Breathing:** he finds you.
- **Holding your breath:** he finds you with the spot's `check_chance`.

A gasp or a breath he hears from inside a spot gives that spot away at any Suspicion.

| Spot | Area | Noise | Check chance |
| --- | --- | --- | --- |
| Oven | Bakehouse | 0.6 | 0.3 (default) |
| Under the cot | Porter's cell | 0.2 | 0.5 |
| Behind the woodpile | Outer court | 0.5 | 0.7 |
| Under the altar cloth | Church | 0.1 | 0.4 |
| The open tomb | Nave | 0.4 | 0.35 |
| Behind the piers (2) | Cloister | 0 | 0.9 (default) |
| Under the beds (3) | Dormitory | 0.2 | 0.6 (default) |
| Grain sacks | Granary | 0.3 | 0.6 |
| In the bone pile | Charnel house | 0.7 | 0.35 |
| Under a sick bed | Infirmary | 0.2 | 0.6 |

The spots I didn't take from the report are *mine*.

## Your body

| Rule | Value | Source |
| --- | --- | --- |
| Breath meter | 12 s, 8 s hungry; refills in 6 s; a gasp when it runs out, then 2 s before you can hold again | default (12/8), mine (rest) |
| Stamina | 25 s of running; refills in 15 s, or 22.5 s hungry; once empty, no running until it's back to 30% | default (25/15/hungry), mine (30%) |
| Hunger | A hand tremor on the lantern, a shorter breath, slower recovery. It's the `hungry` flag, which supper will set in M4 | doc |

Nothing is shown on screen. Breathing turns to panting as stamina runs down. In a hiding spot your breathing is loud and your heart beats.

## Captures

`game/core/flow/capture_flow.gd`, in `main.tscn`.

Since M8 (`docs/frame.md`, "Being caught, and dying"):
- **The one forgiving capture:** the first, if it comes on night 1 or 2. You black out and wake in the infirmary (the `WakePoint` marker) with +40 Dose eased in, and the cult has taken your satchel but not your keys. The hunters go back to their rounds.
- **Every other capture kills you:** a second on nights 1–2, and any from night 3 on. The view drops and goes dark, and the night picks up at the latest save, quiet or bell, with Dose and the rest as they were then.
- **Captures never go back down**, so after a restart every capture kills.
- **Saves:** a level rings the `start` bell when it loads; night 3 also saves at the Matins bell, and quietly just before the crypt.

## The demon

`game/demon/stalker.tscn` uses the Stalking phase by default (`phase` export).

- **It never animates in view.** It is placed only while off screen, and it's gone once you've seen it and looked away.
- **Lantern light freezes it.** It can't leave while your lantern light is on it.
- **The animals go quiet first.** Rooks, rats and the cat stop 5 s before each appearance.
- **Closer each time (Stalking).** Each appearance is at most 0.7 × the last distance.
- **Then it's behind you.** When the next one would be under 6 m, it appears 3.5 m behind you in full silence (the wind stops too). Turn away from it, out of your own lantern light, and the hunter takes over the chase.
- **Glimpses** (`phase = GLIMPSES`, nights 1–2) stay 14–35 m away and never close in.

In this greybox it doesn't appear while the hunter is awake within 25 m or busy, so you never see two at once. It starts again once his chase is over.

**Staring at it:**
- Keeping it within 20° of the centre of view fills a stare meter over 3 s.
- As the meter fills, the screen edges warp, the view narrows by 5°, your ears ring and the lantern gutters.
- Held full for 2 s, you lose your footing for 1.5 s.

These are defaults.

**How it renders by Dose (`game/demon/demon_costume.gd`):**
- **Below 50:** a man of 1.75 m in a pale mask, with 60 cm of antlers on ram's horns.
- **50–74:** it grows about 15% taller, the eyes glow ember from 50 to 58, and the mask sinks into the hood.
- **75 and up:** the arms and fingers stretch, by 40% (*mine*).

The greybox figure is built from primitives in a script. The rigged model replaces it in M5.

## Tests and tools

- `tools/check.sh` runs the suites:
  - `test_hiding`: the oven, the breath meter, stamina, keys
  - `test_hunter`: sight, hearing, chase, winded, doors, locked out, search order, checks, the mill wheel
  - `test_capture`: the infirmary, death, restart
  - `test_stalker`: off screen, silence, closer, stare, behind you, hand-over
- `tools/chase_capture.sh` records the two scripted chase takes to `art/_review/m3/`.
- `tools/m3_shots.sh` renders the hiding views and the demon by Dose.
