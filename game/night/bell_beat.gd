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
	GameState.ring_bell(&"matins")
	tower.ring(3)
	await say("", "(Matins. The brothers gather in the choir.)")
