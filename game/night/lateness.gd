class_name Lateness
## Being late for a duty (docs/mechanics.md, "Time and duties"): the candle
## waits at a duty's mark until he does it, and the time he takes after the
## mark counts as late.
## - Up to 15 minutes: on time.
## - 15 to 45 minutes: noticed. Suspicion +5, and a remark at dawn.
## - More than 45 minutes: someone comes to fetch him (the prior, or Cole
##   at dusk), walking to wherever he is; and if he finds him somewhere he
##   shouldn't be, that counts too (being seen).
## A night with every duty on time, nothing seen and no bell rung out of
## hours takes 5 off Suspicion at dawn (clean_night).

const NOTICED := 0.25
const FETCHED := 0.75
const NOTICED_SUSPICION := 5
const CLEAN_NIGHT := 5
const FETCHER_LOOKS := {
	&"prior": preload("res://game/characters/chr_hugh.tscn"),
	&"cole": preload("res://game/characters/chr_cole.tscn"),
}


static func flag(beat: NightBeat) -> StringName:
	return GameState.tonight("late_" + String(beat.name).to_lower())


## Watches `beat` until he arrives, the beat ends, or the night is gone.
static func watch(beat: NightBeat, director: NightDirector) -> void:
	var noticed := false
	var fetched := false
	while is_instance_valid(beat) and is_instance_valid(director) and director.current == beat and not beat.is_arrived:
		var late := GameState.hour - beat.due
		if late > NOTICED and not noticed:
			noticed = true
			GameState.set_flag(flag(beat), &"noticed")
			GameState.raise_suspicion(NOTICED_SUSPICION)
			Talk.say("", "(You're late. It will have been noticed.)")
		if late > FETCHED and not fetched:
			fetched = true
			GameState.set_flag(flag(beat), &"fetched")
			Lateness.fetch.call(beat, beat.fetcher)
		await beat.get_tree().physics_frame


## The fetcher walks to wherever he is.
static func fetch(from: Node, who: StringName) -> void:
	var tree := from.get_tree()
	var p := tree.get_first_node_in_group(&"player") as Player
	if p == null:
		return
	var npc := (preload("res://game/gate/visitor_npc.tscn") as PackedScene).instantiate() as VisitorNPC
	var v := Visitor.new()
	v.look = FETCHER_LOOKS.get(who, FETCHER_LOOKS[&"prior"])
	npc.visitor = v
	npc.add_to_group(&"fetchers")
	var level := p.get_parent().get_parent()
	level.add_child(npc)
	var start := level.get_node_or_null(^"Marks/PriorFrom" if who == &"prior" else ^"Marks/ColeGate") as Node3D
	npc.global_position = start.global_position if start else p.global_position + Vector3(8, 0, 0)
	npc.follow(p)
	while is_instance_valid(npc) and is_instance_valid(p) and npc.global_position.distance_to(p.global_position) > VisitorNPC.FOLLOW_GAP + 0.4:
		await tree.physics_frame
	if not is_instance_valid(npc):
		return
	npc.stop()
	npc.face(p.global_position)
	GameState.set_flag(GameState.tonight("fetched_by_" + String(who)))
	# Found somewhere he shouldn't be: that counts too.
	for r: Node in tree.get_nodes_in_group(&"restricted"):
		var place: StringName = r.get(&"place")
		if place != &"" and r.call(&"active") and r.call(&"contains", p.global_position) and not GameState.has_flag(SeenWatch.flag(place)):
			GameState.set_flag(SeenWatch.flag(place), StringName("Hugh" if who == &"prior" else "Cole"))
			GameState.set_flag(GameState.tonight("seen_where_" + String(place)), String(r.get(&"where")))
			GameState.raise_suspicion(SeenWatch.SUSPICION)
			break
	var speaker := "Hugh" if who == &"prior" else "Cole"
	await Talk.say(speaker, "You're wanted, porter. You should have been there long since." if who == &"prior" else "(He jerks his head: come.)")


## Dawn: a clean night takes some Suspicion off.
static func clean_night() -> void:
	var prefix := String(GameState.tonight(""))
	for f: StringName in GameState.flags:
		var key := String(f)
		if key.begins_with(prefix + "late_") or key.begins_with(prefix + "seen_") or key == prefix + "bell_rung":
			return
	GameState.lower_suspicion(CLEAN_NIGHT)
	GameState.set_flag(GameState.tonight("clean"))
