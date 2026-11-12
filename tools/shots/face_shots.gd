extends Node3D
## The placeholder faces (docs/systems/faces.md) to art/_review/faces/
## (tools/shots/face_shots.sh): every mood on Thomas, close, in plain light;
## the tells as they play; Anselm's blind eyes; and a face by lantern light
## in the dark, as it is read in the game.

const OUT := "res://art/_review/faces/"

var _n := 0
var _camera: Camera3D
var _sun: DirectionalLight3D
var _env: Environment


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	_env = Environment.new()
	_env.background_mode = Environment.BG_COLOR
	_env.background_color = Color(0.32, 0.3, 0.28)
	_env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	_env.ambient_light_color = Color(0.8, 0.76, 0.7)
	_env.ambient_light_energy = 0.8
	_env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	var we := WorldEnvironment.new()
	we.environment = _env
	add_child(we)
	_sun = DirectionalLight3D.new()
	_sun.rotation_degrees = Vector3(-25.0, 20.0, 0.0)
	_sun.light_energy = 1.2
	add_child(_sun)
	_camera = Camera3D.new()
	_camera.fov = 30.0
	add_child(_camera)
	_camera.current = true
	_run.call_deferred()


func _run() -> void:
	# Every mood, a row of Thomases.
	var row: Array[FaceRig] = []
	var people: Array[Node3D] = []
	for i in Faces.MOODS.size():
		var who := _person("Thomas", "res://game/characters/chr_thomas.tscn", Vector3((i % 8) * 0.42, -floorf(i / 8.0) * 0.55, 0.0))
		people.append(who)
		row.append(FaceRig.on(who))
	await _frames(10)
	for i in row.size():
		row[i].mood(Faces.MOODS[i])
		row[i]._still = 100.0
	_camera.position = Vector3(3.5 * 0.42, 1.68 - 0.27, 5.2)
	await _seconds(1.0)
	await _shot("moods")
	for who in people:
		who.queue_free()
	await _frames(3)

	# One face close, each tell at its height.
	var thomas := _person("Thomas", "res://game/characters/chr_thomas.tscn", Vector3.ZERO)
	var rig := FaceRig.on(thomas)
	_camera.position = Vector3(0.0, 1.7, 1.0)
	await _frames(10)
	for t in [&"glance", &"look down", &"look away", &"swallow", &"lip", &"smile", &"flinch"]:
		rig.mood(&"calm")
		rig._still = 100.0
		rig.tell(t, 0.0)
		await _seconds(float(FaceRig.TELL_TIME[t]) * 0.45)
		await _shot("tell_" + String(t).replace(" ", "_"))
		await _seconds(1.0)
	thomas.queue_free()

	# Anselm: blind.
	var anselm := _person("Anselm", "res://game/characters/chr_anselm.tscn", Vector3.ZERO)
	await _frames(10)
	FaceRig.on(anselm).mood(&"afraid")
	await _seconds(0.5)
	await _shot("anselm_blind")
	anselm.queue_free()

	# In the dark, by a lantern below the face: how it's read at night.
	_sun.visible = false
	_env.ambient_light_energy = 0.05
	var hugh := _person("Hugh", "res://game/characters/chr_hugh.tscn", Vector3.ZERO)
	var lamp := OmniLight3D.new()
	lamp.light_color = Color(1.0, 0.72, 0.42)
	lamp.light_energy = 2.0
	lamp.omni_range = 4.0
	lamp.position = Vector3(0.15, 1.1, 0.6)
	add_child(lamp)
	_camera.position = Vector3(0.0, 1.68, 1.3)
	await _frames(10)
	FaceRig.on(hugh).mood(&"cold")
	await _seconds(0.5)
	await _shot("hugh_by_lantern")
	lamp.position = Vector3(0.15, 1.1, 4.5)
	await _seconds(0.3)
	await _shot("hugh_lantern_far")
	print("face shots done")
	get_tree().quit()


## Someone with `look`, facing the camera (+Z), at `at`.
func _person(person_name: String, look: String, at: Vector3) -> Node3D:
	var who := Node3D.new()
	who.name = person_name
	who.position = at
	who.rotation.y = PI
	var cl := CharacterLook.new()
	cl.name = "Look"
	who.add_child(cl)
	add_child(who)
	cl.look = load(look)
	return who


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _seconds(t: float) -> void:
	await get_tree().create_timer(t).timeout


func _shot(shot_name: String) -> void:
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	_n += 1
	var path := OUT + "%02d_%s.png" % [_n, shot_name]
	img.save_png(ProjectSettings.globalize_path(path))
	print("wrote ", path)
