extends NightBeat
## Night 0 at the gate (design doc, "Night 0": the abbey gate is shut and
## barred and nobody answers; since the old porter went blind no one keeps
## it at night; Mab, begging by the gate, sends him to the Cross Keys). He
## knocks at the grille; nobody comes. Then Mab (the glyph over her) tells
## him where to go.

@export var knock: Duty
@export var mab: Node3D

const KNOCK := preload("res://art/sfx/sfx_knock.wav")


func run() -> void:
	await say("", "(The gate is shut and barred. A lantern burns over it, and no light behind.)")
	await knock.wait_for_use()
	if AudioOut.enabled():
		var a := AudioStreamPlayer3D.new()
		a.stream = KNOCK
		add_child(a)
		a.global_position = knock.global_position
		a.play()
	await say("", "(You knock. You wait. Nobody comes.)")
	mab.add_to_group(&"glyph_targets")
	await until(func() -> bool: return GameState.has_flag(&"n0_sent_to_inn"))
	mab.remove_from_group(&"glyph_targets")
