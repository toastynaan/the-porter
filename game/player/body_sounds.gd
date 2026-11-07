extends Node
## The porter's body is loud (Look and Feel, "Sound feel"): breathing that
## turns to panting as his stamina runs down, loud breathing and a heartbeat
## while hiding, a gasp when a held breath runs out. Holding his breath cuts
## everything but the heart. Placeholder sounds, art/sfx/.

const BREATH := preload("res://art/sfx/sfx_breath_loop.wav")
const PANT := preload("res://art/sfx/sfx_pant_loop.wav")
const HEART := preload("res://art/sfx/sfx_heartbeat_loop.wav")
const GASP := preload("res://art/sfx/sfx_gasp.wav")
const SILENT_DB := -60.0

var _breath: AudioStreamPlayer
var _pant: AudioStreamPlayer
var _heart: AudioStreamPlayer
var _gasp: AudioStreamPlayer

@onready var _player: Player = owner


func _ready() -> void:
	_breath = _make(AudioOut.looped(BREATH))
	_pant = _make(AudioOut.looped(PANT))
	_heart = _make(AudioOut.looped(HEART))
	_gasp = _make(GASP)
	_gasp.volume_db = -4.0
	# The player's own @onready references aren't set yet.
	(_player.get_node(^"Breath") as Breath).gasped.connect(func() -> void:
		if AudioOut.enabled():
			_gasp.play())
	if AudioOut.enabled():
		for p in [_breath, _pant, _heart]:
			p.play()


func _make(stream: AudioStream) -> AudioStreamPlayer:
	var p := AudioStreamPlayer.new()
	p.stream = stream
	p.volume_db = SILENT_DB
	add_child(p)
	return p


func _process(delta: float) -> void:
	if not AudioOut.enabled():
		return
	var hidden := _player.hiding != null
	var holding := _player.breath.holding
	var tired := 1.0 - _player.stamina.value
	var breath_db := -12.0 if hidden else -30.0
	var pant_db := linear_to_db(maxf(pow(tired, 1.5) * 0.5, 0.0001))
	_fade(_breath, SILENT_DB if holding else breath_db, delta)
	_fade(_pant, SILENT_DB if holding else pant_db, delta)
	_fade(_heart, -12.0 if hidden else SILENT_DB, delta)


func _fade(p: AudioStreamPlayer, db: float, delta: float) -> void:
	p.volume_db = move_toward(p.volume_db, db, delta * 60.0)
