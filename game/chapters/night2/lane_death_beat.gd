extends NightBeat
## Night 2's lane death (docs/log/full-game-run.md, "Witnessed deaths"): toward
## midnight a cry from the lane, and Gib's call doesn't come. At the grille,
## under a street lantern, a man is killed: whoever the porter turned away
## after the curfew bell tonight (a visitor whose fate is "lane"), or, if no
## one, Jankin, put out of the Cross Keys at closing, unless the porter
## asked Hob at dusk to keep him in (n2_jankin_kept_in): then no one dies,
## and the night stays quiet. The tall shape behind him never moves while
## the porter looks. The death feeds the rite as the lane death.

## Named outsiders never die in view (docs/log/full-game-run.md).
const NAMED: Array[StringName] = [&"walter", &"joan", &"roger", &"mab"]

@export var hour := 23.25
@export var grate: Duty
@export var death: DeathScene
@export var curfew: Curfew
## Tonight's visitors, to find whom he turned away after the bell.
@export var visitors: Array[Visitor] = []
@export var jankin_look: PackedScene
@export var kept_in_flag := &"n2_jankin_kept_in"
@export var cry_lines := PackedStringArray(["(A cry from the lane, cut off.)"])
@export var death_lines := PackedStringArray()
@export var after_lines := PackedStringArray()


func run() -> void:
	await clock().wait_until(hour)
	var look := jankin_look
	var who := &"jankin"
	for v in visitors:
		var fate: Variant = GameState.get_flag(StringName(String(v.flag) + "_fate"), &"")
		if not NAMED.has(v.id) and fate == &"lane":
			look = v.look
			who = v.id
	if who == &"jankin" and GameState.has_flag(kept_in_flag):
		GameState.set_flag(GameState.tonight("lane_quiet"))
		return
	clock().wake()
	if curfew:
		curfew.silence()
	await say_lines(cry_lines)
	await grate.wait_for_use()
	death.victim_look = look
	await death.play()
	await say_lines(death_lines)
	GameState.set_flag(StringName("died_" + String(who)))
	if who != &"jankin":
		GameState.set_flag(&"lane_death_was_turned_away")
	await say_lines(after_lines)
