extends Node
## Stills of M9's deaths and bodies through the full render pipeline, to
## art/_review/m9/ (tools/m9_shots.sh): each style of death as it happens and
## after, the killer sober and drugged, a hallucination and the nothing
## after it, the crypt's candles, a found body, a hidden one, the cult's
## book page and the ledger's notes.

const OUT := "res://art/_review/m9/"

var _n := 0
var _main: Node
var _pilot: NightPilot


func _ready() -> void:
	NightPilot.fresh_night("user://m9_shots_save.tres")
	GameState.night = 4
	GameState.hour = 22.0
	Talk.line_seconds = 3.0
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	_main = NightPilot.main_with("res://game/encounters/death_demo.tscn")
	add_child(_main)
	await get_tree().create_timer(1.0).timeout
	GameState.hour = 22.0
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	_pilot = NightPilot.new(_main.get(&"current_level"), func(_ok: bool, _w: String) -> void: pass)
	var night := _pilot.night
	var p := _pilot.player
	for b: Brother in get_tree().get_nodes_in_group(&"brothers"):
		b.place(null)

	# Implied, sober: the struggle, then the body and the rolling lantern.
	var implied: DeathScene = night.get_node(^"Deaths/Implied")
	GameState.snap_dose(0.0)
	_watch(implied, Vector3(4.0, 0, 0.6))
	implied.play()
	await _shot("implied_struggle_sober", 0.6)
	await _shot("implied_after", 2.4)

	# Gory, drugged: the demon, blood up the wall.
	var gory: DeathScene = night.get_node(^"Deaths/Gory")
	GameState.snap_dose(80.0)
	_watch(gory, Vector3(3.2, 0, -0.8))
	gory.play()
	await _shot("gory_demon_drugged", 0.45)
	await _shot("gory_after", 2.5)

	# The throat, sober, under the lane's lantern.
	var throat: DeathScene = night.get_node(^"Deaths/Throat")
	GameState.snap_dose(0.0)
	_watch(throat, Vector3(-1.5, 0, 3.5))
	throat.play()
	await _shot("throat_cut", 0.38)
	await _shot("throat_after", 2.5)

	# A hallucination, and what's there when he looks back.
	var fake: DeathScene = night.get_node(^"Deaths/Fake")
	GameState.snap_dose(85.0)
	_watch(fake, Vector3(-4.5, 0, 0.4))
	await fake.play()
	await _shot("fake_body", 1.0)
	_pilot.face(p.global_position - Vector3(10, 0, 0))
	await get_tree().create_timer(1.6).timeout
	_watch(fake, Vector3(-4.5, 0, 0.4))
	await _shot("fake_nothing_there", 0.6)

	# The crypt keeps count: three candles of twelve.
	GameState.snap_dose(0.0)
	p.place(Vector3(19.4, -3.95, -31.0), deg_to_rad(-90.0))
	_pilot.face(Vector3(22.5, -3.6, -32.0))
	await _shot("crypt_candles_three", 1.0)

	# A found body; the book page; a hidden body; the notes.
	var pond: FoundBody = night.get_node(^"Bodies/Pond")
	p.place(pond.global_position + Vector3(-0.6, 0, -2.6), PI)
	_pilot.face(pond.body.call(&"centre") as Vector3)
	await _shot("found_body_pond", 1.5)
	(night.get_node(^"BookPage") as Readable).interact(p)
	await _shot("book_page", 0.6)
	(_main.get_node(^"UI/Page") as PageView).set_showing(false)
	var garden: HiddenBody = night.get_node(^"HiddenBodies/GardenBed")
	garden.uncover()
	p.place(garden.global_position + Vector3(-1.6, 0, -1.4), deg_to_rad(-130.0))
	_pilot.face(garden.global_position + Vector3(0, 0.2, 0))
	await _shot("hidden_body_garden", 1.5)
	var ledger: LedgerView = _main.get_node(^"UI/Ledger")
	ledger.set_showing(true)
	ledger.turn_to(1)
	await _shot("ledger_notes", 0.5)
	ledger.set_showing(false)
	DirAccess.remove_absolute(ProjectSettings.globalize_path(GameState.save_path))
	print("m9 shots done")
	get_tree().quit()


func _watch(death: DeathScene, offset: Vector3) -> void:
	_pilot.player.place(death.global_position + offset, 0.0)
	_pilot.face(death.global_position + Vector3.UP * 1.1)


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
