class_name Footprints
extends Node3D
## Footprints in the snow (night 6; docs/log/full-game-run.md, "Weather"): the
## porter and the hunters leave prints outdoors that stay for the night, and
## each can follow the other's: a hunter who loses the porter goes to his
## freshest print near where he lost him (Hunter._lose_track).

const MAX_PRINTS := 400
const PRINT_SIZE := Vector3(0.14, 0.3, 0.3)

## The prints: [position, time, whose ("porter" or "hunter")], oldest first.
var marks: Array = []

var _mat: StandardMaterial3D
var _player: Player


func _ready() -> void:
	add_to_group(&"footprints")
	_mat = StandardMaterial3D.new()
	_mat.albedo_color = Color(0.32, 0.33, 0.36)
	_hook.call_deferred()


func _hook() -> void:
	if not is_inside_tree():
		return
	_player = get_tree().get_first_node_in_group(&"player") as Player
	if _player:
		_player.stepped.connect(func(_surface: String, _running: bool) -> void: leave(_player.global_position, _player.rotation.y, &"porter"))


static func active(tree: SceneTree) -> bool:
	return Weather.now(tree) == Weather.Kind.SNOW


## A print at `at`, if it's outdoors in the snow.
func leave(at: Vector3, yaw: float, whose: StringName) -> void:
	if not active(get_tree()) or _roofed(at):
		return
	var d := Decal.new()
	var tex := GradientTexture2D.new()
	var g := Gradient.new()
	g.set_color(0, Color(0.18, 0.19, 0.22, 0.85))
	g.set_color(1, Color(0.18, 0.19, 0.22, 0.0))
	tex.gradient = g
	tex.fill = GradientTexture2D.FILL_RADIAL
	tex.fill_from = Vector2(0.5, 0.5)
	tex.fill_to = Vector2(1.0, 0.5)
	d.texture_albedo = tex
	d.size = PRINT_SIZE
	d.cull_mask = 1048573
	add_child(d)
	d.global_transform = Transform3D(Basis(Vector3.UP, yaw), at + Vector3.UP * 0.05)
	marks.append([at, Time.get_ticks_msec(), whose])
	if marks.size() > MAX_PRINTS:
		marks.pop_front()
		get_child(0).queue_free()


## The freshest print of `whose` within `radius` of `near`, or Vector3.INF.
func freshest(whose: StringName, near: Vector3, radius: float) -> Vector3:
	for i in range(marks.size() - 1, -1, -1):
		var p: Array = marks[i]
		if p[2] == whose and (p[0] as Vector3).distance_to(near) < radius:
			return p[0]
	return Vector3.INF


func count(whose: StringName) -> int:
	return marks.filter(func(p: Array) -> bool: return p[2] == whose).size()


func _roofed(at: Vector3) -> bool:
	var q := PhysicsRayQueryParameters3D.create(at + Vector3.UP * 1.0, at + Vector3.UP * 30.0, Layers.WORLD)
	return not get_world_3d().direct_space_state.intersect_ray(q).is_empty()
