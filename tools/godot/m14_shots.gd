extends Node
## Stills of M14's nights 4 and 5 through the full render pipeline, to
## art/_review/m14/ (tools/m14_shots.sh). Each beat is staged in its own
## night's scene: the people put where the beat puts them, its lines up.

const OUT := "res://art/_review/m14/"

var _n := 0
var _main: Node
var _pilot: NightPilot
## The beats' line lists, kept as each night loads: "Beat/prop" -> lines.
var _lines := {}


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	Talk.line_seconds = 30.0
	Talk.auto_choice = func(_o: PackedStringArray) -> int: return -1
	await _night4()
	await _night5()
	print("m14 shots done")
	get_tree().quit()


func _night4() -> void:
	var night := await _load(4, "res://game/nights/night4.tscn")
	var p := _pilot.player
	GameState.hour = 16.6
	var edwin := night.get_node(^"Brothers/Edwin") as Brother
	edwin.place((night.get_node(^"Marks/EdwinDusk") as Marker3D).global_transform)
	p.place(edwin.global_position + Vector3(-1.2, 0, 1.6), 0.0)
	_look_at(p, edwin.face_position())
	_say("Edwin", _line(night, "Director/Edwin", "lines"))
	await _shot("n4_edwin_whispers", 1.2)
	GameState.hour = 19.0
	var mab := _visitor(night, "res://game/gate/visitors/mab_n4.tres", _pilot.mark("Porch"))
	p.place(Vector3(-39.0, 0.05, -2.0), deg_to_rad(90.0))
	_look_at(p, mab.face_position())
	_say("Mab", (mab.visitor as Visitor).greeting)
	await _shot("n4_mab_at_the_grille", 1.0)
	mab.queue_free()
	GameState.hour = 24.5
	var fog := night.get_node(^"FogDeath") as DeathScene
	p.place(fog.global_position + Vector3(-4.0, 0, 0.6), deg_to_rad(-90.0))
	_look_at(p, fog.global_position + Vector3.UP * 1.0)
	fog.play()
	await get_tree().create_timer(0.5).timeout
	await _shot("n4_a_cry_in_the_fog", 0.05)
	await get_tree().create_timer(2.0).timeout
	var hugh := night.get_node(^"Brothers/Hugh") as Brother
	hugh.place((night.get_node(^"Marks/HughKneels") as Marker3D).global_transform)
	p.place(fog.global_position + Vector3(-2.4, 0, 1.4), deg_to_rad(-60.0))
	_look_at(p, fog.global_position + Vector3(0.6, 0.4, 0))
	_say("Hugh", "Stand back from him, porter. And keep your hands where I can see them.")
	await _shot("n4_the_prior_kneels", 1.0)
	hugh.place(null)
	var guest := night.get_node(^"GuestDeath") as DeathScene
	p.place(Vector3(-30.0, 0.05, -16.6), PI)
	_look_at(p, guest.global_position + Vector3.UP * 1.0)
	guest.play()
	await get_tree().create_timer(0.5).timeout
	await _shot("n4_the_guest", 0.05)
	var body := night.get_node(^"Bodies/Edwin") as FoundBody
	body.show_body()
	await get_tree().create_timer(1.5).timeout
	p.place(body.global_position + Vector3(-2.4, 0, 0.6), deg_to_rad(-90.0))
	_look_at(p, body.global_position + Vector3.UP * 0.3)
	_say("", _line(night, "Director/Charnel", "lines"))
	await _shot("n4_edwin_in_the_charnel_house", 1.0)
	var hunters: Array[Hunter] = []
	for m in ["Marks/HunterAhead", "Marks/HunterBehind"]:
		var h := (load("res://game/hunter/hunter.tscn") as PackedScene).instantiate() as Hunter
		h.transform = (night.get_node(NodePath(m)) as Marker3D).global_transform
		night.add_child(h)
		h.stand_still()
		hunters.append(h)
	await get_tree().physics_frame
	var mid := (hunters[0].global_position + hunters[1].global_position) * 0.5
	p.place(mid + Vector3(0, 0, -8.0), 0.0)
	p.rotation.y = PI
	_look_at(p, mid + Vector3.UP * 1.5)
	_say("", _line(night, "Director/Hunters", "two_lines"))
	await _shot("n4_two_at_once", 1.0)
	hunters[1].queue_free()
	hunters[0].unmask()
	p.place(hunters[0].global_position + Vector3(0, 0, -2.6), 0.0)
	p.rotation.y = PI
	_look_at(p, hunters[0].global_position + Vector3.UP * 1.6)
	_say("", _line(night, "Director/Hunters", "unmask_lines"))
	await _shot("n4_osric_unmasked", 1.0)
	hunters[0].queue_free()
	var simon := night.get_node(^"Brothers/Simon") as Brother
	simon.place((night.get_node(^"Marks/SimonScrubbing") as Marker3D).global_transform)
	p.place(simon.global_position + Vector3(-2.0, 0, 1.2), 0.0)
	_look_at(p, simon.face_position())
	_say("Simon", _line(night, "Director/Simon", "lines"))
	await _shot("n4_simon_scrubbing", 1.0)
	GameState.hour = 30.4
	var clock := night.get_node(^"CandleClock") as Node3D
	clock.rotation = Vector3(0, 0, deg_to_rad(80.0))
	p.place(_pilot.mark("DawnCell"), 0.0)
	_look_at(p, clock.global_position)
	_say("", _line(night, "Director/Dawn", "cell_lines"))
	await _shot("n4_the_snapped_clock", 1.0)


