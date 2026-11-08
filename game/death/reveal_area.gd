extends Area3D
## What the porter uses to find a hidden body (HiddenBody): hold `interact`
## on it. Each press works on it while held.

var hidden_body: HiddenBody

var _busy := false


func interact(_by: Node) -> void:
	if _busy or hidden_body == null:
		return
	_busy = true
	while not hidden_body.work(PlayTime.physics(self)):
		await get_tree().physics_frame
		if not (Input.is_action_pressed(&"interact") or hidden_body.get_meta(&"auto", false)):
			break
	_busy = false
