class_name Rite
## The rite (docs/log/full-game-run.md, "The rite"): the cult's book says the
## Hungry Saint wakes when it has been fed ten souls in the six nights, the
## last given in the crypt at Matins on night 6. Six deaths always come;
## five can be stopped by the porter's choices. What the count has reached
## by night 6 decides how strong the Saint is.

enum Strength { SHADOW, WALKS, HUNTS }

## id -> [night, can the porter's choices stop it]
const DEATHS := {
	&"merchant": [1, true],
	&"bell_brother": [2, false],
	&"lane_death": [2, true],
	&"crypt_pilgrim": [3, false],
	&"edwin": [4, false],
	&"fog_brother": [4, false],
	&"night4_guest": [4, true],
	&"simon": [5, true],
	&"sergeant": [5, true],
	&"body5": [5, false],
	&"anselm": [6, false],
}
## 8 or fewer: a shadow that can't leave the crypt (the Rising can't happen);
## 9: it walks the abbey slowly; 10-11: it walks and hunts.
const WALKS_AT := 9
const HUNTS_AT := 10


static func always() -> Array[StringName]:
	var out: Array[StringName] = []
	for id: StringName in DEATHS:
		if not DEATHS[id][1]:
			out.append(id)
	return out


static func stoppable() -> Array[StringName]:
	var out: Array[StringName] = []
	for id: StringName in DEATHS:
		if DEATHS[id][1]:
			out.append(id)
	return out


static func strength(count: int) -> Strength:
	if count >= HUNTS_AT:
		return Strength.HUNTS
	if count >= WALKS_AT:
		return Strength.WALKS
	return Strength.SHADOW


## On night 6 the rite's last victim at Matins: Simon if he lived, otherwise
## a pilgrim from the guesthouse.
static func last_victim() -> StringName:
	return &"pilgrim" if GameState.has_flag(&"died_simon") else &"simon"
