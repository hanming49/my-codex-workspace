"""Editable photo-guided mouse model for Blender 5.2.

Run with Blender --background --python mouse_build.py -- --stage 1|2|3.
The 1.00 x 0.59 x ~0.30 proportions are estimates, not measurements.
"""
import bpy
import math
import sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
BLENDER = Path('/workspace/blender-5.2.0-linux-x64/blender')
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
STAGE = int(args[args.index('--stage') + 1]) if '--stage' in args else 3

LENGTH = 1.0
WIDTH = 0.59
HEIGHT = 0.305
W_SCALE = WIDTH / 0.59
H_SCALE = HEIGHT / 0.305

WIDTH_KEYS = [(-.500,.202),(-.475,.239),(-.420,.267),(-.330,.282),(-.210,.276),
              (-.080,.262),(.045,.269),(.190,.291),(.295,.285),(.395,.250),
              (.465,.166),(.495,.045),(.500,.013)]
HEIGHT_KEYS = [(-.500,.148),(-.450,.161),(-.330,.181),(-.210,.204),(-.090,.241),
               (.045,.277),(.180,.305),(.275,.298),(.370,.261),(.450,.196),(.500,.118)]

def interp(keys, y):
    y = max(keys[0][0], min(keys[-1][0], y))
    for j in range(len(keys)-1):
        y0,v0=keys[j]; y1,v1=keys[j+1]
        if y <= y1:
            t=(y-y0)/(y1-y0)
            s0=(keys[min(j+1,len(keys)-1)][1]-keys[max(j-1,0)][1])/(keys[min(j+1,len(keys)-1)][0]-keys[max(j-1,0)][0])
            s1=(keys[min(j+2,len(keys)-1)][1]-keys[j][1])/(keys[min(j+2,len(keys)-1)][0]-keys[j][0])
            d=y1-y0
            return (2*t**3-3*t*t+1)*v0+(t**3-2*t*t+t)*d*s0+(-2*t**3+3*t*t)*v1+(t**3-t*t)*d*s1
    return keys[-1][1]

def w(y): return interp(WIDTH_KEYS, y)*W_SCALE
def h(y): return interp(HEIGHT_KEYS, y)*H_SCALE
def bottom(y): return (.025 + .003*math.cos(y*math.pi))*H_SCALE
def surface(x,y):
    q=min(.9999,abs(x)/max(.0001,w(y)))
    return bottom(y)+(h(y)-bottom(y))*(1+math.sqrt(max(0,1-q*q)))/2

def mat(name, rgb, rough=.55, metallic=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*rgb,1)
    m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Roughness'].default_value=rough
    p.inputs['Metallic'].default_value=metallic
    return m

def link_mesh(name, vertices, faces, coll, material):
    mesh=bpy.data.meshes.new(name+'_Mesh')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj=bpy.data.objects.new(name, mesh)
    coll.objects.link(obj)
    obj.data.materials.append(material)
    for p in mesh.polygons: p.use_smooth=True
    return obj

def add_grid(name, coll, material, ny, nx, func, thickness=0):
    v=[]; f=[]
    for j in range(ny+1):
        for k in range(nx+1):
            v.append(func(j/ny,k/nx))
    for j in range(ny):
        for k in range(nx):
            a=j*(nx+1)+k
            f.append((a,a+1,a+nx+2,a+nx+1))
    ob=link_mesh(name,v,f,coll,material)
    if thickness:
        so=ob.modifiers.new('Editable shell thickness','SOLIDIFY')
        so.thickness=thickness; so.offset=-1
    return ob

def curve(name, points, material, radius, coll, cyclic=False):
    cu=bpy.data.curves.new(name+'_Curve','CURVE'); cu.dimensions='3D'
    cu.resolution_u=16; cu.bevel_depth=radius; cu.bevel_resolution=3
    sp=cu.splines.new('POLY'); sp.points.add(len(points)-1)
    for p,co in zip(sp.points,points): p.co=(*co,1)
    sp.use_cyclic_u=cyclic
    ob=bpy.data.objects.new(name,cu); coll.objects.link(ob); cu.materials.append(material)
    return ob

