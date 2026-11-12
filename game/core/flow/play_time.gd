class_name PlayTime
## The seconds of play since the last frame, for a beat or a scene that
## counts time in a loop awaiting the tree's frames. Those signals keep coming
## while the game is paused, so a loop that counted the frame's delta went on
## under the pause menu (the wagon drove on). Paused, no time passes. A loop
## that moves bodies awaits physics_frame() instead, which waits out the pause
## (moving them while physics is off upset Jolt later on).


## For a loop that awaits physics_frame.
static func physics(node: Node) -> float:
	return 0.0 if node.get_tree().paused else node.get_physics_process_delta_time()


## For a loop that awaits process_frame.
static func idle(node: Node) -> float:
	return 0.0 if node.get_tree().paused else node.get_process_delta_time()


## Awaits the next physics frame of play, waiting out any pause.
static func physics_frame(node: Node) -> void:
	await node.get_tree().physics_frame
	while node.get_tree().paused:
		await node.get_tree().physics_frame
