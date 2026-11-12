// PSX look, shared by every 3D shader. In vertex(), after any change to
// VERTEX, write
//     PSX_VERTEX
// to snap the vertex to a coarse screen grid (the PlayStation's integer
// vertex positions: surfaces wobble and swim as the camera moves). The grid
// is psx_resolution / psx_snap pixels; psx_snap 0 turns it off.
//
// Only the active camera's pass snaps (its projection's [1][1] is
// psx_cam_fy, which a camera script must set every frame; nothing sets it yet). Shadow-map passes keep
// true positions: snapped casters in a light's own projection don't match the
// receivers' real positions, and the false shadows flash as the view (and the
// flashlight on it) moves. 0 (the editor) never snaps.
//
// The snap fades out between PSX_SNAP_FADE.x and .y metres from the camera:
// far off a pixel covers several centimetres, so snapping there does nothing
// visible except make surfaces a few cm apart (paint, papers, signs) fight.
//
// For affine ("warping") texture mapping, also declare
//     varying vec3 psx_affine;
// write `psx_affine = PSX_AFFINE(UV);` after PSX_VERTEX, and sample with
// `PSX_UV(psx_affine)` in fragment().

#ifndef PSX_GDSHADERINC
#define PSX_GDSHADERINC

global uniform float psx_snap;
global uniform vec2 psx_resolution;
global uniform float psx_cam_fy;

const vec2 PSX_SNAP_FADE = vec2(6.0, 20.0);

vec4 psx_snap_clip(vec4 clip) {
	if (psx_snap <= 0.0 || clip.w <= 0.0) {
		return clip;
	}
	vec2 grid = psx_resolution / psx_snap * 0.5;
	vec2 snapped = round(clip.xy / clip.w * grid) / grid * clip.w;
	clip.xy = mix(snapped, clip.xy, smoothstep(PSX_SNAP_FADE.x, PSX_SNAP_FADE.y, clip.w));
	return clip;
}

// Snap only when `projection` is the active camera's (not a shadow pass).
vec4 psx_snap_camera(vec4 clip, mat4 projection) {
	bool camera = projection[3][3] < 0.5 && abs(abs(projection[1][1]) - psx_cam_fy) < psx_cam_fy * 0.002;
	return camera ? psx_snap_clip(clip) : clip;
}

#define PSX_VERTEX POSITION = psx_snap_camera(PROJECTION_MATRIX * (MODELVIEW_MATRIX * vec4(VERTEX, 1.0)), PROJECTION_MATRIX);
#define PSX_AFFINE(uv) vec3((uv) * POSITION.w, POSITION.w)
#define PSX_UV(a) ((a).xy / (a).z)

#endif