def cube(name, loc, scale, material, coll, bevel=.003):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    ob=bpy.context.object; ob.name=name
    for c in list(ob.users_collection): c.objects.unlink(ob)
    coll.objects.link(ob)
    ob.dimensions=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(material)
    if bevel:
        mod=ob.modifiers.new('Soft machined edges','BEVEL'); mod.width=min(bevel,min(scale)*.33); mod.segments=3
        mod=ob.modifiers.new('Face weighted normals','WEIGHTED_NORMAL')
    return ob

def cylinder(name, loc, radius, depth, material, coll, vertices=64, axis='X'):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    ob=bpy.context.object; ob.name=name
    for c in list(ob.users_collection): c.objects.unlink(ob)
    coll.objects.link(ob)
    if axis=='X': ob.rotation_euler[1]=math.pi/2
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    ob.data.materials.append(material)
    for p in ob.data.polygons: p.use_smooth=True
    be=ob.modifiers.new('Rounded tire edges','BEVEL'); be.width=.003; be.segments=3
    return ob

def oval_button(name, xc, yc, halfx, halfy, zlift, material, coll, n=40):
    # Two concentric rings and a top cap keep the outline rounded and editable.
    rings=[]
    for rr,drop in [(1.0,.004),(.86,0)]:
        for i in range(n):
            a=2*math.pi*i/n; x=xc+halfx*rr*math.cos(a); y=yc+halfy*rr*math.sin(a)
            rings.append((x,y,surface(x,y)+zlift-drop))
    rings.append((xc,yc,surface(xc,yc)+zlift+.0005))
    faces=[]
    for i in range(n):
        nxt=(i+1)%n
        faces.append((i,nxt,n+nxt,n+i))
        faces.append((n+i,n+nxt,2*n))
    return link_mesh(name,rings,faces,coll,material)

def camera(name, xyz, target, ortho=False, scale=1.3):
    d=bpy.data.cameras.new(name); ob=bpy.data.objects.new(name,d); CAMS.objects.link(ob)
    ob.location=xyz
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    if ortho: d.type='ORTHO'; d.ortho_scale=scale
    else: d.lens=70
    d.clip_start=.01; d.clip_end=100
    return ob

def area(name, xyz, target, power, shape=(1,1)):
    d=bpy.data.lights.new(name,'AREA'); ob=bpy.data.objects.new(name,d); LIGHTS.objects.link(ob)
    ob.location=xyz; ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    d.energy=power; d.shape='RECTANGLE'; d.size=shape[0]; d.size_y=shape[1]

def render(name, cam, resolution=(800,600), samples=20):
    SCENE.camera=bpy.data.objects[cam]
    floor=bpy.data.objects.get('Studio_Floor')
    if floor: floor.hide_render=cam in {'Camera_Top','Camera_Left','Camera_Right','Camera_Front'}
    SCENE.render.resolution_x=resolution[0]; SCENE.render.resolution_y=resolution[1]
    SCENE.render.resolution_percentage=100
    SCENE.cycles.samples=samples
    SCENE.render.filepath=str(ROOT/name)
    bpy.ops.render.render(scene=SCENE.name, write_still=True)

