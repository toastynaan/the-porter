class_name Report
## Whom the porter tells about a body (docs/log/full-game-run.md, "Reporting"):
## Thomas (safe now, dangerous later: he tells the cult, and each body told
## to him is Suspicion +5 at the next dusk), the prior (Suspicion +10 at
## once, because Ranulf overhears, and the prior suspects him), or no one
## (nothing, unless a brother saw him by the body: then the cult knows he
## found it and kept quiet, +15, the design doc's number for not reporting
## it the "right" way). reported_<id> holds whom, for what follows.

const PRIOR_SUSPICION := 10
const THOMAS_LATER := 5
const KEPT_QUIET_SUSPICION := 15
const TO: Array[StringName] = [&"thomas", &"prior", &"none"]


## How the porter names each body when he decides whom to tell.
const WHAT := {&"merchant": "the merchant in the fishpond", &"bell_brother": "Brother Bede in the bell tower",
	&"edwin": "Edwin in the charnel house", &"body5": "the body in the granary", &"anselm": "Anselm in his bed"}


static func name_of(id: StringName) -> String:
	return String(WHAT.get(id, "the body"))


static func choices(what: String) -> PackedStringArray:
	return PackedStringArray(["(Tell Brother Thomas about %s.)" % what, "(Tell the prior.)", "(Tell no one.)"])


## Asks him whom to tell about the body `id` ("the merchant in the pond");
## await it. Returns thomas, prior or none.
static func ask(id: StringName, what: String) -> StringName:
	var pick := await Talk.choose(choices(what))
	return apply(id, TO[clampi(pick, 0, 2)])


static func apply(id: StringName, to: StringName) -> StringName:
	GameState.set_flag(StringName("reported_" + String(id)), to)
	match to:
		&"thomas":
			GameState.set_flag(&"thomas_heard", int(GameState.get_flag(&"thomas_heard", 0)) + 1)
			GameState.set_flag(&"thomas_heard_new", int(GameState.get_flag(&"thomas_heard_new", 0)) + 1)
		&"prior":
			GameState.raise_suspicion(PRIOR_SUSPICION)
			GameState.set_flag(&"hugh_suspects", int(GameState.get_flag(&"hugh_suspects", 0)) + 1)
		_:
			if GameState.has_flag(SeenWatch.flag(StringName("near_" + String(id)))):
				GameState.raise_suspicion(KEPT_QUIET_SUSPICION)
	return to


## Bodies found and not yet reported.
static func unreported() -> Array[StringName]:
	var out: Array[StringName] = []
	for f: StringName in GameState.flags:
		var key := String(f)
		if key.begins_with("found_"):
			var id := StringName(key.trim_prefix("found_"))
			if not GameState.has_flag(StringName("reported_" + String(id))):
				out.append(id)
	return out


## Dusk: what Thomas heard since the last dusk has reached the cult.
static func at_dusk() -> void:
	var n := int(GameState.get_flag(&"thomas_heard_new", 0))
	if n > 0:
		GameState.raise_suspicion(THOMAS_LATER * n)
		GameState.flags.erase(&"thomas_heard_new")
