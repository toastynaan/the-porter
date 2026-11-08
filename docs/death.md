# Deaths and bodies (M9)

How people die in front of the porter, what's left after, how he finds bodies and whom he tells, the rite's count, and being seen somewhere he shouldn't be. The story is in `docs/full-game-run.md` ("Deaths and bodies", "The rite"); the rules are in `docs/mechanics.md` ("Investigation", "Being seen", "The payoff"). Numbers marked *mine* are starting values to tune.

## Try it

Run `game/encounters/death_demo.tscn` (F6): night_base with three deaths, a hallucinated one, a body the cult moves, and the cult's book page in the crypt. `test_death` and `test_bodies` play them; `tools/m9_shots.sh` takes stills.

## A death (`DeathScene`)

A `DeathScene` node stands where the victim stands, facing -Z. A night's beat calls `play()` when the porter is where the night wants him; control is never taken away. Its exports: `id` (the flags `died_<id>`, `fed_<id>`), `style`, the `victim` (someone already in the world, a Brother or a visitor, put there at `play()` and taken out as he falls) or a `victim_look` to stand there, the body's `appearance` (colours), the killer, `rite`, `fake`, `lantern`.

| Style | On screen | Timing *(mine)* |
| --- | --- | --- |
| Implied | The two of them shake together, half-seen; a cry cut off; then the body. With `lantern`, his lantern falls and rolls | 1.2 s struggle |
| Gory | One blow; blood up the wall at the `Spray` marker; the body left as it fell, its blood round it | 0.6 s struggle |
| The throat | One quick cut and blood flying through the light (particles in old-blood red), a spray on the floor ahead, then down | the cut at 0.25 s |

Every style leaves a pool of blood where the body falls (0.4 s after it).

- **The killer** is the demon costume by default, which renders by Dose: sober, a man in a mask; drugged, the demon, taller, with ember eyes, and from 75 long fingers and branching horns. Or `killer_node`, someone already there (the night-3 hunter). He never moves while the porter looks: he's gone once the porter has looked away for half a second, unless a beat keeps him (`turn_to`: he turns to the porter, in danger).
- **The body** falls as a ragdoll on the kept ragdoll system (`Corpse`, `game/characters/chr_body.tscn`, built on `game/ragdoll`'s rig in the victim's colours) and stays where it comes to rest. The ragdolls took to the abbey without trouble, so no scripted poses were needed.
- **A real death** sets `died_<id>` and, with `rite`, feeds the rite a soul. A brother whose name matches (`died_edwin`) is out of the world from then on, on every night.
- **A fake death** (`fake`, a hallucination at Dose 75+) plays the same, but feeds nothing and keeps no blood: once the porter has looked away for 1 s *(mine)*, the body, the blood and the killer are gone. Which fakes there are is M10's.
- **After a save,** a death that has happened puts its body back where it lay.

## Blood that stays (`BloodMarks`)

Every mark a death leaves is kept (`GameState.marks`) and stands in the abbey on every night after, under the night's `BloodMarks` node. Four kinds, one scene each in `game/world/props/`: `prop_blood_pool`, `prop_blood_spray` (up a wall), `prop_drag_marks`, `prop_blood_print` (a boot print). All are decals in old blood (#5A1A14) that don't paint the characters. Each dawn, as the porter sleeps, the cult scrubs what would prove men did it (drag marks, boot prints) and misses the rest, so the abbey gets worse night by night.

## Finding bodies (`FoundBody`)

A `FoundBody` is where a body lies: a ragdoll lying dead, or `figure`, a posed character (hanging, sitting). Looking at it within 14° from 5 m or closer for 0.6 s *(mine)* finds it: `found_<id>`, the porter says his `line`, and his `clue` goes in his notes.

**Moving bodies.** A body with `moves` (one that would prove a man did it: the merchant, Edwin, the night-4 guest) is taken by the cult once the porter leaves it to fetch someone: when he's 20 m off and can't see it for a second *(mine)*, it's gone, with the drag marks and prints it left. Coming back, he finds the place empty, says so, and notes it (`moved_clue`).

**Hidden bodies** (`HiddenBody`, five in `night_base.tscn` under `HiddenBodies`): earlier victims, each with a pilgrim's badge whose name was torn from the ledger, there from their night on. Each is found by doing the thing at its `Reveal` marker, mostly by holding E for 1.5 s *(mine)*. Finding one makes a noise: the nearest hunter on his rounds comes to look.

