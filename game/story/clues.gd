class_name Clues
## Every clue the porter can write in his ledger's notes (docs/mechanics.md,
## "Investigation"): something he finds, a lie he notices, something he
## hears that matters, someone missing. Six of them, or two kinds of proof,
## and the prior believes him on night 5 (PriorJudgement). The notes are in
## his own hand, so they're plain and short. DRAFT lines.

const ALL := {
	&"sand_by_the_well": "Sand on the court by the well this morning, where I saw the man killed. Thomas says a beast was slaughtered there.",
	&"bread_warning": "A brother of the choir told me at supper not to eat the bread. Something is wrong with it.",
	&"knock_no_one": "A knock at the gate after midnight. No one there. Mab saw no one come.",
	&"merchant_rope": "Rope marks on the merchant's wrists. A man who falls in a pond drunk doesn't tie his own hands.",
	&"merchant_purse": "The merchant's purse is gone. He had it at the gate.",
	&"merchant_moved": "I went for help and the merchant's body was gone from the pond when I came back.",
	&"sailor_knot": "The brother in the bell tower hangs from a sailor's knot. The only sailor this week left before dark, by my own ledger.",
	&"ledger_torn": "A page is gone from my ledger. The guesthouse has one more empty bed than I wrote.",
	&"oven_badge": "A pilgrim's badge, melted in the oven ash. The name on it was torn from my ledger.",
	&"crypt_book": "A page from a book, by the crypt altar: ten candles drawn in a ring, and a soul for each.",
	&"crypt_candles": "Candles burning in the crypt, in a ring. More of them each night.",
	&"keys_moved": "My keys were moved in the night. There's wax in the teeth: someone took a mould of them.",
	&"incense_bag": "Walter's bag smells of the incense they burn at Matins.",
	&"edwin_missing": "Edwin was not at Matins.",
	&"edwin_comb": "Edwin's wounds are in rows, too even for claws. Like a wool-carding comb.",
	&"edwin_moved": "I went for help and Edwin was gone from the charnel house when I came back.",
	&"guest_moved": "The guest's body was gone from the guesthouse when I came back with help.",
	&"osric_mask": "The demon's mask came off in the fog. It was Brother Osric.",
	&"two_demons": "I saw it in two places at once. There is more than one of them.",
	&"prior_sleeve": "Blood on the prior's sleeve. He was kneeling by the body when I came.",
	&"simon_blood": "Brother Simon on his knees on the cloister flags, scrubbing blood. He hid the rag.",
	&"thomas_sent_simon": "Simon says Thomas sent him to scrub the blood.",
	&"hoof_print": "A hoof print in the mud. Carved wood, with the marks of the straps that tie it to a boot.",
	&"ergot_rye": "The rye in the granary is black-spurred. That is what is in our bread.",
	&"well_badge": "A body down the well, with a pilgrim's badge. The name on it was torn from my ledger.",
	&"race_badge": "A body in the mill race culvert, with a pilgrim's badge. The name was torn from my ledger.",
	&"garden_badge": "A body under the kitchen beds, freshly dug, with a pilgrim's badge. Another torn name.",
	&"loft_badge": "A body in the bell tower loft, with a pilgrim's badge. Another torn name.",
	&"chapter_badge": "A body under the chapter house flags, where Simon was scrubbing. Another torn name.",
}


static func text(id: StringName) -> String:
	return String(ALL.get(id, ""))


static func is_clue(id: StringName) -> bool:
	return ALL.has(id)


## How many clues the porter has written.
static func written() -> int:
	return GameState.notes.filter(func(n: Dictionary) -> bool: return is_clue(n.get("id", &""))).size()
