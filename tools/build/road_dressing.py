"""Stands the trees along the road in (night 0) on the ground the fields'
script makes: it rewrites the Trees node of game/world/road/env_road.tscn
from the list below, each tree set down at the ground's own height there
(tools/build/env_road_fields.py). Run it again after changing the list or
the lie of the land; trees moved by hand in the editor are put back where
the list says, so change the list.

Run: tools/build.sh road_dressing   (it builds no model)
"""
import math
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import porter
from env_road_fields import ground

SCENE = os.path.join(porter.ROOT, "game", "world", "road", "env_road.tscn")
# kind, x, z, and optionally its size (1 is as built) and the way it faces, in degrees.
TREES = [
    # Behind the wagon as it sets off: the road running back into the last light.
    ("thorn", -214.5, 54.6, 1.1), ("pollard", -217.0, 40.4), ("elm", -223.0, 38.6, 1.05), ("oak", -231.0, 56.4, 1.15),
    ("elm", -239.5, 38.9, 0.85), ("pollard", -246.0, 40.6, 0.9), ("elm", -252.0, 55.2, 0.95), ("pollard", -259.0, 53.5),
    ("elm", -266.0, 38.4, 1.15), ("thorn", -272.0, 54.9), ("pollard", -276.0, 40.5, 1.1), ("elm", -292.0, 55.6, 1.0),
    ("elm", -297.0, 38.2, 0.9), ("oak", -318.0, 37.0, 1.0), ("elm", -331.0, 56.0, 1.1), ("elm", -349.0, 38.5, 1.0),
    # Out in the fields, far off.
    ("elm", -243.0, 8.0, 1.2), ("elm", -251.0, 5.0, 1.0), ("oak", -205.0, -14.0, 1.2), ("elm", -282.0, -22.0, 1.1),
    ("elm", -296.0, 96.0, 1.2), ("oak", -262.0, 104.0, 1.1), ("elm", -234.0, 118.0, 1.0), ("elm", -330.0, 6.0, 1.1),
    # Between the chapel and the wall.
    ("pollard", -168.0, 40.5, 1.0), ("pollard", -161.5, 40.7, 0.85), ("oak", -151.0, 27.5, 1.3), ("thorn", -146.0, 54.8, 1.0),
    ("elm", -138.0, 38.6, 1.0), ("thorn", -141.5, 55.0, 0.9), ("elm", -136.8, 57.4, 0.9), ("pollard", -136.0, 40.3, 0.9),
    # (None nearer: the city ditch lies under the wall.)
    ("elm", -160.0, 88.0, 1.1), ("elm", -141.0, 4.0, 1.15), ("oak", -176.0, -6.0, 1.0),
]


def node(i, kind, x, z, size=1.0, yaw=None):
    random.seed(i * 7919 + 3)
    yaw = math.radians(yaw if yaw is not None else random.uniform(0.0, 360.0))
    h, _mask = ground(x, z)
    c, s = math.cos(yaw) * size, math.sin(yaw) * size
    name = "%s%d" % (kind.capitalize(), i)
    return ('[node name="%s" parent="Trees" instance=ExtResource("tree_%s")]\n'
            "transform = Transform3D(%.4f, 0, %.4f, 0, %.4f, 0, %.4f, 0, %.4f, %.2f, %.2f, %.2f)\n\n"
            % (name, kind, c, s, size, -s, c, x, h - 0.05, z))


def main():
    text = open(SCENE).read()
    # Out with the old trees and their resources.
    text = re.sub(r'(?ms)^\[node name="\w+" parent="Trees" instance=ExtResource\("tree_\w+"\)\]\n.*?\n\n', "", text)
    text = re.sub(r'(?ms)^\[node name="Trees" type="Node3D" parent="\."\]\n.*?\n\n', "", text)
    text = re.sub(r'(?m)^\[ext_resource type="PackedScene" path="res://game/world/props/prop_tree_\w+\.tscn" id="tree_\w+"\]\n', "", text)
    kinds = sorted({t[0] for t in TREES})
    resources = "".join('[ext_resource type="PackedScene" path="res://game/world/props/prop_tree_%s.tscn" id="tree_%s"]\n'
                        % (k, k) for k in kinds)
    # With the scene's other resources: they must all come before anything that uses them.
    last = list(re.finditer(r"(?m)^\[ext_resource [^\n]*\n", text))[-1].end()
    text = text[:last] + resources + text[last:]
    nodes = ('[node name="Trees" type="Node3D" parent="."]\n'
             'editor_description = "The trees along the road and out in the fields. tools/build/road_dressing.py stands them '
             'on the ground from its list; change the list, not these."\n\n')
    nodes += "".join(node(i, *t) for i, t in enumerate(TREES))
    marker = '[node name="RidePath"'
    at = text.index(marker)
    text = text[:at] + nodes + text[at:]
    open(SCENE, "w").write(text)
    print("built road_dressing: %d trees" % len(TREES))


if __name__ == "__main__":
    main()
