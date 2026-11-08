# The full-game run (M8–M16)

Nov 8, 2026 · from the grilling session with @Pahul

The run builds the whole of The Porter: the prologue (night 0 at the Cross Keys and the day-1 tour), six nights in order and seven endings, playable from the title screen, with placeholder art and sound. It goes from M8 to M16 without stopping. The story changes it rests on are in the design doc (see its changelog), and the HUD and gore changes are in the Look and Feel. How every mechanic plays (controls, crouching, the satchel, throwing, captures, trust, warnings, companions, the Saint, fire) is in `docs/mechanics.md`; where the two overlap, that file wins on rules and numbers. This file holds the run's own spec: deaths and bodies, the rite, the systems, the nights, the endings and the milestones. It ends with a progress log and the decisions for you to review.

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

**Choices decide who dies.** In the moment you can't stop a death; before it, your choices can. Who you admit, who you turn away, whether you lock the guesthouse, whom you warn and who you save on night 5 change who is killed, and how many. Every night has at least one person a careful porter can save, by a rule he can learn (`docs/mechanics.md`, "Saving people"), and the lane's talk at the next dusk says what would have saved them.

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
| The prologue | Night 0: the wagon ride through Aldgate, the Cross Keys (taproom and rooms), the lane's people, drinking, the curfew bell, the squint scare, the killing seen from your window, sleep. Day 1: grey daylight, the tour of the duties with Thomas and Anselm, the nap (`docs/mechanics.md`) |
| The lane | A hub at each dusk while the gate is open: the people you met on night 0, their rumours (which follow what you did), the inn. After the curfew bell: the watchman calling the hour, windows going dark, lane deaths seen through the grille and the three squints |
| Quiet saves | Before every designed chase and set piece, so a death costs a few minutes at most. Bells still save too, and Continue starts from the last bell |
| Tells | Every hidden number shows in the world: crypt candles for the count, talk stopping and doors locking for Suspicion, greetings for trust (`docs/mechanics.md`) |
| Six nights | Each night: dusk, supper, the gate, knocks, Matins, the round, the small hours, dawn, then sleep and a chapter card. Everything carries over: flags, Dose (halved by a day's sleep), Suspicion, keys, the ledger, the count, bodies, blood, locked doors and what each person thinks of you |
| Saves | At every bell, one slot. Continue on the title screen. Death sends you back to the last bell |
| Menus | Title (New Game, Continue, How to Play, Settings, Quit), pause, settings (field of view 60–90°, mouse sensitivity, invert, volume, clock speed off by default). Manuscript style, as the Look and Feel says |
| Captures and your death | One forgiving capture, on night 1 or 2 only (you wake in the infirmary); every other capture kills. Death is short and first-person: the hunter is on you, a blade or a cord, the view drops and goes dark, then back to the last bell (`docs/mechanics.md`) |
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

(One line per milestone as it lands.)

- 2026-11-08 · M8 · 8289138 · The game's frame: title to chronicle with chapter cards, carry-over, bell and quiet saves, Continue, the capture rule and death, menus and settings, the outline and duty glyph, crouch, lean, satchel, gamepad, the 3-minute hour; nights other than 3 are stubs (17 suites, 426 checks; the commit message's 437 is a miscount). Next: M9, death and bodies.
- 2026-11-08 · M9 · 9a4163c · Deaths and bodies: the death node in three styles with two renders, fakes and ragdoll bodies; blood that stays and is scrubbed at dawn; finding, moving, reporting and hidden bodies; the rite's count, the crypt candles and the book; the ledger's notes; being seen; the prior's judgement (19 suites, 479 checks). Next: M10, the drug and the dark.
- 2026-11-08 · M10 · fd1a2a2 · The drug and the dark: hallucinations by tier (ears, eyes, lies) that leave nothing, carvings, the dead in the choir, the bending flame, breathing walls, reverb; the HUD's one lie; incense by the door from night 4; clean food; Ranulf's remedy; scares between chases and one jump scare a night; the cat; the knock with no one there, the self-lit candle and the Saint's figure (22 suites, 540 checks). Next: M11, hunters and the abbey.
- 2026-11-08 · M11 · 45d2dd1 · Hunters and the abbey: Suspicion's four bands with the gatehouse and locked doors, voices and unmasking, throwing, the bell out of hours, scripted gusts, rain, fog and snow, routines in view, trust and greetings, the talk stopping, warnings, companions, lies at the gate, the saving rules and their rumours, lateness, the well and the wine (25 suites, 612 checks). Next: M12, the prologue and the lane.
- 2026-11-08 · M12 · 735f0f0 · The prologue and the lane: the ride through Aldgate with the body cart, the barred gate and Mab, the Cross Keys inside (three storeys), drinking and its double image, the window killing, the squints, peeking and the squint scare, the curfew and Gib's calls; day 1's daylight, the sand, the six-stop tour and the nap; the lane's dusk talks for every night; night 0 and day 1 played from New Game to night 1's dusk (27 suites, 690 checks). Next: M13, nights 1 and 2 and night 3 brought into line.
- 2026-11-08 · M13 · 9958710 · Nights 1 and 2, and night 3 in line: Bede's warning, the merchant and Walter, one glimpse, the guest taken if unprotected, the knock with no one, the pond at Lauds; Thomas on the prior, Joan, Roger and the sailor, the lane death by the curfew rule or Jankin, Bede in the bell tower, one short, the empty bed and torn page, the abbot's demon and the prior's question; the crypt pilgrim killed before the chase, the book's page, the copied keys; every line of nights 1 to 3 drafted; night 0 to night 3 played in order in test_flow (29 suites, 923 checks). Next: M14, nights 4 and 5.
- 2026-11-08 · M14 · e6e97c7 · Nights 4 and 5: the fast, Edwin's whisper and death, Mab inside the gate, Wulfric in the fog and the prior's sleeve, the guest killed unless warned to bar his door, Edwin in the charnel house, two hunters and Osric's face, Simon scrubbing; the dilemma (both sides), Joan and the sergeant, Anselm's word, the grain and the key, the lock-in and the latrine chute, the prior's arrest and judgement; every line of nights 4 and 5 drafted; night 0 to night 5 played in order in test_flow (31 suites, 1075 checks). Next: M15, night 6 and the endings.

