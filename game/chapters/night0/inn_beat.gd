extends NightBeat
## Night 0 at the Cross Keys (design doc, "The Cross Keys"; "The lane"): the
## warmest room in the game. He can drink and listen, and walk the lane;
## Agnes (the glyph over her) gives him a room at the top of the house. Once
## he has it, the beat is over and the window's beat wants his bed; the
## evening goes on around him until he lies down, or until midnight.

@export var agnes: Node3D


func run() -> void:
	await say("", "(Warm light and noise across the lane. The Cross Keys.)")
	agnes.add_to_group(&"glyph_targets")
	await until(func() -> bool: return GameState.has_flag(&"n0_room") or GameState.hour >= 24.0)
	agnes.remove_from_group(&"glyph_targets")


## Agnes has given him the room.
func skipped() -> void:
	GameState.set_flag(&"n0_room")
