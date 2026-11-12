extends Node
## Faces and reading people (docs/systems/faces.md):
## - The script: "Name {mood, tells}: words" reads as a face and words; an
##   unknown mood or tell, a stance with no claim, or a bad truth is an error.
## - Claims and stances: a confrontation is offered only with its proof in
##   the notes; each read sets read_<claim>, changes trust (and Suspicion
##   for the cult rightly confronted), and writes Alric's note, which never
##   says whether he was right.
## - The face: a placeholder figure has a face that knows whose it is,
##   holds a line's mood, plays its tells (a look away turns the head), goes
##   still, and moves its mouth while they talk; a blind face's eyes don't
##   move.
## - In a talk: their face takes each line's mood; the braces never show;
##   stances show beside their answers; picking one reads the claim.
## Run: tools/check.sh

const SCRIPT := """# A test talk with a claim.
== start
Thomas {warm, nod}: Sit, brother.
Thomas {warm, still}: I was with Anselm all night.
-> alibi

== alibi [claim test_alibi lie]
Thomas {warm, still}: I sat with him till Lauds.
* [believe] God keep you for it. -> end
* [press] All night? You never slept? -> end
* [confront crypt_candles] Then whose candle was in the crypt? -> broken

== broken
Thomas {cold, swallow}: (His smile goes.) You've been busy.
-> end
"""

const BAD := """== start
Thomas {furious}: Unknown mood.
Thomas {warm, wink}: Unknown tell.
Thomas {warm: Unclosed.
* [press] A stance with no claim. -> end

== c [claim x maybe]
Thomas: A bad truth.
* [confront not_a_clue] Bad proof. -> end
"""

const TEST_SAVE := "user://test_faces_save.tres"

