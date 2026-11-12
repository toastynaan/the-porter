extends RefCounted
## Stills of the church's props where they stand: choir stalls, the high
## altar, the open tomb, the carved saints, the crypt's shrine and its
## stair's rail, the bell and its rope; the abbot's seat and the lectern
## (tools/shots/props_shots.sh church). See tools/shots/props_shots.gd.

const DAY := 15.5
const DUSK := 16.6
const NIGHT := 22.0
const SHOTS := [
	{"name": "choir_north", "hour": NIGHT, "eye": Vector3(9.4, 1.65, -31.6), "at": Vector3(12.6, 0.8, -34.9), "lantern": true},
	{"name": "choir_north_fill", "hour": NIGHT, "eye": Vector3(9.4, 1.65, -31.6), "at": Vector3(12.6, 0.8, -34.9), "fill": true},
	{"name": "choir_south_close", "hour": NIGHT, "eye": Vector3(12.4, 1.65, -31.0), "at": Vector3(13.6, 0.9, -29.2), "lantern": true},
	{"name": "choir_stall_desk", "hour": NIGHT, "eye": Vector3(11.6, 1.65, -33.6), "at": Vector3(11.4, 0.9, -34.8), "lantern": true},
	{"name": "choir_long", "hour": NIGHT, "eye": Vector3(8.6, 1.65, -32.0), "at": Vector3(20.0, 1.0, -32.0), "lantern": true},
	{"name": "altar", "hour": NIGHT, "eye": Vector3(23.4, 1.65, -31.2), "at": Vector3(26.4, 0.8, -32.0), "lantern": true},
	{"name": "altar_fill", "hour": NIGHT, "eye": Vector3(23.4, 1.65, -31.2), "at": Vector3(26.4, 0.8, -32.0), "fill": true},
	{"name": "altar_near", "hour": NIGHT, "eye": Vector3(24.8, 1.65, -32.9), "at": Vector3(26.4, 0.6, -32.2), "lantern": true},
	{"name": "tomb", "hour": NIGHT, "eye": Vector3(-1.8, 1.65, -32.2), "at": Vector3(-3.8, 0.6, -34.6), "lantern": true},
	{"name": "tomb_fill", "hour": NIGHT, "eye": Vector3(-1.8, 1.65, -32.2), "at": Vector3(-3.8, 0.6, -34.6), "fill": true},
	{"name": "tomb_west", "hour": NIGHT, "eye": Vector3(-6.4, 1.65, -32.6), "at": Vector3(-4.2, 0.5, -34.5), "lantern": true},
	{"name": "saint_nave", "hour": NIGHT, "eye": Vector3(-11.0, 1.65, -31.4), "at": Vector3(-12.0, 1.3, -28.9), "lantern": true},
	{"name": "saint_nave_near", "hour": NIGHT, "eye": Vector3(-11.6, 1.65, -30.2), "at": Vector3(-12.0, 1.55, -28.9), "lantern": true},
	{"name": "saint_choir", "hour": NIGHT, "eye": Vector3(16.8, 1.65, -33.0), "at": Vector3(18.0, 1.3, -35.3), "lantern": true},
	{"name": "saint_cloister", "hour": NIGHT, "eye": Vector3(-4.6, 1.65, -25.4), "at": Vector3(-6.0, 1.3, -27.7), "lantern": true},
	{"name": "saint_cloister_south", "hour": NIGHT, "eye": Vector3(4.8, 1.65, -7.4), "at": Vector3(6.0, 1.3, -4.9), "lantern": true},
	{"name": "reliquary", "hour": NIGHT, "eye": Vector3(24.0, -2.35, -31.2), "at": Vector3(26.4, -3.3, -32.0), "lantern": true},
	{"name": "reliquary_fill", "hour": NIGHT, "eye": Vector3(24.0, -2.35, -31.2), "at": Vector3(26.4, -3.3, -32.0), "fill": true},
	{"name": "bell_rope", "hour": NIGHT, "eye": Vector3(-22.0, 1.65, -30.4), "at": Vector3(-24.0, 0.9, -32.0), "lantern": true},
	{"name": "bell_from_below", "hour": NIGHT, "eye": Vector3(-22.6, 1.65, -30.8), "at": Vector3(-24.0, 9.6, -32.0), "lantern": true},
	{"name": "bell_from_below_fill", "hour": NIGHT, "eye": Vector3(-22.6, 5.0, -30.8), "at": Vector3(-24.0, 10.0, -32.0), "fill": true},
	{"name": "bell_near_fill", "hour": NIGHT, "eye": Vector3(-21.6, 9.3, -30.0), "at": Vector3(-24.0, 10.3, -32.0), "fill": true},
	{"name": "rail", "hour": NIGHT, "eye": Vector3(19.6, 1.65, -31.6), "at": Vector3(22.0, 0.5, -34.2), "lantern": true},
	{"name": "abbot_seat", "hour": NIGHT, "eye": Vector3(16.2, 1.65, -20.2), "at": Vector3(19.2, 1.1, -21.85), "lantern": true},
	{"name": "lectern", "hour": NIGHT, "eye": Vector3(8.2, 1.65, -1.3), "at": Vector3(10.6, 0.9, 0.0), "lantern": true},
	{"name": "rail_fill", "hour": NIGHT, "eye": Vector3(19.6, 1.65, -31.6), "at": Vector3(22.0, 0.5, -34.2), "fill": true},
]
