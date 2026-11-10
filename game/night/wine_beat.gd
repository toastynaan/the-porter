extends NightBeat
## Night 6's dusk (design doc: "No duties at all. The wine"): Thomas brings
## the porter a cup of spiced wine "for the cold" and watches him. Drunk: Dose
## +40, and caught tonight he wakes in a habit (the New Faith). Refused to his
## face: Suspicion +20 (Wine). The duty flame is over Thomas until the porter
## comes to him.

@export var thomas: Brother
@export var at: Marker3D
@export var near := 3.0
@export var offer_lines := PackedStringArray()
@export var drunk_lines := PackedStringArray()
@export var refused_lines := PackedStringArray()


func run() -> void:
	var p := player()
	thomas.place(at.global_transform)
	thomas.add_to_group(&"glyph_targets")
	await until(func() -> bool: return p.global_position.distance_to(thomas.global_position) < near)
	thomas.remove_from_group(&"glyph_targets")
	thomas.face(p.global_position)
	await say_lines(offer_lines)
	var pick := await Talk.choose(PackedStringArray(["(Drink Brother Thomas's wine.)", "(Refuse it.)"]))
	if pick == 0:
		Wine.drink()
		await say_lines(drunk_lines)
	else:
		Wine.refuse()
		await say_lines(refused_lines)
	thomas.place(null)
