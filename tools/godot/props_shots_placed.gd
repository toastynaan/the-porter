extends RefCounted
## Stills of the props that were new in the props pass, where they were
## placed (tools/props_shots.sh placed). See tools/godot/props_shots.gd.

const NIGHT := 22.0
const DUSK := 16.6
const SHOTS := [
	{"name": "abbot_seat", "hour": NIGHT, "eye": Vector3(16.2, 1.65, -21.0), "at": Vector3(19.1, 1.0, -21.85), "lantern": true},
	{"name": "lectern", "hour": NIGHT, "eye": Vector3(7.6, 1.65, -0.8), "at": Vector3(10.6, 0.9, 0.0), "lantern": true},
	{"name": "cellar_closet", "hour": NIGHT, "eye": Vector3(-15.4, 1.65, -20.0), "at": Vector3(-18.4, 1.2, -21.5), "lantern": true},
	{"name": "crypt_rail", "hour": NIGHT, "eye": Vector3(20.0, 1.65, -30.2), "at": Vector3(24.0, 0.6, -32.6), "lantern": true},
	{"name": "churchyard_cross", "hour": NIGHT, "eye": Vector3(33.4, 1.65, -25.2), "at": Vector3(36.5, 1.6, -27.4), "lantern": true},
	{"name": "churchyard_cross_dusk", "hour": DUSK, "eye": Vector3(30.0, 1.65, -22.0), "at": Vector3(36.5, 1.8, -27.4)},
	{"name": "latrine", "hour": NIGHT, "eye": Vector3(15.0, 5.67, 16.2), "at": Vector3(16.6, 4.5, 18.6), "lantern": true},
	{"name": "warming_hearth", "hour": NIGHT, "eye": Vector3(16.2, 1.65, -8.6), "at": Vector3(19.0, 0.5, -8.0), "lantern": true},
	{"name": "cloister_saint", "hour": NIGHT, "eye": Vector3(-4.6, 1.65, -25.2), "at": Vector3(-6.0, 1.3, -27.3), "lantern": true},
	{"name": "items_court", "hour": NIGHT, "eye": Vector3(-29.2, 1.65, 0.9), "at": Vector3(-30.0, 0.05, 0.0), "lantern": true},
	{"name": "kitchen_hearth", "hour": NIGHT, "eye": Vector3(-15.2, 1.65, 0.2), "at": Vector3(-16.0, 0.9, -2.9), "lantern": true},
]
