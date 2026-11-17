shader_type spatial;
// A real head's face (docs/systems/faces.md, "The face"): all of it is
// painted here, on the head's flat planes (tools/build/people.py). Nothing
// is read from a texture: flat skin with soft shadows (under the brows,
// under the jaw, down the sides of the face), hair as one dark shape with a
// spiked edge, a beard in strokes, and over them the eyes (dark ovals), the
// brows (thick, hatched), the mouth, the creases and the throat, drawn from
// what the FaceRig sets each step (instance uniforms face_a..c). Who he is
// (skin, hair, beard, brows, marks) is the material's, written by his build
// (people.face_look). Lit per vertex and snapped like the rest of the
// person (person.gdshader).
//
// Head space: metres from the neck pivot, x his right, y up, -z forward.

render_mode vertex_lighting, cull_back, diffuse_lambert, specular_schlick_ggx;

#include "res://game/core/render/psx.gdshaderinc"

uniform float roughness : hint_range(0.0, 1.0) = 0.9;
uniform float specular : hint_range(0.0, 1.0) = 0.12;
// Above 0, everything is painted on a grid of this many metres (0.0021: a
// PSX face texture's texels). 0: clean shapes.
uniform float texel = 0.0;

group_uniforms skin;
uniform vec3 skin_color : source_color = vec3(0.68, 0.55, 0.47);
// Skin in its own shadow: darker and pinker.
uniform vec3 shade_color : source_color = vec3(0.53, 0.37, 0.37);
uniform vec3 flush_color : source_color = vec3(0.62, 0.3, 0.24);
// How red the cheeks, the nose and the ears are.
uniform float flush : hint_range(0.0, 1.0) = 0.5;
// How deep the shadow under the brows is (deep-set eyes).
uniform float socket : hint_range(0.0, 1.0) = 0.5;
// How deep the creases are drawn: age, weather.
uniform float lines : hint_range(0.0, 1.0) = 0.5;
uniform float freckles : hint_range(0.0, 1.0) = 0.0;
// A scar along his right jaw.
uniform float scar : hint_range(0.0, 1.0) = 0.0;

group_uniforms hair;
uniform vec3 hair_color : source_color = vec3(0.2, 0.15, 0.11);
// 0 cropped, 1 bowl, 2 tonsure, 3 balding, 4 bald, 5 long (the kit's HAIR_STYLES).
uniform int hair_style = 0;
// Where the hair starts on the brow, metres up the head.
uniform float hairline = 0.236;
// How much of it has gone grey.
uniform float grey_hair : hint_range(0.0, 1.0) = 0.0;
// How far its edge breaks into tufts and strokes (0: a clean edge).
uniform float tufts : hint_range(0.0, 2.0) = 1.0;

group_uniforms beard;
uniform vec3 beard_color : source_color = vec3(0.25, 0.19, 0.15);
// 0 none; below 0.6 stubble, in strokes; from 0.6 a beard, in one shape.
uniform float beard : hint_range(0.0, 1.0) = 0.0;
// Its top edge, raised (m), and how far it stands up under the nose.
uniform float beard_top = 0.0;
uniform float moustache : hint_range(0.0, 1.0) = 0.0;

