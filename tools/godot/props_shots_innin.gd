extends RefCounted
## Stills of the Cross Keys from within (tools/props_shots.sh innin): the
## taproom, the loft, the porter's room, as he sees them. Most by the room's
## own light; `fill` ones check the geometry. Positions are the abbey's: the
## inn's own (x, y, z) is the abbey's (-46.4 - z, y, -2 + x). EVE is before
## the curfew bell, while the door stands open. See tools/godot/props_shots.gd.

const DAY := 15.5
const DUSK := 16.6
const EVE := 20.0
const NIGHT := 22.0
const SHOTS := [
	{"name": "door_in", "hour": EVE, "eye": Vector3(-47.30, 1.65, -2.00), "at": Vector3(-54.90, 1.20, -2.60)},
	{"name": "door_in_dusk", "hour": DUSK, "eye": Vector3(-47.30, 1.65, -2.00), "at": Vector3(-54.90, 1.20, -2.60)},
	{"name": "door_to_counter", "hour": EVE, "eye": Vector3(-47.40, 1.65, -2.30), "at": Vector3(-54.00, 1.10, 2.00)},
	{"name": "door_to_stairs", "hour": EVE, "eye": Vector3(-47.40, 1.65, -1.70), "at": Vector3(-52.40, 1.20, -6.00)},
	{"name": "hearth_back", "hour": EVE, "eye": Vector3(-54.00, 1.65, -2.80), "at": Vector3(-46.90, 1.30, -1.40)},
	{"name": "hearth_close", "hour": EVE, "eye": Vector3(-53.10, 1.50, -2.90), "at": Vector3(-55.70, 0.95, -3.00)},
	{"name": "counter_along", "hour": EVE, "eye": Vector3(-52.80, 1.65, -0.40), "at": Vector3(-55.10, 1.20, 3.00)},
	{"name": "counter_front", "hour": EVE, "eye": Vector3(-52.00, 1.65, 1.30), "at": Vector3(-55.90, 1.30, 2.00)},
	{"name": "stairs_foot", "hour": EVE, "eye": Vector3(-55.50, 1.65, -5.50), "at": Vector3(-51.90, 1.70, -7.10)},
	{"name": "taproom_from_stairs", "hour": EVE, "eye": Vector3(-54.90, 1.65, -5.90), "at": Vector3(-49.40, 1.10, -0.50)},
	{"name": "settle_table", "hour": EVE, "eye": Vector3(-49.60, 1.65, -3.20), "at": Vector3(-52.00, 0.90, -6.20)},
	{"name": "front_right", "hour": EVE, "eye": Vector3(-52.00, 1.65, -1.40), "at": Vector3(-47.80, 0.90, 2.00)},
	{"name": "loft_stair_head", "hour": EVE, "eye": Vector3(-49.60, 4.65, -7.10), "at": Vector3(-53.90, 3.60, 0.50)},
	{"name": "loft_beds", "hour": EVE, "eye": Vector3(-51.00, 4.65, -2.80), "at": Vector3(-55.00, 3.50, 1.60)},
	{"name": "loft_to_stairs", "hour": EVE, "eye": Vector3(-49.40, 4.65, 1.00), "at": Vector3(-52.60, 4.20, -6.50)},
	{"name": "top_landing", "hour": EVE, "eye": Vector3(-55.60, 7.65, -5.90), "at": Vector3(-51.40, 7.00, 0.50)},
	{"name": "room_door", "hour": EVE, "eye": Vector3(-52.00, 7.65, 1.00), "at": Vector3(-47.90, 7.00, 2.00)},
	{"name": "room_window", "hour": EVE, "eye": Vector3(-49.80, 7.65, 0.40), "at": Vector3(-46.70, 7.40, 2.10)},
	{"name": "room_bed", "hour": EVE, "eye": Vector3(-47.60, 7.65, 0.20), "at": Vector3(-49.20, 6.50, 2.60)},
	{"name": "room_window_out", "hour": EVE, "eye": Vector3(-47.30, 7.65, 2.00), "at": Vector3(-38.40, 6.40, 2.00)},
	{"name": "door_in_fill", "hour": EVE, "eye": Vector3(-47.30, 1.65, -2.00), "at": Vector3(-54.90, 1.20, -2.60), "fill": true},
	{"name": "hearth_back_fill", "hour": EVE, "eye": Vector3(-54.00, 1.65, -2.80), "at": Vector3(-46.90, 1.30, -1.40), "fill": true},
	{"name": "counter_fill", "hour": EVE, "eye": Vector3(-52.60, 1.65, 0.20), "at": Vector3(-55.40, 1.20, 2.40), "fill": true},
	{"name": "stairs_fill", "hour": EVE, "eye": Vector3(-53.80, 1.65, -5.20), "at": Vector3(-52.40, 1.60, -7.10), "fill": true},
	{"name": "loft_fill", "hour": EVE, "eye": Vector3(-49.00, 4.65, -4.60), "at": Vector3(-54.20, 3.60, 1.00), "fill": true},
	{"name": "loft_stairs_fill", "hour": EVE, "eye": Vector3(-48.60, 4.65, -1.50), "at": Vector3(-52.80, 4.20, -6.50), "fill": true},
	{"name": "top_fill", "hour": EVE, "eye": Vector3(-54.00, 7.65, -4.40), "at": Vector3(-49.40, 6.60, -6.00), "fill": true},
	{"name": "room_fill", "hour": EVE, "eye": Vector3(-50.30, 7.65, 0.30), "at": Vector3(-47.30, 6.90, 2.60), "fill": true},
	{"name": "door_in_lantern", "hour": EVE, "eye": Vector3(-47.30, 1.65, -2.00), "at": Vector3(-54.90, 1.20, -2.60), "lantern": true},
	{"name": "loft_lantern", "hour": EVE, "eye": Vector3(-51.00, 4.65, -2.80), "at": Vector3(-55.00, 3.50, 1.60), "lantern": true},
]
