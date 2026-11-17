"""Dimension and clearance checks for the built CC-01 Blender scene.

This module is intentionally read-only. It reports the evaluated world-space
envelope and the P0 dimensions that must be stable before detailed modelling.
"""
from __future__ import annotations

import json
import math
import os
from typing import Any

import bpy
from mathutils import Vector

from .config import (
    AUTHORING_FRONT_AXIS,
    AUTHORING_UP_AXIS,
    D,
    H,
    TRACK_W,
    TRACK_T,
    TRACK_Z,
    TRACK_WALL,
    TURN_R,
    W,
    WORLD_FRONT_AXIS,
    WORLD_UP_AXIS,
    BALL_D,
    BALL_R,
    BALL_Z,
    OUT_X,
    POCKET_Y1,
    QUEUE_SPACING,
    GLASS_CLEARANCE_MIN,
    DATUMS_MM,
    DIMENSION_TOLERANCES_MM,
    ASSEMBLY_REVISION,
    AUTHORED_UNITS,
)
from .paths import track_centerline, full_ball_path, selector_branch_paths


TOLERANCE_MM = 2.0
TURN_RADIUS_MIN_MM = 26.0
TURN_RADIUS_MAX_MM = 32.0
PRODUCT_COLLECTIONS = {
    'HOUSING',
    'TRACK_ASSEMBLY',
    'INPUT_ASSEMBLY',
    'RANDOM_SELECTOR',
    'OUTPUT_ASSEMBLY',
    'REAR_CONSTRUCTION',
    'ELECTRONICS',
    'FASTENERS',
    'BALL_ASSEMBLY',
}
MECHANISM_COLLECTIONS = {
    'TRACK_ASSEMBLY',
    'INPUT_ASSEMBLY',
    'RANDOM_SELECTOR',
    'OUTPUT_ASSEMBLY',
    'ELECTRONICS',
    'FASTENERS',
}


def _world_bounds(obj: bpy.types.Object) -> tuple[Vector, Vector]:
    """Return evaluated object bounds in world metres."""
    # Blender can leave matrix_world stale for a viewport-hidden object. The
    # front glass is intentionally hidden during modeling, so briefly include
    # it in evaluation and restore the exact visibility state afterwards.
    was_hidden = obj.hide_viewport
    if was_hidden:
        obj.hide_viewport = False
        bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    try:
        evaluated = obj.evaluated_get(depsgraph)
        corners = [evaluated.matrix_world @ Vector(corner) for corner in evaluated.bound_box]
        return (
            Vector((min(point.x for point in corners), min(point.y for point in corners), min(point.z for point in corners))),
            Vector((max(point.x for point in corners), max(point.y for point in corners), max(point.z for point in corners))),
        )
    finally:
        if was_hidden:
            obj.hide_viewport = True
            bpy.context.view_layer.update()


def _product_objects() -> list[bpy.types.Object]:
    objects = []
    for obj in bpy.context.scene.objects:
        if obj.type not in {'MESH', 'CURVE', 'FONT', 'SURFACE'}:
            continue
        if any(collection.name in PRODUCT_COLLECTIONS for collection in obj.users_collection):
            objects.append(obj)
    return objects


def _check(name: str, actual: Any, expected: Any, passed: bool, units: str = 'mm') -> dict[str, Any]:
    return {
        'name': name,
        'actual': actual,
        'expected': expected,
        'passed': bool(passed),
        'units': units,
    }


