shader_type spatial;
// The fields outside the wall (art/models/env_road_fields.glb, built by
// tools/build/env_road_fields.py). The mesh's vertex colours are masks: red
// the road's mud, green grass, blue ploughed soil, what's left stubble, and
// alpha standing water. UV is (metres along the road, metres from its
// middle), which places the wheel ruts.
//
// It has been raining: everything is dark and half-shining, and water lies
// in the ruts, the ditches and the furrows, flat and nearly a mirror, so it
// carries the sky. Rain troubles it a little.
render_mode diffuse_burley, specular_schlick_ggx;

uniform sampler2D mud_col : source_color, repeat_enable, filter_linear_mipmap_anisotropic;
uniform sampler2D mud_nrm : hint_normal, repeat_enable, filter_linear_mipmap_anisotropic;
uniform sampler2D grass_col : source_color, repeat_enable, filter_linear_mipmap_anisotropic;
uniform sampler2D grass_nrm : hint_normal, repeat_enable, filter_linear_mipmap_anisotropic;
uniform sampler2D stubble_col : source_color, repeat_enable, filter_linear_mipmap_anisotropic;
// Soft blotches, for breaking up the tiling and the edges of things.
uniform sampler2D blotch : repeat_enable, filter_linear_mipmap;
// Metres one tile of each covers.
uniform float mud_size = 3.0;
uniform float grass_size = 3.5;
uniform float stubble_size = 4.0;
uniform vec3 road_tint : source_color = vec3(0.5, 0.45, 0.4);
uniform vec3 soil_tint : source_color = vec3(0.42, 0.38, 0.35);
uniform vec3 grass_tint : source_color = vec3(0.6, 0.66, 0.5);
uniform vec3 stubble_tint : source_color = vec3(0.55, 0.52, 0.42);
uniform vec3 water_color : source_color = vec3(0.012, 0.014, 0.017);
// How wet the ground is, 0..1: darker and shinier.
uniform float wet : hint_range(0.0, 1.0) = 0.7;
// The wheel ruts: metres from the road's middle, and half their width.
uniform float rut_inner = 0.42;
uniform float rut_outer = 1.98;
uniform float rut_half = 0.17;
// Rain on the water, 0..1.
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
	vec4 mask = COLOR;
	float big = texture(blotch, p * 0.013).r;
	float mid = texture(blotch, p * 0.09 + 0.3).r;
	float fine = texture(blotch, p * 0.6 + 0.7).r;

	// Each surface at two sizes, so its tiling doesn't show across a field.
	vec3 mud = mix(texture(mud_col, p / mud_size).rgb, texture(mud_col, p / (mud_size * 3.7) + 0.4).rgb, 0.4);
	vec3 grass = mix(texture(grass_col, p / grass_size).rgb, texture(grass_col, p / (grass_size * 4.1) + 0.2).rgb, 0.45);
	vec3 stubble = texture(stubble_col, p / stubble_size).rgb;
	float w_road = mask.r;
	float w_grass = mask.g;
	float w_soil = mask.b;
	float w_stubble = clamp(1.0 - w_road - w_grass - w_soil, 0.0, 1.0);
	// The edges between them follow the ground's own grain.
	float grit = (mid - 0.5) * 0.9 + (fine - 0.5) * 0.4;
	w_road = smoothstep(0.35, 0.65, w_road + grit * 0.5);
	float rest = max(1.0 - w_road, 0.0);
	float total = max(w_grass + w_soil + w_stubble, 0.001);
	vec3 albedo = mud * road_tint * w_road
			+ (grass * grass_tint * w_grass + mud * soil_tint * w_soil + stubble * stubble_tint * w_stubble) / total * rest;
	albedo *= mix(0.8, 1.15, big);

	// Wheel ruts down the road: they wander together a little along its
	// length, and they are always dark and wet.
	float side = UV.y + (texture(blotch, vec2(UV.x * 0.011, 0.31)).r - 0.5) * 0.7;
	float wobble = (texture(blotch, vec2(UV.x * 0.06, side * 0.3)).r - 0.5) * 0.1;
	float ruts = max(rut(side, rut_inner, wobble), rut(side, rut_outer, wobble)) * w_road;
	albedo *= mix(1.0, 0.55, ruts);

	// Standing water: where the mesh says (ditches, furrows); in the ruts'
	// deeper lengths, spilling wider where it is deepest; and in holes in the
	// road. Long, uneven pools, not a pattern.
	float deep = texture(blotch, vec2(UV.x * 0.013, side * 0.06 + 0.5)).r + (mid - 0.5) * 0.35;
	float wide = max(rut(side, rut_inner, wobble - rut_half * 1.6), rut(side, rut_outer, wobble - rut_half * 1.6));
	float in_ruts = max(ruts * smoothstep(0.44, 0.6, deep), wide * smoothstep(0.6, 0.74, deep)) * w_road;
	float holes = smoothstep(0.69, 0.78, texture(blotch, vec2(UV.x * 0.043, UV.y * 0.1) + 0.37).r + (fine - 0.5) * 0.1) * w_road;
	float water = smoothstep(0.4, 0.6, max(mask.a, max(in_ruts, holes)) + grit * 0.3);

	vec3 n_mud = texture(mud_nrm, p / mud_size).rgb;
	vec3 n_grass = texture(grass_nrm, p / grass_size).rgb;
	vec3 n = mix(n_grass, n_mud, clamp(w_road + w_soil / total * rest, 0.0, 1.0));
	// Rain on the water: two drifting layers of small ripples.
	vec2 r1 = texture(blotch, p * 1.7 + vec2(TIME * 0.31, TIME * 0.23)).rg;
	vec2 r2 = texture(blotch, p * 2.9 - vec2(TIME * 0.27, TIME * 0.35)).gr;
	vec2 struck = rings(p * 2.7, TIME * 1.25) + rings(p * 4.3 + 7.3, TIME * 1.05 + 0.4) * 0.7;
	vec3 n_water = normalize(vec3(((r1 + r2 - 1.0) * 0.1 + struck * 0.45) * rain, 1.0)) * 0.5 + 0.5;

	float damp = wet * mix(0.55, 1.0, w_road + w_soil / total * rest);
	ALBEDO = mix(albedo * mix(1.0, 0.62, damp), water_color, water * 0.94);
	// Only water that is all water shines: its ragged edge stays dull.
	float mirror = smoothstep(0.7, 1.0, water);
	ROUGHNESS = mix(mix(0.96, 0.55, damp * (0.6 + 0.4 * fine)), 0.03, mirror);
	// (And its edge doesn't glint: there the surface is neither one thing nor the other.)
	SPECULAR = mix(0.4, 0.6, mirror) * (1.0 - clamp(water * (1.0 - mirror) * 3.0, 0.0, 1.0));
	NORMAL_MAP = mix(n, n_water, water);
	NORMAL_MAP_DEPTH = mix(0.8, 1.0, water);
	// Water lies level, whatever the ground under it does.
	NORMAL = normalize(mix(NORMAL, (VIEW_MATRIX * vec4(0.0, 1.0, 0.0, 0.0)).xyz, water));
}
