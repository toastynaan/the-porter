class_name AudioOut
## Whether sound really plays. Headless runs (tests, tools) use a dummy audio
## driver that never advances, so a sound started there is still playing at
## quit and leaks; sound players skip play() when this is false.


static func enabled() -> bool:
	return DisplayServer.get_name() != "headless"
