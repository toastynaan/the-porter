class_name Warnings
## Warning someone (docs/mechanics.md, "Warnings"): a guest to bar the
## guesthouse door or leave at first light, a brother to stay in the
## dormitory. A warning given before that night's death saves them, and the
## count is short by one (a death beat checks warned()). If the cult hears of
## it, Suspicion +15: when Ranulf is within EARSHOT as he says it, or when the
## one he warned trusts Thomas more than him and tells him: a brother who
## trusts the porter less than TRUSTED, or anyone who distrusts him.

const OVERHEARD := 15
const EARSHOT := 8.0
const TRUSTED := 30


static func give(who: StringName, node: Node3D = null) -> void:
	if who == &"":
		return
	GameState.set_flag(GameState.tonight("warned_" + String(who)))
	var tree := node.get_tree() if node else Engine.get_main_loop() as SceneTree
	var told := GameState.trust_of(who) < (TRUSTED if People.BROTHERS.has(who) else 0)
	if overheard(tree) or told:
		GameState.set_flag(GameState.tonight("warning_heard_" + String(who)))
		GameState.raise_suspicion(OVERHEARD)


static func warned(who: StringName) -> bool:
	return GameState.has_flag(GameState.tonight("warned_" + String(who)))


## Ranulf is near enough to hear.
static func overheard(tree: SceneTree) -> bool:
	var p := tree.get_first_node_in_group(&"player") as Player
	if p == null:
		return false
	for b: Brother in tree.get_nodes_in_group(&"brothers"):
		if String(b.name).to_lower() == "ranulf" and b.visible and b.global_position.distance_to(p.global_position) < EARSHOT:
			return true
	return false
