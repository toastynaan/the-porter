shader_type spatial;
// Dead grass, reeds and docks on the fields (art/models/env_road_growth.glb,
// tools/build/env_road_growth.py): flat blades, drawn from both sides. A
// blade's UV.y is its height in metres up from the root, which is how far
// the wind bends it. They are lit as the ground they stand on (their
// normals point up), so a tuft is never brighter than the field round it.
render_mode cull_disabled, diffuse_burley, specular_schlick_ggx;

uniform vec3 tint : source_color = vec3(0.75, 0.75, 0.75);
// The wind: its direction over the ground, how far it bends a metre of blade, how fast it gusts.
uniform vec2 wind = vec2(0.95, 0.3);
uniform float bend = 0.16;
uniform float gust = 1.3;
// Blades fade into the ground past this far, m, so the field's edge does not shimmer.
uniform float far = 85.0;

varying float dist;

void vertex() {
	vec3 world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	float wave = sin(TIME * gust + world.x * 0.35 + world.z * 0.21) + 0.5 * sin(TIME * gust * 2.7 + world.x * 1.3 - world.z * 0.9);
	float h = 1.0 - UV.y;  // (a glTF's V runs down)
	VERTEX.xz += wind * (0.5 + 0.5 * wave) * bend * h * h;
	NORMAL = vec3(0.0, 1.0, 0.0);
	dist = length(world - CAMERA_POSITION_WORLD);
}

void fragment() {
	ALBEDO = COLOR.rgb * tint;
	ROUGHNESS = 0.7;
	SPECULAR = 0.25;
	// Thin them out with distance rather than let them flicker.
	float keep = 1.0 - smoothstep(far * 0.6, far, dist);
	if (keep < fract(sin(dot(floor(UV * 37.0) + FRAGCOORD.xy * 0.0, vec2(12.9898, 78.233))) * 43758.5453) * 0.999) {
		discard;
	}
}
