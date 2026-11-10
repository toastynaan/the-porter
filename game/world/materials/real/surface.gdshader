shader_type spatial;
// Stone, plaster, timber and roofs of the city (the wall, Aldgate, the
// houses inside it). One shader, many materials: each gives it two
// surfaces and says how they wear.
//
// - Surface A is the wall as built. Surface B is what shows where it has
//   failed or been mended: bare daub under fallen limewash, mossed stone
//   in a rubble wall, grey weathered oak. B shows in patches of its own
//   (`patches`) and wherever the model asks for it: a vertex's alpha
//   under 1 is that much B. The edge between them is ragged.
// - Both are laid on by the world's axes (so pieces of a building line up
//   without UVs), or by the mesh's UV for a roof (`by_uv`).
// - Nothing is one flat colour over a long wall: slow blotches lighten
//   and darken it (`uneven`).
// - Moss comes up from the ground and lies on ledges (`moss`).
// - Rain: what faces the sky is dark and shines, walls are streaked where
//   it runs down them, undersides stay dry (`wet`).
// The vertex colour's rgb multiplies the colour, as on the old materials.
render_mode diffuse_burley, specular_schlick_ggx;

uniform sampler2D col_a : source_color, repeat_enable, filter_linear_mipmap_anisotropic;
uniform sampler2D nrm_a : hint_normal, repeat_enable, filter_linear_mipmap_anisotropic;
uniform float size_a = 3.0;
uniform vec3 tint_a : source_color = vec3(0.6);
uniform sampler2D col_b : source_color, repeat_enable, filter_linear_mipmap_anisotropic;
uniform sampler2D nrm_b : hint_normal, repeat_enable, filter_linear_mipmap_anisotropic;
uniform float size_b = 3.0;
uniform vec3 tint_b : source_color = vec3(0.6);
uniform float patches : hint_range(0.0, 1.0) = 0.0;
uniform float patch_size = 5.0;
uniform sampler2D blotch : repeat_enable, filter_linear_mipmap;
uniform float uneven : hint_range(0.0, 1.0) = 0.3;
uniform vec3 moss_tint : source_color = vec3(0.17, 0.2, 0.1);
uniform float moss : hint_range(0.0, 1.0) = 0.0;
uniform float moss_height = 2.5;
uniform float wet : hint_range(0.0, 1.0) = 0.7;
uniform float rough = 0.92;
uniform float rough_wet = 0.4;
uniform float bump = 1.0;
uniform bool by_uv = false;

varying vec3 world_pos;
varying vec3 world_normal;
varying vec3 weights;

void vertex() {
	vec3 n = normalize(MODEL_NORMAL_MATRIX * NORMAL);
	world_normal = n;
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	if (!by_uv) {
		vec3 t = vec3(0.0, 0.0, -1.0) * abs(n.x) + vec3(1.0, 0.0, 0.0) * abs(n.y) + vec3(1.0, 0.0, 0.0) * abs(n.z);
		vec3 b = vec3(0.0, 1.0, 0.0) * abs(n.x) + vec3(0.0, 0.0, -1.0) * abs(n.y) + vec3(0.0, 1.0, 0.0) * abs(n.z);
		mat3 back = inverse(MODEL_NORMAL_MATRIX);
		TANGENT = back * normalize(t);
		BINORMAL = back * normalize(b);
	}
	vec3 w = pow(abs(n), vec3(4.0));
	weights = w / dot(w, vec3(1.0));
}

vec4 lay(sampler2D tex, vec3 p, vec3 w, vec2 uv) {
	if (by_uv) {
		return texture(tex, uv);
	}
	p *= vec3(1.0, -1.0, 1.0);
	return texture(tex, p.xy) * w.z + texture(tex, p.xz) * w.y + texture(tex, p.zy * vec2(-1.0, 1.0)) * w.x;
}

void fragment() {
	vec3 p = world_pos;
	// Noise over a wall or a floor alike: one axis along it, one up it or across.
	vec2 q = vec2(p.x + p.z * 0.71, p.y + p.z * 0.37 - p.x * 0.21);
	float big = texture(blotch, q * 0.023).r;
	float mid = texture(blotch, q * (0.55 / patch_size) + 0.37).r;
	float fine = texture(blotch, q * 0.9 + 0.11).r;
	vec3 a = lay(col_a, p / size_a, weights, UV).rgb * tint_a;
	vec3 b = lay(col_b, p / size_b, weights, UV * size_a / size_b).rgb * tint_b;
	vec3 na = lay(nrm_a, p / size_a, weights, UV).rgb;
	vec3 nb = lay(nrm_b, p / size_b, weights, UV * size_a / size_b).rgb;
	// Where B shows: asked for by the mesh, or in patches; the edge follows the noise and A's own dark joints.
	float ask = 1.0 - COLOR.a;
	float own = smoothstep(1.0 - patches * 0.75, 1.0 - patches * 0.75 + 0.08, mid * 0.75 + big * 0.35 + (fine - 0.5) * 0.12);
	float ragged = ask + (mid + fine * 0.5 - 0.75) * 0.9 * smoothstep(0.0, 0.2, ask) * (1.0 - smoothstep(0.8, 1.0, ask));
	float mask = max(smoothstep(0.42, 0.58, ragged), own * step(0.001, patches));
	vec3 albedo = mix(a, b, mask) * COLOR.rgb;
	vec3 n = mix(na, nb, mask);
	albedo *= mix(1.0 - uneven * 0.55, 1.0 + uneven * 0.45, big) * mix(1.0 - uneven * 0.3, 1.0 + uneven * 0.2, mid);
	// Moss: up from the ground, thicker on ledges and in the damp patches.
	float up = clamp(world_normal.y, 0.0, 1.0);
	float low = 1.0 - clamp(p.y / moss_height, 0.0, 1.0);
	float grown = moss * smoothstep(0.62, 0.85, mid * 0.45 + fine * 0.25 + low * 0.5 + up * 0.35);
	albedo = mix(albedo, moss_tint * mix(0.6, 1.5, fine), grown * 0.85);
	// Rain.
	float runs = texture(blotch, vec2(q.x * 0.9, p.y * 0.035)).r;
	float open_sky = smoothstep(-0.25, 0.1, world_normal.y);
	float soaked = wet * open_sky * mix(smoothstep(0.35, 0.65, runs) * 0.75 + 0.1, 1.0, up);
	albedo *= mix(1.0, 0.6, soaked);
	ALBEDO = albedo;
	ROUGHNESS = mix(mix(rough, 1.0, grown), rough_wet + 0.25 * fine, soaked * (1.0 - grown * 0.6));
	SPECULAR = 0.5;
	NORMAL_MAP = n;
	NORMAL_MAP_DEPTH = bump * mix(1.0, 0.6, soaked);
}
