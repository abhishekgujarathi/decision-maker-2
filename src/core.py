"""Small Blender geometry kernel used by the CC-01 assembly modules."""
import math
import bpy
import bmesh
from mathutils import Vector, Matrix

MM = 0.001

def m(v):
    return v * MM

def V(p):
    return Vector((p[0], p[1], p[2]))

def collection(name, parent=None):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in {(x.name) for x in (parent or bpy.context.scene.collection).children}:
        (parent or bpy.context.scene.collection).children.link(c)
    return c

def parent(obj, root):
    obj.parent = root
    obj.matrix_parent_inverse = root.matrix_world.inverted()

def mesh_object(name, verts, faces, coll, root=None):
    me = bpy.data.meshes.new(name + '_MESH')
    me.from_pydata([(x*MM, y*MM, z*MM) for x,y,z in verts], [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    if root: parent(ob, root)
    return ob

def bevel(obj, amount=1.0, segments=2):
    mod = obj.modifiers.new('manufactured_edge_rounds', 'BEVEL')
    mod.width, mod.segments = amount*MM, segments
    mod.limit_method = 'ANGLE'
    return obj

def box(name, center, size, coll, root=None, bevel_mm=0.0):
    cx,cy,cz = center; sx,sy,sz = size
    verts=[(cx+dx*sx/2,cy+dy*sy/2,cz+dz*sz/2) for dx,dy,dz in
           [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(4,0,3,7)]
    ob=mesh_object(name,verts,faces,coll,root)
    if bevel_mm: bevel(ob,bevel_mm,3)
    return ob

def cyl(name, center, radius, depth, coll, root=None, axis='Y', segments=32, bevel_mm=0.0):
    # local Z is depth, then orient it to the requested world axis.
    verts=[]; faces=[]
    for z in (-depth/2, depth/2):
        for i in range(segments):
            a=2*math.pi*i/segments; verts.append((radius*math.cos(a),radius*math.sin(a),z))
    faces.append(tuple(range(segments-1,-1,-1))); faces.append(tuple(range(segments,2*segments)))
    for i in range(segments):
        j=(i+1)%segments; faces.append((i,j,segments+j,segments+i))
    ob=mesh_object(name,verts,faces,coll,root)
    ob.location=V(center)*MM
    if axis=='X': ob.rotation_euler[1]=math.pi/2
    elif axis=='Y': ob.rotation_euler[0]=math.pi/2
    if bevel_mm: bevel(ob,bevel_mm,2)
    return ob

def sphere(name, center, radius, coll, root=None, segments=48, rings=24):
    verts=[]; faces=[]
    for j in range(rings+1):
        v=math.pi*j/rings
        for i in range(segments):
            a=2*math.pi*i/segments
            verts.append((center[0]+radius*math.sin(v)*math.cos(a), center[1]+radius*math.cos(v), center[2]+radius*math.sin(v)*math.sin(a)))
    for j in range(rings):
        for i in range(segments):
            ni=(i+1)%segments; a=j*segments+i; b=j*segments+ni; c=(j+1)*segments+ni; d=(j+1)*segments+i
            faces.append((a,b,c,d))
    return mesh_object(name,verts,faces,coll,root)

def prism(name, pts, depth, coll, root=None, bevel_mm=0.0):
    # polygon in XY, extruded along Z
    n=len(pts); verts=[(x,y,-depth/2) for x,y in pts]+[(x,y,depth/2) for x,y in pts]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    for i in range(n): faces.append((i,(i+1)%n,n+(i+1)%n,n+i))
    ob=mesh_object(name,verts,faces,coll,root)
    if bevel_mm: bevel(ob,bevel_mm,2)
    return ob

def sweep_tube(name, points, radius, coll, root=None, sides=12):
    """Round continuous tube along a polyline; useful for wires and rails."""
    rings=[]
    for i,p in enumerate(points):
        a=V(points[max(i-1,0)]); b=V(points[min(i+1,len(points)-1)])
        t=(b-a).normalized(); ref=Vector((0,0,1))
        if abs(t.dot(ref))>.92: ref=Vector((1,0,0))
        n=t.cross(ref).normalized(); q=t.cross(n).normalized()
        rings.append([(p[0]+radius*(n.x*math.cos(2*math.pi*k/sides)+q.x*math.sin(2*math.pi*k/sides)),
                      p[1]+radius*(n.y*math.cos(2*math.pi*k/sides)+q.y*math.sin(2*math.pi*k/sides)),
                      p[2]+radius*(n.z*math.cos(2*math.pi*k/sides)+q.z*math.sin(2*math.pi*k/sides))) for k in range(sides)])
    verts=[v for ring in rings for v in ring]; faces=[]
    for j in range(len(rings)-1):
        for i in range(sides): faces.append((j*sides+i,j*sides+(i+1)%sides,(j+1)*sides+(i+1)%sides,(j+1)*sides+i))
    faces += [tuple(range(sides-1,-1,-1)), tuple(range((len(rings)-1)*sides,len(rings)*sides))]
    return mesh_object(name,verts,faces,coll,root)

def fastener(name, center, coll, root=None, axis='Z', d=4.0, length=5.0):
    washer=cyl(name+'_WASHER',center,d*0.95,1.0,coll,root,axis,20,0.15)
    screw=cyl(name+'_SCREW',center,d*0.55,length,coll,root,axis,16,0.1)
    return washer, screw

def rotate_object(obj, axis, degrees):
    obj.rotation_mode='XYZ'; idx={'X':0,'Y':1,'Z':2}[axis]; obj.rotation_euler[idx]=math.radians(degrees)

def create_track_channel(name, points, coll, root, width=23.0, floor_t=1.5, wall_h=10.0, wall_t=1.5, cap_start=True, cap_end=True, tangent_points=None, point_offset=0):
    """Build floor and two side walls along a shared centerline.

    Internal named track pieces deliberately omit their end caps. Adjacent
    pieces share the same centerline sample and meet without overlapping cap
    plates; only the true route ends receive closure faces.
    """
    def ribbon(label, section):
        # section is a closed list of (lateral offset, depth offset) points.
        rings=[]
        frame_points = tangent_points or points
        for i,p in enumerate(points):
            frame_i = point_offset + i
            a=V(frame_points[max(0,frame_i-1)]); b=V(frame_points[min(len(frame_points)-1,frame_i+1)])
            t=(b-a).normalized(); side=Vector((-t.y,t.x,0)).normalized()
            rings.append([tuple(V(p)+side*s+Vector((0,0,z))) for s,z in section])
        n=len(section); vs=[v for ring in rings for v in ring]; fs=[]
        for j in range(len(rings)-1):
            for k in range(n): fs.append((j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k))
        if cap_start:
            fs.append(tuple(range(n-1,-1,-1)))
        if cap_end:
            fs.append(tuple(range((len(rings)-1)*n,len(rings)*n)))
        return mesh_object(name+'_'+label,vs,fs,coll,root)
    ribbon('FLOOR',[(-width/2,-floor_t/2),(width/2,-floor_t/2),(width/2,floor_t/2),(-width/2,floor_t/2)])
    ribbon('WALL_L',[(width/2,0),(width/2+wall_t,0),(width/2+wall_t,wall_h),(width/2,wall_h)])
    ribbon('WALL_R',[(-width/2-wall_t,0),(-width/2,0),(-width/2,wall_h),(-width/2-wall_t,wall_h)])
    return name


def loft_rect_shell(name, cx, zc, y0, y1, outer0, outer1, wall, coll, root=None, bevel_mm=0.0):
    """Hollow rectangular funnel/tube along local Y with real wall thickness.

    outer0/outer1 are (width_x, depth_z) of the OUTER rectangle at y0/y1.
    Opening is open at both ends; bore = outer - 2*wall.
    """
    def ring(y, w, d, off):
        hw, hd = w/2 - off, d/2 - off
        return [(cx-hw, y, zc-hd), (cx+hw, y, zc-hd), (cx+hw, y, zc+hd), (cx-hw, y, zc+hd)]
    verts = (ring(y0, *outer0, 0) + ring(y0, *outer0, wall) +
             ring(y1, *outer1, 0) + ring(y1, *outer1, wall))
    O0, I0, O1, I1 = 0, 4, 8, 12
    faces = []
    for k in range(4):
        j = (k+1) % 4
        faces.append((O0+k, O0+j, O1+j, O1+k))      # outer side
        faces.append((I0+j, I0+k, I1+k, I1+j))      # inner side
        faces.append((O1+k, O1+j, I1+j, I1+k))      # top ring
        faces.append((O0+j, O0+k, I0+k, I0+j))      # bottom ring
    ob = mesh_object(name, verts, faces, coll, root)
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data); bm.free()
    if bevel_mm: bevel(ob, bevel_mm, 2)
    return ob


def _fix_normals(ob):
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data); bm.free()

def extrude_y(name, pts_xz, y0, y1, coll, root=None, bevel_mm=0.0):
    """Closed (x,z) polygon extruded along local Y (vertical in the front elevation)."""
    n = len(pts_xz)
    verts = [(x, y0, z) for x, z in pts_xz] + [(x, y1, z) for x, z in pts_xz]
    faces = [tuple(range(n-1, -1, -1)), tuple(range(n, 2*n))]
    for i in range(n):
        j = (i+1) % n
        faces.append((i, j, n+j, n+i))
    ob = mesh_object(name, verts, faces, coll, root)
    _fix_normals(ob)
    if bevel_mm: bevel(ob, bevel_mm, 2)
    return ob

def ring_y(name, cx, cz, y0, y1, r_out, r_in, coll, root=None, segments=32, bevel_mm=0.0):
    """Hollow round tube along local Y (axis vertical). Bore = 2*r_in."""
    verts = []
    for y in (y0, y1):
        for r in (r_out, r_in):
            for i in range(segments):
                a = 2*math.pi*i/segments
                verts.append((cx + r*math.cos(a), y, cz + r*math.sin(a)))
    S = segments
    O0, I0, O1, I1 = 0, S, 2*S, 3*S
    faces = []
    for i in range(S):
        j = (i+1) % S
        faces += [(O0+i, O0+j, O1+j, O1+i), (I0+j, I0+i, I1+i, I1+j),
                  (O1+i, O1+j, I1+j, I1+i), (O0+j, O0+i, I0+i, I0+j)]
    ob = mesh_object(name, verts, faces, coll, root)
    _fix_normals(ob)
    if bevel_mm: bevel(ob, bevel_mm, 2)
    return ob


def set_origin(ob, center_mm):
    """Move the object origin to center_mm (local frame) without moving the geometry."""
    c = Vector(center_mm) * MM
    for v in ob.data.vertices:
        v.co -= c
    ob.data.update()
    ob.location = ob.location + c
    return ob

def cut_boxes(obj, boxes, solver='EXACT'):
    """Boolean-subtract axis-aligned boxes [(center_mm, size_mm), ...] from obj (slots/notches).

    Cutters share obj's parent and parent-inverse, are applied, then deleted.
    Call BEFORE adding a bevel modifier so the boolean is the first modifier.
    """
    # Blender 4.x/5.x renamed the legacy FAST Boolean solver to FLOAT.
    # Keep older callers working while using a solver accepted by current
    # Blender versions.
    solver = {'FAST': 'FLOAT'}.get(str(solver).upper(), solver)
    coll = obj.users_collection[0]
    for i, (cen, size) in enumerate(boxes):
        cutter = box(obj.name + '_CUT_%d' % i, cen, size, coll, None)
        cutter.parent = obj.parent
        cutter.matrix_parent_inverse = obj.matrix_parent_inverse.copy()
        mod = obj.modifiers.new('slot_cut', 'BOOLEAN')
        mod.object = cutter; mod.operation = 'DIFFERENCE'; mod.solver = solver
        with bpy.context.temp_override(object=obj, active_object=obj, selected_objects=[obj]):
            bpy.ops.object.modifier_apply(modifier=mod.name)
        me = cutter.data
        bpy.data.objects.remove(cutter, do_unlink=True)
        if me.users == 0: bpy.data.meshes.remove(me)
    return obj
