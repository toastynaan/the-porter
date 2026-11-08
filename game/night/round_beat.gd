extends NightBeat
## The lantern round (design doc, "Core loop": a set route through 4-5 areas,
## checking doors and lamps; Dose from the incense fades over the round).
## Night 3 is the Stalking phase: the demon appears on the route, closer
## each time, "end of the walk, then the doorway, then behind you in the
## choir". The stops are Duty children of `stops`, in order; each one's
## "hint" metadata says where it is (a placeholder until the candle clock and
## the ledger carry the duties) and its "line" is what the porter finds.

@export var stops: Node3D
@export var stalker: Stalker
## Marker3Ds: where it may stand at the end of a walk, and in a doorway.
@export var walk_end: Node3D
@export var doorways: Node3D


func run() -> void:
	var duties: Array[Duty] = []
	for c in stops.get_children():
		if c is Duty:
			duties.append(c)
	for i in duties.size():
		var hint := String(duties[i].get_meta(&"hint", ""))
		if not hint.is_empty():
			await say("", hint)
		await duties[i].wait_for_use()
		await say("", String(duties[i].get_meta(&"line", "(All is as it should be.)")))
		await _appearance_done()
		match i:
			0:
				stalker.appear_from(points(walk_end))
			1:
				stalker.appear_from(points(doorways))
			2:
				stalker.appear_behind()
				await stalker.handed_over
	GameState.set_flag(&"n3_round")


## Lets the last appearance finish before the next is called up.
func _appearance_done() -> void:
	while stalker.active:
		await get_tree().physics_frame
