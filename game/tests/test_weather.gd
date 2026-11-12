extends Node
## The weather (docs/log/full-game-run.md, "Weather"; M11's "each kind of weather
## tested"), in night_base's furniture with the Weather node set by hand:
## - rain halves what a hunter hears (running 8 m off: heard in clear air,
##   not in the rain) and how far his own sounds carry;
## - fog cuts sight to a few metres both ways (a lit porter 8 m off: seen
##   in clear air, not in fog; 3 m off, seen), but his lantern is a glow a
##   hunter can make out from further and come to look at;
## - snow takes his snow outdoors (not under a roof), and a hunter who
##   loses him follows the freshest one.
## Run: tools/check.sh

const TEST_SAVE := "user://test_weather_save.tres"

var _fails := 0
var _pilot: NightPilot


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	NightPilot.fresh_night(TEST_SAVE)
	Talk.line_seconds = 0.05
	var main := NightPilot.main_with("res://game/dev/encounters/death_demo.tscn")
	add_child(main)
	_pilot = NightPilot.new(main.get(&"current_level"), _check)
	await _pilot.frames(5)
	var night := _pilot.night
	var p := _pilot.player
	(night.get_node(^"Hallucinations") as Hallucinations).active = false
	var weather: Weather = night.get_node(^"Weather")
	var h := (load("res://game/hunting/hunter.tscn") as PackedScene).instantiate() as Hunter
	h.dormant = true
	night.add_child(h)
	await _pilot.frames(2)
	var senses := h.senses
	var heard := [0]
	senses.heard.connect(func(_at: Vector3, _source: Node) -> void: heard[0] += 1)

	# Rain: running heard at 12 m in clear air; in rain, half. (The line
	# x = -2 runs through the north open bay and clears the basin and the yew.)
	p.place(Vector3(-2.0, 0.05, -16.0), 0.0)
	h.global_transform = Transform3D(Basis.IDENTITY, Vector3(-2.0, 0.05, -24.0))
	await _pilot.frames(2)
	weather.kind = Weather.Kind.CLEAR
	senses.hear(p.global_position, Earshot.RUN, p)
	_check(heard[0] == 1, "clear air: running 8 m off is heard")
	weather.kind = Weather.Kind.RAIN
	senses.hear(p.global_position, Earshot.RUN, p)
	_check(heard[0] == 1 and is_equal_approx(Weather.hearing_factor(get_tree()), 0.5), "rain: running 8 m off goes unheard")
	# The range is set in _process, and physics frames can run without one.
	await get_tree().process_frame
	await get_tree().process_frame
	var steps := h.get_node(^"Audio").get_child(0) as AudioStreamPlayer3D
	_check(is_equal_approx(steps.max_distance, 30.0), "and his own steps carry half as far (%.0f m)" % steps.max_distance)

	# Fog: a lit porter 8 m in front.
	h.global_transform = Transform3D(Basis(Vector3.UP, PI), Vector3(-2.0, 0.05, -24.0))
	weather.kind = Weather.Kind.CLEAR
	_check(senses.can_see(p), "clear air: a lit porter 8 m off is seen")
	weather.kind = Weather.Kind.FOG
	_check(not senses.can_see(p), "fog: at 8 m he can't be seen")
	p.place(Vector3(-2.0, 0.05, -21.0), 0.0)
	_check(senses.can_see(p), "at 3 m he can")
	h.global_transform = Transform3D(Basis(Vector3.UP, PI), Vector3(-2.0, 0.05, -22.0))
	p.place(Vector3(-2.0, 0.05, -12.0), 0.0)
	await _pilot.frames(2)
	_check(not senses.can_see(p) and senses.call(&"_glow_in_fog", p), "his lantern is a glow in the fog, 10 m off")
	Input.action_press(&"cover_lantern")
	await _pilot.seconds(0.5)
	_check(not senses.call(&"_glow_in_fog", p), "covered, there's nothing to see")
	Input.action_release(&"cover_lantern")
	weather.call(&"_thicken")
	var env := (night.get_node(^"Abbey/WorldEnvironment") as WorldEnvironment).environment
	_check(env.volumetric_fog_enabled and env.volumetric_fog_density > Weather.FOG_DENSITY - 0.001, "and the fog is thick")

	# Snow: snow outdoors, and a hunter follows them.
	weather.kind = Weather.Kind.SNOW
	var snow: Footprints = night.get_node(^"Footprints")
	p.place(Vector3(-2.0, 0.05, -16.0), 0.0)
	Input.action_press(&"move_forward")
	await _pilot.seconds(2.0)
	Input.action_release(&"move_forward")
	var outdoors := snow.count(&"porter")
	_check(outdoors >= 2, "snow: his steps in the garth leave snow (%d)" % outdoors)
	p.place(Vector3(0.0, 0.05, -1.0), 0.0)
	Input.action_press(&"move_forward")
	await _pilot.seconds(1.5)
	Input.action_release(&"move_forward")
	_check(snow.count(&"porter") == outdoors, "under the refectory roof, none")
	var trail := snow.freshest(&"porter", Vector3(-2.0, 0.05, -18.0), 12.0)
	h.dormant = false
	h.call(&"_set_dormant", false)
	h.last_seen = Vector3(-2.0, 0.05, -12.0)
	h.call(&"_lose_track")
	_check(trail != Vector3.INF and h.state == Hunter.State.INVESTIGATE and (h.get(&"_target") as Vector3).distance_to(trail) < 0.1,
		"losing him, a hunter follows his freshest print")
	h.queue_free()

	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_fails += 1
