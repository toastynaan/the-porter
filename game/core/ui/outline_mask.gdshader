shader_type spatial;
// The first pass of the outline on whatever E would use (game/core/ui/outline.gd):
// it draws nothing, but marks every pixel the thing covers in the stencil, all
// its parts together, seen or hidden (no depth test: a snapped or hidden part
// marks its pixels too). Its next pass, outline.gdshader, draws only where
// nothing is marked, so the outline goes round the thing's whole silhouette,
// never between its parts.
render_mode unshaded, cull_disabled, depth_draw_never, depth_test_disabled, shadows_disabled, fog_disabled;
stencil_mode write, compare_always, 1;

void fragment() {
	ALBEDO = vec3(0.0);
	ALPHA = 0.0;
}
