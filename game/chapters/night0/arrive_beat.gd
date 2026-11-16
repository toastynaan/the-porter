extends NightBeat
## Night 0 at the gate (design doc, "Night 0": the abbey gate is shut and
## barred and nobody answers; since the old porter went blind no one keeps
## it at night; Mab, begging by the gate, sends him to the Cross Keys). The
## carter told him to knock (carter.talk). He knocks at the grille; nobody
## comes; and Mab, by the wall, speaks up herself (her talk, n0_mab): nobody
## opens that gate at night now, he'll have to stay at the Keys (your ask,
## 2026-11-16). If he walks off before she's done, the mark goes over her.

@export var knock: Duty
@export var mab: Node3D

const KNOCK := preload("res://art/sfx/sfx_knock.wav")


func run() -> void:
	# After the carter's last word.
	await until(Talk.quiet)
	await say("", "(The gate is shut and barred. A lantern burns over it, and no light behind.)")
	await knock.wait_for_use()
	if AudioOut.enabled():
		var a := AudioStreamPlayer3D.new()
		a.stream = KNOCK
		add_child(a)
		a.global_position = knock.global_position
		a.play()
	await say("", "(You knock. You wait. Nobody comes.)")
	var talker := mab.get_node_or_null(^"Talker") as Talker
	if talker and not GameState.has_flag(&"n0_sent_to_inn"):
		await talker.interact(player())
	if not GameState.has_flag(&"n0_sent_to_inn"):
		mab.add_to_group(&"glyph_targets")
		await until(func() -> bool: return GameState.has_flag(&"n0_sent_to_inn"))
		mab.remove_from_group(&"glyph_targets")


## Mab has sent him to the Keys.
func skipped() -> void:
	GameState.set_flag(&"n0_sent_to_inn")
