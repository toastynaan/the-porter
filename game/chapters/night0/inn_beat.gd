extends NightBeat
## Night 0 at the Cross Keys (design doc, "The Cross Keys"; "The lane"): the
## warmest room in the game. He can drink and listen, and walk the lane;
## Agnes (the glyph over her) gives him a room at the top of the house. Once
## he has it, the beat is over and the window's beat wants his bed; the
## evening goes on around him until he lies down, or until midnight.
##
## Until she does, the clock waits at eight (holds_clock_at). As it gets
## there a bell in the city strikes eight and he thinks of the curfew and a
## bed (`eight_lines`), and again every `nudge_every` seconds while he still
## has none (`nudge_lines`) (your ask, 2026-11-16).

@export var agnes: Node3D
## What he thinks as the bell strikes eight, and later while he still has
## no bed. DRAFT.
@export var eight_lines := PackedStringArray(["(A bell somewhere in the city strikes eight. The curfew is at nine, and you've no bed yet. Agnes keeps the house, by the fire at the Keys.)"])
@export var nudge_lines := PackedStringArray(["(Still no bed, and the curfew bell at nine. Agnes, by the fire.)"])
## Real seconds between the reminders *(mine)*.
@export var nudge_every := 180.0

const BELL := preload("res://art/sfx/sfx_bell.wav")
## The bell's strokes: how many, how far apart (s), how loud (dB), far off.
const STROKES := 8
const STROKE_GAP := 1.6
const BELL_DB := -16.0


func run() -> void:
	# Not if he has the room already (he went to Agnes before the gate).
	if not _has_room():
		await say("", "(Warm light and noise across the lane. The Cross Keys.)")
	agnes.add_to_group(&"glyph_targets")
	_nudge.call()
	await until(_has_room)
	agnes.remove_from_group(&"glyph_targets")


func _has_room() -> bool:
	return GameState.has_flag(&"n0_room") or GameState.hour >= 24.0


## At eight, with no room yet: the bell, then his thought; then a reminder
## now and then until he has one.
func _nudge() -> void:
	if holds_clock_at < 0.0:
		return
	await until(func() -> bool: return _has_room() or GameState.hour >= holds_clock_at - 0.001)
	if _has_room():
		return
	_strike_eight.call()
	var lines := eight_lines
	while true:
		await until(func() -> bool: return _has_room() or (Talk.quiet() and not player().busy()))
		if _has_room():
			return
		await say_lines(lines)
		lines = nudge_lines
		await wait(nudge_every)
		if _has_room():
			return


## A church bell in the city, far off, striking eight.
func _strike_eight() -> void:
	if not AudioOut.enabled():
		return
	for i in STROKES:
		if not is_inside_tree():
			return
		# Each stroke its own, so it rings on under the next.
		var stroke := AudioStreamPlayer.new()
		stroke.stream = BELL
		stroke.volume_db = BELL_DB
		add_child(stroke)
		stroke.finished.connect(stroke.queue_free)
		stroke.play()
		await wait(STROKE_GAP)


## Agnes has given him the room.
func skipped() -> void:
	GameState.set_flag(&"n0_room")
