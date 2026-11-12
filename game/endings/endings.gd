class_name Endings
## The seven endings and their chronicle entries (docs/log/full-game-run.md,
## "Endings"), in the order they are checked when night 6 ends. Each entry is
## the official version, written decades later; it never matches what the
## porter saw. DRAFT: every chronicle here waits on the user's rewrite.

## id -> [title, chronicle, last line]
const ALL := {
	&"new_faith": ["The New Faith",
		"In the year 1424 the abbey within Aldgate was troubled by a sickness of the mind among its brothers, which the infirmarian Thomas, a man of great learning, cured with prayer and simples. The new porter, Alric, was cured of the same sickness, and kept the gate faithfully until his death in the year 1466. In his time no pilgrim was turned from the door, and the house prospered. The crypt was walled up under the abbot Thomas, the stair being unsafe.",
		"You keep the gate for it, for forty years."],
	&"demon": ["The Demon",
		"In November of 1424 Hugh, prior of the abbey within Aldgate, was slain in the night by the porter Alric, a young man lately come from the country, who was found with the prior's blood on his hands. At his trial he spoke of a devil with a crown of horns, and of a great many dead, and he was hanged at Tyburn. After his death the house was quiet. The brothers kept a candle burning in the crypt, against the devil he had named.",
		"It was fed, and slept."],
	&"rising": ["The Rising",
		"On the morning of the seventeenth of November, 1424, the abbey within Aldgate was found empty at Lauds, its gate standing open to the lane and its brothers dead or fled. The coroner found that they had been set upon by thieves. In the years after, the ward recorded women killed in the lanes about the old abbey ground, which the watch put down to footpads. The killings moved east as the city grew, a few in each generation, and were never laid to any man.",
		"Whitechapel, 1888."],
	&"fire": ["The Fire",
		"On the sixteenth day of November, 1424, lightning struck the granary of the abbey within Aldgate in a winter storm, and the fire took the church and the crypt beneath it. Several brothers died, among them Thomas the infirmarian, who went back into the smoke for the sick. The porter, who raised the alarm, was commended by the bishop. The relic of the saint was lost in the fire; the brothers who were left said it had been taken up into heaven.",
		"You're never sure who was inside."],
	&"gate": ["The Gate",
		"In November of 1424, on information laid by Roger, bailiff of the ward, the sheriff's men entered the abbey within Aldgate and took five of its brothers, who were tried for the murder of pilgrims and hanged at Smithfield. The abbey's lands passed to the ward and were granted to the bailiff for his good service. The church was pulled down, its crypt filled with rubble, and houses were built over the ground.",
		"Its name was never written down again, until 1888."],
	&"witness": ["The Witness",
		"In November of 1424 the porter of the abbey within Aldgate, one Alric, left his gate in the night and fled the city with a woman of no good name, carrying off the keys. He was not found. The house took a new porter at Candlemas. In the spring the woman came before the sheriff with a tale of murders in the abbey; she was judged to be out of her wits, and put out of the city.",
		"The killings stopped, for a while."],
	&"broken_rite": ["The Broken Rite",
		"In November of 1424 a sickness passed through the abbey within Aldgate, of which several brothers died. The abbot Godric, an old man, did not recover from it. At Candlemas the bishop sent a new prior, who found the house poor and its accounts in disorder, and its crypt closed with a new stone, by whose order no one could say.",
		"Denied, not ended."],
}
## The order they are checked in when night 6 ends.
const ORDER: Array[StringName] = [&"new_faith", &"demon", &"rising", &"fire", &"gate", &"witness", &"broken_rite"]
const DEFAULT := &"broken_rite"


static func title(id: StringName) -> String:
	return String(ALL.get(id, ALL[DEFAULT])[0])


static func chronicle(id: StringName) -> String:
	return String(ALL.get(id, ALL[DEFAULT])[1])


static func last_line(id: StringName) -> String:
	return String(ALL.get(id, ALL[DEFAULT])[2])
