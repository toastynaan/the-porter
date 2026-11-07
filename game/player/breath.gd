class_name Breath
extends Node
## Holding the breath while `hold_breath` is held (Look and Feel, "Sound
## feel": holding your breath cuts your body's sounds). A breath meter drains
## while holding: 12 s, or 8 s hungry (M2 report defaults). Run it dry and he
## gasps, which a hunter hears at Earshot.GASP, and can't hold again for a
## moment. Breathing itself carries Earshot.BREATH: a hunter right beside a
## hiding spot hears it.

signal changed(holding: bool)
signal gasped

const CAPACITY := 12.0
const HUNGRY_CAPACITY := 8.0
## Seconds from empty to full while breathing.
const REFILL_TIME := 6.0
## Seconds after a gasp before he can hold his breath again.
const RECOVER_TIME := 2.0
## Seconds between breaths a listener could hear.
const BREATH_PERIOD := 1.0

var holding := false
## 0..1 of the capacity.
var meter := 1.0

var _recover := 0.0
var _breath_t := 0.0

@onready var _player: Player = owner


func capacity() -> float:
	return HUNGRY_CAPACITY if GameState.is_hungry() else CAPACITY


func _process(delta: float) -> void:
	_recover = maxf(_recover - delta, 0.0)
	var want := Input.is_action_pressed(&"hold_breath") and not (_player.crawling or _player.controls_locked)
	var hold := want and _recover == 0.0 and meter > 0.0
	if hold:
		meter = maxf(meter - delta / capacity(), 0.0)
		if meter == 0.0:
			hold = false
			_recover = RECOVER_TIME
			gasped.emit()
			Earshot.make(_player, _player.camera.global_position, Earshot.GASP, _player)
	else:
		meter = minf(meter + delta / REFILL_TIME, 1.0)
	if hold != holding:
		holding = hold
		changed.emit(holding)
	if not holding:
		_breath_t += delta
		if _breath_t >= BREATH_PERIOD:
			_breath_t = 0.0
			Earshot.make(_player, _player.camera.global_position, Earshot.BREATH, _player)
