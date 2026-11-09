# Conversations (M7)

Look at someone (they're outlined) and press E, or they start it themselves (the traveller on the wagon, the carter setting you down, a visitor at the grille). They turn to you, and your view turns to their face for a moment, narrowed; then it's yours again. They say their lines; you pick one of up to three answers and say it, or walk away.

## How a talk plays

- **The camera.** Your view turns to their face over 0.45 s and narrows by 22° (70° to 48°), stays on them for 1.2 s, then widens again over 0.45 s. Move the mouse or stick and it lets go at once. From then on you look where you like while they talk; you stand still.
- **Their lines.** Each shows for its reading time; E skips to the next. The last line stays up while you choose. Each press of E counts once: held down, it skips one line and answers nothing. Something said over a talk (a pickup, a voice) shows over it, and when it's over their line shows again.
- **Answers.** Up to three, numbered, then "Walk away" (on the wagon, "Turn away"), dimmer. Pick with the number keys, or the arrow keys and E. You say the answer you pick: your name, ALRIC, over it, then they reply. An answer in brackets is something you do, not say (give alms, shake your head, say nothing): it shows in italics without the brackets, and you don't say it.
- **Narration.** A line in brackets is what you see, hear or do. It shows in italics, softer, with no brackets and no name. A bracket in a spoken line ("Osric: (He laughs.) Leave it.") shows as a small italic aside over the name, and the words without it. The ones that describe a sound stand in for it until the sound is made.
- **Walking away.** Pick "Walk away", or press any move key: the talk ends at once and you walk off. They may call something after you. A move key you were already holding when the talk began doesn't count until you let go of it.
- **Memory.** Talking to someone sets `talked_<id>`. The next time, they start at their `again` point. Answers can set flags and raise Suspicion, and can be offered only while a flag holds, so a question you've asked can drop off the list.
- **Time.** The candle clock runs while you talk.

At the gate it's the same: Walter's knock opens a conversation at the grille, with his greeting over the three gate choices (admit, turn away, send for the prior) and "Walk away". A visitor with a question offers it first: ask it (you say it, and he answers) or "Ask him nothing". Look him over from boots to face while he waits: the part of him nearest the middle of your view is the one you read. Walk away and he waits at the grille, knocking now and then, until you come back.

## Writing one

Each conversation is a `Conversation` resource, one per person per night (`game/dialogue/night0/` to `night6/`), or one per person for every dusk (`game/dialogue/lane/hob.tres`). All are drafts, and each starts with `# DRAFT`. Edit its `text` in the inspector (the expand button gives a bigger editor) or in any text editor. A person's `Talker` node names the conversation, and the phases in which they'll talk (the brothers at dusk; Mab until the knocks).

```
# A note; ignored.
== start
(A round brother at the kitchen fire, flour to the elbow.)
Osric: The porter! At last, a man with an honest appetite.
-> topics

== again
Osric: Back again? Smell that.
-> topics

== topics
* [if not n3_osric_bread] What's this about the bread? -> bread
* What's for supper, brother? -> supper
* (Nod, and leave him to it.) -> end

== bread [set n3_osric_bread]
Osric: (He laughs.) Extra for you tonight, porter. A man on the gate needs feeding.
-> topics

== supper
Osric: Pease pottage, and our own bread.
-> topics

== leave
Osric: Come hungry!
```

| Line | Means |
| --- | --- |
| `== name` | A point in the talk. It starts at the first point, or at `again` if you've talked to them before |
| `Name: line` | Someone says a line |
| `Name: (aside) line` | A line with a small aside over the name (how they say it) |
| `(line)` with no name | Narration: what the porter sees, hears or does |
| `* answer -> point` | An answer, which he says, and where it leads: another point, or `end`. Three at most |
| `* (answer) -> point` | An answer he does rather than says (give alms, say nothing) |
| `-> point` | Goes on to another point with no answer asked |
| `-> point [if flag]` | Goes there only if the tags hold; a point can list several, and the first that holds is taken (put one with no tags last) |
| `== leave` | Said as you walk away in the middle of a talk |
| `# note` | Ignored |

**Tags**, in square brackets on an answer or after a point's name:

| Tag | Does |
| --- | --- |
| `[if flag]`, `[if not flag]`, `[if flag=value]` | The answer is offered (or the jump taken) only then (e.g. `[if n3_walter=admitted]`) |
| `[if night=2]` | Only on that night (the lane's talks have a branch for each night) |
| `[drink]` | He drinks an ale (`docs/prologue.md`, "Drinking") |
| `[set flag]`, `[set flag=value]` | Sets a flag when the answer is picked or the point is reached |
| `[suspicion 5]` | Raises Suspicion |
| `[item mab_bread]` | Puts something in his satchel (`game/items/items.gd`) |
| `[note bread_warning]` | Writes a clue in his notes (`game/story/clues.gd`) |
| `[trust mab 5]` | Changes what someone thinks of him |
| `[if trust 30]`, `[if not trust 30]` | Offered only if the one he's talking to trusts him that much (or not) |
| `[warn]` | Warns the one he's talking to (`docs/abbey.md`, "Warnings") |
| `[follow]`, `[wait]` | The one he's talking to follows him, or waits (`Companion`) |

**Greetings follow trust:** a talk starts at `start_warm` if they trust him 30 or more, `start_cold` below 0, else `start`; the same for `again_warm`, `again_cold` and `again`, where those points exist.

A point whose answers have all dropped off ends the talk after its lines. `test_dialogue` reads every conversation under `game/dialogue/` and fails on a mistake: an unknown point, a fourth answer, an answer with no `->`, a tag it doesn't know.

## Night 3's conversations

| Who | Where at dusk | Questions |
| --- | --- | --- |
| Thomas | Infirmary | Your headaches; Anselm; the brother found in the bell tower |
| Osric | Kitchen | The bread; supper; the page torn from the ledger (Suspicion +5: the wrong question to the wrong brother) |
| Ranulf | Church | The incense; the relic; the candles |
| Abbot Godric | Chapter house | The demon; how you're doing as porter; his blessing |
| Prior Hugh | North walk | He asks where you were. Tell him what you saw (Suspicion +10: Ranulf overhears), say you were at the gate, or ask what he wants |
| Edwin | West walk | How he is; the bread warning; the bell tower |
| Anselm | Infirmary | "Don't let them in after the bell"; keeping the gate; his eyes |
| Dunstan, Cole | Woodpile, the gate | They say nothing (lay brothers don't talk) |
| The three choir brothers | South walk, nave, east walk | The brother who died; the bread |
| Mab | Outside the gate | What she has seen; whether she eats the abbey's bread; alms |
| The carter, the woman | The lane | Short exchanges before they go home |

The questions that drop off once asked set `n3_<who>_<topic>` flags. The two Suspicion numbers are the design doc's; which questions carry them is mine.
