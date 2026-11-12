extends NightBeat
## Night 6's knock (design doc: "a knock. It is someone you know: the
## bailiff, Joan or Mab, depending on earlier choices. Opening the gate is one
## possible ending."). Roger comes if the merchant or his sergeant died (the
## ward has a case); otherwise Joan, if she's alive and the porter took her
## in or turned her away (she knows the race); otherwise Mab. At the grille:
## - Roger: open the gate for him with two kinds of proof (Items) and his men
##   take the abbey (the Gate ending); without them he waits outside;
## - Joan or Mab: let her in and she goes with him (Companion): out by the
##   mill race with her alive is the Witness ending.
## The grille stays open to him all night: he can come back with the proof.

signal opened(who: StringName)

@export var hour := 20.0
@export var grate: Duty
@export var roger: Visitor
@export var joan: Visitor
@export var mab: Visitor
@export var visitor_scene: PackedScene
@export var porch: Marker3D
@export var inside: Marker3D
@export var gate: AbbeyGate
@export var roger_lines := PackedStringArray()
@export var joan_lines := PackedStringArray()
@export var mab_lines := PackedStringArray()
@export var no_proof_lines := PackedStringArray(["Roger {cold}: Show me something I can hang them with, porter, and I'll come in."])

## Opening the gate: something he does, so in brackets (italics).
const OPEN := "(Open the gate.)"

var who := &""
var npc: VisitorNPC


static func caller() -> StringName:
	if GameState.has_flag(&"died_merchant") or GameState.has_flag(&"died_sergeant"):
		return &"roger"
	var joan_seen := GameState.has_flag(&"n2_joan") or GameState.has_flag(&"n5_joan")
	if joan_seen and not GameState.has_flag(&"died_joan"):
		return &"joan"
	return &"mab"


func run() -> void:
	await clock().wait_until(hour)
	who = caller()
	var v: Visitor = {&"roger": roger, &"joan": joan, &"mab": mab}[who]
	npc = visitor_scene.instantiate() as VisitorNPC
	npc.visitor = v
	get_parent().get_parent().add_child(npc)
	npc.global_transform = porch.global_transform
	await say_lines({&"roger": roger_lines, &"joan": joan_lines, &"mab": mab_lines}[who])
	GameState.set_flag(GameState.tonight("knock"), who)
	# The knock is answered whenever he comes to the grille, all night.
	_answer.call()


func _answer() -> void:
	while is_inside_tree():
		await grate.wait_for_use()
		Talk.begin(npc)
		var pick := await Talk.ask(PackedStringArray([OPEN, "(Not yet.)"]), npc.visitor.said_with(npc.visitor.greeting_face), npc.visitor.greeting)
		Talk.end()
		if pick != 0:
			continue
		if who == &"roger" and PriorJudgement.proof_kinds() < 2:
			for line in no_proof_lines:
				var at := line.find(": ")
				await Talk.say(line.left(at) if at > 0 else "", line.substr(at + 2) if at > 0 else line)
			continue
		gate.show_bar(false)
		await gate.swing(true)
		GameState.set_flag(GameState.tonight("gate_opened"), who)
		if who != &"roger":
			await npc.walk_to(inside.global_position)
			var c := Companion.new()
			c.who = who
			npc.add_child(c)
			GameState.change_trust(who, 30)
			c.set_following.call_deferred(true)
		opened.emit(who)
		return
