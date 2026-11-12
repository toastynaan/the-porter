extends RefCounted
## Stills of the Cross Keys from the lane, and out of the porter's window
## (tools/props_shots.sh innout). See tools/godot/props_shots.gd. The
## windows are lit until the curfew (21.0), so the lit stills come first:
## once it has rung they stay dark. Night 1: it rains.

const NIGHT_NUMBER := 1
const DUSK := 16.6
const EVENING := 20.0
const NIGHT := 22.0
const SHOTS := [
	{"name": "square_dusk", "hour": DUSK, "eye": Vector3(-40.9, 1.65, -2.0), "at": Vector3(-46.4, 4.6, -2.0)},
	{"name": "up_dusk", "hour": DUSK, "eye": Vector3(-40.9, 1.65, -2.0), "at": Vector3(-46.4, 8.6, -2.0)},
	{"name": "north_dusk", "hour": DUSK, "eye": Vector3(-41.0, 1.6, -10.5), "at": Vector3(-46.9, 5.2, -2.5)},
	{"name": "south_dusk", "hour": DUSK, "eye": Vector3(-41.2, 1.65, 9.5), "at": Vector3(-46.9, 5.2, -0.5)},
	{"name": "far_dusk", "hour": DUSK, "eye": Vector3(-42.0, 1.65, -24.0), "at": Vector3(-46.8, 6.0, -2.0)},
	{"name": "window_dusk", "hour": DUSK, "eye": Vector3(-47.3, 7.65, 2.0), "at": Vector3(-40.4, 2.0, -2.0)},
	{"name": "window_played_dusk", "hour": DUSK, "eye": Vector3(-47.3, 7.65, 2.0), "at": Vector3(-37.3, 4.78, 2.0)},
	{"name": "top_dusk", "hour": DUSK, "eye": Vector3(-41.0, 1.65, 0.6), "at": Vector3(-45.7, 7.2, 1.9)},
	{"name": "square_evening", "hour": EVENING, "eye": Vector3(-40.9, 1.65, -2.0), "at": Vector3(-46.4, 4.6, -2.0)},
	{"name": "up_evening", "hour": EVENING, "eye": Vector3(-40.9, 1.65, -2.0), "at": Vector3(-46.4, 8.6, -2.0)},
	{"name": "north_evening", "hour": EVENING, "eye": Vector3(-41.0, 1.6, -10.5), "at": Vector3(-46.9, 5.2, -2.5)},
	{"name": "south_evening", "hour": EVENING, "eye": Vector3(-41.2, 1.65, 9.5), "at": Vector3(-46.9, 5.2, -0.5)},
	{"name": "far_evening", "hour": EVENING, "eye": Vector3(-42.0, 1.65, -24.0), "at": Vector3(-46.8, 6.0, -2.0)},
	{"name": "jetties_evening", "hour": EVENING, "eye": Vector3(-44.8, 1.65, -6.0), "at": Vector3(-47.0, 5.6, -1.5)},
	{"name": "door_evening", "hour": EVENING, "eye": Vector3(-43.4, 1.65, -2.8), "at": Vector3(-46.4, 1.5, -2.0)},
	{"name": "sign_evening", "hour": EVENING, "eye": Vector3(-43.6, 1.65, -8.0), "at": Vector3(-45.0, 4.6, -3.75)},
	{"name": "window_evening", "hour": EVENING, "eye": Vector3(-47.3, 7.65, 2.0), "at": Vector3(-40.4, 2.0, -2.0)},
	{"name": "window_played_evening", "hour": EVENING, "eye": Vector3(-47.3, 7.65, 2.0), "at": Vector3(-37.3, 4.78, 2.0)},
	{"name": "top_fill", "hour": EVENING, "eye": Vector3(-41.0, 1.65, 0.6), "at": Vector3(-45.7, 7.2, 1.9), "fill": true},
	{"name": "square_fill", "hour": EVENING, "eye": Vector3(-40.9, 1.65, -2.0), "at": Vector3(-46.4, 4.6, -2.0), "fill": true},
	{"name": "north_fill", "hour": EVENING, "eye": Vector3(-41.0, 1.6, -10.5), "at": Vector3(-46.9, 5.2, -2.5), "fill": true},
	{"name": "jetties_fill", "hour": EVENING, "eye": Vector3(-44.8, 1.65, -6.0), "at": Vector3(-47.0, 5.6, -1.5), "fill": true},
	{"name": "door_fill", "hour": EVENING, "eye": Vector3(-43.4, 1.65, -2.8), "at": Vector3(-46.4, 1.5, -2.0), "fill": true},
	{"name": "square_lantern", "hour": NIGHT, "eye": Vector3(-41.0, 1.65, -2.0), "at": Vector3(-46.4, 4.6, -2.0), "lantern": true},
	{"name": "north_lantern", "hour": NIGHT, "eye": Vector3(-41.0, 1.6, -10.5), "at": Vector3(-46.9, 5.2, -2.5), "lantern": true},
	{"name": "door_lantern", "hour": NIGHT, "eye": Vector3(-43.4, 1.65, -2.8), "at": Vector3(-46.4, 1.5, -2.0), "lantern": true},
	{"name": "jetties_lantern", "hour": NIGHT, "eye": Vector3(-44.8, 1.65, -6.0), "at": Vector3(-47.0, 5.6, -1.5), "lantern": true},
]