## Decisions to review

Things I decided because the docs didn't say. Accept, change or strike each one.

- The rite needs ten deaths; the Saint's strength bands are 8 or fewer, 9, and 10–11; six deaths always come, five can be stopped.
- The witnessed deaths and their places, as in the table above, including Roger's sergeant (a new minor character) and the drunk from the inn.
- The hidden bodies and their places.
- Which bodies the cult moves (the merchant, Edwin, the night-4 guest).
- On night 6, the rite's last victim is Simon if he lived, otherwise a pilgrim.
- The order the endings are checked in, and each chronicle's last line.
- Turned away, the merchant lives and Roger doesn't come on night 2.
- Thomas's night-4 lead on Simon. Simon tells you Thomas sent him only if you save him.
- The settings list, and the clock-speed setting (off by default).
- The prologue's details: he's sent from a small house in the country; the abbey has no night porter, so he sleeps at the inn; Mab sends him there; the guest killed on night 0 doesn't feed the rite; Thomas's first lie is the sand by the well.
- The lane's people and their names (Hob and Agnes, Jankin, Gib, Ralph and Kit, Margery), and Jankin as the night-2 lane death if you turned no one away.
- The curfew bell at nine, and the watchman calling the hour after it.
- The squints: three, one from the porter's cell and two from the outer court; the scare at the south one.
- Once you've finished the game, New Game can begin at night 1.
- After the review: no supper on night 4 (the house fasts); the dilemma at dusk on night 5; Ranulf gives the remedy; the prior's bloody sleeve on night 4; the candle that lights itself on night 5; Jankin saved by asking Hob.
- The Hungry Saint's look (Look and Feel): about 2.6 m, no horns, a gap in the light that dims your lantern, the same at any Dose.
- The three death styles and which deaths use which (the table above).

