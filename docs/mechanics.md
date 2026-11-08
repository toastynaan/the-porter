# Mechanics (the full-game run)

Nov 8, 2026 · from the mechanics grilling with @Pahul

How everything the player does works, for the run in `docs/full-game-run.md`. The story spec says *what happens*; this file says *how it plays*. Numbers marked *mine* are starting values to tune in playtest. Mechanics already built and unchanged (walking, running, stamina, breath, hiding spots, the hunter's five states, the gate reading, the candle clock, dozing, conversations) are described in `docs/hunting.md`, `docs/night3.md` and `docs/dialogue.md`; this file covers what's new and what changes.

## Controls

| Action | Keyboard and mouse | Gamepad | Notes |
| --- | --- | --- | --- |
| Move, look | WASD, mouse | Left stick, right stick | |
| Run | Shift (hold) | Left stick click | |
| Crouch | Ctrl (hold) | B / Circle | **New.** Hold by default; a setting makes it a toggle |
| Lean left, right | Z, C (hold) | LB, RB (hold) | **New** |
| Use, talk, pick up, throw | E, left click | A / Cross | Throw: E while holding something, looking at nothing usable |
| Lock or unlock | R | Y / Triangle | |
| Cover the lantern | F, right click | LT | |
| Hold your breath | Space (hold) | RT | |
| Look back | Q (hold) | Right stick click | |
| Ledger | L | View / Select | Two pages now: guests and duties, then notes |
| Satchel | I | D-pad down | **New** |
| Pause | Esc | Menu / Start | **New:** opens the pause menu (it frees the mouse now) |

Menus work with either. The gamepad bindings are *mine*.

## Your body

| Rule | Value | Source |
| --- | --- | --- |
| Walk, run | 1.4, 4.0 m/s | Look and Feel |
| Crouch | 0.8 m/s, eyes at 1.0 m; you can't run while crouched | *mine* |
| Crouched steps | Heard at half the walking range (2 m); hidden behind anything 1 m high (stalls, tombs, the well) | *mine* |
| Lean | The view moves 0.4 m to the side and tilts 10°. Hunters can see your head while you lean | *mine* |
| Stamina, breath | As built (25 s, 12 s; hungry 22.5 s recovery, 8 s breath) | M2 defaults |
| Dose | Changes only what you see and hear, never how you move or turn | Grilling |

Staring at the demon still makes you lose your footing (the doc's stare rule). That comes from fear and the henbane, not from Dose controls.

## The lantern

- **Covering** it works as built: covered, it reaches 1 m, and the hunters can't see it.
- **Wind** can put it out. In strong draughts it gutters for 1.5 s as a warning, then goes out if you stay. Strong draughts are open outer doors, the tower stair, and outdoors in the rain on nights 1–2. Covering it protects it from the wind. *(gutter time mine)*
- **Out** means dark, apart from moonlight and other people's lights. Relight it at any lit candle or lamp (hold E for 1.5 s). *(mine)*
- At high Dose the flame bends toward things (the doc), as part of the drug, not a control.

## Your hands

**Outlines.** Whatever E would use gets a thin, pale outline while you look at it within reach (2 m). The centre dot stays. This replaces the dot turning into a hand.

**The satchel** (I) is held up like the ledger. You see what you carry in his hands, with a line for each. Items are keys, evidence (a mask, hoof soles, a purse, the pig's bone, pages of the book), clean food, and the stone or bone you're holding. There's no grid and no weight limit; there's little to carry. If you're caught, the cult takes everything but the keys. (A capture can only happen on nights 1–2, so mostly it's moot.)

**Throwing.**
- Pick up a stone, bone or cup with E. You hold one at a time, in your right hand; the lantern is in the left.
- Throw it with E while looking at nothing usable. It flies about 8 m.
- Where it lands makes a noise the hunter goes to look at (his Investigate state):

| Lands on | Heard within | Source |
| --- | --- | --- |
| Stone | 10 m | *mine* |
| Wood | 8 m | *mine* |
| Mud or grass | 4 m | *mine* |

There are a few throwables in every area, more where people work. They don't come back; the cult tidies them by the next night.

**Keys** work as built: R locks the doors you hold keys for, and a locked door stops a hunter.

**Wedging a door.** Any door can be wedged shut with a stool or bench within 2 m.
- It takes 2 s and makes noise heard within 8 m.
- It holds a hunter for 8 s, then he forces it with a loud crash and the wedge is gone.
- The Hungry Saint ignores wedges.

*(timings mine)*

**Giving** happens in conversations: alms to Mab, clean food to someone hungry, a candle to a guest. Each adds a little trust.

## Being hunted

**Captures** follow one rule for the whole game. A capture on night 1 or 2 wakes you in the infirmary, once. Every other capture kills you:
- a second capture on nights 1–2;
- any capture from night 3 on.

Night 3's rescue by Thomas stays: it's a near miss, not a capture. *This changes what's built: on night 3 the first capture now kills.*

**Your death.** It's short and first-person: the hunter is on you, a blade or a cord, the view drops and goes dark. Then you go back to the last bell with everything as it was then.

**Suspicion** (hidden, 0–100, it only goes up) has the doc's four bands:

| Suspicion | Hunting | Source |
| --- | --- | --- |
| 0–29 | One costumed cultist on a patrol route; he chases what he sees but doesn't search | doc |
| 30–59 | He searches where he last saw you and checks the two hiding spots nearest it (as built) | doc |
| 60–84 | Two hunters. They lock doors behind you (you need your keys or another way round), and one waits at the gatehouse | doc |
| 85+ | Night 6's rules come early: the whole cult hunts you that night | doc |

**Hunters talk.** From night 4 they call your name in a voice you know, shown as a subtitle with the direction (*"Alric..." (behind you, Osric)*). Drugged, the name is missing and it's just "A voice". Before night 4 they're silent. *(the subtitle form is mine)*

**Between chases** (the run's spec): you hear and glimpse the hunter on every round, a jump scare comes at most once a night, and the cat runs before he comes.

**The bell rope** is a gamble. Ring it any time but Matins and the whole abbey comes to the tower:
- The chase breaks off, because the hunter can't be seen in costume by the abbey.
- Whoever reaches you first decides what happens, and that depends on who is nearest and who trusts you:
  - a cultist takes you, which is a capture;
  - the prior questions you;
  - a friend (Edwin; Simon, if you saved him) walks you somewhere safe.
- Each off-hours ring is Suspicion +10. *(mine)*

**Hiding** works as built. Crouching lets you reach low spots without a cut to the hiding view (under beds, behind the tomb). Companions hide with you (see "People").

## The minimal HUD

There are only two things on screen, plus subtitles and the dot.

- **The outline**, as described under "Your hands".
- **The duty glyph:** a small, dim mark (a candle flame, about 1° across) over the one person or thing the current duty needs, seen within 10 m. It never shows during a chase, while hiding, or while talking. The lit way to each duty stays.
- **At Dose 75+ the HUD can lie, a little.** At most once every 10 minutes it outlines something that isn't there: a door in a blank wall, a hand reaching from under a bed. Using it does nothing. *(mine)*

## Time and duties

- **The candle waits** at a duty's mark until you do it (as built), so nothing is skipped. The time you take after the mark counts as late.
- **Lateness** (*mine*):

| How late | What happens |
| --- | --- |
| Up to 15 minutes | On time |
| 15 to 45 minutes | Noticed: Suspicion +5, and a remark at dawn |
| More than 45 minutes | Someone comes to fetch you: the prior, or Cole at dusk. If he finds you somewhere you shouldn't be, that counts too (see "Being seen") |

- **Knocks** go on until you answer them (as built). A visitor never gives up.
- **Dozing** works as built: on the gate bench, once you have the gate and no duty is wanted.

## The gate

Reading, the ledger, and admitting, refusing or sending for the prior all work as built, plus:

- **Lies.** A visitor's story is in their greeting and answers. Some details you can notice contradict it: a "pilgrim" with no badge and soft hands, a "sailor" with no tar on his hands. Noticing one adds a line, *"(Something doesn't fit: no pilgrim's badge.)"*, and a ledger note. What you do with it is up to you. Each visitor's lies are written into their Visitor resource.
- **Talking at the grille.** Each knock is a conversation (as built): their greeting stays up over the three choices and "Walk away". Some visitors have one question you can ask first.

## Investigation

**The ledger's notes** are a second page. The porter writes a short note himself whenever:
- he finds something ("Rope marks on the merchant's wrists");
- notices a lie;
- hears something that matters ("Thomas says he saw Brother Simon out after Compline");
- finds someone missing ("Edwin was not at Matins").

There's no quest log and no arrows; the notes are in his hand, oldest first, a page a night. The cult can tear out guest pages, but not notes. *(that last rule is mine)*

**Bodies** (the run's spec): look at a body for a moment to find it, and a note is written. Report it in conversation (to Thomas or the prior), or don't. Some bodies are moved; blood stays until it's cleaned.

**Accusations** happen in conversations. Some answers name a suspicion ("I saw Brother Simon scrubbing blood"). Who you tell and about whom changes Suspicion, trust, and what people do. Tell Thomas and he uses it. Telling the prior anything is +10 (Ranulf overhears).

**Being seen** somewhere you shouldn't be:
- *Where that is:* the crypt at any time, the granary and stores after Compline, the dormitory floor at night, near a body.
- *Who can see you:* any brother on his routine, by the hunters' sight rules (lantern light, distance, his view).
- *What it costs:* Suspicion +10, once per place per night. He tells someone, and it comes up at dawn.

## People

**Trust.**
- Each person has a hidden trust in you, from −100 to 100. *(mine)*
- *Starting values:* Thomas 40, Edwin 50, Anselm 20, Osric 20, Ranulf 0, Mab 0, Joan 0, Prior Hugh −20, the choir brothers 10.
- *What moves it:*

| Cause | Change |
| --- | --- |
| Answers | ±5 to 15 |
| Gifts | +5 to 10 |
| A warning they heed | +10 |
| Being seen somewhere wrong, by them | −10 |
| Turning away someone they vouched for | −10 |

- *What it decides:*
  - What people tell you: some lines need 30 or more.
  - Whether they come to help when the bell rings: 40 or more.
  - Whether Mab or Joan will flee with you: 30 or more.
  - Who Thomas points you at.

**Warnings.** Some conversations let you warn someone: a guest to bar the guesthouse door or leave at first light, a brother to stay in the dormitory. A warning given before that night's death saves them, and the count is short by one. If the cult hears of it, Suspicion +15. They hear of it if Ranulf is within earshot when you say it, or if the person you warned trusts Thomas more than you and tells him. *(mine)*

**Companions.**
- Ask someone to follow ("Follow me" / "Wait here", in conversation or with a quick E).
- *Following:* they keep 1.8 m behind (as guests do now) and open doors.
- *Hiding:* when you hide, they hide in the nearest free spot within 6 m, or crouch in shadow.
- *Caught:* a companion who is caught is gone, and may be one of the night's deaths.
- *Who:* guests to their beds (as built), Mab or Joan on night 6, and Simon on nights 5–6 if you saved him.

**Routines.** Each brother walks his places by the hour, and lit windows show who's up. They walk in view; only the demon tricks still happen out of sight. A routine that breaks is a clue, and gets a ledger note if you notice it.

## The drug, and food

- **Senses only:** Dose never changes control. Its tiers and fake events are in the run's spec.
- **Incense from night 4.** The smoke is thickest at the altar:
  - In your stall: full dose.
  - By the choir's west door: about a third. *(mine)*
  - Holding your breath: nothing.
  - The catch: if a brother can see you out of your stall while the office is sung, Suspicion +10. *(mine)*
- **Clean food** ends hunger for the night, Dose-free:
  - windfall apples under the orchard trees, two or three a night;
  - a heel of Mab's bread when you give her alms (her trust 20 or more);
  - scraps in the kitchen while Osric's routine has him out (after nine).

## Night 6

**The Hungry Saint.**
- Nothing stops it: doors, locks, wedges and darkness don't, and it cuts through the hidden passages. It's slow, so you can stay ahead, but it never stops coming.
- It always knows roughly where you are and walks toward you, finding its path again every few seconds.
- Its touch is death.
- Its strength depends on the count:

| Count | It | Source |
| --- | --- | --- |
| 7–8 | Stays in the crypt; going down there is the danger | Run spec |
| 9 | Walks the abbey at 0.9 m/s | *mine* |
| 10–11 | Walks at 1.2 m/s and kills any cultist it meets | *mine* |

- Silence comes 25 m before it: the animals and the wind stop. Your lantern dims within 8 m. *(mine)*

**Proof.** The Gate ending needs two different kinds of the four: a costume (mask or hoof soles), a dead pilgrim's purse, the pig's bone, or the cult's book. They're in the crypt passage on night 6, and they go in the satchel. Die and you go back to the last bell with the satchel as it was then.

**Stopping the rite.** Before the Matins mark, either:
- free the victim (hold E on his cords for 3 s *(mine)*), or
- take the book from the crypt altar (E).

Both are in the crypt, so you must go down while the cult and the Saint are about.

**Fire.**
- Hold the lantern to a marked spot (the granary sacks, the crypt hangings) for 2 s. *(mine)*
- It spreads along set paths at about 1 m/s. *(mine)*
- *Smoke:* you can see 3 m in it, and you choke on it. Breathe smoke for 6 s and you collapse, which is death. Holding your breath stops the choking.
- *Flames:* they kill.
- *Death in the fire* takes you back to the last bell, before you set it.

## Settings and accessibility

- **One difficulty,** as designed.
- **Settings:**
  - field of view, 60–90°;
  - mouse sensitivity;
  - invert look;
  - volume;
  - crouch as hold or toggle;
  - subtitle size (small, medium, large);
  - a subtitle backing (a dark band behind subtitles and choices);
  - less motion (no head bob, no lantern sway, a softer stumble).
- **Not in this run:** key remapping and softer scares (you didn't pick them; easy to add later).

## What changes in what's built

| Built now | Becomes | Milestone |
| --- | --- | --- |
| First capture (any night) wakes you in the infirmary | Only on nights 1–2, once; from night 3, death | M8 |
| Esc frees the mouse | Esc opens the pause menu | M8 |
| The dot becomes a hand near usable things | The dot stays; usable things get an outline | M8 |
| The ledger has one page | Two: guests and duties, then notes | M9 |
| The lantern never goes out | The wind can put it out; relight it at a flame | M11 |
| Brothers appear at their places unseen | They walk their routines in view | M11 |
| Incense at Matins is unavoidable | Avoidable in part from night 4 | M10 |

## Which milestone builds what

| Milestone | Mechanics |
| --- | --- |
| M8 | Controls (crouch, lean, the gamepad), the satchel, the outline and the duty glyph, the capture rule and your death, the pause menu and settings |
| M9 | Bodies (finding, reporting, moving), the ledger's notes, being seen |
| M10 | Dose senses-only, HUD lies, incense positioning, clean food |
| M11 | Throwing, wedging, the bell gamble, the lantern and wind, hunters' voices, the Suspicion bands, routines, trust, warnings, companions, lies at the gate |
| M14 | The Hungry Saint, proof, stopping the rite, fire |

## Tests

Each mechanic gets checks in `tools/check.sh` when it's built:
- **Crouch:** the speed, the half hearing range, being hidden behind a stall.
- **Lean:** the offset, and the hunter seeing your head.
- **Throwing:** the hunter goes to where it landed, and the range depends on the surface.
- **Wedge:** it holds for 8 s, he forces it, and the Saint ignores it.
- **Captures:** a capture on night 1 wakes you, a second kills, a capture on night 3 kills.
- **Lantern:** gutters, goes out in a draught, covered stays lit, relights at a candle.
- **Bell:** the chase breaks off, the nearest person comes, Suspicion +10.
- **Lateness:** each band; fetched means the prior walks to you.
- **Being seen:** +10 once per place per night, and the remark at dawn.
- **Trust:** answers and gifts move it; the gates at 30 and 40.
- **Warnings:** a warned guest lives and the count drops; overheard, +15.
- **Companions:** follow, wait, hide with you, caught and gone.
- **Lies:** noticing a contradiction writes the note.
- **Incense:** the dose by place, holding your breath, being seen out of your stall.
- **Food:** eating ends hunger.
- **The HUD:** the outline only within reach, the glyph only for the current duty and never in a chase, lies only at 75+.
- **The Saint:** its speed by count, it passes doors, its touch kills.
- **Proof and the rite:** two kinds open the Gate; freeing the victim or taking the book stops the rite.
- **Fire:** it spreads, choking leads to collapse, flames kill, and death takes you back before you set it.

## Decisions to review

The mechanics I chose because the grilling didn't settle them:
- The gamepad bindings, and crouch on Ctrl and lean on Z and C (E and Q were taken).
- Every number marked *mine* above. The ones that shape play most:
  - crouch 0.8 m/s with half hearing range;
  - wedge holds 8 s;
  - throw noise 10 / 8 / 4 m;
  - bell +10;
  - the lateness bands;
  - trust's starting values and its gates at 30 and 40;
  - warning overheard +15;
  - incense a third by the door;
  - the Saint at 0.9 or 1.2 m/s;
  - smoke collapse after 6 s.
- The cult can't tear out notes, only guest pages.
- Hunters' voices are subtitles with a direction, from night 4.
- Throwables are tidied away by the next night.
