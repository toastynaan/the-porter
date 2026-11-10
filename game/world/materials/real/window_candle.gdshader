shader_type spatial;
// Glass with candles lit behind it (the white chapel at Vespers): leaded in
// small diamonds, brightest low down where the candles stand, never quite
// still. UV runs 0..1 across the pane and up it.
render_mode unshaded;

uniform vec3 glow : source_color = vec3(0.93, 0.6, 0.28);
uniform float energy = 1.5;
// Diamonds across the pane's width.
uniform float panes = 4.0;
uniform float flicker : hint_range(0.0, 1.0) = 0.22;

varying vec3 world_pos;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	vec2 uv = UV * vec2(panes, panes * 3.2);
	// The leads: two sets of slanting lines.
	float a = abs(fract(uv.x + uv.y) - 0.5);
	float b = abs(fract(uv.x - uv.y) - 0.5);
	float lead = smoothstep(0.02, 0.08, min(a, b));
	// Each pane a little different; the light pooled low; each window breathing on its own.
	vec2 cell = floor(vec2(uv.x + uv.y, uv.x - uv.y));
	float pane = 0.75 + 0.25 * fract(sin(dot(cell, vec2(12.9898, 78.233))) * 43758.5453);
	float pool = mix(1.0, 0.35, smoothstep(0.0, 0.95, UV.y));
	float seed = dot(floor(world_pos * 0.7), vec3(1.3, 2.1, 3.7));
	float breathe = 1.0 - flicker * (0.5 + 0.5 * sin(TIME * 7.3 + seed) * sin(TIME * 2.9 + seed * 1.7));
	ALBEDO = glow * energy * lead * pane * pool * breathe;
}