group_uniforms face;
// Where the features are on the head, and their size (m).
uniform vec2 eye_at = vec2(0.031, 0.184);
uniform vec2 eye_size = vec2(0.0042, 0.0066);
uniform vec3 eye_color : source_color = vec3(0.09, 0.065, 0.055);
uniform vec3 white_color : source_color = vec3(0.72, 0.68, 0.6);
uniform vec2 brow_at = vec2(0.034, 0.2005);
// The brows' half length and half thickness; how far the middle arches (in
// thicknesses); how they slant at rest (radians: + the inner ends up, a
// worried look; - down, a stern one); how much they thin toward the temples
// (tools/build/people_kit.py, BROWS).
uniform vec2 brow_size = vec2(0.019, 0.0034);
uniform float brow_arch = 0.4;
uniform float brow_slant = 0.0;
uniform float brow_taper = 0.35;
uniform vec3 brow_color : source_color = vec3(0.18, 0.13, 0.1);
uniform float mouth_y = 0.126;
uniform float mouth_half = 0.0145;
uniform vec3 lip_color : source_color = vec3(0.55, 0.33, 0.29);
uniform vec3 ink : source_color = vec3(0.15, 0.09, 0.08);
uniform vec3 mouth_color : source_color = vec3(0.12, 0.05, 0.04);
uniform vec3 teeth_color : source_color = vec3(0.7, 0.66, 0.57);
// How far a mood moves the face: the brows' rise and tilt, the mouth's
// curve and width, how wide the eyes go. 1 is the FaceRig's own numbers (a
// placeholder's box face); a painted face needs more to read at 4 m.
uniform float expression = 1.6;

// brow_y, brow_tilt, lid, eye_x
instance uniform vec4 face_a = vec4(0.0);
// eye_y, mouth_w, curve, open
instance uniform vec4 face_b = vec4(0.0, 1.0, 0.0, 0.0);
// mouth_y, throat, blind (1), unused
instance uniform vec4 face_c = vec4(0.0);

varying vec3 head_pos;
varying vec3 head_normal;

void vertex() {
	head_pos = VERTEX;
	head_normal = NORMAL;
	PSX_VERTEX
}

float hash(float n) {
	return clamp(fract(sin(n * 127.1 + 3.7) * 43758.5453), 0.0, 1.0);
}

float hash2(vec2 v) {
	return clamp(fract(sin(dot(v, vec2(127.1, 311.7))) * 43758.5453), 0.0, 1.0);
}

float sq(float x) {
	return x * x;
}

// 0 to 1 as x goes from a to b.
float along(float x, float a, float b) {
	return clamp((x - a) / (b - a), 0.0, 1.0);
}

// 1 at whole numbers, 0 half way between: a row of teeth.
float teeth(float t) {
	return abs(fract(t) - 0.5) * 2.0;
}

// How much of a pixel `px` wide is inside a shape, `d` from its edge (- inside).
float fill(float d, float px) {
	return clamp(0.5 - d / px, 0.0, 1.0);
}

float seg(vec2 p, vec2 a, vec2 b) {
	vec2 pa = p - a;
	vec2 ba = b - a;
	float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
	return length(pa - ba * h);
}

// A drawn line from a to b, `w` wide at its middle, thinning to its ends.
float stroke(vec2 p, vec2 a, vec2 b, float w, float px) {
	vec2 pa = p - a;
	vec2 ba = b - a;
	float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
	return fill(length(pa - ba * h) - w * (0.35 + 0.65 * sin(h * PI)), px);
}

// Short strokes laid side by side over a patch, as a brush hatches it: 1 on
// a stroke. `g` is the place (m), `lean` the strokes' angle, `gap` the
// space between them, `some` how many of them are there (0 to 1).
float hatch(vec2 g, float lean, float gap, float some, float px) {
	vec2 dir = vec2(cos(lean), sin(lean));
	float r = dot(g, vec2(-dir.y, dir.x)) / gap;
	float id = floor(r);
	float h = hash(id);
	float k = dot(g, dir) / (0.0055 + 0.004 * h) + h * 9.0;
	float on = step(hash2(vec2(id, floor(k))) + 0.0001, some);
	float f = fract(k);
	float body = min(along(f, 0.08, 0.3), along(f, 0.95, 0.7));
	return on * fill(abs(fract(r) - 0.5) * gap - 0.00042 * body, px) * step(0.01, body);
}

