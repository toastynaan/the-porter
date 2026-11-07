class_name Earshot
## Sounds the hunters can hear. Anything loud calls Earshot.make() with how
## far it carries (its earshot, m); every node in the "listeners" group gets
## hear(). Walls halve the distance (the listener checks). Radii, m (M2
## report defaults where it gave one):

const RUN := 12.0
const WALK := 4.0
const DOOR := 10.0
## A held breath running out.
const GASP := 10.0
## Breathing, heard only up close.
const BREATH := 2.0
## A hiding spot at noise 1 (bones, logs) is as loud as a door.
const SPOT := 10.0
const KEY := 4.0


## `source` is what made it (a hiding spot, a door, the player), or null.
static func make(from: Node, at: Vector3, radius: float, source: Node = null) -> void:
	if radius > 0.0 and from.is_inside_tree():
		from.get_tree().call_group(&"listeners", &"hear", at, radius, source)
