extends Node3D
## Renders a plan view of the abbey: roofs hidden, flat light, no fog, an
## orthographic camera looking straight down, the baked navmesh drawn over
## it in blue. Writes art/_review/abbey/topdown.png (tools/shots/topdown.sh).

const ABBEY := "res://game/world/abbey/abbey.tscn"
const OUT := "res://art/_review/abbey/topdown.png"
const SIZE := 1080


func _ready() -> void:
	var abbey: Node3D = load(ABBEY).instantiate()
	add_child(abbey)
	abbey.get_node(^"Player").queue_free()
	abbey.get_node(^"Wind").queue_free()
	for node in abbey.find_children("Roofs", "Node3D", true, false):
		node.visible = false
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.12, 0.12, 0.12)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color.WHITE
	env.ambient_light_energy = 0.6
	(abbey.get_node(^"WorldEnvironment") as WorldEnvironment).environment = env
	var moon: DirectionalLight3D = abbey.get_node(^"Moon")
	moon.light_color = Color.WHITE
	moon.light_energy = 0.9
	moon.basis = Basis.looking_at(Vector3(0.3, -1.0, -0.4).normalized())
	var cam := Camera3D.new()
	cam.projection = Camera3D.PROJECTION_ORTHOGONAL
	cam.size = 84.0
	cam.far = 200.0
	add_child(cam)
	cam.look_at_from_position(Vector3(0, 60, 0), Vector3.ZERO, Vector3.FORWARD)
	cam.current = true
	_draw_navmesh(abbey.get_node(^"Navigation") as NavigationRegion3D)
	for i in 30:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT).get_base_dir())
	img.save_png(ProjectSettings.globalize_path(OUT))
	print("wrote ", OUT, " ", img.get_size())
	get_tree().quit()


func _draw_navmesh(region: NavigationRegion3D) -> void:
	var nav := region.navigation_mesh
	var verts := nav.get_vertices()
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in nav.get_polygon_count():
		var poly := nav.get_polygon(i)
		for k in range(1, poly.size() - 1):
			for idx in [poly[0], poly[k], poly[k + 1]]:
				st.add_vertex(verts[idx] + Vector3.UP * 0.05)
	var mi := MeshInstance3D.new()
	mi.mesh = st.commit()
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.albedo_color = Color(0.2, 0.5, 1.0, 0.35)
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat.no_depth_test = false
	mi.material_override = mat
	add_child(mi)
