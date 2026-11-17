"""Build CC-01 and render the five P1 orthographic review views."""
import importlib
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

build = importlib.import_module('src.build')
build = importlib.reload(build)
build.build()

scene = __import__('bpy').context.scene
out_dir = os.path.join(ROOT, 'outputs', 'orthographic')
os.makedirs(out_dir, exist_ok=True)
views = {
    'front': 'CC01_FRONT_ORTHO_CAMERA',
    'rear': 'CC01_REAR_ORTHO_CAMERA',
    'left': 'CC01_LEFT_ORTHO_CAMERA',
    'right': 'CC01_RIGHT_ORTHO_CAMERA',
    'top': 'CC01_TOP_ORTHO_CAMERA',
}
for label, camera_name in views.items():
    scene.camera = __import__('bpy').data.objects[camera_name]
    scene.render.resolution_x = 900
    scene.render.resolution_y = 1200 if label in {'front', 'rear'} else 900
    scene.render.resolution_percentage = 100
    scene.render.filepath = os.path.join(out_dir, f'{label}.png')
    __import__('bpy').ops.render.render(write_still=True)
    print('CC-01 orthographic render written to:', scene.render.filepath)
