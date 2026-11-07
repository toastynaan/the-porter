extends NightBeat
## Supper (design doc, "Core loop": bread and ale served by Osric; eat, or
## palm the bread and risk being seen. Night 3: "the bread tastes bitter.
## Thomas offers a remedy for your headaches."). The porter sits: he can look
## but not walk until supper ends.
##
## Eating: Dose +10, slow and lasting. Palming: hungry tonight, and Suspicion
## +5 if Osric is still watching your plate. The remedy: Dose +15; refusing
## it, Suspicion +5. (Doc values; +5 is the low end of the doc's range.)

const BREAD_DOSE := 10.0
const BREAD_TIME := 90.0
const REMEDY_DOSE := 15.0
const REMEDY_TIME := 30.0
const SEEN_SUSPICION := 5
const REFUSE_SUSPICION := 5

@export var seat: Marker3D
@export var bread: Duty
@export var osric: Brother
@export var thomas: Brother
## Seconds Osric watches your plate after serving before he turns away.
@export var watch_time := 5.0

var _osric_watching := false


func run() -> void:
	var p := player()
	p.place(seat.global_position, seat.global_rotation.y)
	p.use_input_override = true
	p.input_override = Vector2.ZERO
	bread.visible = true
	await say("", "(Supper in the refectory with the brothers.)")
	osric.face(p.global_position)
	await say("Osric", "(Serves you bread and ale.)")
	_osric_watching = true
	get_tree().create_timer(watch_time, false).timeout.connect(_osric_turns)
	await bread.wait_for_use()
	var pick := await Talk.choose(PackedStringArray(["Eat the bread", "Palm the bread"]))
	bread.visible = false
	if pick == 0:
		GameState.set_flag(&"n3_ate_bread")
		GameState.add_dose(BREAD_DOSE, BREAD_TIME)
		await say("", "(The bread tastes bitter.)")
	else:
		GameState.set_flag(&"n3_palmed_bread")
		GameState.set_flag(&"hungry")
		if _osric_watching:
			GameState.raise_suspicion(SEEN_SUSPICION)
			GameState.set_flag(&"n3_osric_saw")
			await say("Osric", "(Notices your empty plate.)")
	thomas.face(p.global_position)
	await say("Thomas", "(Offers a remedy for your headaches.)")
	pick = await Talk.choose(PackedStringArray(["Take the remedy", "Refuse it"]))
	if pick == 0:
		GameState.set_flag(&"n3_took_remedy")
		GameState.add_dose(REMEDY_DOSE, REMEDY_TIME)
	else:
		GameState.set_flag(&"n3_refused_remedy")
		GameState.raise_suspicion(REFUSE_SUSPICION)
	await say("", "(Supper ends. At sunset the gate must be barred.)")
	p.use_input_override = false


func _osric_turns() -> void:
	_osric_watching = false
	osric.rotation.y += PI
