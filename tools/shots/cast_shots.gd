extends Node3D
## Night 0's real people (the traveller, the carter, the warden:
## tools/build/chr_*.py) to art/_review/cast_night0/ (tools/shots/cast_shots.sh):
## the three side by side in grey studio light and by lantern in the dark;
## each face close, as the talk sees it with the porter's lantern below it:
## a sheet of every mood and a sheet of every tell at its height; the
## warden's lantern raised beside his face; the traveller and the carter
## seated on the wagon, from the porter's seat and from the side; the carter
## walking. Run at 1920x1080 and at the game's 960x540 (suffix "_game").

const OUT := "res://art/_review/cast_night0/"
const CAST := {
	"Traveller": "res://game/characters/chr_traveller.tscn",
	"Carter": "res://game/characters/chr_carter.tscn",
	"Warden": "res://game/characters/chr_warden.tscn",
}
## The porter's lantern from his eyes (game/player/player.tscn, LanternHand).
const LANTERN_FROM_EYES := Vector3(-0.22, -0.36, -0.52)

var _camera: Camera3D
var _sun: DirectionalLight3D
var _env: Environment
var _lamp: OmniLight3D
var _label: Label
var _suffix := ""
var _people: Array[Node3D] = []


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	_env = Environment.new()
	_env.background_mode = Environment.BG_COLOR
	_env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	_env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	var we := WorldEnvironment.new()
	we.environment = _env
	add_child(we)
	_sun = DirectionalLight3D.new()
	_sun.rotation_degrees = Vector3(-30.0, 35.0, 0.0)
	add_child(_sun)
	_camera = Camera3D.new()
	add_child(_camera)
	_camera.current = true
	_lamp = OmniLight3D.new()
	_lamp.light_color = Color(0.878, 0.643, 0.345)
	_lamp.light_energy = 1.8
	_lamp.omni_range = 5.0
	_lamp.omni_attenuation = 0.8
	_lamp.shadow_enabled = true
	_camera.add_child(_lamp)
	_lamp.position = LANTERN_FROM_EYES
	var layer := CanvasLayer.new()
	add_child(layer)
	_label = Label.new()
	_label.add_theme_font_size_override(&"font_size", 13)
	_label.add_theme_color_override(&"font_color", Color(0.85, 0.8, 0.7))
	layer.add_child(_label)
	var floor_mesh := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(30.0, 30.0)
	var floor_mat := StandardMaterial3D.new()
	floor_mat.albedo_color = Color(0.16, 0.15, 0.14)
	floor_mat.roughness = 1.0
	plane.material = floor_mat
	floor_mesh.mesh = plane
	add_child(floor_mesh)
	_run.call_deferred()


func _run() -> void:
	await _frames(2)
	_suffix = "_game" if get_viewport().get_visible_rect().size.x < 1200.0 else ""
	var names: Array = CAST.keys()
	# Only some of them: tools/shots/cast_shots.sh traveller carter
	var only := OS.get_cmdline_user_args()
	if not only.is_empty():
		names = names.filter(func(n: String) -> bool: return only.has(n.to_lower()))

	# The three side by side: studio, then by lantern.
	_studio()
	var line: Array[Node3D] = []
	for i in names.size():
		line.append(_person(names[i], Vector3((i - 1) * 0.9, 0.0, 0.0), PI))
	await _seconds(0.6)
	_still_faces(line)
	_look(Vector3(0.9, 1.25, 4.6), Vector3(0.0, 0.95, 0.0), 30.0)
	await _shot("lineup_front")
	_look(Vector3(-3.4, 1.3, -3.2), Vector3(0.0, 0.95, 0.0), 30.0)
	await _shot("lineup_back")
	_look(Vector3(4.6, 1.2, 0.2), Vector3(0.0, 0.95, 0.0), 30.0)
	await _shot("lineup_side")
	_night()
	_look(Vector3(0.3, 1.6, 2.6), Vector3(0.0, 1.0, 0.0), 48.0)
	await _shot("lineup_by_lantern")
	_clear()

	# Each face as the talk sees it: every mood, then every tell.
	for n: String in names:
		var who := _person(n, Vector3.ZERO, PI)
		var rig := FaceRig.on(who)
		_night()
		_talk_view(who)
		await _seconds(0.4)
		var tiles: Array[Image] = []
		for m in Faces.MOODS:
			rig.mood(m)
			rig._still = 100.0
			await _seconds(0.7)
			tiles.append(await _tile(String(m)))
		_sheet(tiles, n.to_lower() + "_moods")
		tiles.clear()
		for t: StringName in FaceRig.TELL_TIME:
			if t == &"still":
				continue
			rig.mood(&"calm")
			rig._still = 100.0
			await _seconds(0.5)
			rig.tell(t, 0.0)
			await _seconds(float(FaceRig.TELL_TIME[t]) * (0.3 if t == &"blink" else 0.45))
			tiles.append(await _tile(String(t)))
		rig._tells.clear()
		rig.speak(4.0)
		for k in 3:
			await _seconds(0.13 + 0.07 * k)
			tiles.append(await _tile("talking"))
		_sheet(tiles, n.to_lower() + "_tells")
		rig.speak(0.0)
		rig.mood(&"afraid")
		await _seconds(0.7)
		await _shot(n.to_lower() + "_close_afraid")
		rig.mood(&"warm")
		await _seconds(0.7)
		await _shot(n.to_lower() + "_close_warm")
		_clear()

	if names.has("Warden"):
		await _warden_lantern()
	if names.has("Traveller") and names.has("Carter"):
		await _on_the_wagon()
	if names.has("Carter"):
		await _walking()
	print("cast shots done")
	get_tree().quit()


