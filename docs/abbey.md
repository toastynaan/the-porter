# Hunters and the abbey (M11)

How the cult hunts the porter by Suspicion, what he can do about it (throw things, ring the bell, cover his lantern), and how the abbey's people live around him: routines, trust, warnings, companions, lies at the gate, the rules for saving people, lateness, and the weather. The rules are `docs/mechanics.md`'s; numbers marked *mine* are starting values to tune.

## Suspicion's bands (`Hunt`, in `night_base.tscn`)

A night's beat calls `Hunt.begin()` when the round's hunting starts (from night 3 Suspicion drives it every night) and `end()` after.

| Suspicion | Hunting | Tell |
| --- | --- | --- |
| 0–29 | One costumed cultist on his patrol route; he chases what he sees but doesn't search | |
| 30–59 | He searches where he last saw the porter and checks the two hiding spots nearest it | Talk stops when he comes near; someone watches him at supper |
| 60–84 | Two hunters; one waits at the gatehouse. Three doors he used to pass are locked: the slype, the granary's cloister door and the charnel house (his key opens the charnel house; the others need another way round) | The locked doors, the man at the gate |
| 85+ | Three hunters, all searching (night 6's rules come early; night 6 itself sends the whole cult) | The brothers won't speak to him |

Three patrol routes (`Hunt/Routes`): the cloister and church, the graveyard and infirmary, the outer court and cellar. Each hunter is someone (`Hunter.wearer`): Ranulf, Cole, Dunstan by default. From night 4 they kill with a blade; before, a cord.

**A clean night** (every duty on time, nothing seen, no bell rung out of hours) takes 5 Suspicion off at dawn.

## Hunters talk and unmask

- **Voices** (`HunterVoice`): from night 4, a hunter chasing or searching calls every 6–11 s *(mine)*: a subtitle with where it comes from and whose voice it is, `"Alric..." (behind you, Brother Osric)`. Drugged (Dose 50+ *mine*), it's only "a voice". Before night 4 they're silent.
- **Unmasking** (`Hunter.unmask()`, night 4): the mask comes off, the wearer's own face shows whatever the Dose, and the mask lies at his feet for the porter to take (proof: a costume).

## Throwing (`Thrown`)

Pick up a stone, bone or cup (`Pickup`; eight lie about in `Throwables`: stones in the court and the garth, cups in the refectory, bones in the graveyard). He holds one at a time, in his right hand; a new one replaces it. E while looking at nothing usable throws it about 8 m. Where it first lands makes a noise the hunters come to look at: stone 10 m, wood 8 m, mud or grass 4 m. It stays where it comes to rest; nothing keeps it to the next night.

## The bell out of hours (`OffHoursBell`)

At the tower rope, any time but Matins. The whole abbey comes: any chase breaks off, and it's Suspicion +10. Who comes first:
1. a friend whose trust is 40 or more (Edwin; Simon, if he saved him): he walks the porter to his cell;
2. otherwise, below Suspicion 60, the prior: he questions him (three answers);
3. at 60 or more, a cultist reaches him first: a capture.

## The lantern in the wind (`Gust`)

Gusts are set, never random and never in a chase: the tower stair on night 2, the cloister door that blows open in the fog on night 4 (`night_base.tscn`, `Gusts`). Walking into one, the flame gutters for 1.5 s; covered in time it stays lit, otherwise it goes out. Out, he relights it at any lit candle or lamp by holding E for 1.5 s.

## Weather (`Weather`, `Footprints`)

Each night sets its `Weather/kind`:
- **Rain** (nights 1–2): a hunter hears half as far, and his own steps, humming and panting carry half as far to the porter. Rain falls about the porter and drums.
- **Fog** (night 4): sight is 4 m *(mine)* both ways, but an uncovered lantern is a glow a hunter can make out from 14 m *(mine)* and come to look at. The volumetric fog thickens.
- **Snow** (night 6): outdoors, the porter's and the hunters' steps leave prints for the night (up to 400). A hunter who loses him goes to his freshest print within 12 m of where he lost him.

## The abbey's people

**Routines** (`Routine`, a child of a Brother): stops by the hour, walked in view at 1.2 m/s. A stop can light a candle (a lit window), lock a door, or be "away" (he goes in and is out of sight, asleep). Places a night sets for a phase (Dusk, Supper, Matins) come first. Built now:

| Brother | Routine *(mine)* |
| --- | --- |
| Thomas | From 18:30 at his herbs in the infirmary, his window lit |
| Osric | 18:30 the kitchen; 21:00 the granary's cloister door, which he locks; 21:30 to bed |
| Hugh | 20:30 the north walk, 21:30 the outer court by the guesthouse, 22:30 the east walk, 23:30 to bed (the prior about at night, where he has no business) |
| Ranulf | From 20:00 in the church by the sacristy, his candle lit |

**Trust.** Everyone starts where `docs/mechanics.md` says (`game/story/people.gd`). Answers (`[trust who n]`), gifts and heeded warnings move it. A conversation greets him by it: `start_warm` (30+), `start_cold` (below 0), or `start`, and the same for `again`; `[if trust 30]` offers what they'd only tell someone they trust. Trust 40 brings a friend to the bell; below 0 someone won't follow him.

**The talk stops** (`Murmur`): two brothers talking low on the south walk at dusk; from Suspicion 30 they fall silent when he comes within 8 m and turn to look at him. At supper, from 30, Prior Hugh watches him. At 85+ the brothers won't speak to him at all.

**Warnings** (`Warnings`, the `[warn]` tag): a warning given before that night's death saves them. The cult hears of it, Suspicion +15, if Ranulf is within 8 m *(mine)* when he says it, or if the one he warned trusts Thomas more: a brother who trusts the porter less than 30, or anyone who distrusts him *(mine)*.

**Companions** (`Companion`, a child of a visitor): `[follow]` and `[wait]` in a talk, or a quick E once they're with him. Following, they keep a few steps behind and open doors. When he hides, they hide in the nearest free spot within 6 m, or crouch where they are. A hunter who gets within 1.2 m of one not hidden takes them: gone, and dead.

**Lies at the gate:** a visitor's detail can carry a `lie` ("no tar on a sailor's hands"). Noticing it, the porter thinks "(Something doesn't fit: ...)" and it goes in his notes, where it counts as a clue. A visitor can also have one `question` he can ask first, before the three choices.

## The rules for saving people (`Saving`, `Rumours`)

- Nights 1–3: a guest in a locked guesthouse lives.
- From night 4 the porter's keys have been copied: the lock no longer helps; a guest warned to bar the door from inside lives.
- Turned away before the curfew bell (21:00), a visitor goes to the Cross Keys and lives; after it, he's out in the lane. The gate records when (`<visitor>_refused_at`, `<visitor>_fate`).
- The lane says at the next dusk what would have saved them: `Rumours.tonight()` gives the lines whose flags hold (Hob on the old porter who locked his guests in; Agnes on the inn being shut after the bell; Hob on Jankin; Agnes on barring the door from inside; the bailiff's man left outside). The lane's dusk conversations carry them (`docs/prologue.md`, "The lane at dusk").

## Lateness (`Lateness`)

A duty that watches lateness (`watch_late` on its beat: night 3's supper, Matins bell and dawn) counts from its mark until the porter does it (`arrived()`): up to 15 minutes on time; 15 to 45 noticed (Suspicion +5, flagged for the dawn); past 45 someone comes to fetch him (Cole at supper, the prior otherwise), walking to wherever he is, and if he finds him somewhere he shouldn't be, that counts as being seen.

## The well and the wine

- **The well** (`Well`): draw water and drink: clean on nights 1–3, +5 Dose a drink from night 4. The first time, the bucket comes up heavy (the hidden body).
- **Thomas's wine** (`Wine`, night 6): +40; refusing him to his face is Suspicion +20 *(mine)*. M15 stages it.

## Sounds

New placeholders: rain, a gust, brothers murmuring, a stone's clatter.

## Tests and tools

- **`test_hunt`:** the four bands, the gatehouse, the locked doors and his key; voices by night and Dose; Osric unmasked and his mask; a stone on the flags bringing a hunter, one on the grass not; the bell's three answers, the chase breaking off, +10; a gust putting the lantern out, relighting at a candle, covering in time, no gust in a chase.
- **`test_weather`:** rain halving hearing and the hunters' sounds; fog cutting sight, the lantern's glow; snow prints outdoors only, and a hunter following them.
- **`test_people`:** greetings by trust and lines at 30; trust moved by an answer; the talk stopping at 30; silence at 85; warnings heard and unheard; the saving rules and the next dusk's rumour; a lie noticed; a companion who won't come, then follows, hides, waits and is taken; lateness noticed and Cole come to fetch him; Osric's and Thomas's routines.
- **`tools/m11_shots.sh`:** stills to `art/_review/m11/`.
