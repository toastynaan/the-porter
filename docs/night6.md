# Night 6 and the endings (M15)

The hunt, the Hungry Saint, the proof, the rite, fire, and the seven endings. The story is the design doc's ("The Hungry Saint", Night 6, Endings); the rules are `docs/mechanics.md`'s ("Night 6"). Numbers marked *mine* are starting values to tune. Every line is DRAFT.

## The night (`game/chapters/night6/night6.tscn`, snow)

The routine is gone: no supper, no gate, no duties.

| Beat | What happens |
| --- | --- |
| Wake | Dusk. In the infirmary in Thomas's care, or in his cell if the prior believed him (`thomas_custody`, `prior_believes`) |
| Anselm | Anselm dead in his bed, his blind eyes open and his mouth stuffed with henbane leaves (body 6, fed to the rite; a note) |
| Wine | Thomas brings him a cup of spiced wine "for the cold". Drunk: Dose +40, and if he's caught tonight he wakes in a habit (the New Faith). Refused to his face: Suspicion +20 (`Wine`) |
| Hunt | The quiet save. The whole cult but Thomas is out in costume: four hunters (`Hunt.count_override`), with blades |
| Knock | 20:00 *(mine)*: a knock at the gate. Roger if the merchant or his sergeant died; otherwise Joan, if she's alive and he took her in or turned her away; otherwise Mab. He can answer at the grille all night: open the gate for Roger with two kinds of proof and his men take the abbey; without them Roger waits outside. Let Joan or Mab in and she goes with him (`Companion`) |
| Rite | The quiet save. From 23:00 *(mine)* the last soul (Simon if he lived, otherwise a pilgrim) lies bound in the crypt's ring with Thomas, unmasked, reading from the book, and the Saint wakes. Before the Matins mark he can stop it: free the victim (hold E at the cords for 3 s) or take the book from its stand. Otherwise at Matins the last soul is given |
| ToDawn | Nothing more is asked of him. The night is held open until an ending |

**The proof** lies in the crypt passage (`Proof`): the masks on their pegs, the carved hoof soles, a chest of pilgrims' purses (with the names torn from the ledger), the relic in the crypt (a boiled pig's knuckle), and the book on its stand by the ring. The page from night 3 counts as the book.

**The Demon** (`DemonChoice`): at Dose 75+, from 22:30 *(mine)*, "the demon" comes for him with a light (the prior, coming to help). When it's within 3 m he can strike it, the only time he can (the Demon ending), or run.

## The Hungry Saint (`game/demon/hungry_saint.gd`)

It wakes as the rite begins, its strength the count so far:

| Count | It |
| --- | --- |
| 8 or fewer | A shadow that can't leave the crypt (within 10 m *mine* of its home there) |
| 9 | Walks the abbey at 0.9 m/s |
| 10–11 | Walks at 1.2 m/s, and kills any cultist it meets |

It walks the navmesh toward him, finding its way again every 2.5 s *(mine)*; doors, locks, darkness and hiding don't stop it. Its touch (1.1 m *mine*) is death. Silence comes 25 m before it (the animals and the wind stop) and his lantern dims to a third within 8 m.

**Its kills** (`SaintKills`, only once it walks): Dunstan in the cloister, Cole at the gate, Osric in the choir, each the first time he comes within 14 m *(mine)* after it wakes.

## Fire (`game/world/fire/fire.gd`)

Hold the lit, uncovered lantern to a marked spot (the granary's sacks, the crypt's hangings) from within 2.5 m *(mine)* for 2 s and it catches. It spreads along its path at 1 m/s, a flame a metre. Within 3.5 m *(mine)* of a flame is smoke: sight drops to 3 m and he chokes; 6 s of breathing it is death, and holding his breath stops the choking. A flame within 0.9 m kills. The crypt's fire burns the book if it's still on its stand.

## The endings (`Night6Ending`, `game/endings/endings.gd`)

Checked in this order:

| Ending | When |
| --- | --- |
| The New Faith | Caught tonight after drinking the wine (`CaptureFlow`) |
| The Demon | He struck "the demon" |
| The Rising | The rite finished at Matins with the count at 9 or more |
| The Fire | He leaves (or holds out) with the granary and the crypt burned and the book in the fire |
| The Gate | He opened the gate for Roger with two kinds of proof |
| The Witness | Out by the mill race (where it runs under the wall, `Marks/RaceExit`) with Mab or Joan alive at his heels |
| The Broken Rite | Any other way out (the gate into the lane, the race alone), or he holds out to Lauds |

Each ends with its lines, then the night (`NightDirector.end_night`) and the chronicle (`GameFlow`).

## Tests

- **`test_endings`:** every ending by its own scripted route from night 6's dusk, played through the game's flow as the last chapter and ending in its own chronicle; plus Anselm's body, the wine and refusing it, the Saint's strength at 8 and 9, the fire catching and spreading, the book burning, Roger and Joan at the gate, stopping the rite by taking the book.
- **`test_night6`:** the Saint's speed at 8, 9 and 10, through a locked door, the animals falling silent, Dunstan, Cole and Osric taken as he comes near, a cultist killed at full strength, its touch; freeing the victim by holding E at his cords; no demon for him sober; choking in the smoke only when he breathes it, and the flames.
- **`test_flow`:** New Game through all eight chapters, night 6 played to the Broken Rite and its chronicle.
