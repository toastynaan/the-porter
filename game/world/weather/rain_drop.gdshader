shader_type spatial;
// One drop of rain, as rain_fall.gdshader's particles leave it: falling, a
// long soft streak turned to the camera; landed, a little crown of spray
// that opens and is gone.
//
// Rain has no colour of its own. It shows where light is: faint against
// the sky, gold round a lantern or a fire, brightest with the light behind
// it. So it is lit by every light near it, whichever way it faces.
render_mode blend_mix, cull_disabled, depth_draw_never, skip_vertex_transform, shadows_disabled, specular_disabled;

uniform vec3 tint : source_color = vec3(0.72, 0.78, 0.86);
uniform float alpha = 0.27;
// A streak: how far a drop falls while the eye holds it (m), its width (m), and its direction.
uniform float streak = 0.5;
uniform float width = 0.012;
uniform vec3 fall = vec3(0.14, -1.0, 0.045);
// The narrowest a streak is drawn, in radians of view: under a pixel it would flicker.
uniform float thin = 0.0021;
uniform float splash_time = 0.2;
uniform float splash_size = 0.26;
uniform float far = 30.0;
// How much of the light on a drop reaches the eye, and how much more with the light behind it.
uniform float catch_light = 1.0;
uniform float back_light = 2.5;
// The most light a drop shows, however near the lamp.
uniform float brightest = 1.6;
// A little of the sky's own grey, so rain shows against the dark with no lamp near.
uniform float sky_light = 0.035;

varying float state;
varying float age;
varying float fade;
varying float level;

void vertex() {
	vec3 origin = MODEL_MATRIX[3].xyz;
	state = INSTANCE_CUSTOM.x;
	age = INSTANCE_CUSTOM.y / splash_time;
	level = INSTANCE_CUSTOM.z;
	float k = INSTANCE_CUSTOM.w;
	vec3 to_cam = CAMERA_POSITION_WORLD - origin;
	float dist = length(to_cam);
	to_cam /= max(dist, 0.001);
	vec3 at = origin;
	fade = smoothstep(1.8, 5.0, dist) * (1.0 - smoothstep(far * 0.6, far, dist));
	if (state < 0.5) {
		vec3 axis = normalize(fall);
		vec3 side = normalize(cross(axis, to_cam));
		float w = max(width * mix(0.7, 1.4, k), dist * thin);
		fade *= width / w * mix(0.55, 1.0, fract(k * 7.3));
		at += side * VERTEX.x * w - axis * (VERTEX.y + 0.5) * streak * mix(0.55, 1.45, fract(k * 3.7));
	} else if (state < 1.5) {
		vec3 side = normalize(cross(vec3(0.0, 1.0, 0.0), to_cam));
		float size = max(splash_size * mix(0.6, 1.2, k), dist * thin * 6.0) * mix(0.35, 1.0, sqrt(age));
		at += side * VERTEX.x * size * 2.0 + vec3(0.0, 1.0, 0.0) * (VERTEX.y + 0.5) * size;
		fade *= smoothstep(0.2, 0.7, level);
	}
	VERTEX = (VIEW_MATRIX * vec4(at, 1.0)).xyz;
	NORMAL = (VIEW_MATRIX * vec4(to_cam, 0.0)).xyz;
}

void fragment() {
	float a;
	if (state < 0.5) {
		float across = 1.0 - abs(UV.x * 2.0 - 1.0);
		// UV.y runs down the quad: the drop's head is at the bottom, its tail fades out above.
		a = across * smoothstep(0.0, 0.75, UV.y) * (1.0 - smoothstep(0.92, 1.0, UV.y));
	} else if (state < 1.5) {
		// A crown: a ring of spray thrown up and outward, thinning as it opens.
		vec2 p = vec2(UV.x * 2.0 - 1.0, (1.0 - UV.y) * 1.25);
		float r = length(p);
		float ring = 1.0 - smoothstep(0.0, 0.22, abs(r - 0.8));
		float beads = 0.45 + 0.55 * step(0.35, fract(atan(p.y, p.x) * 3.2 + age));
		float mist = (1.0 - smoothstep(0.0, 0.8, r)) * 0.35;
		a = (ring * beads + mist) * (1.0 - age) * 2.6;
	} else {
		discard;
	}
	ALBEDO = tint;
	EMISSION = tint * sky_light;
	ALPHA = clamp(a * alpha * fade, 0.0, 1.0);
}

void light() {
	float behind = pow(max(dot(LIGHT, -VIEW), 0.0), 3.0);
	DIFFUSE_LIGHT += min(LIGHT_COLOR * ATTENUATION * catch_light * (1.0 + back_light * behind), vec3(brightest));
}