if STAGE==1:
    # Keep the existing scene/data from desktop_house.blend. The mouse lives in a new scene.
    SCENE=bpy.data.scenes.new('Mouse_Product_Studio')
    if bpy.context.window: bpy.context.window.scene=SCENE
    old_scene_names=[s.name for s in bpy.data.scenes if s!=SCENE]
    SCENE['preserved_scenes']=', '.join(old_scene_names)
    SCENE['scale_note']='PHOTO ESTIMATE: length 1.00, max width 0.59, height ~0.305. No physical dimension measured.'
    SCENE.unit_settings.system='METRIC'
    SCENE.unit_settings.scale_length=1
    MOUSE=bpy.data.collections.new('Mouse_Model'); SCENE.collection.children.link(MOUSE)
    SHELL=bpy.data.collections.new('01_Shell'); MOUSE.children.link(SHELL)
    PARTS=bpy.data.collections.new('02_Controls'); MOUSE.children.link(PARTS)
    DETAILS=bpy.data.collections.new('03_Details'); MOUSE.children.link(DETAILS)
    HELPERS=bpy.data.collections.new('04_Construction'); MOUSE.children.link(HELPERS)
    STUDIO=bpy.data.collections.new('Studio'); SCENE.collection.children.link(STUDIO)
    CAMS=bpy.data.collections.new('Cameras'); STUDIO.children.link(CAMS)
    LIGHTS=bpy.data.collections.new('Lights'); STUDIO.children.link(LIGHTS)

    warm=mat('M_WarmWhite_Lower',(0.80,.79,.74),.48)
    upper=mat('M_PaleGrey_Upper',(.83,.85,.83),.58)
    dark=mat('M_Seams_Dark',(.042,.059,.062),.75)
    stage=mat('M_Studio_Clay',(.29,.34,.35),.78)

    # Ring-based closed shell. Y points from the low nose (-) to the rounded rear (+).
    N=64; K=48; vertices=[]; faces=[]
    for j in range(N+1):
        y=-.5+j/N
        for k in range(K):
            theta=2*math.pi*k/K
            vertices.append((w(y)*math.sin(theta),y,bottom(y)+(h(y)-bottom(y))*(1+math.cos(theta))/2))
    for j in range(N):
        for k in range(K):
            a=j*K+k; b=j*K+(k+1)%K
            faces.append((a,b,b+K,a+K))
    faces.append(tuple(reversed(range(K))))
    faces.append(tuple(N*K+k for k in range(K)))
    body=link_mesh('SM_LowerBody_EditableRings',vertices,faces,SHELL,warm)
    body['parameter_length']=LENGTH; body['parameter_width']=WIDTH; body['parameter_height']=HEIGHT
    body['parameter_status']='provisional estimate from five photos'

    # Top panel surfaces follow the same analytic crown as the side shell.
    def button_fn(sign):
        def f(t,q):
            yb=-.105+.016*q*q
            yf=-.494+.013*(1-q*q)
            y=yf+(yb-yf)*t
            x=sign*(.048+q*(.92*w(y)-.048))
            return (x,y,surface(x,y)+.0062)
        return f
    for sign,label in [(-1,'Left'),(1,'Right')]:
        add_grid('SM_'+label+'Click_EditableGrid',SHELL,upper,32,20,button_fn(sign),.002)
    def palm_fn(t,q):
        y0=-.096+.016*q*q; y=y0+(.495-y0)*t
        x=q*.92*w(y)
        return (x,y,surface(x,y)+.006)
    add_grid('SM_PalmShell_EditableGrid',SHELL,upper,45,40,palm_fn,.002)

    # Side shell panels terminate on a photographed, gently rising seam.
    for sign,label in [(-1,'Left'),(1,'Right')]:
        def side_fn(t,q,sign=sign):
            y=-.494+t*.987
            top=math.asin(.92)
            seam=.074+.27*(h(y)-.15)
            c=2*(seam-bottom(y))/(h(y)-bottom(y))-1
            end=math.acos(max(-1,min(1,c)))
            a=top+q*(end-top)
            return (sign*(w(y)*math.sin(a)+.006*math.sin(a)),y,
                    bottom(y)+(h(y)-bottom(y))*(1+math.cos(a))/2+.006*math.cos(a))
        add_grid('SM_'+label+'UpperSide',SHELL,upper,62,14,side_fn,.002)
        pts=[]
        for i in range(61):
            y=-.489+i*.977/60; seam=.074+.27*(h(y)-.15)
            a=math.acos(max(-1,min(1,2*(seam-bottom(y))/(h(y)-bottom(y))-1)))
            pts.append((sign*(w(y)+.008)*math.sin(a),y,seam+.008*math.cos(a)))
        curve('CRV_'+label+'SideSeam',pts,dark,.00155,DETAILS)

    # Stage silhouette preview has only separate main shells, no tiny details.
    floor=cube('Studio_Floor',(0,0,-.025),(200,200,.05),stage,STUDIO,0)
    camera('Camera_Top',(0,0,2.1),(0,0,.13),True,1.33)
    camera('Camera_Left',(-1.9,0,.31),(0,0,.16),True,1.32)
    camera('Camera_Right',(1.9,0,.31),(0,0,.16),True,1.32)
    camera('Camera_Front',(0,-1.8,.17),(0,0,.11),True,.95)
    camera('Camera_ThreeQuarter',(-1.25,-1.40,.93),(0,0,.14),False)
    area('Large_Key',(-.6,-.5,1.25),(0,0,.1),210,(1.5,1.0))
    area('Soft_Fill',(.8,-.05,.75),(0,0,.1),90,(1.2,.7))
    area('Rim',(0,.8,1.2),(0,0,.12),180,(1.0,.7))
    SCENE.world=bpy.data.worlds.new('Studio_Ambience')
    SCENE.world.use_nodes=True
    bg=next(n for n in SCENE.world.node_tree.nodes if n.type=='BACKGROUND')
    bg.inputs['Color'].default_value=(.72,.77,.78,1); bg.inputs['Strength'].default_value=.65
    SCENE.render.engine='CYCLES'; SCENE.cycles.device='CPU'
    SCENE.render.image_settings.file_format='PNG'
    SCENE.view_settings.view_transform='AgX'
    SCENE.render.film_transparent=False
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'mouse_stage1_grey.blend'))
    render('stage1_top.png','Camera_Top',(800,600),16)
    render('stage1_side.png','Camera_Left',(800,600),16)

