shader_type spatial;
// Coals in a fire basket: each lump as hot as its vertex colour says, the
// heat coming and going across the heap.
render_mode unshaded;

uniform vec3 glow : source_color = vec3(1.0, 0.36, 0.08);
uniform vec3 ash : source_color = vec3(0.03, 0.025, 0.022);
uniform float energy = 2.4;

varying vec3 at;

void vertex() {
	at = VERTEX;
}

void fragment() {
	float pulse = 0.65 + 0.35 * sin(TIME * 2.3 + at.x * 31.0 + at.z * 23.0 + at.y * 17.0);
	ALBEDO = mix(ash, glow * energy, COLOR.r * COLOR.r * pulse);
}
