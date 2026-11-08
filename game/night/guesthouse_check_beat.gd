extends NightBeat
## Night 2's round, the guesthouse (design doc: "the guesthouse has one more
## empty bed than your ledger says. A ledger page is gone."). If he let the
## sailor in, the sailor is gone from his bed though the gate is still
## barred, and his page has been torn from the ledger; checking the
## guesthouse, the porter sees it, and it goes in his notes. Otherwise the
## guesthouse is as he left it.

@export var check: Duty
@export var visitor: Visitor
@export var empty_lines := PackedStringArray()
@export var quiet_lines := PackedStringArray(["(The guesthouse is quiet. Everyone you wrote in is where you left them.)"])


func run() -> void:
	var let_in: Variant = GameState.get_flag(visitor.flag, &"")
	var gone: bool = let_in == &"admitted" or let_in == &"prior"
	if gone:
		for n: Node in get_tree().get_nodes_in_group(&"callers"):
			var npc := n as VisitorNPC
			if npc and npc.visitor == visitor:
				npc.set_present(false)
		GameState.tear_ledger(visitor.ledger_name)
	await check.wait_for_use()
	if gone:
		await say_lines(empty_lines)
		GameState.note(&"ledger_torn")
		GameState.set_flag(GameState.tonight("empty_bed"))
	else:
		await say_lines(quiet_lines)
