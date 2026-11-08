# Nights 1 to 3 (M13)

The first three nights as built: nights 1 and 2 teach the routine, night 3 breaks it. The story is the design doc's night-by-night script; the rules are `docs/mechanics.md`'s. Each night is a scene that inherits `night_base.tscn` (`game/nights/night1.tscn`, `night2.tscn`, `night3.tscn`); its Director runs one beat per child, in order. Every line a beat says is an inspector setting on that beat ("Name: words", or a line in brackets for what the porter notices), and every conversation is a file in `game/dialogue/night<N>/`. All of it is DRAFT. Times marked *mine* are starting values to tune.

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

## The gate visitors

`game/gate/visitors/`: `merchant_n1`, `walter_n1`, `joan_n2`, `sailor_n2`, `roger_n2` (new), `walter_n3` (a real greeting, and a question about his bag). New characters: `chr_merchant` and `chr_sailor`.

## Tests and tools

- **`test_night1`:** played twice: left unlocked, Bede's warning, both visitors in the ledger, all present at Matins, one glimpse, the knock with no one, the merchant taken and found in the pond, Thomas's lie, whom to tell; locked in, the merchant lives and curses; Walter turned away before the bell goes to the Keys.
- **`test_night2`:** played three times: Thomas's word at supper, Roger asking after the dead merchant, the sailor turned away after the bell killed in the lane and Gib silent, Bede and the sailor's knot, one short, the abbot and the prior; the sailor let in and Jankin killed, the empty bed and the torn page; Jankin kept in and no one killed in the lane.
- **`test_night3`:** as before, plus the crypt death fed to the rite and the figure turning, the book's page, Thomas's aside, and the copied keys.
- **`test_flow`:** New Game through night 0, day 1 and nights 1 to 3 played in full, then the stubs; the rite holds four souls by night 3's dawn.
- **`NightPilot`:** `play_night1`, `play_night2` (with the porter's choices), `to_the_gate`, `matins_and_round`, `lock_guesthouse`, and `gate_aware_choice` for tests that play whole nights.
- **`tools/m13_shots.sh`:** stills to `art/_review/m13/`.
- `tools/check.sh` now gives each test 7 minutes (`test_flow` plays four whole nights).
