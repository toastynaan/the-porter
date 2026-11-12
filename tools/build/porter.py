"""Shared helpers for The Porter's Blender build scripts (tools/build/*.py).

Every model in the game is built by a script (Look and Feel, "Asset
pipeline"): run one with tools/build.sh <name>, and it writes
art/models/<name>.glb. Conventions:

- Scripts work in the game's own space: metres, +Y up, -Z forward, as Godot
  has it. Mesh.vert() takes care of Blender's Z-up.
- An asset's origin is on the floor at the middle of its footprint, its front
  facing -Z (docs/systems/assets.md).
- Materials are exported by name only, with no images. A material called
  "plaster_white" is linked on import to
  game/world/materials/real/plaster_white.tres (tools/build/link_materials.py),
  so every model shares the game's materials and their textures.
- Vertex colours are exported: materials multiply them in (soot from above,
  damp from below), and the ground's shader reads them as masks.
- An object whose name ends "-colonly" becomes collision only in Godot, and
  "-col" a mesh with collision (Godot's import suffixes).
"""
import math
import os
import random
import sys

import bpy
from mathutils import Vector, noise

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS = os.path.join(ROOT, "art", "models")


def reset(seed=1):
    """An empty file, and the same random numbers every run."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    random.seed(seed)


def material(name):
    return bpy.data.materials.get(name) or bpy.data.materials.new(name)


def fbm(x, z, scale=1.0, octaves=4, seed=0.0):
    """Smooth noise in -1..1 over the ground plane."""
    return noise.fractal(Vector((x * scale + seed * 17.3, z * scale - seed * 9.1, seed)), 1.0, 2.0, octaves)


def srgb(r, g, b, a=1.0):
    """A colour as it looks on screen, made into the linear one a vertex holds."""
    lin = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (lin(r), lin(g), lin(b), a)


def smoothstep(a, b, x):
    if a == b:
        return 0.0 if x < a else 1.0
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3.0 - 2.0 * t)


def lerp(a, b, t):
    return a + (b - a) * t


class Mesh:
    """Gathers one object's geometry: vertices in the game's space, each with
    a colour and a UV, and faces (counter-clockwise seen from outside) each
    with a material."""

    def __init__(self, name):
        self.name = name
        self.verts = []
        self.colors = []
        self.uvs = []
        self.faces = []
        self.face_materials = []
        self.materials = []

    def vert(self, x, y, z, color=(1.0, 1.0, 1.0, 1.0), uv=(0.0, 0.0)):
        # The game's (x, y up, z) is Blender's (x, -z, y up).
        self.verts.append((x, -z, y))
        self.colors.append(tuple(color) if len(color) == 4 else (color[0], color[1], color[2], 1.0))
        self.uvs.append(uv)
        return len(self.verts) - 1

    def face(self, indices, mat):
        if mat not in self.materials:
            self.materials.append(mat)
        self.faces.append(tuple(indices))
        self.face_materials.append(self.materials.index(mat))

    def quad(self, a, b, c, d, mat, color=(1.0, 1.0, 1.0, 1.0), uvs=None):
        """A four-sided face from four points (x, y, z), its own vertices."""
        uvs = uvs or [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
        colors = color if isinstance(color, list) else [color] * 4
        ids = [self.vert(p[0], p[1], p[2], colors[i], uvs[i]) for i, p in enumerate((a, b, c, d))]
        self.face(ids, mat)
        return ids

    def poly(self, points, mat, color=(1.0, 1.0, 1.0, 1.0), uvs=None, facing=None):
        """A flat face through `points` (x, y, z), its own vertices. With
        `facing` (a direction), the face is turned to look that way, so the
        order the points are given in doesn't matter."""
        n = len(points)
        colors = list(color) if isinstance(color, list) else [color] * n
        uvs = list(uvs) if uvs else [(0.0, 0.0)] * n
        points = list(points)
        if facing is not None:
            nx = ny = nz = 0.0
            for i in range(n):
                a, b = points[i], points[(i + 1) % n]
                nx += (a[1] - b[1]) * (a[2] + b[2])
                ny += (a[2] - b[2]) * (a[0] + b[0])
                nz += (a[0] - b[0]) * (a[1] + b[1])
            if nx * facing[0] + ny * facing[1] + nz * facing[2] < 0.0:
                points.reverse()
                colors.reverse()
                uvs.reverse()
        ids = [self.vert(p[0], p[1], p[2], colors[i], uvs[i]) for i, p in enumerate(points)]
        self.face(ids, mat)
        return ids

    def tube(self, points, radii, sides, mat, color=(1.0, 1.0, 1.0, 1.0), caps=False, squash=(1.0, 1.0)):
        """A tube along `points` (x, y, z), `sides` round, `radii` at each
        point. `squash` flattens the ring (its width and height), for a body
        that isn't round. Returns the rings' vertex indices."""
        pts = [Vector(p) for p in points]
        colors = color if isinstance(color, list) else [color] * len(pts)
        first = (pts[1] - pts[0]).normalized()
        side = first.cross(Vector((0.0, 1.0, 0.0)))
        side = side.normalized() if side.length > 1e-4 else Vector((1.0, 0.0, 0.0))
        rings = []
        for i, p in enumerate(pts):
            ahead = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
            side = (side - ahead * side.dot(ahead)).normalized()
            other = side.cross(ahead)
            ring = []
            for k in range(sides):
                a = math.tau * k / sides
                q = p + side * (math.cos(a) * radii[i] * squash[0]) + other * (math.sin(a) * radii[i] * squash[1])
                ring.append(self.vert(q.x, q.y, q.z, colors[i], (k / sides, i / max(len(pts) - 1, 1))))
            rings.append(ring)
        for a, b in zip(rings, rings[1:]):
            for k in range(sides):
                t = (k + 1) % sides
                self.face((a[k], b[k], b[t], a[t]), mat)
        if caps:
            self.face(tuple(rings[0]), mat)
            self.face(tuple(reversed(rings[-1])), mat)
        return rings

    def box(self, lo, hi, mat, color=(1.0, 1.0, 1.0, 1.0), top_color=None, faces="xXyYzZ"):
        """A box from corner `lo` to corner `hi`. `faces` names the sides to
        make: x and X are the low and high x sides, and so on. `top_color`
        tints the upper vertices of the sides, for a gradient up the wall."""
        x0, y0, z0 = lo
        x1, y1, z1 = hi
        up = top_color or color
        side = [color, color, up, up]
        if "x" in faces:
            self.quad((x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0), mat, side)
        if "X" in faces:
            self.quad((x1, y0, z1), (x1, y0, z0), (x1, y1, z0), (x1, y1, z1), mat, side)
        if "z" in faces:
            self.quad((x1, y0, z0), (x0, y0, z0), (x0, y1, z0), (x1, y1, z0), mat, side)
        if "Z" in faces:
            self.quad((x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1), mat, side)
        if "y" in faces:
            self.quad((x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1), mat, color)
        if "Y" in faces:
            self.quad((x0, y1, z1), (x1, y1, z1), (x1, y1, z0), (x0, y1, z0), mat, up)

    def build(self, smooth=False, collection=None, origin=None, parent=None):
        """Makes the Blender object. `origin` (x, y, z in the game's space)
        is the point it turns about, for a wheel or a limb; `parent` the
        object it hangs from."""
        verts = self.verts
        if origin is not None:
            o = (origin[0], -origin[2], origin[1])
            verts = [(v[0] - o[0], v[1] - o[1], v[2] - o[2]) for v in verts]
        mesh = bpy.data.meshes.new(self.name)
        mesh.from_pydata(verts, [], self.faces)
        for name in self.materials:
            mesh.materials.append(material(name))
        for poly, index in zip(mesh.polygons, self.face_materials):
            poly.material_index = index
            poly.use_smooth = smooth
        colors = mesh.color_attributes.new("Color", "FLOAT_COLOR", "POINT")
        for i, c in enumerate(self.colors):
            colors.data[i].color = c
        mesh.color_attributes.active_color = colors
        uv = mesh.uv_layers.new(name="UVMap")
        for loop in mesh.loops:
            uv.data[loop.index].uv = self.uvs[loop.vertex_index]
        mesh.update()
        mesh.validate()
        obj = bpy.data.objects.new(self.name, mesh)
        (collection or bpy.context.scene.collection).objects.link(obj)
        if origin is not None:
            obj.location = (origin[0], -origin[2], origin[1])
        if parent is not None:
            # Keep it where it is in the world as it is hung from its parent.
            obj.parent = parent
            obj.location = [a - b for a, b in zip(obj.location, parent.matrix_world.translation)]
        bpy.context.view_layer.update()
        return obj


def export(name):
    """Writes everything in the file to art/models/<name>.glb."""
    os.makedirs(MODELS, exist_ok=True)
    path = os.path.join(MODELS, name + ".glb")
    bpy.ops.export_scene.gltf(
        filepath=path,
        export_format="GLB",
        export_yup=True,
        export_apply=True,
        export_materials="EXPORT",
        export_image_format="NONE",
        export_vertex_color="ACTIVE",
        export_all_vertex_colors=False,
        export_active_vertex_color_when_no_material=True,
        export_cameras=False,
        export_lights=False,
    )
    tris = sum(len(p.vertices) - 2 for o in bpy.data.objects if o.type == "MESH" for p in o.data.polygons)
    print("built %s: %d objects, %d triangles" % (name, len(bpy.data.objects), tris))
    return path


def argv():
    """Arguments after the "--" on Blender's command line."""
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
