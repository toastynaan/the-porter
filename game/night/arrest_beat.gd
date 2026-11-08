extends NightBeat
## Night 5's dawn (design doc: "the prior arrests you for the killings. If you
## can show him enough (two kinds of proof, or enough written in your
## ledger's notes), he believes you: he lets you go himself and stands with
## you on night 6. If not, Thomas speaks for you and has you released into
## his care."). The prior and those with him wait at `marks`; the duty flame
## is over the prior until the porter comes to him. PriorJudgement decides:
## prior_believes, or thomas_custody.

@export var people: Array[Brother] = []
@export var marks: Array[Marker3D] = []
@export var thomas: Brother
@export var thomas_at: Marker3D
@export var near := 4.0
@export var arrest_lines := PackedStringArray()
@export var believed_lines := PackedStringArray()
@export var custody_lines := PackedStringArray()


func run() -> void:
	var p := player()
	for i in mini(people.size(), marks.size()):
		people[i].place(marks[i].global_transform)
	var prior := people[0]
	prior.add_to_group(&"glyph_targets")
	await until(func() -> bool: return p.global_position.distance_to(prior.global_position) < near)
	prior.remove_from_group(&"glyph_targets")
	for b in people:
		b.face(p.global_position)
	await say_lines(arrest_lines)
	if PriorJudgement.believes():
		GameState.set_flag(&"prior_believes")
		GameState.change_trust(&"hugh", 40)
		await say_lines(believed_lines)
	else:
		GameState.set_flag(&"thomas_custody")
		if thomas and thomas_at:
			thomas.place(thomas_at.global_transform)
			thomas.face(p.global_position)
		await say_lines(custody_lines)
