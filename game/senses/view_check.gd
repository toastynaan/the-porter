class_name ViewCheck
## Whether a camera can see a point: inside the frustum and not behind a
## wall or a closed door.

const BLOCKERS := Layers.WORLD | Layers.DOOR


## True when any of `points` is in view of `camera`.
static func on_screen(camera: Camera3D, points: Array[Vector3]) -> bool:
	for p in points:
		if camera.is_position_in_frustum(p) and clear(camera, camera.global_position, p):
			return true
	return false


## True when nothing solid lies between `from` and `to`.
static func clear(node: Node3D, from: Vector3, to: Vector3) -> bool:
	var query := PhysicsRayQueryParameters3D.create(from, to, BLOCKERS)
	return node.get_world_3d().direct_space_state.intersect_ray(query).is_empty()


## Angle in degrees between the camera's view direction and `point`.
static func off_centre(camera: Camera3D, point: Vector3) -> float:
	var forward := -camera.global_basis.z
	return rad_to_deg(forward.angle_to(point - camera.global_position))
