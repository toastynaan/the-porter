extends Node
## Autoload Settings: the player's settings and whether they have finished
## the game (docs/mechanics.md, "Settings and accessibility"; the run's spec,
## "Menus"), kept in one ConfigFile in user://. Changing one emits `changed`;
## the player, the HUD, the subtitles and the audio follow it. Tests point
## `path` elsewhere before they save.

signal changed

const FOV_RANGE := Vector2(60.0, 90.0)
const SENSITIVITY_RANGE := Vector2(0.25, 2.5)
## Subtitle size: small, medium, large.
const SUBTITLE_SCALES: Array[float] = [0.8, 1.0, 1.3]
## Real seconds per in-game hour with the faster clock (3 min an hour is
## the night's own pace; docs/mechanics.md, "Time and duties").
const FAST_CLOCK_FACTOR := 2.0 / 3.0

var path := "user://settings.cfg"

## Degrees, 60-90 (Look and Feel: 70 by default).
var fov := 70.0
## A multiplier on the mouse and stick look speed.
var sensitivity := 1.0
var invert_look := false
## 0..1, the master bus.
var volume := 0.8
## Crouch held (default) or toggled.
var crouch_toggle := false
## 0 small, 1 medium, 2 large.
var subtitle_size := 1
## A dark band behind subtitles and choices.
var subtitle_backing := false
## No head bob, no lantern sway, a softer stumble.
var less_motion := false
## The duty glyph.
var guidance := true
## The candle clock runs a third faster (off by default).
var fast_clock := false
## Finished the game once: chapter select is open.
var finished := false


func _ready() -> void:
	# Tests run on the defaults, whatever the player has set.
	for arg in OS.get_cmdline_args():
		if arg.contains("res://game/tests/"):
			path = "user://test_settings.cfg"
			apply()
			return
	load_settings()


func load_settings() -> void:
	var cfg := ConfigFile.new()
	if cfg.load(path) == OK:
		fov = clampf(float(cfg.get_value("view", "fov", fov)), FOV_RANGE.x, FOV_RANGE.y)
		sensitivity = clampf(float(cfg.get_value("view", "sensitivity", sensitivity)), SENSITIVITY_RANGE.x, SENSITIVITY_RANGE.y)
		invert_look = bool(cfg.get_value("view", "invert_look", invert_look))
		less_motion = bool(cfg.get_value("view", "less_motion", less_motion))
		volume = clampf(float(cfg.get_value("sound", "volume", volume)), 0.0, 1.0)
		crouch_toggle = bool(cfg.get_value("controls", "crouch_toggle", crouch_toggle))
		subtitle_size = clampi(int(cfg.get_value("text", "subtitle_size", subtitle_size)), 0, 2)
		subtitle_backing = bool(cfg.get_value("text", "subtitle_backing", subtitle_backing))
		guidance = bool(cfg.get_value("help", "guidance", guidance))
		fast_clock = bool(cfg.get_value("help", "fast_clock", fast_clock))
		finished = bool(cfg.get_value("profile", "finished", finished))
	apply()


func save_settings() -> void:
	var cfg := ConfigFile.new()
	cfg.set_value("view", "fov", fov)
	cfg.set_value("view", "sensitivity", sensitivity)
	cfg.set_value("view", "invert_look", invert_look)
	cfg.set_value("view", "less_motion", less_motion)
	cfg.set_value("sound", "volume", volume)
	cfg.set_value("controls", "crouch_toggle", crouch_toggle)
	cfg.set_value("text", "subtitle_size", subtitle_size)
	cfg.set_value("text", "subtitle_backing", subtitle_backing)
	cfg.set_value("help", "guidance", guidance)
	cfg.set_value("help", "fast_clock", fast_clock)
	cfg.set_value("profile", "finished", finished)
	if cfg.save(path) != OK:
		push_error("Settings: could not write %s" % path)


## Sets one setting by name and tells everyone.
func set_value(key: StringName, value: Variant) -> void:
	set(key, value)
	apply()


## Pushes the settings out: the volume here, the rest by `changed`.
func apply() -> void:
	var bus := AudioServer.get_bus_index(&"Master")
	AudioServer.set_bus_volume_db(bus, linear_to_db(maxf(volume, 0.0001)))
	AudioServer.set_bus_mute(bus, volume <= 0.001)
	changed.emit()


func subtitle_scale() -> float:
	return SUBTITLE_SCALES[subtitle_size]


## The candle clock's waking pace, from the night's own.
func clock_pace(seconds_per_hour: float) -> float:
	return seconds_per_hour * (FAST_CLOCK_FACTOR if fast_clock else 1.0)
