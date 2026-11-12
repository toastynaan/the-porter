class_name Routine
extends Node
## A brother's routine by the hour (docs/systems/mechanics.md, "Routines"; design doc,
## "Everyone keeps a routine you can see"): where he goes through the night,
## walking there in view. Each Marker3D child is a stop, with metadata:
## - "hour": from when he goes there (the night's hours: 21.0 is nine, 25.0
##   is one in the morning);
## - "light" (NodePath, optional): a candle lit while he's there (lit
##   windows show who's up);
## - "lock" (NodePath, optional): a door he locks when he gets there
##   (Osric locks the cellar at nine);
## - "away" (bool, optional): he goes in and is out of sight (asleep in the
##   dormitory).
## Places/<Phase>/<Name> markers, where a night has them, come first: his
## routine is what he does the rest of the night.

## The stop for `hour`: the last one whose hour has come, or null.
func stop_for(hour: float) -> Marker3D:
	var best: Marker3D = null
	var best_hour := -INF
	for c in get_children():
		var m := c as Marker3D
		if m == null:
			continue
		var h := float(m.get_meta(&"hour", 0.0))
		if h <= hour and h > best_hour:
			best_hour = h
			best = m
	return best


func stops() -> Array[Marker3D]:
	var out: Array[Marker3D] = []
	for c in get_children():
		if c is Marker3D:
			out.append(c)
	return out
