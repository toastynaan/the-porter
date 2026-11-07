class_name CaptureFlow
extends Node
## Being caught (design doc, "Getting caught"). The first capture is not
## death: you wake in the infirmary (the level's "wake_point" marker) with a
## fresh dose in you (+40), and the hunters go back to their rounds. The
## second, on any night, kills you and restarts the night from the last bell
## (GameState.load_last_bell), at the level's "bell_spawn" marker named after
## that bell. Captures only go up, so after a restart the next one kills too.
##
## The first capture also takes your keys (design doc: "something taken or
## changed: your keys, a page of the ledger, or your friend's trust"; keys
## chosen for night 3, whose dawn has them moved).
##
## A level loaded with no bell rung yet rings "start", so there is always a
## bell to go back to. Hunters find this node through the "capture_flow" group.

signal woke
signal died

const WAKE_DOSE := 40.0
const WAKE_DOSE_TIME := 6.0
const FADE_OUT := 0.6
const BLACK_WAKE := 2.5
const BLACK_DEATH := 3.0
const FADE_IN := 2.5
const CAPTURE_SOUND := preload("res://art/sfx/sfx_capture.wav")

@export var fade: ScreenFade
## Has reload_level() and the level_loaded signal (main.gd).
@export var main: Node

var busy := false

var _sting: AudioStreamPlayer


func _ready() -> void:
	add_to_group(&"capture_flow")
	main.level_loaded.connect(_on_level_loaded)
	_sting = AudioStreamPlayer.new()
	_sting.stream = CAPTURE_SOUND
	add_child(_sting)


func on_captured(hunter: Node3D, player: Player) -> void:
	if busy or player == null:
		return
	busy = true
	player.controls_locked = true
	var to := hunter.global_position - player.global_position
	var turn := player.create_tween().set_parallel()
	turn.tween_property(player, ^"rotation:y", player.rotation.y + wrapf(atan2(-to.x, -to.z) - player.rotation.y, -PI, PI), 0.25)
	turn.tween_property(player.head, ^"rotation:x", deg_to_rad(12.0), 0.25)
	if AudioOut.enabled():
		_sting.play()
	await fade.fade_to(1.0, FADE_OUT)
	GameState.captures += 1
	if GameState.captures >= 2:
		await _die()
	else:
		await _wake(player)
	busy = false


func _wake(player: Player) -> void:
	get_tree().call_group(&"hunters", &"reset")
	get_tree().call_group(&"stalkers", &"reset")
	var bed := get_tree().get_first_node_in_group(&"wake_point") as Node3D
	if bed:
		player.place(bed.global_position, bed.global_rotation.y)
	player.lie_down()
	GameState.add_dose(WAKE_DOSE, WAKE_DOSE_TIME)
	GameState.set_flag(&"woke_in_infirmary")
	GameState.keys.clear()
	GameState.set_flag(&"keys_taken")
	await get_tree().create_timer(BLACK_WAKE).timeout
	fade.fade_to(0.0, FADE_IN)
	await player.get_up(FADE_IN)
	player.controls_locked = false
	woke.emit()


func _die() -> void:
	died.emit()
	await get_tree().create_timer(BLACK_DEATH).timeout
	GameState.load_last_bell()
	main.reload_level()
	await fade.fade_to(0.0, FADE_IN)


func _on_level_loaded(_level: Node) -> void:
	if GameState.last_bell.is_empty():
		GameState.ring_bell(&"start")
		return
	var player := get_tree().get_first_node_in_group(&"player") as Player
	for spawn: Node3D in get_tree().get_nodes_in_group(&"bell_spawn"):
		if spawn.name == GameState.last_bell and player:
			player.place(spawn.global_position, spawn.global_rotation.y)
