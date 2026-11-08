extends NightBeat
## Night 6: the hunt (design doc: "all five cultists in costume. Every route
## you've learned is in play"). The Hunt sends its hunters out (its
## count_override: the whole cult but Thomas, who leads the rite) and they
## stay out until dawn.

@export var hunt: Hunt
@export var lines := PackedStringArray()


func run() -> void:
	hunt.begin()
	await say_lines(lines)
