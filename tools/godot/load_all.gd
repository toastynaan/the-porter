extends Node
## Loads every script, scene and resource under res://game and res://tools,
## so parse errors (and, under tools/check.sh, warnings) print even for files
## no test opens. Runs as a scene (load_all.tscn) so the autoloads exist.

const ROOTS: Array[String] = ["res://game", "res://tools"]
const EXTENSIONS: Array[String] = ["gd", "tscn", "tres", "gdshader", "talk"]


func _ready() -> void:
	var failed := 0
	var count := 0
	for top in ROOTS:
		for path in _files(top):
			if path.get_basename() == "res://tools/godot/load_all":
				continue
			count += 1
			if ResourceLoader.load(path, "", ResourceLoader.CACHE_MODE_IGNORE) == null:
				print("  FAIL could not load %s" % path)
				failed += 1
	print("loaded %d files" % count)
	print("RESULT: %s" % ("PASS" if failed == 0 else "FAIL (%d)" % failed))
	get_tree().quit(0 if failed == 0 else 1)


func _files(dir_path: String) -> Array[String]:
	var out: Array[String] = []
	for f in DirAccess.get_files_at(dir_path):
		if f.get_extension() in EXTENSIONS:
			out.append(dir_path.path_join(f))
	for d in DirAccess.get_directories_at(dir_path):
		out.append_array(_files(dir_path.path_join(d)))
	return out
