class_name Fire
extends Node3D
## Fire on night 6 (docs/systems/mechanics.md, "Fire"): hold the lantern to this
## marked spot (the granary's sacks, the crypt's hangings) for LIGHT_TIME
## seconds, from within REACH m and looking at it, and it catches. Then it
## spreads along `path` (its Marker3D children, in order) at SPREAD m/s,
## a flame every metre. Each flame makes smoke around it: in it he sees
## SMOKE_SIGHT m, and he chokes; SMOKE_DEATH seconds of breathing it and he
## collapses, which is death. Holding his breath stops the choking. Walking
## into a flame kills him. Death takes him back to the last save, before he
## set it. Lit, it sets fire_<id>; the crypt's, with the cult's book still on
## the altar, burns the book too.

signal lit

const LIGHT_TIME := 2.0
const REACH := 2.5
const SPREAD := 1.0
const SMOKE_RADIUS := 3.5
const SMOKE_SIGHT := 3.0
const SMOKE_DEATH := 6.0
const FLAME_RADIUS := 0.9

@export var id := &""
## The path the flames take, from this spot.
@export var path: Array[Marker3D] = []
## The book on the crypt's altar (burned with it if still there).
@export var book: Node3D

var burning := false
var flames: Array[Node3D] = []

var _hold := 0.0
var _spread := 0.0
var _choke := 0.0
var _points: Array[Vector3] = []
var _length := 0.0
var _env: Environment
var _fog_before := -1.0


func _ready() -> void:
	add_to_group(&"fire_spots")
	burning = GameState.has_flag(StringName("fire_" + String(id)))


func _physics_process(delta: float) -> void:
	var p := get_tree().get_first_node_in_group(&"player") as Player
	if p == null:
		return
	if not burning:
		var lantern := _lantern(p)
		var holding := lantern != null and not lantern.out and not lantern.covered \
			and p.camera.global_position.distance_to(global_position) < REACH \
			and ViewCheck.off_centre(p.camera, global_position) < 30.0
		_hold = _hold + delta if holding else 0.0
		if _hold >= LIGHT_TIME:
			light()
		return
	_grow(delta)
	_smoke(p, delta)


## It catches.
func light() -> void:
	if burning and not flames.is_empty():
		return
	burning = true
	GameState.set_flag(StringName("fire_" + String(id)))
	if book and book.visible and not GameState.satchel.has(&"book"):
		GameState.set_flag(&"book_burned")
		book.visible = false
	_points = [global_position]
	for m in path:
		_points.append(m.global_position)
	_length = 0.0
	for i in range(1, _points.size()):
		_length += _points[i - 1].distance_to(_points[i])
	_flame_at(global_position)
	lit.emit()


func _grow(delta: float) -> void:
	if _spread >= _length:
		return
	var before := floori(_spread)
	_spread = minf(_spread + SPREAD * delta, _length)
	for i in range(before + 1, floori(_spread) + 1):
		_flame_at(_along(float(i)))


func _along(d: float) -> Vector3:
	var left := d
	for i in range(1, _points.size()):
		var seg := _points[i - 1].distance_to(_points[i])
		if left <= seg:
			return _points[i - 1].lerp(_points[i], left / maxf(seg, 0.001))
		left -= seg
	return _points[-1]


func _flame_at(at: Vector3) -> void:
	var f := Node3D.new()
	var glow := OmniLight3D.new()
	glow.light_color = Color(1.0, 0.55, 0.2)
	glow.light_energy = 2.5
	glow.omni_range = 6.0
	glow.position = Vector3.UP * 0.8
	f.add_child(glow)
	var body := MeshInstance3D.new()
	var mesh := CylinderMesh.new()
	mesh.top_radius = 0.05
	mesh.bottom_radius = 0.5
	mesh.height = 1.4
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(1.0, 0.45, 0.1)
	mat.emission_enabled = true
	mat.emission = Color(1.0, 0.5, 0.15)
	mat.emission_energy_multiplier = 2.0
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mesh.material = mat
	body.mesh = mesh
	body.position = Vector3.UP * 0.7
	f.add_child(body)
	get_parent().add_child(f)
	f.global_position = at
	flames.append(f)


## Smoke: short sight and choking; a flame: death.
func _smoke(p: Player, delta: float) -> void:
	var in_smoke := false
	for f in flames:
		var d := f.global_position.distance_to(p.global_position)
		if d < FLAME_RADIUS:
			_die(&"fire")
			return
		if d < SMOKE_RADIUS:
			in_smoke = true
	_sight(in_smoke)
	var breath := p.get_node_or_null(^"Breath") as Breath
	var held := breath != null and breath.holding
	if in_smoke and not held:
		_choke += delta
		if _choke >= SMOKE_DEATH:
			_die(&"smoke")
	else:
		_choke = maxf(_choke - delta, 0.0)


func _sight(on: bool) -> void:
	if _env == null:
		var we := get_tree().get_first_node_in_group(&"world_environment") as WorldEnvironment
		if we == null:
			for n in get_tree().root.find_children("*", "WorldEnvironment", true, false):
				we = n as WorldEnvironment
				break
		if we:
			_env = we.environment
	if _env == null:
		return
	if on and _fog_before < 0.0:
		_fog_before = _env.volumetric_fog_density
		_env.volumetric_fog_density = 1.0 / SMOKE_SIGHT
	elif not on and _fog_before >= 0.0:
		_env.volumetric_fog_density = _fog_before
		_fog_before = -1.0


func _die(cause: StringName) -> void:
	set_physics_process(false)
	_sight(false)
	var flow := get_tree().get_first_node_in_group(&"capture_flow") as CaptureFlow
	if flow:
		flow.die(cause)


func _lantern(p: Player) -> Lantern:
	for n in p.find_children("*", "", true, false):
		if n is Lantern:
			return n as Lantern
	return null
