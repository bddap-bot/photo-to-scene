import bpy
import math


def build(entry, collection=None):
    collection = collection or bpy.context.collection
    ident = entry['id']
    shape = entry.get('shape', 'box')
    note = (entry.get('material_note', '') + ' ' + entry.get('label', '')).lower()
    x, y, z = [entry['bbox']['max'][i] - entry['bbox']['min'][i] for i in range(3)]
    made = []
    def mat(name, color, rough=.7, metal=0, glow=None):
        m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
        m.use_nodes = True
        p = m.node_tree.nodes.get('Principled BSDF')
        p.inputs['Base Color'].default_value = (*color, 1)
        p.inputs['Roughness'].default_value = rough
        p.inputs['Metallic'].default_value = metal
        if glow and 'Emission Color' in p.inputs:
            p.inputs['Emission Color'].default_value = (*glow, 1)
            p.inputs['Emission Strength'].default_value = 2
        if any(k in note for k in ('fabric','cloth','textile','fur','rug','upholstery')):
            n = m.node_tree.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 90
            b = m.node_tree.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value = .2; b.inputs['Distance'].default_value = .001
            m.node_tree.links.new(n.outputs['Fac'], b.inputs['Height']); m.node_tree.links.new(b.outputs['Normal'], p.inputs['Normal'])
        return m
    if ident == 'tv': base = mat('TV luminous screen', (.015,.02,.025), .18, 0, (.12,.24,.38))
    elif any(k in note for k in ('black','dark','metal')): base = mat('Charcoal metal', (.025,.027,.03), .38, .18)
    elif any(k in note for k in ('wood','oak','brown')): base = mat('Warm walnut and brown', (.19,.055,.018), .67)
    elif any(k in note for k in ('white','cream','pale')): base = mat('Warm cream', (.65,.57,.45), .77)
    elif 'green' in note: base = mat('Muted green', (.09,.16,.045), .8)
    else: base = mat('Household neutral', (.23,.15,.085), .72)
    def cube(name, lo, hi, bevel=0, material=base):
        bpy.ops.mesh.primitive_cube_add(size=1, location=tuple((lo[i]+hi[i])/2 for i in range(3)))
        o=bpy.context.object; o.name=name; o.dimensions=tuple(max(.001,hi[i]-lo[i]) for i in range(3)); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        if bevel:
            q=o.modifiers.new('edge softness','BEVEL'); q.width=min(bevel,min(o.dimensions)*.12); q.segments=2
        o.data.materials.append(material); made.append(o); return o
    def cyl(name,radius,depth,loc,material=base,vertices=32):
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc)
        o=bpy.context.object;o.name=name;o.data.materials.append(material);made.append(o);return o
    if shape == 'table':
        cube(ident+' top',(0,0,z*.9),(x,y,z),.006)
        for xx in (x*.04,x*.9):
            for yy in (y*.04,y*.86): cube(ident+' leg',(xx,yy,0),(xx+x*.06,yy+y*.1,z*.91),.003)
    elif shape == 'chair':
        cube(ident+' seat',(0,0,z*.42),(x,y,z*.52),.008); cube(ident+' back',(0,y*.88,z*.48),(x,y,z),.008)
        for xx in (x*.05,x*.87):
            for yy in (y*.06,y*.82): cube(ident+' leg',(xx,yy,0),(xx+x*.08,yy+y*.08,z*.45),.003)
    elif shape == 'barrel':
        wood=mat('Barrel oak',(.24,.07,.016),.62);iron=mat('Barrel hoops',(.03,.032,.035),.3,.7);r=min(x,y)*.42
        cyl(ident+' solid body',r*.94,z,(x/2,y/2,z/2),wood,48)
        for j in range(20):
            a=math.tau*j/20;cyl(ident+' stave',r*.075,z,(x/2+r*math.cos(a),y/2+r*math.sin(a),z/2),wood,8)
        for zz in (.08,.25,.5,.75,.92):
            bpy.ops.mesh.primitive_torus_add(major_radius=r,minor_radius=max(.005,r*.025),major_segments=48,location=(x/2,y/2,z*zz));o=bpy.context.object;o.data.materials.append(iron);made.append(o)
    elif shape == 'basket':
        plastic=mat('Basket cream plastic',(.72,.62,.46),.6);cube(ident+' base',(0,0,0),(x,y,z*.12),.006,plastic)
        for j in range(10):
            xx=x*j/9;cube(ident+' rib',(xx,0,z*.1),(min(x,xx+x*.035),y*.06,z),.002,plastic);cube(ident+' rib',(xx,y*.94,z*.1),(min(x,xx+x*.035),y,z),.002,plastic)
        for zz in (.12,.34,.56,.78,.93):
            cube(ident+' rail',(0,0,z*zz),(x,y*.06,min(z,z*(zz+.07))),.002,plastic);cube(ident+' rail',(0,y*.94,z*zz),(x,y,min(z,z*(zz+.07))),.002,plastic)
    elif shape == 'window':
        trim=mat('Window trim',(.75,.72,.65),.55);glass=mat('Window daylight',(.30,.45,.56),.25,0,(.22,.35,.45));cube(ident+' glass',(x*.05,y*.46,z*.05),(x*.95,y*.54,z*.95),0,glass)
        for lo,hi in [((0,0,0),(x*.055,y,z)),((x*.945,0,0),(x,y,z)),((0,0,0),(x,y,z*.05)),((0,0,z*.95),(x,y,z)),((0,0,z*.43),(x,y,z*.455))]: cube(ident+' frame',lo,hi,.002,trim)
    elif shape == 'fireplace':
        cube(ident+' left',(0,0,0),(x*.26,y,z),.004);cube(ident+' right',(x*.74,0,0),(x,y,z),.004);cube(ident+' lintel',(x*.26,0,z*.7),(x*.74,y,z),.004);cube(ident+' base',(x*.26,0,0),(x*.74,y,z*.12),.004)
    elif shape == 'pelt':
        profile=[(0,.72),(.08,.83),(.18,1),(.28,.84),(.68,.82),(.91,.97),(1,.82),(.94,.56),(1,.4),(.92,.2),(1,0),(.78,.15),(.48,.13),(.24,.07),(.29,.27),(.05,.37)]
        verts=[(0,xx*y,zz*z) for xx,zz in profile]+[(x,xx*y,zz*z) for xx,zz in profile];n=len(profile);faces=[tuple(range(n)),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
        me=bpy.data.meshes.new(ident);me.from_pydata(verts,[],faces);o=bpy.data.objects.new(ident,me);collection.objects.link(o);o.data.materials.append(mat('Mottled pelt fur',(.18,.075,.022),.95));made.append(o)
    elif shape in ('cylinder','ring'): cyl(ident,min(x,y)/2,z,(x/2,y/2,z/2),base,32)
    elif ident.endswith('_blind'):
        cube(ident,(0,0,0),(x,y,z),.001)
        for j in range(14): cube(ident+' pleat',(0,0,z*j/14),(x,y*1.2,z*(j+.12)/14),0)
    else: cube(ident,(0,0,0),(x,y,z),min(.004,min(x,y,z)*.06))
    return made