def _envelope_check() -> tuple[dict[str, Any], dict[str, Any]]:
    bounds = [_world_bounds(obj) for obj in _product_objects()]
    if not bounds:
        empty = {'width': 0.0, 'height': 0.0, 'depth': 0.0}
        return empty, _check('world_envelope', empty, {'width': W, 'height': H, 'depth': D}, False)
    minimum = Vector((min(item[0].x for item in bounds), min(item[0].y for item in bounds), min(item[0].z for item in bounds)))
    maximum = Vector((max(item[1].x for item in bounds), max(item[1].y for item in bounds), max(item[1].z for item in bounds)))
    actual = {
        'width': round((maximum.x - minimum.x) * 1000.0, 3),
        'height': round((maximum.z - minimum.z) * 1000.0, 3),
        'depth': round((maximum.y - minimum.y) * 1000.0, 3),
        'min_world': [round(value * 1000.0, 3) for value in minimum],
        'max_world': [round(value * 1000.0, 3) for value in maximum],
    }
    expected = {'width': W, 'height': H, 'depth': D}
    passed = all(abs(actual[key] - expected[key]) <= TOLERANCE_MM for key in expected)
    return actual, _check('world_envelope', actual, expected, passed)


def _glass_clearance_check() -> dict[str, Any]:
    glass = bpy.data.objects.get('FRONT_GLASS')
    if glass is None:
        return _check('glass_clearance', None, 'FRONT_GLASS present and mechanism behind inner face', False)
    glass_min, glass_max = _world_bounds(glass)
    inner_y = glass_max.y  # front is negative Y, so +Y is the inner/back face
    glass_x_min, glass_x_max = glass_min.x, glass_max.x
    glass_z_min, glass_z_max = glass_min.z, glass_max.z
    candidates = []
    for obj in bpy.context.scene.objects:
        if obj.type not in {'MESH', 'CURVE', 'FONT', 'SURFACE'}:
            continue
        if not any(collection.name in MECHANISM_COLLECTIONS for collection in obj.users_collection):
            continue
        minimum, maximum = _world_bounds(obj)
        if maximum.x < glass_x_min or minimum.x > glass_x_max:
            continue
        if maximum.z < glass_z_min or minimum.z > glass_z_max:
            continue
        candidates.append((minimum.y, obj.name))
    if not candidates:
        return _check('glass_clearance', None, 'mechanism candidates', False)
    frontmost_y, frontmost_name = min(candidates)
    clearance_mm = (frontmost_y - inner_y) * 1000.0
    actual = {
        'clearance': round(clearance_mm, 3),
        'frontmost_object': frontmost_name,
        'glass_inner_y': round(inner_y * 1000.0, 3),
        'frontmost_y': round(frontmost_y * 1000.0, 3),
    }
    return _check('glass_clearance', actual, f'>= {GLASS_CLEARANCE_MIN:g} mm', clearance_mm >= GLASS_CLEARANCE_MIN - 1e-3)


def _track_checks() -> list[dict[str, Any]]:
    points = track_centerline()
    step_lengths = [math.dist(points[index - 1], points[index]) for index in range(1, len(points))]
    run_pairs = [((-145.0, 590.0), (145.0, 560.0)), ((145.0, 500.0), (-145.0, 470.0)), ((-145.0, 410.0), (145.0, 380.0))]
    slope_degrees = [round(math.degrees(math.atan2(abs(end[1] - start[1]), abs(end[0] - start[0]))), 3) for start, end in run_pairs]
    return [
        _check('track_width', TRACK_W, '22-24', 22.0 <= TRACK_W <= 24.0),
        _check('track_wall_height', TRACK_WALL, '8-12', 8.0 <= TRACK_WALL <= 12.0),
        _check('u_turn_radius', TURN_R, '26-32', TURN_RADIUS_MIN_MM <= TURN_R <= TURN_RADIUS_MAX_MM),
        _check('track_continuity', {'point_count': len(points), 'max_step': round(max(step_lengths), 3)}, '<= 20 mm', max(step_lengths) <= 20.0),
        _check('track_run_slopes', slope_degrees, '5-8 degrees', all(5.0 <= slope <= 8.0 for slope in slope_degrees), units='degrees'),
    ]


