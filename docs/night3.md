# Night 3 in the greybox (M4)

Night 3, "The oven", runs start to finish as the design doc scripts it. Press F5 and the game opens at supper. Every line is a placeholder in brackets that describes the beat in the design doc's words. Choices take the number keys, or the arrow keys and E. Press L to hold up the ledger.

## The beats

`game/nights/night3.tscn` holds the night. Its `Director` runs one beat script per child, in order (`game/night/*_beat.gd`). Each beat waits for the porter to do his duty before it moves on.

| Beat | What happens | Where it comes from | Flags it sets |
| --- | --- | --- | --- |
| Supper | You sit at the refectory table and can look but not walk. Osric serves bread; use the bread to eat it or palm it. Thomas offers a remedy | Core loop 1; night 3 "the bread tastes bitter. Thomas offers a remedy" | `n3_ate_bread` or `n3_palmed_bread` (+ `hungry`, `n3_osric_saw`), `n3_took_remedy` or `n3_refused_remedy` |
| Gate | Bar the gate (E at the gate), then open the ledger at tonight's page on your cell desk | Core loop 2 | `gate_barred`, `n3_ledger` |
| Knocks | Walter comes up the lane with his lantern and knocks at the grille (see "Keeping the gate" below). At Dose 50+, a small knock low on the gate, with no one there | Core loop 3; night 3 knocks | `n3_walter` (admitted / refused / prior), `n3_child_knock` |
| Bell | Ring the bell rope in the tower. Midnight. **The night saves here** | Core loop 4 | the `matins` bell save |
| Choir | Go to the choir. The incense is lit. Count the brothers by looking at each one. In the dead brother's place stands a hooded stranger, or, drugged, the dead brother | Core loop 4; night 3 Matins | `n3_incense`, `n3_headcount`, `n3_saw_dead_brother` |
| Round | Check three stops: the stores door off the west walk, the chapter house door off the east walk, the sanctuary lamp. The demon appears at the end of the walk, then in a doorway, then behind you in the choir | Core loop 5; demon "Stalking" phase | `n3_round` |
| Crypt | After a quiet stretch, a light shows in the crypt with a figure by it, back turned. Go down and he sees you | Night 3 round | `n3_seen_in_crypt` |
| Chase | The hunter comes for you. The demon stands in doorways that lead away from the bakehouse. Hide in the oven and your hand closes on a jaw. When you climb out after his search he's nearly on you, and Thomas pulls you into the infirmary | Night 3 round; the chase rule "hiding" | `n3_body3`, `n3_thomas_hid_you`, or `n3_caught` |
| Dawn | Back in your cell. Your keys aren't on their hook; find them on the cot | Night 3 dawn | `n3_keys_moved`, `night3_done` |

**If you're caught in the chase:**
- **First capture:** you wake in the infirmary with Thomas over you, +40 Dose, and your keys gone. The night goes on to dawn.
- **Second capture:** it kills you, and the night starts again at the Matins bell.

## Keeping the gate

`game/night/gate_visits_beat.gd`. Visitors are data (`game/gate/visitors/*.tres`, class `Visitor`): a name, a build, a cloak, a greeting, and the details you can notice. Each detail has a part of him (face, body, hands, feet, box, bag), the porter's line, and the words that go into the ledger. Walter's come only from the design doc: plump, a coloured cloak (faded madder red), oily and cheerful, a box of "relics", and on night 3 a bag that smells of the incense.

1. **He comes up the lane.** Walter walks from the far end of the lane carrying his own lantern and stops under the porch lantern.
2. **He knocks.** He knocks until you come to the grille and press E. He greets you.
3. **You read him.** While the choice is open, look at a part of him for a moment and the porter notices it, for example "(His box of relics rattles.)". Only what you noticed goes into the ledger.
4. **You choose:**
   - **Admit him.** Lift the bar, open the gate, and he comes in. Shut the gate and bar it behind him. He follows you to the guesthouse, where you show him a bed (E on it) and he lies down. Then write him in the ledger at your desk.
   - **Turn him away.** He walks back down the lane and is gone.
   - **Send for the prior.** Suspicion +10, because Ranulf overhears. The prior comes, lets him in and takes him to a bed. You still write him in.

**The ledger** is held up with L (gamepad Back). It's a parchment page showing tonight's guests as you wrote them, then tonight's duties, with the done ones struck through. It counts as an object you carry, so it isn't a HUD, and the night goes on while you read.

