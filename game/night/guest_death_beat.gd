extends NightBeat
## The guest he let in tonight, on the round (night 4: "the guesthouse, its
## door open, on your round (seconds too late)"). If `visitor` was let in and
## not warned to bar the door from inside (from night 4 the porter's lock no
## longer helps: Saving), the death plays as he comes to the guesthouse
## (`at`, within `radius`): gory, the rite's cuts. Warned, he lives, and
## answers through the barred door. Turned away, nothing.

@export var visitor: Visitor
@export var death: DeathScene
@export var at: Marker3D
@export var radius := 5.0
@export var death_lines := PackedStringArray()
@export var barred_lines := PackedStringArray()


func run() -> void:
	var let_in: Variant = GameState.get_flag(visitor.flag, &"")
	if let_in != &"admitted" and let_in != &"prior":
		return
	var p := player()
	var way := Wayfinding.show_way(self, at.global_position)
	await until(func() -> bool: return p.global_position.distance_to(at.global_position) < radius)
	Wayfinding.put_out(way)
	if Saving.guest_safe(visitor.id, Saving.guesthouse_locked(get_tree())):
		await say_lines(barred_lines)
		return
	for n: Node in get_tree().get_nodes_in_group(&"callers"):
		var npc := n as VisitorNPC
		if npc and npc.visitor == visitor:
			npc.lying = false
			death.victim = npc
	await death.play()
	await say_lines(death_lines)
