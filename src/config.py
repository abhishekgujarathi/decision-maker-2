"""Dimensioned source of truth for the Chaos Chamber CC-01.

All authored dimensions are millimetres. The enforced Blender world is Z-up:
X is left/right, Z is bottom/top, and Y is depth with the glass/front toward
negative Y. Assembly functions are authored in a local front-elevation frame
(Y-up, positive Z toward the front); ``CHAOS_CHAMBER_ROOT`` maps that frame
into the production world with a +90 degree X rotation.
"""
from math import radians

W, H, D = 420.0, 730.0, 250.0
HX, HZ = W/2, D/2
FOOT_H = 10.0
WALNUT_T = 18.0
CHASSIS_H = 115.0
HEADER_H = 60.0
Y_CHASSIS_TOP = FOOT_H + CHASSIS_H
Y_HEADER_BOTTOM = H - HEADER_H
FRAME_W = 14.0
FRAME_D = 20.0
X_INNER = HX - WALNUT_T
X_POST = X_INNER - FRAME_W/2

GLASS_T = 4.0
GLASS_X = 370.0
GLASS_Y0, GLASS_Y1 = Y_CHASSIS_TOP + 2.0, Y_HEADER_BOTTOM + 6.0
FRONT_Z = HZ
GLASS_Z = FRONT_Z - 25.0

BALL_D = 18.0
BALL_R = BALL_D/2
TRACK_W = 23.0
TRACK_T = 1.5
TRACK_WALL = 10.0
TURN_R = 30.0  # centre-line radius; specification range is 26--32 mm

# Front-elevation centreline.  Runs are slightly inclined and the turns are
# true semicircles in plan so the rail is continuous and collision-friendly.
X_LEFT, X_RIGHT = -145.0, 145.0
RUN_Y = (590.0, 525.0, 460.0)
RUN_DROP = 32.0
TRACK_Z = 63.0  # track floor mid-plane (local z; world y = -z)

# Refinement datums (P2.1). Local z, front = +z, world y = -z.
BALL_Z = TRACK_Z + TRACK_T/2 + BALL_R   # 72.75: ball centre rests on the floor front face
Y_BALL = -BALL_Z                         # production-world ball-plane datum
PLATE_T = 4.0                            # mechanism plate sheet thickness
STANDOFF_L = 6.0                         # standoff length, floor back face -> bracket tab
TAB_T = 2.0                              # bracket tab thickness
PLATE_Z_FRONT = TRACK_Z - TRACK_T/2 - STANDOFF_L - TAB_T   # 54.25
PLATE_Z_BACK = PLATE_Z_FRONT - PLATE_T                      # 50.25
PLATE_Z_CENTER = (PLATE_Z_FRONT + PLATE_Z_BACK) / 2.0
BALL_CLEARANCE = 2.0                     # bore clearance per side around the ball
BORE_D = BALL_D + 2*BALL_CLEARANCE       # 22 mm minimum bore
# RF-C3 escapement gate datums (local authoring frame, y = vertical).
# Gate = flat blade in the ball plane (z = BALL_Z) entering from +x through side-wall slots.
# The queued ball rests on the blade top: queue datum y = gate top + BALL_R.
GATE_T = 3.0                     # blade thickness (y)
GATE_W = 8.0                     # blade width (z), centred on BALL_Z
GATE_LEN = 28.0                  # blade length (x)
QUEUE_SPACING = BALL_D + 4.5     # 22.5 mm between queued ball centres
GATE_LOWER_TOP = 598.5           # lower release gate top face y
GATE_UPPER_TOP = GATE_LOWER_TOP + QUEUE_SPACING   # 621.0
GATE_CLOSED_TIP_DX = -4.0        # closed: tip 4 mm past ball centre (supports ball bottom)
GATE_OPEN_TIP_DX = 11.0          # open: tip 2 mm clear of the ball silhouette (R=9) + 0 slack
GATE_TRAVEL = GATE_OPEN_TIP_DX - GATE_CLOSED_TIP_DX   # 15 mm
GATE_SLOT_CLEAR = 0.5            # slot clearance per side around the blade
QUEUE_Y_LOWER = GATE_LOWER_TOP + BALL_R   # 607.5
QUEUE_Y_UPPER = GATE_UPPER_TOP + BALL_R   # 630.0

SHOW_FRONT_GLASS = True   # glass on by default (RF-B1); set False for unobstructed mechanism renders
WORLD_UP_AXIS = 'Z'
WORLD_FRONT_AXIS = '-Y'
AUTHORING_UP_AXIS = 'Y'
AUTHORING_FRONT_AXIS = '+Z'
RENDER_PREFIX = ''        # e.g. 'cc01_' produces cc01_001.png, cc01_002.png ...
RENDER_DIGITS = 3

PIVOT = (0.0, 315.0, BALL_Z)
OUT_X = (-78.0, 78.0)
POCKET_Y0, POCKET_Y1 = 145.0, 245.0

# P1 mechanical review dimensions.  These are authored in the same local
# front-elevation frame as the rest of the mechanism.
BALL_PATH_SAMPLE_COUNT = 240
GLASS_CLEARANCE_MIN = 3.0

# Phase 2 datum and tolerance table. Values are local authoring-frame mm
# unless explicitly named as a world datum.
DATUMS_MM = {
    'enclosure_center': (0.0, 0.0, 0.0),
    'glass_inner_face_world_y': -98.0,
    'glass_outer_face_world_y': -102.0,
    'track_floor_z': TRACK_Z,
    'ball_plane_z': BALL_Z,
    'plate_front_z': PLATE_Z_FRONT,
    'selector_pivot': PIVOT,
    'gate_pivot': PIVOT,
    'input_centerline': (-145.0, 638.0, BALL_Z),
    'queue_datum_lower_y': QUEUE_Y_LOWER,
    'queue_datum_upper_y': QUEUE_Y_UPPER,
    'gate_travel_mm': GATE_TRAVEL,
    'yes_pocket_center': (OUT_X[0], (POCKET_Y0 + POCKET_Y1) / 2.0, BALL_Z),
    'no_pocket_center': (OUT_X[1], (POCKET_Y0 + POCKET_Y1) / 2.0, BALL_Z),
}

DIMENSION_TOLERANCES_MM = {
    'enclosure_envelope': 2.0,
    'track_width': 0.5,
    'ball_diameter': 0.2,
    'glass_clearance_min': 3.0,
    'selector_stop_angle': 1.0,
}

ASSEMBLY_REVISION = 'P2.1'
AUTHORED_UNITS = 'mm'

