"""Build CC-01 and render isolated track views from several angles."""
import importlib
import os
import sys
import bpy
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

build = importlib.import_module('src.build')
build = importlib.reload(build)
isolate = importlib.import_module('src.isolate')
isolate = importlib.reload(isolate)
build.build()
isolate.isolate_scene('track', include_environment=False, include_hardware=True)

scene = bpy.context.scene
track_objects = [obj for obj in scene.objects if obj.type in {'MESH', 'CURVE'} and not obj.hide_render and not obj.name.startswith('ENV_')]
points = [obj.matrix_world @ Vector(corner) for obj in track_objects for corner in obj.bound_box]
lo = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
hi = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
center = (lo + hi) / 2.0
span = hi - lo

def camera(name, location, target, ortho_scale=None, lens=58.0):
    data = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, data)
    scene.collection.objects.link(cam)
    cam.location = Vector(location)
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    data.clip_start = 0.005
    data.clip_end = 10.0
    if ortho_scale is not None:
        data.type = 'ORTHO'
        data.ortho_scale = ortho_scale
    else:
        data.type = 'PERSP'
        data.lens = lens
        data.sensor_width = 36
    return cam

views = {
    'front': camera('CC01_TRACK_FRONT', (center.x, -1.1, center.z), (center.x, center.y, center.z), 0.44),
    'left': camera('CC01_TRACK_LEFT', (-1.0, center.y, center.z), (center.x, center.y, center.z), 0.42),
    'right': camera('CC01_TRACK_RIGHT', (1.0, center.y, center.z), (center.x, center.y, center.z), 0.42),
    'top': camera('CC01_TRACK_TOP', (center.x, center.y, 1.3), (center.x, center.y, center.z), 0.42),
    'perspective': camera('CC01_TRACK_PERSPECTIVE', (0.55, -0.85, 0.82), (center.x, center.y, center.z), None, 62.0),
}

out_dir = os.path.join(ROOT, 'outputs', 'isolate', 'track_angles')
os.makedirs(out_dir, exist_ok=True)
scene.render.resolution_x = 1000
scene.render.resolution_y = 700
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
for label, cam in views.items():
    scene.camera = cam
    scene.render.filepath = os.path.join(out_dir, f'{label}.png')
    bpy.ops.render.render(write_still=True)
    print('CC-01 track-angle render written to:', scene.render.filepath)