func _night5() -> void:
	var night := await _load(5, "res://game/nights/night5.tscn")
	var p := _pilot.player
	GameState.hour = 16.2
	var thomas := night.get_node(^"Brothers/Thomas") as Brother
	var simon := night.get_node(^"Brothers/Simon") as Brother
	var death := night.get_node(^"SimonDeath") as DeathScene
	thomas.place((night.get_node(^"Marks/ThomasDown") as Marker3D).global_transform)
	simon.place(death.global_transform)
	(night.get_node(^"Masked") as Node3D).visible = true
	p.place(death.global_position + Vector3(-5.0, 0, 2.0), deg_to_rad(-70.0))
	_look_at(p, death.global_position + Vector3(-1.0, 0.8, -1.0))
	_say("", _line(night, "Director/Dilemma", "lines"))
	await _shot("n5_the_chapter_house", 1.0)
	(night.get_node(^"Masked") as Node3D).visible = false
	death.victim = simon
	death.play()
	await get_tree().create_timer(0.2).timeout
	await _shot("n5_simons_throat", 0.05)
	await get_tree().create_timer(1.2).timeout
	death.turn_to(p.global_position)
	await _shot("n5_the_masked_man_turns", 0.4)
	GameState.hour = 20.5
	var sergeant := _visitor(night, "res://game/gate/visitors/sergeant_n5.tres", _pilot.mark("Porch"))
	p.place(Vector3(-39.0, 0.05, -2.0), deg_to_rad(90.0))
	_look_at(p, sergeant.face_position())
	_say("Sergeant", (sergeant.visitor as Visitor).greeting)
	await _shot("n5_the_sergeant_at_the_grille", 1.0)
	sergeant.queue_free()
	GameState.hour = 24.4
	_places(night, "Matins")
	var anselm := night.get_node(^"Brothers/Anselm") as Brother
	anselm.place((night.get_node(^"Marks/AnselmChoir") as Marker3D).global_transform)
	p.place(anselm.global_position + Vector3(-1.2, 0, 0.4), deg_to_rad(-90.0))
	_look_at(p, anselm.face_position())
	_say("Anselm", _line(night, "Director/Anselm", "lines"))
	await _shot("n5_anselm_at_matins", 1.0)
	_places(night, "")
	GameState.hour = 25.0
	var grain := night.get_node(^"Duties/Grain") as Node3D
	p.place(grain.global_position + Vector3(0.0, 0, 1.6), 0.0)
	_look_at(p, grain.global_position + Vector3.UP * 0.4)
	_say("", _line(night, "Director/Granary", "pilgrim_lines"))
	await _shot("n5_the_grain", 1.0)
	var h := (load("res://game/hunter/hunter.tscn") as PackedScene).instantiate() as Hunter
	h.transform = (night.get_node(^"Marks/GranaryHunter") as Marker3D).global_transform
	night.add_child(h)
	h.stand_still()
	p.place(grain.global_position + Vector3(0.0, 0, 3.0), 0.0)
	p.rotation.y = 0.0
	_look_at(p, h.global_position + Vector3.UP * 1.4)
	_say("", _line(night, "Director/Granary", "locked_lines"))
	await _shot("n5_barred_in", 1.0)
	h.queue_free()
	GameState.hour = 30.4
	var hugh := night.get_node(^"Brothers/Hugh") as Brother
	for pair in [["Brothers/Hugh", "Marks/HughArrest"], ["Brothers/ChoirB", "Marks/ArrestA"], ["Brothers/ChoirC", "Marks/ArrestB"]]:
		(night.get_node(NodePath(pair[0])) as Brother).place((night.get_node(NodePath(pair[1])) as Marker3D).global_transform)
	p.place(hugh.global_position + Vector3(-2.2, 0, 0.3), deg_to_rad(-90.0))
	_look_at(p, hugh.face_position())
	_say("Hugh", _line(night, "Director/Arrest", "arrest_lines"))
	await _shot("n5_the_arrest", 1.0)


