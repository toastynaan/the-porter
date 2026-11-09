# Night 3 in the greybox (M4–M7)

Night 3, "The oven", runs from waking at dusk to sleeping at dawn, as the design doc's core loop and night 3 script it. It's the fifth chapter of a New Game (`docs/frame.md`); to play it on its own, choose it in Chapters once you've finished the game, or run `game/nights/night3.tscn` (F6), and you wake in your cell in the late afternoon. Every line and conversation is drafted (DRAFT); `docs/nights.md` has what M13 changed and how the beats are set per night. Choices take the number keys, or the arrow keys and E. Press L to hold up the ledger.

## The beats

`game/nights/night3.tscn` holds the night. It inherits `night_base.tscn`, which every night shares (the abbey, the people, the duties, the marks), and adds its `Director`, which runs one beat script per child, in order (`game/night/*_beat.gd`), and its conversations. Each beat waits for the porter to do his duty before it moves on.

| Beat | What happens | Where it comes from | Flags it sets |
| --- | --- | --- | --- |
| Wake | 16:00. You wake in your cell as the light fails. The gate stands open with Cole at it. Until the supper bell you can walk about, talk to the brothers at their dusk places, or step out into the lane, where Mab begs by the gate and two passers-by go home before dark. The supper bell rings at the candle's mark, 17:15 | Core loop 0 | the `start` bell save |
| Supper | Take your place at the refectory table; seated, you can look but not walk. Osric serves bread; use it to eat it, or, warned on night 1, palm it. Thomas tells you quietly that the prior has been asking about you. Ranulf offers a remedy for your headaches, and Thomas, beside you, warns you off it (the design doc's second review) | Core loop 1; night 3 "the bread tastes bitter"; `docs/drug.md` | `n3_ate_bread` or `n3_palmed_bread` (+ `hungry`, `n3_osric_saw`), `n3_took_remedy` or `n3_refused_remedy` (Thomas's trust +5) |
| Gate | Relieve Cole at the gate; he goes off into the abbey. Shut the gate and bar it, then open the ledger at tonight's page on your cell desk | Core loop 2 | `gate_taken`, `gate_barred`, `n3_ledger` |
| Knocks | At 20:00 Walter comes up the lane with his lantern and knocks at the grille (see "Keeping the gate" below). At 22:00, at Dose 50+, a small knock low on the gate, with no one there | Core loop 3; night 3 knocks | `n3_walter` (admitted / refused / prior), `n3_child_knock` |
| Bell | From 23:45 the bell rope is wanted. Ring it in the tower. After 00:30 it is late, and that is noticed. **The night saves here** | Core loop 4; the candle clock | the `matins` bell save, `matins_late` |
| Choir | Go to the choir. The incense is lit. Count the brothers by looking at each one. In the dead brother's place stands a hooded stranger, or, drugged, the dead brother | Core loop 4; night 3 Matins | `n3_incense`, `n3_headcount`, `n3_saw_dead_brother` |
| Round | Check three stops: the stores door off the west walk, the chapter house door off the east walk, the sanctuary lamp. The demon appears at the end of the walk, then in a doorway, then behind you in the choir | Core loop 5; demon "Stalking" phase | `n3_round` |
| Crypt | After a quiet stretch, a light shows in the crypt with a figure by it, back turned. At the foot of the stair, he has his back to you because he is killing a bound pilgrim (gory; the crypt pilgrim feeds the rite); then he turns and sees you. A page of the cult's book lies by the altar | Night 3 round | `n3_seen_in_crypt`, `died_crypt_pilgrim` |
| Chase | The hunter comes for you. The demon stands in doorways that lead away from the bakehouse. Hide in the oven and your hand closes on a jaw. When you climb out after his search he's nearly on you, and Thomas pulls you into the infirmary | Night 3 round; the chase rule "hiding" | `n3_body3`, `n3_thomas_hid_you`, or `n3_caught` |
| Small hours | Back to the gate. Doze on the bench until the Lauds bell at 06:00. On night 3 the main event was the crypt and the chase, so nothing interrupts | Core loop 6 | |
| Dawn | Grey light. Cole comes for the gate; give it to him and he opens it for the day. In your cell your keys aren't on their hook; find them on the cot, with wax in their teeth: copied. Lie down on the cot and sleep through the day | Core loop 7; night 3 dawn | `n3_keys_moved`, `keys_copied`, `night3_done` |

**If you're caught in the chase,** you die: from night 3 every capture kills (`docs/mechanics.md`, "Being hunted"). The night saves quietly as the Crypt beat starts, so death puts you back in the choir just before the crypt light (the `crypt` spawn), with the round done, not at the Matins bell.