// How far down the hair comes at `aa` round the head from the front (0)
// to the back (PI): across the brow, back at the temples, down in front of
// the ear, over it, down behind it to the nape. (people.hair_line is the
// same line, for the hair's bulk.)
float hair_line(float aa) {
	if (hair_style == 1) {
		// A bowl: a fringe, and cut straight round above the ears.
		return mix(hairline - 0.014, 0.203, along(aa, 0.8, 1.0));
	}
	if (hair_style == 2) {
		// The ring a tonsure leaves.
		return mix(hairline - 0.008, 0.203, along(aa, 0.75, 1.0));
	}
	float y = mix(hairline, hairline + 0.006, along(aa, 0.0, 0.42));
	y = mix(y, hairline - 0.006, along(aa, 0.42, 0.7));
	y = mix(y, 0.2, along(aa, 0.7, 1.16));
	y = mix(y, 0.168, along(aa, 1.16, 1.26));
	y = mix(y, 0.207, along(aa, 1.48, 1.6));
	y = mix(y, 0.152, along(aa, 1.95, 2.12));
	return mix(y, 0.13, along(aa, 2.12, PI));
}

// How much hair is at `p`: 1 in it, 0 on skin.
float hair_at(vec3 p, float a, float aa, float px) {
	// Its edge: uneven tufts down onto the brow, fine strokes where it ends
	// at the sideburns, behind the ears and on the nape.
	float t = a * 6.3 + 0.4;
	float i = floor(t);
	float f = t - i;
	float peak = 0.3 + 0.4 * hash(i + 3.0);
	float tuft = (0.003 + 0.009 * hash(i)) * (f < peak ? f / peak : (1.0 - f) / (1.0 - peak));
	float comb = 0.009 * teeth(aa * 50.0) * (0.4 + 0.6 * hash(floor(aa * 50.0 + 0.5)));
	float edge = mix(tuft, comb, along(aa, 0.9, 1.16));
	if (hair_style == 1 || hair_style == 2) {
		// Cut straight: only a little uneven.
		edge = 0.35 * tuft + 0.0015 * teeth(a * 30.0);
	}
	float h = fill(hair_line(aa) - edge * tufts - p.y, px);
	if (hair_style == 2) {
		// The crown is shaved.
		h *= fill(p.y - 0.266 + 0.003 * teeth(a * 26.0), px);
	} else if (hair_style == 3) {
		// Gone from the brow and the crown: left at the sides and back.
		h *= fill(p.y - 0.258 + 0.006 * teeth(aa * 34.0), px) * fill((1.16 + 0.07 * teeth(p.y * 190.0) - aa) * 0.08, px);
	} else if (hair_style == 4) {
		h *= 0.1;
	}
	return h;
}

vec3 hair_paint(vec3 p, float a, float px) {
	// Grey comes all through it, and in strokes.
	vec3 grey = vec3(0.4, 0.385, 0.365);
	vec3 c = mix(hair_color, grey, grey_hair * 0.5);
	return mix(c, grey * 1.2, 0.6 * hatch(vec2(a * 0.085, p.y), 1.42, 0.003, grey_hair * 0.7, px));
}

// The top edge of a beard at `aa`: across the upper lip, down past the
// mouth's corners, up the cheek to the sideburn.
float beard_line(float aa) {
	float y = mix(0.1415 + 0.003 * moustache, 0.138, along(aa, 0.0, 0.16));
	y = mix(y, 0.129, along(aa, 0.16, 0.3));
	y = mix(y, 0.142, along(aa, 0.3, 0.52));
	y = mix(y, 0.172, along(aa, 0.52, 1.1));
	return mix(y, 0.2, along(aa, 1.1, 1.45)) + beard_top;
}

