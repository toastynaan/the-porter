shader_type spatial;
// A flame on an upright sheet (a brazier's fire): tongues that rise, narrow
// and break off, brightest at the root. UV runs 0..1 across the sheet and
// down it (as a model's does once it is in the game). It adds its light to what is behind it.
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, shadows_disabled;

uniform sampler2D noise : repeat_enable, filter_linear_mipmap;
uniform vec3 hot : source_color = vec3(1.0, 0.74, 0.36);
uniform vec3 cool : source_color = vec3(0.85, 0.22, 0.04);
uniform float energy = 1.6;
uniform float speed = 1.0;

varying float seed;

void vertex() {
	seed = fract(dot(NORMAL, vec3(3.1, 0.0, 7.7)));
}

void fragment() {
	float t = TIME * speed;
	vec2 uv = vec2(UV.x, 1.0 - UV.y);
	float n1 = texture(noise, vec2(uv.x * 0.8 + seed, uv.y * 0.6 - t * 0.55)).r;
	float n2 = texture(noise, vec2(uv.x * 1.9 + 0.3 + seed, uv.y * 1.3 - t * 1.05)).r;
	float n = n1 * 0.62 + n2 * 0.38;
	float x = abs(uv.x - 0.5 + (n1 - 0.5) * 0.25 * uv.y) * 2.0;
	float width = mix(0.8, 0.08, pow(uv.y, 0.75));
	float body = 1.0 - smoothstep(width * 0.45, width, x + (n - 0.5) * 0.45);
	float tongue = smoothstep(uv.y * 1.1 - 0.2, uv.y * 1.1 + 0.2, n + 0.42 * (1.0 - uv.y));
	float a = body * tongue * smoothstep(0.0, 0.1, uv.y);
	ALBEDO = mix(cool, hot, clamp(a * 1.5 - uv.y * 0.7, 0.0, 1.0)) * energy;
	ALPHA = a;
}
