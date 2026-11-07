extends Node
## Render pipeline checks: a 1920x1080 window renders the world at 960x540
## and shows it at 2x; Dose reaches the post shader through the DoseLook
## curves and tints the fog; the night Environment matches the spec.
## Run: tools/check.sh

var _fails := 0


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	GameState.snap_dose(0.0)
	var main: Node = load("res://game/render/main.tscn").instantiate()
	main.level = load("res://game/lookdev/lookdev.tscn")
	add_child(main)
	await get_tree().process_frame
	var world: SubViewport = main.get_node(^"World")
	var screen: TextureRect = main.get_node(^"Screen")
	main.layout_for(Vector2(1920, 1080))
	_check(world.size == Vector2i(960, 540) and main.pixel_scale == 2, "1080p: world 960x540 at 2x (%s)" % world.size)
	_check(screen.size == Vector2(1920, 1080) and screen.position == Vector2.ZERO, "1080p: screen fills the window")
	main.layout_for(Vector2(3456, 2234))
	_check(world.size == Vector2i(864, 540) and main.pixel_scale == 4, "16:10 Retina: world 864x540 at 4x (%s)" % world.size)
	_check(screen.position == Vector2(0, 37), "16:10 Retina: 37 px letterbox (%s)" % screen.position)
	main.layout_for(Vector2(1920, 1080))
	_check(screen.texture_filter == CanvasItem.TEXTURE_FILTER_NEAREST, "screen uses nearest filtering")

	var mat := screen.material as ShaderMaterial
	await get_tree().process_frame
	_check(_param(mat, &"palette_shift") == 0.0 and _param(mat, &"blur") == 0.0, "sober: no shift, no blur")
	_check(is_equal_approx(_param(mat, &"grain"), 0.04) and is_equal_approx(_param(mat, &"vignette"), 0.35),
		"sober grain 0.04, vignette 0.35")
	GameState.snap_dose(75.0)
	await get_tree().process_frame
	_check(absf(_param(mat, &"palette_shift") - 2.0 / 3.0) < 0.01, "dose 75: palette shift 0.67")
	_check(absf(_param(mat, &"edge_warp") - 0.0075) < 0.0005, "dose 75: edge warp 0.75%")
	_check(absf(_param(mat, &"blur") - 0.75) < 0.01, "dose 75: blur 0.75 px")
	_check(absf(_param(mat, &"grain") - 0.075) < 0.001 and absf(_param(mat, &"vignette") - 0.6) < 0.01,
		"dose 75: grain 0.075, vignette 0.6")

	var env := world.find_world_3d().environment
	_check(env != null, "level has an environment")
	if env:
		_check(env.volumetric_fog_albedo != Color("6e7f96"), "fog colour follows dose")
		_check(env.tonemap_mode == Environment.TONE_MAPPER_FILMIC, "filmic tonemap")
		_check(env.volumetric_fog_enabled and env.ssao_enabled and env.glow_enabled and not env.sdfgi_enabled,
			"volumetric fog, SSAO and glow on; SDFGI off")
		_check(env.ambient_light_source == Environment.AMBIENT_SOURCE_COLOR and env.ambient_light_energy < 0.1,
			"near-black colour ambient")
	GameState.snap_dose(0.0)

	# Keys reach the level inside the SubViewport (the lookdev controls).
	var cam: Camera3D = world.get_node(^"Lookdev/Camera")
	var before := cam.global_position
	_press(KEY_4)
	await get_tree().process_frame
	await get_tree().process_frame
	_check(cam.global_position.distance_to(before) > 1.0, "key 4 reaches lookdev (silhouette shot)")
	_press(KEY_BRACKETRIGHT)
	await get_tree().create_timer(2.5).timeout
	_check(absf(GameState.dose - 25.0) < 0.01, "] eases Dose up to 25 (%.2f)" % GameState.dose)
	GameState.snap_dose(0.0)

	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


func _press(key: Key) -> void:
	var e := InputEventKey.new()
	e.keycode = key
	e.physical_keycode = key
	e.pressed = true
	Input.parse_input_event(e)


func _param(mat: ShaderMaterial, param: StringName) -> float:
	return float(mat.get_shader_parameter(param))


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
