"""Build the geometry-only Chaos Chamber CC-01.

Run inside Blender's scripting workspace or with:
    blender --background --python build_cc01.py

This pass intentionally creates no materials, lights, cameras, or animation.
It creates separate, named, editable production geometry with real thickness.
"""
import math
import os
import sys
import types
import bpy
from mathutils import Vector


def _load_helpers():
    """Make helper modules work from Blender Text Editor and command line.

    Blender's Text Editor does not always add the opened script's directory to
    sys.path.  Try the script directory, the .blend directory, the current
    directory, and finally text blocks already loaded in the current .blend.
    """
    candidates = []
    script_file = globals().get('__file__')
    if script_file:
        candidates.append(os.path.dirname(os.path.abspath(script_file)))
    if bpy.data.filepath:
        candidates.append(os.path.dirname(os.path.abspath(bpy.data.filepath)))
    candidates.append(os.getcwd())
    # Fallback for a copied/duplicated Blender Text Editor block such as
    # "build_cc01.py.001", which has no meaningful __file__.  This is the
    # shared workspace location used for this project.
    candidates.append(r'L:\coding\YOUTUBE\blenderr\code-python')
    for folder in candidates:
        if folder and folder not in sys.path:
            sys.path.insert(0, folder)
    try:
        import importlib
        importlib.import_module('src.config')
        importlib.import_module('src.core')
        return
    except ModuleNotFoundError:
        pass

    def text_module(module_name, text_name):
        text = bpy.data.texts.get(text_name)
        if text is None:
            raise ModuleNotFoundError(
                'Could not find %s. Keep cc01_config.py, cc01_core.py, and '
                'build_cc01.py in the same folder, or load both helper files '
                'into Blender Text Editor.' % module_name)
        module = types.ModuleType(module_name)
        module.__file__ = text_name
        exec(compile(text.as_string(), text_name, 'exec'), module.__dict__)
        sys.modules[module_name] = module
        return module

    text_module('src.config', 'config.py')
    text_module('src.core', 'core.py')


_load_helpers()
import importlib
import src.config as _config_module
_config_module = importlib.reload(_config_module)
import src.core as _core_module
# Blender keeps imported modules alive between Text Editor runs. Reload the
# helper so a rerun cannot keep an older cut_boxes signature or Boolean API
# mapping in memory.
_core_module = importlib.reload(_core_module)
from src.config import *
from src.core import *
from src.paths import track_centerline, full_ball_path, selector_branch_paths, selector_drop_path, path_line
import src.materials as _materials_module
import src.scene as _scene_module
_materials_module = importlib.reload(_materials_module)
_scene_module = importlib.reload(_scene_module)
create_materials = _materials_module.create_materials
assign_by_role = _materials_module.assign_by_role
create_basic_scene = _scene_module.create_basic_scene
set_solid_viewport = _scene_module.set_solid_viewport

def clear():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for block in list(datablocks):
            if block.users == 0: datablocks.remove(block)

def tag_component(obj, component_id, group):
    obj['component_id'] = component_id
    obj['component_group'] = group
    return obj


def link_to(obj, coll):
    if coll.objects.get(obj.name) is None:
        coll.objects.link(obj)


def make_track(root, coll, ball_coll):
    # One continuous front-elevation path.  Each run has a modest 5–8° drop;
    # the semicircles preserve tangent direction through both hairpins.
    p=track_centerline()
    # Keep the single source centerline, but expose its manufacturing pieces
    # as separate editable collections for the Phase 2 detailing pass.
    groups = [
        ('TRACK_RUN_01', 0, 28), ('TRACK_UTURN_01', 27, 51),
        ('TRACK_RUN_02', 50, 78), ('TRACK_UTURN_02', 77, 101),
        ('TRACK_RUN_03', 100, 128), ('TRACK_UTURN_03', 127, 151),
    ]
    for index, (name, start, end) in enumerate(groups):
        part_coll = collection(name, coll)
        create_track_channel(
            name, p[start:end], part_coll, root,
            TRACK_W, TRACK_T, TRACK_WALL, TRACK_T,
            cap_start=index == 0,
            cap_end=False,
            tangent_points=p,
            point_offset=start,
        )
        for obj in list(part_coll.objects):
            link_to(obj, coll)
            tag_component(obj, 'CC-310', 'TRACK')
    # The exit transition is one continuous mesh. The two named guide
    # collections remain as manufacturing/review group labels, but they share
    # the same geometry so no internal seam can create an overlap.
    exit_geom_coll = collection('TRACK_EXIT_GUIDE_CONTINUOUS', coll)
    exit_group_01 = collection('TRACK_EXIT_GUIDE_01', coll)
    exit_group_02 = collection('TRACK_EXIT_GUIDE_02', coll)
    create_track_channel(
        'TRACK_EXIT_GUIDE', p[150:168], exit_geom_coll, root,
        TRACK_W, TRACK_T, TRACK_WALL, TRACK_T,
        cap_start=False, cap_end=True,
        tangent_points=p, point_offset=150,
    )
    for obj in list(exit_geom_coll.objects):
        link_to(obj, coll)
        link_to(obj, exit_group_01)
        link_to(obj, exit_group_02)
        tag_component(obj, 'CC-310', 'TRACK_EXIT_GUIDE')
    bracket_coll = collection('TRACK_BRACKETS', coll)
    fastener_coll = collection('TRACK_FASTENERS', coll)
    # Path-test ball: its authored path is stored on the object for a later
    # Follow Path animation, while the current pose remains easy to inspect.
    ball_path = full_ball_path()['INPUT_TO_SELECTOR']
    path_obj = sweep_tube('BALL_CENTRE_PATH', ball_path, 0.45, ball_coll, root, 8)
    path_obj.hide_render = True
    path_obj['path_role'] = '18 mm ball centreline / animation-ready'
    path_obj['sample_count'] = len(ball_path)
    ball = sphere('STEEL_BALL_PATH_TEST', ball_path[0], BALL_R, ball_coll, root)
    ball['diameter_mm'] = BALL_D
    ball['path_object'] = path_obj.name
    ball['pose'] = 'INPUT'
    # Supporting tabs are spaced at real mounting stations, not floating décor.
    for i, (x,y) in enumerate([(-90,584),(90,564),(90,522),(-90,500),(-90,456),(90,436),(40,369)]):
        tab_z = TRACK_Z - TRACK_T/2 - TAB_T/2
        standoff_z = PLATE_Z_FRONT + STANDOFF_L/2
        bracket = box('TRACK_SUPPORT_%02d'%i,(x,y,tab_z),(28,18,TAB_T),bracket_coll,root,1.2)
        tag_component(bracket, 'CC-310', 'TRACK_BRACKET')
        standoff = cyl('TRACK_STANDOFF_%02d'%i,(x,y,standoff_z),3,STANDOFF_L,bracket_coll,root,'Z',20,0.25)
        tag_component(standoff, 'CC-310', 'TRACK_BRACKET')
        washer, screw = fastener('TRACK_FASTENER_%02d'%i,(x,y,PLATE_Z_BACK-1.5),fastener_coll,root,'Z',3,5)
        tag_component(washer, 'CC-310', 'TRACK_FASTENER')
        tag_component(screw, 'CC-310', 'TRACK_FASTENER')
    # Dedicated support stations under all three 30 mm-radius hairpins keep the
    # curved pieces constrained without changing the validated centerline.
    for i, (x, y) in enumerate(((145, 530), (-145, 440), (145, 350)), 1):
        tab_z = TRACK_Z - TRACK_T/2 - TAB_T/2
        standoff_z = PLATE_Z_FRONT + STANDOFF_L/2
        turn_bracket = box('TRACK_UTURN_SUPPORT_%02d' % i,(x,y,tab_z),(34,26,TAB_T),bracket_coll,root,1.2)
        turn_bracket['support_role'] = 'U-turn load support'
        turn_standoff = cyl('TRACK_UTURN_STANDOFF_%02d' % i,(x,y,standoff_z),3.5,STANDOFF_L,bracket_coll,root,'Z',20,0.25)
        tag_component(turn_bracket, 'CC-310', 'TRACK_BRACKET')
        tag_component(turn_standoff, 'CC-310', 'TRACK_BRACKET')
        washer, screw = fastener('TRACK_UTURN_FASTENER_%02d' % i,(x,y,PLATE_Z_BACK-1.5),fastener_coll,root,'Z',3,5)
        tag_component(washer, 'CC-310', 'TRACK_FASTENER')
        tag_component(screw, 'CC-310', 'TRACK_FASTENER')
    return p

