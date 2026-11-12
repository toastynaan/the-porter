extends NightBeat
## Night 6's last beat: nothing more is asked of him. It holds the night
## open until an ending is decided (Night6Ending: he gets out, or holds out
## to Lauds), which ends the night.


func run() -> void:
	await until(func() -> bool: return GameState.has_flag(&"ending"))
