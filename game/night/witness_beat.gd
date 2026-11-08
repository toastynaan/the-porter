extends NightBeat
## A death on the round, seen or heard a few steps ahead (night 4: in the fog
## a choir brother's cry, and the porter reaches him as his lantern is still
## rolling on the flags). The duty flame leads to `spot`; within `radius` of
## it the death plays (DeathScene). Then, out of the fog, `arriver` comes
## and kneels by the body (the prior, with blood on his sleeve after: the
## `note`). `also_dead` are set too (the victim's own died_ flag).

@export var spot: Marker3D
@export var radius := 9.0
@export var death: DeathScene
@export var also_dead: Array[StringName] = []
@export var death_lines := PackedStringArray()
@export var arriver: Brother
@export var arriver_at: Marker3D
@export var arriver_lines := PackedStringArray()
@export var note := &""


func run() -> void:
	var p := player()
	var way := Wayfinding.show_way(self, spot.global_position)
	await until(func() -> bool: return p.global_position.distance_to(spot.global_position) < radius)
	Wayfinding.put_out(way)
	await death.play()
	for f in also_dead:
		GameState.set_flag(f)
	await until(func() -> bool: return p.global_position.distance_to(death.global_position) < 3.5)
	await say_lines(death_lines)
	if arriver and arriver_at:
		await wait(1.5)
		arriver.place(arriver_at.global_transform)
		arriver.face(death.global_position)
		await say_lines(arriver_lines)
		if note != &"":
			GameState.note(note)
