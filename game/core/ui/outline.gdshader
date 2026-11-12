shader_type spatial;
// The thin pale outline on whatever E would use (docs/mechanics.md, "Your
// hands"): the mesh drawn again as a hull a little bigger than itself, its
// back faces only, so only the rim outside the silhouette shows. It grows
// with distance, so it stays about one render pixel thick.
render_mode unshaded, cull_front, depth_draw_never, shadows_disabled, fog_disabled;

uniform vec4 color : source_color = vec4(0.85, 0.82, 0.75, 0.6);
// Thickness as a fraction of the distance from the eye.
uniform float width = 0.007;

void vertex() {
	vec4 view = MODELVIEW_MATRIX * vec4(VERTEX, 1.0);
	vec3 centre = (MODELVIEW_MATRIX * vec4(0.0, 0.0, 0.0, 1.0)).xyz;
	vec3 normal = normalize((MODELVIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
	vec3 out_dir = view.xyz - centre;
	vec3 dir = length(out_dir) > 0.0001 ? normalize(normalize(out_dir) + normal) : normal;
	view.xyz += dir * width * max(-view.z, 0.3);
	POSITION = PROJECTION_MATRIX * view;
}

void fragment() {
	ALBEDO = color.rgb;
	ALPHA = color.a;
}
