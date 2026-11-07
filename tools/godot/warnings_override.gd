extends SceneTree
## Prints an override.cfg that turns every GDScript warning that is on by
## default (level 1, "warn") into an error, so headless runs print them.
## tools/check.sh writes it to the project root for the length of a check.


func _init() -> void:
	var out := "[debug]\n"
	for p in ProjectSettings.get_property_list():
		var n: String = p.name
		if n.begins_with("debug/gdscript/warnings/") and p.type == TYPE_INT and int(ProjectSettings.get_setting(n)) == 1:
			out += n.trim_prefix("debug/") + "=2\n"
	print("--- override.cfg")
	print(out)
	quit()
