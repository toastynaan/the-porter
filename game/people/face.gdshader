shader_type spatial;
// A real head's face (docs/systems/faces.md, "The real faces"): the
// character's painted atlas for the skin and hair (tools/build/people.py),
// and over it the eyes, brows, lids, mouth, creases and throat, drawn here
// from what the FaceRig sets each step (instance uniforms face_a..c). They
// are drawn on a grid of `texel` metres, so they read as a painted PSX face
// texture swapping, not as smooth shapes. Lit per vertex, nearest, snapped,
// like the rest of the person (person.gdshader).
//
// Head space: metres from the neck pivot, x his right, y up, -z forward.

render_mode vertex_lighting, cull_back, diffuse_lambert, specular_schlick_ggx;

#include "res://game/core/render/psx.gdshaderinc"

uniform sampler2D atlas : source_color, filter_nearest_mipmap, repeat_disable;
uniform float roughness : hint_range(0.0, 1.0) = 0.75;
uniform float specular : hint_range(0.0, 1.0) = 0.3;

// The face's layout on the head.
uniform vec2 eye_at = vec2(0.032, 0.184);
uniform vec2 eye_size = vec2(0.0142, 0.006);
uniform float iris_r = 0.0056;
uniform vec2 brow_at = vec2(0.033, 0.204);
// The brows' half length and half thickness; how far the middle arches (in
// thicknesses); how they slant at rest (radians: + the inner ends up, a
// worried look; - down, a stern one); how much they thin toward the temples
// (tools/build/people_kit.py, BROWS).
uniform vec2 brow_size = vec2(0.0165, 0.003);
uniform float brow_arch = 0.8;
uniform float brow_slant = 0.0;
uniform float brow_taper = 0.35;
uniform float mouth_y = 0.126;
uniform float mouth_half = 0.0245;
// How far a mood moves the face: the brows' rise and tilt, the mouth's
// curve and width, how wide the eyes go. 1 is the FaceRig's own numbers (a
// placeholder's box face); a painted face needs more to read at 4 m.
uniform float expression = 1.6;
// One texel of the face, metres.
uniform float texel = 0.0021;
// How deep the creases are drawn: age, weather.
uniform float lines : hint_range(0.0, 1.0) = 0.5;
uniform vec3 white_color : source_color = vec3(0.78, 0.74, 0.66);
uniform vec3 iris_color : source_color = vec3(0.3, 0.22, 0.15);
uniform vec3 ink : source_color = vec3(0.165, 0.114, 0.09);
uniform vec3 brow_color : source_color = vec3(0.18, 0.13, 0.1);
uniform vec3 lip_color : source_color = vec3(0.55, 0.33, 0.29);
uniform vec3 mouth_color : source_color = vec3(0.12, 0.05, 0.04);
uniform vec3 teeth_color : source_color = vec3(0.62, 0.58, 0.5);

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

float seg(vec2 p, vec2 a, vec2 b) {
	vec2 pa = p - a;
	vec2 ba = b - a;
	float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
	return length(pa - ba * h);
}

