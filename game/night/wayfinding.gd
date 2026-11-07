class_name Wayfinding
## Lights the way to a duty without a HUD. Along the navmesh path from the
## porter to it, every unlocked door is opened and a lit lamp is hung over
## the doorway on the duty's side, so each doorway glows toward the next.
## Doors and lamps the porter is looking at are left alone: nothing opens or
## lights in front of him. The caller puts the lamps out (put_out) once the
## duty is done.

const LAMP := preload("res://game/world/props/lamp.tscn")
## Lamp position over a doorway: height, and distance out from the wall's centre.
const LAMP_HEIGHT := 2.35
const LAMP_OUT := 0.5


## Opens the doors between the porter and `to` and lights a lamp over each.
## Returns the lamps.
static func show_way(from: Node, to: Vector3) -> Array[Node3D]:
	var lamps: Array[Node3D] = []
	var player := from.get_tree().get_first_node_in_group(&"player") as Player
	if player == null:
		return lamps
	var path := NavigationServer3D.map_get_path(player.get_world_3d().navigation_map, player.global_position, to, true)
	for door: Door in from.get_tree().get_nodes_in_group(&"doors"):
		if door.locked or ViewCheck.on_screen(player.camera, [door.global_position + Vector3.UP * 1.0]):
			continue
		for i in range(1, path.size()):
			if door.crosses(path[i - 1] + Vector3.UP, path[i] + Vector3.UP):
				if not door.is_open:
					door.set_open(true, true)
				var side := signf((door.global_transform.affine_inverse() * to).z)
				var lamp := LAMP.instantiate() as Node3D
				lamp.position = Vector3(0.0, LAMP_HEIGHT, side * LAMP_OUT)
				door.add_child(lamp)
				lamps.append(lamp)
				break
	return lamps


static func put_out(lamps: Array[Node3D]) -> void:
	for lamp in lamps:
		if is_instance_valid(lamp):
			lamp.queue_free()
	lamps.clear()
