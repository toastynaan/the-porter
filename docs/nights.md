# Nights 1 to 5 (M13, M14)

The first five nights as built: nights 1 and 2 teach the routine, and from night 3 each night breaks a step of it (the crypt breaks the round on night 3, there's no supper on night 4, night 5 opens with the dilemma). The story is the design doc's night-by-night script; the rules are `docs/mechanics.md`'s. Each night is a scene that inherits `night_base.tscn` (`game/nights/night1.tscn`, `night2.tscn`, `night3.tscn`); its Director runs one beat per child, in order. Every line a beat says is an inspector setting on that beat ("Name: words", or a line in brackets for what the porter notices), and every conversation is a file in `game/dialogue/night<N>/`. All of it is DRAFT. Times marked *mine* are starting values to tune.

## The shared beats, now set per night

| Beat | What's set per night |
| --- | --- |
| `Wake` | Its lines (what changed while he slept) |
| `Supper` | Seated, serving, eating and seen-palming lines; a `warner` and his lines (night 1: Bede, after the porter has eaten: sets `bread_warned`, writes the clue); an aside from someone at table (Thomas), unless he already heard it at dusk; the remedy and its lines (night 3) |
| `Gate` | Cole's lines handing over the gate |
| `Knocks` | The visitors and their hours; a visitor with `only_if` comes only if that flag is set (Roger); the prior's lines; the child's knock (night 3 only) |
| `Bell` | Night 2: `hanged`, a body shown as he pulls the rope, dropping past him |
| `Choir` | The lines once he has counted: all there, one short, one wrong |
| `Round` | How many times the shape appears (1 to 3) and the lines after the first |
| `SmallHours`, `Dawn` | Their lines. At dawn, before he sleeps, he decides whom to tell about each body he found and hasn't reported (`Report`). With `keys_moved` (night 3), the keys are on the cot with wax in their teeth: `keys_copied` |

New beats: `Taken` (the cult comes for a guest), `KnockNoOne` (M10's), `Pond` (`dawn_find_beat.gd`, a body found at Lauds), `Lane` (`lane_death_beat.gd`), `Guesthouse` (`guesthouse_check_beat.gd`) and `DawnScene` (`scene_beat.gd`, people at marks, their lines and one question with three answers, each with its reply and tags).

**Brothers by night:** a `Brother` lists the nights he's in the abbey (`nights`). Bede (`Brothers/Warner`, in `chr_choir_brother_dead`) is there only on night 1; the hooded stranger only on night 3, in Bede's stall.

## Night 1, the new porter (rain)

| Beat | What happens |
| --- | --- |
| Wake | 16:00. A fresh candle in his clock; the gate open with Cole at it; the brothers at their dusk places and the lane's people at the gate |
| Supper | The abbot welcomes the new porter; Osric serves him an extra heel of bread; he eats it (he hasn't been warned); then Bede, beside him, tells him quietly not to eat the bread |
| Gate | Cole gives him the gate |
| Knocks | 19:00 the merchant, Geoffrey Pykard of Coventry, with a question he can ask first; 20:15 Walter *(mine: both before the curfew bell, so turning either away sends him to the Cross Keys)* |
| Bell, Choir | Matins: all present. The first incense |
| Round | Three stops; after the first, the tall horned shape stands still at the far end of the walk, and is gone when he looks again |
| Taken | 01:30 *(mine)*: if the merchant is in the guesthouse and nothing keeps him safe (the guesthouse locked, on nights 1–3), the cult takes him: `died_merchant`, fed to the rite |
| KnockNoOne | 02:00: the knock, until he comes to the grille; no one |
| SmallHours | To Lauds |
| Pond | At Lauds, if the merchant died: shouting from the fishpond; the duty flame leads him there; his lantern catches a face under the surface, and it rolls over (found: rope marks on the wrists). Thomas kneels by it: "He drowned drunk". The body is one the cult moves. If the merchant lived because he was locked in, he leaves at first light cursing the porter for it |
| Dawn | Cole takes the gate; whom to tell about the merchant; sleep |

## Night 2, the bell (rain)

| Beat | What happens |
| --- | --- |
| Wake | His ledger lies open, though he shut it |
| Supper | He may palm the bread now. If he didn't speak to Thomas at dusk, Thomas tells him at table that he has seen the prior about the house at night (his dusk talk says it first if he goes to him: `n2_thomas_prior`) |
| Knocks | 19:00 Joan, asking sanctuary; 20:00 Roger the bailiff, only if the merchant died, asking after him; 21:30 the sailor, Adam Cobb, after the curfew bell *(mine)*: he wants a bed till the tide and says he'll be gone before first light; no tar on a sailor's hands |
| Lane | 23:15 *(mine)*: if anyone dies in the lane tonight, a cry, and Gib's call doesn't come. At the grille, under the lantern by the chandler's, a man is killed: the throat; the tall shape behind him never moves while he looks. It's the sailor if he turned him away after the bell (no named outsider ever dies in view), otherwise Jankin, put out of the Cross Keys at closing, unless he asked Hob at dusk to keep him in; then no one, and the lane stays quiet. Fed to the rite as the lane death |
| Bell | The rope is heavy. Bede drops past him, hanged from the bell's frame, barefoot, with a sailor's knot under his ear (found, fed to the rite, a clue) |
| Choir | One short: Bede's stall is empty |
| Round | Two appearances, then the guesthouse: if he let the sailor in, the sailor's bed is empty though the gate is still barred, and his page is torn from the ledger (`GameState.tear_ledger`) |
| SmallHours | To Lauds |
| DawnScene | In the court the abbot declares that a demon has come into the house and orders incense at every office, twice the measure; the prior takes him aside: where was he in the night? Three answers (`n2_told_hugh`) |
| Dawn | Cole; whom to tell about Bede; sleep |

## Night 3, brought into line

- **Supper:** the bread is bitter; Thomas tells him quietly that the prior has been asking about him; then Ranulf's remedy, and Thomas's warning.
- **The crypt:** at the foot of the stair the figure by the light has his back to him because he is killing a bound pilgrim (gory, `CryptPilgrim`, fed to the rite). Then the figure turns and looks straight at him, and the chase starts. A page of the cult's book lies by the altar (`BookPage`).
- **Dawn:** the keys are on the cot with wax in their teeth: copied (`keys_copied`; from night 4 a locked guesthouse saves no one).
- Every placeholder line is gone: the night's conversations and lines are drafted.

## Night 4, Edwin (fog)

Night 4 is the midpoint. From tonight the incense can be avoided by the choir's west door, hunters talk and carry blades, and the well doses (`docs/drug.md`, `docs/abbey.md`).

| Beat | What happens |
| --- | --- |
| Wake | Fog. No supper tonight: the abbot has ordered the house to fast against the demon, and the refectory is locked. No supper bell |
| Edwin, Thomas | At dusk the duty flame leads him to Edwin, by his cell, who whispers that he has seen the demon's face and will tell after Matins; then to Thomas by the gate, who has seen Brother Simon out at night (`SceneBeat`) |
| Fast | At the supper hour, nothing: the refectory door is locked |
| Knocks | 19:00 Mab, asking to come inside the gate for the first time: she saw three horned things come out of the mill race; 20:00 a pilgrim, Richard Payne, a glover of Maidstone. Shown to his bed, the porter can tell him to bar his door from inside (the visitor's `warn_line`: `Warnings`) |
| EdwinDies | 23:00, out of sight: Edwin is dead, and laid out in the charnel house (`offstage_death_beat.gd`) |
| Bell, Choir | Matins: Edwin's place is empty (a note) |
| Round | The three stops, no shape tonight |
| Fog | The quiet save. On the north walk, a few steps ahead in the fog, a cry: Brother Wulfric is killed (implied; his lantern still rolling on the flags when he reaches him). Out of the fog the prior comes and kneels by the body, and when he rises there's blood on his sleeve (`witness_beat.gd`) |
| Guest | If he let the pilgrim in and didn't warn him, the guesthouse door stands open and he's killed as the porter comes to it: gory, the rite's cuts. Warned, he answers through the barred door: someone tried it an hour ago and called his name (`guest_death_beat.gd`) |
| Charnel | Edwin among the bones (found; the comb's rows of cuts; a body the cult moves). Drugged, Edwin sits up and speaks (`find_beat.gd`) |
| Hunters | Two hunters at once, for the first time, out in front of the charnel house: the demon in two places (a note). Osric's comes close, and his mask comes off: seeing his face is a note (`two_hunters_beat.gd`). Caught, he dies. The chase is over once neither has chased or searched for 6 s *(mine)* |
| Simon | On the cloister flags Brother Simon on his knees, scrubbing blood; he hides the rag and says it's wine (a note) |
| SmallHours, Dawn | Lauds; in his cell the cot is soaked and the candle clock snapped (`cell_lines`) |

## Night 5, the granary (clear)

| Beat | What happens |
| --- | --- |
| Wake | A cry from the chapter house |
| Dilemma | The quiet save. In the chapter house Thomas lies on the floor, "attacked", and a masked man pins Brother Simon. He can reach only one (`dilemma_beat.gd`): reaching Thomas, Simon's throat is cut behind him and the masked man turns and looks at him, then goes; reaching Simon, the masked man lets go and leaves by the slype, Thomas gets up bloodied anyway, and Simon tells him Thomas sent him to scrub the blood (a note; Simon's trust +20 *(mine)*). `n5_saved` |
| Supper | Osric serves and smiles; Thomas, his arm bound, looks into the porter's eyes |
| Knocks | 19:00 Joan, only if he turned her away on night 2, back with her brother's badge; 20:30 Nicholas Kene, Roger's sergeant, sent to watch the gate, asking to wait inside it till dawn |
| Bell, Choir | Matins: the abbot falls in the smoke |
| Anselm | In the confusion Anselm grips his sleeve: the key to the crypt passage is under the rye in the granary |
| Granary | The quiet save. In the grain his hand meets a hand: Joan, if he let her in on night 2 or tonight (alive, then not), otherwise a pilgrim long dead (body 5, fed to the rite); the rye is black-spurred (a note); the key, on a loop of cord (the plank closet's door to the hidden stair is locked tonight). Then the cult bars twenty doors of the west range, the church and the dormitory's ground floor behind him and two hunters come, one in the granary and one in the choir; the sergeant, if left in the lane, is killed (heard over the wall). The way out is down the hidden stair, through the crypt (the candle that lights itself), the choir, up the night stairs and down the latrine chute into the mill race. Out, the hunters go and the doors are unbarred (`granary_beat.gd`) |
| SmallHours | To Lauds |
| Arrest | At the gate the prior and two brothers take him and arrest him for the killings. Two kinds of proof or six notes (`PriorJudgement`): he believes him, lets him go and will stand with him tonight (`prior_believes`, the prior's trust +40 *(mine)*); otherwise Thomas speaks for him and takes him into his care (`thomas_custody`) (`arrest_beat.gd`) |
| Sergeant | At dawn, if he died: his lantern smashed in the lane, and blood |
| Dawn | Cole; sleep |

## The gate visitors

`game/gate/visitors/`: `merchant_n1`, `walter_n1`, `joan_n2`, `sailor_n2`, `roger_n2`, `mab_n4`, `pilgrim_n4`, `joan_n5`, `sergeant_n5`, and `walter_n3` (a real greeting, and a question about his bag). New characters: `chr_merchant`, `chr_sailor` and `chr_simon`; Brother Simon (`Brothers/Simon`) is in the abbey on nights 4 to 6.

A conversation's `[if ...]` now also holds for a clue in his notes (`[if osric_mask]`: he has seen Osric's face).

## Tests and tools

- **`test_night1`:** played twice: left unlocked, Bede's warning, both visitors in the ledger, all present at Matins, one glimpse, the knock with no one, the merchant taken and found in the pond, Thomas's lie, whom to tell; locked in, the merchant lives and curses; Walter turned away before the bell goes to the Keys.
- **`test_night2`:** played three times: Thomas's word at supper, Roger asking after the dead merchant, the sailor turned away after the bell killed in the lane and Gib silent, Bede and the sailor's knot, one short, the abbot and the prior; the sailor let in and Jankin killed, the empty bed and the torn page; Jankin kept in and no one killed in the lane.
- **`test_night3`:** as before, plus the crypt death fed to the rite and the figure turning, the book's page, Thomas's aside, and the copied keys.
- **`test_night4`:** played twice: the fast, Edwin's whisper and Thomas on Simon, Mab and the pilgrim let in, Edwin missing, Wulfric in the fog and the prior's sleeve, the guest killed, Edwin in the charnel house, two hunters and Osric's face, Simon scrubbing, the violated cell; then the pilgrim warned, and living.
- **`test_night5`:** played twice: Simon saved and his word about Thomas, the sergeant inside and alive, Anselm's word, a pilgrim's hand and the key, out down the chute, Thomas's care; then Thomas saved and Simon killed, Joan back and the hand in the grain, the sergeant killed in the lane, the prior believing him with two kinds of proof.
- **`test_flow`:** New Game through night 0, day 1 and nights 1 to 5 played in full, then night 6's stub; the rite holds four souls by night 3's dawn and seven by night 5's.
- **`NightPilot`:** `play_night1` to `play_night5` (with the porter's choices), `to_the_gate`, `take_gate`, `matins_and_round`, `lock_guesthouse`, `hand_over_and_sleep`, and `gate_aware_choice` for tests that play whole nights (answer[1] answers a warning at a guest's bed).
- **`tools/m14_shots.sh`:** stills to `art/_review/m14/`.
- **`tools/m13_shots.sh`:** stills to `art/_review/m13/`.
- `tools/check.sh` now gives each test 7 minutes (`test_flow` plays four whole nights).