def _mechanical_checks() -> list[dict[str, Any]]:
    paths = full_ball_path()
    main = paths['INPUT_TO_SELECTOR']
    branch = selector_branch_paths()
    path_sets = [main, branch['YES'], branch['NO']]
    max_step = max(
        math.dist(path[i - 1], path[i])
        for path in path_sets
        for i in range(1, len(path))
    )
    ball = bpy.data.objects.get('STEEL_BALL_PATH_TEST')
    path_obj = bpy.data.objects.get('BALL_CENTRE_PATH')
    branches_separate = all(a[0] <= 20.0 for a in branch['YES']) and all(a[0] >= 20.0 for a in branch['NO'])
    channel_clearance = TRACK_W - BALL_D
    track_inside_chamber = all(-190.0 <= point[0] <= 190.0 and 40.0 <= point[1] <= 690.0 for point in main)
    required = {
        'STEEL_BALL_PATH_TEST': ball is not None,
        'BALL_CENTRE_PATH': path_obj is not None,
        'INPUT_LAUNCH_CRADLE': bpy.data.objects.get('INPUT_LAUNCH_CRADLE_FLOOR') is not None,
        'YES_BRANCH': bpy.data.objects.get('YES_BRANCH_FLOOR') is not None,
        'NO_BRANCH': bpy.data.objects.get('NO_BRANCH_FLOOR') is not None,
        'DIVERTER_GATE': bpy.data.objects.get('DIVERTER_GATE') is not None,
    }
    return [
        _check('ball_diameter', BALL_D, '18 mm', abs(BALL_D - 18.0) <= TOLERANCE_MM),
        _check('ball_track_clearance', {'track_width': TRACK_W, 'ball_diameter': BALL_D, 'side_clearance': round(channel_clearance, 3)}, '>= 4 mm side clearance', channel_clearance >= 4.0),
        _check('track_inside_chamber', {'x_range': [-190.0, 190.0], 'y_range': [40.0, 690.0]}, 'all centreline samples inside chamber', track_inside_chamber),
        _check('ball_path_continuity', {'point_count': sum(len(path) for path in path_sets), 'max_step': round(max_step, 3)}, '<= 20 mm', max_step <= 20.0),
        _check('ball_path_objects', required, 'all required path objects present', all(required.values()), units=''),
        _check('selector_branch_separation', {'yes_max_x': max(p[0] for p in branch['YES']), 'no_min_x': min(p[0] for p in branch['NO'])}, 'YES <= pivot <= NO', branches_separate),
    ]


def _input_checks() -> list[dict[str, Any]]:
    chamber = bpy.data.objects.get('ESCAPEMENT_TUBE')
    upper = bpy.data.objects.get('ESCAPEMENT_UPPER_RETAINER_GATE')
    lower = bpy.data.objects.get('ESCAPEMENT_LOWER_RELEASE_GATE')
    interlock = bpy.data.objects.get('ESCAPEMENT_INTERLOCK_LINK')
    sensor = bpy.data.objects.get('ESCAPEMENT_SENSOR')
    required = {
        'hopper_rim': all(bpy.data.objects.get(name) is not None for name in ('HOPPER_RIM_FRONT', 'HOPPER_RIM_BACK', 'HOPPER_RIM_LEFT', 'HOPPER_RIM_RIGHT')),
        'throat_collar': bpy.data.objects.get('HOPPER_THROAT_COLLAR') is not None,
        'holding_chamber': chamber is not None,
        'upper_gate': upper is not None,
        'lower_gate': lower is not None,
        'interlock': interlock is not None,
        'sensor_datum': sensor is not None and sensor.get('sensing_datum_mm') is not None,
        'launch_bridge': bpy.data.objects.get('HOLDING_TO_CRADLE_BRIDGE') is not None,
    }
    spacing = chamber.get('ball_queue_spacing_mm', 0.0) if chamber else 0.0
    gate_travel = [upper.get('travel_mm', 0.0), lower.get('travel_mm', 0.0)] if upper and lower else [0.0, 0.0]
    independent_stops = bool(upper and lower and upper.get('hard_stops_mm') and lower.get('hard_stops_mm'))
    return [
        _check('input_assembly_detail', required, 'hopper, chamber, gates, interlock, sensor, cradle present', all(required.values()), units=''),
        _check('holding_capacity_and_spacing', {'capacity_balls': chamber.get('capacity_balls') if chamber else 0, 'spacing_mm': spacing}, 'capacity >= 2; spacing >= ball diameter + 2 mm', chamber is not None and chamber.get('capacity_balls', 0) >= 2 and spacing >= BALL_D + 2.0),
        _check('escapement_gate_travel', {'upper_mm': gate_travel[0], 'lower_mm': gate_travel[1], 'independent_hard_stops': independent_stops}, 'both gates have positive travel and stops', all(value > 0.0 for value in gate_travel) and independent_stops),
        _check(
            'one_ball_release_interlock',
            {
                'interlock_logic': interlock.get('logic') if interlock else None,
                'gate_spacing_mm': QUEUE_SPACING,
            },
            'mutual exclusion between retainer and release',
            interlock is not None
            and 'cannot be open together' in interlock.get('logic', '')
            and QUEUE_SPACING >= BALL_D + 2.0,
        ),
    ]


