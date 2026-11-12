class_name SettingsMenu
extends MenuPage
## The settings (docs/systems/mechanics.md, "Settings and accessibility"): field of
## view 60-90°, look sensitivity, invert look, volume, crouch held or
## toggled, subtitle size and backing, less motion, guidance (the duty
## glyph) and the faster clock. Each applies at once; leaving saves them.

const SIZES: Array[String] = ["small", "medium", "large"]

var _fov: HSlider
var _sensitivity: HSlider
var _volume: HSlider
var _toggles := {}
var _size_button: Button


func build() -> void:
	heading.text = "Settings"
	page_width = 340.0
	page.custom_minimum_size.x = px(340.0)
	_fov = _slider("Field of view", Settings.FOV_RANGE.x, Settings.FOV_RANGE.y, 1.0, &"fov")
	_sensitivity = _slider("Look sensitivity", Settings.SENSITIVITY_RANGE.x, Settings.SENSITIVITY_RANGE.y, 0.05, &"sensitivity")
	_volume = _slider("Volume", 0.0, 1.0, 0.05, &"volume")
	_toggle("Fullscreen (F11)", &"fullscreen")
	_toggle("Invert look", &"invert_look")
	_toggle("Crouch toggles (instead of held)", &"crouch_toggle")
	_size_button = add_button("", func() -> void:
		Settings.set_value(&"subtitle_size", (Settings.subtitle_size + 1) % SIZES.size())
		refresh())
	_toggle("A dark band behind subtitles", &"subtitle_backing")
	_toggle("Less motion", &"less_motion")
	_toggle("Describe faces in words", &"describe_faces")
	_toggle("Guidance (the duty flame)", &"guidance")
	_toggle("A faster clock", &"fast_clock")
	add_button("Back", func() -> void: back.emit())
	back.connect(Settings.save_settings)


func refresh() -> void:
	_fov.set_value_no_signal(Settings.fov)
	_sensitivity.set_value_no_signal(Settings.sensitivity)
	_volume.set_value_no_signal(Settings.volume)
	for key: StringName in _toggles:
		(_toggles[key] as CheckBox).set_pressed_no_signal(bool(Settings.get(key)))
	_size_button.text = "Subtitles: %s" % SIZES[Settings.subtitle_size]


func _slider(label: String, low: float, high: float, step: float, key: StringName) -> HSlider:
	var row := HBoxContainer.new()
	var l := Manuscript.rich(label, px(14.0))
	l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(l)
	var s := HSlider.new()
	s.min_value = low
	s.max_value = high
	s.step = step
	s.focus_mode = Control.FOCUS_ALL
	s.custom_minimum_size = Vector2(px(130.0), px(16.0))
	s.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	s.value_changed.connect(func(v: float) -> void: Settings.set_value(key, v))
	row.add_child(s)
	column.add_child(row)
	return s


func _toggle(label: String, key: StringName) -> void:
	var c := CheckBox.new()
	c.text = label
	c.focus_mode = Control.FOCUS_ALL
	c.add_theme_font_override(&"font", Manuscript.BOOK_FONT)
	c.add_theme_font_size_override(&"font_size", px(14.0))
	for state in [&"font_color", &"font_hover_color", &"font_focus_color", &"font_pressed_color", &"font_hover_pressed_color"]:
		c.add_theme_color_override(state, Manuscript.INK)
	c.toggled.connect(func(on: bool) -> void: Settings.set_value(key, on))
	column.add_child(c)
	_toggles[key] = c
