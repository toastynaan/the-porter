extends Node
## Autoload Press: whether a press is a new one. A key held down repeats, and
## in the playtest (the editor's embedded game window) the repeats counted as
## fresh presses: holding E skipped every line of a talk, answered for him,
## and opened the talk again as it closed.
## Handlers that act on a press ask fresh() (or fresh_key() for a plain key):
## a press counts once, and it must be let go before it counts again.

## Per action (or keycode): let go of since its last press.
var _up := {}
## Per action (or keycode): the last event asked about, and the answer, so a
## press that two handlers see gets the same answer from both.
var _asked := {}
var _answer := {}


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS


func _process(_delta: float) -> void:
	for what: Variant in _up:
		if not _up[what] and not _held(what):
			_up[what] = true


## True if `event` presses `action`, let go of since it last did.
func fresh(event: InputEvent, action: StringName) -> bool:
	if _asked.get(action) == event:
		return _answer[action]
	if not event.is_action_pressed(action):
		return false
	return _count(action, event)


## True if `event` presses its key, let go of since it last did.
func fresh_key(event: InputEventKey) -> bool:
	if _asked.get(event.keycode) == event:
		return _answer[event.keycode]
	if not event.pressed or event.echo:
		return false
	return _count(event.keycode, event)


func _count(what: Variant, event: InputEvent) -> bool:
	var counts: bool = _up.get(what, true)
	_up[what] = false
	_asked[what] = event
	_answer[what] = counts
	return counts


func _held(what: Variant) -> bool:
	if what is StringName:
		return Input.is_action_pressed(what)
	return Input.is_key_pressed(what)
