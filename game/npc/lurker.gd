class_name Lurker
extends Figure
## Someone down an alley off the street on the road in (night 0): seen for
## a moment from the wagon, and never met. What they do is `act`; it changes
## as the porter comes within `notice` metres of them.

enum Act {
	## Stands still, and turns slowly to keep facing him as he goes by.
	WATCH,
	## Steps back out of sight (to `retreat`, in their own space) as he comes near.
	WITHDRAW,
	## Rocks slowly on their feet, facing wherever they were put (a wall).
	SWAY,
	## Bent over something on the ground; straightens and turns to him.
	STOOP,
	## Doesn't move at all.
	STILL,
}

@export var act := Act.WATCH
## How near he must be for them to mark him, m.
@export var notice := 14.0
## Where a WITHDRAW figure goes, from where they were put, in their own space.
@export var retreat := Vector3(1.4, 0.0, 0.0)
## How far over a STOOP figure is bent, radians.
@export var bend := 0.95

var _home: Transform3D
var _yaw := 0.0
## 0 when he's far off, 1 once he has been near for a moment.
var _marked := 0.0
var _clock := 0.0


func _ready() -> void:
	_home = transform
	_yaw = rotation.y
	_clock = float(hash(name) % 100) * 0.1
	_pose()


func _process(delta: float) -> void:
	var p := get_tree().get_first_node_in_group(&"player") as Node3D
	if p == null or act == Act.STILL:
		return
	_clock += delta
	var here := get_parent_node_3d().to_global(_home.origin) if get_parent_node_3d() else _home.origin
	var to := p.global_position - here
	var near := to.length() < notice
	_marked = move_toward(_marked, 1.0 if near else 0.0, delta / (0.7 if near else 2.5))
	if near and (act == Act.WATCH or act == Act.STOOP) and Vector2(to.x, to.z).length() > 0.3:
		# Slowly: a head that follows the wagon.
		var want := atan2(-to.x, -to.z) - (get_parent_node_3d().global_rotation.y if get_parent_node_3d() else 0.0)
		_yaw = lerp_angle(_yaw, want, 1.0 - exp(-delta * (1.6 if act == Act.WATCH else 3.0) * _marked))
	_pose()


func _pose() -> void:
	var ease_in := _marked * _marked * (3.0 - 2.0 * _marked)
	match act:
		Act.WATCH:
			rotation = Vector3(0.0, _yaw, 0.0)
		Act.WITHDRAW:
			position = _home.origin + _home.basis * (retreat * ease_in)
		Act.SWAY:
			rotation = Vector3(-0.07 + sin(_clock * 0.8) * 0.06, _home.basis.get_euler().y, sin(_clock * 0.53) * 0.035)
		Act.STOOP:
			rotation = Vector3(-bend * (1.0 - ease_in), _yaw, 0.0)