def make_housing(root, housing, hardware_coll):
    # Footed cabinet envelope with furniture-grade edge radii represented as
    # real solids. In this local authoring frame, +Z is the front; the root
    # maps it to world -Y.
    box('WALNUT_LEFT',(-HX+WALNUT_T/2,H/2,0),(WALNUT_T,H-FOOT_H,D),housing,root,2)
    box('WALNUT_RIGHT',(HX-WALNUT_T/2,H/2,0),(WALNUT_T,H-FOOT_H,D),housing,root,2)
    box('BASE_SIDE_LEFT',(-HX+WALNUT_T/2,FOOT_H+CHASSIS_H/2,0),(WALNUT_T,CHASSIS_H,D),housing,root,2)
    box('BASE_SIDE_RIGHT',(HX-WALNUT_T/2,FOOT_H+CHASSIS_H/2,0),(WALNUT_T,CHASSIS_H,D),housing,root,2)
    box('BASE_FRONT_FASCIA',(0,FOOT_H+CHASSIS_H/2,FRONT_Z-8),(384,CHASSIS_H-10,16),housing,root,2)
    # Keep the header and its nameplate inside the 250 mm world-depth envelope;
    # the structural frame remains the defined front datum at FRONT_Z.
    box('TOP_HEADER',(0,Y_HEADER_BOTTOM+HEADER_H/2,FRONT_Z-10),(384,HEADER_H,18),housing,root,2)
    frame_z=FRONT_Z-FRAME_D/2
    box('FRAME_POST_L',(-X_POST,(Y_CHASSIS_TOP+Y_HEADER_BOTTOM)/2,frame_z),(FRAME_W,Y_HEADER_BOTTOM-Y_CHASSIS_TOP,FRAME_D),housing,root,1.2)
    box('FRAME_POST_R',(X_POST,(Y_CHASSIS_TOP+Y_HEADER_BOTTOM)/2,frame_z),(FRAME_W,Y_HEADER_BOTTOM-Y_CHASSIS_TOP,FRAME_D),housing,root,1.2)
    box('FRAME_RAIL_BOTTOM',(0,Y_CHASSIS_TOP,frame_z),(384,14,FRAME_D),housing,root,1.2)
    box('FRAME_RAIL_TOP',(0,Y_HEADER_BOTTOM,frame_z),(384,14,FRAME_D),housing,root,1.2)
    box('INTERNAL_BACKING',(0,(Y_CHASSIS_TOP+Y_HEADER_BOTTOM)/2,PLATE_Z_CENTER),(356,Y_HEADER_BOTTOM-Y_CHASSIS_TOP-10,PLATE_T),housing,root,1)
    # 4 mm glass and the four-sided EPDM gasket, all physically separate.
    box('FRONT_GLASS',(0,(GLASS_Y0+GLASS_Y1)/2,GLASS_Z),(GLASS_X,GLASS_Y1-GLASS_Y0,GLASS_T),housing,root,0.3)
    gasket_z=GLASS_Z-3.0
    box('GASKET_TOP',(0,GLASS_Y1,gasket_z),(GLASS_X+8,6,6),housing,root,1.5)
    box('GASKET_BOTTOM',(0,GLASS_Y0,gasket_z),(GLASS_X+8,6,6),housing,root,1.5)
    box('GASKET_L',(-GLASS_X/2, (GLASS_Y0+GLASS_Y1)/2,gasket_z),(6,GLASS_Y1-GLASS_Y0,6),housing,root,1.5)
    box('GASKET_R',(GLASS_X/2, (GLASS_Y0+GLASS_Y1)/2,gasket_z),(6,GLASS_Y1-GLASS_Y0,6),housing,root,1.5)
    # left hinge barrels and right quarter-turn latch; origins are at their
    # real axes even though animation is intentionally deferred.
    for i,y in enumerate((190,600)):
        cyl('HINGE_BARREL_%d'%i,(-202,y,111),4,30,housing,root,'Y',24,0.3)
        box('HINGE_LEAF_%d'%i,(-194,y,111),(16,28,2.5),housing,root,0.6)
        fastener('HINGE_SCREW_%d'%i,(-194,y-8,113),hardware_coll,root,'Z',3,5)
    cyl('QUARTER_TURN_LATCH',(194,400,110),8,5,housing,root,'Z',32,0.4)
    box('LATCH_STRIKE',(186,400,105),(18,30,3),housing,root,0.7)
    # fascia/header fasteners
    for i,x in enumerate((-170,170)):
        fastener('HEADER_FASTENER_%d'%i,(x,700,108),hardware_coll,root,'Z',4,6)
    for i,x in enumerate((-170,0,170)):
        fastener('BASE_FASTENER_%d'%i,(x,35,112),hardware_coll,root,'Z',4,6)
    for x in (-170,170):
        cyl('RUBBER_FOOT', (x,FOOT_H/2,-85), 11, FOOT_H, housing, root,'Y',32,1)

