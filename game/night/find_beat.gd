extends NightBeat
## A body to find on the round (night 4: Edwin in the charnel house). The
## duty flame is over it until he finds it (FoundBody). Drugged (`dose`+),
## the dead sit up and speak (`drugged_lines`).

@export var body: FoundBody
@export var lines := PackedStringArray()
@export var dose := 50.0
@export var drugged_lines := PackedStringArray()


func run() -> void:
	body.show_body()
	body.add_to_group(&"glyph_targets")
	var way := Wayfinding.show_way(self, body.global_position)
	await until(func() -> bool: return body.is_found)
	Wayfinding.put_out(way)
	body.remove_from_group(&"glyph_targets")
	await say_lines(lines)
	if GameState.dose >= dose:
		await say_lines(drugged_lines)
