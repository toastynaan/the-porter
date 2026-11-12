class_name Faces
## How people's faces work (docs/systems/faces.md): the moods and tells a
## script may give a line, each person's baseline, and finding the face of
## whoever is speaking.
##
## A spoken line carries its face in braces between the name and the colon:
## "Thomas {warm, still}: I was with Anselm all night." The first word is the
## mood, held for the line; the rest are tells, each played once.

const MOODS: Array[StringName] = [&"calm", &"warm", &"glad", &"amused", &"grave", &"sad", &"weary",
	&"afraid", &"wary", &"angry", &"cold", &"ashamed", &"pleading", &"pained", &"drunk", &"blank"]
const TELLS: Array[StringName] = [&"glance", &"look down", &"look away", &"swallow", &"blink", &"lip",
	&"jaw", &"brow", &"smile", &"still", &"nod", &"shake", &"flinch"]

## The cult (design doc, "Inside the walls"): reading one of them right
## tells them you know.
const CULT: Array[StringName] = [&"thomas", &"ranulf", &"osric", &"cole", &"dunstan"]
## Who Alric writes "her" of in his notes.
const WOMEN: Array[StringName] = [&"mab", &"joan", &"agnes", &"kit", &"margery", &"townswoman",
	&"lane_woman", &"woman"]

## Each person's baseline: how they look when they tell the truth.
##   mood: the face they rest in.
##   blink: blinks a second.
##   gaze: how far their eyes wander while idle (0 steady, 1 restless).
##   down: where their eyes rest (0 on you, 1 on the floor).
##   habit: a tell they do now and then as they talk, which means nothing from them.
##   blind: their eyes don't move.
const BASELINES := {
	&"thomas": {"mood": &"warm", "blink": 0.45, "gaze": 0.3, "habit": &"nod"},
	&"hugh": {"mood": &"cold", "blink": 0.12, "gaze": 0.05, "habit": &"jaw"},
	&"simon": {"mood": &"ashamed", "blink": 0.35, "gaze": 0.5, "down": 0.8, "habit": &"look down"},
	&"anselm": {"mood": &"weary", "blink": 0.05, "gaze": 0.0, "blind": true, "habit": &"lip"},
	&"osric": {"mood": &"glad", "blink": 0.3, "gaze": 0.4, "habit": &"smile"},
	&"ranulf": {"mood": &"grave", "blink": 0.12, "gaze": 0.1},
	&"godric": {"mood": &"weary", "blink": 0.3, "gaze": 0.35, "down": 0.2},
	&"edwin": {"mood": &"warm", "blink": 0.35, "gaze": 0.45, "habit": &"brow"},
	&"joan": {"mood": &"wary", "blink": 0.3, "gaze": 0.3},
	&"walter": {"mood": &"amused", "blink": 0.35, "gaze": 0.7, "habit": &"brow"},
	&"mab": {"mood": &"wary", "blink": 0.25, "gaze": 0.4, "down": 0.3},
	&"cole": {"mood": &"blank", "blink": 0.1, "gaze": 0.05},
	&"dunstan": {"mood": &"blank", "blink": 0.1, "gaze": 0.05},
}
const DEFAULT_BASELINE := {"mood": &"calm", "blink": 0.3, "gaze": 0.3}

## Names a script uses for someone other than their People id.
const ALIASES := {
	&"wulfric": &"choira", &"aldo": &"choirb", &"piers": &"choirc", &"bede": &"warner",
}


## Splits "Thomas {warm, still}" into [name, mood, tells]. No braces: the
## name as it is, no mood, no tells.
static func split(speaker: String) -> Array:
	var open := speaker.find("{")
	var close := speaker.find("}")
	if open < 0 or close < open:
		return [speaker.strip_edges(), &"", PackedStringArray()]
	var name := (speaker.left(open) + speaker.substr(close + 1)).strip_edges()
	var words := speaker.substr(open + 1, close - open - 1).split(",", false)
	var mood := &""
	var tells := PackedStringArray()
	for i in words.size():
		var w := words[i].strip_edges().to_lower()
		if i == 0:
			mood = StringName(w)
		else:
			tells.append(w)
	return [name, mood, tells]


## What is wrong with a face's words: unknown moods or tells. Empty if fine.
static func errors(speaker: String) -> PackedStringArray:
	var out := PackedStringArray()
	if speaker.count("{") != speaker.count("}"):
		out.append("a { with no }")
		return out
	var parts := split(speaker)
	if parts[1] != &"" and not MOODS.has(parts[1]):
		out.append("unknown mood {%s}" % parts[1])
	for t: String in parts[2]:
		if not TELLS.has(StringName(t)):
			out.append("unknown tell {%s}" % t)
	return out


## The People id a script's name stands for: "Prior Hugh" is hugh, "Piers"
## is choirc, "Traveller" is traveller.
static func key_of(name: String) -> StringName:
	var words := name.strip_edges().to_lower().split(" ", false)
	if words.is_empty():
		return &""
	var last := StringName(words[-1])
	return ALIASES.get(last, last)


static func baseline(who: StringName) -> Dictionary:
	return BASELINES.get(who, DEFAULT_BASELINE)


## The face of whoever a script calls `name` in the scene, or null. In a talk
## (`partner` given), the partner's face if it answers to the name, else
## anyone's that does, else the partner's: a visitor's face answers to
## whatever the script calls them. Outside a talk, only a face that answers
## to the name.
static func rig_for(tree: SceneTree, name: String, partner: Node = null) -> FaceRig:
	var key := key_of(name)
	if key == &"":
		return null
	var theirs: FaceRig = FaceRig.on(partner) if partner and is_instance_valid(partner) else null
	if theirs and _answers(theirs, key):
		return theirs
	for r: FaceRig in tree.get_nodes_in_group(&"faces"):
		if _answers(r, key) and r.is_visible_in_tree():
			return r
	return theirs


static func _answers(r: FaceRig, key: StringName) -> bool:
	return r.who == key or key_of(People.display_name(r.who)) == key


static func pronoun(who: StringName) -> String:
	return "her" if WOMEN.has(who) else "him"
