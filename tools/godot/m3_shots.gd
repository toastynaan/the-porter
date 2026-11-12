extends Node
## Review stills for M3 through the full render pipeline, to art/_review/m3/
## (tools/m3_shots.sh): the view from inside hiding spots, the demon in
## lantern light at Dose 0, 60 and 90, and staring at it.

const OUT := "res://art/_review/m3/"
const SPOTS: Array[String] = ["Oven", "UnderCot", "AltarCloth", "OpenTomb", "UnderBedW23", "BonePile"]
const SETTLE_TIME := 1.5

var _player: Player


func _ready() -> void:
	var main: Node = load("res://game/core/render/main.tscn").instantiate()
	main.level = load("res://game/dev/encounters/hunt_demo.tscn")
	add_child(main)
	await get_tree().process_frame
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	_player = get_tree().get_first_node_in_group(&"player")
	for h: Hunter in get_tree().get_nodes_in_group(&"hunters"):
		h.dormant = true
		h.visible = false
	var stalker: Stalker = get_tree().get_first_node_in_group(&"stalkers")
	stalker.active = false
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	GameState.snap_dose(0.0)

	for spot: HidingSpot in get_tree().get_nodes_in_group(&"hiding_spots"):
		if spot.name in SPOTS:
			_player.place(spot.exit.global_position, 0.0)
			_player.hide_in(spot)
			await _shot("hide_%s" % spot.name.to_snake_case())
			_player.leave_hiding(true)

	# The demon in the west cloister walk, 4 m off, in the lantern light.
	stalker.visible = true
	stalker.global_transform = Transform3D(Basis(Vector3.UP, PI), Vector3(-10, 0.05, -21))
	for dose in [0.0, 60.0, 90.0]:
		GameState.snap_dose(dose)
		_player.place(Vector3(-10, 0.05, -17), 0.0)
		_player.head.rotation.x = deg_to_rad(8.0)
		await _shot("demon_dose_%d" % dose)

	# Staring at it across the moonlit garth until the meter is full (after
	# the stumble the close-ups above may have caused).
	stalker.visible = false
	while _player.stumbling:
		await get_tree().process_frame
	await get_tree().create_timer(2.5).timeout
	stalker.visible = true
	GameState.snap_dose(60.0)
	stalker.global_transform = Transform3D(Basis(Vector3.UP, PI), Vector3(0, 0.0, -22))
	_player.place(Vector3(0, 0.0, -12), 0.0)
	await get_tree().create_timer(3.2).timeout
	await _shot("staring", 0.0)
	get_tree().quit()


func _shot(shot_name: String, settle := SETTLE_TIME) -> void:
	await get_tree().create_timer(settle).timeout
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	var s := floori(img.get_height() / 540.0)
	if s > 1:
		img.resize(roundi(img.get_width() / float(s)), roundi(img.get_height() / float(s)), Image.INTERPOLATE_NEAREST)
	var path := OUT + shot_name + ".png"
	img.save_png(ProjectSettings.globalize_path(path))
	print("wrote ", path)
