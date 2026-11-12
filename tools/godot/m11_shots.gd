extends Node
## Stills of M11's hunters and abbey through the full render pipeline, to
## art/_review/m11/ (tools/m11_shots.sh): rain, fog and snow with prints;
## two hunters at Suspicion 60, one at the gatehouse; Osric unmasked; a
## thrown stone; the bell's friend; a gust and the lantern out; Osric at the
## granary door; Thomas's lit window; the brothers falling silent; Mab
## following; Cole come to fetch him.

const OUT := "res://art/_review/m11/"

var _n := 0
var _main: Node
var _pilot: NightPilot


func _ready() -> void:
	NightPilot.fresh_night("user://m11_shots_save.tres")
	GameState.night = 4
	Talk.line_seconds = 3.0
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	_main = NightPilot.main_with("res://game/dev/encounters/death_demo.tscn")
	add_child(_main)
	await get_tree().create_timer(1.0).timeout
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	_pilot = NightPilot.new(_main.get(&"current_level"), func(_ok: bool, _w: String) -> void: pass)
	var night := _pilot.night
	var p := _pilot.player
	(night.get_node(^"Hallucinations") as Hallucinations).active = false
	GameState.hour = 22.0
	var weather: Weather = night.get_node(^"Weather")

	# Rain, fog, snow, in the garth.
	weather.kind = Weather.Kind.RAIN
	weather.call(&"_ready")
	p.place(Vector3(-6.0, 0.05, -12.0), deg_to_rad(-30.0))
	await _shot("rain", 1.5)
	weather.kind = Weather.Kind.FOG
	weather.call(&"_thicken")
	await _shot("fog", 1.5)
	var env := (night.get_node(^"Abbey/WorldEnvironment") as WorldEnvironment).environment
	env.volumetric_fog_density = 0.01
	weather.kind = Weather.Kind.SNOW
	weather.call(&"_ready")
	Input.action_press(&"move_forward")
	await get_tree().create_timer(3.0).timeout
	Input.action_release(&"move_forward")
	p.rotation.y += PI
	p.head.rotation.x = deg_to_rad(-35.0)
	await _shot("snow_prints", 1.0)
	weather.kind = Weather.Kind.CLEAR

	# Suspicion 60: two hunters, one at the gatehouse.
	var hunt: Hunt = night.get_node(^"Hunt")
	GameState.suspicion = 70
	hunt.begin()
	for h in hunt.hunters:
		h.waiting = true
	p.place(Vector3(-31.0, 0.05, -1.0), deg_to_rad(90.0))
	await _shot("hunter_at_the_gatehouse", 1.0)
	var locked: Door = hunt.locks[1]
	p.place(locked.global_position + Vector3(1.6, 0.05, 0.6), deg_to_rad(90.0))
	_pilot.face(locked.global_position + Vector3(0, 1.0, 0))
	locked.interact(p)
	await _shot("door_locked_at_60", 0.5)
	hunt.end()
	GameState.suspicion = 0

	# Osric unmasked.
	var h := (load("res://game/hunting/hunter.tscn") as PackedScene).instantiate() as Hunter
	h.wearer = &"osric"
	night.add_child(h)
	p.place(Vector3(0.0, 0.05, -16.0), 0.0)
	h.global_transform = Transform3D(Basis(Vector3.UP, PI), Vector3(0.0, 0.05, -18.5))
	h.waiting = true
	h.unmask()
	await _shot("osric_unmasked", 1.0)
	h.queue_free()

	# A stone thrown, a hunter turning to it.
	GameState.satchel.append(&"stone")
	var listener := (load("res://game/hunting/hunter.tscn") as PackedScene).instantiate() as Hunter
	night.add_child(listener)
	listener.global_transform = Transform3D(Basis.IDENTITY, Vector3(8.0, 0.05, -24.0))
	p.place(Vector3(-4.0, 0.05, -26.0), deg_to_rad(-90.0))
	p.head.rotation.x = deg_to_rad(-15.0)
	p.throw()
	await _shot("stone_thrown", 1.4)
	listener.queue_free()

	# The bell out of hours: Edwin comes.
	var bell: OffHoursBell = night.get_node(^"OffHoursBell")
	p.place(bell.global_position + Vector3(0.8, 0, 0.8), deg_to_rad(40.0))
	bell.ring(p)
	await _shot("bell_friend_comes", 2.5)
	await get_tree().create_timer(6.0).timeout

	# A gust on night 2: the lantern goes out.
	GameState.night = 2
	var gust: Gust = night.get_node(^"Gusts/TowerStair")
	p.place(gust.global_position - Vector3(0, 1.45, 0), PI)
	await _shot("gust_guttering", 0.6)
	await _shot("lantern_out", 1.5)
	p.lantern.relight()
	GameState.night = 4

	# Routines: Osric at the granary door; Thomas's window.
	GameState.set_phase(GameState.Phase.KNOCKS)
	GameState.hour = 21.0
	var osric: Brother = night.get_node(^"Brothers/Osric")
	p.place(Vector3(-6.0, 0.05, -20.0), deg_to_rad(90.0))
	await get_tree().create_timer(0.2).timeout
	osric.place(Transform3D(Basis.IDENTITY, Vector3(-11, 0.05, -18)))
	osric.set(&"_routine_on", true)
	await get_tree().create_timer(4.0).timeout
	_pilot.face(osric.global_position + Vector3.UP * 1.4)
	await _shot("osric_locks_the_granary", 0.5)
	var thomas: Brother = night.get_node(^"Brothers/Thomas")
	thomas.place(Transform3D(Basis.IDENTITY, Vector3(28, 0.05, 0.0)))
	(night.get_node(^"RoutineLights/Infirmary") as Candle).lit = true
	p.place(Vector3(24.8, 0.05, 2.5), deg_to_rad(60.0))
	_pilot.face(Vector3(28, 1.2, 0.0))
	await _shot("thomas_at_his_herbs", 1.0)

	# The talk stops: the brothers turn to look.
	GameState.set_phase(GameState.Phase.DUSK)
	GameState.hour = 16.5
	await get_tree().create_timer(0.5).timeout
	var murmur: Murmur = night.get_node(^"Murmur")
	GameState.suspicion = 40
	p.place(murmur.global_position + Vector3(4.0, -1.45, 1.0), deg_to_rad(80.0))
	await get_tree().create_timer(0.5).timeout
	_pilot.face(murmur.global_position)
	await _shot("talk_stops", 0.6)
	GameState.suspicion = 0

	DirAccess.remove_absolute(ProjectSettings.globalize_path(GameState.save_path))
	print("m11 shots done")
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
