# The Porter — Medieval Horror Game Design Doc

Nov 6, 2026 · @Pahul

**Changes, Nov 8 2026** (from the grilling session; the full-game run's spec is `docs/full-game-run.md`):
- The demon is real. The cult is raising the Hungry Saint, which will one day be Jack the Ripper. It shows itself only on night 6; before that, everything is men and the drug.
- The rite needs a count of deaths in the six nights. Deaths your choices prevent leave it short.
- Thomas is the villain you trust. He tells you what he has noticed (always about someone else), warns you off Ranulf's remedy, saves you on night 3, and is "attacked" on night 5.
- Brother Simon, a choir brother, draws your suspicion: Thomas sends him to scrub blood, then points you at him. On night 5 you save Thomas or Simon.
- People die in front of you: nine witnessed deaths across the game, on top of the six found bodies. There are also hidden bodies to find.
- Seven endings: the five, rewritten to say what became of the Saint, plus The Rising and The Broken Rite.
- A prologue: **night 0** at the Cross Keys inn on the lane (arriving by carter's wagon through Aldgate, the lane's people, drink, a killing seen from your room), then **day 1**, Thomas and the blind Anselm showing you the porter's duties before your first night. The lane becomes a place you know: a hub at each dusk and a view by night. Three small barred windows (squints) in the wall along the lane.
- After an adversarial review (see the end of this doc): nights are shorter and break their routine; every hidden number has a tell you can see; each night has someone a careful porter can save, by a rule you can learn; quiet saves before chases; the prior is the red herring and Ranulf gives the remedy; three things have no human explanation before night 6; the prior can believe you on night 5.
- Mechanics (from the mechanics grilling; full rules in `docs/mechanics.md`): one forgiving capture, on night 1 or 2 only; crouching and leaning; a satchel; throwing things to draw a hunter; the bell rope, whose answer follows trust and Suspicion; set gusts that can blow the lantern out; quiet saves before every chase; hidden trust per person, warnings and companions; the ledger keeps notes; no fighting.

## Pitch

You are the new porter of an abbey inside the walls of medieval London: you keep the gate, ring the night bells and walk the lantern rounds. Pilgrims vanish, brothers die, and something with horns hunts the cloister at night. The abbey says it is a demon. It is a group of your own brothers, and they are drugging the whole abbey so everyone believes it. But they are also feeding something. Each death is a sacrifice to the Hungry Saint, a real demon, and if they finish, it walks out of the gate into London. Centuries later, London will call it Jack the Ripper.

First-person, single-player, a prologue and 6 nights, roughly 4–5 hours for a first playthrough.

**Design pillars**

1. **People are the horror.** Every threat has a face you have eaten bread with. NPCs are the content.
2. **Two truths, then a third.** Every scare has a supernatural version and a human version. How drugged you are decides which one you see. On night 6 the third truth arrives: the thing the men were calling is real.
3. **Knowing makes you hunted.** Learning things raises the cult's attention on you. Investigation is the risk.
4. **A routine that turns on you.** The gate, the bell and the rounds are safe on night 1 and deadly by night 6.
5. **Grounded medieval detail.** Real jobs, real plants, real buildings. The setting is the world your character believes in, not set dressing.

## Setting

The whole abbey is one walled square about 80 m across. Every building opens off the cloister, so nothing is more than a minute's walk or about 20 seconds' run away and nothing is out of earshot. It is a Benedictine abbey inside the walls of London, late autumn in the 1420s, with about a dozen brothers. Its gate opens onto a narrow lane of the city: timber houses whose upper floors lean out over the street, an inn opposite the gate (the Cross Keys), and a lantern hung outside each house on winter nights (the mayor's order of 1415). The gate is an iron grille under a stone porch, so the porter sees each visitor whole in the lantern light before he decides. Three small barred windows (squints) in the abbey wall look out on the lane: one from the porter's cell, two from the outer court. At nine the city's curfew bell empties the lane, and after it only the night watchman walks it, calling the hour.

Small is the point. The player learns every corner by night 2, so on later nights they notice when something is wrong: a door open that is always shut, a lamp out, a brother where he shouldn't be. With no far-off place to run to, the hunter is always close, and the player can hear him from anywhere. The city is right outside. At dusk, while Cole still keeps the gate open, you can step out and talk to whoever is in the lane. Once you take the gate after supper it stays barred: through the night the street is something you see through the grille and hear over the wall, not somewhere to run. You go out into it at night only when the story sends you. The abbey guards a relic, the finger bone of a local saint, which draws pilgrims and gives the cult its excuse.

&#91;embedded content: Abbey layout · 7 areas around the cloister\]

Seven areas inside the walls, and the lane outside the gate, laid out the way real Benedictine abbeys were: church on the north side, dormitory on the east with night stairs straight down into the church, refectory and kitchens on the south, stores on the west.

| Area | What's in it | Night role | Hiding spots |
| --- | --- | --- | --- |
| Outer court | Gate (an iron grille onto the lane), porter's cell, guesthouse, well | Your hub. Visitors, missing guests | Under your cot, the woodpile |
| The lane (outside the gate) | Timber houses, the Cross Keys inn opposite the gate (its taproom, and rooms upstairs), two alleys | Night 0: the whole lane and the inn are yours. After that, visitors come up it to the gate; at each dusk, while the gate is open, you can go out to the people you know; at night it's seen through the grille and the squints, and walked only when the story sends you out | None |
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

**The cult and its motive.** The abbey is quietly bankrupt. Three years ago the cellarer began robbing and killing wealthy pilgrims to keep it alive. The infirmarian found out and turned the robbery into a faith: the saint's bones must be fed, and a "demon" explains every death. Now five men believe it. Thomas found the rite in an old book: the "saint" they feed is the Hungry Saint, a demon. It wakes when it has been fed ten souls in six nights, with the last given in the crypt at Matins. The new porter's six nights are those six nights. The cult needs a porter who lets the right people in and believes in the demon.

**Inside the walls**

| Character | Public face | Truth | In the cult? |
| --- | --- | --- | --- |
| Brother Thomas, infirmarian | Gentle healer; your first ally and the man you trust most. He tells you what he has noticed: always someone else (the prior out at night, Brother Simon). He warns you not to take Ranulf's remedy, saves you on night 3 by hiding you in the infirmary, and is "attacked" on night 5. | The cult's leader. Doses the abbey with ergot and henbane, and leads the rite to raise the Hungry Saint. The attack is staged, his warnings are true when they cost him nothing, and the men he points you at are innocent. Keeps you alive because the cult needs a porter. | Leader |
| Brother Ranulf, sacrist | Keeps the relic, candles and incense. Offers you a remedy for your headaches | Wears the horned costume most nights. The remedy is henbane | Yes |
| Brother Osric, cellarer | Jolly, feeds you extra bread | Started the killings; handles bodies | Yes |
| Two lay brothers, Cole and Dunstan | Big, silent labourers. Cole keeps the gate by day while the porter sleeps | Wear the other two costumes; the "teleporting" demon | Yes |
| Abbot Godric | Frail, kind, fatherly | Not in the cult. Drugged hardest; truly believes in the demon and orders more incense to drive it out | No |
| Prior Hugh | Harsh, watches you constantly; the obvious suspect. He's out at night, he's near every body, and on night 4 there's blood on his sleeve | Investigating the deaths: the blood is from kneeling to examine a body. Suspects *you*, the new porter. On night 5 he arrests you, and if you can show him enough, he believes you | No |
| Brother Anselm, old porter | Blind, kept in the infirmary | Let victims in for years; guilty and terrified | Was complicit |
| Brother Edwin, novice | Your friend and the person you talk to | Dies on night 4 | No |
| Brother Simon, a choir brother | Quiet. On night 4 you find him scrubbing blood off the cloister flags, and he hides the rag | Thomas sent him to do it, then told you to watch him. On night 5 you save Thomas or Simon. Saved, he tells you who sent him | No |
| 3 other choir brothers | Background faces at Matins | Filler for the headcount; a few can be victims. One warns you on night 1 that something is wrong with the bread, and is the body in the bell tower on night 2. One dies in front of you in the fog on night 4 | No |

**Outside the gate**

| Character | Public face | Truth |
| --- | --- | --- |
| Walter the pardoner | Relic-seller who returns every few nights | Supplies the henbane; knows exactly what it does |
| Mab, a leper | Begs at the gate every night | Sees everyone who comes and goes; the best witness, ignored by all |
| Joan, asking for sanctuary | Says she is fleeing her husband | Her brother vanished here as a pilgrim. She is investigating too |
| Roger, the town bailiff | Demands certain guests be handed over | Wants the abbey's land; useful in one ending |
| Pilgrims (generated) | A new few each night | Traits: wealthy or poor, sick, armed, lying. Wealthy ones are targets |

**The lane** (met on night 0, seen at every dusk after; names are drafts):

| Character | Who | Later |
| --- | --- | --- |
| Hob and Agnes, who keep the Cross Keys | The innkeeper and his wife; they hear everything said over the ale | Their talk at each dusk carries the lane's rumours: who went into the abbey and wasn't seen again, what people say you did |
| Jankin, a drunk | A regular at the Cross Keys, harmless, full of stories | On night 2, if you turned no one away, he is the man killed in the lane |
| Gib, the night watchman | Old; lights the street lanterns, walks the lane after curfew calling the hour | His call is a clock you can hear from inside the walls; the night it stops is a scare |
| Ralph the chandler and his daughter Kit | They make the abbey's candles; Kit sells them at the gate | Ralph knows how many candles the sacrist buys, and when it changed |
| The carter | Brings you in on his wagon on night 0 | Passes in the lane at dusk |
| Margery, with her basket | A neighbour who hurries home before dark | Passes in the lane at dusk |
| Walter and Roger | Drinking at the Cross Keys on night 0, before you meet them at the gate | |

## Core loop: one night

**Before the first night** there is a prologue: night 0 at the Cross Keys and day 1 at the abbey (see "Night-by-night script"). From night 1 the loop below runs every night.

Each night runs from waking at dusk to going to sleep at dawn: a 30–40 minute shift timed by a candle clock in your cell. Nights 1 and 2 teach the routine; from night 3, each night breaks a step of it (see the script), so the routine itself turns on you. The clock burns slowly in real time, and its burn marks are your duties: each is due when the flame reaches its mark, with some slack either side. Talking and exploring cost time, and a duty done very late is noticed.

0. **Waking (dusk).** The porter sleeps through the day while Cole keeps the gate. He wakes in his cell in the late afternoon. The gate still stands open with Cole at it, so for a few minutes of failing light you can look around, talk to the brothers, or step out into the lane and talk to whoever is there, before the supper bell. Waking is when you notice what changed while you slept.
1. **Supper (short dusk scene).** Eat with the brothers in the refectory. Bread and ale are served by Osric. You eat the bread until you have found a clue that something is wrong with it; from then on you can palm it instead, and risk being seen. The first clue is a brother's warning on night 1. Dialogue here sets up the night.
2. **Taking the gate.** After supper you go to the gate and relieve Cole. You close and bar it and keep watch for the night. Enter that night's guests in the ledger by name and description.
3. **Knocks (2–4 per night).** Talk through the grate. Read the visitor: boots, hands, story, what they carry. Choose: admit to the guesthouse, refuse, or send for the prior. Choices are remembered by the visitor and the cult.
4. **Matins bell (midnight).** Ring the bell, go to the choir, count the brothers. The incense is lit here. A missing brother is the night's main mystery.
5. **Lantern round.** Walk a set route through 4–5 areas, checking doors and lamps. This is where bodies, cult activity and chases happen. Optional detours carry clues and risk.
6. **The small hours.** With the round done, you go back to the gate and wait. You can doze until dawn, but each night's main event interrupts the wait.
7. **Lauds and dawn.** The night resolves: who is missing, what was moved, who saw you where. A short morning scene shows the abbey's official version of events. Cole comes to take the gate and you go to your cell to sleep.

**Tools**

- Horn lantern: dim and wind-sensitive. Covering it with your cloak hides you but blinds you.
- The ledger: your record of who came in. The cult tears pages out; comparing it against the guesthouse beds is a core clue.
- Keys: the porter holds keys to the gate, guesthouse and charnel house. Losing them is a story beat.
- The bell rope: summons the whole abbey. Useful in a chase, but who arrives first depends on you: a friend who trusts you, the prior, or (if the cult already suspects you) one of them.
- The satchel: what you carry (evidence, clean food, a stone to throw). The cult takes it if you're caught.

## The two layers: dosing and hallucination

A hidden **Dose** value (0–100) decides whether the game shows you the supernatural version of an event or the real one. The cult keeps everyone dosed because a demon explains every death.

**Sources**

| Source | Dose | Avoidable? | Cost of avoiding |
| --- | --- | --- | --- |
| Rye bread at supper (ergot) | +10 per meal, slow and lasting | Yes, by palming it, once you have found a clue that something is wrong with the bread | Hunger: slower sprint recovery, hand tremor on the lantern. Osric notices empty plates |
| Incense at Matins (henbane) | +25, fast, fades over the round | No on nights 1–3, when the whole church is filled. From night 4, partly: stand near the door and hold your breath | Missing the headcount or being seen not singing raises suspicion |
| Wine at Mass or from Thomas | +40 on cult kill nights | Yes, by refusing | Refusing Thomas directly is a large suspicion jump |
| Ranulf's "remedy" for your headaches | +15 | Yes | Refusing it tips Ranulf off; Thomas, who warned you, is pleased |

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
| 5 | Men | The hunters still wear the costumes so the rest of the abbey keeps believing, but now they talk, call your name, and hunt like men |
| 6 | Men, and the Saint | The men hunt you, and the thing they called comes. See "The Hungry Saint" |

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

## The Hungry Saint

The demon the cult is raising is real, but it shows itself only on night 6. Until then every scare is men, costumes and the drug. That keeps the two truths honest for five nights.

So night 6 is earned, not a cheat, three things before it have no human explanation, even sober, and nothing in the game ever explains them: the knock with no one there on night 1; a crypt candle that lights itself in front of you on night 5; and on night 0, through a squint, a shape too tall and too thin and with no horns, nothing like the demon the lane talks about. On night 6 the player recognises it.

- **The rite.** The cult's book asks for ten souls in six nights, the last in the crypt at Matins on night 6. There's no number on screen, but the crypt keeps count: the cult lights a candle there for each soul, so you can go down and count them. The book's page (found on night 3) says what the candles mean. Deaths your choices prevent leave it short.
- **Its strength on night 6** depends on the count. Short of it, it's a shadow that can't leave the crypt. Near it, it walks the abbey. Met, it hunts.
- **How it moves.** Unlike the costume, it moves in view, slowly. Darkness doesn't hide you from it, silence comes before it, and its touch is death. It kills cultists too.
- **What it becomes.** The chronicle entries follow it down the centuries to Whitechapel, 1888. The game never says "the Ripper"; the last line does the work.
- **The relic.** The saint's finger bone is still a pig's bone. The abbey's holiness is a fraud; the thing in the crypt isn't.

## Suspicion, chases and hiding

A hidden **Suspicion** value (0–100) tracks how much the cult thinks you know. It rises fast and falls slowly: a night with every duty on time and nothing seen takes a little off at dawn. You never see the number, but you see its effects (see `docs/mechanics.md`, "Reading the hidden numbers"). It decides how hard you are hunted, not whether: from night 3 you are hunted regardless. Each night has one designed chase with its own rule; for the rest of the round the hunter is mostly heard, not seen.

**What raises it**

| Action | Suspicion |
| --- | --- |
| Finding a body and not reporting it the "right" way (to Thomas) | +15 |
| Being seen in a restricted area (crypt, granary at night) | +10 |
| Refusing bread, wine or Ranulf's remedy | +5 to +20 |
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

**Getting caught** on night 1 or 2 is not death, once. You wake in the infirmary with Thomas over you, a fresh dose in you (+40), and something taken or changed: your keys, a page of the ledger, or your friend's trust. Any other capture (a second one, or any from night 3 on) kills you and restarts from the last bell.

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

**Witnessed deaths** vary where the player stands, so none plays like a cutscene, and control is never taken away: some you watch helpless (through the grille), some put you in danger (the killer turns toward you), some you reach seconds too late, and some you only hear. On top of the six bodies you find, nine people die in front of you: none on night 1, then 1, 1, 2, 2 and 3. Before them all, on night 0, you watch a man killed by the well from your window at the Cross Keys. They're guests you admitted, brothers, and people in the lane; never Walter, Joan, Mab or Roger. Some are implied (a shape in the fog, a cry cut off), some gory, some one quick cut of the throat with blood flying. Drugged, you see the demon do it; sober, a man in a mask. At high Dose, some are hallucinations that leave no body. In the moment you can't stop them; before, your choices decide who dies, and how many. The full list is in `docs/full-game-run.md`.

**Hidden bodies.** Five earlier victims are hidden for players who explore: down the well, in the mill race culvert, under fresh earth in the gardens, in the bell tower loft, under the chapter house flags. Each carries a pilgrim badge that matches a name torn from the ledger.

**Body behaviour**

- Bodies move. If you leave to fetch someone, the body is gone when you return, and you are the one who looks mad.
- Reporting a body is a choice: to Thomas (safe now, dangerous later), to the prior (he suspects you), or to no one.
- At high Dose, a found body may speak, move or follow you. Sober, it is just dead, which should be worse.

## Night-by-night script

The game runs in three acts: **The Gate** (nights 1–2), **The Rounds** (nights 3–5) and **The Hunt** (night 6).

### Night 0: The Cross Keys

You are Brother Alric, sent from a small house in the country to be the abbey's new porter.
- **The road in.** At dusk you ride into London on the back of a carter's wagon, in from the east past the white chapel and through Aldgate. In the first minutes the wagon pulls aside for a cart coming the other way with a covered body on it: a pilgrim found in the ditch, the traveller says, the third this month. Then he talks: pilgrims who went into the abbey and weren't seen to leave, lights in it at night, a demon.
- **The gate.** The carter sets you down in the lane. The abbey gate is shut and barred and nobody answers: since the old porter went blind, no one keeps it at night. Mab, begging by the gate, sends you to the Cross Keys opposite.
- **The Cross Keys.** The warmest room in the game. Hob and Agnes, Jankin at the bench, Walter selling relics to the drinkers, Roger asking questions, Ralph the chandler. Drink if you like (each ale blurs the night a little more) and listen: everyone has a story about the abbey.
- **The lane.** Walk it. Gib lights the lanterns, Kit sells her last candles, the curfew bell rings at nine and the lane empties. Walk it alone after curfew and, through a squint in the abbey wall, a shape stands perfectly still just inside: too tall, too thin, no horns. Look again and it's gone. Nothing explains it until night 6.
- **The window.** Agnes shows you up to a room at the top of the inn (she sends you up at midnight if you're still drinking). As you lie down, a cry. From the window you see over the abbey wall into the court: a figure in a black habit, its back to you, kills a man by the well and drags him away toward the cellar. Sober, you saw a man. Drunk, you aren't sure what you saw. This death is before your six nights and doesn't feed the rite.

### Day 1: The tour

- **Morning.** Grey daylight. Agnes says you'd had too much, if you had. Cole opens the abbey gate, and the ground by the well has been sanded over.
- **The duties.** In about five minutes, Thomas, leading the blind Anselm by the arm, shows you the porter's work: the gate and its bar, the bench, the ledger on your cell desk, the candle clock, the bell rope in the tower, the round's stops, the guesthouse beds and its key ("the old porter locked the guests in at night"). Ask about the sand by the well and Thomas says a beast was slaughtered for the kitchen: his first lie. When Thomas steps away, Anselm grips your sleeve: "Don't let them in after the bell."
- **The nap.** Your shift begins at night, so they send you to sleep in your cell.

### Night 1: The new porter

- **Dusk:** you wake in your cell as the light fails. The gate is still open with Cole at it: walk the abbey and watch the brothers at their work, or step out into the lane to the people you met last night, before the supper bell.
- **Supper:** meet everyone. Osric gives you extra bread. A choir brother tells you quietly not to eat the bread: something is wrong with it. From night 2 you can palm it.
- **Knocks:** a wealthy merchant-pilgrim (admit him), Walter the pardoner, and a final knock after midnight with no one there. Mab saw nobody. This knock is never explained: it happens even at Dose 0, and no ending accounts for it.
- **Matins:** count is right. First incense; first whisper.
- **Round:** tutorial route. A tall horned shape stands still at the far end of the cloister. Look away and it is gone. No chase.
- **Dawn:** the merchant is in the fishpond (body 1) if you admitted him and left the guesthouse unlocked. Thomas says he drowned drunk. Locked in, he lived; turned away before the curfew bell, he went on to the Cross Keys. The lane's talk at the next dusk tells you which would have saved him.

### Night 2: The bell

- **Dusk:** Thomas tells you, quietly, that he has seen the prior about the abbey at night, where he has no business.
- **Knocks:** Joan asks for sanctuary. A sailor who says he is leaving before dark. Roger the bailiff asks if a "merchant" came through (only if the merchant died).
- **After midnight:** through the grille you watch someone killed in the lane under a street lantern: a tall shape behind him, then he's in the gutter. It's whoever you turned away after the curfew bell, when the Cross Keys had shut; if no one, it's Jankin, put out of the inn at closing, unless you asked Hob at dusk to keep him in.
- **Matins:** you pull the bell rope and it is heavy (body 2: the choir brother who warned you about the bread). The count is one short.
- **Round:** the guesthouse has one more empty bed than your ledger says. A ledger page is gone.
- **Dawn:** the abbot declares the demon has come and orders more incense. The prior asks where you were.

### Night 3: The oven (first chase)

- **Supper:** the bread tastes bitter. Ranulf offers a remedy for your headaches; beside you, Thomas shakes his head. He tells you, quietly, that the prior has been asking about you.
- **Knocks:** Walter again, with a bag that smells of the incense. A child-sized knock low on the gate; no one there (hallucination at Dose 50+).
- **Matins:** you see a brother in the choir who died on night 2 (hallucination) or a hooded stranger in his place (sober).
- **Round:** you see a light in the crypt. At the foot of the stair, the figure by the light has his back to you because he is killing a bound pilgrim. A page of the cult's book lies by the altar. You are spotted. **First chase.** You hide in the bakehouse oven and find bones (body 3). Climbing out, you are nearly caught; Thomas pulls you into the infirmary and hides you.
- **Dawn:** your keys have been moved. They've been copied: from night 4 a locked guesthouse no longer keeps anyone safe. Suspicion now drives hunting every night.

### Night 4: Edwin (midpoint)

- **The routine breaks:** there's no supper. The abbot has ordered the house to fast against the demon, and the refectory is locked. At dusk, Edwin whispers that he has seen the demon's face. He'll tell you after Matins. Thomas tells you he has seen Brother Simon out at night.
- **Knocks:** Mab, inside the gate for the first time, terrified. She saw three demons leave by the mill race.
- **Matins:** Edwin is missing from the count.
- **Round:** in the fog you hear a choir brother killed a few metres ahead of you, and reach him as his lantern is still rolling on the flags. The guest you admitted tonight is dead in the guesthouse, unless you warned him to bar the door from inside (your locked door no longer helps). The prior is kneeling by the body when you get there, and there's blood on his sleeve. You find Edwin in the charnel house (body 4). **Two hunters for the first time**: you see the demon in two places at once. If sober, you see two masked men. One loses his mask in the chase: it is Osric.
- **Later:** you find Brother Simon on his knees on the cloister flags, scrubbing blood, and he hides the rag.
- **Dawn:** someone has been in your cell. Your cot is wet and the candle clock is snapped. Your one safe space is gone.

### Night 5: The granary

- **Dusk, the choice:** you wake to a cry from the chapter house. Thomas is on the floor, "attacked", and Brother Simon is pinned by a masked man. You can reach only one. Save Thomas and Simon's throat is cut in front of you, and the masked man turns toward you; save Simon and Thomas turns up "wounded" anyway, and Simon tells you Thomas sent him to scrub the blood.
- **Supper:** Osric, whose face you saw last night, serves your bread and smiles. Eat it (lose clarity) or don't (he watches you). Thomas checks your eyes.
- **Knocks:** Joan, if you turned her away earlier, back with her brother's pilgrim badge.
- **Matins:** the abbot collapses from the incense. In the confusion, Anselm pulls you aside: the key to the crypt passage is in the granary.
- **Round:** search the grain (body 5). The ergot is in the rye. Down the hidden stair, in the crypt, a candle lights itself in front of you, with no one there. **Hunters lock you inside**; escape through the latrine chute. Roger's sergeant, left outside the gate, is killed in the lane, unless you let him wait inside.
- **Dawn:** the prior arrests you for the killings. If you can show him enough (two kinds of proof, or enough written in your ledger's notes), he believes you: he lets you go himself and stands with you on night 6. If not, Thomas speaks for you and has you released into his care.

### Night 6: The hunt

- **The routine is gone:** no supper, no gate, no duties. You wake in the infirmary at dusk (or in your cell, if the prior believed you). Anselm is dead in his bed (body 6).
- **Gate:** a knock. It is someone you know: the bailiff, Joan or Mab, depending on earlier choices. Opening the gate is one possible ending.
- **The hunt:** all five cultists in costume. Every route you've learned is in play. The crypt passage holds the proof: the costumes, the purses, the relic (which is a pig's bone) and the cult's book.
- **The Saint:** as Matins nears, the Hungry Saint comes. It kills Dunstan in the cloister, Cole at the gate and whoever is nearer of Osric and Ranulf in the choir, and it walks toward you. At Matins the cult gives it the last soul in the crypt (Brother Simon if he lived, otherwise a pilgrim) unless you stop them.
- **End:** see Endings.

## Endings

Seven endings, decided by what you carry out of the crypt, who you let in, whether the rite finishes, and your Dose at the end. They're checked in this order:

| Ending | How you get it | What happens |
| --- | --- | --- |
| **The New Faith** | Caught on night 6 after drinking Thomas's wine | You wake in a habit with a mask in your lap. Thomas: "The porter has always been one of us." |
| **The Demon** | On night 6 at Dose 75+, "the demon" corners you with a light, and you strike it (you can run instead) | You kill it. Sober epilogue: it was the prior, who came to help. You are hanged for the murders |
| **The Rising** | The last rite finishes and the count was near enough | The Hungry Saint walks out of the gate into London |
| **The Fire** | Burn the granary and crypt | The proof and the cult burn together. The record calls it a lightning strike. You are never sure who was inside |
| **The Gate** | Reach the gate with proof and open it for the bailiff | Roger's men take the abbey. The cult hangs, and the bailiff takes the land. Justice, bought by a worse man |
| **The Witness** | Escape by the mill race with Mab or Joan alive | You flee into the dark with the only other person who knows. Nobody believes either of you. Final shot: a new porter at the gate |
| **The Broken Rite** | You stopped the last rite and left any other way, or held out to dawn | The Saint is denied, for now |

Every ending closes with a short chronicle entry, written decades later, giving the official version. It never matches what you saw. Each says, in the official version's words, what became of the thing in the crypt, and the last lines follow it toward Whitechapel, 1888.

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
| Dialogue with memory | Conversations that read and set flags | Our own Talk and Conversation system (M7, `docs/dialogue.md`), with tags on the game-state flags | P1 |
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

**Second review, Nov 8 2026** (played as a horror fan, after the grilling). Verdict: worth making; as first specced, a player would likely quit around night 4. The fixes, all applied above and in `docs/mechanics.md` and `docs/full-game-run.md`:

| # | Problem | Fix |
| --- | --- | --- |
| 11 | Hidden numbers the player can't read, so choices feel random | Every hidden number has a tell in the world: crypt candles for the count, brothers falling silent for Suspicion, greetings for trust |
| 12 | "Someone dies either way" teaches that the gate doesn't matter | Each night has someone a careful porter can save, by a rule you can learn (lock the guesthouse; turn people away before the curfew bell), and the lane's talk tells you what would have saved them. On night 4 the rule breaks |
| 13 | Death costs 10–15 minutes of replay | Quiet saves before every designed chase and set piece |
| 14 | Nights too long and too alike | 30–40 minutes; from night 3 each night breaks a step of the routine |
| 15 | Thomas is obvious | One staged attack, not two; Ranulf gives the remedy and Thomas warns you off it; the prior is a stronger red herring |
| 16 | The real demon could feel like a cheat | Three things with no human explanation before night 6; staying sober and saving people is why it's weak |
| 17 | Investigating has no payoff until the end | On night 5 the prior believes you if you can show him enough, and stands with you on night 6 |
| 18 | Too many mechanics | Cut wedging; the HUD lies once, scripted; the bell's outcome follows trust and Suspicion; wind gusts are scripted; food kept simple |
| 19 | The first scare comes too late | A hook in night 0's first minutes; night 0 is 15–20 minutes; the tour is 5 |
| 20 | Fear can't be judged without sound | Placeholder sounds are wired as each system lands; final recordings stay last |

