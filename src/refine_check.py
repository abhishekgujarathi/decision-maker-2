"""Refinement checks (V-01, V-02, V-05, V-06) for the CC-01 Blender scene.

Read-only. Run inside Blender:
    import importlib, src.refine_check as rc; importlib.reload(rc); rc.run()
Writes outputs/validation/refine_check.json and returns a summary dict.
"""
from __future__ import annotations

import itertools
import json
import os
import re

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

MM = 0.001
FASTENER_RE = re.compile(r'(FASTENER|_SCREW|_WASHER|SENSOR_DATUM|QUEUE_DATUM)')
SKIP_RE = re.compile(r'^(ENV_|BALL_CENTRE_PATH|CC01_)')
BALL_RE = re.compile(r'^STEEL_BALL')

# Planned contacts. Pairs are matched in either order. Edit as design firms up.
PAIR_RULES = [
    (r'^TRACK_(RUN|UTURN)_\d+_', r'^TRACK_(RUN|UTURN)_\d+_'),
    (r'^TRACK_(RUN|UTURN)_\d+_', r'^TRACK_EXIT_GUIDE_'),
    (r'^TRACK_EXIT_GUIDE_', r'^TRACK_EXIT_GUIDE_'),
    (r'^(YES|NO)_BRANCH_', r'^(YES|NO)_BRANCH_'),
    (r'^TRACK_(UTURN_)?SUPPORT_\d+', r'^TRACK_(UTURN_)?STANDOFF_\d+'),
    (r'^ESCAPEMENT_PIN_', r'^ESCAPEMENT_BUSH_'),
    (r'^HOPPER_RIM_', r'^HOPPER_(RIM_|UPPER)'),
    (r'^HOPPER_UPPER', r'^HOPPER_THROAT'),
    (r'^ESCAPEMENT_(UPPER_RETAINER|LOWER_RELEASE)_GATE$', r'^(ESCAPEMENT_ACTUATOR_BRACKET_|ESCAPEMENT_TUBE$|INPUT_LAUNCH_CRADLE_WALL_L$)'),
    (r'^ESCAPEMENT_RETURN_SPRING_', r'^ESCAPEMENT_ACTUATOR_BRACKET_'),
    (r'^ESCAPEMENT_TUBE', r'^HOLDING_TO_CRADLE_BRIDGE'),
    (r'^HOPPER_THROAT', r'^HOPPER_THROAT_COLLAR'),
    (r'^HOPPER_THROAT$', r'^(ESCAPEMENT_TUBE|HOLDING_TO_CRADLE_BRIDGE)$'),
    (r'^(YES|NO)_POCKET_', r'^(YES|NO)_POCKET_'),
    (r'^(YES|NO)_(CATCH_PLATE|RUBBER_IMPACT_PAD)', r'^(YES|NO)_(CATCH_PLATE|RUBBER_IMPACT_PAD)'),
    (r'^(FRAME_|TOP_HEADER|BASE_FRONT_FASCIA)', r'^(FRAME_|TOP_HEADER|BASE_FRONT_FASCIA|WALNUT_)'),
    (r'^GASKET_', r'^GASKET_'),
    (r'^HINGE_BARREL_(\d)', r'^HINGE_LEAF_(\d)'),
    (r'^MECH_PLATE', r'^(TRACK_|MECH_|SELECTOR_|ESCAPEMENT_)'),
    (r'^(WIRING|SENSOR)_HARNESS$', r'^(WIRING|SENSOR)_HARNESS_CLIP_'),
    (r'^ELECTRONICS_TRAY$', r'^(CONTROL_BOARD|MOTOR_DRIVER|POWER_SUPPLY)_STANDOFF_'),
    (r'^(CONTROL_BOARD|MOTOR_DRIVER|POWER_SUPPLY)$', r'^(CONTROL_BOARD|MOTOR_DRIVER|POWER_SUPPLY)_STANDOFF_'),
    (r'^(CONTROL_BOARD|MOTOR_DRIVER)$', r'^(WIRING|SENSOR)_HARNESS(_CLIP_00)?$'),
]
_COMPILED = [(re.compile(a), re.compile(b)) for a, b in PAIR_RULES]


def _label(name):
    m = re.match(r'^(YES|NO)_', name)
    return m.group(1) if m else None


def allowed(a, b):
    for ra, rb in _COMPILED:
        if (ra.search(a) and rb.search(b)) or (ra.search(b) and rb.search(a)):
            if ra.pattern.startswith('^(YES|NO)') and rb.pattern.startswith('^(YES|NO)'):
                return _label(a) == _label(b)
            return True
    return False


def _solid_objects():
    out = []
    for o in bpy.context.scene.objects:
        if o.type != 'MESH' or SKIP_RE.search(o.name):
            continue
        out.append(o)
    return out


def _bvh(obj, dg):
    ev = obj.evaluated_get(dg)
    me = ev.to_mesh()
    verts = [ev.matrix_world @ v.co for v in me.vertices]
    polys = [tuple(p.vertices) for p in me.polygons]
    ev.to_mesh_clear()
    if not polys:
        return None
    lo = Vector((min(v.x for v in verts), min(v.y for v in verts), min(v.z for v in verts)))
    hi = Vector((max(v.x for v in verts), max(v.y for v in verts), max(v.z for v in verts)))
    return BVHTree.FromPolygons(verts, polys, epsilon=0.0), lo, hi


def _build_all():
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    data = {}
    for o in _solid_objects():
        r = _bvh(o, dg)
        if r:
            data[o.name] = r
    return data


