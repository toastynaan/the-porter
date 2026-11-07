extends Node
## Bakes the abbey's navigation mesh into game/world/abbey/abbey_nav.res.
## Run it after changing the layout: tools/bake_nav.sh. (In the editor, the
## Navigation node's Bake NavigationMesh button does the same.)
##
## Only the WORLD layer is baked: door leaves are on their own layer, so
## doorways stay open to the hunters, and the squeezes are too low to bake.

const ABBEY := "res://game/world/abbey/abbey.tscn"
const NAV := "res://game/world/abbey/abbey_nav.res"


func _ready() -> void:
	var abbey: Node3D = load(ABBEY).instantiate()
	add_child(abbey)
	await get_tree().physics_frame
	await get_tree().physics_frame
	var region: NavigationRegion3D = abbey.get_node(^"Navigation")
	var started := Time.get_ticks_msec()
	region.bake_navigation_mesh(false)
	var mesh := region.navigation_mesh
	var err := ResourceSaver.save(mesh, NAV)
	print("baked %d polygons in %.1f s -> %s (%s)" % [
		mesh.get_polygon_count(), (Time.get_ticks_msec() - started) / 1000.0, NAV, error_string(err)])
	get_tree().quit(0 if err == OK and mesh.get_polygon_count() > 0 else 1)
