"""Build and render focused CC-01 assembly views.

Examples:
    blender --background --python isolate_cc01.py -- --group track --render
    blender --background --python isolate_cc01.py -- --group selector,output --render
    blender --background --python isolate_cc01.py -- --group all --render
"""
import argparse
import json
import os
import re
import sys
import bpy
from mathutils import Vector

from .config import RENDER_DIGITS, RENDER_PREFIX
from .core import MM

GROUPS = {
    'housing': ['HOUSING'],
    'input': ['INPUT_ASSEMBLY'],
    'track': ['TRACK_ASSEMBLY'],
    'selector': ['RANDOM_SELECTOR'],
    'output': ['OUTPUT_ASSEMBLY'],
    'rear': ['REAR_CONSTRUCTION'],
    'electronics': ['ELECTRONICS'],
    'mechanism': ['INPUT_ASSEMBLY','TRACK_ASSEMBLY','RANDOM_SELECTOR','OUTPUT_ASSEMBLY','FASTENERS'],
    'interior': ['INPUT_ASSEMBLY','TRACK_ASSEMBLY','RANDOM_SELECTOR','OUTPUT_ASSEMBLY','ELECTRONICS','FASTENERS'],
    'all': ['HOUSING','INPUT_ASSEMBLY','TRACK_ASSEMBLY','RANDOM_SELECTOR','OUTPUT_ASSEMBLY','REAR_CONSTRUCTION','ELECTRONICS','FASTENERS'],
}

def parse_args(argv):
    parser=argparse.ArgumentParser(description='Render isolated CC-01 assembly groups.')
    parser.add_argument('--group', default='all', help='Group or comma-separated groups: housing,input,track,selector,output,rear,electronics,mechanism,interior,all')
    parser.add_argument('--render', action='store_true', help='Write a PNG review image.')
    parser.add_argument('--no-environment', action='store_true', help='Hide tabletop and backdrop.')
    parser.add_argument('--no-hardware', action='store_true', help='Hide shared fasteners in isolated views.')
    parser.add_argument('--width', type=int, default=900)
    parser.add_argument('--height', type=int, default=900)
    parser.add_argument('--output-root', default=None, help='Defaults to repository outputs/isolate folder.')
    return parser.parse_args(argv)

def selected_collections(group_arg, include_hardware=True):
    names=[]
    for token in group_arg.split(','):
        key=token.strip().lower()
        if key not in GROUPS:
            raise ValueError('Unknown group %r. Available groups: %s' % (key, ', '.join(GROUPS)))
        names.extend(GROUPS[key])
    if not include_hardware:
        names=[n for n in names if n != 'FASTENERS']
    return set(names)

def isolate_scene(group_arg, include_environment=True, include_hardware=True):
    keep=selected_collections(group_arg, include_hardware)
    for collection in bpy.data.collections:
        if collection.name == 'ENVIRONMENT':
            visible=include_environment
        elif collection.name in keep:
            visible=True
        elif collection.name in set(sum(GROUPS.values(), [])):
            visible=False
        else:
            visible=True
        collection.hide_viewport=not visible
        collection.hide_render=not visible
    bpy.context.view_layer.update()
    return keep

def visible_bounds():
    points=[]
    for obj in bpy.context.scene.objects:
        if obj.type not in {'MESH','FONT','CURVE'} or obj.hide_render:
            continue
        if any(collection.hide_render for collection in obj.users_collection):
            continue
        if obj.name.startswith('ENV_'):
            continue
        try:
            points.extend([obj.matrix_world @ Vector(corner) for corner in obj.bound_box])
        except (AttributeError, TypeError):
            continue
    if not points:
        return Vector((-210,-50,0)), Vector((210,50,730))
    lo=Vector((min(p.x for p in points),min(p.y for p in points),min(p.z for p in points)))
    hi=Vector((max(p.x for p in points),max(p.y for p in points),max(p.z for p in points)))
    return lo,hi

def frame_isolated_camera(width, height):
    camera=bpy.data.objects.get('CC01_FRONT_ORTHO_CAMERA')
    if camera is None:
        raise RuntimeError('CC01 camera was not created by the main build.')
    lo,hi=visible_bounds(); center=(lo+hi)/2
    span=hi-lo; aspect_x=width/float(height)
    # bound_box/world-matrix coordinates are already Blender metres.
    required_width=max(span.x, span.z*aspect_x, 0.080)*1.28
    lens=85.0
    distance=required_width*lens/36.0
    camera.data.type='PERSP'; camera.data.lens=lens; camera.data.sensor_width=36; camera.data.sensor_fit='HORIZONTAL'
    camera.location=(center.x,center.y-distance,center.z)
    direction=Vector((center.x,center.y,center.z))-camera.location
    camera.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
    camera.data.clip_start=.01; camera.data.clip_end=100.0
    bpy.context.scene.camera=camera
    return {'center_m':tuple(round(v,5) for v in center), 'span_m':tuple(round(v,5) for v in span), 'distance_m':round(distance,5)}

def next_path(folder, prefix=RENDER_PREFIX):
    os.makedirs(folder, exist_ok=True)
    pattern=re.compile(r'^'+re.escape(prefix)+r'(\d{'+str(RENDER_DIGITS)+r'})\.png$',re.IGNORECASE)
    highest=0
    for name in os.listdir(folder):
        match=pattern.match(name)
        if match: highest=max(highest,int(match.group(1)))
    return os.path.join(folder,f'{prefix}{highest+1:0{RENDER_DIGITS}d}.png')

def render_isolated(group_arg, output_root, width, height, framing):
    slug=group_arg.lower().replace(',','_')
    folder=os.path.join(output_root,'isolate',slug)
    filepath=next_path(folder)
    scene=bpy.context.scene; scene.render.resolution_x=width; scene.render.resolution_y=height; scene.render.resolution_percentage=100
    scene.render.filepath=os.path.abspath(filepath)
    bpy.ops.render.render(write_still=True)
    metadata={'group':group_arg,'filepath':os.path.abspath(filepath),'framing':framing}
    with open(os.path.join(folder,os.path.splitext(os.path.basename(filepath))[0]+'.json'),'w',encoding='utf-8') as handle:
        json.dump(metadata,handle,indent=2)
    print('CC-01 isolated render written to:',os.path.abspath(filepath))
    return filepath

def main(argv=None):
    from .build import build
    args=parse_args(sys.argv[sys.argv.index('--')+1:] if argv is None and '--' in sys.argv else (argv or []))
    build()
    keep=isolate_scene(args.group,not args.no_environment,not args.no_hardware)
    framing=frame_isolated_camera(args.width,args.height)
    print('CC-01 isolated groups:', ', '.join(sorted(keep)))
    if args.render:
        root=args.output_root or os.path.abspath(os.path.join(os.path.dirname(__file__),'..','outputs'))
        render_isolated(args.group,root,args.width,args.height,framing)

if __name__=='__main__':
    main()