def _build_gates(x, z, coll, hardware_coll, root):
    """RF-C3: blade gates, actuators, interlock, solenoid, sensor, queued ball.

    Blade lies in the ball plane (z=BALL_Z) and enters from +x through slots in the
    tube and cradle walls. Ball rests on the blade top (queue datum = top + BALL_R).
    """
    specs = [('UPPER_RETAINER', GATE_UPPER_TOP, 'CLOSED retains the upper queued ball'),
             ('LOWER_RELEASE', GATE_LOWER_TOP, 'CLOSED retains the lower queued ball')]
    gcx = x + GATE_CLOSED_TIP_DX + GATE_LEN/2
    gy = {}
    for i, (label, top, role) in enumerate(specs):
        y = top - GATE_T/2; gy[label] = y
        gate = box('ESCAPEMENT_%s_GATE' % label, (gcx, y, z), (GATE_LEN, GATE_T, GATE_W), coll, root, 0.4)
        set_origin(gate, (gcx, y, z))
        gate['actuation_axis'] = 'X'
        gate['closed_tip_x_mm'] = x + GATE_CLOSED_TIP_DX
        gate['open_tip_x_mm'] = x + GATE_OPEN_TIP_DX
        gate['travel_mm'] = GATE_TRAVEL
        gate['hard_stops_mm'] = [x + GATE_CLOSED_TIP_DX, x + GATE_OPEN_TIP_DX]
        gate['gate_top_y_mm'] = top
        gate['queue_datum_y_mm'] = top + BALL_R
        gate['role'] = role
        pin = cyl('ESCAPEMENT_PIN_%d' % i, (x+32, y, z+12), 2.2, 30, coll, root, 'X', 20, 0.2)
        bush_l = cyl('ESCAPEMENT_BUSH_%s_L' % label, (x+19, y, z+12), 3.4, 5, coll, root, 'X', 24, 0.3)
        bush_r = cyl('ESCAPEMENT_BUSH_%s_R' % label, (x+45, y, z+12), 3.4, 5, coll, root, 'X', 24, 0.3)
        guide = box('ESCAPEMENT_GUIDE_%d' % i, (x+32, y, z+16.95), (30, 8, 3), coll, root, 0.4)
        bracket = box('ESCAPEMENT_ACTUATOR_BRACKET_%s' % label, (x+27, y, z), (8, 12, 16), coll, root, 0.8)
        spring = cyl('ESCAPEMENT_RETURN_SPRING_%s' % label, (x+38.5, y, z), 3.2, 17, coll, root, 'X', 20, 0.2)
        for obj in (gate, pin, bush_l, bush_r, guide, bracket, spring):
            obj['component_id'] = 'CC-220'
            obj['mechanism'] = label
        washer, screw = fastener('ESCAPEMENT_FASTENER_%d' % i, (x+32, y, z+18.95), hardware_coll, root, 'Z', 3, 5)
        washer['component_id'] = 'CC-220'; screw['component_id'] = 'CC-220'
    y_up, y_lo = gy['UPPER_RETAINER'], gy['LOWER_RELEASE']; y_mid = (y_up + y_lo)/2
    interlock = sweep_tube('ESCAPEMENT_INTERLOCK_LINK',
                           [(x+27, y_up-6.5, z+10.5), (x+31, y_mid, z+10.5), (x+27, y_lo+6.5, z+10.5)], 1.6, coll, root, 8)
    interlock['logic'] = 'upper retainer and lower release cannot be open together'
    interlock['clearance_state'] = 'one gate closed before the other opens'
    box('ESCAPEMENT_INTERLOCK_STOP', (x+27, y_mid, z), (6, 8, 8), coll, root, 0.8)
    cyl('ESCAPEMENT_SOLENOID', (x+63, y_mid, z), 8, 26, coll, root, 'X', 24, 0.7)
    sensor = cyl('ESCAPEMENT_SENSOR', (x-21, QUEUE_Y_UPPER, z+13), 4, 8, coll, root, 'Z', 20, 0.4)
    sensor['sensing_datum_mm'] = [x, QUEUE_Y_UPPER, z + 13]
    sensor['target'] = 'upper ball in holding chamber'
    box('ESCAPEMENT_SENSOR_BRACKET', (x-21, QUEUE_Y_UPPER, z+7), (10, 8, 5), coll, root, 0.8)
    box('ESCAPEMENT_SENSOR_DATUM', (x, QUEUE_Y_UPPER, z+13), (2, 2, 2), coll, root, 0)
    sensor['component_id'] = 'CC-220'
    # ball in the holding chamber is geometry, not a material cue.
    sphere('STEEL_BALL_INPUT', (x, QUEUE_Y_UPPER, z), BALL_R, coll, root)
    return gy


