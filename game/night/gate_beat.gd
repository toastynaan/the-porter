extends NightBeat
## Closing the gate (design doc, "Core loop": bar the gate at sunset; enter
## that night's guests in the ledger). The bar stays down from here on.

@export var bar_duty: Duty
## The bar prop; out of its brackets until the porter bars the gate.
@export var gate_bar: StaticBody3D
@export var ledger: Duty


func _ready() -> void:
	_show_bar(GameState.has_flag(&"gate_barred"))


func run() -> void:
	await bar_duty.wait_for_use()
	_show_bar(true)
	GameState.set_flag(&"gate_barred")
	await say("", "(You lift the bar into its brackets. It takes both hands.)")
	await say("", "(Tonight's guests go in the ledger, on the desk in your cell.)")
	await ledger.wait_for_use()
	GameState.set_flag(&"n3_ledger")
	await say("", "(You enter tonight's guests in the ledger.)")


func _show_bar(down: bool) -> void:
	if gate_bar:
		gate_bar.visible = down
		gate_bar.collision_layer = Layers.WORLD if down else 0
