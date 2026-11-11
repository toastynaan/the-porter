shader_type spatial;
// The brook through the city (art/models/env_city_brook.glb): black water
// sliding slowly between stone walls. It is nearly a mirror, so the
// bridge's lanterns and the lit windows over it lie on it in long broken
// streaks; the current wrinkles it and the rain rings it.
render_mode diffuse_burley, specular_schlick_ggx;

uniform sampler2D blotch : repeat_enable, filter_linear_mipmap;
uniform vec3 water_color : source_color = vec3(0.01, 0.013, 0.016);
// The way it runs and how fast, m/s.
uniform vec2 flow = vec2(0.02, 0.22);
uniform float wrinkle : hint_range(0.0, 1.0) = 0.16;
uniform float rain : hint_range(0.0, 1.0) = 1.0;

varying vec3 world_pos;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

vec2 rings(vec2 p, float t) {
	vec2 cell = floor(p);
	vec2 h = fract(sin(vec2(dot(cell, vec2(127.1, 311.7)), dot(cell, vec2(269.5, 183.3)))) * 43758.5453);
	float age = fract(t + h.x * 7.0);
	vec2 d = fract(p) - 0.5 - (h - 0.5) * 0.5;
	float r = length(d);
	float front = age * 0.42;
	float wave = sin((r - front) * 60.0) * smoothstep(0.07, 0.0, abs(r - front)) * (1.0 - age);
	return d / max(r, 0.001) * wave;
}

void fragment() {
	vec2 p = world_pos.xz;
	vec2 r1 = texture(blotch, p * vec2(0.9, 0.35) - flow * TIME * 0.9).rg;
	vec2 r2 = texture(blotch, p * vec2(2.3, 0.8) - flow * TIME * 1.7 + 0.37).gr;
	vec2 r3 = texture(blotch, p * 0.21 - flow * TIME * 0.3).rg;
	vec2 struck = rings(p * 2.3, TIME * 1.2) + rings(p * 3.7 + 5.1, TIME * 1.0 + 0.3) * 0.7;
	vec2 n = (r1 + r2 - 1.0) * wrinkle + (r3 - 0.5) * wrinkle * 0.8 + struck * 0.4 * rain;
	ALBEDO = water_color;
	ROUGHNESS = 0.04;
	SPECULAR = 0.6;
	NORMAL = normalize((VIEW_MATRIX * vec4(0.0, 1.0, 0.0, 0.0)).xyz);
	NORMAL_MAP = normalize(vec3(n, 1.0)) * 0.5 + 0.5;
	NORMAL_MAP_DEPTH = 1.0;
}