vec3 eye(vec2 q, float s, vec3 c, float lid, vec2 look, float smile, bool blind) {
	vec2 e = q - vec2(s * eye_at.x, eye_at.y);
	// The socket, darker under the brow.
	float sock = length(e / vec2(0.021, 0.0135) - vec2(0.0, 0.2));
	if (sock < 1.0) {
		c *= sock < 0.72 ? 0.8 : 0.89;
	}
	float t = e.x / eye_size.x;
	// The outer corner sits a little higher than the inner.
	float ey = e.y - 0.0007 * t * s;
	if (abs(t) < 1.0) {
		float w = 1.0 - t * t;
		float up_k = lid >= 0.0 ? 1.0 - 1.9 * lid : 1.0 - 1.8 * lid;
		// The upper lid follows the eye down.
		float upper = eye_size.y * up_k * pow(w, 0.55) + min(look.y, 0.0) * 0.5;
		float lower = -eye_size.y * (0.85 + 0.6 * max(-lid, 0.0)) * pow(w, 0.7) + smile * eye_size.y * 1.3 * w;
		if (upper > lower + texel * 0.5) {
			if (ey < upper && ey > lower) {
				vec2 ic = vec2(s * eye_at.x + look.x, eye_at.y + look.y);
				vec2 d = (q - ic) / iris_r;
				float r = length(d * vec2(1.0, 0.95));
				if (blind) {
					c = mix(white_color, vec3(0.72, 0.72, 0.68), r < 1.0 ? 0.6 : 0.0);
				} else if (r < 1.0) {
					c = r < 0.45 ? iris_color * 0.2 : iris_color;
					vec2 hl = ic + vec2(-0.4, 0.45) * iris_r;
					if (abs(q.x - hl.x) < texel * 0.5 && abs(q.y - hl.y) < texel * 0.5) {
						c = white_color * 1.25;
					}
				} else {
					c = white_color;
				}
				// The lid's shadow over the top of the eye.
				if (ey > upper - texel * 1.2) {
					c = ink;
				} else if (ey > upper - texel * 2.2) {
					c *= 0.72;
				}
			} else if (ey >= upper && ey < upper + texel * 0.9 + texel * 0.4 * (1.0 - abs(t))) {
				c = ink;
			} else if (ey > upper + eye_size.y * 1.05 && ey < upper + eye_size.y * 1.05 + texel && w > 0.25) {
				// The fold of the lid above.
				c *= 0.8;
			} else if (ey <= lower && ey > lower - texel) {
				c *= 0.8;
			}
		} else if (abs(ey - lower) < texel * 0.7) {
			// Shut: a dark line where the lids meet.
			c = ink;
		}
	} else if (e.x * s > 0.0 && abs(t) < 1.28 && abs(ey - 0.0006) < texel * 0.6 && lid < 0.9) {
		// The lashes' wing past the outer corner.
		c = mix(c, ink, 0.6);
	}
	return c;
}

