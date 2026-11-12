extends RefCounted
## Stills of the working rooms' props: the stores, the granary and its closet,
## the bakehouse oven, the hearths, the latrine, the mill and its wheel, the
## infirmarer's mortar (tools/shots/props_shots.sh stores). See tools/shots/props_shots.gd.

const DAY := 15.5
const DUSK := 16.6
const NIGHT := 22.0
const SHOTS := [
	{"name": "stores", "hour": NIGHT, "eye": Vector3(-15.6, 1.7, -8.6), "at": Vector3(-19.2, 0.8, -8.0), "lantern": true},
	{"name": "stores_fill", "hour": NIGHT, "eye": Vector3(-15.6, 1.7, -8.6), "at": Vector3(-19.2, 0.8, -8.0), "fill": true},
	{"name": "stores_barrels", "hour": NIGHT, "eye": Vector3(-17.2, 1.7, -11.2), "at": Vector3(-18.8, 0.5, -9.7), "lantern": true},
	{"name": "stores_shelves", "hour": NIGHT, "eye": Vector3(-17.0, 1.7, -6.0), "at": Vector3(-19.4, 1.0, -6.0), "lantern": true},
	{"name": "granary_sacks", "hour": NIGHT, "eye": Vector3(-16.6, 1.7, -23.0), "at": Vector3(-14.5, 0.5, -26.0), "lantern": true},
	{"name": "granary_sacks_fill", "hour": NIGHT, "eye": Vector3(-16.6, 1.7, -23.0), "at": Vector3(-14.5, 0.5, -26.0), "fill": true},
	{"name": "granary_sacks_close", "hour": NIGHT, "eye": Vector3(-16.2, 1.7, -24.6), "at": Vector3(-15.2, 0.3, -26.0), "lantern": true},
	{"name": "granary_closet", "hour": NIGHT, "eye": Vector3(-14.6, 1.7, -19.6), "at": Vector3(-18.05, 1.1, -22.0), "lantern": true},
	{"name": "granary_closet_fill", "hour": NIGHT, "eye": Vector3(-14.6, 1.7, -19.6), "at": Vector3(-18.05, 1.1, -22.0), "fill": true},
	{"name": "granary_closet_inside", "hour": NIGHT, "eye": Vector3(-18.9, 1.7, -19.4), "at": Vector3(-18.6, 1.0, -24.0), "lantern": true},
	{"name": "bakehouse_oven", "hour": NIGHT, "eye": Vector3(-14.4, 1.7, 9.6), "at": Vector3(-18.0, 1.0, 8.0), "lantern": true},
	{"name": "bakehouse_oven_fill", "hour": NIGHT, "eye": Vector3(-14.4, 1.7, 9.6), "at": Vector3(-18.0, 1.0, 8.0), "fill": true},
	{"name": "bakehouse_oven_mouth", "hour": NIGHT, "eye": Vector3(-16.5, 1.25, 8.0), "at": Vector3(-18.6, 0.75, 8.0), "lantern": true},
	{"name": "bakehouse_oven_inside", "hour": NIGHT, "eye": Vector3(-18.95, 1.2, 8.0), "at": Vector3(-17.3, 0.95, 8.0), "fill": true},
	{"name": "bakehouse_bones_close", "hour": NIGHT, "eye": Vector3(-18.05, 1.02, 8.12), "at": Vector3(-18.67, 0.66, 7.8), "fill": true},
	{"name": "kitchen_hearth_close", "hour": NIGHT, "eye": Vector3(-15.3, 1.7, -0.9), "at": Vector3(-16.0, 0.6, -3.0), "lantern": true},
	{"name": "kitchen_hearth", "hour": NIGHT, "eye": Vector3(-14.6, 1.7, 0.6), "at": Vector3(-16.0, 1.0, -3.0), "lantern": true},
	{"name": "kitchen_hearth_fill", "hour": NIGHT, "eye": Vector3(-14.6, 1.7, 0.6), "at": Vector3(-16.0, 1.0, -3.0), "fill": true},
	{"name": "warming_hearth", "hour": NIGHT, "eye": Vector3(15.4, 1.7, -6.6), "at": Vector3(19.0, 0.8, -8.0), "lantern": true},
	{"name": "warming_hearth_fill", "hour": NIGHT, "eye": Vector3(15.4, 1.7, -6.6), "at": Vector3(19.0, 0.8, -8.0), "fill": true},
	{"name": "latrine_seat", "hour": NIGHT, "eye": Vector3(14.2, 5.67, 15.0), "at": Vector3(16.4, 4.5, 18.6), "lantern": true},
	{"name": "latrine_seat_fill", "hour": NIGHT, "eye": Vector3(14.2, 5.67, 15.0), "at": Vector3(16.4, 4.5, 18.6), "fill": true},
	{"name": "mill_stones", "hour": NIGHT, "eye": Vector3(25.6, 1.7, 9.6), "at": Vector3(28.0, 0.3, 12.0), "lantern": true},
	{"name": "mill_stones_fill", "hour": NIGHT, "eye": Vector3(25.6, 1.7, 9.6), "at": Vector3(28.0, 0.3, 12.0), "fill": true},
	{"name": "mill_wheel_bank", "hour": NIGHT, "eye": Vector3(26.4, 1.65, 22.6), "at": Vector3(28.0, 0.9, 18.0), "lantern": true},
	{"name": "mill_wheel_bank_fill", "hour": NIGHT, "eye": Vector3(26.4, 1.65, 22.6), "at": Vector3(28.0, 0.9, 18.0), "fill": true},
	{"name": "mill_wheel_dusk", "hour": DUSK, "eye": Vector3(23.0, 1.65, 21.4), "at": Vector3(28.0, 0.8, 18.0)},
	{"name": "mill_wheel_race", "hour": NIGHT, "eye": Vector3(24.4, 0.45, 18.0), "at": Vector3(28.0, 0.4, 18.0), "lantern": true},
	{"name": "mill_wheel_under", "hour": NIGHT, "eye": Vector3(26.2, -0.75, 18.0), "at": Vector3(28.0, -0.7, 18.0), "fill": true},
	{"name": "infirmary_mortar", "hour": NIGHT, "eye": Vector3(33.0, 1.65, -1.7), "at": Vector3(34.0, 0.85, -2.5), "lantern": true},
]
