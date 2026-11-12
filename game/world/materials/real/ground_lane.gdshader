shader_type spatial;
// The lane outside the abbey gate (art/models/env_lane_ground.glb, built by
// tools/build/env_lane.py): a carriageway of setts laid in courses across
// it, a kerb and a flagged sidewalk each side, all of it wet. Mud is only
// in the joints, the gutters and the alleys.
//
// The mesh's vertex colours say what a face is and what lies on it:
//   green  what it is: 0 setts, 0.5 a kerb stone, 1 flags
//   red    mud over it (an alley); on a kerb stone, its tone
//   blue   on setts, how near the nearest kerb is: metres = blue * 2.25 - 0.25;
//          on a kerb stone, half its length in metres
//   alpha  standing water; on a kerb stone, a number of its own
// UV is in metres: on setts (along the road, across it), on flags (along
// the walk, from its wall), on a kerb stone (from its end, over its top and
// down its face). The stones' relief is laid along those directions, found
// from the UV itself, so a model can be turned any way.
//
// The setts are drawn here, stone by stone: each has its own length, tone,
// tilt and height, which is what makes a wet street glitter. Beyond a dozen
// metres a course is narrower than a pixel and they fade to their mean.
//
// `plain_flags` is for a face with no such colours or UV (the greybox block
// that is the gate's apron): flags all over it, laid by the world's axes.
render_mode diffuse_burley, specular_schlick_ggx;

uniform sampler2D flag_col : source_color, repeat_enable, filter_linear_mipmap_anisotropic;
uniform sampler2D flag_nrm : hint_normal, repeat_enable, filter_linear_mipmap_anisotropic;
uniform sampler2D mud_col : source_color, repeat_enable, filter_linear_mipmap_anisotropic;
uniform sampler2D mud_nrm : hint_normal, repeat_enable, filter_linear_mipmap_anisotropic;
uniform sampler2D blotch : repeat_enable, filter_linear_mipmap;
// A sett: metres from course to course, and its usual length along the course.
uniform vec2 sett_size = vec2(0.125, 0.21);
uniform float sett_joint = 0.005;
uniform float sett_round = 0.028;
uniform float sett_shoulder = 0.8;
uniform float sett_dome = 0.35;
uniform float sett_tilt = 0.24;
uniform float flag_size = 2.1;
uniform float flag_shift = 0.0;
uniform float flag_relief = 0.9;
uniform float mud_size = 3.0;
uniform vec3 sett_tint : source_color = vec3(0.3, 0.3, 0.31);
uniform vec3 joint_tint : source_color = vec3(0.035, 0.03, 0.025);
uniform vec3 flag_tint : source_color = vec3(0.54, 0.53, 0.5);
uniform vec3 kerb_tint : source_color = vec3(0.46, 0.45, 0.43);
uniform vec3 mud_tint : source_color = vec3(0.4, 0.36, 0.32);
uniform vec3 water_color : source_color = vec3(0.012, 0.014, 0.017);
uniform float gutter_wide = 0.23;
uniform float rain : hint_range(0.0, 1.0) = 1.0;
uniform bool plain_flags = false;

varying vec3 world_pos;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
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

// A normal map's lean along the texture's own two directions (its green is up the picture).
vec2 lean(sampler2D map, vec2 at) {
	vec2 n = texture(map, at).rg * 2.0 - 1.0;
	return vec2(n.x, -n.y);
}

vec4 hash4(vec2 at) {
	return fract(sin(vec4(dot(at, vec2(127.1, 311.7)), dot(at, vec2(269.5, 183.3)), dot(at, vec2(419.2, 371.9)), dot(at, vec2(97.3, 157.1)))) * 43758.5453);
}

// Where stone `k` of a course begins: each stone has a length of its own.
float cut(float row, float k) {
	return k + (fract(sin(dot(vec2(row, k), vec2(12.9898, 78.233))) * 43758.5453) - 0.5) * 0.6;
}