**Lateness** (`docs/abbey.md`): supper, the Matins bell and the hand-over at dawn are watched: 15 minutes late is noticed (Suspicion +5), 45 brings Cole (at supper) or the prior to fetch you. From Suspicion 30 the prior watches you at supper.

## The candle clock

`game/night/night_clock.gd` (the `Clock` node). The night runs on in-game hours from 16:00 to 06:00 the next morning (hours past midnight count on: 30.0 is 06:00).

- **Awake, time runs slowly in real time:** 3 minutes an hour (2 with the faster-clock setting). Dusk to the supper bell is under 4 minutes, and the whole night is within the run's 30–40 minutes if you doze through the waits.
- **Dozing on the gate bench, it runs fast:** 2 seconds an hour, with the screen nearly black. Whatever needs you wakes you: a knock (the visitor is at the grille already when you wake), the Matins mark, the Lauds bell. You can doze only once you have the gate, while the night is waiting on it (the knocks, before Matins, the small hours), and while no duty is wanted.
- **The candle in your cell** (`CandleClock`, on the desk) burns down from 16:00 to 07:00, with rings at the supper bell, Matins and Lauds. Look at it and press E: "(The candle stands at 19:40. The next mark is Matins.)".
- **The bells** ring at the marks: supper at 17:15, Matins at midnight (you ring it, from 23:45), Lauds at 06:00.
- **The ledger** lists each duty with its time.
- **The candle waits for the night.** It doesn't burn past the mark of a beat the night hasn't reached, so however long the round and the chase take, Lauds and the morning wait for the small hours.
- **Dose decays as the clock runs,** at the doc's 10 an hour, while you're awake and while you doze.

## Dusk and dawn light

`game/night/daylight.gd`. From 16:00 to 17:30 failing daylight fades into night, and from 06:00 to 07:00 grey morning comes up. Day is overcast, flat and grey with no strong shadows (Look and Feel, lighting rule 6), so daylight raises the sky and the ambient light in the night's moonlight colour, with a soft shadowless light from the low sun's side. The lane's lanterns are lit once it is dark. The strength of each is an export on the `Daylight` node.

## People to talk to

At dusk, look at someone and press E: your view turns to their face for a moment, they say their line, and you pick one of three answers or walk away (see `docs/dialogue.md`). The brothers stand at their dusk places (`Places/Dusk`): Thomas and Anselm in the infirmary, Osric in the kitchen, Ranulf in the church, Godric in the chapter house, Hugh on the north walk, Edwin on the west walk, Dunstan by the woodpile, and the three choir brothers on the south walk, in the nave and on the east walk. In the lane are Mab, by the gate, and two passers-by, a carter and a woman with a basket, who go home at 17:30. Every line is a placeholder that gives the person's public face from the cast table. Each person has a `Talker` child (`game/npc/talker.gd`) naming their conversation (`game/dialogue/night3/`) and the phases they talk in. Mab can be talked to until the knocks; the brothers only at dusk.

Everyone wears a character scene from `game/characters/` (see `docs/assets.md`). Night 3 has eleven brothers in the choir: the seven named ones, the three living choir brothers, and the stranger in the dead brother's place. Dunstan, a lay brother, is about only at dusk.

## Keeping the gate

`game/night/gate_visits_beat.gd`. Visitors are data (`game/gate/visitors/*.tres`, class `Visitor`): a name, a build, a cloak, a greeting, and the details you can notice. Each detail has a part of him (face, body, hands, feet, box, bag), the porter's line, and the words that go into the ledger. Walter's come only from the design doc: plump, a coloured cloak (faded madder red), oily and cheerful, a box of "relics", and on night 3 a bag that smells of the incense.