def v02_intersections(data):
    names = [n for n in data if not FASTENER_RE.search(n) and not BALL_RE.search(n)]
    bad, ok = [], 0
    for a, b in itertools.combinations(names, 2):
        A, B = data[a], data[b]
        if any(A[1][i] > B[2][i] or B[1][i] > A[2][i] for i in range(3)):
            continue
        if not A[0].overlap(B[0]):
            continue
        if allowed(a, b):
            ok += 1
        else:
            bad.append([a, b])
    return {'unintended': bad, 'allowed_count': ok}


def _ring_centres(obj, ring=8):
    vs = [obj.matrix_world @ v.co for v in obj.data.vertices]
    return [sum(vs[i:i + ring], Vector()) / ring for i in range(0, len(vs) - ring + 1, ring)]


def v01_ball_sweep(data):
    """Distance from each path sample (ball centre) to all non-ball solids minus ball radius."""
    path = bpy.data.objects.get('BALL_CENTRE_PATH')
    if path is None:
        return {'error': 'no BALL_CENTRE_PATH'}
    keep = [n for n in data if not FASTENER_RE.search(n) and not BALL_RE.search(n)
            and not n.startswith(('FRAME_', 'WALNUT_', 'BASE_', 'TOP_HEADER', 'GASKET', 'HINGE', 'INTERNAL_BACKING',
                                  'MECH_PLATE', 'RUBBER_FOOT', 'FRONT_GLASS', 'REAR_', 'ELECTRONICS', 'LATCH', 'QUARTER'))]
    verts, polys = [], []
    for n in keep:
        o = bpy.data.objects[n]
        dg = bpy.context.evaluated_depsgraph_get()
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        base = len(verts)
        verts += [ev.matrix_world @ v.co for v in me.vertices]
        polys += [tuple(base + i for i in p.vertices) for p in me.polygons]
        ev.to_mesh_clear()
    tree = BVHTree.FromPolygons(verts, polys)
    # ball radius from first ball object
    ball = next((bpy.data.objects[n] for n in bpy.data.objects.keys() if BALL_RE.search(n)), None)
    radius = (ball.dimensions.x / 2.0) if ball else 0.009
    bad, worst, n = [], 1e9, 0
    for i, c in enumerate(_ring_centres(path)):
        loc, nrm, idx, dist = tree.find_nearest(c)
        clr = (dist - radius) / MM
        n += 1
        worst = min(worst, clr)
        if clr < -0.05:
            bad.append([i, [round(v / MM, 1) for v in c], round(clr, 2)])
    return {'samples': n, 'interfering': len(bad), 'min_clearance_mm': round(worst, 3), 'worst': sorted(bad, key=lambda r: r[2])[:12]}


def v05_floating(data, gap_mm=0.5):
    """Connected components over contact (gap <= gap_mm). Component not holding the housing is floating."""
    names = [n for n in data if not FASTENER_RE.search(n) and not BALL_RE.search(n)
             and n not in ('FRONT_GLASS',) and not n.startswith('HOLDING_QUEUE')]
    parent = {n: n for n in names}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    pad = gap_mm * MM
    for a, b in itertools.combinations(names, 2):
        A, B = data[a], data[b]
        if any(A[1][i] - pad > B[2][i] or B[1][i] - pad > A[2][i] for i in range(3)):
            continue
        touch = bool(A[0].overlap(B[0]))
        if not touch:
            # nearest-vertex probe both ways
            o1, o2 = bpy.data.objects[a], bpy.data.objects[b]
            for oa, tb in ((o1, B[0]), (o2, A[0])):
                for v in oa.data.vertices:
                    loc, nrm, idx, d = tb.find_nearest(oa.matrix_world @ v.co, pad)
                    if loc is not None:
                        touch = True
                        break
                if touch:
                    break
        if touch:
            parent[find(a)] = find(b)
    comps = {}
    for n in names:
        comps.setdefault(find(n), []).append(n)
    host = find('WALNUT_LEFT') if 'WALNUT_LEFT' in parent else None
    float_comps = [sorted(v) for k, v in comps.items() if k != host]
    return {'components': len(comps), 'floating': float_comps}


def v06_glass():
    g = bpy.data.objects.get('FRONT_GLASS')
    if g is None:
        return {'error': 'missing'}
    bpy.context.view_layer.update()
    lo = Vector((min((g.matrix_world @ Vector(c)).x for c in g.bound_box), min((g.matrix_world @ Vector(c)).y for c in g.bound_box), min((g.matrix_world @ Vector(c)).z for c in g.bound_box)))
    hi = Vector((max((g.matrix_world @ Vector(c)).x for c in g.bound_box), max((g.matrix_world @ Vector(c)).y for c in g.bound_box), max((g.matrix_world @ Vector(c)).z for c in g.bound_box)))
    return {'parent': g.parent.name if g.parent else None, 'hide_viewport': g.hide_viewport, 'hide_render': g.hide_render,
            'world_min_mm': [round(v / MM, 1) for v in lo], 'world_max_mm': [round(v / MM, 1) for v in hi],
            'pose_ok': bool(g.parent) and abs(lo.y / MM + 102) < 0.6 and abs(hi.y / MM + 98) < 0.6}


def run(write=True, skip=()):
    data = _build_all()
    res = {'objects': len(data)}
    if 'V06' not in skip:
        res['V06_glass'] = v06_glass()
    if 'V01' not in skip:
        res['V01_ball_sweep'] = v01_ball_sweep(data)
    if 'V02' not in skip:
        res['V02_intersections'] = v02_intersections(data)
    if 'V05' not in skip:
        res['V05_floating'] = v05_floating(data)
    if write:
        p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs', 'validation', 'refine_check.json')
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(res, f, indent=2)
    return res