vec3 face(vec2 q, vec3 skin) {
	float s = q.x < 0.0 ? -1.0 : 1.0;
	float brow_y = face_a.x * expression;
	// The mood's tilt, and with his brows' own slant.
	float mood_tilt = face_a.y * expression;
	float tilt = mood_tilt + brow_slant;
	float lid = face_a.z;
	lid = clamp(lid < 0.0 ? lid * expression : lid, -0.65, 1.0);
	float eye_x = face_a.w;
	float eye_y = face_b.x;
	float mw = clamp(1.0 + (face_b.y - 1.0) * expression, 0.4, 1.6);
	float curve = clamp(face_b.z * expression, -0.7, 0.7);
	float open = clamp(face_b.w, 0.0, 1.0);
	float my = mouth_y + face_c.x;
	float throat = face_c.y;
	bool blind = face_c.z > 0.5;
	float smile = max(curve, 0.0);
	vec2 look = vec2(clamp(eye_x * 0.8, -eye_size.x + iris_r * 0.7, eye_size.x - iris_r * 0.7), clamp(eye_y * 0.55, -0.0045, 0.004));
	if (blind) {
		look = vec2(0.0);
	}
	vec3 c = eye(q, s, skin, lid, look, smile, blind);

	// Brows: tilted up in the middle (sad, afraid) or down (angry).
	float u = (q.x - s * brow_at.x) * s;
	float bl = brow_size.x;
	if (abs(u) < bl) {
		float k = u / bl;
		float yc = brow_at.y + brow_y - u * tan(tilt) + brow_size.y * brow_arch * (1.0 - k * k) - brow_size.y * brow_arch * 0.5;
		float half_thick = brow_size.y * max(1.0 + brow_taper * 0.57 - brow_taper * (k + 1.0), 0.3);
		if (abs(q.y - yc) < half_thick) {
			c = brow_color;
		}
	}
	// Raised brows crease the forehead; a frown knits two lines between them.
	float raise = max(brow_y / 0.011, 0.0) + max(mood_tilt - 0.24, 0.0) * 2.0;
	if (raise > 0.45 && abs(q.x) < 0.03) {
		for (int i = 0; i < 2; i++) {
			float ly = brow_at.y + 0.019 + float(i) * 0.008 + brow_y * 0.6 + mood_tilt * 0.008 * (1.0 - abs(q.x) / 0.03);
			if (abs(q.y - ly) < texel * 0.5) {
				c *= 0.84;
			}
		}
	}
	if ((mood_tilt < -0.3 || (mood_tilt > 0.45 && lid > 0.5)) && abs(abs(q.x) - 0.0055) < texel * 0.55
			&& q.y > brow_at.y - 0.005 && q.y < brow_at.y + 0.008) {
		c *= 0.78;
	}

	// The lines from the nose to the mouth's corners: deeper with a smile.
	float mh = mouth_half * mw * (1.0 - 0.22 * open);
	vec2 n0 = vec2(s * 0.0175, 0.146);
	vec2 n1 = vec2(s * (mh + 0.007), my - 0.007 + mh * tan(curve) * 0.6);
	float depth = lines * 0.07 + smile * 0.45 + max(-curve, 0.0) * 0.25;
	if (seg(q, n0, n1) < texel * 0.6) {
		c *= 1.0 - min(depth, 0.32);
	}

	// The mouth: a line that curves at its corners, opens as they talk,
	// thins as it presses.
	float mt = q.x / mh;
	if (abs(mt) <= 1.0) {
		float ly = my + mh * tan(curve) * pow(abs(mt), 1.6);
		float gap = open * 0.012 * pow(max(1.0 - mt * mt, 0.0), 0.8);
		float thick = 0.0056 * clamp(mw, 0.45, 1.2) * (1.0 - 0.5 * abs(mt));
		// Open, the upper lip lifts a little and the jaw drops the rest.
		ly += gap * 0.3;
		float dy = q.y - ly;
		if (dy > -gap - texel * 0.5 && dy < texel * 0.5) {
			c = gap > texel ? mouth_color : mix(ink, lip_color, 0.2);
			if (gap > texel * 2.0 && dy > -texel * 1.0 && abs(mt) < 0.7) {
				c = teeth_color;
			}
		} else if (dy >= texel * 0.5 && dy < texel * 0.5 + thick * 0.6) {
			c = mix(c, lip_color, 0.5);
		} else if (dy <= -gap - texel * 0.5 && dy > -gap - texel * 0.5 - thick) {
			c = mix(c, lip_color, 0.7) * (dy > -gap - texel * 1.5 ? 1.0 : 1.08);
		} else if (dy <= -gap - texel * 0.5 - thick && dy > -gap - texel * 1.5 - thick && abs(mt) < 0.6) {
			c *= 0.8;
		}
	}
	if (curve > 0.18 && length(q - vec2(s * (mh + texel), my + mh * tan(curve))) < texel * 0.75) {
		c *= 0.78;
	}

	// The throat: the lump in it, lit from above, rises as he swallows.
	if (q.y < 0.076 && q.y > -0.02 && abs(q.x) < 0.014) {
		float d = (q.y - (0.034 + throat * 0.028)) / 0.008;
		if (abs(d) < 1.0 - abs(q.x) / 0.014) {
			c *= d > 0.0 ? 1.16 : 0.7;
		}
	}
	return c;
}

void fragment() {
	vec3 c = texture(atlas, UV).rgb * COLOR.rgb;
	if (head_pos.z < -0.03 && head_normal.z < -0.15) {
		vec2 q = (floor(head_pos.xy / texel) + 0.5) * texel;
		c = face(q, c);
	}
	ALBEDO = c;
	ROUGHNESS = roughness;
	SPECULAR = specular;
}
