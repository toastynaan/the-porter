extends RefCounted
## Stills of the lane's ground: its setts, kerbs, sidewalks and gutters, and
## the lanterns on their brackets (tools/props_shots.sh street). See
## tools/godot/props_shots.gd. Night 1: it rains.

const NIGHT_NUMBER := 1
const DAY := 15.5
const DUSK := 16.6
const NIGHT := 22.0
const SHOTS := [
	{"name": "south_night", "hour": NIGHT, "eye": Vector3(-43.7, 1.65, 2.5), "at": Vector3(-43.9, 0.9, 32.0)},
	{"name": "south_lantern", "hour": NIGHT, "eye": Vector3(-43.7, 1.65, 2.5), "at": Vector3(-43.9, 0.9, 32.0), "lantern": true},
	{"name": "south_dusk", "hour": DUSK, "eye": Vector3(-43.7, 1.65, 2.5), "at": Vector3(-43.9, 0.9, 32.0)},
	{"name": "north_night", "hour": NIGHT, "eye": Vector3(-43.2, 1.65, -6.5), "at": Vector3(-43.9, 0.9, -38.0)},
	{"name": "north_lantern", "hour": NIGHT, "eye": Vector3(-43.2, 1.65, -6.5), "at": Vector3(-43.9, 0.9, -38.0), "lantern": true},
	{"name": "north_dusk", "hour": DUSK, "eye": Vector3(-43.2, 1.65, -6.5), "at": Vector3(-43.9, 0.9, -38.0)},
	{"name": "as_the_picture_night", "hour": NIGHT, "eye": Vector3(-43.9, 1.5, -14.0), "at": Vector3(-44.5, 1.0, 20.0)},
	{"name": "as_the_picture_dusk", "hour": DUSK, "eye": Vector3(-43.9, 1.5, -14.0), "at": Vector3(-44.5, 1.0, 20.0)},
	{"name": "kerb_west_night", "hour": NIGHT, "eye": Vector3(-44.5, 1.65, 8.2), "at": Vector3(-45.5, 0.0, 9.6)},
	{"name": "kerb_west_lantern", "hour": NIGHT, "eye": Vector3(-44.5, 1.65, 8.2), "at": Vector3(-45.5, 0.0, 9.6), "lantern": true},
	{"name": "kerb_east_lantern", "hour": NIGHT, "eye": Vector3(-42.6, 1.65, -13.0), "at": Vector3(-41.3, 0.0, -10.8), "lantern": true},
	{"name": "kerb_west_dusk", "hour": DUSK, "eye": Vector3(-44.5, 1.65, 8.2), "at": Vector3(-45.5, 0.0, 9.6)},
	{"name": "gate_apron_lantern", "hour": NIGHT, "eye": Vector3(-44.7, 1.65, -7.0), "at": Vector3(-41.6, 0.2, -2.6), "lantern": true},
	{"name": "gate_apron_dusk", "hour": DUSK, "eye": Vector3(-44.7, 1.65, -7.0), "at": Vector3(-41.6, 0.2, -2.6)},
	{"name": "bend_night", "hour": NIGHT, "eye": Vector3(-42.2, 1.65, 43.6), "at": Vector3(-52.0, 0.0, 47.4)},
	{"name": "bend_lantern", "hour": NIGHT, "eye": Vector3(-42.2, 1.65, 43.6), "at": Vector3(-52.0, 0.0, 47.4), "lantern": true},
	{"name": "bend_dusk", "hour": DUSK, "eye": Vector3(-42.2, 1.65, 43.6), "at": Vector3(-52.0, 0.0, 47.4)},
	{"name": "bend_along_lantern", "hour": NIGHT, "eye": Vector3(-48.0, 1.65, 47.2), "at": Vector3(-66.0, 0.6, 47.0), "lantern": true},
	{"name": "alley_lantern", "hour": NIGHT, "eye": Vector3(-44.4, 1.65, 14.3), "at": Vector3(-50.0, -0.2, 15.1), "lantern": true},
	{"name": "alley_dusk", "hour": DUSK, "eye": Vector3(-44.4, 1.65, 14.3), "at": Vector3(-50.0, -0.2, 15.1)},
	{"name": "alley_inside_lantern", "hour": NIGHT, "eye": Vector3(-53.0, 1.65, 15.0), "at": Vector3(-44.0, 0.2, 15.0), "lantern": true},
	{"name": "bracket_night", "hour": NIGHT, "eye": Vector3(-44.5, 1.65, 6.9), "at": Vector3(-46.0, 2.75, 5.5)},
	{"name": "bracket_dusk", "hour": DUSK, "eye": Vector3(-44.3, 1.65, 3.6), "at": Vector3(-46.0, 2.75, 5.5)},
	{"name": "arch_lantern", "hour": NIGHT, "eye": Vector3(-43.4, 1.65, 45.0), "at": Vector3(-43.4, 0.6, 54.0), "lantern": true},
	{"name": "fill_kerb", "hour": NIGHT, "eye": Vector3(-44.2, 1.65, 12.0), "at": Vector3(-45.6, 0.0, 14.2), "fill": true},
	{"name": "fill_apron", "hour": NIGHT, "eye": Vector3(-44.7, 1.65, -7.0), "at": Vector3(-41.6, 0.2, -2.6), "fill": true},
	{"name": "fill_bend", "hour": NIGHT, "eye": Vector3(-44.4, 1.65, 43.0), "at": Vector3(-47.4, 0.0, 46.4), "fill": true},
	{"name": "fill_setts", "hour": NIGHT, "eye": Vector3(-43.4, 1.65, 20.0), "at": Vector3(-43.8, 0.0, 21.6), "fill": true},
	{"name": "brk_housem13", "hour": DUSK, "eye": Vector3(-43.9, 1.65, -10.2), "at": Vector3(-46.2, 2.6, -11.5), "fill": true},
	{"name": "brk_inn", "hour": DUSK, "eye": Vector3(-43.9, 1.65, -0.7), "at": Vector3(-46.2, 2.6, -2.0), "fill": true},
	{"name": "brk_house27", "hour": DUSK, "eye": Vector3(-43.9, 1.65, 30.1), "at": Vector3(-46.2, 2.6, 28.8), "fill": true},
]
