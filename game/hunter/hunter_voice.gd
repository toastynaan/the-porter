class_name HunterVoice
extends Node
## Hunters talk (docs/mechanics.md, "Hunters talk"): from night 4 they call
## the porter's name in a voice he knows, shown as a subtitle with where it
## comes from: "Alric..." (behind you, Osric). Drugged (Dose 50+), the name
## is missing and it's only "A voice". Before night 4 they're silent. While
## a hunter chases or searches, he calls every EVERY seconds.

const FROM_NIGHT := 4
const DRUGGED := 50.0
const EVERY := Vector2(6.0, 11.0)
const CALLS: Array[String] = ["Alric...", "Brother Alric.", "Come out, porter.", "We only want to talk, Alric."]

var _t := 3.0
var _rng := RandomNumberGenerator.new()

@onready var _hunter: Hunter = get_parent() as Hunter


func _process(delta: float) -> void:
	if _hunter == null or _hunter.dormant or GameState.night < FROM_NIGHT:
		return
	if _hunter.state != Hunter.State.CHASE and _hunter.state != Hunter.State.SEARCH:
		return
	_t -= delta
	if _t <= 0.0:
		_t = _rng.randf_range(EVERY.x, EVERY.y)
		call_out()


## The line he calls now, as the porter hears it.
func call_out() -> String:
	var p := get_tree().get_first_node_in_group(&"player") as Player
	if p == null:
		return ""
	var who := "a voice" if GameState.dose >= DRUGGED or _hunter.wearer == &"" else People.display_name(_hunter.wearer)
	var line := "\"%s\" (%s, %s)" % [CALLS[_rng.randi() % CALLS.size()], direction(p, _hunter.global_position), who]
	Talk.say("", line)
	return line


## Where `at` is from him: ahead, behind, to the left or right, above, below.
static func direction(p: Player, at: Vector3) -> String:
	var local := p.global_transform.affine_inverse() * at
	if local.y > 2.5:
		return "above you"
	if local.y < -2.5:
		return "below you"
	if absf(local.x) > absf(local.z):
		return "to your right" if local.x > 0.0 else "to your left"
	return "ahead of you" if local.z < 0.0 else "behind you"
