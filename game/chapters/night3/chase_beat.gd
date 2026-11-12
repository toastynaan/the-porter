extends NightBeat
## The first chase (design doc, night 3: "You hide in the bakehouse oven and
## find bones (body 3). Climbing out, you are nearly caught; Thomas pulls you
## into the infirmary and hides you."). Its rule is hiding: the hunter
## searches whatever the Suspicion, and the oven doesn't give you up while
## you hold your breath. "The night 3 chase is running from it and finding
## it ahead of you": the demon stands in doorways that lead away from the
## bakehouse (`blockers`: Marker3D triggers, each with a "Stand" child).
##
## Caught, the usual rules apply: the first capture wakes you in the
## infirmary with Thomas over you, the second sends you back to Matins.

const BONES := preload("res://art/sfx/sfx_bones.wav")
## Seconds in the oven before the hand closes on the jaw.
const BONES_AFTER := 1.5

@export var hunter: Hunter
@export var stalker: Stalker
@export var oven: HidingSpot
@export var blockers: Node3D
@export var blocker_radius := 3.0
@export var thomas: Brother
@export var rescue_porter: Marker3D
@export var rescue_thomas: Marker3D
@export var bones_lines := PackedStringArray(["(Your hand closes on something in the ash. A jaw.)"])
@export var rescue_lines := PackedStringArray(["Thomas {grave}: (Pulls you into the infirmary and hides you.)"])
@export var caught_lines := PackedStringArray(["Thomas {warm}: (Over you as you wake.)"])

var _woke := false
var _audio: AudioStreamPlayer3D


func _ready() -> void:
	_audio = AudioStreamPlayer3D.new()
	_audio.stream = BONES
	add_child(_audio)


func run() -> void:
	var p := player()
	hunter.always_search = true
	var chance := oven.check_chance
	oven.check_chance = 0.0
	var flow := get_tree().get_first_node_in_group(&"capture_flow") as CaptureFlow
	if flow:
		flow.woke.connect(func() -> void: _woke = true, CONNECT_ONE_SHOT)
	var used: Array[Node] = []
	var in_oven := 0.0
	var bones := false
	var searched := false
	while true:
		await get_tree().physics_frame
		var dt := PlayTime.physics(self)
		for b in blockers.get_children():
			if b is Marker3D and not used.has(b) and p.global_position.distance_to((b as Marker3D).global_position) < blocker_radius:
				if stalker.appear_ahead((b.get_node(^"Stand") as Node3D).global_position):
					used.append(b)
		in_oven = in_oven + dt if p.hiding == oven else 0.0
		if not bones and in_oven >= BONES_AFTER:
			bones = true
			_bones.call()
		if hunter.state == Hunter.State.SEARCH:
			searched = true
		if hunter.state == Hunter.State.CAPTURE:
			await until(func() -> bool: return _woke)
			GameState.set_flag(GameState.tonight("caught"))
			thomas.place(rescue_thomas.global_transform)
			thomas.face(p.global_position)
			await say_lines(caught_lines)
			break
		# He has searched and you come out (or never hid): nearly caught.
		if searched and p.hiding == null and not p.busy():
			await _nearly_caught(p)
			break
	oven.check_chance = chance
	hunter.reset()


func _bones() -> void:
	GameState.set_flag(GameState.tonight("body3"))
	if AudioOut.enabled():
		_audio.global_position = oven.view.global_position
		_audio.play()
	await say_lines(bones_lines)


## He comes back as you climb out; Thomas pulls you away.
func _nearly_caught(p: Player) -> void:
	hunter.alert(p.global_position)
	var t := 0.0
	while t < 3.0 and hunter.global_position.distance_to(p.global_position) > 6.0 and hunter.state != Hunter.State.CHASE:
		await get_tree().physics_frame
		t += PlayTime.physics(self)
	# He is on you; Thomas's hand is quicker.
	hunter.stand_still()
	p.controls_locked = true
	await fade_to(1.0, 0.4)
	hunter.reset()
	p.place(rescue_porter.global_position, rescue_porter.global_rotation.y)
	thomas.place(rescue_thomas.global_transform)
	thomas.face(p.global_position)
	GameState.set_flag(GameState.tonight("thomas_hid_you"))
	await fade_to(0.0, 1.0)
	p.controls_locked = false
	await say_lines(rescue_lines)
