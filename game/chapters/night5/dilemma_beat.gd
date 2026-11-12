extends NightBeat
## Night 5's dusk, the choice (design doc: "you wake to a cry from the chapter
## house. Thomas is on the floor, 'attacked', and Brother Simon is pinned by a
## masked man. You can reach only one."). The duty flame is over both; he
## reaches one by using him (`reach_thomas`, `reach_simon`):
## - Thomas: behind him Simon's throat is cut (`death`, the masked man is its
##   killer and turns to the porter, then goes); n5_saved=thomas.
## - Simon: the masked man (`masked`) lets him go and is gone once unseen;
##   Thomas gets up "wounded" anyway; Simon tells him Thomas sent him to
##   scrub the blood (the note thomas_sent_simon); n5_saved=simon.
## Saving Simon is the night's rule (docs/systems/mechanics.md, "Saving people").

@export var thomas: Brother
@export var thomas_down: Marker3D
@export var thomas_up: Marker3D
@export var simon: Brother
@export var masked: Node3D
@export var death: DeathScene
@export var reach_thomas: Duty
@export var reach_simon: Duty
@export var lines := PackedStringArray()
@export var thomas_lines := PackedStringArray()
@export var thomas_after := PackedStringArray()
@export var simon_lines := PackedStringArray()
@export var simon_tells := PackedStringArray()


func run() -> void:
	var p := player()
	thomas.place(thomas_down.global_transform)
	simon.place(death.global_transform)
	masked.visible = true
	await until(func() -> bool: return p.global_position.distance_to(death.global_position) < 9.0 or reach_thomas.enabled)
	await say_lines(lines)
	var picked := [&""]
	reach_thomas.used.connect(func(_by: Node) -> void: if picked[0] == &"": picked[0] = &"thomas", CONNECT_ONE_SHOT)
	reach_simon.used.connect(func(_by: Node) -> void: if picked[0] == &"": picked[0] = &"simon", CONNECT_ONE_SHOT)
	reach_thomas.enabled = true
	reach_simon.enabled = true
	await until(func() -> bool: return picked[0] != &"")
	reach_thomas.enabled = false
	reach_simon.enabled = false
	GameState.set_flag(GameState.tonight("saved"), picked[0])
	if picked[0] == &"thomas":
		masked.visible = false
		death.victim = simon
		await death.play()
		death.turn_to(p.global_position)
		await say_lines(thomas_lines)
		thomas.place(thomas_up.global_transform)
		thomas.face(p.global_position)
		await say_lines(thomas_after)
	else:
		await say_lines(simon_lines)
		await until(func() -> bool: return not ViewCheck.on_screen(p.camera, [masked.global_position + Vector3.UP * 1.5]))
		masked.visible = false
		thomas.place(thomas_up.global_transform)
		thomas.face(p.global_position)
		simon.face(p.global_position)
		GameState.change_trust(&"simon", 20)
		await say_lines(simon_tells)
		GameState.note(&"thomas_sent_simon")
