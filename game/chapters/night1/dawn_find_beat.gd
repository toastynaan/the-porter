extends NightBeat
## Lauds after someone died out of sight (design doc, night 1: "the merchant
## is in the fishpond (body 1)... Thomas says he drowned drunk"). If `died`
## is set: a shout, and the duty flame leads him to the body, where `witness`
## kneels; the body is found when he looks at it (FoundBody: the scare and
## the clue), then the witness gives the house's account. Otherwise, if the
## guest lived, a line or two as he leaves at first light: cursing the porter
## for locking him in (`locked_flag`), or just going.

@export var died := &"died_merchant"
@export var body: FoundBody
@export var witness: Brother
@export var witness_at: Marker3D
## The Visitor flag (he was let in) and the flag that he was locked in.
@export var guest_flag := &"n1_merchant"
@export var locked_flag := &"n1_guesthouse_locked"
@export var shout_lines := PackedStringArray(["(Shouting, from the fishpond.)"])
@export var found_lines := PackedStringArray()
@export var locked_lines := PackedStringArray()
@export var lived_lines := PackedStringArray()


func run() -> void:
	if GameState.has_flag(died):
		await _discovery()
		return
	var let_in: Variant = GameState.get_flag(guest_flag, &"")
	if let_in != &"admitted" and let_in != &"prior":
		return
	await say_lines(locked_lines if GameState.has_flag(locked_flag) else lived_lines)


func _discovery() -> void:
	var p := player()
	body.show_body()
	if witness and witness_at:
		witness.place(witness_at.global_transform)
		witness.face(body.global_position)
	await say_lines(shout_lines)
	var target: Node3D = body
	if witness:
		target = witness
	target.add_to_group(&"glyph_targets")
	var way := Wayfinding.show_way(self, body.global_position)
	await until(func() -> bool: return body.is_found)
	Wayfinding.put_out(way)
	target.remove_from_group(&"glyph_targets")
	if witness:
		witness.face(p.global_position)
	await say_lines(found_lines)