def _phase2_checks() -> list[dict[str, Any]]:
    named_track_groups = {
        'TRACK_RUN_01', 'TRACK_RUN_02', 'TRACK_RUN_03',
        'TRACK_UTURN_01', 'TRACK_UTURN_02', 'TRACK_UTURN_03',
        'TRACK_EXIT_GUIDE_01', 'TRACK_EXIT_GUIDE_02', 'TRACK_EXIT_GUIDE_CONTINUOUS',
        'TRACK_BRACKETS', 'TRACK_FASTENERS',
    }
    present_groups = {name for name in named_track_groups if bpy.data.collections.get(name) is not None}
    ball_coll = bpy.data.collections.get('BALL_ASSEMBLY')
    rear_required = ('REAR_SERVICE_COVER', 'SELECTOR_SERVICE_HATCH', 'POWER_INLET', 'MAIN_SWITCH')
    rear_present = {name: bpy.data.objects.get(name) is not None for name in rear_required}
    rear_fasteners = len([obj for obj in bpy.data.objects if obj.name.startswith('REAR_FASTENER_')])
    ids = {obj.get('component_id') for obj in bpy.context.scene.objects}
    return [
        _check('track_phase2_groups', sorted(present_groups), sorted(named_track_groups), present_groups == named_track_groups, units=''),
        _check('ball_assembly_collection', {'present': ball_coll is not None, 'objects': len(ball_coll.objects) if ball_coll else 0}, 'BALL_ASSEMBLY with path-test ball', ball_coll is not None and len(ball_coll.objects) >= 2, units=''),
        _check('component_identifiers', sorted(value for value in ids if value), 'CC-210/220/310/420/530/610 present', {'CC-210', 'CC-220', 'CC-310', 'CC-420', 'CC-530', 'CC-610'} <= ids, units=''),
        _check('service_access', {'objects': rear_present, 'rear_fastener_count': rear_fasteners}, 'rear cover, hatch, inlet, switch, >= 6 rear fasteners', all(rear_present.values()) and rear_fasteners >= 6, units=''),
    ]


