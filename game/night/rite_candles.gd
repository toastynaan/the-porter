class_name RiteCandles
extends Node3D
## The crypt keeps count (docs/full-game-run.md, "The rite"; docs/mechanics.md,
## "Reading the hidden numbers"): the cult lights a candle here for each
## soul the rite has been fed, so the porter can go down and count them.
## Lights the first GameState.count of its Candle children, in order.


func _ready() -> void:
	add_to_group(&"rite_candles")
	for c in get_children():
		c.add_to_group(&"rite_candle")
	GameState.fed.connect(func(_id: StringName) -> void: refresh())
	GameState.loaded.connect(refresh)
	refresh()


func refresh() -> void:
	var i := 0
	for c in get_children():
		if c is Candle:
			(c as Candle).lit = i < GameState.count
			i += 1


func lit_count() -> int:
	return get_children().filter(func(c: Node) -> bool: return c is Candle and (c as Candle).lit).size()
