# The drug and the dark (M10)

What the drug does to the porter's senses, the scares between chases, the abbey cat, clean food, and the things nothing explains. The rules come from the design doc ("The two layers", "Effect tiers"), `docs/systems/mechanics.md` ("The drug, and food", "The minimal HUD") and `docs/log/full-game-run.md` ("The drug", "Scares between chases", "The cat"). Numbers marked *mine* are starting values to tune.

## Dose changes what he sees and hears, never his body

He walks, runs and turns the same at Dose 100 as at 0. The staring stumble is fear and the henbane, not Dose (`StareMeter`), as before.

## The tiers (`Hallucinations`, in `night_base.tscn`)

Every so often, while he's about, one event the tier allows plays; the tiers stack. None plays during a chase, while he talks, dozes or reads, or while a menu or card is up. Nothing an event shows is left behind.

| Dose | Events | Always on |
| --- | --- | --- |
| Below 25 | None | |
| 25+ (his ears) | A whisper at his shoulder; three steps behind him; his name called from 10–15 m ("Someone calls your name", in Edwin's voice once Edwin is dead) | The lantern flame bends toward the nearest uncanny thing (the demon, a body, the dead) within 9 m; reverb grows |
| 50+ (his eyes) | A tall shape at the edge of his view (48° off centre, 7–12 m), gone the moment he looks within 22° of it or after 2.5 s; a face in the grain of the nearest wooden door he isn't looking at, gone once he has stared at it 1.5 s | Carved saints turn their heads to follow him, but only while he isn't looking (`Carving`, six in the abbey) |
| 75+ (and lies) | Hooves running at him from behind that stop just short; a death in front of him that never happened (a fake `DeathScene`: no body, no blood, no soul once he looks away) | The walls breathe (the whole image swells and settles); the dead stand in the choir at Matins (`DeadInChoir`) |

Gaps between events *(mine)*: 40–70 s at 25+, 30–55 s at 50+, 20–40 s at 75+. Flame bend: from Dose 25, full at 60, up to 0.6 rad *(mine)*. Breathing: from 75, 0.6% of the screen at 100 *(mine)*. Reverb: from 25, 40% wet at 100 *(mine)*. The curves are in `game/core/render/dose_look.tres`.

## The HUD lies once (`FalseDoor`)

On night 5 or 6, and only at Dose 75+, a door's outline shows in the blank wall of the cloister's west walk (between the granary's door and the stores'). The slab is the wall's own stone, so only the outline shows. Use it and it swings open on more stone, and is gone. It happens once in the game (`hud_lie_told`). Everywhere else the outline is true.

## The incense from night 4 (`choir_beat.gd`)

On nights 1–3 the incense is unavoidable, as before: +25, and Dose held at 50 or more for the night. From night 4 it comes a breath at a time over the 8 s it burns, and where he stands decides how much:

| Where | Dose |
| --- | --- |
| His stall (`Marks/PorterStall`, within 1.3 m *mine*) | The whole +25 |
| By the choir's west door (`Marks/ChoirWestDoor`, within 2.2 m *mine*) | About a third |
| Anywhere, holding his breath | None |

Out of his stall while the office is sung, if a brother in the choir can see him (the hunters' sight rules): Suspicion +10, once a night.

## Clean food

- **Windfall apples** (`Pickup`, under `Windfalls`): nine places under the orchard trees, and a different third of them each night (three).
- **Mab's bread:** give her alms and she gives you a heel of bread from a baker in Fenchurch Street (her conversation's `[item mab_bread]`).
- **Eating:** hungry, an apple is eaten as you pick it up; otherwise it goes in the satchel, and with the satchel up E eats clean food while you're hungry. Clean food ends hunger for the night and adds no Dose.

Conversations can now give things and change things: `[item id]` puts something in the satchel, `[note clue]` writes a clue, `[trust who amount]` changes what someone thinks of him (`docs/systems/dialogue.md`).

## Ranulf's remedy

At supper (night 3 now) Ranulf offers the remedy and Thomas, beside you, warns you off it. Taking it is Dose +15. Refusing it tips Ranulf off (Suspicion +5) and pleases Thomas (trust +5). DRAFT lines:

> **Ranulf:** You keep rubbing your eyes, brother. The new ones always get the headaches. A little of this in your ale, and you'll sleep.
> **Thomas:** (Quietly, so only you hear.) Not his physic. Not that one. Trust me.

## Scares between chases (`Scares`)

A night's round beats call these where the night wants them (M13 to M15):
- **Steps above:** felt (or hooves) crossing the floor over his head; only under a roof.
- **A light ahead goes out:** the nearest candle ahead of him, 3–16 m off and in view, gutters and goes out. Never a duty's lamp, a lamp lighting the way, or the crypt's count.
- **Jump scares,** at most one a night: a body drops on a rope 1.6 m in front of him, or a face at the gate's grille. Each is gone once he looks away.

## The abbey cat (`Cat`, `game/people/cat.tscn`)

It follows the porter, keeping 1.8–3.2 m off, trotting to catch up when he's far. Every 35–70 s *(mine)* it stops and stares into the dark for 4 s: at a man standing there if a hunter is within 10 m, at nothing otherwise. When the animals go quiet before the demon, it hisses and bolts 14 m away from him and is gone until the quiet is over.

## The three things nothing explains

- **The knock with no one there** (night 1): `knock_no_one_beat.gd` knocks at the gate at its hour, at any Dose, until he comes to the grille; the lane is empty both ways, and it goes in his notes. Night 1 places it in the small hours (M13).
- **The candle that lights itself** (night 5): `SelfLitCandle`, by the crypt's ring; it lights once he has looked at it from close for a second, at any Dose.
- **The shape through the squint** (night 0): the Hungry Saint's figure (`game/characters/chr_saint.tscn`: about 2.6 m, too thin, bent forward, no horns, unshaded black, a gap in the light) stands inside the south squint once (`docs/places/prologue.md`, "The squint scare").

## Sounds

New placeholders (`tools/build/sfx_placeholders.py`): three whispers, his name called, a sting, a body dropping on a rope, the cat's hiss, a bite of an apple. The face in the grain is a generated texture (`tools/build/tex_face_grain.py`, `art/tex/tex_face_grain.png`).

## Tests and tools

- **`test_drug`:** the tiers; nothing at Dose 0, an ears event at 30; his name and Edwin's voice; the shape at the edge gone when looked at; the face in the grain gone when stared at; a fake death leaving no body, blood or soul; hooves, whispers, steps; carvings turning only unseen; the dead in the choir at 80 and gone at 40; the flame bending toward the demon; the walls breathing and the reverb; the same walk and look at 95; the HUD's lie only on night 5 at 75+, outlined in reach, opening on stone; the candle lighting itself.
- **`test_incense`:** night 4's Matins: the whole dose in his stall, a third by the west door, none holding his breath; seen out of his stall, +10 once.
- **`test_dark`:** the cat following, staring at a man, bolting when the animals go quiet and coming back; steps above only under a roof; a light ahead going out; one jump scare a night; three apples a night; an apple ending hunger, or kept and eaten from the satchel; Mab's bread for alms.
- **`tools/m10_shots.sh`:** stills to `art/_review/m10/`: one view of Matins at Dose 0, 25, 50, 75 and 100, and each event.
