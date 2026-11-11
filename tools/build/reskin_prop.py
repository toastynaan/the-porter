#!/usr/bin/env python3
"""reskin_prop.py NAME "DESCRIPTION" [MODEL[:WEIGHT] ...]
Turns game/world/props/prop_NAME.tscn from a greybox placeholder into the real prop:
its Blocks stay (collision, footsteps) but are no longer drawn (`shown = false`), and the
model art/models/prop_NAME.glb is added as `Model`. With several MODELs (names without
"prop_"), `Model` is a PropVariant showing one of them by where the prop stands.
DESCRIPTION replaces the scene's editor_description. Run from the repo root. Safe to run twice."""
import re, sys
name, desc, models = sys.argv[1], sys.argv[2], sys.argv[3:] or [sys.argv[1]]
path = "game/world/props/prop_%s.tscn" % name
t = open(path).read()
assert t.strip(), path + " is empty"
if 'name="Model"' in t:
    sys.exit(path + ": already has a Model")
# Blocks: not drawn.
def hide(m):
    body = m.group(0)
    if 'ExtResource("block")' in body and "shown = false" not in body:
        body = body.rstrip("\n") + "\nshown = false\n\n"
    return body
t = re.sub(r'\[node name="[^"]+" type="StaticBody3D"[^\]]*\]\n(?:(?!\n\[).)*\n?', hide, t, flags=re.S)
# MeshInstance3D placeholders (the props built from primitive meshes): hidden.
def hide_mesh(m):
    body = m.group(0)
    if "visible = false" not in body:
        body = body.rstrip("\n") + "\nvisible = false\n\n"
    return body
if "--keep-meshes" not in models:
    t = re.sub(r'\[node name="[^"]+" type="MeshInstance3D"[^\]]*\]\n(?:(?!\n\[).)*\n?', hide_mesh, t, flags=re.S)
models = [m for m in models if not m.startswith("--")]
ext = ""
for m in models:
    mm = m.split(":")[0]
    ext += '[ext_resource type="PackedScene" path="res://art/models/prop_%s.glb" id="model_%s"]\n' % (mm, mm)
if len(models) > 1:
    ext += '[ext_resource type="Script" path="res://game/world/props/prop_variant.gd" id="variant_gd"]\n'
# After the last ext_resource (they must all come before any sub_resource), or after the header if there is none.
i = t.rfind("[ext_resource")
j = t.index("\n", i if i >= 0 else 0) + 1
t = t[:j] + ("" if i >= 0 else "\n") + ext + t[j:]
t = re.sub(r"\n{3,}", "\n\n", t)
t = re.sub(r'editor_description = "[^"]*"', 'editor_description = "%s"' % desc.replace('"', "'"), t, count=1)
t = t.replace(' groups=["placeholder"]', "", 1)
t = t.rstrip("\n") + "\n\n"
if len(models) == 1:
    t += '[node name="Model" parent="." instance=ExtResource("model_%s")]\n' % models[0].split(":")[0]
else:
    weights = [m.split(":")[1] if ":" in m else "1" for m in models]
    t += '[node name="Model" type="Node3D" parent="."]\nscript = ExtResource("variant_gd")\n'
    if any(w != "1" for w in weights):
        t += "weights = PackedFloat32Array(%s)\n" % ", ".join(weights)
    for i, m in enumerate(models):
        mm = m.split(":")[0]
        t += '\n[node name="%s" parent="Model" instance=ExtResource("model_%s")]\n' % ("".join(w.title() for w in mm.split("_")), mm)
assert "[node " in t and len(t) > 100
open(path, "w").write(t)
print("reskinned", path)
