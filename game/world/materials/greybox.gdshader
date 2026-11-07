shader_type spatial;
// Greybox surface: a flat colour with faint world-space lines every metre and
// stronger ones every 4 m (the kit grid), so distances read while walking.
// The lines fade out where they would be thinner than a pixel.

render_mode diffuse_burley, specular_schlick_ggx;

uniform vec3 albedo : source_color = vec3(0.35);
uniform float roughness : hint_range(0.0, 1.0) = 0.9;
uniform float line_strength : hint_range(0.0, 1.0) = 0.18;

varying vec3 world_pos;
varying vec3 world_normal;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	world_normal = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

// 1 on a grid line `spacing` apart, about a pixel wide, 0 elsewhere.
float grid_line(vec2 p, float spacing) {
	vec2 c = p / spacing;
	vec2 w = max(fwidth(c), vec2(1e-5));
	vec2 d = abs(fract(c - 0.5) - 0.5) / w;
	float line = 1.0 - clamp(min(d.x, d.y) - 0.5, 0.0, 1.0);
	return line * (1.0 - smoothstep(0.12, 0.35, max(w.x, w.y)));
}

void fragment() {
	vec3 n = abs(world_normal);
	vec2 p = n.y > 0.5 ? world_pos.xz : (n.x > n.z ? world_pos.zy : world_pos.xy);
	float lines = max(grid_line(p, 1.0) * 0.5, grid_line(p, 4.0));
	ALBEDO = albedo * (1.0 - line_strength * lines);
	ROUGHNESS = roughness;
}
