extends NightBeat
## Night 6's rite (design doc: "At Matins the cult gives it the last soul in
## the crypt (Brother Simon if he lived, otherwise a pilgrim) unless you stop
## them"; docs/mechanics.md, "Stopping the rite"). From `begins` the last
## soul lies bound in the crypt with Thomas over him and the book on the
## altar. Before the Matins mark (`due`) the porter can stop it: free the
## victim (stand at his cords holding E for FREE_TIME), or take the book
## from the altar (it goes in his satchel). Otherwise at Matins the rite is
## finished: the last soul is given, and with the count at 9 or more the
## Saint rises (the Rising). The Saint wakes at `begins` (HungrySaint).

const FREE_TIME := 3.0
const FREE_REACH := 1.4

@export var begins := 23.0
@export var victim: Node3D
@export var thomas: Brother
@export var thomas_at: Marker3D
@export var book: Pickup
@export var saint: HungrySaint
@export var rite_lines := PackedStringArray()
@export var freed_lines := PackedStringArray()
@export var book_lines := PackedStringArray()
@export var done_lines := PackedStringArray()
@export var silence_lines := PackedStringArray()

var _hold := 0.0


func run() -> void:
	await clock().wait_until(begins)
	clock().wake()
	victim.visible = true
	# The last soul: Simon if he lived, otherwise a pilgrim.
	for c in victim.get_children():
		if c is Node3D:
			(c as Node3D).visible = String(c.name).to_lower() == String(Rite.last_victim())
	if thomas and thomas_at:
		thomas.place(thomas_at.global_transform)
	if saint:
		saint.wake()
		await say_lines(silence_lines)
	var p := player()
	var said := false
	while GameState.hour < due:
		if not said and p.global_position.distance_to(victim.global_position) < 8.0:
			said = true
			await say_lines(rite_lines)
		if GameState.satchel.has(&"book") or (book and not is_instance_valid(book)):
			GameState.set_flag(&"rite_stopped", &"book")
			await say_lines(book_lines)
			return
		var holding := p.global_position.distance_to(victim.global_position) < FREE_REACH \
			and Input.is_action_pressed(&"interact")
		_hold = _hold + PlayTime.physics(self) if holding else 0.0
		if _hold >= FREE_TIME:
			GameState.set_flag(&"rite_stopped", &"freed")
			victim.visible = false
			await say_lines(freed_lines)
			return
		await get_tree().physics_frame
	GameState.set_flag(&"rite_done")
	GameState.feed_rite(Rite.last_victim())
	await say_lines(done_lines)
