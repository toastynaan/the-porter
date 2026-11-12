extends Node
## Stills of M13's nights 1 to 3 through the full render pipeline, to
## art/_review/m13/ (tools/m13_shots.sh). Each beat is staged in its own
## night's scene: the people put where the beat puts them, its lines up.

const OUT := "res://art/_review/m13/"

var _n := 0
var _main: Node
var _pilot: NightPilot


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	Talk.line_seconds = 30.0
	Talk.auto_choice = func(_o: PackedStringArray) -> int: return -1
	await _night1()
	await _night2()
	await _night3()
	print("m13 shots done")
	get_tree().quit()


func _night1() -> void:
	var night := await _load(1, "res://game/chapters/night1/night1.tscn")
	var p := _pilot.player
	# Supper: Bede leans in.
	_places(night, "Supper")
	p.place(_pilot.mark("PorterSeat"), PI)
	var bede := night.get_node(^"Brothers/Warner") as Brother
	_look_at(p, bede.face_position())
	_say("Bede", "Don't eat the bread, porter. Not tomorrow, not any night. Something is wrong with it.")
	await _shot("n1_bede_warns_about_the_bread", 1.0)
	# The merchant at the grille.
	GameState.hour = 19.0
	var merchant := _visitor(night, "res://game/chapters/night1/visitors/merchant_n1.tres", _pilot.mark("Porch"))
	p.place(Vector3(-39.0, 0.05, -2.0), deg_to_rad(90.0))
	_look_at(p, merchant.face_position())
	_say("Merchant", (merchant.visitor as Visitor).greeting)
	await _shot("n1_the_merchant_at_the_grille", 1.0)
	merchant.queue_free()
	# Matins: all present.
	GameState.hour = 24.2
	_places(night, "Matins")
	p.place(_pilot.mark("Choir") + Vector3(-5.5, 0, 0), deg_to_rad(-90.0))
	_say("", "(Every stall filled, every face one you know. All present.)")
	await _shot("n1_matins_all_present", 1.0)
	# The shape at the end of the walk.
	_places(night, "")
	var stalker := night.get_node(^"Stalker") as Stalker
	p.place(Vector3(-10.2, 0.05, -6), deg_to_rad(0.0))
	var ends: Array[Vector3] = []
	for m in night.get_node(^"Stalk/WalkEnd").get_children():
		ends.append((m as Node3D).global_position)
	stalker.appear_from(ends)
	await get_tree().create_timer(0.6).timeout
	_look_at(p, stalker.global_position + Vector3.UP * 1.6)
	await _shot("n1_a_shape_at_the_end_of_the_walk", 0.3)
	stalker.reset()
	# The knock with no one there.
	GameState.hour = 26.0
	p.place(Vector3(-39.0, 0.05, -2.0), deg_to_rad(90.0))
	p.head.rotation.x = deg_to_rad(-4.0)
	_say("", "(No one. The lane is empty both ways, and the lanterns are steady.)")
	await _shot("n1_the_knock_with_no_one_there", 1.0)
	# The merchant in the pond at dawn.
	GameState.hour = 30.3
	var body := night.get_node(^"Bodies/Pond") as FoundBody
	body.show_body()
	var thomas := night.get_node(^"Brothers/Thomas") as Brother
	thomas.place((night.get_node(^"Marks/PondThomas") as Marker3D).global_transform)
	thomas.face(body.global_position)
	await get_tree().create_timer(1.5).timeout
	p.place(body.global_position + Vector3(-3.0, 0, 1.5), 0.0)
	_look_at(p, body.global_position + Vector3(0.3, 0.2, -0.4))
	_say("Thomas", "The merchant. He drowned drunk, poor soul, wandering about in the dark. It happens.")
	await _shot("n1_the_merchant_in_the_pond_at_dawn", 0.6)