def make_input(root, coll, hardware_coll):
    x=-145; z=BALL_Z
    _gy=(GATE_UPPER_TOP-GATE_T/2, GATE_LOWER_TOP-GATE_T/2)
    # Hopper: truncated square frustum with an actual throat and mounting collar.
    # RF-C1: hollow funnel centred on the ball plane (z=BALL_Z), 2 mm walls,
    # bore >= BORE_D, bottom 1 mm into the throat, top 3 mm into the rim.
    HOP_WALL=2.0; RIM_DEPTH=36.0
    loft_rect_shell('HOPPER_UPPER',x,z,643,678,(31.0,29.0),(39.0,29.0),HOP_WALL,coll,root,0.4)
    # RF-C2: throat = hollow funnel ring, bore 22 mm (BORE_D), 2 mm wall, axis vertical.
    ring_y('HOPPER_THROAT',x,z,638,644,BORE_D/2+2.0,BORE_D/2,coll,root,32,0.3)
    # Phase 2 hopper details: a distinct rim, wall-return pieces, and a
    # replaceable throat collar make the formerly solid blockout serviceable.
    # Rim: 48 x 36 mm outer (RIM_DEPTH), wraps the 39 x 29 hopper top with 0.5 mm embed.
    rz=RIM_DEPTH/2-2.0
    box('HOPPER_RIM_FRONT',(x,678,z+rz),(48,6,4),coll,root,0.8)
    box('HOPPER_RIM_BACK',(x,678,z-rz),(48,6,4),coll,root,0.8)
    box('HOPPER_RIM_LEFT',(x-21.5,678,z),(5,6,2*rz),coll,root,0.8)
    box('HOPPER_RIM_RIGHT',(x+21.5,678,z),(5,6,2*rz),coll,root,0.8)
    ring_y('HOPPER_THROAT_COLLAR',x,z,640,643.5,15.0,BORE_D/2+1.75,coll,root,32,0.3)
    box('ESCAPEMENT_BACKING',(x,620,z+12),(42,72,4),coll,root,1)
    # RF-C2: holding tube = front U-channel (open to the track floor), bore 26.5 wide x 22 tall.
    zf=BALL_Z-BALL_R; XI=13.25; XO=15.25; WEB=2.0
    tube_pts=[(-XO,zf),(-XI,zf),(-XI,zf+BORE_D),(XI,zf+BORE_D),(XI,zf),(XO,zf),(XO,zf+BORE_D+WEB),(-XO,zf+BORE_D+WEB)]
    tube_pts=[(x+px,pz) for px,pz in tube_pts]
    chamber=extrude_y('ESCAPEMENT_TUBE',tube_pts,594,639,coll,root,0.0)
    cut_boxes(chamber,[((x+14.25,g,z),(6.0,GATE_T+2*GATE_SLOT_CLEAR,GATE_W+2*GATE_SLOT_CLEAR)) for g in _gy])
    bevel(chamber,0.4,2)
    chamber['capacity_balls'] = 2
    chamber['ball_queue_spacing_mm'] = QUEUE_SPACING
    chamber['centerline_datum_mm'] = [x, 638, z]
    chamber['role'] = 'two-ball holding chamber'
    # Non-invasive queue datum marks show the two ball centers without adding
    # extra balls to the production assembly.
    for i, y in enumerate((QUEUE_Y_UPPER, QUEUE_Y_LOWER)):
        marker=torus = cyl('HOLDING_QUEUE_DATUM_%02d' % i,(x,y,z-12),5.5,1.0,coll,root,'Z',24,0.15)
        marker['queue_index'] = i + 1
    # A short launch cradle closes the physical gap between the holding
    # chamber and the first track point.
    launch = path_line((x,638,TRACK_Z),(x,602,TRACK_Z),8)
    launch += path_line((x,602,TRACK_Z),(x+15,590,TRACK_Z),5)[1:]
    create_track_channel('INPUT_LAUNCH_CRADLE',launch,coll,root,TRACK_W,TRACK_T,TRACK_WALL,TRACK_T,cap_start=True,cap_end=False)
    cut_boxes(bpy.data.objects['INPUT_LAUNCH_CRADLE_WALL_L'],[((x+12.25,g,z),(4.0,GATE_T+2*GATE_SLOT_CLEAR,GATE_W+2*GATE_SLOT_CLEAR)) for g in _gy],'FLOAT')
    # RF-C2: bridge = rear U-clamp behind the cradle floor, straps lap the tube sides 2.5 mm.
    zb=TRACK_Z-TRACK_T/2-2.0
    br_pts=[(-XO,zb),(XO,zb),(XO,zf+2.5),(XI,zf+2.5),(XI,TRACK_Z-TRACK_T/2+0.5),(-XI,TRACK_Z-TRACK_T/2+0.5),(-XI,zf+2.5),(-XO,zf+2.5)]
    br_pts=[(x+px,pz) for px,pz in br_pts]
    extrude_y('HOLDING_TO_CRADLE_BRIDGE',br_pts,594,639,coll,root,0.4)
    _build_gates(x, z, coll, hardware_coll, root)

