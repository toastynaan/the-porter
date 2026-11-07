class_name Visitor
extends Resource
## Someone who knocks at the gate on a night (design doc, "Knocks"; "Gate
## visitors": scripted visitor resources queued per night, no generated
## pilgrims in the first build). Who they are, what the porter can notice
## through the grille, and what they say. Lines are placeholders in the
## design doc's words until the script is written.

@export var id := &""
## The speaker name on subtitles.
@export var speaker := ""
## The name he writes in the ledger; what he noticed follows it.
@export var ledger_name := ""
@export var build := BrotherFigure.Build.AVERAGE
## A coloured cloak (alpha 0: none, a habit or a tunic).
@export var cloak_color := Color(0, 0, 0, 0)
## A brown work tunic rather than a black habit (lay folk).
@export var tunic := false
## Said at the grille when the porter comes to it.
@export var greeting := ""
@export var details: Array[VisitorDetail] = []
## The flag that records the porter's choice: admitted, refused or prior.
@export var flag := &""


func has_part(part: StringName) -> bool:
	return details.any(func(d: VisitorDetail) -> bool: return d.part == part)
