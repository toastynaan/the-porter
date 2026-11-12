extends Node
## One still of the Test a scene page (a chapter's beats), to art/_review/menus/.

func _ready() -> void:
	var main: Node = load("res://game/render/main.tscn").instantiate()
	add_child(main)
	await get_tree().create_timer(1.0).timeout
	var flow := main.get_node(^"Game") as GameFlow
	flow.title.close()
	flow.scene_select.open()
	flow.scene_select.call(&"_list_beats", 5)
	await get_tree().create_timer(0.8).timeout
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://art/_review/menus/"))
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://art/_review/menus/scene_select.png"))
	get_tree().quit()
