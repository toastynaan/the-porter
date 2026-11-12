# Faces and reading people

Everyone who speaks shows it on their face: a mood for each line, and now and then a twitch, a tell. Some things people say are claims worth weighing. Alric answers a claim with a stance, believe, press or confront, and how he read them changes what they tell him, what they think of him, and what the cult knows. Nothing on the screen says whether he read them right. Their face, their answer and his notes do.

Inspired by L.A. Noire's interrogations (2011), and built around what players found wrong with them (below).

## What L.A. Noire did, and what we take

L.A. Noire's detective questions a witness from his notebook. Each answer is a statement; the player watches the actor's captured face (MotionScan) and picks Truth, Doubt or Lie (renamed Good Cop, Bad Cop, Accuse in the 2017 release). Lie needs evidence from the notebook. A right call opens more of the story, a wrong one closes that line for good. A chime and a tick or cross in the notebook said which. Intuition points removed a wrong option.

What players found wrong, and what we do instead:

| Their problem | Ours |
| --- | --- |
| Three vague buttons. Players picked "Doubt" and the detective shouted an accusation they never meant | Every stance is a line Alric says, written out before you pick it. You always know what you're saying |
| Doubt and Lie were hard to tell apart | Press and confront differ by one thing: confront needs proof from your notes, and names it |
| Tells were exaggerated, and innocent people showed them too, so faces lied about lying | Everyone has a baseline: how *they* look when they tell the truth. A tell is a change from their own baseline, not a twitch in general. Nervous isn't lying: the prior glares at everyone |
| A chime said right or wrong, which turned reading into a quiz | No sound and no tick. Their reaction, and Alric's own note, are all you get |
| One right answer, and a wrong one closed the case | Wrong reads cost something but never block the story. What you miss is what they would have told you |

## Moods and tells

Every spoken line in a script carries a face, in braces between the name and the colon:

```
Thomas {warm}: Sit, brother. You look done in.
Thomas {warm, still}: I was with Anselm all night. He was very bad.
Hugh {cold, jaw}: Where were you at Lauds?
Simon {afraid, look down, swallow}: I didn't see anything. I was asleep.
```

The words are shown as before; the braces are not. The first word is the **mood**, held for the line. Any after it are **tells**, each played once during the line.

**Moods** (the face held while the line is up):

| Mood | Face |
| --- | --- |
| `calm` | Level brows, mouth at rest, steady eyes |
| `warm` | Brows soft, a small smile |
| `glad` | Brows up, a wide smile |
| `amused` | One brow up, a crooked smile |
| `grave` | Brows low and level, mouth flat |
| `sad` | Brows tilted up in the middle, mouth corners down |
| `weary` | Lids heavy, mouth slack, head a little down |
| `afraid` | Brows up and drawn together, eyes wide, mouth tight |
| `wary` | Brows low, eyes narrow, head back a little |
| `angry` | Brows down hard, mouth tight, chin forward |
| `cold` | Brows level, eyes still, mouth flat, no blinks |
| `ashamed` | Head down, eyes down, mouth tight |
| `pleading` | Brows up in the middle, head forward |
| `pained` | Brows knit, eyes shut tight, mouth pulled |
| `drunk` | Lids heavy, head loose, a slow smile |
| `blank` | Nothing: the lay brothers, the dead |

**Tells** (one-off twitches during a line):

| Tell | What the face does |
| --- | --- |
| `glance` | Eyes slide to one side and back |
| `look down` | Eyes drop and stay down a moment |
| `look away` | Head and eyes turn away, then back |
| `swallow` | The throat moves |
| `blink` | Three quick blinks |
| `lip` | Lips press together |
| `jaw` | The jaw sets |
| `brow` | Brows flick up and down |
| `smile` | A smile comes and goes, too quickly |
| `still` | Everything stops: no blinks, no movement, for the length of the line |
| `nod` | A small nod |
| `shake` | A small shake of the head |
| `flinch` | The head jerks back a little |

A tell is just a twitch. It means nothing alone. It means something when it isn't how that person usually looks.

### Baselines

Each person has a baseline in `game/people/faces.gd`: how often they blink, how steady their eyes are, where they usually look, what they do when they talk. Their truthful lines use their baseline mood and tells; their lies and evasions break from it. Some baselines the story needs:

