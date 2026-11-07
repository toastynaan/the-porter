extends Node
## Autoload TimeDirector: the game clock and hitstop. A slim port of big-kick's
## (no slow-motion table or Focus yet). RagdollController and PoseAnimator look
## it up at /root/TimeDirector.

## Game seconds: physics frames / tick rate, in step with the simulation.
func now() -> float:
	return Engine.get_physics_frames() / float(Engine.physics_ticks_per_second)

## Freeze every target that has freeze_hitstop(duration_real) (a zombie, the
## viewmodel) for `duration_real` s.
func hitstop(targets: Array, duration_real: float) -> void:
	for t in targets:
		if is_instance_valid(t) and t.has_method(&"freeze_hitstop"):
			t.freeze_hitstop(duration_real)

## The player keeps real time under any Engine.time_scale.
func player_time_factor() -> float:
	return 1.0 / maxf(Engine.time_scale, 0.01)

func player_delta(delta: float) -> float:
	return delta * player_time_factor()
