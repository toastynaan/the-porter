class_name AudioOut
## Whether sound really plays. Headless runs (tests, tools) use a dummy audio
## driver that never advances, so a sound started there is still playing at
## quit and leaks; sound players skip play() when this is false.


static func enabled() -> bool:
	return DisplayServer.get_name() != "headless"


## A copy of `wav` that loops end to end (the placeholder WAVs import unlooped).
static func looped(wav: AudioStreamWAV) -> AudioStreamWAV:
	var loop := wav.duplicate() as AudioStreamWAV
	loop.loop_mode = AudioStreamWAV.LOOP_FORWARD
	loop.loop_begin = 0
	loop.loop_end = int(loop.get_length() * loop.mix_rate)
	return loop
