extends RefCounted
## Stills of the graveyard's, the charnel house's and the gardens' props
## (tools/props_shots.sh yard). See tools/godot/props_shots.gd.

const DAY := 15.5
const DUSK := 16.6
const NIGHT := 22.0
const SHOTS := [
	{"name": "graves_dusk", "hour": DUSK, "eye": Vector3(20.0, 1.65, -20.5), "at": Vector3(27.0, 0.2, -16.0)},
	{"name": "graves_lantern", "hour": NIGHT, "eye": Vector3(24.4, 1.65, -19.4), "at": Vector3(27.0, 0.1, -16.4), "lantern": true},
	{"name": "graves_north_dusk", "hour": DUSK, "eye": Vector3(28.0, 1.65, -28.6), "at": Vector3(34.0, 0.2, -35.0)},
	{"name": "graves_north_lantern", "hour": NIGHT, "eye": Vector3(31.8, 1.65, -33.4), "at": Vector3(34.6, 0.1, -35.8), "lantern": true},
	{"name": "graves_north_fill", "hour": NIGHT, "eye": Vector3(28.0, 1.65, -28.6), "at": Vector3(34.0, 0.2, -35.0), "fill": true},
	{"name": "charnel_inside", "hour": NIGHT, "eye": Vector3(34.2, 1.7, -19.2), "at": Vector3(39.0, 0.75, -20.4), "lantern": true},
	{"name": "charnel_along", "hour": NIGHT, "eye": Vector3(36.6, 1.7, -17.0), "at": Vector3(38.5, 0.8, -21.5), "lantern": true},
	{"name": "charnel_gap", "hour": NIGHT, "eye": Vector3(36.6, 1.7, -21.6), "at": Vector3(38.6, 0.5, -21.0), "lantern": true},
	{"name": "charnel_hiding", "hour": NIGHT, "eye": Vector3(39.1, 0.4, -21.0), "at": Vector3(36.0, 0.6, -20.6), "fill": true},
	{"name": "charnel_fill", "hour": NIGHT, "eye": Vector3(33.6, 1.7, -20.0), "at": Vector3(39.0, 0.7, -20.0), "fill": true},
	{"name": "garden_dusk", "hour": DUSK, "eye": Vector3(-5.0, 1.65, 24.6), "at": Vector3(3.0, 0.1, 30.0)},
	{"name": "garden_lantern", "hour": NIGHT, "eye": Vector3(-0.7, 1.65, 31.0), "at": Vector3(1.0, 0.1, 28.2), "lantern": true},
	{"name": "garden_fill", "hour": NIGHT, "eye": Vector3(-4.0, 1.65, 31.0), "at": Vector3(4.0, 0.1, 30.5), "fill": true},
]