func _night2() -> void:
	var night := await _load(2, "res://game/chapters/night2/night2.tscn")
	var p := _pilot.player
	# Supper: Thomas's word in his ear.
	_places(night, "Supper")
	p.place(_pilot.mark("PorterSeat"), PI)
	var thomas := night.get_node(^"Brothers/Thomas") as Brother
	_look_at(p, thomas.face_position())
	_say("Thomas", "(Low, under the reading.) I've seen the prior about the house at night, Alric. Places he has no business being.")
	await _shot("n2_thomas_at_supper", 1.0)
	# The sailor at the grille.
	GameState.hour = 21.5
	var sailor := _visitor(night, "res://game/chapters/night2/visitors/sailor_n2.tres", _pilot.mark("Porch"))
	p.place(Vector3(-39.0, 0.05, -2.0), deg_to_rad(90.0))
	_look_at(p, sailor.part_position(&"hands"))
	await _shot("n2_the_sailor_at_the_grille", 1.0)
	sailor.queue_free()
	# The death in the lane, through the grille.
	GameState.hour = 23.3
	var death := night.get_node(^"LaneDeath") as DeathScene
	death.victim_look = load("res://game/characters/chr_sailor.tscn")
	p.place(Vector3(-39.0, 0.05, -2.0), deg_to_rad(90.0))
	_look_at(p, death.global_position + Vector3.UP * 1.2)
	death.play()
	await get_tree().create_timer(0.15).timeout
	_say("", "(A flash at his throat, one cut, and he folds into the gutter. Blood runs dark in the lantern light.)")
	await _shot("n2_the_death_in_the_lane", 0.05)
	await get_tree().create_timer(1.5).timeout
	await _shot("n2_in_the_gutter", 0.1)
	# Matins: one short.
	_places(night, "Matins")
	p.place(_pilot.mark("Choir") + Vector3(-2.0, 0, 0), deg_to_rad(-90.0))
	_look_at(p, Vector3(16, 1.2, -29.9))
	_say("", "(One short. Bede's stall stands empty, and nobody looks at it.)")
	await _shot("n2_matins_one_short", 1.0)
	# The empty bed.
	GameState.hour = 25.0
	p.place(Vector3(-29.2, 0.05, -19.0), 0.0)
	_look_at(p, Vector3(-29.2, 0.5, -22.6))
	_say("", "(The sailor's bed is empty. The blanket is folded square, as if no one had slept in it.)")
	await _shot("n2_the_empty_bed", 1.0)
	# The abbot at dawn.
	GameState.hour = 30.3
	var godric := night.get_node(^"Brothers/Godric") as Brother
	var hugh := night.get_node(^"Brothers/Hugh") as Brother
	godric.place((night.get_node(^"Marks/GodricDawn") as Marker3D).global_transform)
	hugh.place((night.get_node(^"Marks/HughDawn") as Marker3D).global_transform)
	p.place(godric.global_position + Vector3(-2.6, 0, -0.6), deg_to_rad(-90.0))
	godric.face(p.global_position)
	hugh.face(p.global_position)
	_look_at(p, godric.face_position())
	_say("Godric", "Brothers. A demon has come into this house. Brother Bede is dead of it, and I will not pretend otherwise.")
	await _shot("n2_the_abbot_at_dawn", 1.0)
	# Bede in the bell tower.
	GameState.hour = 24.0
	var bede := night.get_node(^"Bodies/Bede") as FoundBody
	bede.show_body()
	p.place(Vector3(-24, 0.05, -30.8), 0.0)
	await get_tree().create_timer(0.5).timeout
	_look_at(p, bede.global_position + Vector3.UP * 1.4)
	_say("", "(Brother Bede, turning slowly on a rope from the bell's frame. His feet are bare.)")
	await _shot("n2_bede_in_the_bell_tower", 0.6)


func _night3() -> void:
	var night := await _load(3, "res://game/chapters/night3/night3.tscn")
	var p := _pilot.player
	GameState.hour = 25.0
	(night.get_node(^"CryptLight") as Node3D).visible = true
	var hunter := night.get_node(^"Hunter") as Hunter
	hunter.stand_still()
	p.place(_pilot.mark("CryptFoot"), deg_to_rad(-90.0))
	_look_at(p, hunter.global_position + Vector3.UP * 1.3)
	_say("", "(A light, down in the crypt. Someone is down there.)")
	await _shot("n3_the_light_in_the_crypt", 1.0)
	var death := night.get_node(^"CryptPilgrim") as DeathScene
	death.play()
	await get_tree().create_timer(0.3).timeout
	_say("", "(The arm rises and falls, and rises. The bound man's heels drum on the flags and stop.)")
	await _shot("n3_the_killing_in_the_crypt", 0.05)
	await get_tree().create_timer(1.6).timeout
	death.turn_to(p.global_position)
	_say("", "(The figure straightens, and turns, and looks straight at you.)")
	await _shot("n3_the_figure_turns", 0.3)
	var page := night.get_node(^"BookPage") as Readable
	page.interact(p)
	await _shot("n3_the_page_by_the_altar", 0.8)


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
	night.get_node(^"Director").queue_free()
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
