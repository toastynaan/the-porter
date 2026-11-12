extends NightBeat
## Night 3's turn (design doc: "you see a light in the crypt. At the foot of
## the stair, the figure by the light has his back to you because he is
## killing a bound pilgrim... You are spotted."). After a quiet stretch (the
## doc's pacing rule: a long stretch of nothing before the main event) a
## light shows in the crypt with a costumed figure by it, back turned. At the
## foot of the stair the death plays in front of him (the crypt pilgrim:
## gory, feeding the rite); then the figure turns, and he's seen: Suspicion
## +10 (seen in a restricted area), and the chase.

const SEEN_SUSPICION := 10

@export var quiet_time := 20.0
@export var light: Node3D
@export var hunter: Hunter
## The foot of the crypt stair.
@export var crypt: Marker3D
@export var crypt_radius := 4.0
## The bound pilgrim's death (the hunter is its killer_node).
@export var death: DeathScene
@export var light_lines := PackedStringArray(["(A light, down in the crypt.)"])
@export var death_lines := PackedStringArray()


func run() -> void:
	await wait(quiet_time)
	light.visible = true
	hunter.stand_still()
	await say_lines(light_lines)
	var p := player()
	await until(func() -> bool: return p.global_position.distance_to(crypt.global_position) < crypt_radius)
	if death:
		await death.play()
		death.turn_to(p.global_position)
		await say_lines(death_lines)
	hunter.chase()
	GameState.raise_suspicion(SEEN_SUSPICION)
	GameState.set_flag(GameState.tonight("seen_in_crypt"))