else:
    SCENE=bpy.data.scenes['Mouse_Product_Studio']
    if bpy.context.window: bpy.context.window.scene=SCENE
    MOUSE=bpy.data.collections['Mouse_Model']; SHELL=bpy.data.collections['01_Shell']
    PARTS=bpy.data.collections['02_Controls']; DETAILS=bpy.data.collections['03_Details']
    HELPERS=bpy.data.collections['04_Construction']; STUDIO=bpy.data.collections['Studio']
    CAMS=bpy.data.collections['Cameras']; LIGHTS=bpy.data.collections['Lights']

if STAGE==2:
    bpy.data.objects['Camera_Top'].data.ortho_scale=1.55
    bpy.data.objects['Camera_ThreeQuarter'].data.lens=62
    # The reference is a cool grey shell in diffuse room light; hold the whites below clipping.
    mat('M_PaleGrey_Upper',(.71,.735,.735),.58)
    mat('M_WarmWhite_Lower',(.79,.78,.73),.48)
    SCENE.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.42
    bpy.data.objects['Large_Key'].data.energy=115
    bpy.data.objects['Soft_Fill'].data.energy=54
    bpy.data.objects['Rim'].data.energy=95
    SCENE.view_settings.exposure=-.75
    upper=bpy.data.materials['M_PaleGrey_Upper']
    dark=bpy.data.materials['M_Seams_Dark']
    trim=mat('M_CentralTrim_Gloss',(.89,.89,.82),.28)
    wheelmat=mat('M_Wheel_Rubber',(.81,.79,.68),.68)
    groove=mat('M_Wheel_Grooves',(.53,.51,.42),.83)
    buttonmat=mat('M_TopButton',(.82,.84,.80),.33)
    portmat=mat('M_Port_Recess',(.020,.025,.025),.74)
    metal=mat('M_Port_Inner',(.28,.31,.29),.35,.2)
    # Concealed hinge roots connect both movable click caps to the core.
    for sign,label in [(-1,'Left'),(1,'Right')]:
        xx=sign*.16; yy=-.15
        verts=[]
        for dz in (-.009,.003):
            for x,y in [(xx-.010,yy-.011),(xx+.010,yy-.011),
                        (xx+.010,yy+.011),(xx-.010,yy+.011)]:
                # Sloped upper face meets the click cap without a coplanar patch.
                tilt=.002*(y-yy)/.011 if dz>0 else 0
                verts.append((x,y,surface(x,y)+dz+tilt))
        faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
        link_mesh('SM_'+label+'Click_HingeRoot',verts,faces,PARTS,upper)

    # Separate dark line under the curved button/palm boundary.
    for sign,label in [(-1,'Left'),(1,'Right')]:
        points=[]
        for i in range(29):
            q=i/28; y=-.100+.016*q*q
            x=sign*(.047+q*(.92*w(y)-.047))
            points.append((x,y,surface(x,y)+.005))
        curve('CRV_'+label+'ButtonRearGap',points,dark,.0022,DETAILS)
    points=[]
    for i in range(35):
        y=-.492+i*.39/34
        points.append((0,y,surface(0,y)+.0053))
    curve('CRV_CenterButtonGap',points,dark,.0017,DETAILS)

    # Central glossy strip is one editable mesh containing the front bridge, rails and rounded rear.
    v=[]; f=[]
    def patch(ny,nx,fun):
        offset=len(v)
        for j in range(ny+1):
            for k in range(nx+1): v.append(fun(j/ny,k/nx))
        for j in range(ny):
            for k in range(nx):
                a=offset+j*(nx+1)+k; f.append((a,a+1,a+nx+2,a+nx+1))
    def panel(y0,y1,x0,x1):
        patch(12,5,lambda t,q:(x0+(x1-x0)*q,y0+(y1-y0)*t,surface(x0+(x1-x0)*q,y0+(y1-y0)*t)+.012))
    panel(-.482,-.431,-.049,.049)
    panel(-.431,-.260,-.050,-.034)
    panel(-.431,-.260,.034,.050)
    def rear(t,q):
        y=-.260+t*.333
        taper=1 if y<.028 else max(.09,math.sqrt(max(0,1-((y-.028)/.047)**2)))
        x=(q*2-1)*.05*taper
        return (x,y,surface(x,y)+.012)
    patch(26,12,rear)
    tr=link_mesh('SM_CentralGlossTrim_Editable',v,f,PARTS,trim)
    sol=tr.modifiers.new('Trim wall thickness','SOLIDIFY'); sol.thickness=.002; sol.offset=-1

    # Dark well around a partly submerged wheel; supports give it visible wall depth.
    cube('SM_WheelWell_Recess',(0,-.348,.171),(.068,.180,.024),dark,PARTS,.008)
    cube('SM_WheelWell_InnerFloor',(0,-.348,.161),(.060,.161,.009),portmat,PARTS,.005)
    cylinder('SM_ScrollWheel',(0,-.351,.172),.040,.052,wheelmat,PARTS,64)
    # Short diagonal tread cuts arch over the wheel's visible crown.
    for j in range(11):
        angle=.28+j*.245
        if angle>2.79: break
        pts=[]
        for k in range(9):
            xx=-.026+k*.052/8
            a=angle+.38*(xx/.026)
            pts.append((xx,-.351+.0405*math.cos(a),.172+.0405*math.sin(a)))
        curve(f'CRV_WheelTread_{j:02d}',pts,groove,.00085,DETAILS)
    oval_button('SM_TopModeButton',0,-.153,.028,.033,.014,buttonmat,PARTS)

    # Left side keys: long tapered capsules on the warm-white lower band.
    for idx,(yy,zz) in enumerate([(-.104,.103),(.090,.127)],1):
        x=-w(yy)*.955-.002
        b=cube(f'SM_LeftSideButton_{idx}',(x,yy,zz),(.013,.130,.026),buttonmat,PARTS,.011)
        b.rotation_euler[0]=math.radians(-7)
    # Front USB opening is a real Boolean in the lower shell plus an extruded lip and recess.
    cut=cube('CONSTRUCTION_PortBoolean',(0,-.491,.070),(.092,.087,.028),portmat,HELPERS,.008)
    cut.hide_render=True; cut.hide_set(True)
    body=bpy.data.objects['SM_LowerBody_EditableRings']
    bo=body.modifiers.new('Editable USB-C opening','BOOLEAN'); bo.operation='DIFFERENCE'
    bo.solver='EXACT'; bo.object=cut
    def rr(hw,hh,r):
        pts=[]
        for cx,cz,start in [(hw-r,hh-r,0),(-hw+r,hh-r,90),(-hw+r,-hh+r,180),(hw-r,-hh+r,270)]:
            for i in range(5):
                a=math.radians(start+i*90/4)
                pts.append((cx+r*math.cos(a),cz+r*math.sin(a)))
        return pts
    outer=rr(.056,.019,.011); inner=rr(.041,.011,.007)
    rings=[]
    for y,poly in [(-.507,outer),(-.508,inner),(-.470,inner),(-.470,outer)]:
        rings.extend([(x,y,.071+z) for x,z in poly])
    n=len(outer); faces=[]
    for ring in range(4):
        for k in range(n):
            a=ring*n+k; b=ring*n+(k+1)%n; next_ring=(ring+1)%4
            faces.append((a,b,next_ring*n+(k+1)%n,next_ring*n+k))
    lip=link_mesh('SM_FrontPort_ExtrudedBezel',rings,faces,PARTS,portmat)
    cube('SM_PortInnerRecess',(0,-.450,.071),(.079,.015,.019),portmat,PARTS,.005)
    cube('SM_PortTongue',(0,-.472,.068),(.057,.050,.005),metal,PARTS,.002)

    # The photographed black geometric spider is line geometry fitted to the crown.
    logo=mat('M_BlackGeometricLogo',(.013,.021,.024),.42)
    strokes=[[(0,.286),(-.013,.266),(-.012,.239),(0,.219),(.012,.239),(.013,.266),(0,.286)],
             [(-.009,.285),(-.032,.304),(-.061,.302),(-.067,.285),(-.038,.290),(-.016,.274)],
             [(-.015,.269),(-.063,.277),(-.048,.253),(-.022,.255)],
             [(-.018,.250),(-.052,.245),(-.034,.220),(-.011,.232)],
             [(-.008,.279),(-.003,.304)],
             [(-.003,.273),(0,.246),(.003,.273)]]
    for idx,stroke in enumerate(strokes):
        for mirror in ([1] if idx==0 else [-1,1]):
            coords=[]
            for x,y in stroke:
                xx=x*mirror
                coords.append((xx,y,surface(xx,y)+.0069))
            curve(f'CRV_Logo_{idx}_{mirror}',coords,logo,.0019,DETAILS)

    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'mouse_stage2_parts.blend'))
    render('stage2_top.png','Camera_Top',(800,600),18)
    render('stage2_three_quarter.png','Camera_ThreeQuarter',(800,600),18)

