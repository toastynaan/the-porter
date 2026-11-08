extends NightBeat
## Night 5's round (design doc: "search the grain (body 5). The ergot is in
## the rye. Down the hidden stair, in the crypt, a candle lights itself...
## Hunters lock you inside; escape through the latrine chute. Roger's
## sergeant, left outside the gate, is killed in the lane"). The duty flame
## leads to the granary's grain; using it, his hand meets a hand (body 5:
## Joan if he sheltered her, else a pilgrim), the rye is black-spurred, and
## he finds the key to the crypt passage (it opens the plank closet's door).
## Then the cult bars `locks` behind him and two hunters come (`hunter_at`);
## the way out is down the hidden stair, through the crypt and the choir, up
## the night stairs to the dormitory and down the latrine chute into the
## mill race (`chute`'s far end). If the sergeant was left outside, he's
## killed in the lane as the doors are barred (`sergeant_death`, heard only).
## Out, the hunters go and the doors are unbarred.

const HUNTER := preload("res://game/hunter/hunter.tscn")

@export var grain: Duty
@export var body: FoundBody
@export var joan_flags: Array[StringName] = [&"n2_joan", &"n5_joan"]
@export var key := &"crypt_passage"
## The plank closet's door to the hidden stair: locked tonight, and the key
## is in the grain.
@export var passage: Door
@export var locks: Array[Door] = []
@export var hunter_at: Array[Marker3D] = []
@export var wearers: Array[StringName] = [&"cole", &"dunstan"]
@export var chute: Squeeze
@export var sergeant_flag := &"n5_sergeant"
@export var sergeant_death: DeathScene
@export var joan_lines := PackedStringArray()
@export var pilgrim_lines := PackedStringArray()
@export var ergot_lines := PackedStringArray()
@export var key_lines := PackedStringArray()
@export var locked_lines := PackedStringArray()
@export var sergeant_lines := PackedStringArray()
@export var out_lines := PackedStringArray()

var hunters: Array[Hunter] = []


func _ready() -> void:
	if passage and not GameState.keys.has(key):
		passage.set_open(false, true)
		passage.locked = true
		passage.key = key


func run() -> void:
	var p := player()
	await grain.wait_for_use()
	var joan := joan_flags.any(func(f: StringName) -> bool:
		var v: Variant = GameState.get_flag(f, &"")
		return v == &"admitted" or v == &"prior")
	GameState.set_flag(GameState.tonight("body5"), &"joan" if joan else &"pilgrim")
	await say_lines(joan_lines if joan else pilgrim_lines)
	if joan:
		GameState.set_flag(&"died_joan")
	body.show_body()
	body.find()
	await say_lines(ergot_lines)
	GameState.note(&"ergot_rye")
	if not GameState.keys.has(key):
		GameState.keys.append(key)
	await say_lines(key_lines)
	for d in locks:
		d.set_open(false, true)
		d.locked = true
	var left_out: Variant = GameState.get_flag(sergeant_flag, &"")
	if sergeant_death and left_out == &"refused":
		sergeant_death.play()
		GameState.set_flag(&"died_sergeant")
	for i in hunter_at.size():
		var h := HUNTER.instantiate() as Hunter
		h.wearer = wearers[i] if i < wearers.size() else &""
		h.weapon = &"blade" if GameState.night >= 4 else &"cord"
		h.transform = hunter_at[i].global_transform
		get_parent().get_parent().add_child(h)
		hunters.append(h)
	await get_tree().physics_frame
	for h in hunters:
		h.always_search = true
		h.alert(p.global_position)
	await say_lines(locked_lines)
	if sergeant_death and left_out == &"refused":
		await say_lines(sergeant_lines)
	var out: Vector3 = (chute as Squeeze).points()[-1]
	await until(func() -> bool: return p.global_position.distance_to(out) < 2.5 and not p.busy())
	for h in hunters:
		if is_instance_valid(h):
			h.queue_free()
	hunters.clear()
	for d in locks:
		d.locked = false
	GameState.set_flag(GameState.tonight("escaped"))
	await say_lines(out_lines)