def make_selector(root, coll, hardware_coll):
    px,py,pz=PIVOT
    # The mechanism plate is the structural datum.  The selector's actuator
    # hardware lives behind it; only the pivot/hub and gate project into the
    # ball plane through the plate opening.
    box('SELECTOR_BACKPLATE',(px,py+12,PLATE_Z_CENTER),(130,78,PLATE_T),coll,root,1.5)
    cyl('PIVOT_SHAFT',(px,py,pz),2,20,coll,root,'Z',24,0.2)
    # Compact upright selector blade: 26 mm wide x 18 mm high, 2 mm deep,
    # centered on the pivot and ball plane. The previous diamond was a flat
    # placeholder that could not present a contact face to the ball.
    plate=prism('DIVERTER_GATE',[(-13,-9),(13,-9),(13,9),(-13,9)],2,coll,root,0.8)
    plate.location.z=pz*MM; plate.location.y=py*MM
    plate['states'] = 'LEFT/YES, RIGHT/NO'
    plate['state_angles_deg'] = (-11.0, 11.0)
    plate['hard_stop_angles_deg'] = (-11.0, 11.0)
    plate['blade_width_mm'] = 26.0
    plate['blade_height_mm'] = 18.0
    plate['blade_thickness_mm'] = 2.0
    plate['pivot_datum_mm'] = [px, py, pz]
    plate['interlock'] = 'single pivot gate; one branch open at a time'
    cyl('DIVERTER_HUB',(px,py,pz),8,8,coll,root,'Z',32,0.6)
    # One physical stop per side. Their upper faces meet the blade's lower
    # corners at the declared +/-11 degree travel limits.
    box('DIVERTER_STOP_L',(-16,py-12,pz),(6,6,10),coll,root,0.8)
    box('DIVERTER_STOP_R',(16,py-12,pz),(6,6,10),coll,root,0.8)
    # RF-E5: the full actuator stack stays behind the mechanism plate and
    # inside the 62 mm-wide rear service-hatch window.  The output shaft is
    # deliberately long enough to cross the 4 mm plate rather than merely
    # touch its rear face.
    servo_x = 12.0
    servo = box('SELECTOR_SERVO',(servo_x,py-16,35),(36,30,26),coll,root,2)
    servo['service_hatch_x_extent_mm'] = [-31.0, 31.0]
    servo['mounted_behind_plate'] = True
    shaft = cyl('SERVO_OUTPUT_SHAFT',(servo_x,py-16,47),3,16,coll,root,'Z',20,0.3)
    shaft['passes_through_mechanism_plate'] = True
    linkage = sweep_tube('SELECTOR_LINKAGE',[(servo_x,py-16,47),(8,py-8,45),(0,py,44)],2,coll,root,8)
    linkage['mounted_behind_plate'] = True
    spring = cyl('SELECTOR_RETURN_SPRING',(px,py-25,42),6,18,coll,root,'Y',20,0.5)
    spring['mounted_behind_plate'] = True
    for x in (-24,24):
        sensor = box('SELECTOR_LIMIT_SENSOR', (x,py+10,40),(12,8,18),coll,root,1)
        sensor['service_hatch_x_extent_mm'] = [-31.0, 31.0]
        sensor['mounted_behind_plate'] = True
        fastener('SELECTOR_SENSOR_SCREW',(x,py+10,47),hardware_coll,root,'Z',3,5)
    # Physically separate, non-crossing branch channels from the gate to each
    # output pocket.  The shared entry stops at the pivot; branches diverge
    # immediately after it and remain on opposite sides of the divider.
    create_track_channel('SELECTOR_DROP', selector_drop_path(), coll, root, TRACK_W, TRACK_T, TRACK_WALL, TRACK_T, cap_start=False, cap_end=False)
    for label, branch in selector_branch_paths().items():
        create_track_channel(label+'_BRANCH',branch,coll,root,TRACK_W,TRACK_T,TRACK_WALL,TRACK_T,cap_start=False,cap_end=True)
        # The branch channel is now the inclined guide. The old solid
        # 42 x 100 mm guide blocks overlapped the branch walls and pocket.

def make_pocket(label, x, root, coll, hardware_coll):
    y0,y1=POCKET_Y0,POCKET_Y1
    pocket_depth=35.0; pocket_center_z=75.0
    box(label+'_POCKET_SIDE_L',(x-31,(y0+y1)/2,pocket_center_z),(5,y1-y0,pocket_depth),coll,root,1)
    box(label+'_POCKET_SIDE_R',(x+31,(y0+y1)/2,pocket_center_z),(5,y1-y0,pocket_depth),coll,root,1)
    top = box(label+'_POCKET_TOP',(x,y1,pocket_center_z),(67,5,pocket_depth),coll,root,0)
    cut_boxes(top,[((x,y1,pocket_center_z),(26,8,pocket_depth+4))],'FLOAT')
    bevel(top,1,3)
    top['entry_slot_width_mm'] = 26.0
    box(label+'_POCKET_BACK',(x,(y0+y1)/2,58),(67,y1-y0,5),coll,root,1)
    box(label+'_POCKET_FLOOR',(x,y0,75),(67,5,pocket_depth),coll,root,1)
    # RF-F2: author the stop as an actual inclined solid rather than rotate a
    # world-origin box.  The forward (+Y) face catches the descending ball;
    # the 18 degree rake guides it down onto a rubber-faced stop.
    catch_angle = math.radians(18.0)
    catch_bottom_y = y0 + 14.0
    catch_bottom_z = BALL_Z - 9.0
    catch_h = 18.0
    catch_t = 4.0
    catch_top_y = catch_bottom_y + math.tan(catch_angle) * catch_h
    catch_pts = [
        (x - 22.0, catch_bottom_y, catch_bottom_z),
        (x - 22.0, catch_top_y, catch_bottom_z + catch_h),
        (x - 22.0, catch_top_y - catch_t, catch_bottom_z + catch_h),
        (x - 22.0, catch_bottom_y - catch_t, catch_bottom_z),
        (x + 22.0, catch_bottom_y, catch_bottom_z),
        (x + 22.0, catch_top_y, catch_bottom_z + catch_h),
        (x + 22.0, catch_top_y - catch_t, catch_bottom_z + catch_h),
        (x + 22.0, catch_bottom_y - catch_t, catch_bottom_z),
    ]
    catch = mesh_object(label+'_CATCH_PLATE', catch_pts,
                        [(0,3,2,1), (4,5,6,7), (0,1,5,4), (1,2,6,5),
                         (2,3,7,6), (3,0,4,7)], coll, root)
    bevel(catch, 1.0, 2)
    rest_y = catch_bottom_y + math.tan(catch_angle) * BALL_R + BALL_R
    catch['surface_role'] = 'inclined ball rest'
    catch['rake_angle_deg'] = 18.0
    catch['rest_datum_mm'] = [x, rest_y, BALL_Z]
    # Thin rubber follows the catch face and remains outside the resting ball
    # volume except at the intended contact patch.
    pad_z0, pad_h, pad_t = BALL_Z - 5.5, 11.0, 2.0
    pad_y0 = catch_bottom_y + math.tan(catch_angle) * (pad_z0 - catch_bottom_z)
    pad_y1 = pad_y0 + math.tan(catch_angle) * pad_h
    pad_pts = [
        (x - 21.0, pad_y0 + pad_t, pad_z0), (x - 21.0, pad_y1 + pad_t, pad_z0 + pad_h),
        (x - 21.0, pad_y1, pad_z0 + pad_h), (x - 21.0, pad_y0, pad_z0),
        (x + 21.0, pad_y0 + pad_t, pad_z0), (x + 21.0, pad_y1 + pad_t, pad_z0 + pad_h),
        (x + 21.0, pad_y1, pad_z0 + pad_h), (x + 21.0, pad_y0, pad_z0),
    ]
    pad = mesh_object(label+'_RUBBER_IMPACT_PAD', pad_pts,
                      [(0,3,2,1), (4,5,6,7), (0,1,5,4), (1,2,6,5),
                       (2,3,7,6), (3,0,4,7)], coll, root)
    bevel(pad, 0.6, 2)
    pad['surface_role'] = 'rubber-faced stop'
    pad['rest_datum_mm'] = [x, rest_y, BALL_Z]
    box(label+'_INSPECTION_WINDOW',(x,(y0+y1)/2,90),(50,52,3),coll,root,0.4)
    # Opposed optical sensor bodies straddle the declared rest datum.  The
    # datum tube is deliberate non-physical inspection geometry for V-04.
    sensor = box(label+'_SENSOR',(x-29.0,rest_y,BALL_Z),(6,8,8),coll,root,1)
    sensor['beam_datum_mm'] = [x, rest_y, BALL_Z]
    receiver = box(label+'_SENSOR_RECEIVER',(x+29.0,rest_y,BALL_Z),(6,8,8),coll,root,1)
    receiver['beam_datum_mm'] = [x, rest_y, BALL_Z]
    beam = cyl(label+'_SENSOR_BEAM_DATUM',(x,rest_y,BALL_Z),0.6,52.0,coll,root,'X',16,0.0)
    beam['inspection_role'] = 'optical beam through ball rest datum'
    beam['rest_datum_mm'] = [x, rest_y, BALL_Z]
    cyl(label+'_INDICATOR',(x-22,y1-13,90),5,5,coll,root,'Z',24,0.5)
    # Keep the hardware behind the glass inner face. The old FRONT_Z-10
    # placement was a front-surface placeholder and failed the clearance test.
    for dx in (-27,27): fastener(label+'_POCKET_FASTENER',(x+dx,y0+5,90),hardware_coll,root,'Z',3,5)
    cu=bpy.data.curves.new(label+'_LABEL','FONT'); cu.body=label; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.size=16*MM; cu.extrude=.45*MM
    text=bpy.data.objects.new(label+'_LABEL',cu); coll.objects.link(text); text.location=(x*MM,(y1-13)*MM,94*MM); parent(text,root)

