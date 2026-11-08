shader_type canvas_item;
// The one post-process pass (Look and Feel, "Rendering style", "Colour
// palette"). It runs on the full-screen TextureRect that shows the 960x540
// world render. Every effect is worked out once per source pixel (the UV is
// snapped to the source pixel's centre), so the result scales up as crisply
// as the nearest-filtered image under it.
//
// Order: edge warp, blur, palette shift, grain, vignette, ordered dither and
// posterise. DoseDriver writes the uniforms from GameState.dose through the
// DoseLook curves (game/render/dose_look.tres).

// The world render twice: nearest for the image, linear for the blur taps.
uniform sampler2D src_nearest : filter_nearest, repeat_disable;
uniform sampler2D src_linear : filter_linear, repeat_disable;

uniform float dose : hint_range(0.0, 100.0) = 0.0;
// Grain amplitude (+/-) at black; half that at white ("stronger in the dark").
uniform float grain : hint_range(0.0, 0.2) = 0.04;
// Posterise levels per channel ("about 48").
uniform float levels : hint_range(2.0, 256.0) = 48.0;
// Corner darkening, 0..1.
uniform float vignette : hint_range(0.0, 1.0) = 0.35;
// 0 = sober palette, 1 = the full drugged shift.
uniform float palette_shift : hint_range(0.0, 1.0) = 0.0;
// Largest UV displacement at the screen's edges, as a fraction of the screen.
uniform float edge_warp : hint_range(0.0, 0.05) = 0.0;
// Blur radius in source pixels.
uniform float blur : hint_range(0.0, 4.0) = 0.0;
// 0..1 from staring at the demon (M3); adds its own edge warp.
uniform float stare : hint_range(0.0, 1.0) = 0.0;
uniform float stare_warp : hint_range(0.0, 0.05) = 0.012;
// The walls breathe (Dose 75+): the whole image swells and settles slowly.
uniform float breathe : hint_range(0.0, 0.05) = 0.0;

// Drugged shift targets (Look and Feel, "Drugged shift").
uniform vec3 bruise : source_color = vec3(0.165, 0.086, 0.133);	// #2A1622, shadows
uniform vec3 ergot : source_color = vec3(0.722, 0.690, 0.290);	// #B8B04A, highlights
// Extra saturation on reds and ambers at the full shift ("+30%").
uniform float warm_saturation : hint_range(0.0, 1.0) = 0.3;

const float BAYER[16] = float[16](
	0.0, 8.0, 2.0, 10.0,
	12.0, 4.0, 14.0, 6.0,
	3.0, 11.0, 1.0, 9.0,
	15.0, 7.0, 13.0, 5.0);

float luma(vec3 c) {
	return dot(c, vec3(0.299, 0.587, 0.114));
}

float hash12(vec2 p) {
	vec3 p3 = fract(vec3(p.xyx) * 0.1031);
	p3 += dot(p3, p3.yzx + 33.33);
	return fract((p3.x + p3.y) * p3.z);
}

vec3 rgb2hsv(vec3 c) {
	vec4 k = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
	vec4 p = mix(vec4(c.bg, k.wz), vec4(c.gb, k.xy), step(c.b, c.g));
	vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
	float d = q.x - min(q.w, q.y);
	return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + 1e-10)), d / (q.x + 1e-10), q.x);
}

vec3 hsv2rgb(vec3 c) {
	vec3 p = abs(fract(c.xxx + vec3(1.0, 2.0 / 3.0, 1.0 / 3.0)) * 6.0 - 3.0);
	return c.z * mix(vec3(1.0), clamp(p - 1.0, 0.0, 1.0), c.y);
}

void fragment() {
	vec2 src_size = vec2(textureSize(src_nearest, 0));
	vec2 px = floor(UV * src_size);
	vec2 uv = (px + 0.5) / src_size;
	vec2 c = uv - 0.5;
	float r = length(c);

	// The walls breathe: the image swells from the centre and settles.
	if (breathe > 0.0) {
		uv = 0.5 + c * (1.0 - breathe * (0.5 + 0.5 * sin(TIME * 0.9)));
		c = uv - 0.5;
		r = length(c);
	}

	// Edge warp: the edges breathe in and out, out of phase around the frame.
	float warp = edge_warp + stare * stare_warp;
	if (warp > 0.0 && r > 0.0) {
		float wave = 0.5 + 0.5 * sin(TIME * 0.8 + atan(c.y, c.x) * 3.0);
		uv -= c / r * warp * smoothstep(0.2, 0.75, r) * wave;
	}

	vec3 col = texture(src_nearest, uv).rgb;
	if (blur > 0.01) {
		vec2 o = blur / src_size;
		vec3 b = texture(src_linear, uv).rgb * 0.25;
		b += (texture(src_linear, uv + vec2(o.x, 0.0)).rgb + texture(src_linear, uv - vec2(o.x, 0.0)).rgb
			+ texture(src_linear, uv + vec2(0.0, o.y)).rgb + texture(src_linear, uv - vec2(0.0, o.y)).rgb) * 0.125;
		b += (texture(src_linear, uv + o).rgb + texture(src_linear, uv - o).rgb
			+ texture(src_linear, uv + vec2(o.x, -o.y)).rgb + texture(src_linear, uv + vec2(-o.x, o.y)).rgb) * 0.0625;
		col = mix(col, b, clamp(blur, 0.0, 1.0));
	}

	if (palette_shift > 0.0) {
		float s = palette_shift;
		// Shadows lift and warm: black becomes bruise purple at the full shift.
		col = mix(col, bruise + col * (1.0 - bruise), s);
		// Highlights go sickly: tinted toward ergot, brightness kept.
		float l = luma(col);
		col = mix(col, ergot * (l / luma(ergot)), smoothstep(0.35, 0.85, l) * s * 0.6);
		// Reds and ambers get louder; everything else stays dull.
		vec3 hsv = rgb2hsv(col);
		float hue_dist = min(abs(hsv.x - 0.05), 1.0 - abs(hsv.x - 0.05));
		float warm = 1.0 - smoothstep(0.06, 0.12, hue_dist);
		hsv.y = clamp(hsv.y * (1.0 + warm_saturation * s * warm), 0.0, 1.0);
		col = hsv2rgb(hsv);
	}

	// Film grain, a new pattern 24 times a second; triangular noise in -1..1,
	// so most grains are faint.
	vec2 seed = px + floor(TIME * 24.0) * vec2(17.0, 59.0);
	float n = hash12(seed) + hash12(seed + vec2(113.0, 7.0)) - 1.0;
	col += n * grain * (1.0 - 0.5 * luma(col));

	col *= 1.0 - vignette * smoothstep(0.3, 1.0, r * 1.41421);

	// Ordered dither into the posterise step: no banding in the near-black.
	float q = levels - 1.0;
	float d = BAYER[int(mod(px.x, 4.0)) + int(mod(px.y, 4.0)) * 4] / 16.0;
	col = floor(clamp(col, 0.0, 1.0) * q + d) / q;

	COLOR = vec4(col, 1.0);
}
