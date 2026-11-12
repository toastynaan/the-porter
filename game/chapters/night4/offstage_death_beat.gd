extends NightBeat
## Someone dies out of sight (night 4: Edwin, before Matins). At `hour` the
## flags in `died` are set (so a Brother named in them is out of the world
## from the next phase), and `body`, where he lies, is in the world from now
## (a FoundBody: it feeds the rite as it's shown).

@export var hour := 23.0
@export var died: Array[StringName] = []
@export var body: FoundBody


func run() -> void:
	await clock().wait_until(hour)
	for f in died:
		GameState.set_flag(f)
	for b: Brother in get_tree().get_nodes_in_group(&"brothers"):
		if b.is_dead():
			b.place(null)
	if body:
		body.show_body()
