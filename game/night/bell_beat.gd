extends NightBeat
## The Matins bell (design doc, "Core loop": at midnight ring the bell, go
## to the choir). The rope can be rung from a little before the Matins mark
## (`early`); rung more than `late` after it, the lateness is noticed (the
## candle clock: "a duty done very late is noticed"). The night saves here: a
## death sends you back to this bell.

@export var rope: Duty
@export var tower: BellTower
## Hours either side of `due`.
@export var early := 0.25
@export var late := 0.5
## Night 2: the rope is heavy, and a body drops past him, hanging from the
## bell's frame (a FoundBody, shown as he pulls).
@export var hanged: FoundBody
@export var heavy_lines := PackedStringArray()

const DROP := preload("res://art/sfx/sfx_body_drop.wav")
const DROP_HEIGHT := 3.5


func _ready() -> void:
	# Picked up from a save after it: he's still hanging there.
	if hanged and GameState.has_flag(hanged.found_flag()):
		hanged.show_body.call_deferred()


func run() -> void:
	await clock().wait_until(due - early)
	var rung := [false]
	rope.used.connect(func(_by: Node) -> void: rung[0] = true, CONNECT_ONE_SHOT)
	rope.enabled = true
	clock().wake()
	await say("", "(The candle has burned down to the Matins mark. Ring the bell in the tower.)")
	while not rung[0]:
		if GameState.hour > due + late and not GameState.has_flag(&"matins_late"):
			GameState.set_flag(&"matins_late")
			Talk.say("", "(The bell is late. It will have been noticed.)")
		await get_tree().physics_frame
	rope.enabled = false
	arrived()
	if hanged:
		await _heavy()
	GameState.ring_bell(&"matins")
	tower.ring(3)
	await say("", "(Matins. The brothers gather in the choir.)")


## The rope is heavy; something drops past him in the dark.
func _heavy() -> void:
	var rest := hanged.position
	hanged.position = rest + Vector3.UP * DROP_HEIGHT
	hanged.show_body()
	var drop := create_tween()
	drop.tween_property(hanged, ^"position", rest, 0.35).set_ease(Tween.EASE_IN).set_trans(Tween.TRANS_QUAD)
	if AudioOut.enabled():
		var a := AudioStreamPlayer3D.new()
		a.stream = DROP
		hanged.add_child(a)
		a.play()
	await drop.finished
	await say_lines(heavy_lines)
	hanged.find()
