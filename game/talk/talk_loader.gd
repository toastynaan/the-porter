class_name TalkLoader
extends ResourceFormatLoader
## Loads a conversation written as a plain text file (`.talk`, docs/systems/dialogue.md)
## as a Conversation. Godot registers it by itself, as it does any named loader.
##
## A .talk file is the conversation's script as it is, with its id on the
## first line:
##
##   @id n3_thomas
##   # DRAFT
##   == start
##   Thomas {warm}: Sit, brother.
##
## No escaping: a quote is a quote. Edit it in any text editor (in Godot,
## add "talk" to Editor Settings, FileSystem, TextFile Extensions).

const EXTENSION := "talk"
const CONVERSATION := "res://game/talk/conversation.gd"


func _get_recognized_extensions() -> PackedStringArray:
	return PackedStringArray([EXTENSION])


func _handles_type(type: StringName) -> bool:
	return type == &"Resource"


func _get_resource_type(path: String) -> String:
	return "Resource" if path.get_extension() == EXTENSION else ""


func _load(path: String, _original_path: String, _use_sub_threads: bool, _cache_mode: int) -> Variant:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return FileAccess.get_open_error()
	return parse(f.get_as_text(), path)


## A Conversation from a .talk file's text: "@id x" on the first line is
## its id (else the file's name), the rest is its script.
##
## Godot compiles loaders at startup, before the autoloads that Conversation
## uses exist, so Conversation is fetched here, when a file is loaded, and
## not named in this script.
static func parse(source: String, path := "") -> Resource:
	var c: Resource = (load(CONVERSATION) as Script).new()
	var lines := source.split("\n")
	var id := StringName(path.get_file().get_basename()) if not path.is_empty() else &""
	if not lines.is_empty() and lines[0].begins_with("@id "):
		id = StringName(lines[0].trim_prefix("@id ").strip_edges())
		lines.remove_at(0)
	c.set(&"id", id)
	c.set(&"text", "\n".join(lines))
	return c