| Body | From | Found by | Seen? |
| --- | --- | --- | --- |
| Down the well | Night 1 | Drawing water: the bucket comes up heavy | Described, not seen |
| The mill race culvert | Night 2 | Wading past the wheel (walking into it) | Yes |
| The kitchen beds | Night 3 | Digging at the turned earth | Yes |
| The bell tower loft | Night 4 | Climbing the ladder past the bell | Described |
| Under the chapter house flags | Night 5 | Lifting a loose flag | Described |

## Reporting (`Report`)

Whom he tells about a body: **Brother Thomas** (safe now, dangerous later: Thomas tells the cult, and each body told to him is Suspicion +5 at the next dusk), **the prior** (+10 at once, because Ranulf overhears, and the prior suspects him: `hugh_suspects`), or **no one** (nothing, unless a brother saw him by the body; then the cult knows he found it and kept quiet, +15, the design doc's number). `reported_<id>` holds whom, for the dawn and what follows. `Report.ask()` offers the choice; the nights put it at dawn, or in Thomas's and the prior's conversations.

## The rite (`Rite`, `RiteCandles`)

`game/story/rite.gd` lists the eleven deaths that can feed the rite: six always come (the bell-tower brother, the crypt pilgrim, Edwin, the fog brother, body 5, Anselm), five can be stopped (the merchant, the lane death, the night-4 guest, Simon, Roger's sergeant). `GameState.feed_rite(id)` counts each once. By night 6 the count decides the Saint: 8 or fewer, a shadow in the crypt; 9, it walks; 10–11, it hunts. The last soul at Matins on night 6 is Simon if he lived, otherwise a pilgrim.

**The crypt keeps count:** twelve candle places in a ring in the crypt (`RiteCandles`), and one is lit for each soul, in order. The ring has room for all eleven deaths and the last.

**The cult's book** (`Readable`): a page lies by the crypt altar. Reading it (E) holds the page up (`PageView`), puts it in the satchel as `book_page` and notes it. The page says what the candles are for. DRAFT text:

> ...and he who is hungry shall be fed in six nights, ten souls and no fewer, and for every soul a candle, that he may count them. The last shall be given him at Matins of the sixth night, in the place beneath the altar. Then shall he rise who was hungry, and go out at the gate, and walk in the city, and be fed.
>
> *(Under the words, ten candles drawn in a ring around a tall figure with no face.)*

## The ledger's notes

The ledger has a second page: press L once for guests and duties, again for the notes, a third time to put it away. Notes are in the porter's hand, oldest first, under each night (`GameState.note(id)`, once per id). `game/story/clues.gd` holds every clue the game can write (29 now), DRAFT lines.

## Being seen (`Restricted`, `SeenWatch`)

Places he shouldn't be seen are boxes under `Restricted` in `night_base.tscn`, each with the hour it starts to count: the crypt and its passage (any time), the granary and stores (after Compline, 20:00 *(mine)*), the dormitory floor (from 20:00). The ground within 4 m *(mine)* of a found body counts too. A brother in the world who can see him there by the hunters' sight rules (lantern light, distance, his view) sees him: Suspicion +10, once per place per night (`n<night>_seen_<place>` holds who). It comes up at dawn: `SeenWatch.remarks()` gives the lines ("Prior Hugh saw you in the crypt last night, and has said so.").

## The prior's judgement (`PriorJudgement`)

At dawn on night 5 the prior believes the porter if he can show two different kinds of proof (a costume, a purse, the relic, the book: `Items.proof_kinds`) or has six clues in his notes. M14 stages the arrest.

## Names

The choir brothers needed names for the lines that mention them: Brother Wulfric, Brother Aldo and Brother Piers, and Brother Bede, who warns about the bread on night 1 and hangs in the bell tower on night 2 *(mine)*. `game/story/people.gd` holds everyone's name and starting trust.

## Tests and tools

- **`test_death`:** each style plays: sober and drugged killers, the body falling and settling, the pool, the spray, the blood flying; the killer gone when unseen; a soul and a candle for each; the hallucination that leaves nothing; bodies and blood after a reload; the dawn scrub.
- **`test_bodies`:** finding and the note; the cult moving a body and its drag marks; coming back to nothing; reporting to Thomas, the prior or no one; being seen in the crypt and the granary (before and after Compline), once per place; the remark at dawn; the prior's judgement; the book page; two hidden bodies and their nights; the rite's count and the Saint's strength.
- **`tools/m9_shots.sh`:** stills to `art/_review/m9/`.
