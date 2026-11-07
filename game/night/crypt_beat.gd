extends NightBeat
## Night 3's turn (design doc: "you see a light in the crypt. Investigate and
## you are spotted."). After a quiet stretch (the doc's pacing rule: a long
## stretch of nothing before the main event; greybox length here) a light
## shows in the crypt with a costumed figure standing by it, back turned.
## Going down, you are seen: Suspicion +10 (seen in a restricted area).

const SEEN_SUSPICION := 10

@export var quiet_time := 20.0
@export var light: Node3D
@export var hunter: Hunter
## The foot of the crypt stair.
@export var crypt: Marker3D
@export var crypt_radius := 4.0


func run() -> void:
	await wait(quiet_time)
	light.visible = true
	hunter.stand_still()
	await say("", "(A light, down in the crypt.)")
	var p := player()
	await until(func() -> bool: return p.global_position.distance_to(crypt.global_position) < crypt_radius)
	hunter.chase()
	GameState.raise_suspicion(SEEN_SUSPICION)
	GameState.set_flag(&"n3_seen_in_crypt")
