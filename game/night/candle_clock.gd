class_name CandleClock
extends Node3D
## The candle clock on the porter's desk (design doc, "Core loop"; Look and
## Feel, "UI": time and the next duty are shown by the candle clock in your
## cell). A tall candle burns down from `start_hour` to `end_hour`; dark
## rings mark the duties. Look at it and press `interact` to read it.

signal read

@export var start_hour := 16.0
@export var end_hour := 31.0
## Height of the unburned candle, m.
@export var length := 0.36
## hour -> name of the mark ("supper", "Matins", "Lauds").
@export var marks := {17.25: "the supper bell", 24.0: "Matins", 30.0: "Lauds"}

var _wax: MeshInstance3D
var _flame: MeshInstance3D
var _rings: Dictionary = {}


func _ready() -> void:
	var wax := StandardMaterial3D.new()
	wax.albedo_color = Color("#D8C9A3")
	_wax = _mesh(_cylinder(0.022, 1.0), wax)
	var flame := StandardMaterial3D.new()
	flame.albedo_color = Color.BLACK
	flame.emission_enabled = true
	flame.emission = Color("#E0A458")
	flame.emission_energy_multiplier = 6.0
	var sphere := SphereMesh.new()
	sphere.radius = 0.007
	sphere.height = 0.026
	_flame = _mesh(sphere, flame)
	var ink := StandardMaterial3D.new()
	ink.albedo_color = Color("#2B1D12")
	for hour: float in marks:
		_rings[hour] = _mesh(_cylinder(0.0235, 0.006), ink)
	var area := Area3D.new()
	area.collision_layer = Layers.INTERACT
	area.collision_mask = 0
	area.monitoring = false
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(0.18, length + 0.08, 0.18)
	shape.shape = box
	shape.position = Vector3(0.0, length * 0.5, 0.0)
	area.add_child(shape)
	add_child(area)
	_update()


func _process(_delta: float) -> void:
	_update()


## Height of the wax left now, m.
func height() -> float:
	return length * clampf(1.0 - (GameState.hour - start_hour) / (end_hour - start_hour), 0.03, 1.0)


func interact(_by: Node) -> void:
	var next := ""
	for hour: float in marks:
		if GameState.hour < hour:
			next = marks[hour]
			break
	var line := "(The candle stands at %s." % NightClock.clock_text(GameState.hour)
	line += " The next mark is %s.)" % next if not next.is_empty() else " Past the last mark.)"
	read.emit()
	await Talk.say("", line)


func _update() -> void:
	var h := height()
	_wax.scale = Vector3(1.0, h, 1.0)
	_wax.position = Vector3(0.0, h * 0.5, 0.0)
	_flame.position = Vector3(0.0, h + 0.015, 0.0)
	for hour: float in _rings:
		var at := length * (1.0 - (hour - start_hour) / (end_hour - start_hour))
		var ring := _rings[hour] as MeshInstance3D
		ring.position = Vector3(0.0, at, 0.0)
		ring.visible = at < h


func _mesh(mesh: Mesh, mat: Material) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.material_override = mat
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(mi)
	return mi


func _cylinder(radius: float, height_m: float) -> CylinderMesh:
	var c := CylinderMesh.new()
	c.top_radius = radius
	c.bottom_radius = radius
	c.height = height_m
	c.radial_segments = 8
	c.rings = 1
	return c
