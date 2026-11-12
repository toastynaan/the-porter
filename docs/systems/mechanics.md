# Mechanics (the full-game run)

Nov 8, 2026 · from the mechanics grilling with @Pahul; revised after the adversarial review the same day (see the design doc's "Second review")

How everything the player does works, for the run in `docs/log/full-game-run.md`. The story spec says *what happens*; this file says *how it plays*. Numbers marked *mine* are starting values to tune in playtest. Mechanics already built and unchanged (walking, running, stamina, breath, hiding spots, the hunter's five states, the gate reading, the candle clock, dozing, conversations) are described in `docs/systems/hunting.md`, `docs/places/night3.md` and `docs/systems/dialogue.md`; this file covers what's new and what changes.

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
| Peek through a squint | E at a squint | A / Cross | **New:** your eye to the bars; look about a little; E to step back |

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
- **Wind** can put it out, but only at set moments, never at random and never in a chase: a gust down the tower stair on night 2, the door that blows open in the fog on night 4, and a few more like them. The flame gutters for 1.5 s as a warning, and covering it in time keeps it lit. *(gutter time mine)*
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

**Giving** happens in conversations: alms to Mab, clean food to someone hungry, a candle to a guest. Each adds a little trust.

## Being hunted

**Captures** follow one rule for the whole game. A capture on night 1 or 2 wakes you in the infirmary, once. Every other capture kills you:
- a second capture on nights 1–2;
- any capture from night 3 on.

Night 3's rescue by Thomas stays: it's a near miss, not a capture. *This changes what's built: on night 3 the first capture now kills.*

**Your death.** It's short and first-person: the hunter is on you, a blade or a cord, the view drops and goes dark. Then you go back to the last save with everything as it was then.

**Quiet saves.** Besides the bell saves, the game saves quietly just before every designed chase and set piece: the crypt on night 3, the fog on night 4, the granary on night 5, each stage of night 6, the fire. A death never costs more than a few minutes of replay. Continue on the title screen still starts from the last bell.

**Suspicion** (hidden, 0–100) rises fast and falls slowly: a night with every duty on time, nothing seen and no off-hours bell takes 5 off at dawn *(mine)*. It has the doc's four bands:

| Suspicion | Hunting | Source |
| --- | --- | --- |
| 0–29 | One costumed cultist on a patrol route; he chases what he sees but doesn't search | doc |
| 30–59 | He searches where he last saw you and checks the two hiding spots nearest it (as built) | doc |
| 60–84 | Two hunters. They lock doors behind you (you need your keys or another way round), and one waits at the gatehouse | doc |
| 85+ | Night 6's rules come early: the whole cult hunts you that night | doc |

**Hunters talk.** From night 4 they call your name in a voice you know, shown as a subtitle with the direction (*"Alric..." (behind you, Osric)*). Drugged, the name is missing and it's just "A voice". Before night 4 they're silent. *(the subtitle form is mine)*

**Between chases** (the run's spec): you hear and glimpse the hunter on every round, a jump scare comes at most once a night, and the cat runs before he comes.

**The bell rope.** Ring it any time but Matins and the whole abbey comes to the tower:
- The chase breaks off, because the hunter can't be seen in costume by the abbey.
- Who comes first follows rules you can learn, not chance:
  - a friend whose trust is 40 or more (Edwin; Simon, if you saved him) walks you somewhere safe;
  - otherwise, at Suspicion below 60 the prior comes and questions you;
  - at 60 or more a cultist reaches you first, which is a capture.
- Each off-hours ring is Suspicion +10. *(mine)*

**Hiding** works as built. Crouching lets you reach low spots without a cut to the hiding view (under beds, behind the tomb). Companions hide with you (see "People").

## The minimal HUD

There are only two things on screen, plus subtitles and the dot.

- **The outline**, as described under "Your hands".
- **The duty glyph:** a small, dim mark (a candle flame, about 1° across) over the one person or thing the current duty needs, seen within 10 m. It never shows during a chase, while hiding, or while talking. The lit way to each duty stays. A setting turns the glyph off for players who want no help.
- **The HUD lies once.** One scripted moment, on night 5 or 6 and only at Dose 75+: an outline on a door in a blank wall, which opens on nothing. The HUD is otherwise always true, so it stays something the player can trust.

## Reading the hidden numbers

No number is ever shown, but each has a tell in the world, so the player can learn what their choices do:

| Number | How you can tell |
| --- | --- |
| The rite's count | The crypt: the cult lights a candle there for each soul. Go down and count them. Looking at the lit ring from within 6 m *(mine)* writes the `crypt_candles` note. The book's page (night 3) says what they're for |
| Suspicion | 30+: talk stops when you walk into a room, and someone is always watching you at supper. 60+: doors you used to pass are locked, and one hunter waits at the gatehouse. 85+: the brothers won't speak to you at all |
| Trust | Each person greets you warmly, plainly or coldly; at 30+ they tell you more; low, they won't follow you |
| Dose | The image itself (Look and Feel) |
| Hunger | The hand tremor on the lantern, and slow recovery |
| Lateness | A brother remarks on it; very late, someone comes for you |

## Saving people

Each night has at least one person a careful porter can save, by a rule he can learn. The lane's talk at the next dusk tells him what would have saved them ("Turned away after the bell, poor soul, and the Keys was shut").

| Rule | Nights | How you learn it |
| --- | --- | --- |
| Lock the guesthouse once your guests are in bed, and the cult can't reach them | 1–3 | Anselm on the tour: "the old porter locked the guests in at night" |
| Turn someone away before the curfew bell and they go to the Cross Keys and live; after it, the inn is shut and they're out in the lane | All | Mab and Hob, at dusk |
| Ask Hob to keep Jankin in at closing | 2 | Hob's talk at dusk |
| Your keys were copied (night 3's dawn), so locking no longer works: warn a guest to bar the door from inside | 4–5 | The night-4 guest's death, and the lane's talk after it |
| Let Roger's sergeant wait inside the gate | 5 | He asks to |
| Save Simon, not Thomas | 5 | What you've seen of each |

The night-4 change is deliberate: the rule you trusted turns on you (design pillar 4).

## Time and duties

- **Length:** a night is 30–40 minutes. Awake, the clock runs at 3 minutes an in-game hour (it's 4 in night 3's build now). Dozing skips the waits. *(mine)*
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
- **Talking at the grille.** Each knock is a conversation (as built): their greeting stays up over the three choices and "Walk away". Some visitors have one question you can ask first; it comes up under the greeting, and the three choices follow in the same talk.

## Investigation

**The ledger's notes** are a second page. The porter writes a short note himself whenever:
- he finds something ("Rope marks on the merchant's wrists");
- notices a lie;
- hears something that matters ("Thomas says he saw Brother Simon out after Compline");
- finds someone missing ("Edwin was not at Matins").

There's no quest log and no arrows; the notes are in his hand, oldest first, a page a night. The cult can tear out guest pages, but not notes. *(that last rule is mine)*

**Bodies** (the run's spec): look at a body for a moment to find it, and a note is written. Report it in conversation (to Thomas or the prior), or don't. Some bodies are moved; blood stays until it's cleaned.

**The payoff.** At dawn on night 5 the prior arrests you. Show him two kinds of proof, or enough in your notes (6 of the clues the game can write *(mine)*), and he believes you: he lets you go himself and stands with you on night 6. Otherwise Thomas speaks for you and takes you into his care.

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
- **Clean food** ends hunger for the night, Dose-free: windfall apples under the orchard trees (two or three a night), or a heel of Mab's bread when you give her alms.
- **The remedy** comes from Ranulf (+15). Thomas, beside you, warns you off it.

## Night 6

**The Hungry Saint.**
- Nothing stops it: doors, locks and darkness don't, and it cuts through the hidden passages. It's slow, so you can stay ahead, but it never stops coming.
- It always knows roughly where you are and walks toward you, finding its path again every few seconds.
- Its touch is death.
- Its strength depends on the count:

| Count | It | Source |
| --- | --- | --- |
| 8 or fewer | Stays in the crypt; going down there is the danger | Run spec |
| 9 | Walks the abbey at 0.9 m/s | *mine* |
| 10–11 | Walks at 1.2 m/s and kills any cultist it meets | *mine* |

- Silence comes 25 m before it: the animals and the wind stop. Your lantern dims within 8 m. *(mine)*

**The Demon ending is a choice.** At Dose 75+ on night 6, "the demon" (the prior, coming to help) corners you with a light. A prompt to strike appears, the only time you can. Strike and you get the Demon ending; run and the night goes on. Before then, people remark on your eyes ("you're full of it, brother"), so the state is unmistakable.

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

## Night 0 and day 1

**The ride in.** It's on rails: the wagon drives itself from the white chapel through Aldgate to the lane, about two minutes *(mine)*, with something along the way every 10 to 15 seconds. Early on it pulls aside for a cart carrying four covered bodies (the hook). The wagon jolts and sways over the road, and your view with it. You can look about, and talk to the traveller beside you whenever you like; the cart cuts that talk short, and he talks about the dead (a conversation, three answers). At Aldgate the warden stops the wagon, walks up, holds his lantern to your face and talks to you, and walks back. It ends when the carter sets you down.

**Drinking** at the Cross Keys (night 0). It's a conversation answer with Hob or Agnes.
- Each ale is +1 drink, to 5. You lose 1 an hour, and sleep clears it. *(mine)*
- Drink affects sight only, like Dose:

| Drink | You see |
| --- | --- |
| 1–2 | Softer focus |
| 3+ | A slow double image and a drift to the view; the killing at the window is seen through it, and your ledger note says you'd drunk too much |

- Day 1 starts with a headache blur until noon if you drank 3 or more. *(mine)*

**Sleeping** at the inn ends night 0. Lying down on the bed in your room triggers the cry and the window. You can stay at the window or not. Then you sleep, and day 1 begins.

**The squint scare.** Night 0 only, once. If you walk the lane alone after the curfew bell and pass the south squint, a shape stands still just inside it: too tall, too thin, no horns. It's gone once you've looked away. It's one of the three things never explained before night 6 (it's the Saint).

**Length.** Night 0 is 15–20 minutes. The window always happens: if you're still drinking at midnight, Agnes sends you up to bed.

**The tour (day 1).** About five minutes, and skippable on replay. Follow Thomas and Anselm, a companion pair walking ahead. At each duty they stop, explain it, and let you try it:
- bar the gate;
- open the ledger;
- look at the candle clock;
- take hold of the bell rope (you don't ring it by day);
- check a round stop;
- turn down a guest bed, and take the guesthouse key.

The duty glyph marks each one. Then they take you to your cell, and lying on the cot is the nap: a fade to dusk, and night 1 begins with its wake.

**Peeking.** At a squint, E puts your eye to the bars. The view is held, as when hiding, within 25° of straight ahead. You can't be seen through it except up close with a light. From inside, the porter's cell squint shows the lane and the gate.

## The lane at dusk

- **Who's about:** while the gate stands open at dusk, the lane's people are out on their routines: Hob and Agnes at the inn door, Kit selling candles at the gate, Gib lighting the lanterns, Mab begging, the carter and Margery passing.
- **What they say** changes with the nights. Each person's dusk conversation reads the flags: who died, whom you turned away, what you reported. The rumours run ahead of you: what happens in the abbey is talked about in the lane the next dusk.
- **The inn** is open at dusk. You can go in, talk and drink (drink works as on night 0).
- **The curfew bell** rings at nine. The lane empties, and after it only Gib walks the lane, calling the hour every hour (a clock you can hear from inside). If his call stops, something has happened.
- **Lane deaths** happen after curfew, seen through the grille or a squint (the run's spec).

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
  - less motion (no head bob, no lantern sway, a softer stumble);
  - guidance (the duty glyph on or off).
- **Chapter select** on the title screen once you've finished the game: start any night, with the state a typical playthrough would have reached.
- **Not in this run:** key remapping and softer scares (you didn't pick them; easy to add later).

## Sound while the run lasts

Final recordings come last, but horror is half sound, so each system wires its placeholder sounds as it lands: room tone, footsteps per surface, the chant, the hunter humming, knocks, the curfew bell, the watchman's call, the silence before the Saint. Playtests then mean something.

## What changes in what's built

| Built now | Becomes | Milestone |
| --- | --- | --- |
| First capture (any night) wakes you in the infirmary | Only on nights 1–2, once; from night 3, death | M8 |
| Esc frees the mouse | Esc opens the pause menu | M8 |
| The dot becomes a hand near usable things | The dot stays; usable things get an outline | M8 |
| The ledger has one page | Two: guests and duties, then notes | M9 |
| The lantern never goes out | Set gusts can put it out; relight it at a flame | M11 |
| Death or capture sends you back to the last bell | Quiet saves before every chase and set piece | M8 |
| The clock runs 4 minutes an hour awake | 3 minutes an hour | M8 |
| Brothers appear at their places unseen | They walk their routines in view | M11 |
| Incense at Matins is unavoidable | Avoidable in part from night 4 | M10 |

## Which milestone builds what

| Milestone | Mechanics |
| --- | --- |
| M8 | Controls (crouch, lean, the gamepad), the satchel, the outline and the duty glyph, the capture rule, quiet saves and your death, the pause menu, settings and chapter select, the clock's pace |
| M9 | Bodies (finding, reporting, moving), the ledger's notes, being seen, the crypt candles |
| M10 | Dose senses-only, the HUD's one lie, incense positioning, clean food, the remedy |
| M11 | Throwing, the bell, scripted gusts, hunters' voices, the Suspicion bands and their tells, routines, trust and greetings, warnings, companions, lies at the gate, the rules for saving people |
| M12 | Night 0 and day 1: the ride, the Cross Keys, drinking, the window, the squints and the squint scare, peeking, the tour; the lane at dusk (its people, rumours, the curfew bell, the watchman) |
| M15 | The Hungry Saint, proof, stopping the rite, fire, the Demon ending's strike |

## Tests

Each mechanic gets checks in `tools/check.sh` when it's built:
- **Crouch:** the speed, the half hearing range, being hidden behind a stall.
- **Lean:** the offset, and the hunter seeing your head.
- **Throwing:** the hunter goes to where it landed, and the range depends on the surface.
- **Captures and saves:** a capture on night 1 wakes you, a second kills, a capture on night 3 kills; death goes back to the quiet save before the chase, not the bell.
- **Lantern:** a set gust blows it out, covered in time it stays lit, it relights at a candle, and there are no gusts in chases.
- **Bell:** the chase breaks off, and who comes follows trust and Suspicion; Suspicion +10.
- **Tells:** a candle lights in the crypt for each death; talk stops at Suspicion 30; greetings follow trust.
- **Saving people:** a locked guesthouse saves a guest on nights 1–3 and not on night 4; turned away before curfew they live, after it they die; the next dusk's talk names what would have saved them.
- **Suspicion:** a clean night takes 5 off at dawn.
- **The prior:** enough proof or notes and he believes you on night 5.
- **Lateness:** each band; fetched means the prior walks to you.
- **Being seen:** +10 once per place per night, and the remark at dawn.
- **Trust:** answers and gifts move it; the gates at 30 and 40.
- **Warnings:** a warned guest lives and the count drops; overheard, +15.
- **Companions:** follow, wait, hide with you, caught and gone.
- **Lies:** noticing a contradiction writes the note.
- **Incense:** the dose by place, holding your breath, being seen out of your stall.
- **Food:** eating ends hunger.
- **The HUD:** the outline only within reach, the glyph only for the current duty and never in a chase, the glyph setting turns it off, and the one lie only at 75+.
- **The Saint:** its speed by count, it passes doors, its touch kills.
- **Proof and the rite:** two kinds open the Gate; freeing the victim or taking the book stops the rite; the Demon ending only by striking at 75+.
- **Fire:** it spreads, choking leads to collapse, flames kill, and death takes you back before you set it.
- **Night 0:** the ride arrives at the lane, drink blurs and wears off, lying down plays the window, the squint scare happens once and only after curfew, and the night ends in sleep.
- **Day 1:** the tour visits every duty, then the nap leads to night 1's dusk.
- **The lane:** dusk lines change with the flags, the curfew bell empties the lane, and the watchman calls the hour.

## Decisions to review

The mechanics I chose because the grilling didn't settle them:
- The gamepad bindings, and crouch on Ctrl and lean on Z and C (E and Q were taken).
- Every number marked *mine* above. The ones that shape play most:
  - crouch 0.8 m/s with half hearing range;
  - throw noise 10 / 8 / 4 m;
  - bell +10, and who comes (trust 40, Suspicion 60);
  - a clean night takes 5 Suspicion off;
  - the clock at 3 minutes an hour;
  - the prior believes you with 6 clues noted;
  - the lateness bands;
  - trust's starting values and its gates at 30 and 40;
  - warning overheard +15;
  - incense a third by the door;
  - the Saint at 0.9 or 1.2 m/s;
  - smoke collapse after 6 s.
- The cult can't tear out notes, only guest pages.
- Hunters' voices are subtitles with a direction, from night 4.
- Throwables are tidied away by the next night.
- Drink: +1 an ale, 5 at most, lose 1 an hour; double image at 3+; the headache until noon.
- The ride takes about two minutes; peeking through a squint gives 25° either way.
- The rules for saving people, and the night-4 break (copied keys).
- Where the scripted gusts are, and which moment the HUD lies.
- Chapter select gives a typical state for each night.

Added during the run (M8, `docs/systems/frame.md`):
- Looking with the right stick: 2.6 rad/s at full tilt, times the sensitivity setting.
- Crouching: the body is 1.15 m tall and it takes 0.25 s; he stands again only with headroom. A hunter looks for the top of his back (0.12 m under his eyes) and his chest (0.55 m), so a 1 m stall hides him from any distance.
- Leaning takes 0.2 s, not while running, and stops 0.15 m short of a wall.
- The faster clock runs 2 minutes an in-game hour (the night's own pace is 3).
- Your death: a cord unless the hunter carries a blade (all of them do for now); the cord pulls the head up and back and shakes it; the blade is a dark-red flash; the view drops and rolls over 0.7 s, then 2 s of black.
- The outline is about 2 render pixels thick at any distance, pale parchment at 60%; the glyph is lantern-coloured at about 40%.
- Hunters and visitors don't collide with door leaves; they stop at shut doors and turn back at locked ones by rule.
- The chapter card goes on by itself after 14 s if you press nothing.

Added during the run (M9, `docs/systems/death.md`):
- Finding a body: looking within 14° of it from 5 m or closer for 0.6 s.
- A body the cult moves goes once the porter is 20 m off and can't see it for a second.
- Being seen: "after Compline" and "at night" start at 20:00; "near a body" is within 4 m.
- Reporting to no one costs nothing unless a brother saw him by the body (+15, the design doc's number); reporting to Thomas costs +5 per body at the next dusk ("dangerous later").
- A hidden body is found by holding E for 1.5 s at it (the culvert's by wading into it), and the nearest hunter on his rounds hears and comes to look.
- The ledger turns to the notes with a second press of L, and goes away with a third.
- A hallucinated death is gone once the porter has looked away for 1 s.

Added during the run (M10, `docs/systems/drug.md`):
- The drug's events come every 40–70 s at Dose 25+, 30–55 s at 50+, 20–40 s at 75+, never in a chase, a talk or a doze.
- The shape at the edge of view: 48° off centre, 7–12 m off, gone when he looks within 22° of it or after 2.5 s. The face in the grain: gone after 1.5 s of staring.
- The flame bends toward the uncanny from Dose 25, fully at 60, within 9 m, up to 0.6 rad. Reverb from 25 to 40% wet at 100. The walls breathe from 75, 0.6% of the screen at 100.
- Carved saints (six, new to the abbey) turn their heads from Dose 50, within 15 m, only unseen.
- Incense: "in your stall" is within 1.3 m of it; "by the west door" within 2.2 m; it burns 8 s.
- Windfall apples: nine places, three a night; with the satchel up, E eats clean food while hungry.
- Refusing Ranulf's remedy: Suspicion +5 (as built) and Thomas's trust +5.
- The cat keeps 1.8–3.2 m off, stares every 35–70 s for 4 s (at a hunter within 10 m if there is one), and bolts 14 m when the animals go quiet.
- The HUD's lie is the cloister's west walk wall, between the granary's door and the stores'.

Added during the run (M11, `docs/systems/abbey.md`):
- At Suspicion 60+ the cult locks three doors: the slype, the granary's cloister door and the charnel house (his key opens that one). At 85+ three hunters, all searching.
- Hunters call every 6–11 s while chasing or searching; "drugged" for the voice is Dose 50+. From night 4 hunters kill with a blade.
- Fog sight 4 m; an uncovered lantern shows as a glow from 14 m. Snow: up to 400 prints; a hunter follows the freshest within 12 m of where he lost the porter.
- Routines: Thomas at his herbs from 18:30; Osric locks the granary's cloister door at 21:00 and goes to bed at 21:30; Hugh walks the cloister and the court from 20:30 to 23:30; Ranulf in the church from 20:00.
- A warning is overheard if Ranulf is within 8 m; it reaches Thomas if a brother who trusts the porter less than 30 was warned, or anyone who distrusts him.
- A companion is taken by a hunter within 1.2 m, and that's their death. Someone below trust 0 won't follow.
- Refusing Thomas's wine to his face: Suspicion +20.
- At the bell, the prior's questions have three answers; "Something was after me" makes him suspect the porter more.

Added during the run (M12, `docs/places/prologue.md`):
- Night 0 runs from 16:30 at 150 s an in-game hour, so the ride is grey dusk turning dark and midnight comes about 19 minutes in. Rain until 19:00.
- The ride: about two minutes; 3.5 m/s in the fields, 2 m/s up to Aldgate, 3.2 m/s in the streets, 2.5 m/s in the lane, speeding up and slowing at 1.2 m/s²; the carter pulls in about 13 s in and stops while the body cart (2 m/s) passes on the porter's side; the wagon stops at Aldgate for the warden and at the gate until nobody's talking. *(Changed after the run: it was 1.5 m/s and 3.1 minutes with little on the way.)*
- Drink: a blur of 0.5 + 0.15 source pixels an ale once over 0.5; the double image grows from 2 (the third ale wearing in) to full at 5; the headache comes from three ales drunk that night (counted, not what's left at sleep): a 0.9-pixel blur until noon.
- The squints: the cell's at z −6, the court's at 6 and 14; the slit 0.18 × 0.5 m, splayed to 0.4 m at both faces; peeking puts the eye 0.12 m from the bars.
- The squint scare: he must pass outside within about 4.6 m with nobody of the lane within 12 m; it appears only out of his view; it counts as seen from within 3.5 m, looking within 15° of the slit with a clear line through; it goes when he looks 35° away or steps 4 m off; walking 8 m off without seeing it lets it come again.
- The curfew: people out in the lane walk to the nearest house door and go in (30 s at most); people indoors stay; windows go dark one by one through the hour; Gib calls every hour from ten to five.
- Out at midnight on night 0, or shut out by the curfew, Agnes sends him up to bed and the window plays.
- Day 1 starts at 8:00 in daylight brighter than any dusk: sky 1.4, ambient 1.7, a shadowless sun 0.6.

Added during the run (M13, `docs/places/nights.md`):
- Night 1's knocks at 19:00 (the merchant) and 20:15 (Walter), both before the curfew bell; the cult comes for an unprotected guest at 01:30; the knock with no one at 02:00.
- Night 2's knocks at 19:00 (Joan), 20:00 (Roger, only if the merchant died) and 21:30 (the sailor, after the bell, so turning him away puts him in the lane); the lane death at 23:15.
- The round's shape appears once on night 1, twice on night 2 and three times on night 3.
- Whom to tell about a body is asked at dawn, before he sleeps, for every body found and not yet reported.
- The lane death's victim, in order: someone turned away after the bell tonight who isn't a named outsider; else Jankin, unless Hob kept him in; else no one.

Added during the run (M14, `docs/places/nights.md`):
- Night 4's knocks at 19:00 (Mab) and 20:00 (the pilgrim, so turning him away sends him to the Keys); Edwin dies out of sight at 23:00.
- The night-4 warning is given at the guest's bed, as the porter shows him to it.
- The fog death plays within 9 m of its spot; the prior arrives 1.5 s after the porter reaches the body.
- Two hunters at night 4's charnel house; Osric's mask comes off once he's been within 7 m for 0.6 s; the chase ends after 6 s with neither chasing or searching. The scripted hunters carry blades from night 4.
- Night 5's dilemma has no time limit: the first of the two he reaches is the one he saves. Saving Simon is Simon's trust +20.
- Night 5's knocks at 19:00 (Joan, if she comes) and 20:30 (the sergeant).
- The lock-in bars twenty doors (the west range's, the church's and the dormitory's ground floor) and sends two hunters (one in the granary, one in the choir); it ends when he's out of the latrine chute.
- The prior believing him is his trust +40.
- A conversation's `[if clue]` holds for a clue in his notes as well as a flag.

Added during the run (M15, `docs/places/night6.md`):
- Night 6's knock at 20:00; the rite and the Saint from 23:00; the Demon's approach from 22:30.
- The Saint: a shadow that keeps within 10 m of its home in the crypt at 8 or fewer; finds its way again every 2.5 s; its touch reaches 1.1 m; hiding doesn't save him from it; its lantern-dimming is to a third. It kills Dunstan, Cole and Osric (the choir's) the first time he comes within 14 m of each after it wakes, once it walks.
- Night 6's hunters: Osric, Ranulf, Cole and Dunstan (Thomas leads the rite), all with blades.
- Fire: catches from within 2.5 m of the spot (measured from his eyes); smoke within 3.5 m of a flame; a flame kills within 0.9 m.
- Who knocks on night 6: Roger if the merchant or his sergeant died; otherwise Joan, if she's alive and he met her at the gate; otherwise Mab. Roger won't come in without two kinds of proof.
- Leaving any other way (the gate into the lane, the race alone) or holding out to Lauds is the Broken Rite, whether the rite was stopped or the count was too low.

Added after the run (playtest fixes):
- The ride's paces and stops (`docs/places/prologue.md`, "The ride's cues"): 3.5, 2, 3.2 and 2.5 m/s, 1.2 m/s² to speed up and slow down; the body cart at 2 m/s from 40 m past the pull-over, waiting 9 m off; a cue's lines dropped once the wagon is 12 to 40 m past (each cue sets its own); the warden's stop is 1 s after his lines.
- Paused, nothing in a night counts time: the beats' and scenes' timers and loops wait with the tree (`PlayTime`).
- A cue's or a beat's line waits until nobody's talking and no line is up (`Talk.quiet()`) on the ride and at the gate after it, so lines don't cover each other there.
- A press counts once, and only after the key is let go (`Press`): holding E, Esc, the ledger or satchel key, lock or crouch-toggle does nothing more than one press. In the playtest (the editor's game window) a held E's repeats counted as new presses: it ran through a whole talk, answered for him, and opened it again as it closed.
- A move key held when a talk begins doesn't walk him away until he lets go of it and presses one again.
- Talking, his view turns to their face and narrows for 1.2 s, then widens and is his: he looks anywhere while they talk (looking away lets go at once). The old cone (30° either side, 40° by 50° at the grille) is gone. Someone can start a talk themselves the same way (the traveller as the wagon sets off).
- He says the answer he picks (ALRIC over it), then they reply; an answer in brackets is something he does, shown in italics and not said. Narration (a line in brackets) shows in italics without brackets or a name. On the wagon the last choice is "Turn away".
- On the ride the traveller opens the talk as the wagon sets off (pace 2.6 m/s to the wall, from 3.5), and the carter's "Whoa" 6 m before the pull-over breaks off any talk.
- Turning to someone is gentler: the view takes 0.9 s to turn and narrow (it was 0.45 s), and pulling the mouse takes it back even mid-turn. Following the body cart is slower too.
- Every mouse click counts as its own press (a key held down still counts once). E answers nothing for 0.3 s after answers come up (it was 0.4).
- The traveller on the road: after each answer the questions left come up again, so one turn to him is one talk (each answer used to end it, and he opened the next with only "Brother?"); with nothing left to ask he says so (a new line, DRAFT).
- A chapter's card fades into the dark (0.6 s) and the chapter loads under black; before, the card stayed on screen, not answering, while the night loaded, and the night then cut in.
- Night 0 opens on black and comes up over 3.5 s as the wagon rolls. The ride starts 22 m further back (48 m short of the chapel), so the first 8 s are the road and nobody talking; it is a little over two minutes now.
- As the body cart passes, his view goes to the body on it and follows it by (3.6 s, narrowed 22°; moving the mouse lets go). Before, it turned to the traveller, who starts the talk about it.
- Talking, third pass (`docs/systems/dialogue.md`): a point's last line comes up together with its answers; E answers nothing for 0.4 s after a choice comes up, later 0.3 s (a number key answers at once); the arrows wrap, and the wheel moves the answer too; number keys work from the keypad as well.
- Whoever he's talking to stands still until the talk is over, then goes on. If they go (out of the world, or more than 6 m off), the talk is cut short with no parting line. A capture or a death cuts it short too.
- Anything said while he's talking or being asked something, that isn't part of it, shows small above the talk's line and never takes the question's place. With no talk or question open, a line said over another has its place, and the older one ends if it has less than 0.6 s left when it's uncovered.
- One question is open at a time; a second waits. A beat's question keeps the line just said (within 0.3 s) up over its answers.
- At the grille it's one talk each time he comes to it: the greeting once, the question under it, then the three choices under the visitor's answer. Before, the visitor greeted him again and his view turned again between the question and the choices.
- Every choice that is something he does is written in brackets and shows in italics: the gate's three, the bread, the remedy, the wine, whom to tell about a body, striking the demon, opening the gate on night 6, the tour. What he says to the prior at night 2's dawn and at the bell, and his question about the sand, he now says aloud ("What's the sand for, by the well?" is new, DRAFT).
- The look: EB Garamond; the name in lantern-coloured small capitals; answers left-aligned in a centred block with a thin bar on the one the arrows are on; a soft gradient under it; fades of 0.16 s in and 0.22 s out; a line rises over 0.24 s when its answers come up under it.
- The ride's cuts (supersedes the carter's "Whoa" above): the carter pulls in without breaking off a talk; when the body cart is 8 m off the traveller breaks off any talk himself with "Whoa. Look at that." At Aldgate (a stop with `cut_in`) the traveller breaks off any talk to greet the warden; the warden (the cue's `inspector`) walks up at 1.2 m/s to 1.35 m out from the wagon's middle, 0.25 m behind the porter's seat, raises his lantern over 0.8 s to 0.75 m from the porter's eyes and 0.25 m to the side, and walks back to his place.
- Carts jolt (`CartJolt` on each cart's `Bed`): each wheel runs over its own road (swells 4 cm, judder 1 cm, stones up to 8 cm *mine*) on a 2.4 Hz spring damped 0.3; the bed sways with the difference between the wheels and tips about the horse's back (2.4 m forward). Riders sit on the bed; the porter's view takes 80% of his seat's roll and pitch. Less motion: a third of the jolt and no tilt. The cart going by carries four bodies.
