extends NightBeat
## A short scene (night 2's dawn: the abbot declares the demon, and the
## prior asks the porter where he was). `people` are put at `marks` (a
## Brother by place(), anyone else moved there); the duty flame is over the
## first of them until the porter comes within `near`; then their lines,
## and perhaps one question with three answers (the last line stays up over
## them, and he says the one he picks). Each answer has its reply
## and its tags ("set flag=value; trust hugh -5; suspicion 5", as in a
## conversation's tags), applied when it's picked.

@export var people: Array[Node3D] = []
@export var marks: Array[Marker3D] = []
@export var near := 4.0
@export var lines := PackedStringArray()
@export var answers := PackedStringArray()
@export var replies := PackedStringArray()
@export var answer_tags := PackedStringArray()
## Written in his notes, and set (tonight's), once the lines are said.
@export var note := &""
@export var flag := &""


func run() -> void:
	var p := player()
	for i in mini(people.size(), marks.size()):
		var who := people[i]
		if who.has_method(&"place"):
			who.call(&"place", marks[i].global_transform)
		else:
			who.global_transform = marks[i].global_transform
	if people.is_empty():
		return
	var first := people[0]
	first.add_to_group(&"glyph_targets")
	await until(func() -> bool: return p.global_position.distance_to(first.global_position) < near)
	first.remove_from_group(&"glyph_targets")
	for who in people:
		if who.has_method(&"face"):
			who.call(&"face", p.global_position)
	await say_lines(lines)
	if note != &"":
		GameState.note(note)
	if flag != &"":
		GameState.set_flag(GameState.tonight(String(flag)))
	if answers.is_empty():
		return
	var pick := maxi(await Talk.answer(answers), 0)
	if pick < answer_tags.size():
		var tags := PackedStringArray()
		for t in answer_tags[pick].split(";", false):
			tags.append(t.strip_edges())
		Conversation.apply(tags)
	if pick < replies.size():
		await say_lines(PackedStringArray([replies[pick]]))
