"""Procedural material library for the CC-01 presentation scene."""
import bpy

def _input(node, *names):
    for name in names:
        if name in node.inputs:
            return node.inputs[name]

def _principled(name, color, roughness, metallic=0.0):
    mat=bpy.data.materials.new(name); mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF')
    _input(bsdf,'Base Color').default_value=(*color,1)
    _input(bsdf,'Roughness').default_value=roughness
    _input(bsdf,'Metallic').default_value=metallic
    return mat

def create_materials():
    mats={
        'CHARCOAL':_principled('MAT_CHARCOAL',(0.10,0.12,0.15),.42,.12),
        'RUBBER':_principled('MAT_EPDM_RUBBER',(0.008,0.009,0.010),.78),
        'STEEL':_principled('MAT_POLISHED_STEEL',(.70,.74,.78),.14,.92),
        'METAL':_principled('MAT_BRUSHED_STAINLESS',(.62,.67,.72),.25,.88),
        'AMBER':_principled('MAT_AMBER_INDICATOR',(.32,.055,.006),.22,.05),
        'GLASS':_principled('MAT_LOW_IRON_GLASS',(.92,.97,1.0),.08),
        'BACKDROP':_principled('MAT_BACKDROP',(.075,.090,.115),.58,.05),
    }
    bsdf=mats['GLASS'].node_tree.nodes.get('Principled BSDF'); tr=_input(bsdf,'Transmission Weight','Transmission')
    if tr: tr.default_value=1.0
    _input(bsdf,'IOR').default_value=1.45
    amber=mats['AMBER'].node_tree.nodes.get('Principled BSDF'); em=_input(amber,'Emission Color','Emission')
    if em: em.default_value=(1.0,.08,.005,1)
    strength=_input(amber,'Emission Strength')
    if strength: strength.default_value=2.0

    wood=bpy.data.materials.new('MAT_WALNUT_PROCEDURAL'); wood.use_nodes=True
    nt=wood.node_tree; bsdf=nt.nodes.get('Principled BSDF')
    noise=nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=3.2; noise.inputs['Detail'].default_value=5.0
    wave=nt.nodes.new('ShaderNodeTexWave'); wave.wave_type='BANDS'; wave.bands_direction='X'; wave.inputs['Scale'].default_value=7.0; wave.inputs['Distortion'].default_value=6.0
    ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color=(.012,.003,.001,1); ramp.color_ramp.elements[1].color=(.20,.055,.018,1)
    nt.links.new(noise.outputs['Fac'],ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'],bsdf.inputs['Base Color']); _input(bsdf,'Roughness').default_value=.34
    mats['WALNUT']=wood
    return mats

def assign(obj, material):
    if hasattr(obj.data,'materials'):
        if obj.data.materials: obj.data.materials[0]=material
        else: obj.data.materials.append(material)

def assign_by_role(mats, objects):
    for obj in objects:
        n=obj.name.upper()
        if n.startswith('WALNUT_') or n.startswith('BASE_SIDE_'): key='WALNUT'
        elif 'GLASS' in n or 'WINDOW' in n: key='GLASS'
        elif 'BACKING' in n: key='CHARCOAL'
        elif 'GASKET' in n or 'RUBBER' in n or 'FOOT' in n: key='RUBBER'
        elif 'BALL' in n or 'DIVERTER' in n or 'PIVOT_SHAFT' in n: key='STEEL'
        elif 'LABEL' in n: key='STEEL'
        elif 'NAMEPLATE' in n: key='CHARCOAL'
        elif 'INDICATOR' in n: key='AMBER'
        elif 'ELECTRONICS' in n or 'BOARD' in n or 'DRIVER' in n or 'SUPPLY' in n: key='CHARCOAL'
        elif 'FASTENER' in n or 'SCREW' in n or 'WASHER' in n: key='STEEL'
        elif n.startswith('REAR_') or n.startswith('VENT_') or n.startswith('POWER_') or n.startswith('MAIN_SWITCH'): key='METAL'
        else: key='METAL'
        assign(obj,mats[key])
