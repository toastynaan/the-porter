extends Control
## The hour as the sky shows it: a small dial in the top right corner, a
## half circle over a line of horizon. By day a sun crosses it, from the
## east at six to the west as it sets; by night a moon. Under it, the hour in
## words as the watch calls it, to the nearest quarter ("Nine of the clock",
## "Half past nine"), so the curfew at nine can be seen coming (your ask,
## 2026-11-16: the moon alone didn't say what hour it was). Faint, so it
## sits at the edge of the eye (Look and Feel, "UI": almost no HUD; your
## ask, 2026-11-12). Shown while there's a night or day to play, not in
## menus or while a card is up; Settings, "The sky dial", turns it off.

## When the sun rises and sets, and the moon, by the clock (hours; past
## midnight counts on, 30 is six in the morning).
const SUNRISE := 6.0
const SUNSET := 17.25
## Size at 1080 lines, px: the dial's width and its margin from the corner.
const WIDTH := 58.0
const MARGIN := 26.0
const INK := Color(0.86, 0.82, 0.72, 0.38)
const SUN := Color(0.98, 0.78, 0.45, 0.75)
const MOON := Color(0.82, 0.86, 0.94, 0.7)
## The hour's words: their size at 1080 lines, px, and how far under the horizon.
const FONT := preload("res://art/fonts/eb_garamond/EBGaramond.ttf")
const WORDS_SIZE := 17.0
const WORDS_BELOW := 24.0
const WORDS := Color(0.86, 0.82, 0.72, 0.62)
const NUMBERS := ["Twelve", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven"]

var _hour := -1.0


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func _process(_delta: float) -> void:
	var want := Settings.sky_dial and _playing()
	if want != visible:
		visible = want
	var h := snappedf(GameState.hour, 0.02)
	if visible and h != _hour:
		_hour = h
		queue_redraw()


## A level is loaded and being played (not the title, a menu or a card).
func _playing() -> bool:
	var player := get_tree().get_first_node_in_group(&"player")
	return player != null and GameState.seconds_per_hour > 0.0 and not get_tree().paused


func _draw() -> void:
	var u := size.y / 1080.0
	var w := WIDTH * u
	var r := w * 0.5
	var centre := Vector2(size.x - MARGIN * u - r, MARGIN * u + r)
	var line := maxf(1.0, 1.2 * u)
	# The sky's arc and the horizon.
	draw_arc(centre, r, PI, TAU, 32, INK, line, true)
	draw_line(centre + Vector2(-r - 4.0 * u, 0.0), centre + Vector2(r + 4.0 * u, 0.0), INK, line, true)
	var h := fposmod(GameState.hour, 24.0)
	var day := h >= SUNRISE and h < SUNSET
	# How far across the sky: the sun by day, the moon by night (sunset to sunrise).
	var t: float
	if day:
		t = (h - SUNRISE) / (SUNSET - SUNRISE)
	else:
		var since := fposmod(h - SUNSET, 24.0)
		t = since / (24.0 - (SUNSET - SUNRISE))
	var angle := PI + PI * clampf(t, 0.0, 1.0)
	var at := centre + Vector2(cos(angle), sin(angle)) * r
	if day:
		draw_circle(at, 3.4 * u, SUN, true, -1.0, true)
	else:
		draw_circle(at, 3.2 * u, MOON, true, -1.0, true)
		# A crescent: the moon with a bite of night taken out of it.
		draw_circle(at + Vector2(1.6, -1.0) * u, 2.8 * u, Color(0.05, 0.05, 0.07, 0.85), true, -1.0, true)
	# The hour in words, under the horizon.
	var words := hour_words(GameState.hour)
	var px := int(round(WORDS_SIZE * u))
	if px <= 0:
		return
	var wide := FONT.get_string_size(words, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
	var at_words := Vector2(minf(centre.x - wide * 0.5, size.x - MARGIN * u * 0.6 - wide), centre.y + WORDS_BELOW * u)
	draw_string_outline(FONT, at_words, words, HORIZONTAL_ALIGNMENT_LEFT, -1, px, maxi(2, int(3.0 * u)), Color(0.0, 0.0, 0.0, 0.45))
	draw_string(FONT, at_words, words, HORIZONTAL_ALIGNMENT_LEFT, -1, px, WORDS)


## The hour as the watch would call it, to the nearest quarter: "Nine of the
## clock", "A quarter past nine", "Half past nine", "A quarter to ten";
## "Midnight" and "Noon".
static func hour_words(hour: float) -> String:
	var q := int(round(fposmod(hour, 24.0) * 4.0)) % 96
	var h := floori(q / 4.0)
	var part := q % 4
	var next := (h + 1) % 24
	match part:
		0:
			if h == 0:
				return "Midnight"
			if h == 12:
				return "Noon"
			return "%s of the clock" % NUMBERS[h % 12]
		1:
			return "A quarter past %s" % _name(h)
		2:
			return "Half past %s" % _name(h)
		_:
			return "A quarter to %s" % _name(next)


static func _name(h: int) -> String:
	if h == 0:
		return "midnight"
	if h == 12:
		return "noon"
	return String(NUMBERS[h % 12]).to_lower()
