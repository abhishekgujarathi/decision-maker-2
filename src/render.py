"""Render the calibrated CC-01 scene to a predictable review image."""
import os
import re
import bpy
from .config import RENDER_PREFIX, RENDER_DIGITS

def next_review_path(output_dir, prefix=RENDER_PREFIX):
    os.makedirs(output_dir, exist_ok=True)
    pattern=re.compile(r'^'+re.escape(prefix)+r'(\d{'+str(RENDER_DIGITS)+r'})\.png$', re.IGNORECASE)
    highest=0
    for filename in os.listdir(output_dir):
        match=pattern.match(filename)
        if match:
            highest=max(highest,int(match.group(1)))
    next_number=highest+1
    filename=f'{prefix}{next_number:0{RENDER_DIGITS}d}.png'
    return os.path.abspath(os.path.join(output_dir,filename))

def render_review(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    filepath=next_review_path(output_dir)
    scene=bpy.context.scene
    scene.render.filepath=filepath
    scene.render.resolution_percentage=100
    bpy.ops.render.render(write_still=True)
    print('CC-01 review render written to:', filepath)
    return filepath