## The first line of a beat's `prop` (without its speaker).
func _line(_night: Node, beat: String, prop: String) -> String:
	var lines := PackedStringArray(_lines.get("%s/%s" % [beat, prop], PackedStringArray()))
	if lines.is_empty():
		return ""
	var at := lines[0].find(": ")
	return lines[0].substr(at + 2) if at > 0 and not lines[0].begins_with("(") else lines[0]


## Loads a night on its own in a fresh main scene, at dusk.
func _load(n: int, path: String) -> Node:
	if _main:
		_main.queue_free()
		await get_tree().process_frame
	NightPilot.fresh_night("user://m13_shots_save.tres")
	GameState.night = n
	GameState.carried = true
	_main = NightPilot.main_with(path)
	add_child(_main)
	await get_tree().create_timer(0.8).timeout
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	_pilot = NightPilot.new(_main.get(&"current_level"), func(_ok: bool, _w: String) -> void: pass)
	var night := _pilot.night
	var director := night.get_node(^"Director")
	for beat in director.get_children():
		for prop in beat.get_property_list():
			if prop["type"] == TYPE_PACKED_STRING_ARRAY:
				_lines["Director/%s/%s" % [beat.name, prop["name"]]] = beat.get(prop["name"])
	director.queue_free()
	Talk.reset()
	(night.get_node(^"Hallucinations") as Hallucinations).active = false
	_pilot.clock().set_pace(3600.0, 0.1)
	return night


## Puts every brother at his place for `phase` ("" for out of the world).
func _places(night: Node, phase: String) -> void:
	for b: Brother in get_tree().get_nodes_in_group(&"brothers"):
		var mark: Node3D = null
		if phase != "":
			mark = night.get_node_or_null(NodePath("Places/%s/%s" % [phase, b.name])) as Node3D
		if mark and b.here_tonight():
			b.place(mark.global_transform)
		else:
			b.place(null)


func _visitor(night: Node, path: String, at: Vector3) -> VisitorNPC:
	var npc := (load("res://game/gate/visitor_npc.tscn") as PackedScene).instantiate() as VisitorNPC
	npc.visitor = load(path)
	night.add_child(npc)
	npc.global_transform = Transform3D(Basis(Vector3.UP, deg_to_rad(-90.0)), at)
	return npc


func _say(who: String, words: String) -> void:
	Talk.reset()
	Talk.say(who, words)


func _look_at(p: Player, at: Vector3) -> void:
	var to := at - p.camera.global_position
	p.rotation.y = atan2(-to.x, -to.z)
	p.head.rotation.x = atan2(to.y, Vector2(to.x, to.z).length())


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