## The warden holds his lantern up beside his face.
func _warden_lantern() -> void:
	var warden := _person("Warden", Vector3.ZERO, PI)
	_night()
	_lamp.visible = false
	var look := warden.get_node(^"Look") as CharacterLook
	var lantern := look.part(^"Lantern")
	var eyes := Vector3(0.0, 2.2, 1.45)
	_look(Vector3(1.4, 1.35, 3.0), Vector3(0.0, 1.2, 0.0), 40.0)
	await _seconds(0.3)
	await _shot("warden_lantern_down")
	if lantern:
		var face := (warden.get_node(^"Look") as CharacterLook).face_position()
		var near := eyes + (face - eyes).normalized() * 0.75 + warden.global_basis.x * 0.25
		lantern.position = (lantern.get_parent() as Node3D).to_local(near)
	await _seconds(0.3)
	await _shot("warden_lantern_up")
	_look(eyes, look.face_position(), 48.0)
	FaceRig.on(warden).mood(&"wary")
	await _seconds(0.6)
	await _shot("warden_lantern_up_porter_view")
	_clear()
	_lamp.visible = true


## On the wagon: the traveller at the back beside the porter, the carter up front.
func _on_the_wagon() -> void:
	var wagon: Node3D = load("res://game/world/road/prop_wagon.tscn").instantiate()
	add_child(wagon)
	var trav := _person("Traveller", Vector3.ZERO, 0.0, true)
	var cart := _person("Carter", Vector3.ZERO, 0.0, true)
	trav.reparent(wagon.get_node(^"Bed/TravellerSeat"), false)
	trav.transform = Transform3D.IDENTITY
	cart.reparent(wagon.get_node(^"Bed/CarterSeat"), false)
	cart.transform = Transform3D.IDENTITY
	_night()
	_env.ambient_light_energy = 0.35
	var seat := wagon.get_node(^"Bed/Seat") as Node3D
	await _seconds(0.5)
	_still_faces([trav, cart])
	var porter_eyes := seat.global_position + Vector3.UP * 0.82
	_look(porter_eyes, (trav.get_node(^"Look") as CharacterLook).face_position(), 48.0)
	await _shot("wagon_porter_view")
	_look(Vector3(3.2, 1.8, 0.6), Vector3(0.0, 1.0, -0.2), 45.0)
	await _shot("wagon_side")
	_look(Vector3(-2.6, 2.2, 2.6), Vector3(0.0, 1.0, -0.3), 45.0)
	await _shot("wagon_back")
	_studio()
	await _shot("wagon_back_studio")
	wagon.queue_free()
	_people.clear()
	await _frames(2)


