extends NightBeat
## Night 0 at the gate (design doc, "Night 0": the abbey gate is shut and
## barred and nobody answers; since the old porter went blind no one keeps
## it at night; Mab, begging by the gate, sends him to the Cross Keys). The
## carter told him to knock (carter.talk). He knocks at the grille; nobody
## comes; and Mab, by the wall, speaks up herself (her talk, n0_mab): nobody
## opens that gate at night now, he'll have to stay at the Keys (your ask,
## 2026-11-16). If he walks off before she's done, the mark goes over her.
##
## He needn't knock. If he talks to Mab first ("No use knocking, brother"),
## or goes straight over to the Keys and Agnes gives him the room, the gate
## is behind him and the knock is no longer wanted: before, the night waited
## here for a knock that never came, and his bed never became his.
##
## Nor does the night wait at the gate past eight. If the clock gets as far
## as it may with no bed (the Inn's hold) and he has neither knocked nor
## heard Mab out, the gate's beat is over and the Inn's begins: its bell
## strikes eight and he thinks of Agnes.

@export var knock: Duty
@export var mab: Node3D

const KNOCK := preload("res://art/sfx/sfx_knock.wav")


func run() -> void:
	# After the carter's last word.
	await until(Talk.quiet)
	if not _moved_on():
		await say("", "(The gate is shut and barred. A lantern burns over it, and no light behind.)")
	var knocked := [false]
	var on_knock := func(_by: Node) -> void: knocked[0] = true
	knock.used.connect(on_knock)
	knock.enabled = true
	await until(func() -> bool: return knocked[0] or _moved_on() or _clock_waits())
	knock.enabled = false
	knock.used.disconnect(on_knock)
	if knocked[0]:
		# Mab's first words know it ("I could have told you.").
		GameState.set_flag(&"n0_knocked")
		if AudioOut.enabled():
			var a := AudioStreamPlayer3D.new()
			a.stream = KNOCK
			add_child(a)
			a.global_position = knock.global_position
			a.play()
		await say("", "(You knock. You wait. Nobody comes.)")
		var talker := mab.get_node_or_null(^"Talker") as Talker
		if talker and not _moved_on():
			await talker.interact(player())
		if not _moved_on():
			mab.add_to_group(&"glyph_targets")
			await until(func() -> bool: return _moved_on() or _clock_waits())
			mab.remove_from_group(&"glyph_targets")
	elif GameState.has_flag(&"n0_sent_to_inn") and not GameState.has_flag(&"n0_room"):
		# Mab, before any knock: the Keys once she has had her say.
		await until(Talk.quiet)


## The gate is behind him: Mab has sent him to the Keys, or Agnes has
## given him the room already.
func _moved_on() -> bool:
	return GameState.has_flag(&"n0_sent_to_inn") or GameState.has_flag(&"n0_room")


## The clock has gone as far as it may while he has no bed (the director's
## cap: the Inn's hold at eight).
func _clock_waits() -> bool:
	var c := clock()
	return c != null and GameState.hour >= c.cap - 0.001


## He knocked, and Mab has sent him to the Keys.
func skipped() -> void:
	GameState.set_flag(&"n0_knocked")
	GameState.set_flag(&"n0_sent_to_inn")
