class_name RideCue
extends Marker3D
## Something on the road in (night 0) that happens as the carter's wagon
## passes this spot (RideBeat): a line or two, a sound, a change of pace, a
## stop. Place it beside the road; it counts from the nearest point of the
## road to it. Its lines wait while the porter is talking to someone, and are
## dropped once the wagon is `keep` metres past. With `hold` the wagon stops
## here, waits until he's done talking, says the lines and stands for `hold`
## seconds. With `talk`, someone turns to him and starts a conversation after
## the lines (the traveller as the wagon sets off); with `cut_in`, its lines
## cut short any talk he's in and are said at once (a stop with `cut_in`
## doesn't wait for the talk to end either). With an `inspector`, someone
## walks up to the stopped wagon with the last of the lines, holds a lantern
## to his face for `close_lines`, and walks back to his place with
## `parting_lines` (the warden at Aldgate).

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
## A conversation `talker` starts with him here, after the lines; it waits,
## like the lines, while he's talking to someone.
@export var talk: Conversation
@export var talker: Node3D
## The lines cut short any talk he's in, and drop any still waiting.
@export var cut_in := false
## At a stop: who walks up to him with a lantern (its character scene's
## "Lantern"), what is said while it's held to his face, and as he goes back.
@export var inspector: Node3D
@export var close_lines: PackedStringArray
@export var parting_lines: PackedStringArray

## Metres along the road (RideBeat sets it).
var along := 0.0
