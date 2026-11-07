class_name NightBeat
extends Node
## One beat of a night (design doc, "Night-by-night script"). The director
## sets the beat's `phase` and awaits run(). A beat with a `bell` is where the
## night picks up again after a death sends it back to that bell.

@export var phase := GameState.Phase.SUPPER
@export var bell := &""


## Does the beat; returns when it is over. Beats override this.
func run() -> void:
	await get_tree().process_frame


func player() -> Player:
	return get_tree().get_first_node_in_group(&"player") as Player


func say(speaker: String, text: String) -> void:
	await Talk.say(speaker, text)


## Fades the screen if the game's capture flow (and its fade) is there.
func fade_to(alpha: float, seconds: float) -> void:
	var flow := get_tree().get_first_node_in_group(&"capture_flow") as CaptureFlow
	if flow:
		await flow.fade.fade_to(alpha, seconds)


func until(condition: Callable) -> void:
	while not condition.call():
		await get_tree().physics_frame


func wait(seconds: float) -> void:
	await get_tree().create_timer(seconds, false, true).timeout


## The Marker3D children of `holder`, as positions.
func points(holder: Node) -> Array[Vector3]:
	var out: Array[Vector3] = []
	for c in holder.get_children():
		if c is Marker3D:
			out.append((c as Marker3D).global_position)
	return out
