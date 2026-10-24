import bpy,math,os
from mathutils import Vector
from pathlib import Path
R=Path(__file__).parent
s=bpy.data.scenes.new('Chibi_Reference_Character');bpy.context.window.scene=s
C=bpy.data.collections.new('Character_Editable');s.collection.children.link(C)
T=bpy.data.collections.new('Presentation');s.collection.children.link(T)
def mat(n,c,r=.8):
 m=bpy.data.materials.get(n) or bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=r;return m
skin=mat('Skin_WarmCream',(.88,.77,.64));hair=mat('Hair_SageGrey',(.59,.68,.55));dark=mat('Ink_SoftCharcoal',(.065,.068,.056));white=mat('Ivory_CollarAndSocks',(.91,.89,.79));navy=mat('Dress_NavyPlaid',(.055,.067,.105));iris=mat('Eyes_LightBrown',(.42,.27,.17));glint=mat('Eye_CreamHighlights',(.99,.93,.80));shoe=mat('Shoes_CharcoalBrown',(.07,.065,.055))
def link(o,n,m,coll=C):
 o.name=n
 for col in list(o.users_collection):col.objects.unlink(o)
 coll.objects.link(o);o.data.materials.append(m);return o
def uv(n,loc,scale,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=24,location=loc);o=link(bpy.context.object,n,m);o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for p in o.data.polygons:p.use_smooth=True
 return o
def mesh(n,v,f,m):
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);C.objects.link(o);me.materials.append(m)
 for p in me.polygons:p.use_smooth=True
 return o
def line(n,pts,m,rad=.008,cyclic=False):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.bevel_depth=rad;cu.bevel_resolution=3;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,v in zip(sp.points,pts):p.co=(*v,1)
 sp.use_cyclic_u=cyclic;o=bpy.data.objects.new(n,cu);C.objects.link(o);cu.materials.append(m);return o
def loft(n,sections,m,pleats=0):
 v=[];f=[];K=64
 for z,rx,ry in sections:
  for k in range(K):
   a=2*math.pi*k/K;rr=1+pleats*math.cos(a*12);v.append((rx*math.cos(a)*rr,ry*math.sin(a)*rr,z))
 for j in range(len(sections)-1):
  for k in range(K):
   a=j*K+k;b=j*K+(k+1)%K;f.append((a,b,b+K,a+K))
 f.extend([tuple(reversed(range(K))),tuple((len(sections)-1)*K+k for k in range(K))]);return mesh(n,v,f,m)
def strand(n,points,widths,depths,m=hair):
 v=[];f=[];K=12
 # Catmull-Rom interpolation of editable hair control stations.
 for j in range(len(points)-1):
  for step in range(8):
   t=step/8;inds=[max(j-1,0),j,j+1,min(j+2,len(points)-1)]
   def interp(vals):
    a,b,c,d=[vals[i] for i in inds];return .5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)
   p=interp([Vector(x) for x in points]);w=max(.001,interp(widths));d=max(.001,interp(depths))
   for k in range(K):
    a=2*math.pi*k/K;v.append(tuple(p+Vector((w*math.cos(a),d*math.sin(a),0))))
 p=Vector(points[-1]);v.extend(tuple(p+Vector((.001*math.cos(2*math.pi*k/K),.001*math.sin(2*math.pi*k/K),0))) for k in range(K))
 N=len(v)//K
 for j in range(N-1):
  for k in range(K):
   a=j*K+k;b=j*K+(k+1)%K;f.append((a,b,b+K,a+K))
 f.extend([tuple(reversed(range(K))),tuple((N-1)*K+k for k in range(K))]);return mesh(n,v,f,m)
