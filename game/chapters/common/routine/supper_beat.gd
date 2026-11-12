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
## What he does with the bread once he has been warned: in brackets (italics).
const BREAD_CHOICES := ["(Eat the bread.)", "(Palm the bread.)"]

@export var seat: Marker3D
## His place at the table: he sits when he uses it.
@export var seat_duty: Duty
@export var bread: Duty
@export var osric: Brother
@export var thomas: Brother
## Who offers the remedy (none: no remedy tonight).
@export var ranulf: Brother
## Who watches him at supper from Suspicion 30 (docs/systems/mechanics.md, "Reading
## the hidden numbers": someone is always watching you at supper).
@export var watcher: Brother

const WATCHED_FROM := 30
## Seconds Osric watches your plate after serving before he turns away.
@export var watch_time := 5.0
@export var warned_flag := &"bread_warned"

@export_group("Lines")
## Said once he's seated ("Name: words", or a line in brackets).
@export var seated_lines := PackedStringArray(["(Supper in the refectory with the brothers.)"])
## Osric serving.
@export var serve_lines := PackedStringArray(["Osric: Bread and ale, brother."])
@export var eat_lines := PackedStringArray(["(The bread tastes bitter.)"])
@export var palm_seen_lines := PackedStringArray(["Osric: Not hungry, brother? There's no shame in a good appetite."])
## Who warns him about the bread after he has eaten (night 1: Bede), and
## what he says; it sets `warned_flag` and writes the clue.
@export var warner: Brother
@export var warn_lines := PackedStringArray()
## A word in his ear from someone at the table (Thomas), unless he has
## already heard it (`aside_unless`, a flag).
@export var aside_by: Brother
@export var aside_lines := PackedStringArray()
@export var aside_unless := &""
## Ranulf's offer and Thomas's warning, when there's a remedy tonight.
@export var remedy_lines := PackedStringArray([
	"Ranulf: You keep rubbing your eyes, brother. The new ones always get the headaches. A little of this in your ale, and you'll sleep.",
	"Thomas: (Quietly, so only you hear.) Not his physic. Not that one. Trust me."])
@export var end_lines := PackedStringArray(["(Supper ends. Go and take the gate from Cole.)"])
@export_group("")

var _osric_watching := false


func _ready() -> void:
	bread.visible = false


func run() -> void:
	var p := player()
	await say("", "(Supper. Take your place in the refectory.)")
	await seat_duty.wait_for_use()
	arrived()
	p.place(seat.global_position, seat.global_rotation.y)
	if watcher and GameState.suspicion >= WATCHED_FROM:
		watcher.face(p.global_position)
		GameState.set_flag(GameState.tonight("watched_at_supper"), StringName(watcher.name))
	p.use_input_override = true
	p.input_override = Vector2.ZERO
	bread.visible = true
	await say_lines(seated_lines)
	osric.face(p.global_position)
	await say_lines(serve_lines)
	_osric_watching = true
	get_tree().create_timer(watch_time, false).timeout.connect(_osric_turns)
	await bread.wait_for_use()
	var pick := 0
	if GameState.has_flag(warned_flag):
		pick = await Talk.choose(PackedStringArray(BREAD_CHOICES))
	bread.visible = false
	if pick == 0:
		GameState.set_flag(GameState.tonight("ate_bread"))
		GameState.add_dose(BREAD_DOSE, BREAD_TIME)
		await say_lines(eat_lines)
	else:
		GameState.set_flag(GameState.tonight("palmed_bread"))
		GameState.set_flag(&"hungry")
		if _osric_watching:
			GameState.raise_suspicion(SEEN_SUSPICION)
			GameState.set_flag(GameState.tonight("osric_saw"))
			await say_lines(palm_seen_lines)
	if warner and not warn_lines.is_empty():
		warner.face(p.global_position)
		await say_lines(warn_lines)
		GameState.set_flag(warned_flag)
		GameState.note(&"bread_warning")
	if aside_by and not aside_lines.is_empty() and (aside_unless == &"" or not GameState.has_flag(aside_unless)):
		aside_by.face(p.global_position)
		await say_lines(aside_lines)
		GameState.set_flag(GameState.tonight("supper_aside"))
	if ranulf:
		await _remedy(p)
	await say_lines(end_lines)
	p.use_input_override = false


## Ranulf offers his remedy; Thomas, beside him, warns him off it.
func _remedy(p: Player) -> void:
	ranulf.face(p.global_position)
	thomas.face(p.global_position)
	await say_lines(remedy_lines)
	var pick := await Talk.choose(PackedStringArray(["(Take Brother Ranulf's remedy.)", "(Refuse it.)"]))
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
