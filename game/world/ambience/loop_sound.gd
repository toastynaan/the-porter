extends AudioStreamPlayer3D
## A sound that goes on where it stands: the Keys' hearth, the watch fire at
## Aldgate. Its stream loops; it plays from the start, unless sound is off
## (headless tests), so it isn't autoplay.


func _ready() -> void:
	if stream is AudioStreamWAV:
		stream = AudioOut.looped(stream as AudioStreamWAV)
	if AudioOut.enabled():
		play()
