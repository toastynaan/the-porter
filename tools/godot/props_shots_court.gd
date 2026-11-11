extends RefCounted
## Stills of the outer court's and the cell's props, and the plain furniture
## (tools/props_shots.sh court). See tools/godot/props_shots.gd.

const DAY := 15.5
const DUSK := 16.6
const NIGHT := 22.0
const SHOTS := [
	{"name": "cell_desk", "hour": NIGHT, "eye": Vector3(-34.9, 1.65, -10.2), "at": Vector3(-33.2, 0.8, -10.7), "lantern": true},
	{"name": "cell_desk_fill", "hour": NIGHT, "eye": Vector3(-34.9, 1.65, -10.2), "at": Vector3(-33.2, 0.8, -10.7), "fill": true},
	{"name": "cell_cot", "hour": NIGHT, "eye": Vector3(-36.6, 1.65, -9.4), "at": Vector3(-38.4, 0.4, -11.2), "lantern": true},
	{"name": "cell_door_inside", "hour": NIGHT, "eye": Vector3(-35.2, 1.65, -7.6), "at": Vector3(-34.0, 1.1, -4.0), "lantern": true},
	{"name": "well", "hour": NIGHT, "eye": Vector3(-30.6, 1.65, 2.2), "at": Vector3(-28.0, 1.3, 4.0), "lantern": true},
	{"name": "well_dusk", "hour": DUSK, "eye": Vector3(-33.0, 1.65, 0.5), "at": Vector3(-28.0, 1.3, 4.0)},
	{"name": "woodpiles", "hour": NIGHT, "eye": Vector3(-33.6, 1.65, -15.4), "at": Vector3(-36.5, 0.7, -13.2), "lantern": true},
	{"name": "gate_bench_and_bar", "hour": NIGHT, "eye": Vector3(-36.6, 1.65, 0.6), "at": Vector3(-39.6, 0.9, 0.2), "lantern": true},
	{"name": "guest_beds", "hour": NIGHT, "eye": Vector3(-31.0, 1.65, -20.0), "at": Vector3(-34.2, 0.4, -22.2), "lantern": true},
	{"name": "guest_beds_fill", "hour": NIGHT, "eye": Vector3(-29.0, 1.65, -19.0), "at": Vector3(-33.0, 0.3, -22.4), "fill": true},
	{"name": "guest_stool", "hour": NIGHT, "eye": Vector3(-28.4, 1.65, -18.6), "at": Vector3(-27.0, 0.4, -17.6), "lantern": true},
	{"name": "refectory_tables", "hour": NIGHT, "eye": Vector3(-9.6, 1.65, -0.2), "at": Vector3(-4.0, 0.7, -1.4), "lantern": true},
	{"name": "refectory_tables_fill", "hour": NIGHT, "eye": Vector3(-9.6, 1.65, -0.2), "at": Vector3(-4.0, 0.7, -1.4), "fill": true},
	{"name": "dormitory_beds", "hour": NIGHT, "eye": Vector3(16.0, 5.67, -19.0), "at": Vector3(13.6, 4.3, -24.5), "lantern": true},
	{"name": "gate_lamp", "hour": NIGHT, "eye": Vector3(-37.6, 1.65, -2.6), "at": Vector3(-39.4, 2.5, -3.75), "lantern": true},
	{"name": "chapter_benches", "hour": NIGHT, "eye": Vector3(16.4, 1.65, -20.2), "at": Vector3(19.3, 0.4, -22.5), "lantern": true},
]
