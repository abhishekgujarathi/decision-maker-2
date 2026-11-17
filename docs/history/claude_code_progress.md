mkdir -p /home/claude/chaos_chamber/chaos_chamber && cd /home/claude/chaos_chamber && cat > chaos_chamber/config.py << 'EOF'
"""
config.py - single source of truth for every dimension of the Chaos Chamber CC-01.

ALL VALUES ARE IN MILLIMETRES.  (Blender scene units are metres; utils.mm() converts.)

Blender axes used by this project
    X : left  -> right
    Y : front -> back   (FRONT OF THE MACHINE FACES -Y, the back is +Y)
    Z : bottom -> top
Origin = centre of the bottom of the chassis, on the table plane.
glTF export maps this to  Y-up / +Z-front, i.e. exactly the brief's coordinate system
(brief X = X, brief Y(up) = Z, brief Z(front) = -Y).
"""
import math

# ----------------------------------------------------------------------------- overall
W, H, D = 420.0, 730.0, 250.0
HX, HY = W / 2, D / 2                     # 210 / 125
FOOT_H = 10.0                             # rubber feet
Z_BODY0 = FOOT_H                          # underside of enclosure
Z_TOP = H

# ----------------------------------------------------------------------------- housing
T_WALNUT = 18.0
X_IN = HX - T_WALNUT                      # 192 : inner face of walnut panels
CHASSIS_H = 115.0
Z_CH_TOP = Z_BODY0 + CHASSIS_H            # 125
HEADER_H = 60.0
Z_HEADER0 = Z_TOP - HEADER_H              # 670
POST_W, POST_D = 14.0, 20.0               # frame post section (X x Y)
X_OPEN = X_IN - POST_W                    # 178 -> visible chamber is 356 mm wide
Z_OPEN0, Z_OPEN1 = Z_CH_TOP, Z_HEADER0    # 125..670  -> 545 mm tall
Y_FRONT = -HY                             # -125 front plane of frame / header / fascia
Y_POST_REAR = Y_FRONT + POST_D            # -105

# front door glass (hinged left, latch right)
GLASS_T = 4.0
GLASS_HX = 185.0                          # 370 wide
GLASS_Z0, GLASS_Z1 = Z_CH_TOP + 2.0, Z_HEADER0 + 6.0   # 127..676
GLASS_Y_FRONT = -100.0
GLASS_Y_REAR = GLASS_Y_FRONT + GLASS_T    # -96
HINGE_X = -189.0
HINGE_Y = -102.5
HINGE_ZS = (190.0, 600.0)
LATCH_Z = 400.0

# rear
Y_REAR_PANEL0, Y_REAR_PANEL1 = 119.0, 122.0
Y_BACK_PLATE0, Y_BACK_PLATE1 = 60.0, 63.0  # internal charcoal backing sheet

# ----------------------------------------------------------------------------- ball / track
BALL_D = 18.0
BALL_R = BALL_D / 2
TRACK_W_IN = 23.0                         # internal width (brief 22-24)
SHEET_T = 1.5
TRACK_WALL_RUN = 10.0                     # side wall height above floor (brief 8-12)
TRACK_WALL_TURN = 12.0                    # raised retaining lip in bends
TURN_R = 30.0                             # centre-line bend radius (brief 26-32)
RUN_SLOPE = 8.0                           # deg (brief 5-8)
TURN_SLOPE = 20.0                         # deg
SLOPE_BLEND = 15.0                        # mm either side of a junction
LIP_RAMP = 20.0

Y_TRACK_A = -5.0                          # depth of runs 1 and 3
Y_TRACK_B = -65.0                         # depth of run 2 and exit leg
X_TURN = 115.0                            # where straight runs end / arcs begin  (apex = +-145)
X_START = -157.0                          # run-1 start (rear wall of launch cradle)
Z_P0 = 590.0                              # ball-centre height at x = -145 (brief P0)
X_P0 = -145.0
EXIT_TIP = (12.0, Y_TRACK_B, 343.0)       # exit leg ends here (ball centre)