// Where course `k` begins: no two are the same width.
float row_cut(float k, float uneven) {
	return k + (fract(sin(k * 78.233) * 43758.5453) - 0.5) * uneven;
}

// The way a value known at each pixel rises over the surface, in the world.
vec3 rise(float fx, float fy, vec3 dp1, vec3 dp2, vec3 n) {
	vec3 g = (fx * cross(dp2, n) + fy * cross(n, dp1)) / dot(dp1, cross(dp2, n));
	return g;
}

void fragment() {
	vec2 p = world_pos.xz;
	vec2 uv = plain_flags ? p : UV;
	vec4 what = plain_flags ? vec4(0.0, 1.0, 1.0, 0.0) : COLOR;
	// The two directions the UV runs in, in the world.
	vec3 up = normalize((INV_VIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
	vec3 dp1 = dFdx(world_pos);
	vec3 dp2 = dFdy(world_pos);
	vec3 tu = normalize(rise(dFdx(uv.x), dFdy(uv.x), dp1, dp2, up) + vec3(1.0e-6, 0.0, 0.0));
	vec3 tv = normalize(rise(dFdx(uv.y), dFdy(uv.y), dp1, dp2, up) + vec3(0.0, 0.0, 1.0e-6));
	// On setts: how far the nearest kerb is, and the way from it.
	float d = what.b * 2.25 - 0.25;
	vec3 td = normalize(rise(dFdx(d), dFdy(d), dp1, dp2, up) + tv * 1.0e-4);
	// The setts' two layings: courses across the road, and two courses along the kerb for the gutter's channel.
	vec2 lay_road = uv / sett_size;
	vec2 lay_kerb = vec2(d / 0.13, uv.x / sett_size.y + 0.4);
	vec2 wide_road = fwidth(lay_road);
	vec2 wide_kerb = fwidth(lay_kerb);

	float big = texture(blotch, p * 0.021).r;
	float mid = texture(blotch, p * 0.11 + 0.3).r;
	float fine = texture(blotch, p * 0.7 + 0.7).r;
	float grit = texture(blotch, p * 3.1 + 0.2).r;

	vec3 albedo;
	vec3 tilt;
	float rough;
	// How high the surface stands here, 0 in a joint to 1 on a stone's crown: water covers the low first.
	float high;
	float water = what.a;
	if (what.g > 0.75) {
		// Flags: two courses to the walk's width.
		vec2 q = vec2(uv.x, uv.y + flag_shift) / flag_size;
		vec3 c = texture(flag_col, q).rgb;
		albedo = c * flag_tint * mix(0.75, 1.15, big);
		vec2 n = lean(flag_nrm, q);
		tilt = (tu * n.x + tv * n.y) * flag_relief;
		rough = mix(0.16, 0.42, smoothstep(0.3, 0.7, fine * 0.6 + grit * 0.4));
		high = 0.62 + (mid - 0.5) * 0.5;
		// Rain lies in a flag's dish here and there.
		water = max(water, smoothstep(0.58, 0.74, texture(blotch, p * 0.19 + 0.11).r + (fine - 0.5) * 0.2) * 0.72);
	} else if (what.g > 0.25) {
		// A kerb stone: long, pale, clean on its top and its arris, dark and wet at its foot.
		float len = what.b * 2.0;
		float end = min(uv.x, len - uv.x);
		float joint = 1.0 - smoothstep(0.003, 0.011, end);
		float grain = texture(blotch, vec2(uv.x + what.a * 7.0, uv.y) * 1.9).r;
		float speck = texture(blotch, vec2(uv.x + what.a * 7.0, uv.y) * 9.0).r;
		albedo = kerb_tint * mix(0.78, 1.18, what.r) * mix(0.8, 1.15, grain) * mix(0.85, 1.1, speck);
		float foot = smoothstep(0.24, 0.31, uv.y + (grain - 0.5) * 0.05);
		albedo *= mix(1.0, 0.45, foot) * (1.0 - 0.75 * joint);
		tilt = tu * (smoothstep(0.03, 0.0, uv.x) - smoothstep(0.03, 0.0, len - uv.x)) * -0.5 + (tu * (grain - 0.5) + tv * (speck - 0.5)) * 0.25;
		rough = mix(0.2, 0.4, speck) + 0.4 * joint;
		high = 1.0;
		water = 0.0;
	} else {
		// Setts.
		bool by_kerb = d < 0.26;
		vec2 lay = by_kerb ? lay_kerb : lay_road;
		vec2 wide = by_kerb ? wide_kerb : wide_road;
		vec2 pitch = by_kerb ? vec2(0.13, sett_size.y) : sett_size;
		vec3 e0 = by_kerb ? td : tu;
		vec3 e1 = by_kerb ? tu : tv;
		// The courses wander, no two are the same width and no joint is straight.
		vec2 wander = (vec2(texture(blotch, p * 0.3 + 0.13).r, texture(blotch, p * 0.3 + 0.57).r) - 0.5) * 0.07;
		wander += (vec2(texture(blotch, p * 5.0 + 0.31).r, texture(blotch, p * 5.0 + 0.77).r) - 0.5) * 0.012;
		lay += wander / pitch;
		float uneven = by_kerb ? 0.0 : 0.36;
		float row = floor(lay.x);
		float lo = row_cut(row, uneven);
		float hi = row_cut(row + 1.0, uneven);
		if (lay.x < lo) {
			row -= 1.0;
			hi = lo;
			lo = row_cut(row, uneven);
		} else if (lay.x > hi) {
			row += 1.0;
			lo = hi;
			hi = row_cut(row + 1.0, uneven);
		}
		vec2 local;
		vec2 to_edge;
		local.x = (lay.x - lo) / (hi - lo) - 0.5;
		to_edge.x = min(lay.x - lo, hi - lay.x) * pitch.x;
		float along = lay.y + fract(sin(row * 127.1) * 43758.5453) * 7.31;
		float k = floor(along);
		lo = cut(row, k);
		hi = cut(row, k + 1.0);
		if (along < lo) {
			k -= 1.0;
			hi = lo;
			lo = cut(row, k);
		} else if (along > hi) {
			k += 1.0;
			lo = hi;
			hi = cut(row, k + 1.0);
		}
		vec4 own = hash4(vec2(row, k));
		local.y = (along - lo) / (hi - lo) - 0.5;
		to_edge.y = min(along - lo, hi - along) * pitch.y;
		to_edge -= sett_joint * (0.6 + 0.9 * own.x);
		// Its corners are worn round.
		vec2 corner = max(sett_round - to_edge, 0.0);
		float edge = (to_edge.x < sett_round && to_edge.y < sett_round) ? sett_round - length(corner) : min(to_edge.x, to_edge.y);
		// A course narrower than a pixel can't be drawn: the setts fade to their mean.
		float blur = max(wide.x, wide.y);
		float seen = 1.0 - smoothstep(0.3, 0.8, blur);
		float soft = max(blur * pitch.x * 0.7, 0.0015);
		float stone = mix(0.87, smoothstep(-soft, soft, edge), seen);
		// Its shape: shoulders rounded down into the joints, a dome, and a tilt of its own as it has settled.
		vec2 shoulder = max(sett_round * 1.3 - to_edge, 0.0) / (sett_round * 1.3);
		shoulder *= length(shoulder) / max(length(shoulder), 1.0);
		vec2 fall = sign(local) * shoulder * sett_shoulder + local * (1.0 + 2.0 * dot(local, local)) * sett_dome + (own.yz - 0.5) * sett_tilt;
		tilt = (e0 * fall.x + e1 * fall.y) * stone * seen;
		// The stone's own grain, from the flags' picture, set down differently on each.
		vec2 qg = (uv + own.zw * 3.0) / 0.8;
		float grain = dot(texture(flag_col, qg).rgb, vec3(1.7));
		vec2 pit = lean(flag_nrm, qg);
		tilt += (tu * pit.x + tv * pit.y) * 0.7 * stone;
		float crown = smoothstep(0.0, 0.03, edge);
		float sunk = smoothstep(0.7, 1.0, own.w) * seen;
		high = stone * (0.5 + 0.5 * crown) - 0.45 * sunk;
		vec3 face = sett_tint * mix(0.65, 1.3, mix(0.5, own.x, seen)) * mix(0.75, 1.2, big) * mix(0.85, 1.12, mid) * clamp(grain, 0.5, 1.6);
		// A few are a warmer stone.
		face *= mix(vec3(1.0), vec3(1.14, 1.0, 0.84), step(0.8, own.z) * seen);
		albedo = mix(joint_tint, face, stone);
		rough = mix(0.8, mix(0.16, 0.4, mix(0.5, own.y, seen) * 0.5 + fine * 0.5) + 0.2 * (1.0 - seen), stone);
		// Mud: over the stones where the mesh says (an alley), and silted along a gutter.
		float silt = (1.0 - smoothstep(0.0, 0.45, d)) * 0.3;
		float muddy = smoothstep(0.38, 0.62, what.r * 0.9 + silt + ((mid - 0.5) * 0.9 + (1.0 - stone) * 0.4) * step(0.3, what.r) + (big - 0.5) * 0.3 - high * 0.12);
		vec2 q = p / mud_size;
		vec2 n = lean(mud_nrm, q);
		albedo = mix(albedo, texture(mud_col, q).rgb * mud_tint * 0.6, muddy);
		tilt = mix(tilt, vec3(n.x, 0.0, n.y), muddy * 0.8);
		rough = mix(rough, mix(0.7, 0.5, fine), muddy);
		high = mix(high, 0.5 + (fine - 0.5) * 0.6, muddy);
		// Water stands along the kerb's foot, for most of its length, and in the hollows.
		float full = smoothstep(0.3, 0.45, texture(blotch, p * 0.043 + 0.61).r);
		float gutter = (1.0 - smoothstep(gutter_wide - 0.07, gutter_wide + 0.03, d + (mid - 0.5) * 0.14)) * mix(0.45, 1.0, full);
		float holes = smoothstep(0.6, 0.72, texture(blotch, p * 0.047 + 0.37).r + (fine - 0.5) * 0.12) * 0.8;
		water = max(water, max(gutter, holes));
	}
	// Water covers the joints first, then the stones' shoulders, then everything.
	float flood = smoothstep(-0.1, 0.1, water * 1.3 - high - 0.12);
	vec2 r1 = texture(blotch, p * 1.7 + vec2(TIME * 0.31, TIME * 0.23)).rg;
	vec2 r2 = texture(blotch, p * 2.9 - vec2(TIME * 0.27, TIME * 0.35)).gr;
	vec2 struck = rings(p * 2.7, TIME * 1.25) + rings(p * 4.3 + 7.3, TIME * 1.05 + 0.4) * 0.7;
	vec2 ripple = ((r1 + r2 - 1.0) * 0.1 + struck * 0.45) * rain;
	vec3 n_wet = normalize(up + tilt);
	vec3 n_water = normalize(up + vec3(ripple.x, 0.0, ripple.y));
	// Everything is wet: darker than dry, and it shines. Shallow water shows the stone under it; only where it stands deep is it dark.
	float deep = smoothstep(0.7, 1.0, water);
	ALBEDO = mix(albedo * 0.6, mix(albedo * 0.42, water_color, 0.35 + 0.6 * deep), flood);
	ROUGHNESS = mix(rough, 0.035, flood);
	// A little more than water gives: the lane has few lamps, and it is the wet that shows them.
	SPECULAR = mix(0.75, 0.6, flood);
	NORMAL = normalize((VIEW_MATRIX * vec4(normalize(mix(n_wet, n_water, flood)), 0.0)).xyz);
}
