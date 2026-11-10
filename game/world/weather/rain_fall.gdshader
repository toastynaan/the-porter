shader_type particles;
// Rain (game/world/weather/weather.gd): each particle is one drop. It is
// born in a slab over the camera, falls on the wind, and where it lands
// (the roofs, the ground, the wagon: a height field over the camera,
// GPUParticlesCollisionHeightField3D) it becomes a splash for a moment.
// A drop born under a roof is put out at once, so it does not rain indoors
// or under an arch.
//
// What a drop is doing is kept in CUSTOM for the shader that draws it
// (rain_drop.gdshader): x 0 falling, 1 splashing, 2 gone; y how long it
// has splashed, s; z how level the thing it hit is; w a random number.

// Half the size of the slab drops are born in, m.
uniform vec3 extents = vec3(13.0, 0.5, 13.0);
uniform float speed = 11.5;
// The wind, m/s, and how much it gusts.
uniform vec3 wind = vec3(1.6, 0.0, 0.5);
uniform float gust = 0.5;
uniform float splash_time = 0.2;
// A drop already this deep in something when it is first found there was born inside it.
uniform float born_inside = 0.9;

float rand(inout uint seed) {
	seed = seed * 747796405u + 2891336453u;
	uint r = ((seed >> ((seed >> 28u) + 4u)) ^ seed) * 277803737u;
	return float((r >> 22u) ^ r) / 4294967295.0;
}

void start() {
	uint seed = (NUMBER + 1u) * 2654435761u + INDEX * 97u + RANDOM_SEED;
	if (RESTART_POSITION) {
		vec3 r = vec3(rand(seed), rand(seed), rand(seed)) * 2.0 - 1.0;
		TRANSFORM = mat4(1.0);
		TRANSFORM[3].xyz = (EMISSION_TRANSFORM * vec4(r * extents, 1.0)).xyz;
	}
	float k = rand(seed);
	if (RESTART_VELOCITY) {
		float blow = 1.0 + gust * sin(TIME * 0.7 + TRANSFORM[3].x * 0.05) * sin(TIME * 0.31 + 1.7);
		VELOCITY = wind * blow + vec3(0.0, -speed * mix(0.85, 1.15, k), 0.0);
	}
	if (RESTART_CUSTOM) {
		CUSTOM = vec4(0.0, 0.0, 0.0, k);
	}
}

void process() {
	if (CUSTOM.x < 0.5) {
		if (COLLIDED) {
			if (COLLISION_DEPTH > born_inside) {
				CUSTOM.x = 2.0;
			} else {
				TRANSFORM[3].xyz += COLLISION_NORMAL * COLLISION_DEPTH;
				CUSTOM.x = 1.0;
				CUSTOM.y = 0.0;
				CUSTOM.z = COLLISION_NORMAL.y;
			}
			VELOCITY = vec3(0.0);
		}
	} else {
		VELOCITY = vec3(0.0);
		CUSTOM.y += DELTA;
		if (CUSTOM.x < 1.5 && CUSTOM.y > splash_time) {
			CUSTOM.x = 2.0;
		}
	}
}
