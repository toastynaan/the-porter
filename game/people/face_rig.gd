class_name FaceRig
extends Node3D
## A placeholder face (docs/systems/faces.md, "The face"): eyes that look
## about, brows, a mouth line, lids that blink, a throat that swallows, and
## the head it turns, nods and tips. It sits at the neck of a BrotherFigure,
## with the head's parts under it, and moves in steps at 15 frames a second
## like every other character. Between lines it idles on its owner's
## baseline (Faces.BASELINES); a line gives it a mood to hold, tells to
## play once, and a mouth that moves while it is up.
##
## The real character models will answer to the same calls: line(), mood(),
## tell(), speak().

## Steps a second, as every character moves (Look and Feel, "PSX").
const STEP := 1.0 / 15.0
## Where the face is on the head, from the neck: the face box's front.
const FACE_Y := 0.1
const FACE_Z := -0.137
const INK := Color("#2A1D17")
const BLIND_EYE := Color("#B9B2A6")

## Each mood's face: offsets from rest. brow_y and eye_y in metres; tilt,
## curve, pitch, yaw, roll in radians; lid 0 open to 1 shut (below 0: wide);
## mouth_w a scale.
const MOOD_POSES := {
	&"calm": {},
	&"warm": {"brow_tilt": 0.1, "curve": 0.15, "lid": 0.1},
	&"glad": {"brow_y": 0.006, "curve": 0.3, "mouth_w": 1.2},
	&"amused": {"brow_y": 0.004, "curve": 0.18, "roll": 0.05},
	&"grave": {"brow_y": -0.004, "curve": -0.05, "mouth_w": 0.9},
	&"sad": {"brow_tilt": 0.35, "curve": -0.2, "pitch": 0.08, "lid": 0.2},
	&"weary": {"lid": 0.45, "curve": -0.08, "pitch": 0.1},
	&"afraid": {"brow_y": 0.008, "brow_tilt": 0.3, "lid": -0.3, "mouth_w": 0.75},
	&"wary": {"brow_y": -0.004, "lid": 0.3, "pitch": -0.06},
	&"angry": {"brow_y": -0.006, "brow_tilt": -0.4, "mouth_w": 0.8, "pitch": -0.05},
	&"cold": {"brow_y": -0.002, "mouth_w": 0.95},
	&"ashamed": {"pitch": 0.25, "eye_y": -0.008, "mouth_w": 0.85},
	&"pleading": {"brow_tilt": 0.35, "brow_y": 0.005, "pitch": -0.05},
	&"pained": {"brow_tilt": 0.4, "lid": 0.8, "mouth_w": 1.1, "curve": -0.25},
	&"drunk": {"lid": 0.5, "curve": 0.15, "roll": 0.1},
	&"blank": {},
}
## How long each tell takes, seconds.
const TELL_TIME := {
	&"glance": 0.6, &"look down": 0.9, &"look away": 1.1, &"swallow": 0.45, &"blink": 0.6, &"lip": 0.7,
	&"jaw": 0.7, &"brow": 0.4, &"smile": 0.4, &"still": 0.0, &"nod": 0.45, &"shake": 0.7, &"flinch": 0.35,
}
const CHANNELS := ["brow_y", "brow_tilt", "lid", "eye_x", "eye_y", "mouth_w", "curve", "open", "mouth_y",
	"pitch", "yaw", "roll", "throat"]

## Whose face this is (a People id), found from the scene on ready.
var who := &""
## Hooded: the face is in shadow, nothing on it shows; the head still moves.
var hooded := false

var _base := {}
var _mood := &""
var _pose := {}
## Tells playing: [name, seconds in, seconds long, side (+1 or -1)].
var _tells: Array = []
var _still := 0.0
var _speak := 0.0
var _blink := 0.0
var _next_blink := 1.0
var _gaze := Vector2.ZERO
var _next_gaze := 1.0
var _clock := 0.0
var _acc := 0.0

var _eyes: Array[MeshInstance3D] = []
var _brows: Array[MeshInstance3D] = []
var _mouth: Array[MeshInstance3D] = []
var _throat: MeshInstance3D