# Face is broad, with a shallower front-to-back dimension.
head=uv('Head_Editable',(0,0,1.49),(.49,.345,.435),skin)
uv('Neck',(0,0,1.045),(.10,.09,.14),skin)
loft('Torso_Dress',[(.65,.23,.145),(.81,.205,.15),(.96,.20,.135),(1.04,.13,.10)],navy)
loft('Skirt_Main',[(.45,.30,.20),(.49,.31,.20),(.65,.245,.165),(.79,.21,.15)],navy,.035)
loft('Skirt_LowerRuffle',[(.385,.35,.235),(.405,.355,.24),(.45,.31,.21),(.49,.295,.20)],navy,.045)
loft('Waist_Belt',[(.765,.218,.159),(.805,.218,.159)],navy)
for sign,label in [(-1,'L'),(1,'R')]:
 uv('Leg_'+label,(sign*.145,.005,.26),(.071,.072,.18),skin)
 uv('Sock_'+label,(sign*.145,-.008,.105),(.076,.079,.065),white)
 uv('Shoe_'+label,(sign*.145,-.044,.048),(.085,.125,.049),shoe)
 strand('Sleeve_'+label,[(sign*.16,0,.99),(sign*.235,0,.88),(sign*.285,-.015,.72),(sign*.29,-.025,.67)],[.083,.077,.078,.07],[.086,.082,.075,.07],navy)
 uv('Cuff_'+label,(sign*.291,-.027,.661),(.080,.075,.043),white)
 uv('Hand_'+label,(sign*.30,-.03,.585),(.055,.047,.085),skin)
 uv('Thumb_'+label,(sign*.255,-.060,.60),(.022,.022,.038),skin)
 uv('Ear_'+label,(sign*.472,.015,1.38),(.065,.045,.084),skin)
# Rounded crown with opening around forehead and face; full back coverage.
v=[];f=[];K=96;N=28
for j in range(N+1):
 for k in range(K):
  a=2*math.pi*k/K;front=(1-math.sin(a))/2
  limit=2.10-.86*(front**3)
  t=.015+(limit-.015)*j/N
  v.append((.515*math.sin(t)*math.cos(a),.015+.375*math.sin(t)*math.sin(a),1.52+.455*math.cos(t)))
for j in range(N):
 for k in range(K):
  a=j*K+k;b=j*K+(k+1)%K;f.append((a,b,b+K,a+K))
cap=mesh('Hair_Crown',v,f,hair);so=cap.modifiers.new('Hair shell thickness','SOLIDIFY');so.thickness=.016
# Broad back locks, deliberately separated into editable masses.
for i,x in enumerate([-.40,-.27,-.135,0,.135,.27,.40]):
 yy=.18+.14*(1-abs(x)/.44)
 strand('Hair_BackLock_%02d'%i,[(x,yy,1.65),(x*1.1,yy+.035,1.35),(x*1.15,yy+.04,1.04),(x*1.18+.025,yy+.015,.84)],[.105,.115,.105,.001],[.105,.105,.075,.001])
for sign,label in [(-1,'L'),(1,'R')]:
 strand('Hair_SideLock_'+label,[(sign*.34,-.18,1.83),(sign*.43,-.285,1.57),(sign*.43,-.28,1.28),(sign*.36,-.23,1.10)],[.085,.057,.047,.001],[.085,.047,.035,.001])
# Lighting and inspection cameras.
def camera(n,pos,target=(0,0,1.0)):
 d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);T.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=2.35;return o
cams={n:camera('Camera_'+n,p) for n,p in [('front',(0,-5,1.1)),('side',(5,0,1.1)),('back',(0,5,1.1)),('three_quarter',(3,-5,2.2))]}
def area(n,pos,power,size):
 d=bpy.data.lights.new(n,'AREA');o=bpy.data.objects.new(n,d);T.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler();d.energy=power;d.shape='DISK';d.size=size
area('Key',(-3,-4,5),350,4);area('Fill',(3,-2,3),200,4);area('Rim',(0,3,4),250,3)
s.world=bpy.data.worlds.new('Soft_Studio');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.65,.69,.73,1);s.world.node_tree.nodes.get('Background').inputs[1].default_value=.7
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=900;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
def render(name,view):
 s.camera=cams[view];s.render.filepath=str(R/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'stage1_blockout.blend'))
render('stage1_front','front');render('stage1_side','side')
