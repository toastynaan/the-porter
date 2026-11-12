extends NightBeat
## The cult comes for a guest in the small hours (docs/systems/mechanics.md, "Saving
## people"; night 1: the merchant). At `hour`, if the porter let `guest` in
## (his Visitor flag is admitted, or prior), and nothing keeps him safe
## (Saving.guest_safe: the guesthouse locked on nights 1-3, or warned to bar
## the door), he's gone from his bed: died_<guest>, and his death feeds the
## rite. Nothing is seen; the porter finds out at dawn. Whether the
## guesthouse was locked is kept (n<night>_guesthouse_locked) for the lane's
## talk at the next dusk.

@export var hour := 25.5
## The Visitor's flag and id.
@export var visitor_flag := &"n1_merchant"
@export var guest := &"merchant"


func run() -> void:
	await clock().wait_until(hour)
	var let_in: Variant = GameState.get_flag(visitor_flag, &"")
	if let_in != &"admitted" and let_in != &"prior":
		return
	var locked := Saving.guesthouse_locked(get_tree())
	if locked:
		GameState.set_flag(GameState.tonight("guesthouse_locked"))
	if Saving.guest_safe(guest, locked):
		GameState.set_flag(GameState.tonight(String(guest) + "_safe"))
		return
	for n: Node in get_tree().get_nodes_in_group(&"callers"):
		var npc := n as VisitorNPC
		if npc and npc.visitor and npc.visitor.id == guest:
			npc.set_present(false)
	GameState.set_flag(StringName("died_" + String(guest)))
	GameState.feed_rite(guest)
