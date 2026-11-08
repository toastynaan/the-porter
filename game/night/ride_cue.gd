class_name RideCue
extends Marker3D
## Something on the road in (night 0) that happens as the carter's wagon
## passes this spot (RideBeat): a line or two, a sound, a change of pace, a
## stop. Place it beside the road; it counts from the nearest point of the
## road to it. Its lines wait while the porter is talking to someone, and are
## dropped once the wagon is `keep` metres past. With `hold` the wagon stops
## here, waits until he's done talking, says the lines and stands for `hold`
## seconds (the warden at Aldgate looking them over).

## "Name: words" is Name speaking; a line in brackets is what he notices.
@export var lines: PackedStringArray
## Played here as the wagon passes.
@export var sound: AudioStream
@export var volume_db := 0.0
## The wagon's pace from here on, m/s (0: unchanged).
@export var pace := 0.0
## Seconds the wagon stands here (0: it doesn't stop).
@export var hold := 0.0
## Metres past this spot after which the lines are no longer worth saying.
@export var keep := 30.0
## People here who turn to watch the wagon while it's within 15 m.
@export var watchers: Array[Node3D] = []

## Metres along the road (RideBeat sets it).
var along := 0.0
