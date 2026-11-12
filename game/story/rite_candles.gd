class_name RiteCandles
extends Node3D
## The crypt keeps count (docs/log/full-game-run.md, "The rite"; docs/systems/mechanics.md,
## "Reading the hidden numbers"): the cult lights a candle here for each
## soul the rite has been fed, so the porter can go down and count them.
## Lights the first GameState.count of its Candle children, in order.
## The first time he looks at the ring lit, from close enough to count it,
## he writes the crypt_candles note (proof for a confrontation, and for the
## prior on night 5).

## Metres from a lit candle, and degrees from the middle of his view, from
## which he has seen the ring. *(mine)*
const SEE_RANGE := 6.0
const SEE_ANGLE := 35.0
## Seconds between looks.
const LOOK_EVERY := 0.4

var _since := 0.0


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


func _physics_process(delta: float) -> void:
	_since += delta
	if _since < LOOK_EVERY or GameState.has_note(&"crypt_candles"):
		return
	_since = 0.0
	var p := get_tree().get_first_node_in_group(&"player") as Player
	if p and seen_by(p):
		GameState.note(&"crypt_candles")


## He is looking at a lit candle of the ring, near enough, with nothing between.
func seen_by(p: Player) -> bool:
	var eye := p.camera.global_position
	for c in get_children():
		if c is Candle and (c as Candle).lit:
			# The flame, not the base: the base stands on stone.
			var at := (c as Candle).global_position + Vector3.UP * 0.2
			if eye.distance_to(at) <= SEE_RANGE and ViewCheck.off_centre(p.camera, at) <= SEE_ANGLE \
					and ViewCheck.clear(self, eye, at):
				return true
	return false