## The carter walking down the lane.
func _walking() -> void:
	var walker := _person("Carter", Vector3(0.0, 0.0, 1.5), PI)
	_night()
	_look(Vector3(2.2, 1.4, 0.0), Vector3(0.0, 0.9, 0.0), 45.0)
	var t := 0.0
	while t < 0.62:
		walker.position.z -= 1.2 * get_process_delta_time()
		t += get_process_delta_time()
		await get_tree().process_frame
	_look(walker.position + Vector3(2.2, 1.4, 0.0), walker.position + Vector3(0.0, 0.9, 0.0), 45.0)
	await _shot("carter_walking")
	_clear()


## Someone with his look, at `at` turned `yaw` (PI faces +Z, the camera).
func _person(person_name: String, at: Vector3, yaw: float, seated := false) -> Node3D:
	var who := Node3D.new()
	who.name = person_name
	who.position = at
	who.rotation.y = yaw
	var cl := CharacterLook.new()
	cl.name = "Look"
	cl.seated = seated
	who.add_child(cl)
	add_child(who)
	cl.look = load(CAST[person_name])
	_people.append(who)
	return who


func _clear() -> void:
	for p in _people:
		if is_instance_valid(p):
			p.queue_free()
	_people.clear()


func _still_faces(who: Array[Node3D]) -> void:
	for w in who:
		var rig := FaceRig.on(w)
		if rig:
			rig._still = 100.0


func _studio() -> void:
	_env.background_color = Color(0.3, 0.29, 0.28)
	_env.ambient_light_color = Color(0.8, 0.78, 0.74)
	_env.ambient_light_energy = 0.7
	_sun.visible = true
	_sun.light_energy = 1.1
	_lamp.visible = false


## The dark of the road, a little moon, and the porter's lantern.
func _night() -> void:
	_env.background_color = Color(0.043, 0.047, 0.063)
	_env.ambient_light_color = Color(0.43, 0.5, 0.59)
	_env.ambient_light_energy = 0.12
	_sun.visible = true
	_sun.light_energy = 0.05
	_sun.light_color = Color(0.6, 0.68, 0.8)
	_lamp.visible = true


## The talk's view of `who`: from the porter's eyes a step away, narrowed.
func _talk_view(who: Node3D) -> void:
	var face := (who.get_node(^"Look") as CharacterLook).face_position()
	_look(face + Vector3(0.12, 0.02, 1.15), face, 48.0 - 26.0)


func _look(from: Vector3, at: Vector3, fov: float) -> void:
	_camera.fov = fov
	_camera.global_position = from
	_camera.look_at(at)


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _seconds(t: float) -> void:
	await get_tree().create_timer(t).timeout


func _grab() -> Image:
	await RenderingServer.frame_post_draw
	return get_viewport().get_texture().get_image()


func _shot(shot_name: String) -> void:
	_label.text = ""
	var img: Image = await _grab()
	var path := OUT + shot_name + _suffix + ".png"
	img.save_png(ProjectSettings.globalize_path(path))
	print("wrote ", path)


## The middle of the view, labelled.
func _tile(caption: String) -> Image:
	var size := get_viewport().get_visible_rect().size
	var w := int(size.x * 0.25)
	var h := int(size.y * 0.62)
	var top := int(size.y * 0.24)
	_label.text = caption
	_label.position = Vector2((size.x - w) * 0.5 + 6.0, top + 4.0)
	var img: Image = await _grab()
	return img.get_region(Rect2i(int((size.x - w) * 0.5), top, w, h))


func _sheet(tiles: Array[Image], sheet_name: String) -> void:
	if tiles.is_empty():
		return
	var cols := 6
	var w := tiles[0].get_width()
	var h := tiles[0].get_height()
	var rows := ceili(tiles.size() / float(cols))
	var sheet := Image.create(cols * w, rows * h, false, tiles[0].get_format())
	sheet.fill(Color(0.05, 0.05, 0.05))
	for i in tiles.size():
		sheet.blit_rect(tiles[i], Rect2i(0, 0, w, h), Vector2i((i % cols) * w, int(float(i) / cols) * h))
	var path := OUT + sheet_name + _suffix + ".png"
	sheet.save_png(ProjectSettings.globalize_path(path))
	print("wrote ", path)
