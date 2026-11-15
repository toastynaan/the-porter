class_name People
## Who's who: the name each person goes by, and what they think of the
## porter at the start (docs/systems/mechanics.md, "Trust": -100 to 100; starting
## values Thomas 40, Edwin 50, Anselm 20, Osric 20, Ranulf 0, Mab 0, Joan 0,
## Prior Hugh -20, the choir brothers 10). Ids are the node names, lower case.

const NAMES := {
	&"thomas": "Brother Thomas", &"osric": "Brother Osric", &"ranulf": "Brother Ranulf",
	&"godric": "Abbot Godric", &"hugh": "Prior Hugh", &"edwin": "Brother Edwin",
	&"anselm": "Brother Anselm", &"simon": "Brother Simon", &"cole": "Cole", &"dunstan": "Dunstan",
	&"choira": "Brother Wulfric", &"choirb": "Brother Aldo", &"choirc": "Brother Piers",
	&"warner": "Brother Bede", &"stranger": "a hooded brother",
	&"mab": "Mab", &"joan": "Joan", &"walter": "Walter", &"roger": "Roger the bailiff",
	&"hob": "Hob", &"agnes": "Agnes", &"jankin": "Jankin", &"gib": "Gib the watchman",
	&"ralph": "Ralph the chandler", &"kit": "Kit", &"margery": "Margery", &"carter": "the carter",
}
## Strangers he meets by what they do, until they tell him their name: the
## speaker in the talk files -> [id, name]. Their talks set knows_<id> where
## the name is said; from then on the talk shows the name over their lines.
## (The carter's and the warden's names are mine, 2026-11-15.)
const MET_BY_NAME := {
	"Traveller": [&"traveller", "Will Fuller"], "Carter": [&"carter", "Hamo"], "Warden": [&"warden", "Lambert"],
}
## The brothers (they have Brother Thomas to confide in).
const BROTHERS: Array[StringName] = [&"thomas", &"osric", &"ranulf", &"godric", &"hugh", &"edwin", &"anselm",
	&"simon", &"cole", &"dunstan", &"choira", &"choirb", &"choirc", &"warner"]
const START_TRUST := {
	&"thomas": 40, &"edwin": 50, &"anselm": 20, &"osric": 20, &"ranulf": 0, &"mab": 0, &"joan": 0,
	&"hugh": -20, &"choira": 10, &"choirb": 10, &"choirc": 10, &"warner": 10, &"simon": 10,
}


static func id_of(node: Node) -> StringName:
	return StringName(String(node.name).to_lower())


## What the talk shows over a speaker's lines: their name once he knows it.
static func label(speaker: String) -> String:
	var met: Array = MET_BY_NAME.get(speaker, [])
	if met.is_empty() or not GameState.has_flag(StringName("knows_" + String(met[0]))):
		return speaker
	return String(met[1])


static func display_name(id: StringName) -> String:
	var key := StringName(String(id).to_lower())
	return String(NAMES.get(key, String(id)))