# ----------------------------------------------------------------------------- input assembly
TUBE_X, TUBE_Y = X_P0, Y_TRACK_A
TUBE_Z0, TUBE_Z1 = 600.0, 640.0
TUBE_R_IN, TUBE_T = 10.5, 1.5
BALL_B_Z, BALL_A_Z = 612.0, 630.0         # waiting positions (ball B on lower pin, ball A on B)
PIN_D = 3.5
PIN_Z_LOWER = BALL_B_Z - BALL_R - PIN_D / 2   # 601.25
PIN_Z_UPPER = BALL_A_Z - BALL_R - PIN_D / 2   # 619.25
FUNNEL_Z0, FUNNEL_Z1 = 640.0, 666.0
PIN_STROKE = 16.0

# ----------------------------------------------------------------------------- selector / output
FORK_X = 0.0
PIVOT_Z = 312.0
PLATE_Z = PIVOT_Z + 2.0                   # plate underside sits on the hub (ball rests at z = 325, brief P8)
DIVERTER_TILT = 10.0                      # +-10 deg  => 20 deg between positions (brief 18-22)
OUT_X = 75.0                              # pocket centres  +-75  (brief P9/P10)
POCKET_W, POCKET_D = 64.0, 56.0
POCKET_Z0, POCKET_Z1 = 150.0, 240.0

# ----------------------------------------------------------------------------- misc
BUILD_ENVIRONMENT = False                 # table / wall / lamp (not part of the product)
BUILD_ELECTRONICS = True
EOF
cat > chaos_chamber/utils.py << 'EOF'
"""
utils.py - geometry kernel shared by every part module.

* Everything is authored in MILLIMETRES and converted to metres on mesh creation.
* MeshBuilder wraps a bmesh and offers box / cylinder / sphere / revolve / prism / sweep.
* Booleans are applied through the dependency graph (no bpy.ops, so they work headless).
* Hardware (screws, nuts, washers ...) is created once per spec and INSTANCED as linked duplicates.
"""
import math
import bpy
import bmesh
from mathutils import Vector, Matrix, Euler

MM = 0.001
UV_SCALE = 1.0 / 200.0          # 1 UV tile = 200 mm (box projected)
REG = {}                        # name -> object  (registry of every created object)
ANCHORS = {}                    # name -> Vector in mm (connection points shared between modules)


def mm(v):
    """mm -> m for a scalar or a vector-like."""
    if isinstance(v, (int, float)):
        return v * MM
    return Vector([c * MM for c in v])


def vec(v):
    return Vector(v) if not isinstance(v, Vector) else v.copy()


# ----------------------------------------------------------------------------- rotations
def rot3(rot):
    """None | Matrix | (rx,ry,rz) degrees  ->  3x3 matrix"""
    if rot is None:
        return Matrix.Identity(3)
    if isinstance(rot, Matrix):
        return rot.to_3x3()
    return Euler([math.radians(a) for a in rot], 'XYZ').to_matrix()


def axis_rot(axis):
    """3x3 matrix that maps local +Z onto the requested axis ('X','Y','Z', '-X'.. or a vector)."""
    table = {'Z': (0, 0, 1), 'X': (1, 0, 0), 'Y': (0, 1, 0),
             '-Z': (0, 0, -1), '-X': (-1, 0, 0), '-Y': (0, -1, 0)}
    d = Vector(table[axis]) if isinstance(axis, str) else Vector(axis).normalized()
    if (d - Vector((0, 0, 1))).length < 1e-9:
        return Matrix.Identity(3)
    if (d + Vector((0, 0, 1))).length < 1e-9:
        return Matrix.Rotation(math.pi, 3, 'X')
    return d.to_track_quat('Z', 'Y').to_matrix()


# ----------------------------------------------------------------------------- collections / empties
def collection(name, parent=None):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    c = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(c)
    return c


