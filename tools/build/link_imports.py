#!/usr/bin/env python3
"""Sets how Godot imports what the build made, after Godot has imported it
once (tools/build.sh runs it between two imports).

- art/models/*.glb: every material in the model that has a file of the same
  name in game/world/materials/real/ is linked to it, so the model uses the
  game's own material (its textures, its shader) wherever it is placed.
- art/tex/tex_*.jpg: mipmaps, and video-memory compression; *_nrm as a
  normal map; *_col as colour.

It only rewrites a .import file whose settings change, and then removes
Godot's imported copy so the next import makes it again.
"""
import glob
import json
import os
import re
import struct

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REAL = os.path.join(ROOT, "game", "world", "materials", "real")


def glb_materials(path):
    with open(path, "rb") as f:
        f.read(12)
        length, _kind = struct.unpack("<II", f.read(8))
        doc = json.loads(f.read(length))
    return [m.get("name", "") for m in doc.get("materials", [])]


def set_param(text, key, value):
    pattern = re.compile(r"(?m)^%s=.*$" % re.escape(key))
    line = "%s=%s" % (key, value)
    return pattern.sub(line, text) if pattern.search(text) else text.rstrip("\n") + "\n" + line + "\n"


def replace_value(text, key, value):
    """Replaces `key`'s value, a {...} that may run over several lines."""
    start = text.index("\n" + key + "=") + 1
    at = text.index("{", start)
    depth = 0
    for i in range(at, len(text)):
        depth += {"{": 1, "}": -1}.get(text[i], 0)
        if depth == 0:
            return text[:start] + key + "=" + value + text[i + 1:]
    raise ValueError("unbalanced braces after " + key)


def forget(import_text):
    """Removes the imported copies an .import file names."""
    for rel in re.findall(r'"(res://\.godot/imported/[^"]+)"', import_text):
        path = os.path.join(ROOT, rel[len("res://"):])
        if os.path.exists(path):
            os.remove(path)


def link_model(path):
    imp = path + ".import"
    if not os.path.exists(imp):
        return False
    text = open(imp).read()
    linked = {}
    for name in glb_materials(path):
        tres = os.path.join(REAL, name + ".tres")
        if os.path.exists(tres):
            linked[name] = "res://" + os.path.relpath(tres, ROOT)
    body = "{}"
    if linked:
        rows = ['"%s": {\n"use_external/enabled": true,\n"use_external/fallback_path": "%s",\n'
                '"use_external/path": "%s"\n}' % (n, p, p) for n, p in sorted(linked.items())]
        body = '{\n"materials": {\n%s\n}\n}' % ",\n".join(rows)
    new = replace_value(text, "_subresources", body)
    if new == text:
        return False
    forget(text)
    open(imp, "w").write(new)
    return True


def link_texture(path):
    imp = path + ".import"
    if not os.path.exists(imp):
        return False
    text = open(imp).read()
    new = set_param(text, "mipmaps/generate", "true")
    new = set_param(new, "compress/mode", "2")
    new = set_param(new, "detect_3d/compress_to", "0")
    if path.endswith("_nrm.jpg"):
        new = set_param(new, "compress/normal_map", "1")
    if new == text:
        return False
    forget(text)
    open(imp, "w").write(new)
    return True


def main():
    changed = [p for p in sorted(glob.glob(os.path.join(ROOT, "art", "models", "*.glb"))) if link_model(p)]
    changed += [p for p in sorted(glob.glob(os.path.join(ROOT, "art", "tex", "tex_*.jpg"))) if link_texture(p)]
    for p in changed:
        print("linked", os.path.relpath(p, ROOT))


if __name__ == "__main__":
    main()
