shader_type sky;
// The sky (Look and Feel, "Lighting rules": moonlight is fill, not sight; day
// scenes are flat and grey). At night it is one flat colour, the moonlight
// blue the game has always had. With daylight in it (Daylight sets `light`)
// it becomes an overcast sky: a low deck of rain cloud drifting over, and at
// dusk a strip of dying light along the horizon where the sun went down
// (`glow_dir`): pale straw at the rim, going grey and then slate above it,
// barred with cloud. It is a cold light. Purple and rose are kept for the
// drugged look, so there is none here. The Environment's background energy dims
// the whole of it as night comes, so the last thing left is the strip.

// 0 at night, 1 in full daylight (Daylight.light).
uniform float light : hint_range(0.0, 1.0) = 0.0;
// Toward where the sun set (or will rise), in the world.
uniform vec3 glow_dir = vec3(-1.0, 0.0, 0.2);
// The night's one colour: moonlight (#6E7F96).
uniform vec3 night_color : source_color = vec3(0.431, 0.498, 0.588);
// The cloud deck: in shadow, and its lighter breaks.
uniform vec3 cloud_dark : source_color = vec3(0.13, 0.15, 0.2);
uniform vec3 cloud_light : source_color = vec3(0.42, 0.47, 0.55);
// The strip of light: at the rim, above it, and higher still.
uniform vec3 glow_rim : source_color = vec3(0.95, 0.76, 0.47);
uniform vec3 glow_mid : source_color = vec3(0.56, 0.5, 0.44);
uniform vec3 glow_high : source_color = vec3(0.27, 0.3, 0.36);
// How bright the strip is against the rest (the sky's energy scales both).
uniform float glow_strength : hint_range(0.0, 8.0) = 2.2;
// How high the strip reaches, and how far round the horizon it spreads.
uniform float glow_height : hint_range(0.02, 0.6) = 0.14;
uniform float glow_spread : hint_range(0.5, 8.0) = 2.6;
// A second, cold break in the cloud low on another side of the sky (night 0:
// behind the city, so its wall and towers stand black against something).
// None unless Daylight asks for it.
uniform vec3 break_dir = vec3(1.0, 0.0, 0.0);
uniform float break_strength : hint_range(0.0, 4.0) = 0.0;
uniform vec3 break_color : source_color = vec3(0.47, 0.54, 0.66);
uniform float break_height : hint_range(0.02, 0.6) = 0.24;
uniform float break_spread : hint_range(0.5, 12.0) = 5.0;
uniform sampler2D clouds : repeat_enable, filter_linear_mipmap;
// 0 clear, 1 a solid deck.
uniform float cloud_cover : hint_range(0.0, 1.0) = 0.7;
uniform vec2 wind = vec2(0.0035, 0.0012);

float deck(vec2 uv) {
	float n = texture(clouds, uv).r * 0.6 + texture(clouds, uv * 2.3 + vec2(0.37, 0.11)).r * 0.4;
	return n;
}

void sky() {
	vec3 d = normalize(EYEDIR);
	float h = d.y;
	// How much of the day is left, and how much of that is dusk.
	float day = smoothstep(0.0, 0.3, light);
	float dusk = smoothstep(0.02, 0.3, light) * (1.0 - smoothstep(0.8, 1.0, light));

	// The cloud deck, seen from below: stretched toward the horizon.
	float up = max(h, 0.0);
	vec2 uv = d.xz / (up + 0.22) * 0.11 + wind * TIME;
	float n = deck(uv);
	float cover = smoothstep(1.0 - cloud_cover - 0.25, 1.0 - cloud_cover + 0.3, n);
	// Near the horizon the deck closes up and greys out in the haze.
	float haze = 1.0 - smoothstep(0.0, 0.3, up);
	vec3 overcast = mix(cloud_light, cloud_dark, cover * (1.0 - haze * 0.5));
	overcast = mix(overcast, mix(cloud_light, cloud_dark, 0.55), haze * 0.7);

	// The strip of light where the sun went down.
	vec2 flat_d = normalize(d.xz + vec2(1e-5));
	vec2 flat_g = normalize(glow_dir.xz + vec2(1e-5));
	float toward = pow(max(dot(flat_d, flat_g) * 0.5 + 0.5, 0.0), glow_spread);
	float rise = max(h, 0.0) / glow_height;
	float rim = exp(-rise * rise * 3.0);
	float mid = exp(-rise * 1.1);
	float high = exp(-rise * 0.35);
	vec3 strip = glow_rim * rim + glow_mid * mid * (1.0 - rim * 0.7) + glow_high * high * (1.0 - mid * 0.6);
	// Cloud lies across it in long level bars, seen edge on.
	// Twice round the cloud texture in one turn, so it meets itself.
	float round_about = atan(d.z, d.x) / TAU * 2.0;
	vec2 bar_uv = vec2(round_about + wind.x * TIME, h * 2.6 + 0.3);
	// (No mipmaps: where the turn meets itself the jump would pick the blurriest.)
	float bars = textureLod(clouds, bar_uv, 0.0).r * 0.6 + textureLod(clouds, bar_uv * vec2(2.0, 2.3) + vec2(0.37, 0.11), 0.0).r * 0.4;
	bars = smoothstep(0.42, 0.62, bars) * smoothstep(0.015, 0.06, h);
	strip *= mix(1.0, 0.22, bars);
	vec3 lit_belly = glow_mid * cover * mid * 0.35;
	vec3 dusk_sky = overcast * mix(1.0, 0.55, dusk) + (strip * glow_strength + lit_belly) * toward * dusk;
	// The cold break: a ragged pale band, torn across by the same bars of cloud.
	vec2 flat_b = normalize(break_dir.xz + vec2(1e-5));
	float toward_b = pow(max(dot(flat_d, flat_b) * 0.5 + 0.5, 0.0), break_spread);
	float rise_b = max(h, 0.0) / break_height;
	float band = exp(-rise_b * rise_b * 1.6) * mix(1.0, 0.25, bars) * mix(1.0, 0.55, cover);
	dusk_sky += break_color * band * break_strength * toward_b;

	// Just below the horizon the sky carries on as it is at the rim: distant
	// ground fades into it (the fog takes its colour from here). Further
	// down it goes to the ground's own dark.
	float below = smoothstep(-0.1, -0.55, h);
	dusk_sky = mix(dusk_sky, overcast * 0.35, below);

	// Night is the one flat colour; day brings the deck in.
	COLOR = mix(night_color, dusk_sky, day);
}