def empty(name, coll, parent=None, loc=(0, 0, 0), size=20.0, kind='PLAIN_AXES'):
    o = bpy.data.objects.new(name, None)
    o.empty_display_type = kind
    o.empty_display_size = size * MM
    o.location = mm(loc)
    coll.objects.link(o)
    if parent:
        set_parent(o, parent)
    REG[name] = o
    return o


def set_parent(obj, parent):
    obj.parent = parent
    obj.matrix_parent_inverse = parent.matrix_world.inverted()


# ----------------------------------------------------------------------------- mesh builder
class MeshBuilder:
    def __init__(self):
        self.bm = bmesh.new()

    # ---- primitives --------------------------------------------------------------------
    def box(self, center, size, rot=None, bevel=0.0, bevel_seg=2):
        sx, sy, sz = size
        M = (Matrix.Translation(Vector(center)) @ rot3(rot).to_4x4()
             @ Matrix.Diagonal((sx, sy, sz, 1.0)))
        res = bmesh.ops.create_cube(self.bm, size=1.0, matrix=M)
        if bevel > 0:
            edges = list({e for v in res['verts'] for e in v.link_edges})
            bmesh.ops.bevel(self.bm, geom=edges, offset=min(bevel, min(size) * 0.45),
                            offset_type='OFFSET', segments=bevel_seg, profile=0.5, affect='EDGES')
        return res['verts']

    def cyl(self, center, r, length, axis='Z', seg=24, r2=None, cap=True):
        M = Matrix.Translation(Vector(center)) @ axis_rot(axis).to_4x4()
        bmesh.ops.create_cone(self.bm, cap_ends=cap, cap_tris=False, segments=seg, radius1=r,
                              radius2=(r if r2 is None else r2), depth=length, matrix=M, calc_uvs=False)

    def sphere(self, center, r, useg=48, vseg=24):
        bmesh.ops.create_uvsphere(self.bm, u_segments=useg, v_segments=vseg, radius=r,
                                  matrix=Matrix.Translation(Vector(center)), calc_uvs=False)

    def grid(self, rings, closed_profile=True, closed_path=False, cap_start=False, cap_end=False):
        """Skin a list of rings (each a list of mm Vectors)."""
        bm = self.bm
        vr = [[bm.verts.new(p) for p in ring] for ring in rings]
        m, n = len(vr), len(vr[0])
        for i in (range(m) if closed_path else range(m - 1)):
            a, b = vr[i], vr[(i + 1) % m]
            for j in (range(n) if closed_profile else range(n - 1)):
                j2 = (j + 1) % n
                try:
                    bm.faces.new((a[j], a[j2], b[j2], b[j]))
                except ValueError:
                    pass
        try:
            if cap_start:
                bm.faces.new(vr[0])
            if cap_end:
                bm.faces.new(vr[-1][::-1])
        except ValueError:
            pass
        return vr

    def revolve(self, profile, center=(0, 0, 0), axis='Z', seg=48, phase=0.0):
        """Revolve a CLOSED (r, h) loop (all r>0) about an axis through `center`."""
        Rm = axis_rot(axis)
        c = Vector(center)
        rings = []
        for k in range(seg):
            a = 2 * math.pi * k / seg + phase
            ca, sa = math.cos(a), math.sin(a)
            rings.append([c + Rm @ Vector((r * ca, r * sa, h)) for r, h in profile])
        self.grid(rings, True, True)

    def prism(self, pts2d, depth, origin=(0, 0, 0), u=(1, 0, 0), v=(0, 1, 0), n=None):
        """Extrude a 2-D polygon (pts in the u/v plane at `origin`) by `depth` along n (default u x v)."""
        u, v = Vector(u), Vector(v)
        n = Vector(n) if n is not None else u.cross(v)
        n = n.normalized() * depth
        o = Vector(origin)
        vs = [self.bm.verts.new(o + u * p[0] + v * p[1]) for p in pts2d]
        f = self.bm.faces.new(vs)
        r = bmesh.ops.extrude_face_region(self.bm, geom=[f])
        nv = [g for g in r['geom'] if isinstance(g, bmesh.types.BMVert)]
        bmesh.ops.translate(self.bm, vec=n, verts=nv)

    def tube_along(self, pts, radius, seg=10, closed=False, up=(0, 0, 1)):
        """Round wire / spring swept along a polyline."""
        rings = []
        n = len(pts)
        for i, p in enumerate(pts):
            a = pts[max(i - 1, 0)]
            b = pts[min(i + 1, n - 1)]
            T = (Vector(b) - Vector(a)).normalized()
            ref = Vector(up)
            if abs(T.dot(ref)) > 0.95:
                ref = Vector((1, 0, 0))
            N = T.cross(ref).normalized()
            B = T.cross(N).normalized()
            rings.append([Vector(p) + (N * math.cos(2 * math.pi * k / seg) +
                                       B * math.sin(2 * math.pi * k / seg)) * radius for k in range(seg)])
        self.grid(rings, True, closed, cap_start=not closed, cap_end=not closed)

    def spring(self, p0, p1, coil_r, wire_r, turns, seg_per_turn=14, wire_seg=8):
        p0, p1 = Vector(p0), Vector(p1)
        ax = (p1 - p0)
        L = ax.length
        axn = ax.normalized()
        ref = Vector((0, 0, 1)) if abs(axn.z) < 0.9 else Vector((1, 0, 0))
        e1 = axn.cross(ref).normalized()
        e2 = axn.cross(e1).normalized()
        steps = int(turns * seg_per_turn)
        pts = []
        for i in range(steps + 1):
            t = i / steps
            a = 2 * math.pi * turns * t
            pts.append(p0 + axn * (L * t) + (e1 * math.cos(a) + e2 * math.sin(a)) * coil_r)
        self.tube_along(pts, wire_r, seg=wire_seg, up=tuple(axn))

    # ---- finishing ---------------------------------------------------------------------
    def _uv_box(self, origin):
        bm = self.bm
        layer = bm.loops.layers.uv.verify()
        bm.faces.ensure_lookup_table()
        for f in bm.faces:
            n = f.normal
            ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
            for l in f.loops:
                p = l.vert.co + origin
                if az >= ax and az >= ay:
                    uv = (p.x, p.y)
                elif ay >= ax:
                    uv = (p.x, p.z)          # front/back : U=x  V=z  (vertical grain)
                else:
                    uv = (p.y, p.z)          # sides      : U=y  V=z
                l[layer].uv = (uv[0] * UV_SCALE, uv[1] * UV_SCALE)

    def to_mesh(self, name, origin=(0, 0, 0), smooth_deg=40.0, uv=True):
        bm = self.bm
        origin = Vector(origin)
        if len(bm.faces):
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        bm.normal_update()
        if uv and len(bm.faces):
            self._uv_box(origin * 0)  # world-mm projection (before re-centering)
        mark_smooth(bm, smooth_deg)
        bmesh.ops.translate(bm, vec=-origin, verts=bm.verts[:])
        bmesh.ops.scale(bm, vec=Vector((MM, MM, MM)), verts=bm.verts[:])
        mesh = bpy.data.meshes.new(name)
        bm.to_mesh(mesh)
        bm.free()
        return mesh

    def build(self, name, coll, origin=(0, 0, 0), parent=None, smooth_deg=40.0, uv=True):
        mesh = self.to_mesh(name, origin, smooth_deg, uv)
        o = bpy.data.objects.new(name, mesh)
        o.location = mm(origin)
        coll.objects.link(o)
        if parent is not None:
            set_parent(o, parent)
        REG[name] = o
        return o


