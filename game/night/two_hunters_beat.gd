extends NightBeat
## Two hunters for the first time (night 4's chase rule; design doc: "you see
## the demon in two places at once. If sober, you see two masked men. One
## loses his mask in the chase: it is Osric"). As the beat starts, one comes
## at him from `ahead` and one from `behind`, both on him at once. With both
## in view he sees the demon in two places (the note `two_demons`). Once
## Osric's hunter has been within `unmask_range` for a moment, his mask
## comes off; seeing his face is the note `osric_mask`. The chase is over
## once neither has been chasing or searching for `calm` seconds; they go.
## Caught, he dies (CaptureFlow: from night 3 every capture kills).

const HUNTER := preload("res://game/hunter/hunter.tscn")

@export var ahead: Marker3D
@export var behind: Marker3D
@export var wearers: Array[StringName] = [&"osric", &"ranulf"]
@export var unmask_range := 7.0
@export var calm := 6.0
@export var two_lines := PackedStringArray()
@export var unmask_lines := PackedStringArray()

var hunters: Array[Hunter] = []


func run() -> void:
	var p := player()
	for i in 2:
		var h := HUNTER.instantiate() as Hunter
		h.wearer = wearers[i] if i < wearers.size() else &""
		h.weapon = &"blade" if GameState.night >= 4 else &"cord"
		var at := (ahead if i == 0 else behind).global_transform
		h.transform = at
		get_parent().get_parent().add_child(h)
		hunters.append(h)
	await get_tree().physics_frame
	for h in hunters:
		h.always_search = true
		h.chase()
	var seen_two := false
	var unmasked := false
	var face_seen := false
	var near := 0.0
	var calm_for := 0.0
	while calm_for < calm:
		var dt := PlayTime.physics(self)
		var alive := hunters.filter(func(h: Variant) -> bool: return is_instance_valid(h))
		var on := alive.filter(func(h: Hunter) -> bool:
			return ViewCheck.on_screen(p.camera, [h.global_position + Vector3.UP * 1.5]))
		if not seen_two and on.size() == 2:
			seen_two = true
			GameState.note(&"two_demons")
			Talk.say("", two_lines[0] if not two_lines.is_empty() else "(It's in two places at once.)")
		var osric: Hunter = hunters[0] if is_instance_valid(hunters[0]) else null
		if not unmasked and osric and osric.global_position.distance_to(p.global_position) < unmask_range:
			near += dt
			if near > 0.6:
				unmasked = true
				osric.unmask()
		if unmasked and not face_seen and osric \
				and ViewCheck.on_screen(p.camera, [osric.global_position + Vector3.UP * 1.6]) \
				and ViewCheck.clear(p, p.camera.global_position, osric.global_position + Vector3.UP * 1.6):
			face_seen = true
			GameState.note(&"osric_mask")
			say_lines(unmask_lines)
		var busy := alive.any(func(h: Hunter) -> bool:
			return h.state == Hunter.State.CHASE or h.state == Hunter.State.SEARCH or h.state == Hunter.State.CAPTURE)
		calm_for = 0.0 if busy else calm_for + dt
		await get_tree().physics_frame
	for h in hunters:
		if is_instance_valid(h):
			h.queue_free()
	hunters.clear()