if STAGE==3:
    # Small material distinctions are judged under broad softboxes.
    mat('M_PaleGrey_Upper',(.43,.46,.47),.59)
    mat('M_WarmWhite_Lower',(.58,.57,.54),.46)
    mat('M_CentralTrim_Gloss',(.66,.66,.62),.25)
    mat('M_Wheel_Rubber',(.62,.60,.54),.68)
    mat('M_BlackGeometricLogo',(.0005,.0006,.0007),1.0)
    for idx,yy in enumerate([-.104,.090],1):
        bpy.data.objects[f'SM_LeftSideButton_{idx}'].location.x=-w(yy)-.003
    # The simplified underside rests on Z=0; move the complete editable asset together.
    for ob in MOUSE.all_objects:
        ob.location.z-=.025
    # Studio settings are retained in the file. No external image textures are used.
    SCENE['unobserved_parts']='Underside and port internals are simplified/provisional; no unseen mechanisms modeled.'
    SCENE['reference_views']='Five user-supplied photos: front, high oblique, left profile, top, left three-quarter.'
    SCENE['texture_pack']='All materials and logo geometry are internal; no external textures.'
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'photo_mouse_editable.blend'))
    render('mouse_top.png','Camera_Top',(1200,900),52)
    render('mouse_left_side.png','Camera_Left',(1200,900),52)
    render('mouse_three_quarter.png','Camera_ThreeQuarter',(1200,900),52)
    render('mouse_front.png','Camera_Front',(1000,750),36)
    render('mouse_right_side.png','Camera_Right',(1000,750),36)
    SCENE.camera=bpy.data.objects['Camera_ThreeQuarter']
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'photo_mouse_editable.blend'))
    mesh_objects=[o for o in MOUSE.all_objects if o.type=='MESH' and not o.name.startswith('CONSTRUCTION')]
    print('MODEL_SUMMARY', {'meshes':len(mesh_objects), 'materials':len(bpy.data.materials),
                           'body_dimensions':tuple(round(x,4) for x in bpy.data.objects['SM_LowerBody_EditableRings'].dimensions),
                           'faces':sum(len(o.data.polygons) for o in mesh_objects)})
