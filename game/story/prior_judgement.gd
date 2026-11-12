class_name PriorJudgement
## The prior's judgement at dawn on night 5 (docs/systems/mechanics.md, "The
## payoff"): he arrests the porter, and believes him if he can show two
## different kinds of proof (a costume, a purse, the relic, the book) or
## has enough in his notes (6 of the clues the game can write). Believed,
## the prior lets him go himself and stands with him on night 6; otherwise
## Thomas speaks for him and takes him into his care.

const CLUES_NEEDED := 6
const KINDS_NEEDED := 2


static func proof_kinds() -> int:
	return Items.proof_kinds(GameState.satchel).size()


static func believes() -> bool:
	return proof_kinds() >= KINDS_NEEDED or Clues.written() >= CLUES_NEEDED
