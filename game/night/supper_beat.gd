extends NightBeat
## Supper (design doc, "Core loop" 1: bread and ale served by Osric. You
## eat the bread until you have found a clue that something is wrong with
## it; from then on you can palm it instead, and risk being seen. Night 3:
## "the bread tastes bitter. Thomas offers a remedy for your headaches.").
## At the supper bell the porter goes to his place in the refectory; seated,
## he can look but not walk until supper ends. Palming needs `warned_flag`
## (the choir brother's warning on night 1).
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
## His place at the table: he sits when he uses it.
@export var seat_duty: Duty
@export var bread: Duty
@export var osric: Brother
@export var thomas: Brother
## Who offers the remedy (none: no remedy tonight).
@export var ranulf: Brother
## Seconds Osric watches your plate after serving before he turns away.
@export var watch_time := 5.0
@export var warned_flag := &"bread_warned"

var _osric_watching := false


func _ready() -> void:
	bread.visible = false


func run() -> void:
	var p := player()
	await say("", "(Supper. Take your place in the refectory.)")
	await seat_duty.wait_for_use()
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
	var pick := 0
	if GameState.has_flag(warned_flag):
		pick = await Talk.choose(PackedStringArray(["Eat the bread", "Palm the bread"]))
	bread.visible = false
	if pick == 0:
		GameState.set_flag(GameState.tonight("ate_bread"))
		GameState.add_dose(BREAD_DOSE, BREAD_TIME)
		await say("", "(The bread tastes bitter.)")
	else:
		GameState.set_flag(GameState.tonight("palmed_bread"))
		GameState.set_flag(&"hungry")
		if _osric_watching:
			GameState.raise_suspicion(SEEN_SUSPICION)
			GameState.set_flag(GameState.tonight("osric_saw"))
			await say("Osric", "Not hungry, brother? There's no shame in a good appetite.")
	if ranulf:
		await _remedy(p)
	await say("", "(Supper ends. Go and take the gate from Cole.)")
	p.use_input_override = false


## Ranulf offers his remedy; Thomas, beside him, warns him off it.
func _remedy(p: Player) -> void:
	ranulf.face(p.global_position)
	await say("Ranulf", "You keep rubbing your eyes, brother. The new ones always get the headaches. A little of this in your ale, and you'll sleep.")
	thomas.face(p.global_position)
	await say("Thomas", "(Quietly, so only you hear.) Not his physic. Not that one. Trust me.")
	var pick := await Talk.choose(PackedStringArray(["Take Brother Ranulf's remedy", "Refuse it"]))
	if pick == 0:
		GameState.set_flag(GameState.tonight("took_remedy"))
		GameState.add_dose(REMEDY_DOSE, REMEDY_TIME)
		await say("", "(It tastes of honey, and under the honey, something green.)")
	else:
		GameState.set_flag(GameState.tonight("refused_remedy"))
		GameState.raise_suspicion(REFUSE_SUSPICION)
		GameState.change_trust(&"thomas", 5)
		await say("Ranulf", "As you like.")
		await say("Thomas", "(Softly.) Good.")


func _osric_turns() -> void:
	_osric_watching = false
	osric.rotation.y += PI