func _ready() -> void:
	add_to_group(&"faces")
	who = _find_who()
	_base = Faces.baseline(who)
	_mood = _base.get("mood", &"calm")
	_next_blink = randf_range(0.5, 2.0)
	_build()
	for c in CHANNELS:
		_pose[c] = 0.0
	_pose["mouth_w"] = 1.0
	_apply()


## The face of `node`, or null: its own, or one anywhere under it (a
## character's look is an internal child).
static func on(node: Node) -> FaceRig:
	if node is FaceRig:
		return node
	for c in node.get_children(true):
		var r := on(c)
		if r:
			return r
	return null


## A line said by this face: hold `m` (its baseline if empty), play `tells`
## a moment in, one after another, and move the mouth for `seconds`. The
## drug adds what isn't there (docs/systems/faces.md, "The drug").
func line(m: StringName, tells: PackedStringArray, seconds: float) -> void:
	var dose := GameState.dose
	mood(m if m != &"" else _base.get("mood", &"calm"))
	speak(seconds)
	var at := randf_range(0.35, 0.7)
	for t in tells:
		tell(StringName(t), at)
		at += float(TELL_TIME.get(StringName(t), 0.5)) + 0.15
	var habit: StringName = _base.get("habit", &"")
	if habit != &"" and tells.is_empty() and randf() < 0.35:
		tell(habit, randf_range(0.6, maxf(0.7, seconds - 0.6)))
	if dose >= 50.0 and randf() < 0.35:
		var fake: StringName = Faces.TELLS[randi() % Faces.TELLS.size()]
		if fake != &"still":
			tell(fake, randf_range(0.2, maxf(0.3, seconds)))
	if dose >= 75.0 and randf() < 0.25:
		_flash_mood(Faces.MOODS[randi() % Faces.MOODS.size()], randf_range(0.3, seconds), 0.5)


func mood(m: StringName) -> void:
	if MOOD_POSES.has(m):
		_mood = m


## Plays a tell `delay` seconds from now.
func tell(t: StringName, delay := 0.0) -> void:
	if t == &"still":
		_still = maxf(_still, delay + maxf(_speak, 2.0))
		return
	if not TELL_TIME.has(t):
		return
	_tells.append([t, -delay, float(TELL_TIME[t]), 1.0 if randf() < 0.5 else -1.0])


## The mouth moves for `seconds`: they are talking.
func speak(seconds: float) -> void:
	_speak = maxf(seconds, 0.0)


func mood_now() -> StringName:
	return _mood


## Tells playing or waiting, by name.
func tells_now() -> Array[StringName]:
	var out: Array[StringName] = []
	for t: Array in _tells:
		out.append(t[0])
	if _still > 0.0:
		out.append(&"still")
	return out


func _flash_mood(m: StringName, delay: float, seconds: float) -> void:
	var was := _mood
	await get_tree().create_timer(delay, false).timeout
	if not is_inside_tree():
		return
	_mood = m
	await get_tree().create_timer(seconds, false).timeout
	if is_inside_tree() and _mood == m:
		_mood = was


func _process(delta: float) -> void:
	_acc += delta
	if _acc < STEP:
		return
	var dt := _acc
	_acc = 0.0
	_advance(dt)
	_apply()


