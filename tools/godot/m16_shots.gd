extends Node
## Stills of M16: the chronicle page of each of the seven endings, in the
## order they're checked, to art/_review/m16/ (tools/m16_shots.sh).

const OUT := "res://art/_review/m16/"

var _n := 0


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	var main: Node = load("res://game/core/render/main.tscn").instantiate()
	add_child(main)
	await get_tree().create_timer(0.5).timeout
	var flow: GameFlow = main.get_node(^"Game")
	flow.title.visible = false
	for id in Endings.ORDER:
		flow.chronicle.seconds = 60.0
		flow.chronicle.show_ending(Endings.title(id), Endings.chronicle(id), Endings.last_line(id))
		await _shot(String(id), 0.8)
		flow.chronicle.visible = false
	print("m16 shots done")
	get_tree().quit()


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
