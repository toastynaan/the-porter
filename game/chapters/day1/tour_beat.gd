extends NightBeat
## The tour (design doc, "Day 1: The duties"; docs/mechanics.md, "The tour"):
## about five minutes. Thomas, leading the blind Anselm by the arm, walks
## ahead and stops at each of the porter's duties; at each, he explains it
## and the porter tries it: bar the gate, open the ledger, read the candle
## clock, take hold of the bell rope (no ringing by day), check a round stop,
## turn down a guest bed and take the guesthouse key. The glyph marks each
## one. By the well, the porter can ask about the sand: Thomas's first lie.
## When Thomas steps away, Anselm grips his sleeve. Skippable once the game
## has been finished.

## The pair, walking ahead.
@export var thomas: VisitorNPC
@export var anselm: VisitorNPC
## Their stops: Marker3Ds in order, where they stand at each duty.
@export var stops: Node3D
@export var bar_gate: Duty
@export var ledger: Duty
@export var candle_clock: CandleClock
@export var bell_rope: Duty
@export var round_stop: Duty
@export var guest_bed: Duty
@export var guest_key: Duty
@export var sand: Node3D
## The brothers the pair stand in for today (out of the world while they walk).
@export var hide_brothers: Array[Brother] = []

## Each stop's duty, and Thomas's lines there (DRAFT).
const LINES := [
	["Thomas", "The gate, first. By day Cole keeps it; from Compline to Lauds it's yours. The bar takes both hands. Try it."],
	["Thomas", "Your ledger, on the desk in your cell. Every soul who comes in at night goes in it: name, and what you see of them."],
	["Thomas", "The candle clock. It burns from dusk to Lauds, and the rings are your duties. Matins at the black ring: the bell's yours to ring."],
	["Thomas", "The bell. Take hold of the rope, there. Not by day, God forbid. At Matins you'll ring it and count us in the choir."],
	["Thomas", "After Matins, your round: these doors, the lamps, the sanctuary light. Try the latch. It should always be fast."],
	["Thomas", "The guesthouse. You'll turn down a bed for any guest you let in. And the key. Keep it on you."],
]

var tried: Array[int] = []


func _ready() -> void:
	for b in hide_brothers:
		b.place.call_deferred(null)


func run() -> void:
	if Settings.finished:
		var pick := await Talk.choose(PackedStringArray(["(Walk the duties with Thomas.)", "(Skip the tour: you've kept this gate before.)"]))
		if pick == 1:
			GameState.set_flag(&"d1_tour_skipped")
			return
	var p := player()
	await say("Thomas", "Brother Alric. I'm Thomas, the infirmarian. This is Brother Anselm, who kept the gate before you.")
	await say("Anselm", "Kept it till my eyes went. Thomas will show you. I'll listen.")
	var duties: Array = [bar_gate, ledger, candle_clock, bell_rope, round_stop, guest_bed]
	var markers := points(stops)
	for i in duties.size():
		await _walk_to(markers[i])
		if i == 0:
			await _by_the_well(p)
		await say(LINES[i][0], LINES[i][1])
		if duties[i] is Duty:
			await (duties[i] as Duty).wait_for_use()
		else:
			candle_clock.add_to_group(&"glyph_targets")
			await candle_clock.read
			candle_clock.remove_from_group(&"glyph_targets")
		tried.append(i)
	await guest_key.wait_for_use()
	if not GameState.keys.has(&"guesthouse"):
		GameState.keys.append(&"guesthouse")
	await say("", "(The guesthouse key, heavy and cold, on your ring with the gate's.)")
	await say("Anselm", "(He tells Thomas to go on; he'll find his own way.)")
	await say("Thomas", "I'll see you at supper, brother. Sleep first. The nights are long.")
	thomas.go_to(markers[-1] + Vector3(20.0, 0.0, 0.0))
	await wait(1.5)
	anselm.face(p.global_position)
	await say("Anselm", "(He grips your sleeve, and lowers his voice.) Don't let them in after the bell. Whatever they tell you. Don't let them in.")
	GameState.set_flag(&"d1_anselm_warned")
	await say("Anselm", "The old porter locked the guests in at night. Remember that.")
	GameState.set_flag(&"d1_tour_done")


## Thomas leads Anselm to the next stop; the porter follows.
func _walk_to(m: Vector3) -> void:
	anselm.follow(thomas)
	await thomas.walk_to(m)
	thomas.face(player().global_position)


## By the well: he may ask about the sand. Thomas's first lie.
func _by_the_well(p: Player) -> void:
	if sand == null or p.global_position.distance_to(sand.global_position) > 14.0:
		return
	var pick := await Talk.answer(PackedStringArray(["What's the sand for, by the well?", "(Say nothing.)"]))
	if pick == 0:
		await say("Thomas", "A beast slaughtered for the kitchen, early. They sanded it for the flies. It's nothing.")
		GameState.set_flag(&"d1_asked_sand")
		GameState.note(&"sand_by_the_well")
