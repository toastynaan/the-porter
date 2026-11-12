class_name SeenWatch
extends Node
## Being seen somewhere he shouldn't be (docs/mechanics.md, "Being seen").
## While the porter is in a restricted place (group "restricted": Restricted
## boxes, and the ground near a body), any brother in the world who can see
## him by the hunters' sight rules (lantern light, distance, his view)
## sees him: Suspicion +10, once per place per night, and the brother tells
## someone, so it comes up at dawn (remarks()).

signal seen(place: StringName, by: Node3D)

const SUSPICION := 10
const INTERVAL := 0.2

var _t := 0.0


func _ready() -> void:
	add_to_group(&"seen_watch")


func _physics_process(delta: float) -> void:
	_t += delta
	if _t < INTERVAL:
		return
	_t = 0.0
	var p := get_tree().get_first_node_in_group(&"player") as Player
	if p == null or p.hiding:
		return
	for r: Node in get_tree().get_nodes_in_group(&"restricted"):
		var place: StringName = r.get(&"place")
		if place == &"" or GameState.has_flag(flag(place)) or not r.call(&"active") or not r.call(&"contains", p.global_position):
			continue
		for b: Node3D in get_tree().get_nodes_in_group(&"brothers"):
			if b.is_visible_in_tree() and sees(b, p):
				_seen(r, b)
				break


## Whether brother `b` can see the porter: from his eyes, facing his way,
## by the hunters' rules.
static func sees(b: Node3D, p: Player) -> bool:
	var eye := b.global_position + Vector3.UP * 1.6
	return HunterSenses.sees_from(b, eye, -b.global_basis.z, p)


static func flag(place: StringName) -> StringName:
	return GameState.tonight("seen_" + String(place))


func _seen(r: Node, b: Node3D) -> void:
	GameState.set_flag(flag(r.get(&"place")), StringName(b.name))
	GameState.set_flag(GameState.tonight("seen_where_" + String(r.get(&"place"))), String(r.get(&"where")))
	GameState.raise_suspicion(SUSPICION)
	seen.emit(r.get(&"place"), b)


## Tonight's: who saw him where, as the dawn will put it.
static func remarks() -> PackedStringArray:
	var out := PackedStringArray()
	var prefix := String(GameState.tonight("seen_"))
	for f: StringName in GameState.flags:
		var key := String(f)
		if key.begins_with(prefix) and not key.begins_with(String(GameState.tonight("seen_where_"))):
			var place := key.trim_prefix(prefix)
			var where: String = GameState.get_flag(GameState.tonight("seen_where_" + place), "where you shouldn't be")
			out.append("%s saw you %s last night, and has said so." % [People.display_name(StringName(GameState.flags[f])), where])
	return out
