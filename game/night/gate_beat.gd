extends NightBeat
## Taking the gate (design doc, "Core loop" 2: after supper you go to the
## gate and relieve Cole. You close and bar it and keep watch for the night;
## guests go into the ledger by name and description, here as they come, at
## the knocks). Cole goes off into the abbey. The bar stays down unless the
## porter lifts it to let someone in.

@export var gate: AbbeyGate
@export var cole: VisitorNPC
## Where Cole goes once relieved (out of sight).
@export var cole_off: Marker3D
@export var relieve: Duty
@export var shut_gate: Duty
@export var bar_duty: Duty
@export var ledger: Duty


func _ready() -> void:
	gate.show_bar(GameState.has_flag(&"gate_barred"))
	if GameState.has_flag(&"gate_taken"):
		cole.set_present.call_deferred(false)


func run() -> void:
	await relieve.wait_for_use()
	GameState.set_flag(&"gate_taken")
	await say("Cole", "(Says nothing. He leaves you the gate.)")
	_cole_goes.call()
	await say("", "(Shut the gate and bar it.)")
	await shut_gate.wait_for_use()
	await gate.swing(false)
	await bar_duty.wait_for_use()
	gate.show_bar(true)
	GameState.set_flag(&"gate_barred")
	await say("", "(You lift the bar into its brackets. It takes both hands.)")
	await say("", "(Open the ledger at tonight's page, on the desk in your cell.)")
	await ledger.wait_for_use()
	GameState.set_flag(&"n3_ledger")
	await say("", "(Tonight's page. Guests are written in as they come.)")


## Cole walks off, and is gone once no one is looking.
func _cole_goes() -> void:
	await cole.walk_to(cole_off.global_position)
	var p := player()
	while ViewCheck.on_screen(p.camera, [cole.global_position + Vector3.UP * 1.0]):
		await get_tree().physics_frame
	cole.set_present(false)
