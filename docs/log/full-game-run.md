# The full-game run (M8–M16)

Nov 8, 2026 · from the grilling session with @Pahul

The run builds the whole of The Porter: the prologue (night 0 at the Cross Keys and the day-1 tour), six nights in order and seven endings, playable from the title screen, with placeholder art and sound. It goes from M8 to M16 without stopping. The story changes it rests on are in the design doc (see its changelog), and the HUD and gore changes are in the Look and Feel. How every mechanic plays (controls, crouching, the satchel, throwing, captures, trust, warnings, companions, the Saint, fire) is in `docs/systems/mechanics.md`; where the two overlap, that file wins on rules and numbers. This file holds the run's own spec: deaths and bodies, the rite, the systems, the nights, the endings and the milestones. It ends with a progress log and the decisions for you to review.

## The agreement

- **Scope:** the prologue (night 0 and day 1), all six nights, all seven endings, menus, saves and death, with placeholder art and sound. Generated pilgrims stay out (the doc's scope decision); every visitor is written by hand.
- **No stops until the end.** I commit after each milestone, push it to main, and add a line to "Progress" below. I stop early only if I'm blocked or something breaks that I can't fix.
- **Gaps:** where the docs don't say, I decide in their spirit and add the decision to "Decisions to review" at the bottom. Numbers I pick are marked *mine* in the docs, as before.
- **Writing:** I draft real lines for every conversation, scene and chronicle entry. Each conversation file starts `# DRAFT` until you've rewritten or accepted it.
- **Sound:** final recordings stay last, but each system wires its placeholder sounds as it lands, so playtests can judge fear.
- **Length:** a first playthrough of 4–5 hours (night 0 15–20 minutes, the tour 5, nights 30–40). Bigger means deeper, not longer: every night different, every choice with a consequence you can see.
- **Before it starts:** you read this file and the two doc changelogs and say go. Close the Godot editor during the run (or don't save from it): I'll be rewriting scenes on disk.

## Done when

1. **From the title screen,** New Game plays night 0, day 1 and nights 1 to 6 in order, with a chapter card for each. Once you've finished the game, chapter select can start any night. Continue picks up at the last bell; death sends you back to the last quiet save, a few minutes back at most.
2. **Every night runs** from waking at dusk to sleeping at dawn in a scripted test that passes.
3. **Each of the seven endings** can be reached by a scripted route, and each shows its chronicle entry.
4. **The deaths:** every witnessed death and found body happens where this file says. Every death that choices can prevent is prevented by its choice in a test.
5. **The checks:** `tools/check.sh` passes with warnings as errors, and there's a still of every night's main beats in `art/_review/`.
6. **The docs:** they describe what was built, `docs/play-guide.md` tells you how to play every route, and "Decisions to review" is complete.

What the tests can't tell you is whether it's scary. That's your playtest, after the run.

## Deaths and bodies

There are three kinds of death:
- **Found bodies:** the design doc's six, one a night (the pond, the bell tower, the oven, the charnel house, the granary, the infirmary).
- **Witnessed deaths:** nine, rising from none on night 1 to three on night 6, on top of the six. You see them happen. Before them, the killing you watch from the inn's window on night 0, which comes before your six nights and doesn't feed the rite.
- **Hidden bodies:** five optional ones, earlier victims, for players who explore.

**Who can die in front of you:** guests you admitted, brothers, and people in the lane. The named outsiders (Walter, Joan, Mab, Roger) never die in view; Joan can still be body 5, as the doc says.

**How much is shown:** it varies by death.
- *Implied:* a struggle half-seen in silhouette, a cry cut off, a lantern dropped on the flags.
- *Gory:* the wounds in view, blood on the walls, the body left as it fell.
- *The throat:* one quick cut and blood flying through the light.

The body falls as a ragdoll (the kept ragdoll system). Fresh blood stays dark (Look and Feel, "Old blood").

**Two renders:** drugged, you see the demon do it, with long fingers and a crown of horns; sober, a man in a mask. At Dose 75 and up, some deaths you see are hallucinations: they leave no body and no blood, and the cult doesn't need to clean them up. You can't tell which until you go and look.

**Choices decide who dies.** In the moment you can't stop a death; before it, your choices can. Who you admit, who you turn away, whether you lock the guesthouse, whom you warn and who you save on night 5 change who is killed, and how many. Every night has at least one person a careful porter can save, by a rule he can learn (`docs/systems/mechanics.md`, "Saving people"), and the lane's talk at the next dusk says what would have saved them.

**Where you stand** varies, so no death plays like a cutscene, and control is never taken away: helpless behind the grille; in danger, as the killer turns to you; seconds too late; or only hearing it.

### Witnessed deaths

| Night | Victim | Where you see it | Shown | Your choices |
| --- | --- | --- | --- | --- |
| 0 | A guest of the abbey | From your room at the top of the Cross Keys, over the wall: by the well | Implied: a figure in a black habit, back to you, a struggle, then dragging him toward the cellar. Sober you saw a man; drunk you aren't sure | None (before your six nights) |
| 2 | Whoever you turned away after the curfew bell; if no one, Jankin, put out of the Cross Keys at closing | The lane, through the grille, under a street lantern after midnight (helpless) | The throat. Far off: a tall shape behind him, then he's down in the gutter. The demon never moves while you look (Glimpses phase) | Turn people away only before curfew, and ask Hob at dusk to keep Jankin in, and no one dies |
| 3 | A bound pilgrim, taken before your watch | The crypt, from the foot of the stair: the figure by the light has his back to you because he is killing him (in danger) | Gory. Then he turns and sees you, and the night-3 chase starts | None |
| 4 | A choir brother (not Simon) | The cloister walk in the fog: you hear it a few metres ahead, and reach him as his lantern is still rolling on the flags (seconds too late) | Implied: a cry cut off, then the body. The prior is the next to arrive, and there's blood on his sleeve | None |
| 4 | The guest you admitted tonight | The guesthouse, its door open, on your round (seconds too late) | Gory: the rite's cuts, the marks the Saint itself leaves on night 6 | Warn him to bar the door from inside (your lock no longer helps), or turn him away before curfew |
| 5 | Brother Simon, if you save Thomas | The chapter house at dusk, as you carry Thomas out (in danger: the masked man turns to you) | The throat, in front of you | Save Simon and no one dies here |
| 5 | Roger's sergeant, sent to watch the gate | The lane, during the lock-in (heard only) | Implied: you hear it from inside the granary. His lantern is out and his blood is there at dawn | Let him wait inside the gate and he lives |
| 6 | Dunstan | The cloister: the Hungry Saint finds him first (in danger: it turns to you next) | Gory: the first time you see it move | None |
| 6 | Cole | At the gate, keeping it shut against you | The throat | None |
| 6 | Osric or Ranulf (whichever is nearer you) | The choir | Implied: the candles go out one by one, then silence | None |

### Found bodies

These are the design doc's six, with what changes:

| Night | Body | Changes |
| --- | --- | --- |
| 1 | The merchant in the fishpond | Only if you admitted him and left the guesthouse unlocked. Locked in, or turned away before curfew (he goes to the Cross Keys), he lives; the pond is empty at dawn, and Roger doesn't come asking on night 2 |
| 2 | The choir brother in the bell tower, who warned you about the bread | None |
| 3 | Bones in the oven | Old victims, from before your watch |
| 4 | Edwin in the charnel house | None |
| 5 | Joan under the grain (if you sheltered her), otherwise a pilgrim | None |
| 6 | Anselm in his infirmary bed | None |

**Moving bodies:** the cult moves the bodies that would prove a man did it: the merchant (rope marks), Edwin (the carding-comb wounds) and the night-4 guest. Leave to fetch someone and they're gone when you get back. The others stay where they fell.

**Reporting:** as the doc says. Find a body and choose whom to tell:
- *Thomas:* safe now, dangerous later.
- *The prior:* Suspicion +10, because Ranulf overhears, and he suspects you.
- *No one.*

The dawn scene and later conversations follow what you chose.

**Blood and marks** stay until the cult cleans them. Each dawn they scrub what would prove men did it (drag marks, boot prints in blood) and miss the rest. The abbey gets worse night by night: the doc's "the map remembers".

### Hidden bodies

There are five optional ones. Each is an earlier victim, has a pilgrim badge that matches a name torn from the ledger, and is a risk to find (a hunter's patrol passes nearby).

| Where | From | Found by |
| --- | --- | --- |
| Down the well | Night 1 | Drawing water; the bucket comes up heavy |
| The mill race culvert | Night 2 | Wading the race past the wheel |
| Under the kitchen beds in the gardens, freshly dug | Night 3 | Your lantern on the turned earth; dig with your hands |
| The bell tower loft | Night 4 | Climbing past the bell |
| Under the chapter house flags | Night 5 | A loose flag where Simon was scrubbing |

## The rite

The cult's book says the Hungry Saint wakes when it has been fed **ten** souls in the six nights, with the last given in the crypt at Matins on night 6. No number is shown, but the crypt keeps count: the cult lights a candle there for each soul, and you can go down and count them. The book's page (night 3) says what the candles are for.

| Deaths | How many | Which |
| --- | --- | --- |
| Always come | 6 | The bell-tower brother (night 2); the crypt pilgrim (3); Edwin and the fog brother (4); body 5 (5); Anselm (6) |
| Your choices can stop | 5 | The merchant (1); the lane death (2); the night-4 guest; Brother Simon (5); Roger's sergeant (5) |

What the count has reached by night 6 decides how strong the Saint is:
- **8 or fewer:** it's a shadow that can't leave the crypt. The Rising can't happen. (Save three of the five and you get here.)
- **9:** it walks the abbey slowly, and the cult's last rite can finish it.
- **10–11:** it walks and hunts, and only stopping the last rite (or the fire) keeps it in.

On night 6 its last victim at Matins is Brother Simon if he lived, otherwise a pilgrim from the guesthouse.

## Systems

| System | What it does |
| --- | --- |
| The prologue | Night 0: the wagon ride through Aldgate, the Cross Keys (taproom and rooms), the lane's people, drinking, the curfew bell, the squint scare, the killing seen from your window, sleep. Day 1: grey daylight, the tour of the duties with Thomas and Anselm, the nap (`docs/systems/mechanics.md`) |
| The lane | A hub at each dusk while the gate is open: the people you met on night 0, their rumours (which follow what you did), the inn. After the curfew bell: the watchman calling the hour, windows going dark, lane deaths seen through the grille and the three squints |
| Quiet saves | Before every designed chase and set piece, so a death costs a few minutes at most. Bells still save too, and Continue starts from the last bell |
| Tells | Every hidden number shows in the world: crypt candles for the count, talk stopping and doors locking for Suspicion, greetings for trust (`docs/systems/mechanics.md`) |
| Six nights | Each night: dusk, supper, the gate, knocks, Matins, the round, the small hours, dawn, then sleep and a chapter card. Everything carries over: flags, Dose (halved by a day's sleep), Suspicion, keys, the ledger, the count, bodies, blood, locked doors and what each person thinks of you |
| Saves | At every bell, one slot. Continue on the title screen. Death sends you back to the last bell |
| Menus | Title (New Game, Continue, How to Play, Settings, Quit), pause, settings (field of view 60–90°, mouse sensitivity, invert, volume, clock speed off by default). Manuscript style, as the Look and Feel says |
| Captures and your death | One forgiving capture, on night 1 or 2 only (you wake in the infirmary); every other capture kills. Death is short and first-person: the hunter is on you, a blade or a cord, the view drops and goes dark, then back to the last bell (`docs/systems/mechanics.md`) |
| Minimal HUD | A thin pale outline on whatever E would use, while you look at it and within reach. A faint glyph above the one person or thing the current duty needs, seen within about 10 m, never during a chase or while hiding. The lit way stays |
| Deaths | A scripted death node: the victim, the killer, the style (implied, gory, throat), two renders by Dose, a ragdoll body, blood that stays. At Dose 75+ it can be a hallucination that leaves nothing behind |
| Bodies | Found, reported (Thomas, the prior, no one), moved by the cult, cleaned up after |
| The rite | The hidden count; the cult's book as a readable object; the Saint's strength on night 6 |
| The drug | Dose tiers as the doc says: whispers, steps behind you, your name; shapes at the edge of view, carvings that turn their heads; at 75+ the walls breathe and the dead stand in the choir. Fake events leave no trace |
| Scares between chases | The hunter heard and glimpsed on every round (steps on the floor above, a lantern going out ahead), hallucination events by Dose, and a few jump scares (a body dropping, a face at the grille), at most one a night |
| Hunters | Suspicion as the doc's four bands: search where you were seen; two hunters who lock doors behind you and wait at the gatehouse; night-6 rules early. They call your name in a voice you know (subtitles), and from night 4 they talk and hunt like men |
| Brothers | Each walks a routine by the hour (Osric locks the cellar at nine; Thomas grinds herbs; lit windows show who's up). A routine that breaks is a clue. Each remembers how you treated them |
| Weather | Rain on nights 1–2 halves what the hunter hears, and what you hear. Fog on night 4 cuts sight to a few metres for you and for him. Snow on night 6 leaves footprints you and the hunters can follow |
| The cat | Follows you on rounds, stares into corners (sometimes a man is there), runs before the demon |
| Dosing | Bread (+10), incense (+25, from night 4 avoidable by the door), Ranulf's remedy (+15), the well from night 4 (+5 a drink), Thomas's wine on night 6 (+40) |
| Gate visitors | The doc's knocks, all written: the merchant, Walter, the knock with no one there, Joan, the sailor, Roger, Mab inside, pilgrims. The cult tears ledger pages |
| The Hungry Saint | Night 6 only. It walks slowly and moves in view. Darkness doesn't hide you from it, silence comes before it, and its touch is death. It kills cultists too |
| Fire | Take a flame to the granary or the crypt. The fire spreads along set paths, smoke cuts your sight and burns, and you have to get out |

## The nights

The night-by-night script is in the design doc. In short:

| Night | Knocks | Witnessed | Found | Thomas | Chase rule | Weather |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | None: you're outside, at the Cross Keys | The killing by the well, from your window | None | Not yet met | None (the squint scare, if you walk alone after curfew) | Rain at dusk, then clear |
| Day 1 | None | None | The sand by the well | Leads the tour with Anselm; his first lie | None | Overcast day |
| 1 | The merchant, Walter, the knock with no one there | None | The merchant (if admitted) | Kind; the night is a tutorial | None (a glimpse at the end of the cloister) | Rain |
| 2 | Joan, the sailor, Roger | Someone turned away after curfew, or Jankin (or no one) | The bell-tower brother | Tells you the prior is about at night | None (glimpses) | Rain |
| 3 | Walter, the child's knock | The crypt pilgrim | The oven bones | Warns you off Ranulf's remedy; tells you the prior asks about you; saves you from the hunter | Hiding (as built) | Clear |
| 4 | Mab, inside the gate, and a pilgrim | The fog brother; the guest (or no one) | Edwin | No supper (the house fasts); tells you he saw Brother Simon out at night; you find Simon scrubbing blood | Two hunters; one is Osric | Fog |
| 5 | Joan (if turned away before) and Roger's sergeant | Simon (or no one); the sergeant (or no one) | Joan or a pilgrim | The dilemma at dusk: 'attacked' in the chapter house as Simon is; you save one. At dawn the prior arrests you, and believes you if you can show him enough | Locked in the granary; out by the latrine chute | Clear |
| 6 | Roger, Joan or Mab, depending on what you did | Dunstan, Cole, Osric or Ranulf | Anselm | No duties at all. The wine; the truth in the crypt | The whole cult, and the Saint | Snow |

Nights 1 and 2 teach the routine. From night 3 each breaks a step of it: the crypt breaks the round (3), there's no supper (4), the night opens with the dilemma (5), and there are no duties at all (6).

## Endings

They're checked in this order when night 6 ends:

| Ending | How you get it | What happens | The chronicle's last line |
| --- | --- | --- | --- |
| The New Faith | Caught on night 6 after drinking Thomas's wine | You wake in a habit with a mask in your lap. "The porter has always been one of us" | You keep the gate for it, for forty years |
| The Demon | At Dose 75+, "the demon" corners you with a light and you choose to strike | You kill it. Sober: it was the prior, who came to help. You're hanged for the murders | It was fed, and slept |
| The Rising | The last rite finishes (you didn't stop it) and the count reached 9 or more | It walks out of the gate into London | Whitechapel, 1888 |
| The Fire | You burned the granary and the crypt, with the book | The proof, the cult and the book burn together. The record calls it lightning | You're never sure who was inside |
| The Gate | Reach the gate with proof (a costume, a purse, the pig's bone) and open it for Roger | Roger's men take the abbey; the cult hangs; the bailiff takes the land | Its name was never written down again, until 1888 |
| The Witness | Escape by the mill race with Mab or Joan alive | You flee with the only other person who knows. No one believes either of you. A new porter is at the gate | The killings stopped, for a while |
| The Broken Rite | You stopped the last rite and left any other way, or held out to dawn | Denied, for now | Denied, not ended |

Each chronicle entry is a short paragraph written decades later in a plain chronicler's voice, giving the official version. It never matches what you saw. I draft them.

## Milestones

| Milestone | What | Done when |
| --- | --- | --- |
| M8 | The game's frame: six nights in order, carry-over, bell saves, quiet saves and Continue, chapter cards and chapter select, title, pause and settings menus, the capture rule and your death, the minimal HUD (and its setting), crouch, lean, the satchel, the gamepad, the clock's pace | A test plays a stub of each night from New Game to dawn and back through the title; death and Continue work |
| M9 | Death and bodies: the death node (three styles, two renders, fakes, ragdoll), blood that stays and gets cleaned, moving bodies, reporting, hidden bodies, the rite's count, the crypt candles and the book, the ledger's notes, being seen, the prior's night-5 judgement | Each style plays in a test scene; reporting changes what follows; the count adds up |
| M10 | The drug and the dark: Dose tiers (senses only), hallucination and fake events, the HUD's one lie, incense by the door, clean food, Ranulf's remedy, scares between chases, jump scares, the cat, the three things never explained | Each tier's events fire in a test, fakes leave nothing, and stills by Dose |
| M11 | Hunters and the abbey: the Suspicion bands, two hunters, locked doors, voices, unmasking; throwing, the bell, scripted gusts; routines, trust and greetings, warnings, companions, lies at the gate, the rules for saving people and the dusk talk that teaches them; weather; the well; the wine | Each band and each kind of weather tested; routines walk by the hour |
| M12 | The prologue and the lane: the road through Aldgate, the Cross Keys inside and out (the inn gains a storey), the lane's people and their dusk rumours, drinking, the curfew bell and the watchman, the squints and the squint scare, the killing from the window; day 1's tour and the nap | Night 0 and day 1 play from New Game to night 1's dusk in one test; the lane's lines change with flags |
| M13 | Nights 1 and 2, and night 3 brought into line (the crypt death, Thomas's beats, the rite's page) | Night 0 to night 3 play in order in one test |
| M14 | Nights 4 and 5: the fog, Edwin, Osric unmasked, Simon and the blood, the dilemma, the granary, the arrest | Night 0 to night 5 in order; both sides of the dilemma |
| M15 | Night 6: the hunt, the Hungry Saint, proof, stopping the rite, fire, the crypt, the seven endings and their chronicles | Every ending reached by a scripted route |
| M16 | Full pass: every route played by tests, fixes, timing (4–5 hours), the play guide, the decisions list | "Done when" above, all of it |

## Risks

- **Size.** This is about eight milestones the size of M7. I'll keep each one shippable, so the game works at every commit.
- **The dev build.** Godot 4.8.dev7 may break under this much more. If it costs real time, I'll log it and work around it rather than change versions without you.
- **Ragdolls.** The kept ragdoll system was built for the old project. If it fights the new bodies, bodies fall as a scripted pose instead, and I'll log that.
- **The feel.** Pacing, fear and whether players find their way can only be judged by your playtest. I'll keep the doc's rule of 5–10 quiet minutes before each night's main event.

## Progress

In `docs/log/progress.md`.

## Decisions to review

In `docs/log/decisions.md`.