vec3 beard_paint(vec3 c, vec3 p, float aa, float px) {
	if (beard <= 0.0 || aa > 1.62) {
		return c;
	}
	float d = beard_line(aa) - p.y;
	float end = 1.0 - along(aa, 1.5, 1.62);
	vec2 g = vec2(aa * 0.085, p.y);
	if (beard >= 0.6) {
		// One shape, its edges broken into strokes.
		float jag = (0.3 + 0.7 * hash(floor(aa * 23.0 + 0.5))) * teeth(aa * 23.0);
		float m = fill(0.005 * jag - d, px) * fill(0.066 + 0.008 * jag - p.y, px) * end;
		vec3 b = mix(beard_color, beard_color * 1.35 + 0.02, 0.5 * hatch(g, -0.95, 0.0032, 0.45, px));
		return mix(c, b, m);
	}
	// Stubble: a shadow on the jaw, and strokes down it toward the chin.
	float low = along(p.y, 0.058, 0.082);
	float m = smoothstep(-0.002, 0.026, d) * low * end * step(0.0, d);
	c = mix(c, mix(shade_color, beard_color, 0.35), m * beard * 0.9);
	float strokes = max(hatch(g, -0.95, 0.0031, 0.25 + 0.7 * beard, px), hatch(g + 0.013, -1.3, 0.0043, 0.2 + 0.6 * beard, px));
	return mix(c, beard_color, 0.75 * strokes * m);
}

// The skin: flat, with the shadows a painter gives it.
vec3 skin_paint(vec3 p, float aa, float down, bool nose, bool ear) {
	vec3 c = skin_color;
	// Under the brows, across the eyes, fading down the cheeks and round the temples.
	float band = smoothstep(0.148, 0.192, p.y) * (1.0 - smoothstep(0.1975, 0.2035 + 0.02 * along(aa, 0.45, 1.0), p.y));
	c = mix(c, shade_color, band * (1.0 - smoothstep(0.4, 1.15, aa)) * (0.2 + 0.6 * socket));
	// The sides of the face turn from the light, most along the jaw.
	c = mix(c, shade_color, 0.3 * along(aa, 0.5, 1.15) * (1.0 - 0.7 * along(p.y, 0.1, 0.23)));
	// Under the jaw and down the neck: deepest right under it.
	float jaw = mix(0.083, 0.112, smoothstep(0.25, 1.7, aa));
	float under = max(1.0 - smoothstep(jaw - 0.007, jaw + 0.001 + 0.03 * along(aa, 1.6, 2.2), p.y), nose ? 0.0 : down);
	c = mix(c, shade_color, under * mix(0.3, 0.95, along(p.y, -0.035, jaw)) * (1.0 - 0.6 * along(aa, 1.6, 2.4)));
	// Red in the cheeks, the nose and the ears.
	float red = 0.0;
	if (ear) {
		red = 0.7;
		// The hollow of the ear.
		c = mix(c, shade_color, 0.75 * (1.0 - smoothstep(0.004, 0.019, p.z)) * (1.0 - abs(p.y - 0.176) / 0.03));
	} else if (nose) {
		red = 0.9 * exp(-sq((p.y - 0.152) / 0.014));
	} else if (p.z < 0.0) {
		red = 0.75 * exp(-(sq((abs(p.x) - 0.046) / 0.02) + sq((p.y - 0.146) / 0.018)));
	}
	return mix(c, flush_color, 0.34 * flush * red);
}

