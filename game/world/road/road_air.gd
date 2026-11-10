class_name RoadAir
extends Node
## The air over the fields on the road in (night 0): distance. Out here the
## land runs to the horizon, so far things fade into the sky they stand
## against (the Environment's depth fog, with the sky's own colour behind
## it): trees toward the last light go pale and gold-edged, the city wall
## ahead a grey ghost. The abbey's nights don't have it: inside the wall it
## thins out, and it is gone by the turn into the lane. The volumetric fog
## (the lantern's haze) is the game's own and is left alone.

## How much of a far thing the fog takes, out in the fields, 0..1.
@export var density := 0.85
## Metres at which it begins and at which it is whole, and how it grows
## between (below 1: sooner; above: later).
@export var begins := 14.0
@export var whole := 230.0
@export var curve := 0.75
## How far the fog takes on the sky behind it (the rest is its own grey).
@export var aerial := 0.85
## East of `inside_x` there is none; west of `outside_x`, all of it.
@export var inside_x := -66.0
@export var outside_x := -124.0

var amount := 0.0


func _process(_delta: float) -> void:
	var env := get_viewport().find_world_3d().environment
	var p := get_tree().get_first_node_in_group(&"player") as Node3D
	if env == null or p == null:
		return
	amount = smoothstep(inside_x, outside_x, p.global_position.x)
	env.fog_enabled = amount > 0.001
	env.fog_mode = Environment.FOG_MODE_DEPTH
	env.fog_depth_begin = begins
	env.fog_depth_end = whole
	env.fog_depth_curve = curve
	env.fog_density = density * amount
	env.fog_aerial_perspective = aerial
	env.fog_sky_affect = 0.0
	env.fog_light_color = Color(0.43, 0.5, 0.59)
	env.fog_light_energy = env.background_energy_multiplier * 0.6