func _advance(dt: float) -> void:
	_clock += dt
	_speak = maxf(_speak - dt, 0.0)
	_still = maxf(_still - dt, 0.0)
	var target := {}
	for c in CHANNELS:
		target[c] = 0.0
	target["mouth_w"] = 1.0
	for k: String in MOOD_POSES.get(_mood, {}):
		target[k] = float(target[k]) + float(MOOD_POSES[_mood][k])
	var blind: bool = _base.get("blind", false)
	var down: float = _base.get("down", 0.0)
	target["eye_y"] = float(target["eye_y"]) - 0.008 * down
	target["pitch"] = float(target["pitch"]) + 0.12 * down
	# Idle: blinks, small glances, breathing. Still, none of it.
	if _still <= 0.0:
		_next_blink -= dt
		if _next_blink <= 0.0:
			_blink = 0.15
			var rate: float = _base.get("blink", 0.3) * (0.3 if _mood == &"cold" or _mood == &"blank" else 1.0)
			_next_blink = randf_range(0.6, 1.4) / maxf(rate, 0.02)
		_next_gaze -= dt
		if _next_gaze <= 0.0 and not blind:
			var g: float = _base.get("gaze", 0.3)
			_gaze = Vector2(randf_range(-1.0, 1.0), randf_range(-0.6, 0.6)) * 0.006 * g
			_next_gaze = randf_range(1.2, 3.5)
		target["pitch"] = float(target["pitch"]) + sin(_clock * 1.6) * 0.012
	_blink = maxf(_blink - dt, 0.0)
	if _blink > 0.0 and not blind:
		target["lid"] = 1.0
	target["eye_x"] = float(target["eye_x"]) + _gaze.x
	target["eye_y"] = float(target["eye_y"]) + _gaze.y
	# Talking: the mouth opens and shuts in steps.
	if _speak > 0.0:
		target["open"] = 0.5 + 0.5 * sin(_clock * 37.0) if fmod(_clock, 0.9) < 0.75 else 0.0
	# Tells, on top.
	for t: Array in _tells:
		t[1] = float(t[1]) + dt
		var p := float(t[1]) / float(t[2])
		if p >= 0.0 and p <= 1.0:
			_tell_pose(t[0], p, float(t[3]), target, blind)
	_tells = _tells.filter(func(t: Array) -> bool: return float(t[1]) < float(t[2]))
	# Moods ease; tells and blinks snap, as they would.
	for c in CHANNELS:
		var snap: bool = c in ["lid", "open", "throat", "eye_x", "eye_y"]
		_pose[c] = target[c] if snap else lerpf(float(_pose[c]), float(target[c]), clampf(dt * 9.0, 0.0, 1.0))


func _tell_pose(t: StringName, p: float, side: float, pose: Dictionary, blind: bool) -> void:
	var bump := sin(p * PI)
	var hold := clampf(minf(p, 1.0 - p) * 5.0, 0.0, 1.0)
	match t:
		&"glance":
			if not blind:
				pose["eye_x"] = float(pose["eye_x"]) + 0.009 * side * hold
		&"look down":
			if not blind:
				pose["eye_y"] = float(pose["eye_y"]) - 0.009 * hold
			pose["pitch"] = float(pose["pitch"]) + 0.14 * hold
		&"look away":
			pose["yaw"] = float(pose["yaw"]) + 0.5 * side * hold
			if not blind:
				pose["eye_x"] = float(pose["eye_x"]) + 0.008 * side * hold
		&"swallow":
			pose["throat"] = bump
			pose["pitch"] = float(pose["pitch"]) + 0.04 * bump
		&"blink":
			if fmod(p * 3.0, 1.0) < 0.45:
				pose["lid"] = 1.0
		&"lip":
			pose["mouth_w"] = float(pose["mouth_w"]) * (1.0 - 0.4 * hold)
			pose["mouth_y"] = float(pose["mouth_y"]) + 0.004 * hold
			pose["open"] = 0.0
		&"jaw":
			pose["mouth_w"] = float(pose["mouth_w"]) * (1.0 - 0.15 * hold)
			pose["pitch"] = float(pose["pitch"]) - 0.06 * hold
			pose["open"] = 0.0
		&"brow":
			pose["brow_y"] = float(pose["brow_y"]) + 0.009 * bump
		&"smile":
			pose["curve"] = float(pose["curve"]) + 0.35 * bump
			pose["mouth_w"] = float(pose["mouth_w"]) + 0.2 * bump
		&"nod":
			pose["pitch"] = float(pose["pitch"]) + 0.16 * bump
		&"shake":
			pose["yaw"] = float(pose["yaw"]) + 0.22 * sin(p * TAU * 2.0) * bump
		&"flinch":
			pose["pitch"] = float(pose["pitch"]) - 0.14 * bump
			pose["roll"] = float(pose["roll"]) + 0.08 * side * bump


