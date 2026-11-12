extends Node
## Development keys, in debug builds only:
##   [ and ]  ease Dose down or up by 25 over 2 seconds, to try the look anywhere
##   H        hungry or fed (shorter breath, slower sprint recovery, tremor)
##   K        the nearest awake hunter starts chasing you
##   J        the demon appears now, somewhere you aren't looking
##   G        out into the street by the gate, and back in again

const STEP := 25.0
const EASE_TIME := 2.0
## Just outside the gate in the lane, and just inside it in the outer court.
const STREET := Vector3(-43.4, 0.05, 2.0)
const COURT := Vector3(-36.0, 0.05, -2.0)


func _ready() -> void:
	if not OS.is_debug_build():
		queue_free()


func _unhandled_input(event: InputEvent) -> void:
	var key := event as InputEventKey
	if key == null or not key.pressed or key.echo:
		return
	match key.keycode:
		KEY_BRACKETLEFT:
			GameState.add_dose(-minf(STEP, GameState.dose), EASE_TIME)
		KEY_BRACKETRIGHT:
			GameState.add_dose(minf(STEP, GameState.DOSE_MAX - GameState.dose), EASE_TIME)
		KEY_H:
			GameState.set_flag(&"hungry", not GameState.is_hungry())
			print("hungry: ", GameState.is_hungry())
		KEY_K:
			_chase_me()
		KEY_J:
			for stalker: Stalker in get_tree().get_nodes_in_group(&"stalkers"):
				stalker.appear_now()
		KEY_G:
			var player := get_tree().get_first_node_in_group(&"player") as Player
			if player:
				var outside := player.global_position.x < -40.4
				player.place(COURT if outside else STREET, deg_to_rad(-90.0 if outside else 0.0))


func _chase_me() -> void:
	var player := get_tree().get_first_node_in_group(&"player") as Node3D
	if player == null:
		return
	var nearest: Hunter = null
	for hunter: Hunter in get_tree().get_nodes_in_group(&"hunters"):
		if not hunter.dormant and (nearest == null or hunter.global_position.distance_to(player.global_position)
				< nearest.global_position.distance_to(player.global_position)):
			nearest = hunter
	if nearest:
		nearest.chase()