def mark_smooth(bm, deg=40.0):
    """Smooth-shade everything but flag edges sharper than `deg` as sharp (works Blender 3.x-5.x)."""
    lim = math.radians(deg)
    for e in bm.edges:
        if len(e.link_faces) == 2:
            a = e.link_faces[0].normal.angle(e.link_faces[1].normal, 0.0)
            e.smooth = a < lim
        else:
            e.smooth = False
    for f in bm.faces:
        f.smooth = True


def finish_mesh(obj, deg=40.0, uv=True):
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.normal_update()
    mark_smooth(bm, deg)
    if uv and len(bm.faces):
        mb = MeshBuilder()
        mb.bm = bm
        mb._uv_box(obj.location / MM)
        mb.bm = None
    bm.to_mesh(me)
    bm.free()
    if hasattr(me, 'use_auto_smooth'):       # Blender <= 4.0
        me.use_auto_smooth = True
        me.auto_smooth_angle = math.radians(deg)


# ----------------------------------------------------------------------------- booleans
def apply_modifiers(obj):
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg)
    new = bpy.data.meshes.new_from_object(ev)
    old = obj.data
    obj.modifiers.clear()
    obj.data = new
    new.name = old.name
    if old.users == 0:
        bpy.data.meshes.remove(old)


def boolean_cut(obj, cutter, op='DIFFERENCE'):
    """Subtract a MeshBuilder (authored in world mm) from obj."""
    cut = cutter.build('_CUTTER', bpy.context.scene.collection, uv=False)
    cut.display_type = 'WIRE'
    m = obj.modifiers.new('BOOL', 'BOOLEAN')
    m.operation = op
    m.object = cut
    m.solver = 'EXACT'
    apply_modifiers(obj)
    me = cut.data
    bpy.data.objects.remove(cut)
    bpy.data.meshes.remove(me)
    REG.pop('_CUTTER', None)
    finish_mesh(obj)


