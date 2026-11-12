extends Node
## Captures the player's view at fixed spots in the abbey through the full
## render pipeline, to art/_review/abbey/view_<name>.png (tools/shots/abbey_shots.sh).

const OUT := "res://art/_review/abbey/"
## name: [feet position, yaw (0 = facing north), pitch, dose]
const VIEWS := {
	"outer_court": [Vector3(-33, 0.05, 2), -60.0, 4.0, 0.0],
	"cloister_walk": [Vector3(-10, 0.05, -26.5), 180.0, 0.0, 0.0],
	"cloister_walk_dose75": [Vector3(-10, 0.05, -26.5), 180.0, 0.0, 75.0],
	"nave": [Vector3(-16, 0.05, -32), -90.0, 4.0, 0.0],
	"choir_night_stairs": [Vector3(13, 0.05, -31), -110.0, 12.0, 0.0],
	"dormitory": [Vector3(16, 4.02, -26.5), 180.0, -4.0, 0.0],
	"graveyard": [Vector3(30, 0.0, -6), 10.0, 6.0, 0.0],
	"mill_race": [Vector3(20, -1.2, 18), -90.0, 0.0, 0.0],
	"bakehouse_oven": [Vector3(-14.6, 0.05, 8.3), 90.0, -14.0, 0.0],
	"granary_hidden_door": [Vector3(-16.4, 0.05, -17.0), 60.0, -4.0, 0.0],
	"crypt": [Vector3(15, -4.0, -31.5), -90.0, 2.0, 0.0],
	"orchard": [Vector3(-8, 0.0, 21.5), 150.0, 6.0, 0.0],
	"graveyard_yew": [Vector3(31, 0.0, -9.5), -20.0, 10.0, 0.0],
}
const SETTLE_TIME := 1.5


func _ready() -> void:
	var main: Node = load("res://game/core/render/main.tscn").instantiate()
	main.set(&"level", load("res://game/chapters/night3/night3.tscn"))
	add_child(main)
	await get_tree().process_frame
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var player: Player = get_tree().get_first_node_in_group(&"player")
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	for view_name: String in VIEWS:
		var v: Array = VIEWS[view_name]
		GameState.snap_dose(v[3])
		player.global_position = v[0]
		player.velocity = Vector3.ZERO
		player.rotation = Vector3(0, deg_to_rad(v[1]), 0)
		player.head.rotation = Vector3(deg_to_rad(v[2]), 0, 0)
		await get_tree().create_timer(SETTLE_TIME).timeout
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		var s := floori(img.get_height() / 540.0)
		if s > 1:
			img.resize(roundi(img.get_width() / float(s)), roundi(img.get_height() / float(s)), Image.INTERPOLATE_NEAREST)
		var path := OUT + "view_%s.png" % view_name
		img.save_png(ProjectSettings.globalize_path(path))
		print("wrote ", path)
	get_tree().quit()
