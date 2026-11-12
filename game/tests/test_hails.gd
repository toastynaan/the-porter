extends Node
## People who start talks (docs/systems/dialogue.md, "Who starts a talk"):
## - a hail: someone whose talk has a `hail` point calls out to him the first
##   time he comes near while they can talk, once; it is never where the talk
##   itself starts; E then talks to them as usual, and the talk knows he was
##   hailed;
## - chatter: two people talk among themselves when he comes near, once, each
##   in their own voice; it stops if he walks off.
## Run: tools/check.sh

const HAILER := """@id test_hailer
== hail
Osric {glad}: Brother! You're the new porter?
== start
-> hailed [if hailed_test_hailer]
Osric {calm}: Good evening.
-> end
== hailed
Osric {glad}: I knew it was you.
-> end
"""

const CHATTER := """@id test_chatter
== start
Osric {glad}: And then he says, a horned thing on the wall.
Thomas {warm}: He'd drunk the cellar dry.
Osric {amused}: Twice over.
"""

var _fails := 0


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	Talk.line_seconds = 0.3
	GameState.phase = GameState.Phase.DUSK
	var abbey: Node3D = load("res://game/world/abbey/abbey.tscn").instantiate()
	add_child(abbey)
	var p: Player = abbey.get_node(^"Player")
	var osric := _brother(abbey, "Osric", "res://game/characters/chr_osric.tscn", Vector3(-30, 0.05, 5.5))
	var talker := Talker.new()
	talker.name = &"Talker"
	talker.conversation = TalkLoader.parse(HAILER) as Conversation
	osric.add_child(talker)
	p.place(Vector3(-30, 0.05, 20.0), PI)
	await _seconds(0.6)

	# A hail.
	_check(talker.conversation.start(false) == "start", "a hail is never where the talk starts")
	_check(not Talk.history.any(func(l: Array) -> bool: return l[0] == "Osric"), "far off, nobody calls out")
	p.place(Vector3(-30, 0.05, 9.0), PI)
	await _seconds(0.8)
	_check(Talk.history.has(["Osric", "Brother! You're the new porter?"]) and GameState.has_flag(&"hailed_test_hailer"),
		"coming near, he calls out to him, once")
	await _seconds(1.0)
	var said := Talk.history.size()
	p.place(Vector3(-30, 0.05, 20.0), PI)
	await _seconds(0.5)
	p.place(Vector3(-30, 0.05, 9.0), PI)
	await _seconds(0.8)
	_check(Talk.history.size() == said, "and not again")
	p.place(Vector3(-30, 0.05, 7.5), PI)
	await _seconds(0.2)
	await Talk.converse(talker.conversation, osric)
	_check(Talk.history.has(["Osric", "I knew it was you."]), "talking to him after, the talk knows he was hailed")

	# Chatter.
	var thomas := _brother(abbey, "Thomas", "res://game/characters/chr_thomas.tscn", Vector3(-27, 0.05, 5.5))
	talker.conversation = null
	var chat := Chatter.new()
	chat.talk = TalkLoader.parse(CHATTER) as Conversation
	chat.people = [osric, thomas]
	abbey.add_child(chat)
	chat.global_position = Vector3(-28.5, 0.05, 5.5)
	p.place(Vector3(-28.5, 0.05, 20.0), PI)
	await _seconds(0.6)
	_check(not Talk.history.has(["Osric", "And then he says, a horned thing on the wall."]), "far off, he hears nothing")
	Talk.line_seconds = 0.8
	p.place(Vector3(-28.5, 0.05, 8.5), PI)
	await _seconds(0.6)
	_check(Talk.history.has(["Osric", "And then he says, a horned thing on the wall."]) and GameState.has_flag(&"overheard_test_chatter"),
		"coming near, he hears them talking among themselves")
	p.place(Vector3(-28.5, 0.05, 25.0), PI)
	await _seconds(2.5)
	_check(not Talk.history.has(["Osric", "Twice over."]), "he walks off, and it stops")

	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


func _brother(abbey: Node3D, who: String, look: String, at: Vector3) -> Brother:
	var b: Brother = load("res://game/people/brother.tscn").instantiate()
	b.name = who
	(b.get_node(^"Look") as CharacterLook).look = load(look)
	abbey.add_child(b)
	b.place(Transform3D(Basis.IDENTITY, at))
	return b


func _seconds(t: float) -> void:
	await get_tree().create_timer(t).timeout


func _check(ok: bool, what: String) -> void:
	if not ok:
		_fails += 1
	print("  %s %s" % ["ok  " if ok else "FAIL", what])