def text_cutter(text, size, center, depth=0.7, facing='-Y', bold=False):
    """Return a MeshBuilder-like object (bpy mesh wrapped) that contains extruded text, centred at `center` (mm).
    facing '-Y' -> reads correctly from the machine's front; '+Y' -> from the back."""
    cu = bpy.data.curves.new('_txt', 'FONT')
    cu.body = text
    cu.size = size * MM
    cu.extrude = depth * MM
    cu.align_x = 'CENTER'
    cu.align_y = 'CENTER'
    cu.resolution_u = 4
    ob = bpy.data.objects.new('_txt', cu)
    bpy.context.scene.collection.objects.link(ob)
    rot = (math.radians(90), 0, 0) if facing == '-Y' else (math.radians(90), 0, math.pi)
    ob.rotation_euler = rot
    ob.location = mm(center)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    me.transform(ob.matrix_world)           # to world metres
    bpy.data.objects.remove(ob)
    bpy.data.curves.remove(cu)
    bm = bmesh.new()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    bmesh.ops.scale(bm, vec=Vector((1 / MM,) * 3), verts=bm.verts[:])   # back to mm so MeshBuilder works
    mb = MeshBuilder()
    mb.bm = bm
    return mb


# ----------------------------------------------------------------------------- hardware (instanced)
_HW_CACHE = {}


def _hw_mesh(key):
    """Hardware meshes are built with the fastener axis = +Z, head UNDERSIDE at z=0, shank pointing -Z."""
    if key in _HW_CACHE:
        return _HW_CACHE[key]
    kind = key[0]
    mb = MeshBuilder()
    if kind in ('pan', 'csk', 'cap'):
        _, d, L = key
        if kind == 'pan':
            hd, hh = d * 1.9, d * 0.62
            mb.cyl((0, 0, hh / 2), hd / 2, hh, seg=20, r2=hd / 2 * 0.86)
        elif kind == 'cap':
            hd, hh = d * 1.6, d
            mb.cyl((0, 0, hh / 2), hd / 2, hh, seg=20, r2=hd / 2 * 0.96)
        else:   # countersunk: head top flush with surface (z = 0), cone goes down
            hd, hh = d * 2.0, d * 0.55
            mb.cyl((0, 0, -hh / 2), d / 2, hh, seg=20, r2=hd / 2)
        mb.cyl((0, 0, -L / 2 - (hh if kind == 'csk' else 0)), d / 2 * 0.98,
               L - (0 if kind != 'csk' else 0), seg=12)
        top = None
        bm = mb.bm
        for f in bm.faces:
            if len(f.verts) == 20 and f.calc_center_median().z > (hh * 0.9 if kind != 'csk' else -0.01) and f.normal.z > 0.9:
                top = f
        if top is not None:
            bmesh.ops.inset_region(bm, faces=[top], thickness=(hd / 2) * (0.38 if kind != 'cap' else 0.45),
                                   depth=-(hh * 0.55))
    elif kind == 'nut':
        _, d = key
        mb.cyl((0, 0, d * 0.4), d * 0.99, d * 0.8, seg=6)
    elif kind == 'washer':
        _, d = key
        ro, ri, t = d * 1.0 + 1.0, d / 2 + 0.2, max(0.5, d * 0.18)
        mb.revolve([(ri, 0), (ro, 0), (ro, t), (ri, t)], seg=24)
    elif kind == 'standoff':
        _, d, L = key
        mb.cyl((0, 0, -L / 2), d / 2, L, seg=6)
    elif kind == 'foot':
        _, d, h = key
        mb.revolve([(d * 0.28, 0), (d / 2 - 1.5, 0), (d / 2, 1.5), (d / 2, h - 1.5), (d / 2 - 1.5, h), (d * 0.28, h)],
                   seg=36)
    mesh = mb.to_mesh('HW_' + '_'.join(str(k) for k in key), uv=False)
    _HW_CACHE[key] = mesh
    return mesh


