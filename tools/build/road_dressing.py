"""Stands the trees, and everything else in the fields, along the road in
(night 0) on the ground the fields' script makes: it rewrites the Trees
and Dressing nodes of game/world/road/env_road.tscn from the lists below,
each thing set down at the ground's own height there
(tools/build/env_road_fields.py). Run it again after changing a list or
the lie of the land; things moved by hand in the editor are put back where
the lists say, so change the lists.

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
    # Dead oaks: one by the road, the rooks' tree; others in the fields.
    ("snag", -189.0, 37.2, 1.1), ("snag", -301.0, 61.0, 0.9), ("snag", -138.0, 28.0, 1.0), ("snag", -246.0, 96.0, 1.2),
    # Thorns and willows down the ditches and in the hedges.
    ("thorn", -203.0, 39.4, 0.9), ("thorn", -196.5, 54.9, 1.0), ("pollard", -209.0, 53.6, 1.0), ("thorn", -226.0, 55.3, 0.8),
    ("thorn", -245.0, 55.4, 1.1), ("pollard", -233.5, 40.2, 1.0), ("thorn", -283.0, 38.7, 1.0), ("thorn", -257.0, 38.8, 0.85),
    ("pollard", -176.0, 40.6, 0.95), ("thorn", -157.0, 54.6, 0.9), ("pollard", -150.5, 53.4, 0.9), ("thorn", -172.0, 39.2, 0.8),
    ("pollard", -136.6, 63.0, 1.0), ("pollard", -136.4, 34.5, 0.9), ("thorn", -214.5, 24.0, 1.0), ("thorn", -213.5, 6.0, 0.9),
    ("thorn", -152.5, 84.0, 1.0), ("thorn", -151.5, 104.0, 0.9), ("thorn", -276.5, 18.0, 1.0),
    # A copse on the north rise, and one behind the cot.
    ("elm", -228.0, 14.0, 0.9), ("oak", -234.0, 19.0, 0.9), ("thorn", -224.0, 20.0, 1.2), ("elm", -270.0, 92.0, 1.0),
    ("oak", -257.0, 90.0, 0.8),
]

# Everything else: kind, x, z, the way it faces in degrees (0: its front to
# the north, -z), and optionally its size. A kind is a model
# (art/models/prop_field_<kind>.glb) unless SCENES names a scene for it.
SCENES = {"mill": "res://game/world/props/prop_field_mill.tscn", "shrine": "res://game/world/props/prop_field_shrine.tscn",
          "cot": "res://game/world/props/prop_field_cot.tscn"}


def run(kind, x0, z0, x1, z1, skip=()):
    """Ten-metre lengths of hedge or seven of fence from one point to another, with gaps at `skip`."""
    step = 9.6 if kind == "hedge" else 7.0
    length = math.hypot(x1 - x0, z1 - z0)
    n = max(int(round(length / step)), 1)
    yaw = math.degrees(math.atan2(z1 - z0, x1 - x0))
    out = []
    for i in range(n):
        if i in skip:
            continue
        k = (i + 0.5) / n
        out.append((kind, x0 + (x1 - x0) * k, z0 + (z1 - z0) * k, yaw + (180.0 if i % 2 else 0.0)))
    return out


DRESSING = (
    # Hedges along the road, broken, and down the furlongs' edges away from it.
    run("hedge", -302.0, 55.3, -207.0, 55.2, skip=(2, 7))
    + run("hedge", -296.0, 38.7, -238.0, 38.6, skip=(3,))
    + run("hedge", -214.0, 36.5, -214.0, -30.0, skip=(4,))
    + run("hedge", -276.0, 36.5, -276.0, -12.0)
    + run("hedge", -152.0, 58.5, -152.0, 118.0, skip=(3,))
    + run("hedge", -214.0, 80.0, -214.0, 128.0)
    + run("hedge", -338.0, 56.0, -338.0, 104.0)
    + run("hedge", -200.0, 38.9, -162.0, 39.0, skip=(1, 2))
    + [
        # Gates in the gaps.
        ("gate", -268.0, 38.7, 0.0), ("gate", -278.5, 55.3, 180.0),
        # Hurdles: a fold in the corner of the north field, and by the cot.
        ("fence", -146.5, 39.6, 0.0), ("fence", -143.2, 36.3, 90.0), ("fence", -146.5, 33.0, 180.0), ("fence", -258.0, 73.0, 0.0),
        # The people of the fields: a cot with a light, its ricks; another far to the north.
        ("cot", -262.0, 78.0, 6.0), ("rick", -252.5, 80.5, 0.0), ("rick", -249.6, 84.6, 40.0), ("rick", -238.0, 24.5, 0.0),
        ("cot", -206.0, 0.0, 172.0),
        # The mill on the western rise, against the last light.
        ("mill", -326.0, 16.0, 105.0),
        # On the road: a shrine somebody still lights, a mile stone, planks over the ditch to the chapel's gate, a wrecked wheel.
        ("shrine", -207.5, 51.0, 0.0), ("stone", -171.0, 43.3, 20.0), ("bridge", -180.8, 52.5, 0.0), ("wreck", -151.5, 41.9, 200.0),
        ("bridge", -268.0, 41.5, 0.0), ("stone", -258.0, 50.6, 200.0),
        # And in the fields, things with arms.
        ("scarecrow", -197.0, 29.0, 100.0), ("scarecrow", -247.0, 67.0, 250.0), ("scarecrow", -165.0, 22.0, 60.0),
    ]
)


def node(i, kind, x, z, size=1.0, yaw=None):
    random.seed(i * 7919 + 3)
    yaw = math.radians(yaw if yaw is not None else random.uniform(0.0, 360.0))
    h, _mask = ground(x, z)
    c, s = math.cos(yaw) * size, math.sin(yaw) * size
    name = "%s%d" % (kind.capitalize(), i)
    return ('[node name="%s" parent="Trees" instance=ExtResource("tree_%s")]\n'
            "transform = Transform3D(%.4f, 0, %.4f, 0, %.4f, 0, %.4f, 0, %.4f, %.2f, %.2f, %.2f)\n\n"
            % (name, kind, c, s, size, -s, c, x, h - 0.05, z))


def dress(i, kind, x, z, yaw=0.0, size=1.0):
    h, _mask = ground(x, z)
    a = math.radians(yaw)
    c, s = math.cos(a) * size, math.sin(a) * size
    return ('[node name="%s%d" parent="Dressing" instance=ExtResource("field_%s")]\n'
            "transform = Transform3D(%.4f, 0, %.4f, 0, %.4f, 0, %.4f, 0, %.4f, %.2f, %.2f, %.2f)\n\n"
            % (kind.capitalize(), i, kind, c, -s, size, s, c, x, h - 0.03, z))


def main():
    text = open(SCENE).read()
    # Out with the old dressing and its resources.
    text = re.sub(r'(?ms)^\[node name="\w+" parent="Dressing" instance=ExtResource\("field_\w+"\)\]\n.*?\n\n', "", text)
    text = re.sub(r'(?ms)^\[node name="Dressing" type="Node3D" parent="\."\]\n.*?\n\n', "", text)
    text = re.sub(r'(?m)^\[ext_resource type="PackedScene" path="[^"]+" id="field_\w+"\]\n', "", text)
    # Out with the old trees and their resources.
    text = re.sub(r'(?ms)^\[node name="\w+" parent="Trees" instance=ExtResource\("tree_\w+"\)\]\n.*?\n\n', "", text)
    text = re.sub(r'(?ms)^\[node name="Trees" type="Node3D" parent="\."\]\n.*?\n\n', "", text)
    text = re.sub(r'(?m)^\[ext_resource type="PackedScene" path="res://game/world/props/prop_tree_\w+\.tscn" id="tree_\w+"\]\n', "", text)
    kinds = sorted({t[0] for t in TREES})
    resources = "".join('[ext_resource type="PackedScene" path="res://game/world/props/prop_tree_%s.tscn" id="tree_%s"]\n'
                        % (k, k) for k in kinds)
    # With the scene's other resources: they must all come before anything that uses them.
    last = list(re.finditer(r"(?m)^\[ext_resource [^\n]*\n", text))[-1].end()
    for k in sorted({d[0] for d in DRESSING}):
        resources += '[ext_resource type="PackedScene" path="%s" id="field_%s"]\n' % (
            SCENES.get(k, "res://art/models/prop_field_%s.glb" % k), k)
    text = text[:last] + resources + text[last:]
    nodes = ('[node name="Trees" type="Node3D" parent="."]\n'
             'editor_description = "The trees along the road and out in the fields. tools/build/road_dressing.py stands them '
             'on the ground from its list; change the list, not these."\n\n')
    nodes += "".join(node(i, *t) for i, t in enumerate(TREES))
    nodes += ('[node name="Dressing" type="Node3D" parent="."]\n'
              'editor_description = "Hedges, hurdles, gates, the cots and their ricks, the mill, the shrine, the scarecrows '
              '(tools/build/prop_field.py). tools/build/road_dressing.py stands them on the ground from its list; change the list, '
              'not these."\n\n')
    nodes += "".join(dress(i, *d) for i, d in enumerate(DRESSING))
    marker = '[node name="RidePath"'
    at = text.index(marker)
    text = text[:at] + nodes + text[at:]
    open(SCENE, "w").write(text)
    print("built road_dressing: %d trees, %d other things" % (len(TREES), len(DRESSING)))


if __name__ == "__main__":
    main()
