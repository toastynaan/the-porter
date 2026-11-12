extends RefCounted
## Stills of the Cross Keys with its outside and inside together, and the
## lane before it (tools/shots/props_shots.sh inn). See tools/shots/props_shots.gd.
## The lane's curfew darkens the houses by 22.0, so the evening is 20.0.

const DUSK := 16.6
const EVENING := 20.0
const SHOTS := [
	{"name": "from_the_gate", "hour": EVENING, "eye": Vector3(-40.9, 1.65, -2.0), "at": Vector3(-46.4, 3.4, -2.0)},
	{"name": "from_the_gate_dusk", "hour": DUSK, "eye": Vector3(-40.9, 1.65, -2.0), "at": Vector3(-46.4, 3.4, -2.0)},
	{"name": "door_from_the_lane", "hour": EVENING, "eye": Vector3(-42.6, 1.65, -2.6), "at": Vector3(-46.6, 1.3, -2.0)},
	{"name": "lane_north", "hour": EVENING, "eye": Vector3(-42.2, 1.65, -12.0), "at": Vector3(-45.6, 2.2, 6.0)},
	{"name": "lane_south", "hour": EVENING, "eye": Vector3(-42.2, 1.65, 8.0), "at": Vector3(-45.6, 2.4, -8.0)},
	{"name": "lane_south_lantern", "hour": EVENING, "eye": Vector3(-42.2, 1.65, 8.0), "at": Vector3(-45.6, 1.6, -8.0), "lantern": true},
	{"name": "inside_to_the_door", "hour": EVENING, "eye": Vector3(-51.4, 1.65, -3.4), "at": Vector3(-46.7, 1.3, -2.0)},
	{"name": "inside_from_the_door", "hour": EVENING, "eye": Vector3(-47.3, 1.65, -2.0), "at": Vector3(-55.0, 1.3, -3.0)},
	{"name": "inside_door_leaf", "hour": EVENING, "eye": Vector3(-49.0, 1.65, -0.4), "at": Vector3(-46.7, 1.2, -2.6)},
	{"name": "porters_window", "hour": DUSK, "eye": Vector3(-47.3, 7.65, 2.0), "at": Vector3(-40.4, 2.0, -2.0)},
	{"name": "porters_window_evening", "hour": EVENING, "eye": Vector3(-47.3, 7.65, 2.0), "at": Vector3(-40.4, 2.0, -2.0)},
	{"name": "kerb", "hour": EVENING, "eye": Vector3(-43.4, 1.65, 4.0), "at": Vector3(-45.6, 0.0, 6.5), "lantern": true},
]