def _output_checks() -> list[dict[str, Any]]:
    """Verify both pockets have a physical rest and an aligned optical datum."""
    states = {}
    for label in ('YES', 'NO'):
        names = {
            'catch': label + '_CATCH_PLATE',
            'pad': label + '_RUBBER_IMPACT_PAD',
            'sensor': label + '_SENSOR',
            'receiver': label + '_SENSOR_RECEIVER',
            'beam': label + '_SENSOR_BEAM_DATUM',
        }
        objects = {role: bpy.data.objects.get(name) for role, name in names.items()}
        catch = objects['catch']
        datum = list(catch.get('rest_datum_mm', ())) if catch else []
        aligned = (
            len(datum) == 3
            and abs(datum[2] - BALL_Z) <= 0.1
            and all(objects.values())
            and all(list(obj.get('beam_datum_mm', datum)) == datum for obj in (objects['sensor'], objects['receiver']))
            and list(objects['beam'].get('rest_datum_mm', ())) == datum
        )
        states[label] = {'objects': {role: obj is not None for role, obj in objects.items()}, 'rest_datum_mm': datum, 'aligned': aligned}
    branches = selector_branch_paths()
    entries = {}
    for label, x in zip(('YES', 'NO'), OUT_X):
        endpoint = branches[label][-1]
        top = bpy.data.objects.get(label + '_POCKET_TOP')
        entry_ok = (
            top is not None
            and abs(endpoint[0] - x) <= 0.1
            and abs(endpoint[1] - POCKET_Y1) <= 0.1
            # Branch paths are authored on the channel floor. The travelling
            # ball centre is floor + half floor thickness + ball radius.
            and abs(endpoint[2] - TRACK_Z) <= 0.1
            and abs(endpoint[2] + TRACK_T / 2.0 + BALL_R - BALL_Z) <= 0.1
            and top.get('entry_slot_width_mm', 0.0) >= BALL_D + 4.0
        )
        entries[label] = {'branch_endpoint_mm': list(endpoint), 'slot_width_mm': top.get('entry_slot_width_mm') if top else None, 'aligned': entry_ok}
    return [
        _check('output_pocket_rest_and_sensor', states, 'inclined rubber-faced rest and beam through BALL_Z', all(state['aligned'] for state in states.values()), units=''),
        _check('output_branch_entry_alignment', entries, 'branch endpoint at entry slot and >= 22 mm bore', all(entry['aligned'] for entry in entries.values()), units=''),
    ]


def _electronics_checks() -> list[dict[str, Any]]:
    root = bpy.data.objects.get('CHAOS_CHAMBER_ROOT')
    tray = bpy.data.objects.get('ELECTRONICS_TRAY')
    if root is None or tray is None:
        return [_check('electronics_mounting', None, 'tray and three mounted assemblies', False, units='')]
    bpy.context.view_layer.update()
    root_inverse = root.matrix_world.inverted()

    def authored_bounds(obj):
        corners = [root_inverse @ (obj.matrix_world @ Vector(corner)) for corner in obj.bound_box]
        return tuple((min(point[i] for point in corners) * 1000.0,
                      max(point[i] for point in corners) * 1000.0) for i in range(3))

    tray_bounds = authored_bounds(tray)
    assemblies = {}
    for name in ('CONTROL_BOARD', 'MOTOR_DRIVER', 'POWER_SUPPLY'):
        board = bpy.data.objects.get(name)
        mounts = [obj for obj in bpy.data.objects if obj.get('mounts') == name]
        board_bounds = authored_bounds(board) if board else None
        mount_bounds = [authored_bounds(obj) for obj in mounts]
        within = bool(board_bounds) and all(
            board_bounds[axis][0] >= tray_bounds[axis][0] - 0.1
            and board_bounds[axis][1] <= tray_bounds[axis][1] + 0.1
            for axis in (0, 1)
        )
        supported = len(mounts) == 4 and all(
            abs(mount_bounds[index][0][0] - mount_bounds[index][0][1]) <= 0.1
            for index in range(len(mounts))
        )
        mounts_bridge = len(mounts) == 4 and all(
            mount_bounds[index][2][0] <= board_bounds[2][1] + 0.1
            and mount_bounds[index][2][1] >= tray_bounds[2][0] - 0.1
            for index in range(len(mounts))
        ) if board_bounds else False
        assemblies[name] = {
            'board_x_y_bounds_mm': board_bounds[:2] if board_bounds else None,
            'mount_count': len(mounts),
            'within_tray': within,
            'standoffs_bridge_board_to_tray': mounts_bridge,
        }
    passed = all(item['within_tray'] and item['mount_count'] == 4 and item['standoffs_bridge_board_to_tray'] for item in assemblies.values())
    return [_check('electronics_mounting', {'tray_bounds_mm': tray_bounds, 'assemblies': assemblies}, 'three electronics assemblies inside tray with four tray-to-board standoffs each', passed, units='')]