// One eye: a dark oval. A lid comes down across it (weary, wary; a blink
// shuts it to a line); a smile lifts its foot; afraid, it stands in white.
vec3 eye(vec2 q, float s, vec3 c, float lid, vec2 look, float smile, float px) {
	float wide = max(-lid, 0.0);
	float shut = max(lid, 0.0);
	vec2 at = vec2(s * eye_at.x, eye_at.y);
	vec2 r = eye_size * (1.0 + 0.12 * wide);
	// The fold of the lid above it, which stays as the eye looks about.
	float fold = eye_at.y + eye_size.y * 1.45 - 0.0016 * sq((q.x - at.x) / (eye_size.x * 2.1));
	c = mix(c, shade_color * 0.82, 0.5 * (0.35 + 0.65 * lines) * fill(abs(q.y - fold) - 0.00045, px)
			* fill(abs(q.x - at.x) - eye_size.x * 2.1, px));
	// Lines under it, with age.
	if (lines > 0.55) {
		float bag = eye_at.y - eye_size.y * 1.75 + 0.0022 * sq((q.x - at.x) / (eye_size.x * 2.2));
		c = mix(c, shade_color * 0.82, (lines - 0.55) * 1.6 * fill(abs(q.y - bag) - 0.00045, px)
				* fill(abs(q.x - at.x - s * 0.001) - eye_size.x * 2.0, px));
	}
	vec2 ctr = at + look;
	vec2 e = q - ctr;
	if (shut > 0.86) {
		// Shut: a line where the lids meet.
		float y = -r.y * 0.35 - 0.0012 * sq(e.x / (r.x * 1.7)) * (1.0 - 2.0 * step(0.3, smile));
		return mix(c, ink, fill(abs(e.y - y) - 0.0007, px) * fill(abs(e.x) - r.x * 1.7, px));
	}
	// Wide: the white shows round it.
	if (wide > 0.02) {
		vec2 rw = eye_size * (1.0 + 0.9 * wide) + vec2(0.0022, 0.0008) * wide;
		float dw = (length((q - at) / rw) - 1.0) * min(rw.x, rw.y);
		c = mix(c, shade_color * 0.7, 0.6 * fill(dw - 0.0005, px));
		c = mix(c, white_color, 0.9 * fill(dw, px));
	}
	float d = (length(e / r) - 1.0) * min(r.x, r.y);
	// The lids: the upper comes down, the lower up a little with it, and up with a smile.
	float top = r.y * (1.0 - 1.55 * shut);
	float foot = -r.y * (1.0 - 0.45 * shut) + smile * r.y * (1.5 - 0.5 * sq(e.x / r.x));
	float open = fill(e.y - top, px) * fill(foot - e.y, px);
	c = mix(c, eye_color, fill(d, px) * open);
	// A pale eye (a blind man's) has a rim, or it is lost on his skin.
	c = mix(c, eye_color * 0.62, step(0.4, dot(eye_color, vec3(0.333))) * fill(abs(d + 0.0006) - 0.0005, px) * open);
	if (shut > 0.12) {
		// The lid's edge across it.
		c = mix(c, ink, fill(abs(e.y - top) - 0.0006, px) * fill(abs(e.x) - r.x * 1.5, px));
	}
	return c;
}