def make_outputs(root, coll, hardware_coll):
    make_pocket('YES',OUT_X[0],root,coll,hardware_coll)
    make_pocket('NO',OUT_X[1],root,coll,hardware_coll)
    box('OUTPUT_DIVIDER',(0,195,70),(8,100,50),coll,root,1)

def make_rear(root, coll, hardware_coll):
    box('REAR_SERVICE_COVER',(0,390,-118),(360,500,3),coll,root,1)
    for i,x in enumerate((-160,160)):
        for j,y in enumerate((180,390,600)):
            fastener('REAR_FASTENER_%d_%d'%(i,j),(x,y,-116),hardware_coll,root,'Z',4,6)
    for i in range(8): box('VENT_SLOT_%02d'%i,(-60+i*18,54,-116),(10,3,4),coll,root,1)
    box('POWER_INLET',(125,70,-114),(32,22,12),coll,root,2)
    box('MAIN_SWITCH',(165,115,-114),(22,12,16),coll,root,1)
    box('SELECTOR_SERVICE_HATCH',(0,300,-114),(62,48,6),coll,root,1)

def make_electronics(root, coll):
    box('ELECTRONICS_TRAY',(0,80,45),(300,55,3),coll,root,1)
    # RF-G1: electronics sit on the rear side of the tray, retained by real
    # standoffs.  Their footprints are entirely within the 300 x 55 mm tray.
    for name, center, size, offsets in (
        ('CONTROL_BOARD', (-70,80,37), (92,40,8), ((-40,-15), (40,-15), (-40,15), (40,15))),
        ('MOTOR_DRIVER', (50,80,35), (54,40,12), ((-22,-15), (22,-15), (-22,15), (22,15))),
        ('POWER_SUPPLY', (120,74,32), (60,32,18), ((-24,-11), (24,-11), (-24,11), (24,11))),
    ):
        board = box(name, center, size, coll, root, 1)
        for index, (dx, dy) in enumerate(offsets):
            standoff = cyl('%s_STANDOFF_%02d' % (name, index), (center[0]+dx, center[1]+dy,42.25), 2.0, 3.0, coll, root, 'Z', 16, 0.2)
            standoff['mounts'] = name
            standoff['mounting_role'] = 'tray standoff'
    # RF-F5: harnesses are routed behind the mechanism plate (local z <
    # PLATE_Z_BACK) instead of through the output pockets and branch walls.
    wiring_route = [(-108,88,40),(-90,120,40),(-45,145,40),(-35,285,40)]
    sensor_route = [(60,88,40),(60,140,40),(52,260,40),(42,285,40)]
    wiring = sweep_tube('WIRING_HARNESS',wiring_route,2,coll,root,8)
    sensor = sweep_tube('SENSOR_HARNESS',sensor_route,1.5,coll,root,8)
    wiring['route_role'] = 'behind mechanism plate'
    sensor['route_role'] = 'behind mechanism plate'
    for name, points in (('WIRING_HARNESS', wiring_route), ('SENSOR_HARNESS', sensor_route)):
        for index, point in enumerate(points):
            clip = box('%s_CLIP_%02d' % (name, index), point, (8,8,2), coll, root, 0.6)
            clip['retains'] = name
            clip['mounted_behind_plate'] = True

