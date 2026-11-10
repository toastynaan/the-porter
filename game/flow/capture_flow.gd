class_name CaptureFlow
extends Node
## Being caught, and dying (docs/mechanics.md, "Being hunted"). One capture
## in the game is forgiving: the first, if it comes on night 1 or 2, wakes
## you in the infirmary (the level's "wake_point" marker) with a fresh dose
## in you (+40), the satchel emptied but for the keys, and the hunters back
## on their rounds. Every other capture kills you.
##
## Death is short and first-person: the hunter is on you, a blade or a cord,
## the view drops and goes dark. Then the night goes back to the latest save,
## quiet or bell (GameState.load_resume), with everything as it was then, at
## the level's "bell_spawn" marker named after it. Other deaths (fire, smoke,
## the Saint's touch) come through die() with their own cause.
##
## A level loaded with no bell rung yet rings "start", so there is always a
## save to go back to. Hunters find this node through the "capture_flow" group.

signal woke
signal died
## A death begins (`cause`: blade, cord, fire, smoke, saint).
signal dying(cause: StringName)

const WAKE_DOSE := 40.0
const WAKE_DOSE_TIME := 6.0
## The nights whose first capture wakes you instead.
const FORGIVING_NIGHTS: Array[int] = [1, 2]
const FADE_OUT := 0.6
const BLACK_WAKE := 2.5
const BLACK_DEATH := 2.0
const FADE_IN := 2.5
## Seconds for the view to drop to the floor.
const FALL_TIME := 0.7
const CAPTURE_SOUND := preload("res://art/sfx/sfx_capture.wav")
const DEATH_SOUNDS := {
	&"blade": preload("res://art/sfx/sfx_death_blade.wav"),
	&"cord": preload("res://art/sfx/sfx_death_cord.wav"),
}

@export var fade: ScreenFade
## Has reload_level() and the level_loaded signal (main.gd).
@export var main: Node

var busy := false
## How the last death came (blade, cord, fire, smoke, saint), for tests.
var last_cause := &""

var _sting: AudioStreamPlayer
var _blow: AudioStreamPlayer


func _ready() -> void:
	add_to_group(&"capture_flow")
	main.level_loaded.connect(_on_level_loaded)
	_sting = AudioStreamPlayer.new()
	_sting.stream = CAPTURE_SOUND
	add_child(_sting)
	_blow = AudioStreamPlayer.new()
	add_child(_blow)


## Whether a capture now would wake you instead of killing you.
static func forgiving() -> bool:
	return GameState.captures == 0 and FORGIVING_NIGHTS.has(GameState.night)


func on_captured(hunter: Node3D, player: Player) -> void:
	if busy or player == null:
		return
	# Whatever he was saying to someone stops here.
	Talk.interrupt()
	# Night 6, after Thomas's wine: he isn't killed. He wakes in a habit.
	if GameState.night == 6 and GameState.has_flag(&"drank_wine"):
		busy = true
		player.controls_locked = true
		_turn_to(player, hunter)
		await fade.fade_to(1.0, FADE_OUT)
		GameState.set_flag(&"ending", &"new_faith")
		busy = false
		get_tree().call_group(&"night_director", &"end_night")
		return
	if forgiving():
		busy = true
		player.controls_locked = true
		_turn_to(player, hunter)
		if AudioOut.enabled():
			_sting.play()
		await fade.fade_to(1.0, FADE_OUT)
		GameState.captures += 1
		await _wake(player)
		busy = false
		return
	GameState.captures += 1
	var weapon: Variant = hunter.get(&"weapon")
	await die(weapon if weapon is StringName else &"cord", hunter)


## Kills the porter: a blade or a cord from `killer`, or fire, smoke or the
## Saint. The view drops and goes dark, and the night goes back to the
## latest save.
func die(cause: StringName, killer: Node3D = null) -> void:
	var player := get_tree().get_first_node_in_group(&"player") as Player
	if busy or player == null:
		return
	dying.emit(cause)
	Talk.interrupt()
	busy = true
	last_cause = cause
	player.controls_locked = true
	died.emit()
	if killer:
		_turn_to(player, killer)
	if AudioOut.enabled():
		_sting.play()
		if DEATH_SOUNDS.has(cause):
			_blow.stream = DEATH_SOUNDS[cause]
			_blow.play()
	match cause:
		&"blade":
			# One quick cut: a dark flash and the head knocked back.
			fade.flash(Manuscript.RUBRIC, 0.5)
			await _tween_head(player, deg_to_rad(18.0), 0.0, 0.12)
		&"cord":
			# The cord from behind: the head pulled up and back, shaking.
			fade.fade_to(0.45, 0.8)
			await _tween_head(player, deg_to_rad(35.0), 0.12, 0.8)
		_:
			await get_tree().create_timer(0.3).timeout
	await player.fall_dead(FALL_TIME)
	await fade.fade_to(1.0, FADE_OUT)
	await get_tree().create_timer(BLACK_DEATH).timeout
	GameState.load_resume()
	main.reload_level()
	await fade.fade_to(0.0, FADE_IN)
	busy = false


func _turn_to(player: Player, at: Node3D) -> void:
	var to := at.global_position - player.global_position
	var turn := player.create_tween().set_parallel()
	turn.tween_property(player, ^"rotation:y", player.rotation.y + wrapf(atan2(-to.x, -to.z) - player.rotation.y, -PI, PI), 0.25)
	turn.tween_property(player.head, ^"rotation:x", deg_to_rad(12.0), 0.25)


func _tween_head(player: Player, pitch: float, shake: float, seconds: float) -> void:
	var t := player.create_tween()
	t.tween_property(player.head, ^"rotation:x", pitch, seconds * 0.4).set_trans(Tween.TRANS_SINE)
	if shake > 0.0:
		for i in 4:
			t.tween_property(player.head, ^"rotation:z", shake * (1.0 if i % 2 == 0 else -1.0), seconds * 0.15)
	await t.finished


func _wake(player: Player) -> void:
	get_tree().call_group(&"hunters", &"reset")
	get_tree().call_group(&"stalkers", &"reset")
	var bed := get_tree().get_first_node_in_group(&"wake_point") as Node3D
	if bed:
		player.place(bed.global_position, bed.global_rotation.y)
	player.lie_down()
	GameState.add_dose(WAKE_DOSE, WAKE_DOSE_TIME)
	GameState.set_flag(&"woke_in_infirmary")
	# The cult takes everything but the keys.
	GameState.satchel.clear()
	await get_tree().create_timer(BLACK_WAKE).timeout
	fade.fade_to(0.0, FADE_IN)
	await player.get_up(FADE_IN)
	player.controls_locked = false
	woke.emit()


func _on_level_loaded(_level: Node) -> void:
	if GameState.last_bell.is_empty():
		GameState.ring_bell(&"start")
		return
	var player := get_tree().get_first_node_in_group(&"player") as Player
	for spawn: Node3D in get_tree().get_nodes_in_group(&"bell_spawn"):
		if spawn.name == GameState.last_bell and player:
			player.place(spawn.global_position, spawn.global_rotation.y)