// The features: eyes, brows, mouth, creases, throat. `q` is the place on
// the face, seen from in front.
vec3 face(vec2 q, vec3 c, float px) {
	float s = q.x < 0.0 ? -1.0 : 1.0;
	float brow_y = face_a.x * expression;
	// The mood's tilt, and with his brows' own slant.
	float mood_tilt = face_a.y * expression;
	float tilt = mood_tilt + brow_slant;
	float lid = face_a.z;
	lid = clamp(lid < 0.0 ? lid * expression : lid, -0.65, 1.0);
	float mw = clamp(1.0 + (face_b.y - 1.0) * expression, 0.4, 1.6);
	float curve = clamp(face_b.z * expression, -0.7, 0.7);
	float open = clamp(face_b.w, 0.0, 1.0);
	float my = mouth_y + face_c.x;
	float throat = face_c.y;
	bool blind = face_c.z > 0.5;
	float smile = max(curve, 0.0);
	vec2 look = blind ? vec2(0.0) : vec2(clamp(face_a.w * 0.62, -0.0062, 0.0062), clamp(face_b.x * 0.5, -0.0045, 0.0036));
	vec3 crease = shade_color * 0.8;

	// Raised brows crease the forehead (and age leaves the creases there);
	// a frown knits two lines between them.
	float raise = max(brow_y / 0.011, 0.0) + max(mood_tilt - 0.24, 0.0) * 2.0;
	float furrow = clamp(max(raise - 0.35, 0.0) * 1.2 + max(lines - 0.5, 0.0) * 1.1, 0.0, 0.8);
	if (furrow > 0.0) {
		for (int i = 0; i < 2; i++) {
			float w = 0.03 - 0.007 * float(i);
			float ly = brow_at.y + 0.017 + float(i) * 0.009 + brow_y * 0.6 + (mood_tilt * 0.008 - 0.002) * (1.0 - abs(q.x) / w);
			c = mix(c, crease, furrow * fill(abs(q.y - ly) - 0.00055 * (1.0 - 0.6 * abs(q.x) / w), px) * fill(abs(q.x) - w, px));
		}
	}
	if (mood_tilt < -0.3 || (mood_tilt > 0.45 && lid > 0.5)) {
		vec2 k0 = vec2(s * 0.0045, brow_at.y + 0.009);
		c = mix(c, crease, 0.8 * stroke(q, k0, k0 + vec2(s * 0.0012, -0.012), 0.0008, px));
	}
	// Crow's feet, with age.
	if (lines > 0.5) {
		vec2 k0 = vec2(s * (eye_at.x + eye_size.x * 2.6), eye_at.y);
		for (int i = -1; i < 2; i++) {
			c = mix(c, crease, (lines - 0.5) * 0.9 * stroke(q, k0, k0 + vec2(s * 0.0055, float(i) * 0.0022 + 0.0008), 0.0005, px));
		}
	}

	c = eye(q, s, c, lid, look, smile, px);

	// Brows: tilted up in the middle (sad, afraid) or down (angry). Thick,
	// blunt at the nose, thinner to the temple, hatched as a brush leaves them.
	float u = (q.x - s * brow_at.x) * s;
	float k = u / brow_size.x;
	float yc = brow_at.y + brow_y - u * tan(tilt) + brow_size.y * brow_arch * (0.5 - k * k);
	float thick = brow_size.y * max(1.0 + brow_taper * 0.57 - brow_taper * (k + 1.0), 0.25);
	float brow = fill(abs(q.y - yc) - thick, px) * fill(u - brow_size.x, px) * fill(-brow_size.x - u + (q.y - yc) * 0.35, px);
	float strand = teeth((u + (q.y - yc) * 0.9) / 0.0034);
	c = mix(c, mix(brow_color, c, 0.4 * step(0.72, strand) * along(k, -0.5, 0.1)), brow);

	// The lines from the nose to the mouth's corners: deeper with a smile.
	float mh = mouth_half * mw * (1.0 - 0.2 * open);
	float depth = max(lines - 0.35, 0.0) * 0.9 + smile * 1.3 + max(-curve, 0.0) * 0.6;
	vec2 n0 = vec2(s * 0.0185, 0.146);
	vec2 n1 = vec2(s * (mh + 0.0085 + 0.004 * smile), my - 0.003 + mh * tan(curve) * 0.5);
	c = mix(c, crease, min(depth, 0.75) * stroke(q, n0, n1, 0.0007, px));

	// The mouth: a dark line that curves at its corners, opens as they
	// talk, thins as it presses; a lip under it, and the lip's shadow.
	float mt = q.x / mh;
	float amt = abs(mt);
	float ly = my + mh * tan(curve) * pow(min(amt, 1.2), 1.6);
	float gap = open * 0.012 * pow(max(1.0 - mt * mt, 0.0), 0.8);
	// Open, the upper lip lifts a little and the jaw drops the rest.
	float dy = q.y - ly - gap * 0.3;
	float full = clamp(mw, 0.45, 1.2);
	float lip = 0.0046 * full;
	c = mix(c, shade_color * 0.9, 0.55 * fill(abs(dy + gap + lip + 0.0026 - 0.003 * mt * mt) - 0.0008, px) * fill(amt - 0.5, px / mh));
	c = mix(c, lip_color, 0.7 * fill(length(vec2(mt / 0.74, (dy + gap) / lip)) - 1.0, px / lip) * fill(dy + gap, px));
	c = mix(c, lip_color, 0.45 * fill(length(vec2(mt / 0.86, dy / (0.0024 * full))) - 1.0, px / (0.0024 * full)) * fill(-dy, px));
	if (amt < 1.0 && gap > px) {
		float inside = fill(dy, px) * fill(-gap - dy, px);
		c = mix(c, mouth_color, inside);
		c = mix(c, teeth_color, inside * step(0.004, gap) * fill(-0.0026 - dy, px) * fill(amt - 0.68, px / mh));
	}
	float line = (0.0011 + 0.0004 * (1.0 - amt)) * min(1.0, (1.06 - amt) / 0.25);
	c = mix(c, ink, fill(abs(dy) - line, px) * step(amt, 1.06));
	c = mix(c, ink, fill(abs(dy + gap) - line * 0.7, px) * step(amt, 1.0) * step(px, gap));
	if (curve > 0.18) {
		// A smile tucks in at its corners.
		vec2 k0 = vec2(s * (mh + 0.0012), my + mh * tan(curve) - 0.0015);
		c = mix(c, crease, 0.8 * stroke(q, k0, k0 + vec2(s * 0.0012, 0.004), 0.0007, px));
	}

	// The throat: the lump in it, lit from above, rises as he swallows.
	if (q.y < 0.078) {
		vec2 t = vec2(q.x / 0.0105, (q.y - (0.036 + throat * 0.028)) / 0.012);
		float lump = smoothstep(1.0, 0.45, length(t));
		c = mix(c, shade_color * 0.88, 0.6 * lump * smoothstep(0.3, -0.5, t.y));
		c = mix(c, skin_color, 0.4 * lump * smoothstep(-0.1, 0.6, t.y));
	}
	return c;
}

