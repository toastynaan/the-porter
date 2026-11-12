class_name Saving
## The rules a careful porter can learn for saving people (docs/systems/mechanics.md,
## "Saving people"; docs/log/full-game-run.md, "Choices decide who dies"). Each
## night's death beats ask these, and the lane's talk at the next dusk says
## what would have saved them (Rumours).
## - Nights 1-3: lock the guesthouse once the guests are in bed, and the cult
##   can't reach them.
## - From night 4 the porter's keys have been copied (night 3's dawn), so the
##   lock no longer helps: only a guest warned to bar the door from inside
##   lives.
## - Turned away before the curfew bell, a visitor goes to the Cross Keys and
##   lives; after it the inn is shut and he's out in the lane.

## The curfew bell, nine o'clock.
const CURFEW := 21.0
## From this night a locked guesthouse no longer keeps anyone safe.
const KEYS_COPIED_FROM := 4


static func turned_away_fate(hour: float) -> StringName:
	return &"cross_keys" if hour < CURFEW else &"lane"


## Whether a guest `who` in the guesthouse lives through tonight.
static func guest_safe(who: StringName, locked: bool) -> bool:
	if Warnings.warned(who):
		return true
	return locked and GameState.night < KEYS_COPIED_FROM


## The guesthouse door is locked now (a door with the "guesthouse" key).
static func guesthouse_locked(tree: SceneTree) -> bool:
	for d: Door in tree.get_nodes_in_group(&"doors"):
		if d.key == &"guesthouse":
			return d.locked and not d.is_open
	return false