- **Thomas:** warm, soft eyes, blinks often, nods while you talk. He lies well: when he lies his face goes `still` and the smile stays. The tell is the absence of his usual movement.
- **Prior Hugh:** cold, a hard stare, `jaw` often. He glares when he tells the truth. He is the obvious suspect and his face says so, and it is wrong.
- **Simon:** ashamed, eyes down nearly always. `look down` means nothing from Simon; looking you in the eye does.
- **Anselm:** blind. His eyes don't move, so you read him by his mouth and throat: `swallow`, `lip`.
- **Osric:** glad, loud, laughing. His tell is a `smile` that comes too fast.
- **Ranulf:** grave, measured, few blinks. His tell is a `glance` toward the church.
- **Joan:** wary with everyone. She lies about her husband (`glance`, `lip`), and tells the truth about her brother (steady, `sad`).
- **Walter:** amused, never still, always selling. His tell is that he stops selling.

## Claims and stances

A claim is a line worth weighing. It is marked on its point with `[claim <id> <truth>]`, and the point's last line is the claim:

```
== alibi [claim thomas_alibi lie]
Thomas {warm, still}: I was with Anselm all night. He was very bad.
* [believe] God keep you for it, brother. -> alibi_believed
* [press] All night? You never slept? -> alibi_pressed
* [confront crypt_candles] Then whose candle was burning in the crypt at Lauds? -> alibi_broken
```

**Truth** is one of:
- `true`: they mean it, and it's so.
- `hiding`: true as far as it goes, and they're holding something back.
- `lie`: it isn't so.

**Stances** are answers marked `[believe]`, `[press]` or `[confront <note>]`. A confront answer names the note in Alric's ledger that proves it, and is offered only if he has that note. A claim's answers can mix stances with ordinary answers. Each stance leads where its writer sends it; the game does the rest:

| The claim is | Believe | Press | Confront |
| --- | --- | --- | --- |
| `true` | Right. Trust +2 | Wrong: they close up. Trust −2 | Wrong: trust −10, and they remember it |
| `hiding` | Wrong: you never hear the rest | Right: they tell the rest. Trust +1 | Too hard: they close up. Trust −5 |
| `lie` | Wrong: you never hear the truth | Half: they dig in and close up | Right: the truth, and a note. If they're in the cult, Suspicion +10 *(mine)*: now they know you know |

*(The numbers are mine.)* "Close up" is written by the writer: the point a wrong stance leads to ends the topic, and the claim's flags keep it shut for the night.

Every read sets `read_<claim>` to `believed`, `pressed` or `confronted`, and `read_<claim>_right` if it was the right call, so later talks can follow it ("You called me a liar on Tuesday"). Accusing someone wrongly sets `wronged_<person>`.

### Feedback

There is no sound, icon or tick. Alric writes each read in his ledger notes in his own hand:

> Thomas says he was with Anselm all night. His face never moved. I don't believe him.
> The prior says he was praying in the church. I believe him.
> Simon says he saw nothing. He knows more than he says.

The note says what Alric thought, not whether he was right. A wrong read and a right read look the same on the page. The page is where you go back over it.

## Seeing a face

Reading a face is looking at it. Nothing in the game reads it for you.

- **Light.** At night a face is only readable in light: your lantern uncovered, a candle, a fire. In the dark the face is a shape. Faces lit from below look wrong even when they're kind (Look and Feel, "Faces lit from below").
- **Distance.** Past about 4 m the placeholder face is too small to read. Up close, at the grille or across a table, it's easy.
- **Looking.** The talk turns your view to their face for a moment, and then the view is yours. A tell plays a moment into the line, so if you've looked away, you miss it.
- **The drug.** From Dose 50, faces twitch with tells nobody made. From Dose 75, a face sometimes shows the wrong mood for a moment. The drug affects your senses, not the world, so a drugged reading is a bad reading.
- **Accessibility.** A setting, *Describe faces*, off by default, writes the mood and tells as an aside beside the name for players who can't see the face well.

## The face (placeholder)

Until the real character models exist, each placeholder figure (`BrotherFigure`) has a `FaceRig`:
- two eyes that look about,
- two brows that rise, fall and tilt,
- a mouth line that widens, tightens and moves with speech,
- lids that blink,
- a throat that swallows,
- a head that nods, shakes, turns, tips and flinches.

It moves in steps at 15 frames a second, like every other character (Look and Feel, "PSX"). Between lines it idles on its baseline: blinks, small glances, breathing.

The real models plug into the same interface (`FaceRig.mood()`, `tell()`, `speak()`): each mood is a face texture, and tells are the head, eye and texture changes.

## Where it's used

Every spoken line in every conversation and every chapter's scripted lines carries a mood. Tells go where people would show them, not on every line. Claims go where the story has someone lying or holding back:
- **the cult:** Thomas, Ranulf, Osric, Cole and Dunstan;
- **people hiding things:** Anselm, Simon, Joan;
- **people who look guilty and aren't:** Prior Hugh;
- **visitors at the grille** whose story doesn't fit, alongside reading their boots and hands.

There are a few claims a night, not every line.
