# Conversations (M7)

Look at someone (they're outlined) and press E, or they start it themselves (the traveller on the wagon, the carter setting you down, a visitor at the grille). They turn to you and stand still, and your view turns to their face for a moment, narrowed; then it's yours again. They say their lines; you pick one of up to three answers and say it, or walk away.

## How a talk plays

- **The camera.** Your view turns to their face over 0.9 s and narrows by 22° (70° to 48°), stays on them for 1.2 s, then widens again over 0.9 s *(mine; it was 0.45 s, which read as a snap)*. Pull the mouse (24 pixels in all) or push the stick and it lets go at once, even while it is still turning. From then on you look where you like while they talk; you stand still. A talk can point your eyes at what it's about instead of at the speaker (`Talk.converse(..., watch)`): the view goes there, narrowed, and follows it for 3.6 s. The traveller's talk about the body cart does: you look at the body, not at him.
- **They stand still too.** Whoever you're talking to stops where they are until the talk is over, then goes on: a passer-by doesn't walk off, a brother doesn't leave for supper while you look away, the lane's people don't go home at the curfew bell in the middle of a line. If they do go (taken out of the world, or more than 6 m off *(mine)*), the talk is cut short.
- **Their lines.** Each shows for its reading time; E skips to the next. Each press of E counts once: held down, it skips one line and answers nothing. Every click of the mouse counts as its own press.
- **One turn to someone is one talk.** A talk shouldn't end after each answer and make you turn to them again: its points lead back to the questions that are left (`-> topics`), and someone with nothing left to say says so, not just "Brother?".
- **Answers.** Up to three, numbered, then "Walk away" (on the wagon, "Turn away"), dimmer. A point's last line comes up together with its answers and stays while you choose. Pick with the number keys, or the arrow keys (or the wheel) and E. For 0.3 s after they come up *(mine)* E answers nothing, so the press that skipped the last line can't answer for you; a number key answers at once. You say the answer you pick: your name, ALRIC, over it, then they reply. An answer in brackets is something you do, not say (give alms, shake your head, say nothing): it shows in italics without the brackets, and you don't say it.
- **Narration.** A line in brackets is what you see, hear or do. It shows in italics, softer, with no brackets and no name. A bracket in a spoken line ("Osric: (He laughs.) Leave it.") shows as an italic aside beside the name, and the words without it. The ones that describe a sound stand in for it until the sound is made.
- **Heard meanwhile.** Anything said while you're talking or being asked something that isn't part of it (a thing you notice, the supper bell, a voice in the dark) shows small above the talk's line. It never takes the question's place, and E doesn't skip it; it goes when its time is up.
- **Walking away.** Pick "Walk away", or press any move key: the talk ends at once and you walk off. They may call something after you. A move key you were already holding when the talk began doesn't count until you let go of it.
- **Memory.** Talking to someone sets `talked_<id>`. The next time, they start at their `again` point. Answers can set flags and raise Suspicion, and can be offered only while a flag holds, so a question you've asked can drop off the list.
- **Time.** The candle clock runs while you talk.

At the gate it's one talk each time you come to the grille. Walter's knock opens it: his greeting, with his question under it if he has one ("What's in the bag?", or "Ask him nothing"). Ask, and you say it and he answers; then, in the same talk, the three gate choices (admit, turn away, send for the prior) and "Walk away" come up under the last thing he said. He greets you once. Look him over from boots to face while you choose: the part of him nearest the middle of your view is the one you read, and what you notice shows above his line. Walk away and he waits at the grille, knocking now and then, until you come back.

**Questions outside a talk.** A beat can ask you something with no conversation open (the bread, the remedy, the wine, whom to tell about a body, the prior's question at dawn). The line just said stays up over the answers. What you do is in brackets, so in italics ("Eat the bread." / "Palm the bread."); what you say, you say, as in a talk. One question is open at a time: a second waits for the first to be answered.

## How it looks

One column at the bottom of the screen, in the book face the menus use (EB Garamond), drawn by `game/talk/talk_view.gd`:

- **The name** in small capitals, lantern-coloured; your own name is paler. A line's aside sits beside it in italics.
- **The line**, centred. Narration is in italics, softer.
- **The answers** in a block under it, left-aligned and numbered. The one the arrows are on is brighter, with a thin flame-coloured bar and its number lit. Things you do are in italics; "Walk away" stands a little apart, dimmer.
- **Heard meanwhile**, small, at the top.
- A soft dark gradient lies under it all, so it reads over a lit wall. The Settings' dark band draws a solid panel instead. The Settings' subtitle size scales everything.
- Lines and answers fade in and out (0.16 s in, 0.22 s out *mine*). A line already up rises to make room when its answers come up under it; with less motion on, it jumps. The speaker's name stays lit while the same person goes on talking.

`tools/shots/talk_shots.sh` renders it all to `art/_review/talk/`, driven by the real keys.

## Writing one

Each conversation is a `Conversation` resource, one per person per night (`game/chapters/night0/dialogue/` to `night6/`), or one per person for every dusk (`game/chapters/common/lane/hob.tres`). All are drafts, and each starts with `# DRAFT`. Edit its `text` in the inspector (the expand button gives a bigger editor) or in any text editor. A person's `Talker` node names the conversation, and the phases in which they'll talk (the brothers at dusk; Mab until the knocks).

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
| `Name {mood, tell}: line` | A line with a face: a mood held for the line, then tells played once (`docs/systems/faces.md`). The braces don't show |
| `Name: (aside) line` | A line with a small aside over the name (how they say it) |
| `(line)` with no name | Narration: what the porter sees, hears or does |
| `* answer -> point` | An answer, which he says, and where it leads: another point, or `end`. Three at most. The point's last line comes up with them |
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
| `[drink]` | He drinks an ale (`docs/places/prologue.md`, "Drinking") |
| `[set flag]`, `[set flag=value]` | Sets a flag when the answer is picked or the point is reached |
| `[suspicion 5]` | Raises Suspicion |
| `[item mab_bread]` | Puts something in his satchel (`game/items/items.gd`) |
| `[note bread_warning]` | Writes a clue in his notes (`game/story/clues.gd`) |
| `[trust mab 5]` | Changes what someone thinks of him |
| `[if trust 30]`, `[if not trust 30]` | Offered only if the one he's talking to trusts him that much (or not) |
| `[warn]` | Warns the one he's talking to (`docs/systems/abbey.md`, "Warnings") |
| `[follow]`, `[wait]` | The one he's talking to follows him, or waits (`Companion`) |
| `[claim id true]`, `[claim id hiding]`, `[claim id lie]` | On a point: its last line is a claim to weigh (`docs/systems/faces.md`, "Claims and stances") |
| `[believe]`, `[press]`, `[confront note]` | On an answer to a claim: Alric's stance, shown small beside it. A confrontation is offered only with that note in his ledger |

**Greetings follow trust:** a talk starts at `start_warm` if they trust him 30 or more, `start_cold` below 0, else `start`; the same for `again_warm`, `again_cold` and `again`, where those points exist.

A point whose answers have all dropped off ends the talk after its lines. `test_dialogue` reads every conversation under `game/chapters/` and fails on a mistake: an unknown point, a fourth answer, an answer with no `->`, a tag it doesn't know.

**From a beat's script** (`Talk`, `game/talk/talk.gd`): `say()` for a line of the night's; `choose()` for a question (it keeps the line just said up over the answers); `ask()` to say a line with answers under it at once; `answer()` for a question whose spoken answer he then says. A beat that opens a talk itself (`begin()` to `end()`, as the gate does) says the talk's own lines with `line()`, so they have the main place and E skips them; `say()` there is something heard meanwhile.

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
