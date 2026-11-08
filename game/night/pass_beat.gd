extends NightBeat
## The night goes by (a night not built yet, M8's stubs): the screen goes
## dark, the candle burns down to Lauds, and grey light comes up.

@export var lines := PackedStringArray(["(The night goes by.)"])
@export var lauds := 30.0
@export var tower: BellTower


func run() -> void:
	var p := player()
	p.controls_locked = true
	await fade_to(1.0, 1.0)
	for line in lines:
		await say("", line)
	GameState.hour = maxf(GameState.hour, lauds)
	if tower:
		tower.ring(3)
	await fade_to(0.0, 1.5)
	p.controls_locked = false
