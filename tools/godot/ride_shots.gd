extends Node
## Stills of the reworked ride in (night 0) through the full render pipeline,
## to art/_review/ride/ (tools/ride_shots.sh), at the ride's own pace: talking
## to the traveller in the fields, the carter pulled in and the body cart going
## by, the warden at Aldgate walking up and his lantern in the porter's face, the woman in the doorway, the lane, and the
## wagon driving off down it.

const OUT := "res://art/_review/ride/"

var _n := 0
var _main: Node
var _pilot: NightPilot


func _ready() -> void:
	NightPilot.fresh_night("user://ride_shots_save.tres")
	GameState.night = 0
	GameState.chapter = 0
	Talk.line_seconds = 2.5
	Talk.auto_choice = func(_o: PackedStringArray) -> int: return -1
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	_main = NightPilot.main_with("res://game/nights/night0.tscn")
	add_child(_main)
	await get_tree().create_timer(0.5).timeout
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	_pilot = NightPilot.new(_main.get(&"current_level"), func(_ok: bool, _w: String) -> void: pass)
	var night := _pilot.night
	var p := _pilot.player
	(night.get_node(^"Hallucinations") as Hallucinations).active = false
	var ride := night.get_node(^"Director/Ride")
	var traveller := ride.get(&"traveller") as Node3D
	var wagon := night.get_node(^"Wagon") as Node3D

	# Talking to the traveller in the fields.
	await _until(func() -> bool: return p.riding != null, 5.0)
	await get_tree().create_timer(1.0).timeout
	(traveller.get_node(^"Talker") as Talker).interact(p)
	await _until(func() -> bool: return Talk.is_choosing(), 15.0)
	await _shot("talking_to_the_traveller", 0.6)

	# Pulled in; the body cart goes by and the talk breaks off.
	var cart := night.get_node(^"BodyCart") as Node3D
	await _until(func() -> bool: return GameState.has_flag(&"talked_n0_traveller"), 40.0)
	Talk.auto_choice = func(_o: PackedStringArray) -> int: return 0
	await _until(func() -> bool: return cart.global_position.distance_to(p.global_position) < 3.5, 15.0)
	_look_at(p, cart.global_position + Vector3.UP * 0.9)
	await _shot("the_body_cart_goes_by", 0.05)

	# The warden at Aldgate walks up, and holds his lantern to his face.
	var warden := night.get_node(^"RoadFolk/Warden") as Node3D
	await _until(func() -> bool: return Talk.history.has(["Warden", "Let's have a look at you, then."]), 90.0)
	_look_at(p, warden.global_position + Vector3.UP * 1.5)
	await _shot("the_warden_walks_up", 0.9)
	await _until(func() -> bool: return Talk.history.has(["", "(He holds his lantern up to your face, and looks at you a long moment.)"]), 20.0)
	await _shot("the_lantern_in_his_face", 0.3)

	# The woman in the doorway.
	var woman := night.get_node(^"RoadFolk/Townswoman") as Node3D
	await _until(func() -> bool: return wagon.global_position.x > -95.0, 40.0)
	_look_at(p, woman.global_position + Vector3.UP * 1.4)
	await _shot("a_woman_in_a_doorway", 0.3)

	# The lane.
	await _until(func() -> bool: return wagon.global_position.x > -46.0 and wagon.global_position.z < 30.0, 40.0)
	_look_at(p, Vector3(-44.0, 1.5, 0.0))
	await _shot("into_the_lane", 0.3)

	# Set down; the wagon drives off.
	await _until(func() -> bool: return GameState.has_flag(&"talked_n0_carter") and not Talk.talking, 60.0)
	await get_tree().create_timer(4.0).timeout
	if is_instance_valid(wagon):
		_look_at(p, wagon.global_position + Vector3.UP * 1.0)
	await _shot("the_wagon_drives_off", 0.1)
	print("ride shots done")
	get_tree().quit()


func _look_at(p: Player, at: Vector3) -> void:
	var to := at - p.camera.global_position
	p.rotation.y = atan2(-to.x, -to.z)
	p.head.rotation.x = atan2(to.y, Vector2(to.x, to.z).length())


func _until(cond: Callable, limit: float) -> void:
	var t := 0.0
	while not cond.call() and t < limit:
		await get_tree().process_frame
		t += get_process_delta_time()


func _shot(shot_name: String, settle := 0.5) -> void:
	await get_tree().create_timer(settle).timeout
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	var s := floori(img.get_height() / 540.0)
	if s > 1:
		img.resize(roundi(img.get_width() / float(s)), roundi(img.get_height() / float(s)), Image.INTERPOLATE_NEAREST)
	_n += 1
	var path := OUT + "%02d_%s.png" % [_n, shot_name]
	img.save_png(ProjectSettings.globalize_path(path))
	print("wrote ", path)
