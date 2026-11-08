# Conversations (M7)

Look at someone and press E. They turn to you, and your view eases in on their face and narrows. They say their line; you pick one of up to three answers, or walk away. Every line is a placeholder in brackets until the script is written.

## How a talk plays

- **The camera.** Your view turns to their face over 0.45 s and narrows by 22° (70° to 48°). You can look about within 30° of their face, so you can still study them. You stand still.
- **Their lines.** Each shows for its reading time; E skips to the next. The last line stays up while you choose.
- **Answers.** Up to three, numbered, then "Walk away", dimmer. Pick with the number keys, or the arrow keys and E.
- **Walking away.** Pick "Walk away", or press any move key: the talk ends at once, your view widens again, and you walk off. They may call something after you.
- **Memory.** Talking to someone sets `talked_<id>`. The next time, they start at their `again` point. Answers can set flags and raise Suspicion, and can be offered only while a flag holds, so a question you've asked can drop off the list.
- **Time.** The candle clock runs while you talk.

At the gate it's the same: Walter's knock opens a conversation at the grille, with his greeting over the three gate choices (admit, turn away, send for the prior) and "Walk away". There you can look him over from boots to face (40° either side, 50° up and down), and the part of him nearest the middle of your view is the one you read, starting with his face. Walk away and he waits at the grille, knocking now and then, until you come back.

## Writing one

Each conversation is a `Conversation` resource, one per person per night: `game/dialogue/night3/osric.tres`. Edit its `text` in the inspector (the expand button gives a bigger editor) or in any text editor. A person's `Talker` node names the conversation, and the phases in which they'll talk (the brothers at dusk; Mab until the knocks).

```
# A note; ignored.
== start
Osric: (Placeholder: Osric greets you.)
-> topics

== again
Osric: (Placeholder: Osric, still at the fire.)
-> topics

== topics
* [if not n3_osric_bread] (Ask about the bread.) -> bread
* (Ask what is for supper.) -> supper
* (Wish him good night.) -> end

== bread [set n3_osric_bread]
Osric: (Placeholder: he promises you extra bread.)
-> topics

== supper
Osric: (Placeholder: Osric on tonight's supper.)
-> topics

== leave
Osric: (Placeholder: he calls after you.)
```

| Line | Means |
| --- | --- |
| `== name` | A point in the talk. It starts at the first point, or at `again` if you've talked to them before |
| `Name: line` | Someone says a line |
| `(line)` with no name | What the porter notices |
| `* answer -> point` | An answer and where it leads: another point, or `end`. Three at most |
| `-> point` | Goes on to another point with no answer asked |
| `== leave` | Said as you walk away in the middle of a talk |
| `# note` | Ignored |

**Tags**, in square brackets on an answer or after a point's name:

| Tag | Does |
| --- | --- |
| `[if flag]`, `[if not flag]`, `[if flag=value]` | The answer is offered only then (e.g. `[if n3_walter=admitted]`) |
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
