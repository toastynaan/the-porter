shader_type spatial;
// A person's clothes, hands and what they carry (tools/build/people.py): the
// character's hand-painted atlas, read texel by texel (nearest), times the
// shading painted into the vertices, lit per vertex like the PlayStation's
// people (the locked PSX character style). Snaps to the PSX grid
// (psx.gdshaderinc).

render_mode vertex_lighting, cull_back, diffuse_lambert, specular_schlick_ggx;

#include "res://game/core/render/psx.gdshaderinc"

uniform sampler2D atlas : source_color, filter_nearest_mipmap, repeat_disable;
uniform float roughness : hint_range(0.0, 1.0) = 0.9;
uniform float specular : hint_range(0.0, 1.0) = 0.25;

void vertex() {
	PSX_VERTEX
}

void fragment() {
	ALBEDO = texture(atlas, UV).rgb * COLOR.rgb;
	ROUGHNESS = roughness;
	SPECULAR = specular;
}
