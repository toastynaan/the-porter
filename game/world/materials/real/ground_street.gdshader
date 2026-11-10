shader_type spatial;
// The street inside Aldgate (art/models/env_aldgate_street.glb, built by
// tools/build/env_aldgate_street.py): cobbles, with mud trodden over them
// down the middle where the carts go and in drifts against the houses,
// and rain standing in every hollow. The mesh's vertex colours are masks:
// red mud, alpha standing water (the kennel down the middle). UV is
// (metres along the street, metres from its middle), for the wheel ruts.
//
// Everything is wet. The cobbles' crowns shine and the water is nearly a
// mirror, so every lantern and lit window lies along the street in pieces.
render_mode diffuse_burley, specular_schlick_ggx;

uniform sampler2D cobble_col : source_color, repeat_enable, filter_linear_mipmap_anisotropic;
uniform sampler2D cobble_nrm : hint_normal, repeat_enable, filter_linear_mipmap_anisotropic;
uniform sampler2D mud_col : source_color, repeat_enable, filter_linear_mipmap_anisotropic;
uniform sampler2D mud_nrm : hint_normal, repeat_enable, filter_linear_mipmap_anisotropic;
uniform sampler2D blotch : repeat_enable, filter_linear_mipmap;
uniform float cobble_size = 2.2;
uniform float mud_size = 3.0;
uniform vec3 cobble_tint : source_color = vec3(0.5, 0.5, 0.5);
uniform vec3 mud_tint : source_color = vec3(0.46, 0.42, 0.38);
uniform vec3 water_color : source_color = vec3(0.012, 0.014, 0.017);
uniform float rut_inner = 0.42;
uniform float rut_outer = 1.98;
uniform float rut_half = 0.17;
uniform float rain : hint_range(0.0, 1.0) = 1.0;

varying vec3 world_pos;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

float rut(float side, float at, float wobble) {
	return 1.0 - smoothstep(rut_half * 0.5, rut_half * 1.6, max(abs(abs(side) - at) + wobble, 0.0));
}

// Rings where drops strike standing water: one in each cell of a grid, each at its own moment.
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
	float big = texture(blotch, p * 0.021).r;
	float mid = texture(blotch, p * 0.11 + 0.3).r;
	float fine = texture(blotch, p * 0.7 + 0.7).r;
	vec3 cobble = texture(cobble_col, p / cobble_size).rgb * cobble_tint;
	vec3 mud = texture(mud_col, p / mud_size).rgb * mud_tint;
	// Mud lies where the mesh says and in patches of its own, and fills the cobbles' joints first.
	float joints = 1.0 - smoothstep(0.1, 0.3, dot(cobble, vec3(0.6)) / max(dot(cobble_tint, vec3(0.33)), 0.01));
	float muddy = smoothstep(0.38, 0.62, COLOR.r * 0.9 + (mid - 0.5) * 0.9 + (big - 0.5) * 0.5 + joints * 0.25);
	// The wheel ruts, as on the road outside: they come in through the gate.
	float side = UV.y + (texture(blotch, vec2(UV.x * 0.011, 0.31)).r - 0.5) * 0.5;
	float wobble = (texture(blotch, vec2(UV.x * 0.06, side * 0.3)).r - 0.5) * 0.1;
	float ruts = max(rut(side, rut_inner, wobble), rut(side, rut_outer, wobble)) * muddy;
	vec3 albedo = mix(cobble, mud, muddy) * mix(0.8, 1.12, big);
	albedo *= mix(1.0, 0.6, ruts);
	// Standing water: the kennel, the ruts' deeper lengths, hollows in the mud and between sunk cobbles.
	float deep = texture(blotch, vec2(UV.x * 0.017, side * 0.07 + 0.5)).r + (mid - 0.5) * 0.3;
	float holes = smoothstep(0.62, 0.72, texture(blotch, p * 0.047 + 0.37).r + (fine - 0.5) * 0.12);
	float water = smoothstep(0.4, 0.6, max(COLOR.a, max(ruts * smoothstep(0.42, 0.58, deep), holes)) + (mid - 0.5) * 0.25);
	vec2 r1 = texture(blotch, p * 1.7 + vec2(TIME * 0.31, TIME * 0.23)).rg;
	vec2 r2 = texture(blotch, p * 2.9 - vec2(TIME * 0.27, TIME * 0.35)).gr;
	vec2 struck = rings(p * 2.7, TIME * 1.25) + rings(p * 4.3 + 7.3, TIME * 1.05 + 0.4) * 0.7;
	vec3 n_water = normalize(vec3(((r1 + r2 - 1.0) * 0.1 + struck * 0.45) * rain, 1.0)) * 0.5 + 0.5;
	vec3 n = mix(texture(cobble_nrm, p / cobble_size).rgb, texture(mud_nrm, p / mud_size).rgb, muddy);
	float mirror = smoothstep(0.7, 1.0, water);
	ALBEDO = mix(albedo * 0.6, water_color, water * 0.94);
	// Wet stone shines more than wet mud; water most of all.
	ROUGHNESS = mix(mix(mix(0.42, 0.3, fine), mix(0.75, 0.5, fine), muddy), 0.03, mirror);
	SPECULAR = mix(0.5, 0.6, mirror) * (1.0 - clamp(water * (1.0 - mirror) * 3.0, 0.0, 1.0));
	NORMAL_MAP = mix(n, n_water, water);
	NORMAL_MAP_DEPTH = mix(1.1, 1.0, water);
	NORMAL = normalize(mix(NORMAL, (VIEW_MATRIX * vec4(0.0, 1.0, 0.0, 0.0)).xyz, water));
}
