class_name Items
## What the porter can carry in his satchel (docs/systems/mechanics.md, "Your hands"):
## keys (GameState.keys), evidence, clean food and the thing in his hand.
## Each item has a name and the line he reads in the satchel. Evidence kinds
## are what the Gate ending counts (two different kinds of proof).

## id -> [name, line, kind]
const ALL := {
	&"mask": ["A carved mask", "Pale wood, a long face, eye holes and no mouth. A crack runs down it from the brow.", &"costume"],
	&"hoof_soles": ["Carved hoof soles", "Wooden hooves on leather straps, made to be tied under boots.", &"costume"],
	&"purse": ["A pilgrim's purse", "Empty. A scallop badge is stitched to the flap, and a name inside it in ink.", &"purse"],
	&"pig_bone": ["The relic", "The saint's finger bone, out of its glass. It is a pig's knuckle.", &"relic"],
	&"book_page": ["A page of a book", "Black letters in a hand you don't know. Ten candles drawn in a ring.", &"book"],
	&"book": ["The cult's book", "Heavy, bound in skin. The page torn from it fits the stub.", &"book"],
	&"apple": ["A windfall apple", "Bruised, cold from the grass. Nothing the abbey baked.", &"food"],
	&"mab_bread": ["A heel of bread", "Mab's, from the town. Not the abbey's rye.", &"food"],
	&"stone": ["A stone", "Small enough to throw.", &"throwable"],
	&"bone": ["A bone", "A knuckle of something. Small enough to throw.", &"throwable"],
	&"cup": ["A wooden cup", "Small enough to throw.", &"throwable"],
}
## The keys, by what they lock.
const KEY_NAMES := {&"gate": "the gate", &"guesthouse": "the guesthouse", &"charnel": "the charnel house",
	&"crypt_passage": "the crypt passage"}


static func display_name(id: StringName) -> String:
	return String(ALL[id][0]) if ALL.has(id) else String(id)


static func line(id: StringName) -> String:
	return String(ALL[id][1]) if ALL.has(id) else ""


static func kind(id: StringName) -> StringName:
	return ALL[id][2] if ALL.has(id) else &""


## The kinds of proof among `ids` (costume, purse, relic, book).
static func proof_kinds(ids: Array[StringName]) -> Array[StringName]:
	var out: Array[StringName] = []
	for id in ids:
		var k := kind(id)
		if k in [&"costume", &"purse", &"relic", &"book"] and not out.has(k):
			out.append(k)
	return out