def add_nameplate(root, coll):
    # Text is intentionally plain geometry; material/engraving depth is a later pass.
    cu=bpy.data.curves.new('CHAOS_CHAMBER_NAMEPLATE_TEXT','FONT'); cu.body='CHAOS CHAMBER'; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.size=18*MM; cu.extrude=0.4*MM
    ob=bpy.data.objects.new('CHAOS_CHAMBER_NAMEPLATE_TEXT',cu); coll.objects.link(ob); ob.location=(0*MM,704*MM,(FRONT_Z-1)*MM); parent(ob,root)


def _input(node, *names):
    for name in names:
        if name in node.inputs:
            return node.inputs[name]
    return None


def principled_material(name, base, roughness=0.45, metallic=0.0):
    mat=bpy.data.materials.new(name)
    mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF')
    _input(bsdf,'Base Color').default_value=(*base,1)
    _input(bsdf,'Roughness').default_value=roughness
    _input(bsdf,'Metallic').default_value=metallic
    return mat


def textured_materials():
    """Create restrained procedural materials; no external image assets needed."""
    mats={}
    mats['CHARCOAL']=principled_material('MAT_CHARCOAL',(0.018,0.022,0.028),0.34,0.15)
    mats['RUBBER']=principled_material('MAT_EPDM_RUBBER',(0.008,0.009,0.010),0.78,0.0)
    mats['STEEL']=principled_material('MAT_POLISHED_STEEL',(0.52,0.56,0.60),0.16,0.92)
    mats['METAL']=principled_material('MAT_BRUSHED_STAINLESS',(0.34,0.38,0.42),0.28,0.88)
    mats['AMBER']=principled_material('MAT_AMBER_INDICATOR',(0.32,0.055,0.006),0.22,0.05)
    amber_bsdf=mats['AMBER'].node_tree.nodes.get('Principled BSDF')
    emission=_input(amber_bsdf,'Emission Color','Emission')
    if emission: emission.default_value=(1.0,0.08,0.005,1)
    estrength=_input(amber_bsdf,'Emission Strength')
    if estrength: estrength.default_value=2.0

    walnut=bpy.data.materials.new('MAT_WALNUT_PROCEDURAL'); walnut.use_nodes=True
    nt=walnut.node_tree; bs=nt.nodes.get('Principled BSDF')
    tex=nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=3.2; tex.inputs['Detail'].default_value=5.0; tex.inputs['Roughness'].default_value=.7
    wave=nt.nodes.new('ShaderNodeTexWave'); wave.wave_type='BANDS'; wave.bands_direction='X'; wave.inputs['Scale'].default_value=7.0; wave.inputs['Distortion'].default_value=6.0; wave.inputs['Detail'].default_value=5.0
    mix=nt.nodes.new('ShaderNodeMixRGB'); mix.blend_type='MULTIPLY'; mix.inputs[0].default_value=.65
    ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color=(.012,.003,.001,1); ramp.color_ramp.elements[1].color=(.20,.055,.018,1)
    nt.links.new(tex.outputs['Fac'],ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'],mix.inputs[1]); nt.links.new(wave.outputs['Color'],mix.inputs[2]); nt.links.new(mix.outputs[0],bs.inputs['Base Color'])
    _input(bs,'Roughness').default_value=.34
    mats['WALNUT']=walnut

    brushed=bpy.data.materials.new('MAT_BRUSHED_METAL_PROCEDURAL'); brushed.use_nodes=True
    nt=brushed.node_tree; bs=nt.nodes.get('Principled BSDF')
    noise=nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=85; noise.inputs['Detail'].default_value=2.0; noise.inputs['Roughness'].default_value=.35
    ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color=(.18,.20,.22,1); ramp.color_ramp.elements[1].color=(.72,.76,.80,1)
    nt.links.new(noise.outputs['Fac'],ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color']); _input(bs,'Metallic').default_value=.9; _input(bs,'Roughness').default_value=.27
    mats['BRUSHED']=brushed

    glass=principled_material('MAT_LOW_IRON_GLASS',(0.92,0.97,1.0),0.08,0.0)
    bs=glass.node_tree.nodes.get('Principled BSDF'); tr=_input(bs,'Transmission Weight','Transmission')
    if tr: tr.default_value=1.0
    _input(bs,'IOR').default_value=1.45
    mats['GLASS']=glass
    return mats


def assign_material(obj, mat):
    if hasattr(obj.data,'materials') and obj.data.materials:
        obj.data.materials[0]=mat
    elif hasattr(obj.data,'materials'):
        obj.data.materials.append(mat)


def apply_materials(mats):
    for obj in bpy.context.scene.objects:
        n=obj.name.upper()
        if n.startswith('WALNUT_') or n.startswith('BASE_SIDE_'):
            mat=mats['WALNUT']
        elif 'GLASS' in n or 'WINDOW' in n:
            mat=mats['GLASS']
        elif 'GASKET' in n or 'RUBBER' in n or 'FOOT' in n:
            mat=mats['RUBBER']
        elif 'BALL' in n:
            mat=mats['STEEL']
        elif 'INDICATOR' in n:
            mat=mats['AMBER']
        elif 'CHARCOAL' in n or 'ELECTRONICS' in n or 'BOARD' in n or 'DRIVER' in n or 'SUPPLY' in n:
            mat=mats['CHARCOAL']
        elif n.startswith('CHAOS_CHAMBER_NAMEPLATE_TEXT'):
            mat=mats['BRUSHED']
        elif n.startswith('REAR_') or n.startswith('VENT_') or n.startswith('POWER_') or n.startswith('MAIN_SWITCH'):
            mat=mats['METAL']
        elif n.startswith('RUBBER_'):
            mat=mats['RUBBER']
        elif n.startswith('HW_') or 'FASTENER' in n or 'SCREW' in n or 'WASHER' in n:
            mat=mats['STEEL']
        else:
            mat=mats['BRUSHED']
        assign_material(obj,mat)


def look_at(obj, target):
    direction=Vector(target)*MM-obj.location
    obj.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()


def basic_scene(mats):
    scene=bpy.context.scene
    engines={item.identifier for item in scene.render.bl_rna.properties['engine'].enum_items}
    try:
        scene.render.engine='BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in engines else 'BLENDER_EEVEE'
    except TypeError:
        scene.render.engine='BLENDER_EEVEE'
    scene.render.resolution_x=700; scene.render.resolution_y=900; scene.render.resolution_percentage=100
    scene.render.film_transparent=False
    scene.world.color=(0.018,0.022,0.03)
    scene.world.use_nodes=True
    bg=scene.world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(0.012,0.016,0.024,1); bg.inputs['Strength'].default_value=.28
    env=collection('ENVIRONMENT')
    table=box('ENV_TABLE',(0,-8,0),(1500,16,1100),env,None,3); assign_material(table,mats['WALNUT'])
    wall=box('ENV_BACK_WALL',(0,430,-245),(1500,900,20),env,None,2); assign_material(wall,mats['CHARCOAL'])
    # Camera is in front (+Z), slightly elevated and left for a product-style view.
    data=bpy.data.cameras.new('CC01_HERO_CAMERA'); cam=bpy.data.objects.new('CC01_HERO_CAMERA',data); scene.collection.objects.link(cam)
    cam.location=(520*MM,390*MM,940*MM); data.lens=58; look_at(cam,(0,365,0)); scene.camera=cam
    def area(name, loc, energy, size, color):
        ld=bpy.data.lights.new(name,'AREA'); ld.energy=energy; ld.shape='DISK'; ld.size=size; ld.color=color
        ob=bpy.data.objects.new(name,ld); scene.collection.objects.link(ob); ob.location=Vector(loc)*MM; look_at(ob,(0,380,0)); return ob
    area('KEY_SOFTBOX',(430,580,520),900,420,(1.0,.78,.60))
    area('FILL_SOFTBOX',(-470,430,360),650,500,(.55,.70,1.0))
    area('RIM_SOFTBOX',(0,620,-360),800,320,(.75,.85,1.0))

def build():
    clear()
    scene=bpy.context.scene
    scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1.0; scene.unit_settings.length_unit='MILLIMETERS'
    root=bpy.data.objects.new('CHAOS_CHAMBER_ROOT',None); bpy.context.scene.collection.objects.link(root)
    housing=collection('HOUSING'); track=collection('TRACK_ASSEMBLY'); ball=collection('BALL_ASSEMBLY'); inp=collection('INPUT_ASSEMBLY'); selector=collection('RANDOM_SELECTOR'); output=collection('OUTPUT_ASSEMBLY'); rear=collection('REAR_CONSTRUCTION'); elec=collection('ELECTRONICS'); hardware=collection('FASTENERS')
    make_housing(root,housing,hardware)
    glass=bpy.data.objects.get('FRONT_GLASS')
    if glass is not None and not SHOW_FRONT_GLASS:
        glass.hide_viewport=True
        glass.hide_render=True
    make_track(root,track,ball)
    make_input(root,inp,hardware)
    make_selector(root,selector,hardware)
    make_outputs(root,output,hardware)
    make_rear(root,rear,hardware)
    make_electronics(root,elec)
    add_nameplate(root,housing)
    root['assembly_revision'] = ASSEMBLY_REVISION
    root['authored_units'] = AUTHORED_UNITS
    root['coordinate_convention'] = 'Z-up / front -Y / X left-right'
    root['datum_table'] = {key: list(value) if isinstance(value, tuple) else value for key, value in DATUMS_MM.items()}
    root['dimension_tolerance_table_mm'] = dict(DIMENSION_TOLERANCES_MM)
    for collection_name, component_id in {
        'HOUSING': 'CC-100', 'INPUT_ASSEMBLY': 'CC-210',
        'RANDOM_SELECTOR': 'CC-420', 'OUTPUT_ASSEMBLY': 'CC-530',
        'REAR_CONSTRUCTION': 'CC-610', 'ELECTRONICS': 'CC-620',
        'FASTENERS': 'CC-700', 'BALL_ASSEMBLY': 'CC-340',
    }.items():
        assembly_collection = bpy.data.collections.get(collection_name)
        if assembly_collection is not None:
            assembly_collection['component_id'] = component_id
            assembly_collection['assembly_revision'] = ASSEMBLY_REVISION
            assembly_collection['authored_units'] = AUTHORED_UNITS
    component_ids = {
        'HOPPER_': 'CC-210', 'ESCAPEMENT_': 'CC-220',
        'DIVERTER_': 'CC-420', 'SELECTOR_': 'CC-420', 'PIVOT_': 'CC-420',
        'YES_': 'CC-530', 'NO_': 'CC-530', 'OUTPUT_': 'CC-530',
        'REAR_': 'CC-610', 'VENT_': 'CC-610', 'POWER_': 'CC-610', 'MAIN_SWITCH': 'CC-610',
    }
    for obj in bpy.context.scene.objects:
        for prefix, component_id in component_ids.items():
            if obj.name.upper().startswith(prefix):
                tag_component(obj, component_id, prefix.rstrip('_'))
                break
        if obj.get('component_id') is None:
            collection_ids = {
                collection.name: collection.get('component_id')
                for collection in obj.users_collection
                if collection.get('component_id')
            }
            if collection_ids:
                component_id = next(iter(collection_ids.values()))
                tag_component(obj, component_id, 'ASSEMBLY')
    # The assembly modules are authored in a convenient front-elevation frame
    # (Y-up, Z-depth). Map that frame into Blender's production world: Z-up,
    # Y-depth, front toward -Y. Rotation +90° about X gives (x,y,z)->(x,-z,y).
    root.rotation_euler[0]=math.radians(90.0)
    root['coordinate_system']='Z-up / front -Y / X left-right'
    mats=create_materials()
    assign_by_role(mats, bpy.context.scene.objects)
    create_basic_scene(mats)
    set_solid_viewport()
    bpy.context.view_layer.update()
    # Keep a clean front-oriented viewport for immediate inspection.
    for obj in bpy.context.selected_objects: obj.select_set(False)
    root.select_set(True); bpy.context.view_layer.objects.active=root
    print('CC-01 geometry build complete:', len(bpy.data.objects), 'objects')

if __name__ == '__main__': build()