func _apply() -> void:
	rotation = Vector3(-float(_pose["pitch"]), float(_pose["yaw"]), float(_pose["roll"]))
	if hooded:
		return
	var lid := clampf(float(_pose["lid"]), -0.4, 1.0)
	for i in _eyes.size():
		var e := _eyes[i]
		var sx := -1.0 if i == 0 else 1.0
		e.position = Vector3(sx * 0.032 + float(_pose["eye_x"]), FACE_Y + 0.025 + float(_pose["eye_y"]) - 0.003 * maxf(lid, 0.0), FACE_Z)
		e.scale = Vector3(1.0, maxf(1.0 - lid, 0.08), 1.0)
	for i in _brows.size():
		var b := _brows[i]
		var sx := -1.0 if i == 0 else 1.0
		b.position = Vector3(sx * 0.032, FACE_Y + 0.05 + float(_pose["brow_y"]), FACE_Z)
		# Tilt up raises the inner ends (sad, afraid); down lowers them (angry).
		b.rotation.z = -sx * float(_pose["brow_tilt"])
	var w := clampf(float(_pose["mouth_w"]), 0.4, 1.5)
	var open := clampf(float(_pose["open"]), 0.0, 1.0)
	for i in _mouth.size():
		var m := _mouth[i]
		var sx := -1.0 if i == 0 else 1.0
		m.position = Vector3(0.0, FACE_Y - 0.045 + float(_pose["mouth_y"]), FACE_Z)
		m.rotation.z = sx * float(_pose["curve"])
		m.scale = Vector3(w, 1.0 + 2.5 * open, 1.0)
	if _throat:
		# At rest it sits in the collar; a swallow lifts it into sight.
		_throat.position.y = -0.065 + 0.03 * float(_pose["throat"])


func _build() -> void:
	if hooded:
		return
	var ink := _mat(INK)
	var eye := _mat(BLIND_EYE if _base.get("blind", false) else INK)
	for sx in [-1.0, 1.0]:
		_eyes.append(_part(Vector3(0.022, 0.012, 0.004), eye, Vector3.ZERO))
		_brows.append(_part(Vector3(0.036, 0.007, 0.004), ink, Vector3.ZERO))
		# Each half of the mouth reaches from the middle to its corner, so tipping it curves the mouth.
		_mouth.append(_part(Vector3(0.025, 0.006, 0.004), ink, Vector3(sx * 0.0125, 0, 0)))
	var skin := Color("#B89A80")
	var fig := get_parent()
	while fig and not fig is BrotherFigure:
		fig = fig.get_parent()
	if fig:
		skin = (fig as BrotherFigure).face_color
	_throat = _part(Vector3(0.05, 0.03, 0.02), _mat(skin.darkened(0.15)), Vector3.ZERO)
	_throat.position = Vector3(0.0, -0.065, -0.085)


## A small box; its mesh is moved by `offset` inside its node, so the node
## turns about its own origin (a mouth half turns about the middle).
func _part(box_size: Vector3, mat: Material, offset: Vector3) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var b := BoxMesh.new()
	b.size = box_size
	b.material = mat
	mi.mesh = b
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	if offset != Vector3.ZERO:
		var holder := MeshInstance3D.new()
		holder.mesh = null
		add_child(holder)
		mi.position = offset
		holder.add_child(mi)
		return holder
	add_child(mi)
	return mi


func _mat(color: Color) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.roughness = 0.9
	return m


## Whose face: the person whose look this is (a CharacterLook's parent), or
## the character scene's own name.
func _find_who() -> StringName:
	var n := get_parent()
	var last_named: Node = null
	while n:
		if n is CharacterLook:
			var person := n.get_parent()
			return People.id_of(person) if person else &""
		if not n is BrotherFigure:
			last_named = n
		n = n.get_parent()
	return People.id_of(last_named) if last_named else &""