var _fails := 0


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	GameState.save_path = TEST_SAVE
	Talk.line_seconds = 0.4

	# The script.
	_check(Faces.split("Thomas {warm, still}") == ["Thomas", &"warm", PackedStringArray(["still"])]
		and Faces.split("Prior Hugh") == ["Prior Hugh", &"", PackedStringArray()]
		and Faces.split("Simon {afraid, look down, swallow}")[2] == PackedStringArray(["look down", "swallow"]),
		"\"Name {mood, tells}\" splits into the name, the mood and the tells")
	_check(Faces.key_of("Prior Hugh") == &"hugh" and Faces.key_of("Piers") == &"choirc" and Faces.key_of("Traveller") == &"traveller",
		"a script's name finds its person: Prior Hugh is hugh, Piers is choirc")
	var c := Conversation.new()
	c.text = SCRIPT
	_check(c.errors().is_empty(), "a script with faces, a claim and stances reads without errors %s" % [c.errors()])
	var line := c.point("start").lines[0]
	_check(line.speaker == "Thomas {warm, nod}" and line.text == "Sit, brother.", "the face stays with the speaker, not the words")
	var alibi := c.point("alibi")
	_check(alibi.claim() == [&"test_alibi", "lie"] and alibi.answers[0].stance() == "believe" and alibi.answers[1].stance() == "press"
		and alibi.answers[2].stance() == "confront" and alibi.answers[2].proof() == &"crypt_candles",
		"a claim knows its truth; each stance answer knows its stance, and a confrontation its proof")
	var bad := Conversation.new()
	bad.text = BAD
	var errors := " / ".join(bad.errors())
	_check(errors.contains("unknown mood {furious}") and errors.contains("unknown tell {wink}") and errors.contains("a { with no }")
		and errors.contains("a stance on a point with no [claim]") and errors.contains("unknown tag [claim x maybe]")
		and errors.contains("unknown tag [confront not_a_clue]"),
		"a bad face, a stance with no claim, a bad truth and an unknown proof are errors: %s" % errors)

	# The proof.
	GameState.notes.clear()
	_check(c.offered(alibi).size() == 2, "without the proof in his notes, he can't confront")
	GameState.note(&"crypt_candles")
	_check(c.offered(alibi).size() == 3, "with it, he can")

	# Reads.
	var right := Reading.read(&"r1", "true", "believe", &"hugh", "I was praying in the church.")
	_check(right and GameState.get_flag(&"read_r1") == &"believed" and GameState.has_flag(&"read_r1_right")
		and GameState.trust_of(&"hugh") == People.START_TRUST.get(&"hugh", 0) + 2,
		"believing the truth is right: read_ set, trust +2")
	var before := GameState.trust_of(&"edwin")
	Reading.read(&"r2", "true", "confront", &"edwin", "I was in the dorter.")
	_check(GameState.trust_of(&"edwin") == before - 10 and GameState.has_flag(&"wronged_edwin") and not GameState.has_flag(&"read_r2_right"),
		"confronting the truth costs trust 10, and they remember it")
	var suspicion := GameState.suspicion
	Reading.read(&"r3", "lie", "confront", &"thomas", "I sat with him till Lauds.")
	_check(GameState.suspicion == suspicion + Reading.CULT_SUSPICION and GameState.has_flag(&"read_r3_right"),
		"confronting one of the cult with the truth is right, and they know you know (Suspicion +%d)" % Reading.CULT_SUSPICION)
	suspicion = GameState.suspicion
	Reading.read(&"r4", "hiding", "press", &"simon", "I didn't see anything.")
	_check(GameState.suspicion == suspicion and GameState.has_flag(&"read_r4_right"), "pressing someone who holds back is right")
	var note := _note_text(&"read_r3")
	var note_wrong := _note_text(&"read_r2")
	_check(note.begins_with("Brother Thomas says, \"I sat with him till Lauds.\"") and note.contains("I don't believe him")
		and note_wrong.contains("I don't believe him") and not note.to_lower().contains("right") and not note.to_lower().contains("wrong"),
		"his note says what they said and what he made of it, the same whether he was right or not: %s" % note)
	_check(_note_text(&"read_r4").contains("I pressed him") and Faces.pronoun(&"joan") == "her", "pressing is written so; Joan is \"her\"")

	# The face.
	var abbey: Node3D = load("res://game/world/abbey/abbey.tscn").instantiate()
	add_child(abbey)
	var player: Player = abbey.get_node(^"Player")
	var thomas: Brother = load("res://game/people/brother.tscn").instantiate()
	thomas.name = &"Thomas"
	(thomas.get_node(^"Look") as CharacterLook).look = load("res://game/characters/chr_thomas.tscn")
	abbey.add_child(thomas)
	thomas.place(Transform3D(Basis.IDENTITY, Vector3(-30, 0.05, 5.5)))
	var anselm: Brother = load("res://game/people/brother.tscn").instantiate()
	anselm.name = &"Anselm"
	(anselm.get_node(^"Look") as CharacterLook).look = load("res://game/characters/chr_anselm.tscn")
	abbey.add_child(anselm)
	anselm.place(Transform3D(Basis.IDENTITY, Vector3(-27, 0.05, 5.5)))
	await _seconds(0.5)
	player.place(Vector3(-30, 0.05, 7.5), PI)
	var rig := FaceRig.on(thomas)
	_check(rig != null and rig.who == &"thomas" and rig.is_in_group(&"faces") and rig.mood_now() == &"warm",
		"a placeholder brother has a face that knows whose it is, resting on his baseline (warm)")
	_check(Faces.rig_for(get_tree(), "Thomas") == rig and Faces.rig_for(get_tree(), "Brother Thomas") == rig,
		"a script's name finds his face in the scene")
	rig.line(&"afraid", PackedStringArray(["look away"]), 2.0)
	var yaw_max := 0.0
	var moved_mouth := false
	var mouth := rig._mouth[0] as Node3D
	var mouth_scale := mouth.scale.y if mouth else 1.0
	var t := 0.0
	while t < 2.0:
		await get_tree().process_frame
		t += get_process_delta_time()
		yaw_max = maxf(yaw_max, absf(rig.rotation.y))
		if mouth and absf(mouth.scale.y - mouth_scale) > 0.1:
			moved_mouth = true
	_check(rig.mood_now() == &"afraid" and yaw_max > 0.3, "a line holds its mood, and a look away turns his head (%.2f rad)" % yaw_max)
	_check(moved_mouth, "his mouth moves while he talks")
	rig.line(&"warm", PackedStringArray(["still"]), 3.0)
	_check(rig.tells_now().has(&"still"), "\"still\" stops him for the line")
	var blind := FaceRig.on(anselm)
	var eye := blind._eyes[0] as Node3D
	var eye_at := eye.position.x
	blind.line(&"afraid", PackedStringArray(["glance", "look away"]), 2.0)
	var eye_moved := false
	t = 0.0
	while t < 2.0:
		await get_tree().process_frame
		t += get_process_delta_time()
		if absf(eye.position.x - eye_at) > 0.0005:
			eye_moved = true
	_check(not eye_moved, "Anselm is blind: his eyes don't move, even on a glance")

	# In a talk.
	GameState.notes.clear()
	GameState.note(&"crypt_candles")
	GameState.flags.erase(&"read_test_alibi")
	var offered: Array[PackedStringArray] = []
	Talk.auto_choice = func(options: PackedStringArray) -> int:
		offered.append(Talk.view._marks.duplicate())
		return 2 if options.size() >= 4 else -1
	var moods: Array[StringName] = []
	var watch := func(_s: String, _t: String) -> void: moods.append(rig.mood_now())
	Talk.said.connect(watch)
	await Talk.converse(c, thomas)
	Talk.said.disconnect(watch)
	Talk.auto_choice = Callable()
	var braces := Talk.history.any(func(l: Array) -> bool: return str(l[0]).contains("{") or str(l[1]).contains("{"))
	_check(not braces and Talk.history.has(["Thomas", "Sit, brother."]), "in a talk the braces never show; the name and words do")
	_check(moods.has(&"warm") and moods.has(&"cold"), "his face takes each line's mood (%s)" % [moods])
	_check(not offered.is_empty() and offered[0].slice(0, 3) == PackedStringArray(["believe", "press", "confront"]),
		"the stances show beside their answers (%s)" % [offered])
	_check(GameState.get_flag(&"read_test_alibi") == &"confronted" and GameState.has_flag(&"read_test_alibi_right")
		and GameState.has_note(&"read_test_alibi"), "confronting the claim reads it: the flag, and his note")

	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	print("RESULT: %s" % ("PASS" if _fails == 0 else "FAIL (%d)" % _fails))
	get_tree().quit(0 if _fails == 0 else 1)


func _note_text(id: StringName) -> String:
	for n in GameState.notes:
		if n.get("id") == id:
			return str(n.get("text", ""))
	return ""


func _seconds(t: float) -> void:
	await get_tree().create_timer(t).timeout


func _check(ok: bool, what: String) -> void:
	if not ok:
		_fails += 1
	print("  %s %s" % ["ok  " if ok else "FAIL", what])
