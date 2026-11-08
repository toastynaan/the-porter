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
## How he looks: his character scene (game/characters/chr_<name>.tscn).
@export var look: PackedScene
## Carries his own lantern (at night; not in daylight).
@export var lantern := true
## Said at the grille when the porter comes to it.
@export var greeting := ""
@export var details: Array[VisitorDetail] = []
## The flag that records the porter's choice: admitted, refused or prior.
@export var flag := &""
## One question he can ask first (docs/mechanics.md, "Talking at the
## grille"), and what they answer.
@export var question := ""
@export var answer: PackedStringArray = []
## He only comes if this flag is set (e.g. Roger, if the merchant died).
@export var only_if := &""


func has_part(part: StringName) -> bool:
	return details.any(func(d: VisitorDetail) -> bool: return d.part == part)
