extends Node
## Stills of the sky dial in the top right, at four hours of night 0 (in the
## lane, the clock running), to art/_review/menus/sky_dial_<hour>.png, and the
## corner alone, enlarged, as sky_dial_corners.png.
## Run: Godot --path . --windowed --resolution 1920x1080 res://tools/shots/sky_dial_shot.tscn

const HOURS := [16.5, 17.5, 21.0, 2.0]


func _ready() -> void:
	var main: Node = load("res://game/core/render/main.tscn").instantiate()
	add_child(main)
	await get_tree().create_timer(1.0).timeout
	var flow := main.get_node(^"Game") as GameFlow
	flow.title.close()
	await flow.start_at(0, &"Arrive")
	await get_tree().create_timer(4.0).timeout
	var dir := ProjectSettings.globalize_path("res://art/_review/menus/")
	DirAccess.make_dir_recursive_absolute(dir)
	var corners: Array[Image] = []
	for h: float in HOURS:
		GameState.hour = h
		await get_tree().create_timer(1.5).timeout
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		img.save_png(dir.path_join("sky_dial_%04.1f.png" % h))
		var w := img.get_width()
		var corner := img.get_region(Rect2i(w - (w >> 3), 0, w >> 3, w >> 4))
		corner.resize(corner.get_width() * 3, corner.get_height() * 3, Image.INTERPOLATE_NEAREST)
		corners.append(corner)
	var sheet := Image.create(corners[0].get_width(), corners[0].get_height() * corners.size(), false, corners[0].get_format())
	for i in corners.size():
		sheet.blit_rect(corners[i], Rect2i(Vector2i.ZERO, corners[i].get_size()), Vector2i(0, i * corners[0].get_height()))
	sheet.save_png(dir.path_join("sky_dial_corners.png"))
	print("wrote ", dir)
	get_tree().quit()
