class_name DutyGlyph
extends Control
## The duty glyph (docs/mechanics.md, "The minimal HUD"): a small, dim candle
## flame, about 1° across, over the one person or thing the current duty
## needs (the nearest node in the "glyph_targets" group: wanted Duties, and
## people a beat marks), seen within RANGE and in clear view. Never during a
## chase, while hiding or talking, with the ledger or satchel up, or with
## the guidance setting off. Drawn at full resolution over the world render.

const RANGE := 10.0
## Degrees across, of the vertical field of view.
const SIZE_DEGREES := 1.0
const COLOR := Color(0.88, 0.64, 0.35, 0.42)

## main.gd: where the world render sits on screen, and at what scale.
@export var main: Node

## The target the glyph is over now, or null (tests read it).
var target: Node3D
var _at := Vector2.ZERO
var _size := 0.0


func _ready() -> void:
	add_to_group(&"duty_glyph")
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func _process(_delta: float) -> void:
	var was := target
	target = _pick()
	if target != null or was != null:
		queue_redraw()


## Whether the glyph may show at all now.
static func allowed(tree: SceneTree) -> bool:
	if not Settings.guidance:
		return false
	var p := tree.get_first_node_in_group(&"player") as Player
	if p == null or p.hiding != null or p.talking or Talk.talking:
		return false
	for h: Hunter in tree.get_nodes_in_group(&"hunters"):
		if not h.dormant and h.state == Hunter.State.CHASE:
			return false
	for view: Node in tree.get_nodes_in_group(&"held_books"):
		if view.get(&"showing") == true:
			return false
	return true


static func point_of(node: Node3D) -> Vector3:
	return node.call(&"glyph_point") if node.has_method(&"glyph_point") else node.global_position + Vector3.UP * 2.0


func _pick() -> Node3D:
	if not allowed(get_tree()):
		return null
	var p := get_tree().get_first_node_in_group(&"player") as Player
	var camera := p.camera
	var best: Node3D = null
	var best_d := RANGE
	for n: Node in get_tree().get_nodes_in_group(&"glyph_targets"):
		var node := n as Node3D
		if node == null or not node.is_visible_in_tree():
			continue
		var at := point_of(node)
		var d := camera.global_position.distance_to(at)
		if d < best_d and ViewCheck.on_screen(camera, [at]):
			best_d = d
			best = node
	if best:
		var screen := main.get(&"screen") as Control if main else null
		var px := float(main.get(&"pixel_scale")) if main else 1.0
		var origin := screen.position if screen else Vector2.ZERO
		_at = origin + camera.unproject_position(point_of(best)) * px
		var view_h := (screen.size.y if screen else size.y)
		_size = view_h * SIZE_DEGREES / maxf(camera.fov, 1.0)
	return best


func _draw() -> void:
	if target == null:
		return
	# A flame: a teardrop, point up.
	var w := maxf(_size * 0.55, 2.0)
	var h := maxf(_size, 3.0)
	var pts := PackedVector2Array()
	for i in 12:
		var a := TAU * i / 12.0
		pts.append(_at + Vector2(sin(a) * w * 0.5, -cos(a) * h * 0.35 + h * 0.15))
	pts[0] = _at + Vector2(0.0, -h * 0.7)
	draw_colored_polygon(pts, COLOR)