def hardware(key, loc, direction, coll, name, parent=None):
    """Place an instanced fastener.  `direction` = outward normal of the surface it is fastened to."""
    mesh = _hw_mesh(key)
    o = bpy.data.objects.new(name, mesh)
    o.location = mm(loc)
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = axis_rot(direction).to_quaternion()
    coll.objects.link(o)
    if parent is not None:
        set_parent(o, parent)
    return o


def screws(spec, points, direction, coll, prefix, parent):
    """Place the same screw at many points (list of mm vectors)."""
    out = []
    for i, p in enumerate(points):
        out.append(hardware(spec, p, direction, coll, f'{prefix}_{i + 1:02d}', parent))
    return out


# ----------------------------------------------------------------------------- misc helpers
def poly_curve(name, pts, coll, parent=None, bevel=0.0, closed=False):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = bevel * MM
    cu.bevel_resolution = 3
    cu.use_fill_caps = True
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for p, q in zip(sp.points, pts):
        p.co = (q[0] * MM, q[1] * MM, q[2] * MM, 1.0)
    sp.use_cyclic_u = closed
    o = bpy.data.objects.new(name, cu)
    coll.objects.link(o)
    if parent is not None:
        set_parent(o, parent)
    REG[name] = o
    return o


def wire(name, pts, coll, parent=None, radius=0.9):
    """Smooth round wire: bezier spline with auto handles and real thickness."""
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = radius * MM
    cu.bevel_resolution = 3
    cu.resolution_u = 8
    cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER')
    sp.bezier_points.add(len(pts) - 1)
    for bp, q in zip(sp.bezier_points, pts):
        bp.co = (q[0] * MM, q[1] * MM, q[2] * MM)
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, cu)
    coll.objects.link(o)
    if parent is not None:
        set_parent(o, parent)
    REG[name] = o
    return o


def rotate_about(obj, pivot_world_mm, axis, deg):
    """Rotate a (parentless-transform) object about a world pivot - used for posing mechanisms."""
    R = Matrix.Rotation(math.radians(deg), 4, axis)
    P = Matrix.Translation(mm(pivot_world_mm))
    obj.matrix_world = P @ R @ P.inverted() @ obj.matrix_world


def clear_scene():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    for m in list(bpy.data.meshes):
        bpy.data.meshes.remove(m)
    for c in list(bpy.data.curves):
        bpy.data.curves.remove(c)
    REG.clear()
    ANCHORS.clear()
    _HW_CACHE.clear()


def setup_units():
    s = bpy.context.scene
    s.unit_settings.system = 'METRIC'
    s.unit_settings.scale_length = 1.0
    s.unit_settings.length_unit = 'MILLIMETERS'
    s.render.fps = 24
EOF
echo ok
Output

ok