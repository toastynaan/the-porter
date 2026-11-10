shader_type spatial;
// A lit window in a timber house: no glass, but horn or oiled cloth with a
// rushlight or a fire somewhere behind it. A dull uneven glow, warmest low
// down, never quite still; and now and then somebody inside passes between
// the light and the window. UV runs 0..1 across the pane and down it.
render_mode unshaded;

uniform vec3 glow : source_color = vec3(0.92, 0.56, 0.24);
uniform float energy = 1.25;
uniform float flicker : hint_range(0.0, 1.0) = 0.18;

varying vec3 world_pos;
varying float seed;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	vec3 origin = (MODEL_MATRIX * vec4(0.0, 0.0, 0.0, 1.0)).xyz;
	seed = fract(sin(dot(floor(origin * 4.0), vec3(12.9898, 78.233, 37.719))) * 43758.5453);
}

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float soft(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}

void fragment() {
	// The horn: cloudy, each pane its own.
	float cloud = 0.62 + 0.38 * soft(world_pos.xy * 5.0 + world_pos.z * 3.0 + seed * 40.0);
	float pool = mix(1.0, 0.5, smoothstep(0.0, 1.0, 1.0 - UV.y));
	float t = TIME + seed * 60.0;
	float breathe = 1.0 - flicker * (0.5 + 0.5 * sin(t * 6.1) * sin(t * 2.3));
	// Somebody crossing the room: a soft dark shape that comes and goes.
	float walk = fract(t * 0.035);
	float there = smoothstep(0.0, 0.05, walk) * (1.0 - smoothstep(0.25, 0.3, walk)) * step(0.45, seed);
	float body = 1.0 - there * 0.8 * (1.0 - smoothstep(0.15, 0.5, abs(UV.x - mix(-0.5, 1.5, walk / 0.3))));
	float each = mix(0.65, 1.1, seed);
	ALBEDO = glow * energy * cloud * pool * breathe * body * each;
}
