class_name Thrown
extends RigidBody3D
## Something the porter has thrown (docs/mechanics.md, "Throwing"): it flies
## about 8 m, and where it first lands makes a noise the hunters go to look
## at (Investigate). How far it carries depends on what it lands on: stone
## 10 m, wood 8 m, mud or grass 4 m. It stays where it comes to rest; the
## cult tidies it away by the next night (it isn't kept).

signal landed(at: Vector3, surface: String)

const CLATTER := preload("res://art/sfx/sfx_clatter.wav")
const HEARD := {"stone": 10.0, "wood": 8.0, "mud": 4.0, "grass": 4.0}
## Throw speed, m/s, and how much of it goes up.
const SPEED := 8.5
const LOFT := 0.25

var item := &"stone"
var has_landed := false
var surface := ""


func _ready() -> void:
	add_to_group(&"thrown")
	collision_layer = 0
	collision_mask = Layers.WORLD | Layers.DOOR
	contact_monitor = true
	max_contacts_reported = 1
	mass = 0.3
	var shape := CollisionShape3D.new()
	var sphere := SphereShape3D.new()
	sphere.radius = 0.04
	shape.shape = sphere
	add_child(shape)
	var mesh := MeshInstance3D.new()
	var ball := SphereMesh.new()
	ball.radius = 0.04
	ball.height = 0.07
	mesh.mesh = ball
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.45, 0.43, 0.4) if item == &"stone" else Color(0.78, 0.74, 0.62)
	mesh.material_override = mat
	add_child(mesh)
	body_entered.connect(_on_body)


## How far a landing on `on` is heard, m.
static func heard_within(on: String) -> float:
	return float(HEARD.get(on, 10.0))


func _on_body(body: Node) -> void:
	if has_landed:
		return
	has_landed = true
	surface = String(body.get_meta(&"surface", "stone"))
	Earshot.make(self, global_position, heard_within(surface), self)
	if AudioOut.enabled():
		var a := AudioStreamPlayer3D.new()
		a.stream = CLATTER if surface in ["stone", "wood"] else load("res://art/sfx/sfx_step_%s_0.wav" % surface)
		a.unit_size = 4.0
		add_child(a)
		a.play()
	landed.emit(global_position, surface)
