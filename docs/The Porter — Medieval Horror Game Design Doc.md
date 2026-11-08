# The Porter — Medieval Horror Game Design Doc

Nov 6, 2026 · @Pahul

## Pitch

You are the new porter of an abbey inside the walls of medieval London: you keep the gate, ring the night bells and walk the lantern rounds. Pilgrims vanish, brothers die, and something with horns hunts the cloister at night. The abbey says it is a demon. It is a group of your own brothers, and they are drugging the whole abbey so everyone believes it.

First-person, single-player, 6 nights, roughly 4–6 hours.

**Design pillars**

1. **People are the horror.** Every threat has a face you have eaten bread with. NPCs are the content.
2. **Two truths.** Every scare has a supernatural version and a human version. How drugged you are decides which one you see.
3. **Knowing makes you hunted.** Learning things raises the cult's attention on you. Investigation is the risk.
4. **A routine that turns on you.** The gate, the bell and the rounds are safe on night 1 and deadly by night 6.
5. **Grounded medieval detail.** Real jobs, real plants, real buildings. The setting is the world your character believes in, not set dressing.

## Setting

The whole abbey is one walled square about 80 m across. Every building opens off the cloister, so nothing is more than a minute's walk or about 20 seconds' run away and nothing is out of earshot. It is a Benedictine abbey inside the walls of London, late autumn in the 1420s, with about a dozen brothers. Its gate opens onto a narrow lane of the city: timber houses whose upper floors lean out over the street, an inn opposite the gate, and a lantern hung outside each house on winter nights (the mayor's order of 1415). The gate is an iron grille under a stone porch, so the porter sees each visitor whole in the lantern light before he decides.

Small is the point. The player learns every corner by night 2, so on later nights they notice when something is wrong: a door open that is always shut, a lamp out, a brother where he shouldn't be. With no far-off place to run to, the hunter is always close, and the player can hear him from anywhere. The city is right outside, but the porter bars the gate at sunset: on most nights the street is something you see through the grille and hear over the wall, not somewhere to run. You go out into it only when the story sends you. The abbey guards a relic, the finger bone of a local saint, which draws pilgrims and gives the cult its excuse.

&#91;embedded content: Abbey layout · 7 areas around the cloister\]

Seven areas inside the walls, and the lane outside the gate, laid out the way real Benedictine abbeys were: church on the north side, dormitory on the east with night stairs straight down into the church, refectory and kitchens on the south, stores on the west.

| Area | What's in it | Night role | Hiding spots |
| --- | --- | --- | --- |
| Outer court | Gate (an iron grille onto the lane), porter's cell, guesthouse, well | Your hub. Visitors, missing guests | Under your cot, the woodpile |
| The lane (outside the gate) | Timber houses, the inn opposite the gate, two alleys | Visitors come up it to the gate. Seen through the grille and over the wall; walked only when the story sends you out | None |
| Church | Choir, bell tower, crypt and relic underneath | Matins headcount, incense, cult meetings below | Under the altar cloth, inside an open tomb |
| Cloister | Covered walkway around a garden | Every route crosses it; long sightlines through the arches | Behind pillars (unreliable) |
| Dormitory (east) | Beds upstairs, chapter house below, night stairs to the church | Empty beds tell you who is out | Under beds |
| South range | Refectory, kitchen, bakehouse | Supper scenes; bones in the oven | A cold oven |
| Cellar (west) | Granary and stores; hidden stair to the crypt | Ergot source; how the hunters "teleport" | Grain sacks |
| Graveyard and infirmary | Charnel house, fishpond and mill race; infirmary and latrine block | Bodies; the two escape routes | Bone piles, the latrine chute, under the mill wheel |

### Making it feel alive

- **Everyone keeps a routine you can see.** Lit windows show who is awake. Snoring from the dormitory, Osric locking the cellar, Thomas grinding herbs. When a routine breaks, the player notices.
- **Sound carries everywhere.** Because the map is small, you hear the dorm, the mill wheel, the chant and footsteps from almost any point. Directional audio is the main way to track people.
- **Animals as tells.** Rooks in the bell tower scatter when someone climbs it. Rats in the granary go quiet when a hunter is near. The abbey cat follows you on rounds and stares into dark corners; sometimes a man is standing there, sometimes nothing is.
- **The map remembers.** Each night leaves marks that stay: a fresh grave dug on night 2, a door that stays locked from night 3, Edwin's empty bed, wax drips on the crypt stairs.
- **Weather changes the space.** Rain on nights 1–2 covers sound. Fog on night 4 cuts sightlines to a few metres. Snow on night 6 leaves footprints, so you can track the hunters and they can track you.

### Making small scary

- **No safe distance.** The hunter is never more than about 20 seconds away at a run, and the player knows it.
- **Familiar spaces go wrong.** The same 7 areas every night, so small changes land hard.
- **Doors as decisions.** Most areas have 2 exits. The hunters lock doors as Suspicion rises, so the map shrinks across the game until night 6 opens everything at once.
- **Hidden connections.** The night stairs and the hidden cellar stair let hunters cut across the map faster than you can. That is how the "demon" appears in two places, until night 5 shows you the passage.

## Cast

You play **Brother Alric**, 19, made porter after the old porter went blind. Everyone else below is a full NPC with a schedule, dialogue and memory of how you treated them.

**The cult and its motive.** The abbey is quietly bankrupt. Three years ago the cellarer began robbing and killing wealthy pilgrims to keep it alive. The infirmarian found out and turned the robbery into a faith: the saint's bones must be fed, and a "demon" explains every death. Now five men believe it.

**Inside the walls**

| Character | Public face | Truth | In the cult? |
| --- | --- | --- | --- |
| Brother Thomas, infirmarian | Gentle healer; your first ally. Saves you on night 3 by hiding you in the infirmary. | The cult's leader. Doses the abbey with ergot and henbane. Keeps you alive because the cult needs a porter. | Leader |
| Brother Ranulf, sacrist | Keeps the relic, candles and incense | Wears the horned costume most nights | Yes |
| Brother Osric, cellarer | Jolly, feeds you extra bread | Started the killings; handles bodies | Yes |
| Two lay brothers, Cole and Dunstan | Big, silent labourers | Wear the other two costumes; the "teleporting" demon | Yes |
| Abbot Godric | Frail, kind, fatherly | Not in the cult. Drugged hardest; truly believes in the demon and orders more incense to drive it out | No |
| Prior Hugh | Harsh, watches you constantly; the obvious suspect | Investigating the deaths. Suspects *you*, the new porter | No |
| Brother Anselm, old porter | Blind, kept in the infirmary | Let victims in for years; guilty and terrified | Was complicit |
| Brother Edwin, novice | Your friend and the person you talk to | Dies on night 4 | No |
| 4 choir brothers | Background faces at Matins | Filler for the headcount; a few can be victims | No |

**Outside the gate**

| Character | Public face | Truth |
| --- | --- | --- |
| Walter the pardoner | Relic-seller who returns every few nights | Supplies the henbane; knows exactly what it does |
| Mab, a leper | Begs at the gate every night | Sees everyone who comes and goes; the best witness, ignored by all |
| Joan, asking for sanctuary | Says she is fleeing her husband | Her brother vanished here as a pilgrim. She is investigating too |
| Roger, the town bailiff | Demands certain guests be handed over | Wants the abbey's land; useful in one ending |
| Pilgrims (generated) | A new few each night | Traits: wealthy or poor, sick, armed, lying. Wealthy ones are targets |

## Core loop: one night

Each night runs from waking at dusk to going to sleep at dawn: a 40–60 minute shift timed by a candle clock in your cell. The clock burns slowly in real time, and its burn marks are your duties: each is due when the flame reaches its mark, with some slack either side. Talking and exploring cost time, and a duty done very late is noticed.

0. **Waking (dusk).** The porter sleeps through the day while the day porter keeps the gate. He wakes in his cell in the late afternoon and has a few minutes of failing light to look around and talk before the supper bell. Waking is when you notice what changed while you slept.
1. **Supper (short dusk scene).** Eat with the brothers in the refectory. Bread and ale are served by Osric. You eat the bread until you have found a clue that something is wrong with it; from then on you can palm it instead, and risk being seen. Dialogue here sets up the night.
2. **Closing the gate.** Bar the gate at sunset. Enter that night's guests in the ledger by name and description.
3. **Knocks (2–4 per night).** Talk through the grate. Read the visitor: boots, hands, story, what they carry. Choose: admit to the guesthouse, refuse, or send for the prior. Choices are remembered by the visitor and the cult.
4. **Matins bell (midnight).** Ring the bell, go to the choir, count the brothers. The incense is lit here. A missing brother is the night's main mystery.
5. **Lantern round.** Walk a set route through 4–5 areas, checking doors and lamps. This is where bodies, cult activity and chases happen. Optional detours carry clues and risk.
6. **The small hours.** With the round done, you go back to the gate and wait. You can doze until dawn, but each night's main event interrupts the wait.
7. **Lauds and dawn.** The night resolves: who is missing, what was moved, who saw you where. A short morning scene shows the abbey's official version of events. The day porter relieves you at the gate and you go to your cell to sleep.

**Tools**

- Horn lantern: dim and wind-sensitive. Covering it with your cloak hides you but blinds you.
- The ledger: your record of who came in. The cult tears pages out; comparing it against the guesthouse beds is a core clue.
- Keys: the porter holds keys to the gate, guesthouse and charnel house. Losing them is a story beat.
- The bell rope: summons the whole abbey. Useful in a chase, but you don't know whose side arrives.

## The two layers: dosing and hallucination

A hidden **Dose** value (0–100) decides whether the game shows you the supernatural version of an event or the real one. The cult keeps everyone dosed because a demon explains every death.

**Sources**

| Source | Dose | Avoidable? | Cost of avoiding |
| --- | --- | --- | --- |
| Rye bread at supper (ergot) | +10 per meal, slow and lasting | Yes, by palming it, once you have found a clue that something is wrong with the bread | Hunger: slower sprint recovery, hand tremor on the lantern. Osric notices empty plates |
| Incense at Matins (henbane) | +25, fast, fades over the round | No on nights 1–3, when the whole church is filled. From night 4, partly: stand near the door and hold your breath | Missing the headcount or being seen not singing raises suspicion |
| Wine at Mass or from Thomas | +40 on cult kill nights | Yes, by refusing | Refusing Thomas directly is a large suspicion jump |
| Thomas's "remedy" for your headaches | +15 | Yes | Refusing it after night 3 tips him off |

Dose decays about 10 per in-game hour. It rarely reaches zero before the next source. From night 4 the cult also doses the well water: +5 every time you drink.

**Effect tiers**

| Dose | What changes |
| --- | --- |
| 0–24 | Clear. Masks look like masks |
| 25–49 | Audio: whispers, footsteps behind you, your name called. Lantern flame bends toward things |
| 50–74 | Visual: shapes at the edge of view, faces in the wood grain, carvings that turn their heads. Real cultists start rendering as demons |
| 75–100 | Full: the demon rendering, walls that breathe, dead brothers standing in the choir. Fake events mixed with real ones |

**Same event, two renders**

| Drugged, you see | Sober, it is |
| --- | --- |
| A horned demon with burning eyes | Ranulf in a horned mask, a lantern behind it |
| Hooves on the stone | Boots with carved wooden hoof soles |
| The demon in two places at once | Three men in identical costumes |
| Claw marks on a body | Wounds from a wool-carding comb |
| A body "burned by hellfire" | Quicklime |
| Whispering inside the walls | Monks chanting in the passage behind the crypt |
| A dead brother standing in the choir | A cultist in his habit, hood up |

**Reality checks the player can use**

- Mab the leper never eats abbey bread. Ask her what she saw.
- Physical evidence persists: a hoof print that looked cloven while drugged is a carved sole when you come back sober.
- Fake events leave nothing behind. Real ones usually leave something (wax drips, a footprint, a moved object), but the cult cleans up some scenes, so a missing trace proves nothing.

**Historical note:** henbane is a real deliriant that causes vivid hallucinations, and medieval people did inhale its smoke. Ergot poisoning (St. Anthony's Fire) was real but mainly caused convulsions and gangrene; its hallucinations are exaggerated here. Henbane carries most of the visual effects, which is the more accurate split.

## The demon: Slenderman first, men later

For the first half of the game the threat should feel like a supernatural stalker in the Slenderman mould: tall, silent, always further away than it should be, and never seen moving. Every one of its tricks has a human explanation that the player only pieces together from night 4.

**Phases**

| Nights | Phase | What the player experiences |
| --- | --- | --- |
| 1–2 | Glimpses | A tall horned silhouette at the edge of sight: on the far side of the graveyard, at the end of the cloister walk, in the bell tower window. Look away and back and it is gone. It never makes a sound and never approaches |
| 3 | Stalking | It appears on your route, closer each time: end of the walk, then the doorway, then behind you in the choir. The night 3 chase is running from it and finding it ahead of you |
| 4 | Cracks | In the fog it makes mistakes. You hear it breathe, stumble and swear under its breath. Two of it appear at once. One loses its mask: it is Osric |
| 5–6 | Men | The hunters still wear the costumes so the rest of the abbey keeps believing, but now they talk, call your name, and hunt like men |

**Rules for the Glimpses and Stalking phases**

- It is rarely on screen, and only ever still. It never animates in the player's view.
- It moves only while the player is looking away. Each appearance is closer.
- It never attacks before night 3.
- Silence is the tell: the rooks, rats and the abbey cat go quiet before it appears.
- **Staring at it** builds a distortion effect (ringing ears, the edges of the screen warping, the lantern guttering). Keep staring and you lose your footing. This is the henbane, but the player doesn't know that yet.

**How each trick is done**

| What the player sees | How the cult does it |
| --- | --- |
| Impossibly tall and thin | An antler-and-horn headdress adds about 60 cm; the wearer stands on a wall, tomb or step, framed against the sky |
| Never seen moving | They freeze the moment lantern light touches them and move only when you turn away |
| Closer every time you look | Three men in identical costumes at pre-planned spots along your route |
| Ahead of you when you run | The night stairs and the hidden cellar stair are shortcuts you don't know about yet |
| Silent | Felt overshoes. The wooden hoof soles come out only when they want to be heard |
| Staring makes you sick | Henbane, fear and a lantern you're gripping too hard |

## Suspicion, chases and hiding

A hidden **Suspicion** value (0–100) tracks how much the cult thinks you know. It only goes up. It decides how hard you are hunted, not whether: from night 3 you are hunted regardless. Each night has one designed chase with its own rule; for the rest of the round the hunter is mostly heard, not seen.

**What raises it**

| Action | Suspicion |
| --- | --- |
| Finding a body and not reporting it the "right" way (to Thomas) | +15 |
| Being seen in a restricted area (crypt, granary at night) | +10 |
| Refusing bread, wine or Thomas's remedy | +5 to +20 |
| Asking the wrong brother the wrong question | +5 to +15 |
| Admitting a guest the cult wanted kept out, or turning away one they wanted in | +10 |
| Telling the prior anything | +10 (Ranulf overhears) |

**Thresholds**

| Suspicion | Hunting behaviour |
| --- | --- |
| 0–29 | One costumed cultist on a patrol route; does not search for you |
| 30–59 | Searches the last place you were seen; checks hiding spots near you |
| 60–84 | Two hunters; they lock doors behind you and wait at the gatehouse |
| 85+ | Night 6 rules early: the whole cult hunts you |

**The hunter is a man**

- Same speed as you on flat ground. Faster than a hungry player, slower on stairs and ladders.
- Can't fit through the gap under the mill wheel or the latrine chute.
- Needs light to see you. Cover your lantern and stand still in darkness and he walks past.
- Gets winded after about 20 seconds of sprinting and stops to listen.
- Talks. Hunters call your name in a brother's voice you recognise, which is how sober players identify them.
- Can be locked out. You hold the keys, until night 5.

**Hiding**

Each hiding spot has a noise and a check chance. The hunter checks the 2 spots nearest your last-seen position. A spot used twice in one night is checked first. Holding your breath in a spot drains a breath meter; hunger shortens it.

**Getting caught** the first time is not death. You wake in the infirmary with Thomas over you, a fresh dose in you (+40), and something taken or changed: your keys, a page of the ledger, or your friend's trust. The second capture, on any night, kills you and restarts from the last bell.

&#91;embedded content: Hunter AI · 5 states\]

The only way out of a chase is to break line of sight and get hidden before the search reaches you.

## Bodies

Six bodies across six nights. Each one is a scare first and a clue second. Clues are optional; the scare is not.

| Night | Victim | Where and how you find it | The scare | The clue that says "human" |
| --- | --- | --- | --- | --- |
| 1 | Wealthy pilgrim you admitted | Floating face-down in the fishpond at dawn | Your lantern catches a face just under the surface as you walk past; it rolls over | No water in the lungs (Thomas lies about this), rope marks on the wrists, purse gone |
| 2 | Choir brother | Hanging in the bell tower when you go to ring Matins | You pull the rope and it is heavy. Something drops past you | Sailor's knot. Only one guest this week was a sailor, and he left before dark (per the ledger) |
| 3 | Pilgrims (several) | Bones in the bakehouse oven ash | You are hiding in the oven during your first chase. Your hand closes on a jaw | A pilgrim's badge melted in the ash. The badge matches a name torn from the ledger |
| 4 | Edwin, your friend | Laid out in the charnel house among the bones | He is missing at Matins. You find him on your round; drugged, he sits up and speaks | Wounds match a wool-carding comb. You find the comb in Osric's storeroom later |
| 5 | Joan, if you sheltered her (otherwise a pilgrim) | Under the grain in the granary | You plunge your arm into the rye to find the hidden key; a hand grips back. She is alive, then she isn't | The rye is black-spurred with ergot. This is the dosing source |
| 6 | Brother Anselm | In his infirmary bed | He was going to tell you everything. His blind eyes are open and his mouth is stuffed with henbane leaves | Killed for talking. Proves Thomas, the only one with infirmary access |

**Body behaviour**

- Bodies move. If you leave to fetch someone, the body is gone when you return, and you are the one who looks mad.
- Reporting a body is a choice: to Thomas (safe now, dangerous later), to the prior (he suspects you), or to no one.
- At high Dose, a found body may speak, move or follow you. Sober, it is just dead, which should be worse.

## Night-by-night script

The game runs in three acts: **The Gate** (nights 1–2), **The Rounds** (nights 3–5) and **The Hunt** (night 6).

### Night 1: The new porter

- **Supper:** meet everyone. Osric gives you extra bread. Anselm, blind, grabs your sleeve: "Don't let them in after the bell."
- **Knocks:** a wealthy merchant-pilgrim (admit him), Walter the pardoner, and a final knock after midnight with no one there. Mab saw nobody. This knock is never explained: it happens even at Dose 0, and no ending accounts for it.
- **Matins:** count is right. First incense; first whisper.
- **Round:** tutorial route. A tall horned shape stands still at the far end of the cloister. Look away and it is gone. No chase.
- **Dawn:** the merchant is in the fishpond (body 1). Thomas says he drowned drunk.

### Night 2: The bell

- **Knocks:** Joan asks for sanctuary. A sailor who says he is leaving before dark. Roger the bailiff asks if a "merchant" came through.
- **Matins:** you pull the bell rope and it is heavy (body 2). The count is one short.
- **Round:** the guesthouse has one more empty bed than your ledger says. A ledger page is gone.
- **Dawn:** the abbot declares the demon has come and orders more incense. The prior asks where you were.

### Night 3: The oven (first chase)

- **Supper:** the bread tastes bitter. Thomas offers a remedy for your headaches.
- **Knocks:** Walter again, with a bag that smells of the incense. A child-sized knock low on the gate; no one there (hallucination at Dose 50+).
- **Matins:** you see a brother in the choir who died on night 2 (hallucination) or a hooded stranger in his place (sober).
- **Round:** you see a light in the crypt. Investigate and you are spotted. **First chase.** You hide in the bakehouse oven and find bones (body 3). Climbing out, you are nearly caught; Thomas pulls you into the infirmary and hides you.
- **Dawn:** your keys have been moved. Suspicion now drives hunting every night.

### Night 4: Edwin (midpoint)

- **Supper:** Edwin whispers that he has seen the demon's face. He'll tell you after Matins.
- **Knocks:** Mab, inside the gate for the first time, terrified. She saw three demons leave by the mill race.
- **Matins:** Edwin is missing from the count.
- **Round:** you find Edwin in the charnel house (body 4). **Two hunters for the first time**: you see the demon in two places at once. If sober, you see two masked men. One loses his mask in the chase: it is Osric.
- **Dawn:** someone has been in your cell. Your cot is wet and the candle clock is snapped. Your one safe space is gone.

### Night 5: The granary

- **Supper:** Osric, whose face you saw last night, serves your bread and smiles. Eat it (lose clarity) or don't (he watches you). Thomas checks your eyes.
- **Knocks:** Joan, if you turned her away earlier, back with her brother's pilgrim badge.
- **Matins:** the abbot collapses from the incense. In the confusion, Anselm pulls you aside: the key to the crypt passage is in the granary.
- **Round:** search the grain (body 5). The ergot is in the rye. **Hunters lock you inside**; escape through the latrine chute.
- **Dawn:** the prior arrests you for the killings. Thomas speaks for you and has you released into his care.

### Night 6: The hunt

- **Supper:** none. You wake in the infirmary at dusk. Anselm is dead in the next bed (body 6).
- **Gate:** a knock. It is someone you know: the bailiff, Joan or Mab, depending on earlier choices. Opening the gate is one possible ending.
- **The hunt:** all five cultists in costume. Every route you've learned is in play. The crypt passage holds the proof: the costumes, the purses and the relic, which is a pig's bone.
- **End:** see Endings.

## Endings

Five endings, decided by what you carry out of the crypt, who you let in, and your Dose at the end.

| Ending | How you get it | What happens |
| --- | --- | --- |
| **The Gate** | Reach the gate with proof and open it for the bailiff | Roger's men take the abbey. The cult hangs, and the bailiff takes the land. Justice, bought by a worse man |
| **The Witness** | Escape by the mill race with Mab or Joan alive | You flee into the dark with the only other person who knows. Nobody believes either of you. Final shot: a new porter at the gate |
| **The Fire** | Burn the granary and crypt | The proof and the cult burn together. The record calls it a lightning strike. You are never sure who was inside |
| **The Demon** | Finish with Dose 75+ | You fight and kill "the demon". Sober epilogue: it was the prior, who came to help. You are hanged for the murders |
| **The New Faith** | Caught on night 6 after drinking Thomas's wine | You wake in a habit with a mask in your lap. Thomas: "The porter has always been one of us." |

Every ending closes with a short chronicle entry, written decades later, giving the official version. It never matches what you saw.

## Systems to build in Godot

Build in priority order. P0 makes one night playable; P1 makes six nights; P2 is polish. Audio is P0 alongside the table: the Matins chant as a dynamic music layer, hunters humming it on their rounds, footsteps per surface, and the hoof soles on stone.

| System | What it does | Godot 4 approach | Priority |
| --- | --- | --- | --- |
| Game state | Dose, Suspicion, night number, flags for every choice | Autoload singleton; save as a Resource at each bell | P0 |
| Candle clock and night phases | Drives supper → gate → Matins → round → dawn | Phase state machine in the autoload; signals on phase change | P0 |
| Dual render | Swaps an object between its real and hallucinated version by Dose | A `DualRender` component node holding two child meshes or materials; listens for Dose changes | P0 |
| Hallucination post-process | Vignette, chromatic shift, breathing walls, light bending | Screen-space shader on a full-screen quad; uniforms driven by Dose | P0 |
| Hunter AI | Patrol, investigate, chase, search, lose track | NavigationAgent3D plus a state machine or behaviour tree (LimboAI or Beehave addons) | P0 |
| Hiding and breath | Enter spot, hold breath, hunter checks | Area3D per spot with noise and check-chance exports | P0 |
| Dialogue with memory | Conversations that read and set flags | Dialogic 2 addon, with conditions on the game-state flags | P1 |
| NPC schedules | Who is where at each phase | Per-NPC schedule Resource: phase → location marker → activity | P1 |
| Gate visitors | Knock, grate conversation, admit or refuse | Visitor Resources (scripted plus generated pilgrims) queued per night | P1 |
| Headcount | Count brothers in the choir at Matins | Seat markers in the choir; schedules fill or leave them empty | P1 |
| Ledger | Written record that can be tampered with | UI page backed by a list in game state; cult events remove entries | P1 |
| Fake events | Hallucination-only scares that leave no trace | Event nodes gated on Dose ranges; no persistent props | P2 |
| Chronicle epilogues | Official version of each ending | Text scenes keyed off ending flags | P2 |

**Vertical slice target:** night 3 alone. It has supper, a gate scene, Matins, a round, the first chase and a body. If night 3 is scary, the game works.

## Adversarial review: is it actually scary?

Verdict: the premise and the set pieces are strong, but the draft above had three flaws that would have made it stop being scary halfway through. All three are fixed in the sections above; the rest are listed with their fixes.

| # | Severity | Problem | Fix | Applied? |
| --- | --- | --- | --- | --- |
| 1 | Critical | **The reveal kills the fear.** Once the player knows the demon is men in masks, the monster becomes a man they can outrun. A player who skips bread on night 1 sees masks immediately. | Matins incense is unavoidable on nights 1–3, so nobody sees a mask clearly before night 4. After the reveal, fear moves to the faces: on night 4 a hunter unmasks and it is Osric, who passes you bread at supper the next evening. Supper becomes the most frightening scene in the game. | Yes |
| 2 | Critical | **Being caught is not scary.** Waking up in the infirmary every time teaches players that capture is safe. | The first capture is the infirmary wake-up. The second capture kills you, from any night. | Yes |
| 3 | Critical | **Optimal play skips the horror.** A careful player avoids all doses and never sees the demon. The "fake events leave no trace" rule also teaches players to ignore scares. | Incense is unavoidable early; from night 4 the cult also doses the well water. The trace rule becomes unreliable: the cult cleans up some real scenes, so a missing trace proves nothing. | Yes |
| 4 | High | **Chase fatigue.** A hunter every night from night 3 becomes a chore once the AI's pattern is learned. | One designed chase per night, each with a different rule: hiding (3), two hunters (4), locked in (5), whole cult (6). The rest of the round the hunter is mostly heard, not seen. Being searched for is scarier than being chased. | Yes |
| 5 | High | **The Thomas twist is telegraphed.** The friendly healer who explains the drugs is the oldest trick in the genre. | Make the prior the obvious suspect, and have Thomas genuinely save you on night 3 by hiding you in the infirmary. He needs you alive because the cult needs a porter. | Yes |
| 6 | High | **Everything gets explained.** Fully solving the mystery leaves nothing to fear afterwards. | One event is never explained: the knock with nobody there on night 1. Mab saw no one, it happens even at Dose 0, and the chronicle never mentions it. | Yes |
| 7 | High | **Sound was missing from the build plan.** Horror lives mostly in audio. | Audio added to P0: the Matins chant as a dynamic layer, hunters humming the chant on their rounds, footstep surfaces, and the hoof soles on stone. | Yes |
| 8 | Medium | **No quiet stretches.** Constant events flatten tension. | Each night needs 5–10 minutes of round with nothing happening, placed just before the night's main event. | Pacing rule for level design |
| 9 | Medium | **Gate scenes could become paperwork.** Reading boots and stories is a Papers, Please loop, which is tense but not scary. | Keep it to 2–3 hand-written knocks per night; no generated pilgrims in the first build. The scariest knocks are people who should be inside the walls. | Scope decision |
| 10 | Medium | **Scope is large for a solo build.** Six nights, about 15 NPCs with schedules, five endings and two meta systems. | Ship night 3 as the vertical slice. Build three endings first (Gate, Witness, Demon) and add the rest if the slice works. | Scope decision |

**Playtest test for night 3.** It passes if most testers: hesitate before opening the gate, flinch in the oven, refuse to go back to the crypt without being made to, and are unsure whether the horned figure is real. If testers call the hunter "annoying" rather than scary, cut his time on screen, don't add more of him.