Added during the run:
- **M8.** The chronicle's year is 1424, and night 0 is the eve of Saint Martin (10 November), so day 1 is Martinmas and night 6 the 16th. The chapter cards' headings, titles and paragraphs (`game/flow/chapters.tres`) are drafts, each the chronicle's few lines about that day, never what happens in it.
- **M8.** Chapter select starts a night with that night's own start state (its Director's `start_` values), the same one it uses played on its own. Until each night is built, the stubs' starting Dose is 25 (night 2), 30 (nights 4 and 5) and 35 (night 6).
- **M8.** Finishing the game deletes the saves, so the title offers Chapters and New Game, not Continue.
- **M8.** The seven chronicle entries are drafted now (`game/endings/endings.gd`), with the last lines above; M15 wires the endings to them.
- **M9.** How each style plays on screen and its timing (`docs/death.md`): the implied struggle 1.2 s, gory 0.6 s, the throat's cut at 0.25 s; a pool of blood under every body.
- **M9.** The crypt's ring has twelve candle places (all eleven deaths that can come before Matins on night 6, and the last).
- **M9.** The hidden bodies by night: the well from night 1, the race culvert from 2, the kitchen beds from 3, the bell tower loft from 4, the chapter house flags from 5. The well, loft and flag bodies are described, not shown.
- **M9.** The choir brothers' names: Wulfric, Aldo and Piers, and Bede, who warns about the bread and hangs in the bell tower.
- **M9.** The book page's words (`docs/death.md`), and the 29 clues the porter can write (`game/story/clues.gd`), all DRAFT.
- **M10.** Which hallucinations each tier plays (`docs/drug.md`): whispers, steps behind and the name at 25+; a shape at the edge and a face in the grain at 50+; hooves that stop short and a death that never happened at 75+. The fake deaths are these hallucinations, at random times.
- **M10.** Six carved saints in the cloister, nave and choir, for "carvings that turn their heads".
- **M10.** The jump scares are a body dropping on a rope and a face at the grille.
- **M10.** The candle that lights itself stands by the crypt's ring of rite candles, so it can't be mistaken for the count.
- **M10.** Mab's bread is from a baker in Fenchurch Street.
- **M11.** The three patrol routes (cloister and church, graveyard and infirmary, outer court and cellar) and who wears the costumes by default: Ranulf, Cole, Dunstan.
- **M11.** The brothers' routines (`docs/abbey.md`); only Thomas, Osric, Hugh and Ranulf keep one so far; the rest are in bed after Compline.
- **M11.** The lane's rumours that teach the saving rules (`game/story/rumours.gd`), DRAFT lines, given to Hob and Agnes.
- **M12.** Every line of night 0 and the lane at dusk (`game/dialogue/night0/`, `game/dialogue/lane/`, DRAFT), including facts they add: Mab's "More go in than come out"; Ralph's sacrist buying far more candles since Michaelmas, paid in coin the abbey never had; Roger wanting word of any merchant who goes in at the gate; Agnes hinting on night 4 that a guest should bar his own door; Gib on night 3 saying the dead man "smelled like a church"; Mab's bread making "the rooks scream at nothing".
- **M12.** Flags the drafts set for later nights to read: `n0_roger_agreed` (he promised Roger word of merchants), `n0_hob_jankin` (he heard that Hob puts Jankin out at closing), `lane_kit_n4_look` (he promised Kit to look for the candles), `mab_alms_<night>`.
- **M12.** Night 0's drinkers at the Keys: Jankin, Walter, Roger and Ralph. The traveller and the carter talk on the ride; the carter won't wait while he knocks.
- **M12.** The killing from the window: a guest with a lantern, killed by the well by a figure in a black habit with its back to the window, then dragged toward the cellar. Drunk, his note says he isn't sure what he saw.
- **M12.** Day 1 starts in his room at the Keys with Cole at the open gate; the tour's six stops and Thomas's lines (DRAFT, `tour_beat.gd`); Anselm also says the old porter locked the guests in.
- **M12.** The lane's dusk talks run on every night; night 3 keeps its own Mab, carter and Margery.
- **M12.** In an implied death the victim's lantern is lit, so the struggle is shapes against its light; dropped, it burns low on the ground.
- **M12.** After the tour Thomas and Anselm don't walk him to his cell: Thomas leaves for the infirmary, Anselm stays to warn him, and the duty flame leads him to his cot.
- **M12.** The cell's squint looks straight out across the lane at the houses opposite; the gate, in the same wall 4 m away, is out of its 25°.
- **M13.** Every line of nights 1 to 3 (DRAFT): the brothers' dusk talks (`game/dialogue/night1/`, `night2/`, `night3/`), the gate visitors and the beats' lines (`docs/nights.md`). Facts they add: the merchant is Geoffrey Pykard of Coventry, sober at the gate, his wife sick since Lammas; the sailor is Adam Cobb, his bundle tied with a seaman's knot; Walter "known at this gate since before you were breeched"; Joan hides her brother's badge on a cord and brings nothing; Roger wears a seal ring and wants the merchant's purse; Anselm kept the gate thirty years and was "the old porter" who locked the guests in; Bede sang in the third stall on the left, threw his bread over the wall, taught Edwin his letters, and hanged barefoot; Thomas says the prior was up the tower stair first on night 2, says the knock was boys from the lane, and calls Bede's fasting the cause of what he "sees in the rafters"; the kitchen bled a beast (Osric says a pig) by the well; Hugh's rule that no one comes in after the bell without him, and his "drunk men drown with their purses on"; Osric's rye "came in damp"; Ranulf counts every candle and alone holds the reliquary's key; the abbot dreamed of something counting on its fingers at the foot of his bed.
- **M13.** The sailor knocks after the curfew bell on night 2 and says he'll be gone before first light (the design doc: "leaving before dark"), so turning him away is how a porter puts someone in the lane on night 2. Let in, he's gone from his bed by the round and his page is torn out: "one more empty bed than your ledger says". The `sailor_knot` note now reads "The only sailor this week came to my gate."
- **M13.** A ledger page is torn on night 2 only when the sailor was let in (his own page).
- **M13.** Night 1's merchant body is found at Lauds, when the brothers' shouting draws the porter to the fishpond, with Thomas there to give the house's account; Dunstan stands by with a boathook.
- **M13.** Night 2's dawn: the abbot speaks to the brothers in the outer court; the prior's three answers set `n2_told_hugh` (the gate, the round, or everything, which costs Hugh's trust 5).
- **M13.** The crypt pilgrim is killed in front of the hunter, who is turned so his back is to the stair; the page of the book lies by the crypt's altar from night 3 on.
- **M13.** Bede appears only on night 1 (a `nights` list on each brother); the hooded stranger only on night 3.
- **M13.** Flags the night-1 and night-2 talks set for later scenes: `n1_thomas_well` (he told Thomas what he saw from the window), `n1_thomas_whisper` (told or kept Anselm's warning), `n1_hugh_why`, `n1_osric_beast` (+5 Suspicion), `n1_edwin_squint`, `n2_thomas_bread` (+5), `n2_hugh_lock` (and the `merchant_purse` note), `n2_osric_bread` (+5), `n2_ranulf_ralph` (+5), `n2_godric_counsel`, `n2_choirb_bede`.
- **M14.** Every line of nights 4 and 5 (DRAFT, `game/dialogue/night4/`, `night5/`, the visitors and the beats' lines). Facts they add: Mab has sat outside the gate eleven years; she saw three horned things taller than men come out of the mill race where it runs under the wall, smelling of incense, and one slipped and swore; the night-4 pilgrim is Richard Payne, a glover of Maidstone, with an eating knife; Joan says there was no husband, her brother came before Michaelmas with money sewn in his coat; Roger's sergeant is Nicholas Kene; Thomas gives the porter an alibi for night 3 and says the masked man was "as tall as the prior"; Simon has been "Thomas's shadow" since Thomas nursed him through a fever at Michaelmas; Simon says the blood on the flags is wine, and found a loose flag by the chapter house (the hidden body); drugged, Edwin says "You've eaten bread from its hand. So have I."; Osric stumbles in the fog, swears and puts the mask back on; the guest's cuts are laid in rows and crossed, "as if someone had been writing on him"; the masked man leaves the chapter house by the slype; the abbot lifts the fast after Prime on day 5 and won't send for the bishop; the key is on a loop of cord under the rye; Hugh: "I've been watching the wrong man".
- **M14.** Joan can be body 5 though named outsiders never die in view: she's found dying under the grain, not killed in front of him.
- **M14.** The night-4 guest's body isn't moved by the cult (the merchant's and Edwin's are).
- **M14.** No Matins chase on night 4: the round's set pieces come in order (the fog, the guesthouse, the charnel house, the two hunters, Simon), each led by the duty flame.
- **M14.** Night 4's two hunters are Osric and Ranulf; night 5's are Cole and Dunstan.
- **M14.** On night 5 the plank closet's door to the hidden stair is locked until he finds the key in the grain.
