extends NightBeat
## Closing the gate (design doc, "Core loop": bar the gate at sunset; enter
## that night's guests in the ledger, here as they come, at the knocks). The
## bar stays down unless the porter lifts it to let someone in.

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
	await say("", "(Open the ledger at tonight's page, on the desk in your cell.)")
	await ledger.wait_for_use()
	GameState.set_flag(&"n3_ledger")
	await say("", "(Tonight's page. Guests are written in as they come.)")


func _show_bar(down: bool) -> void:
	if gate_bar:
		gate_bar.visible = down
		# On the door layer: it blocks the porter but stays out of the navmesh,
		# so the gateway is walkable when the gate is open.
		gate_bar.collision_layer = Layers.DOOR if down else 0
