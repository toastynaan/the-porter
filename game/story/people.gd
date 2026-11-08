class_name People
## Who's who: the name each person goes by, and what they think of the
## porter at the start (docs/mechanics.md, "Trust": -100 to 100; starting
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
const START_TRUST := {
	&"thomas": 40, &"edwin": 50, &"anselm": 20, &"osric": 20, &"ranulf": 0, &"mab": 0, &"joan": 0,
	&"hugh": -20, &"choira": 10, &"choirb": 10, &"choirc": 10, &"warner": 10, &"simon": 10,
}


static func id_of(node: Node) -> StringName:
	return StringName(String(node.name).to_lower())


static func display_name(id: StringName) -> String:
	var key := StringName(String(id).to_lower())
	return String(NAMES.get(key, String(id)))
