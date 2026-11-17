"""Basic presentation environment, camera, and lighting."""
import bpy
from mathutils import Vector
from .core import box, collection, MM

def look_at(obj, target_mm):
    direction=Vector(target_mm)*MM-obj.location
    obj.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()

def create_basic_scene(materials):
    scene=bpy.context.scene
    # Blender 4.x renamed Eevee; use whichever engine this installation exposes.
    engines={item.identifier for item in scene.render.bl_rna.properties['engine'].enum_items}
    try:
        scene.render.engine='BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in engines else 'BLENDER_EEVEE'
    except TypeError:
        # Defensive fallback for older Blender builds with incomplete RNA enum data.
        scene.render.engine='BLENDER_EEVEE'
    # Portrait product frame; the P1 camera set below is orthographic so the
    # review renders can be used for dimension and clearance inspection.
    scene.render.resolution_x=900; scene.render.resolution_y=1200; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.render.film_transparent=False
    try:
        scene.view_settings.view_transform='AgX'
    except TypeError:
        try: scene.view_settings.view_transform='Filmic'
        except TypeError: pass
    for look in ('AgX - Medium High Contrast','Medium High Contrast','Medium High Contrast'):
        try:
            scene.view_settings.look=look
            break
        except TypeError:
            continue
    scene.view_settings.exposure=0.75
    if scene.world is None:
        scene.world=bpy.data.worlds.new('CC01_WORLD')
    scene.world.use_nodes=True; bg=scene.world.node_tree.nodes.get('Background')
    bg.inputs['Color'].default_value=(.032,.040,.055,1); bg.inputs['Strength'].default_value=.62
    env=collection('ENVIRONMENT')
    # World coordinates: Z is up, Y is depth, front/glass is negative Y.
    table=box('ENV_TABLE',(0,0,-8),(1500,1100,16),env,None,3); table.data.materials.append(materials['WALNUT'])
    wall=box('ENV_BACK_WALL',(0,245,430),(1500,20,900),env,None,2); wall.data.materials.append(materials['BACKDROP'])
    def ortho(name, loc, target, scale):
        data=bpy.data.cameras.new(name); cam=bpy.data.objects.new(name,data); scene.collection.objects.link(cam)
        data.type='ORTHO'; data.ortho_scale=scale*MM; data.clip_start=.01; data.clip_end=10.0
        cam.location=Vector(loc)*MM; look_at(cam,target); return cam

    cameras = {
        'CC01_FRONT_ORTHO_CAMERA': ortho('CC01_FRONT_ORTHO_CAMERA',(0,-1600,365),(0,0,365),820),
        'CC01_REAR_ORTHO_CAMERA': ortho('CC01_REAR_ORTHO_CAMERA',(0,1600,365),(0,0,365),820),
        'CC01_LEFT_ORTHO_CAMERA': ortho('CC01_LEFT_ORTHO_CAMERA',(-1600,0,365),(0,0,365),340),
        'CC01_RIGHT_ORTHO_CAMERA': ortho('CC01_RIGHT_ORTHO_CAMERA',(1600,0,365),(0,0,365),340),
        'CC01_TOP_ORTHO_CAMERA': ortho('CC01_TOP_ORTHO_CAMERA',(0,0,1600),(0,0,0),470),
    }
    scene.camera=cameras['CC01_FRONT_ORTHO_CAMERA']

    def area(name, loc, energy, size, color, target=(0,0,365), shape='DISK', specular=1.0):
        ld=bpy.data.lights.new(name,'AREA'); ld.energy=energy; ld.shape=shape; ld.size=size; ld.color=color
        if hasattr(ld,'use_shadow'): ld.use_shadow=True
        if hasattr(ld,'specular_factor'): ld.specular_factor=specular
        ob=bpy.data.objects.new(name,ld); scene.collection.objects.link(ob); ob.location=Vector(loc)*MM; look_at(ob,target)
        return ob

    # Cinematic product rig: warm key, cool fill, broad front reflection,
    # controlled top highlight, and a cool rear separation source.
    area('KEY_WARM_LARGE',(-430,-560,560),3000,460,(1.0,.72,.50),shape='DISK',specular=.85)
    area('FILL_COOL_LARGE',(430,-520,390),1900,560,(.48,.65,1.0),shape='DISK',specular=.55)
    area('FRONT_REFLECTION_CARD',(0,-820,410),2600,700,(1.0,.94,.84),shape='DISK',specular=1.0)
    area('TOP_EDGE_STRIP',(0,-260,880),1700,260,(1.0,.82,.62),target=(0,0,620),shape='RECTANGLE',specular=.9)
    area('REAR_RIM_COOL',(0,330,520),2400,220,(.42,.62,1.0),shape='DISK',specular=1.0)
    area('LEFT_WALNUT_KICK',(-560,-80,330),1200,260,(1.0,.48,.25),target=(-100,0,330),shape='DISK',specular=.45)
    sun_data=bpy.data.lights.new('AMBIENT_SUN','SUN'); sun_data.energy=0.38; sun_data.angle=0.22
    sun=bpy.data.objects.new('AMBIENT_SUN',sun_data); scene.collection.objects.link(sun); sun.location=Vector((-300,-500,900))*MM; look_at(sun,(0,0,365))

def set_solid_viewport():
    """Return visible 3D viewports to Solid mode after the build."""
    screen=getattr(bpy.context,'screen',None)
    if screen is None:
        return
    for area in screen.areas:
        if area.type=='VIEW_3D':
            for space in area.spaces:
                if space.type=='VIEW_3D':
                    space.shading.type='SOLID'
                    space.shading.light='STUDIO'
                    space.shading.color_type='MATERIAL'