1. **He comes up the lane.** At his hour (`knock_hours` on the Knocks beat; Walter's is 20:00) Walter walks from the far end of the lane carrying his own lantern and stops under the porch lantern. If you're dozing, he's at the grille when the knock wakes you.
2. **He knocks.** He knocks until you come to the grille and press E. You talk through the grille: your view turns to his face for a moment, and he greets you.
3. **You read him.** While the choice is open, look at a part of him for a moment and the porter notices it, for example "(His box of relics rattles.)". The part nearest the middle of your view is the one you read, so talking face to face you notice his face first. Only what you noticed goes into the ledger.
4. **You choose,** or walk away. Walk away and he waits at the grille, knocking now and then, until you come back:
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
| Night 3's starting Dose, from the nights before | 30 | mine (my M4 recommendation; waiting on you) |
| Talking: the view narrows, turns to their face in | 22° (70° to 48°), 0.45 s | mine |
| Talking: the view stays on their face, then is his | 1.2 s, then 0.45 s to widen; looking away lets go at once (after the run) | mine |
| Walter's place under the porch | 0.3 m north of the middle of the gate, so the grille's centre stile isn't across his face | mine |
| Waking pace | 180 s per in-game hour | mechanics (*mine*), for the run's 30–40 minute nights |
| Dozing pace | 2 s per in-game hour | mine |
| Marks: supper bell, Matins, Lauds | 17:15, 00:00, 06:00 | mine (the doc names the bells, not their times) |
| Walter's knock, the child's knock | 20:00, 22:00 | mine |
| The Matins window | from 15 minutes before; late after 30 minutes past | mine |
| Dusk, dawn | 16:00–17:30, 06:00–07:00 | mine ("about five minutes" of failing light is yours) |
| Passers-by go home | 17:30 | mine |
| A day's sleep | Dose halves | mine (you asked for "falling over the day but not to zero") |
| Quiet stretch before the crypt light | 20 s | doc wants 5–10 minutes; greybox length |
| In the chase, the oven doesn't give you up while you hold your breath | — | mine, so the scripted beat holds |

## Restaging it

Everything is a marker you can move in the editor, under `night3.tscn`:

| Node | What it holds |
| --- | --- |
| `Places/Supper/<Name>`, `Places/Matins/<Name>` | Where each brother stands in each phase. A brother only moves while you aren't looking |
| `Places/Dusk/<Name>` | Where each brother is at dusk, for talking |
| `Brothers` | The brothers, each with his `Look` (character scene) and `Talker` (conversation) |
| `People` | Cole (at the gate by day), Mab, and the two passers-by with their walks (`People/Walks`) |
| `Marks` | Where you wake, your seat, the choir, the foot of the crypt stair, the infirmary spots for you and Thomas, Cole's place at the gate and where he goes off to (`ColeGate`, `ColeOff`), your cell at dawn, and the Matins spawn |
| `Duties` | Things you use: your seat at supper, relieving Cole and handing him the gate, the bread, the gate bar, the grate, the ledger, the bell rope, the round's stops (each has a `hint` and a `line`), the moved keys, and the cot you sleep on |
| `GateBench`, `CandleClock`, `Clock`, `Daylight`, `BellTower`, `AbbeyGate` | The bench you doze on, the candle on your desk, the night's hours, the light, the bell, and the gate's leaves and bar |
| `Stalk/WalkEnd`, `Stalk/Doorways` | Where the demon may stand on the round, first choice first |
| `Stalk/Blockers` | During the chase, running near one of these puts the demon at its `Stand` |
| `CryptLight`, `Hunter` | The cult's light, and the hunter waiting by it |

Times are exports too. Each beat's `due` is its mark on the candle, and `can_doze` says whether you may doze while it waits. The Knocks beat has `knock_hours` and `child_knock_hour`; the Bell beat has `early` and `late`. The `Clock` node holds the paces. The other pacing waits are Choir `office_time`, Crypt `quiet_time` and Supper `watch_time`.

## Not built yet

- **Visible duties:** the gate grate isn't built. Lines in brackets stand in for it, along with a few routing hints, alongside the lit way.
- **Bodies on screen:** there are no hands in view, and the bell rope doesn't lift you. Waking and sleeping are fades, not lying down and getting up.
- **Morning scene:** dawn doesn't show the abbey's official version of the night.
- **Lateness:** only the Matins bell can be late. Supper and the gate wait for you.
- **Cole** appears out of the kitchen at dawn even if you're looking that way.
- **The brothers:** they're greybox figures with their builds and props from the character table. They don't move between places, sit, or make their sounds.

## Tests and tools

- **`test_night3`:** the whole night in order, from waking to sleep, with every beat's effects and the clock's marks.
- **`test_gate`:** the gate job's three outcomes, talking at the grille and walking away from it, reading, the ledger entry and the ledger page.
- **`test_dialogue`:** conversations: the script and its mistakes, every conversation file, the camera, answers and their tags, walking away, `again`, skipping a line.
- **`test_night3_caught`:**
  - restarting at the Matins bell
  - the quiet save before the crypt
  - caught in the chase: death, back to the quiet save with the round done (not to Matins), twice
  - Continue still starts at the Matins bell
- **`tools/night3_shots.sh`:** plays the night from dusk to dawn and saves a still per beat to `art/_review/m7/`.