To add a visitor, make a new `Visitor` resource and add it to the Knocks beat's `visitors` list. To restage the gate, move these markers and duties:
- markers: `Marks/LaneStart`, `LaneLeave`, `Porch`, `Inside`, `PriorFrom`
- duties: `Duties/OpenGate`, `ShutGate`, `GuestBeds/Bed0`–`Bed5`

## Finding the way

There is no HUD, so the world shows where the next duty is (`game/night/wayfinding.gd`):
- **A lamp at the duty.** While a duty is due, its lamp burns: at the gate, in the tower by the bell rope, by each door on the round. The ledger is lit by your cell candle, the sanctuary lamp is the lamp itself, and at dawn a candle stands by the moved keys.
- **Lit doorways on the way.** The doors on the path from you to the duty are opened, and a lamp hangs over each doorway on the duty's side, so each lit doorway leads to the next. They go out once the duty is done. Doors and lamps you're looking at are left alone, so nothing opens or lights in front of you.
- **Sound.** You can follow the knocking to the gate, and the Matins chant starts when you ring the bell, so you can follow it to the choir.

Each duty's lamp is its `lamp` export. Set `open_way` off on a duty to leave its route dark.

## Numbers

| What | Value | Source |
| --- | --- | --- |
| Bread | Dose +10, eased in over 90 s | +10 doc, timing mine |
| Remedy | Dose +15 over 30 s | +15 doc, timing mine |
| Palming seen by Osric, refusing the remedy | Suspicion +5 each | low end of the doc's +5 to +20 |
| Osric watches your plate after serving | 5 s | mine |
| Sending for the prior | Suspicion +10 | doc |
| Visitors' walking pace | 1.2 m/s | mine |
| Reading a detail | looking within 9° of it, from 4 m or closer, for 0.35 s | mine |
| Seen in the crypt | Suspicion +10 | doc |
| Incense | +25 over 8 s, and at least enough to reach Dose 50; Dose doesn't fall below 50 for the rest of the night | doc +25; floor of 50 is the M0 default |
| The stranger becomes the dead brother | Dose 50 (he changes only while you aren't looking) | mine: the tier where cultists start rendering as demons |
| Round clock | 60 s per in-game hour, so Dose decays 10 a minute toward 50 | mine |
| Quiet stretch before the crypt light | 20 s | doc wants 5–10 minutes; greybox length |
| In the chase, the oven doesn't give you up while you hold your breath | — | mine, so the scripted beat holds |

## Restaging it

Everything is a marker you can move in the editor, under `night3.tscn`:

| Node | What it holds |
| --- | --- |
| `Places/Supper/<Name>`, `Places/Matins/<Name>` | Where each brother stands in each phase. A brother only moves while you aren't looking |
| `Marks` | Your seat, the choir, the foot of the crypt stair, the infirmary spots for you and Thomas, Walter's guesthouse bed, your cell at dawn, and the Matins spawn |
| `Duties` | Things you use: the bread, the gate bar, the grate, the ledger, the bell rope, the round's stops (each has a `hint` and a `line`), and the moved keys |
| `Stalk/WalkEnd`, `Stalk/Doorways` | Where the demon may stand on the round, first choice first |
| `Stalk/Blockers` | During the chase, running near one of these puts the demon at its `Stand` |
| `CryptLight`, `Hunter` | The cult's light, and the hunter waiting by it |

The pacing waits are exports on each beat: Knocks `first_delay`, Choir `office_time`, Crypt `quiet_time`, Supper `watch_time`.

## Not built yet

- **Visible duties:** the candle clock, the ledger page and the gate grate aren't built. Lines in brackets stand in for them, along with a few routing hints, alongside the lit way.
- **Bodies on screen:** there are no hands in view, and the bell rope doesn't lift you.
- **Morning scene:** dawn doesn't show the abbey's official version of the night.
- **The brothers:** they're greybox figures with their builds from the character table. They don't move between places, sit, or have props or sounds.
- **Walter:** he's in a brown tunic until his coloured cloak gets a colour.

## Tests and tools

- **`test_night3`:** the whole night in order, with every beat's effects.
- **`test_gate`:** the gate job's three outcomes, reading, the ledger entry and the ledger page.
- **`test_night3_caught`:**
  - restarting at the Matins bell
  - being caught in the chase (infirmary, keys gone, dawn)
  - being caught twice (back to Matins, with the night as it was at the bell)
- **`tools/night3_shots.sh`:** plays the night and saves a still per beat to `art/_review/m4/`.
