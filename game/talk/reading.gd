class_name Reading
## Weighing what people say (docs/systems/faces.md, "Claims and stances"):
## when Alric answers a claim with a stance, what it costs or gains, and the
## note he writes about it. Nothing on the screen says whether he was right.

const STANCES := ["believe", "press", "confront"]
## true: they mean it, and it's so. hiding: true, and they hold something
## back. lie: it isn't so, and they know it. mistaken: it isn't so, and they
## believe it (the prior's accusation). misleading: true words said to lead
## him wrong (Thomas pointing at innocent men).
const TRUTHS := ["true", "hiding", "lie", "mistaken", "misleading"]

## What each read does to trust, by [truth][stance]. *(mine)*
const TRUST := {
	"true": {"believe": 2, "press": -2, "confront": -10},
	"hiding": {"believe": 0, "press": 1, "confront": -5},
	"lie": {"believe": 0, "press": 0, "confront": 0},
	"mistaken": {"believe": 0, "press": 1, "confront": 2},
	"misleading": {"believe": 0, "press": 0, "confront": 0},
}
## The right stances for each truth. A confrontation is only ever offered
## with its proof, so where it's listed it is a right read.
const RIGHT := {
	"true": ["believe"],
	"hiding": ["press"],
	"lie": ["confront"],
	"mistaken": ["press", "confront"],
	"misleading": ["press", "confront"],
}
## Confronting one of the cult with the truth: they know you know. *(mine)*
const CULT_SUSPICION := 10

## What Alric writes after the claim, by stance.
const VERDICT := {
	"believe": "I believe %s.",
	"press": "I don't think that's all of it. I pressed %s.",
	"confront": "I don't believe %s, and I told %s so.",
}


## Alric took `stance` on claim `id` (whose `truth` the script knows) made
## by `who` in `line`: sets read_<id>, changes trust and Suspicion, and
## writes his note. True if he read them right.
static func read(id: StringName, truth: String, stance: String, who: StringName, line: String) -> bool:
	var right := is_right(truth, stance)
	GameState.set_flag(StringName("read_%s" % id), StringName(_past(stance)))
	if right:
		GameState.set_flag(StringName("read_%s_right" % id))
	if who != &"":
		var change: int = TRUST.get(truth, {}).get(stance, 0)
		if change != 0:
			GameState.change_trust(who, change)
		# Accusing someone who told the truth: they remember it.
		if stance == "confront" and truth in ["true", "hiding"]:
			GameState.set_flag(StringName("wronged_%s" % who))
		# Showing one of the cult you see through them.
		if stance == "confront" and truth in ["lie", "misleading"] and Faces.CULT.has(who):
			GameState.raise_suspicion(CULT_SUSPICION)
	GameState.note(StringName("read_%s" % id), note_text(who, line, stance))
	return right


static func is_right(truth: String, stance: String) -> bool:
	return (RIGHT.get(truth, []) as Array).has(stance)


## His note: what they said, and what he made of it. Never whether he was right.
static func note_text(who: StringName, line: String, stance: String) -> String:
	var name := People.display_name(who) if who != &"" else "They"
	var words := Talk.aside(line)[1] as String
	var him := Faces.pronoun(who)
	var verdict: String = VERDICT.get(stance, "")
	verdict = verdict % ([him, him] if verdict.count("%s") == 2 else [him])
	return "%s says, \"%s\" %s" % [name, words, verdict]


static func _past(stance: String) -> String:
	return {"believe": "believed", "press": "pressed", "confront": "confronted"}.get(stance, stance)