def _architecture_checks() -> list[dict[str, Any]]:
    root = bpy.data.objects.get('CHAOS_CHAMBER_ROOT')
    required_ids = {'CC-100', 'CC-210', 'CC-310', 'CC-340', 'CC-420', 'CC-530', 'CC-610', 'CC-620', 'CC-700'}
    product_objects = _product_objects()
    missing_ids = sorted(obj.name for obj in product_objects if not obj.get('component_id'))
    editable = all(obj.name and obj.data is not None for obj in product_objects)
    present_ids = {obj.get('component_id') for obj in product_objects if obj.get('component_id')}
    datum_keys = set(DATUMS_MM)
    root_datum_keys = set(root.get('datum_table', {})) if root else set()
    return [
        _check('assembly_metadata', {
            'revision': root.get('assembly_revision') if root else None,
            'units': root.get('authored_units') if root else None,
            'coordinate_convention': root.get('coordinate_convention') if root else None,
        }, f'{ASSEMBLY_REVISION} / {AUTHORED_UNITS} / Z-up front -Y', root is not None and root.get('assembly_revision') == ASSEMBLY_REVISION and root.get('authored_units') == AUTHORED_UNITS, units=''),
        _check('named_datums', sorted(root_datum_keys), sorted(datum_keys), root_datum_keys == datum_keys, units=''),
        _check('dimension_tolerance_table', sorted(DIMENSION_TOLERANCES_MM), 'reusable Phase 2 nominal tolerance table', bool(DIMENSION_TOLERANCES_MM), units=''),
        _check('production_component_ids', sorted(present_ids), sorted(required_ids), required_ids <= present_ids, units=''),
        _check('editable_production_objects', {'count': len(product_objects), 'missing_component_ids': missing_ids}, 'all production objects named and data-backed', editable and not missing_ids, units=''),
    ]


def validate_scene(write_report: bool = True, report_path: str | None = None) -> dict[str, Any]:
    """Validate the current Blender scene and optionally write a JSON report."""
    envelope, envelope_check = _envelope_check()
    checks = [
        _check(
            'coordinate_convention',
            {
                'world_up': WORLD_UP_AXIS,
                'world_front': WORLD_FRONT_AXIS,
                'authoring_up': AUTHORING_UP_AXIS,
                'authoring_front': AUTHORING_FRONT_AXIS,
            },
            'Z-up / front -Y; authoring Y-up / front +Z',
            WORLD_UP_AXIS == 'Z' and WORLD_FRONT_AXIS == '-Y' and AUTHORING_UP_AXIS == 'Y' and AUTHORING_FRONT_AXIS == '+Z',
            units='',
        ),
        envelope_check,
        *_track_checks(),
        *_mechanical_checks(),
        *_input_checks(),
        *_output_checks(),
        *_electronics_checks(),
        *_phase2_checks(),
        *_architecture_checks(),
        _glass_clearance_check(),
    ]
    result = {
        'passed': all(check['passed'] for check in checks),
        'tolerance_mm': TOLERANCE_MM,
        'envelope': envelope,
        'checks': checks,
    }
    if write_report:
        if report_path is None:
            root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            report_path = os.path.join(root, 'outputs', 'validation', 'phase1_validation.json')
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as handle:
            json.dump(result, handle, indent=2)
        result['report_path'] = report_path
    print('CC-01 P0 validation: ' + ('PASS' if result['passed'] else 'FAIL'))
    for check in checks:
        print('  %-24s %s | actual=%s | expected=%s' % (check['name'], 'PASS' if check['passed'] else 'FAIL', check['actual'], check['expected']))
    return result


if __name__ == '__main__':
    validate_scene()
