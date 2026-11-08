class_name Night6Ending
extends Node
## How night 6 ends (docs/full-game-run.md, "Endings", checked in this
## order). The New Faith is CaptureFlow's (caught after the wine). The rest:
## - the Demon: he struck "the demon" (DemonChoice);
## - the Rising: the rite finished with the count at 9 or more (RiteBeat);
## - the Fire, the Gate, the Witness, the Broken Rite: when he leaves (out at
##   the opened gate into the lane, or out under the wall by the mill race at
##   `race_exit`) or holds out to Lauds (`dawn`): the granary and the crypt
##   both burned with the book (the Fire); else the gate opened for Roger
##   with proof (the Gate); else out by the race with Mab or Joan alive at his
##   heels (the Witness); else the Broken Rite.
## Each ends with its lines, then the night (NightDirector.end_night) and the
## chronicle (GameFlow).

@export var director: NightDirector
@export var demon: DemonChoice
@export var knock: Node
@export var race_exit: Marker3D
@export var race_radius := 2.5
## West of this x he's out of the gate, in the lane.
@export var lane_x := -41.0
@export var dawn := 30.0
@export var lines := {}

var ending := &""


func _ready() -> void:
	if demon:
		demon.struck.connect(func() -> void: finish(&"demon"))
	if knock and knock.has_signal(&"opened"):
		knock.connect(&"opened", func(who: StringName) -> void:
			if who == &"roger":
				finish(&"gate"))


func _physics_process(_delta: float) -> void:
	if ending != &"" or GameState.night != 6:
		return
	if GameState.has_flag(&"rite_done") and GameState.count >= 9:
		finish(&"rising")
		return
	var p := get_tree().get_first_node_in_group(&"player") as Player
	if p == null:
		return
	var out_by_race := race_exit and p.global_position.distance_to(race_exit.global_position) < race_radius
	var out_by_gate := GameState.has_flag(&"n6_gate_opened") and p.global_position.x < lane_x
	if out_by_race or out_by_gate or GameState.hour >= dawn - 0.01:
		finish(decide(out_by_race))


## The ending for leaving now (or holding out to dawn).
static func decide(by_race: bool) -> StringName:
	if GameState.has_flag(&"fire_granary") and GameState.has_flag(&"fire_crypt") and GameState.has_flag(&"book_burned"):
		return &"fire"
	if GameState.get_flag(&"n6_gate_opened", &"") == &"roger" and PriorJudgement.proof_kinds() >= 2:
		return &"gate"
	if by_race and _companion_alive():
		return &"witness"
	return &"broken_rite"


static func _companion_alive() -> bool:
	var tree := Engine.get_main_loop() as SceneTree
	for c in tree.root.find_children("*", "", true, false):
		var comp := c as Companion
		if comp and comp.following and not comp.is_caught and (comp.who == &"joan" or comp.who == &"mab"):
			return true
	return false


func finish(id: StringName) -> void:
	if ending != &"":
		return
	ending = id
	GameState.set_flag(&"ending", id)
	var said: PackedStringArray = lines.get(id, PackedStringArray())
	for line in said:
		var at := line.find(": ")
		if at > 0 and not line.begins_with("("):
			await Talk.say(line.left(at), line.substr(at + 2))
		else:
			await Talk.say("", line)
	if director:
		director.end_night()
