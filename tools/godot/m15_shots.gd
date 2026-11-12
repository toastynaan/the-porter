extends Node
## Stills of M15's night 6 through the full render pipeline, to
## art/_review/m15/ (tools/m15_shots.sh). Each beat is staged in night 6's
## scene: the people put where the beat puts them, its lines up.

const OUT := "res://art/_review/m15/"

var _n := 0
var _main: Node
var _pilot: NightPilot
## The beats' line lists, kept as each night loads: "Beat/prop" -> lines.
var _lines := {}


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	Talk.line_seconds = 30.0
	Talk.auto_choice = func(_o: PackedStringArray) -> int: return -1
	var night := await _load(6, "res://game/chapters/night6/night6.tscn")
	var p := _pilot.player
	GameState.hour = 16.4
	var anselm := night.get_node(^"Bodies/Anselm") as Node3D
	p.place(Vector3(27.6, 0.05, 2.4), deg_to_rad(-90.0))
	_look_at(p, anselm.global_position + Vector3.UP * 0.5)
	_say("", _line(night, "Director/Anselm", "lines"))
	await _shot("anselm_in_his_bed", 1.5)
	var thomas := night.get_node(^"Brothers/Thomas") as Brother
	thomas.place((night.get_node(^"Marks/ThomasWine") as Marker3D).global_transform)
	p.place(thomas.global_position + Vector3(-1.4, 0, 0.3), deg_to_rad(-90.0))
	thomas.face(p.global_position)
	_look_at(p, thomas.face_position())
	_say("Thomas", _line(night, "Director/Wine", "offer_lines"))
	await _shot("thomas_brings_wine", 1.0)
	thomas.place(null)
	GameState.hour = 19.5
	var hunt := night.get_node(^"Hunt") as Hunt
	hunt.begin()
	for h in hunt.hunters:
		h.stand_still()
	await get_tree().create_timer(0.3).timeout
	if not hunt.hunters.is_empty():
		var h0 := hunt.hunters[0]
		p.place(h0.global_position + Vector3(0, 0, 5.0), 0.0)
		_look_at(p, h0.global_position + Vector3.UP * 1.5)
	_say("", _line(night, "Director/Hunt", "lines"))
	await _shot("the_cult_in_costume", 1.0)
	hunt.end()
	GameState.hour = 20.0
	var roger := _visitor(night, "res://game/chapters/night6/visitors/roger_n6.tres", _pilot.mark("Porch"))
	p.place(Vector3(-39.0, 0.05, -2.0), deg_to_rad(90.0))
	_look_at(p, roger.face_position())
	_say("Roger", (roger.visitor as Visitor).greeting)
	await _shot("roger_at_the_grille", 1.0)
	roger.queue_free()
	var mask := night.get_node(^"Proof/Mask") as Node3D
	p.place(mask.global_position + Vector3(-1.6, 0.0, 0.0) * 1.0 + Vector3(0, -0.1, 0), deg_to_rad(-90.0))
	_look_at(p, mask.global_position)
	_say("", _line_any(["n6 proof mask"]))
	await _shot("the_proof_in_the_passage", 1.0)
	GameState.hour = 23.2
	var victim := night.get_node(^"Victim") as Node3D
	victim.visible = true
	for c in victim.get_children():
		(c as Node3D).visible = c.name == &"Pilgrim"
	thomas.place((night.get_node(^"Marks/ThomasRite") as Marker3D).global_transform)
	p.place(Vector3(19.0, -4.0, -32.0), deg_to_rad(-90.0))
	_look_at(p, victim.global_position + Vector3.UP * 0.6)
	_say("", _line(night, "Director/Rite", "rite_lines"))
	await _shot("the_rite_in_the_crypt", 1.0)
	thomas.place(null)
	victim.visible = false
	var saint := night.get_node(^"Saint") as HungrySaint
	GameState.count = 9
	saint.wake()
	saint.set_physics_process(false)
	# In the garth, against the snow: a gap in the light.
	saint.global_position = Vector3(0.0, 0.05, -16.0)
	p.place(Vector3(0.0, 0.05, -10.5), 0.0)
	_look_at(p, saint.global_position + Vector3.UP * 1.6)
	_say("", _line(night, "Director/Rite", "silence_lines"))
	await _shot("the_hungry_saint", 1.0)
	saint.sleep()
	var dunstan := night.get_node(^"SaintDeaths/Dunstan") as DeathScene
	p.place(dunstan.global_position + Vector3(0, 0, 5.0), 0.0)
	_look_at(p, dunstan.global_position + Vector3.UP * 1.2)
	dunstan.play()
	await get_tree().create_timer(0.5).timeout
	await _shot("dunstan_taken", 0.05)
	var fire := night.get_node(^"FireGranary") as Fire
	fire.light()
	p.place(fire.global_position + Vector3(2.0, 0, 6.0), deg_to_rad(20.0))
	await get_tree().create_timer(3.0).timeout
	_look_at(p, fire.global_position + Vector3(0, 0.8, 2.0))
	_say("", _line_any(["n6 fire set"]))
	await _shot("the_granary_burns", 0.3)
	fire.set_physics_process(false)
	GameState.snap_dose(85.0)
	GameState.hour = 22.6
	var prior := _visitor(night, "res://game/gate/visitors/prior_hugh.tres", Vector3(2.0, 0.05, -2.0))
	prior.look.visible = false
	prior.add_child((load("res://game/demon/demon_costume.tscn") as PackedScene).instantiate())
	p.place(Vector3(4.6, 0.05, -2.0), deg_to_rad(90.0))
	_look_at(p, prior.face_position())
	_say("", PackedStringArray(night.get_node(^"Demon").get(&"demon_lines"))[0])
	await _shot("the_demon_with_a_light", 1.2)
	print("m15 shots done")
	get_tree().quit()


## A line from the scene lines file (via the beats' copies) or empty.
func _line_any(_keys: Array) -> String:
	return ""


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