void fragment() {
	vec3 p = head_pos;
	float px = max(length(dFdx(p)), length(dFdy(p))) + 0.00001;
	if (texel > 0.0) {
		p = (floor(p / texel) + 0.5) * texel;
		px = 0.00001;
	}
	float a = atan(p.x, -p.z);
	float aa = abs(a);
	// The build marks the ears (1) and the nose (2) in the UVs.
	bool nose = UV.x > 1.5;
	bool ear = UV.x > 0.5 && !nose;
	// (`down`: how far a plane faces the ground, the underside of the jaw.)
	vec3 c = skin_paint(p, aa, along(-head_normal.y, 0.25, 0.7), nose, ear);
	if (!ear) {
		if (freckles > 0.0 && p.z < -0.02 && p.y > 0.138 && p.y < 0.2) {
			vec2 cell = floor(p.xy / 0.0034);
			vec2 at = (cell + 0.25 + 0.5 * vec2(hash2(cell), hash2(cell + 7.3))) * 0.0034;
			float there = step(hash2(cell + 3.1), 0.6 * freckles * (1.0 - along(abs(p.x), 0.03, 0.066)));
			c = mix(c, vec3(0.45, 0.27, 0.18), 0.5 * there * fill(length(p.xy - at) - 0.0005 - 0.0004 * hash2(cell + 1.7), px));
		}
		if (scar > 0.0 && a > 0.0) {
			vec2 g = vec2(a * 0.085, p.y);
			vec2 s0 = vec2(0.036, 0.1);
			vec2 s1 = vec2(0.086, 0.136);
			c = mix(c, shade_color * 0.9, scar * 0.7 * fill(seg(g, s0, s1) - 0.0016, px));
			c = mix(c, mix(skin_color, vec3(0.86, 0.74, 0.7), 0.7), scar * stroke(g, s0, s1, 0.0009, px));
		}
		if (!nose) {
			c = beard_paint(c, p, aa, px);
		}
		if (p.z < -0.03 && head_normal.z < -0.15) {
			c = face(p.xy, c, px);
		}
		if (!nose) {
			c = mix(c, hair_paint(p, a, px), hair_at(p, a, aa, px));
		}
	}
	ALBEDO = c * COLOR.rgb;
	ROUGHNESS = roughness;
	SPECULAR = specular;
}
