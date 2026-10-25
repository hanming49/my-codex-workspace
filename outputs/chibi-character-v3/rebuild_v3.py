import bpy, math, bmesh, json, sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).parent
s=bpy.data.scenes['Chibi_Reference_Character'];bpy.context.window.scene=s
C=bpy.data.collections['Character_Editable'];HC=bpy.data.collections['02_Hair'];FC=bpy.data.collections['01_Head_Face']
hair=bpy.data.materials['Hair_SageGrey']
for o in list(HC.objects):bpy.data.objects.remove(o,do_unlink=True)
def mesh(name,vs,fs,sub=0):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update()
 ob=bpy.data.objects.new(name,me);HC.objects.link(ob);me.materials.append(hair)
 for p in me.polygons:p.use_smooth=True
 if sub:
  m=ob.modifiers.new('Editable smooth surface','SUBSURF');m.levels=sub;m.render_levels=sub
 return ob

def surface(name,fn,nu,nv,thick=.008):
 vs=[fn(i/nu,j/nv) for i in range(nu+1) for j in range(nv+1)]
 fs=[]
 for i in range(nu):
  for j in range(nv):
   a=i*(nv+1)+j;fs.append((a,a+1,a+nv+2,a+nv+1))
 ob=mesh(name,vs,fs)
 m=ob.modifiers.new('Editable thickness','SOLIDIFY');m.thickness=thick;m.offset=-1
 return ob

def ss(t):return t*t*(3-2*t)
def sp(x,p):return math.copysign(abs(x)**p,x)
# Smaller, softly squared face: straightened cheeks and shallow curved chin.
head=bpy.data.objects['Head_Editable']
for v in head.data.vertices:
 x,y,z=v.co;v.co=(.45*sp(x/.5145,.82),y*.94,.37*sp(z/.40,.72))
head.location.z=1.44

def face_y(x,z,off):
 return -.2726*max(.012,1-abs(x/.45)**(2/.82)-abs((z-1.44)/.37)**(2/.576))**.26-off
for ob in FC.objects:
 if ob.name.startswith('Eye_') and ob.type=='MESH':
  off=next(v for k,v in {'Outline':.004,'Ivory':.006,'Iris':.008,'Pupil':.010,'Glint':.012}.items() if k in ob.name)
  for v in ob.data.vertices:
   v.co.x*=.88;v.co.z=1.44+(v.co.z-1.47)*.92;v.co.y=face_y(v.co.x,v.co.z,off)
 if ob.type=='CURVE' and ob.name.startswith(('UpperLid','Brow','Mouth')):
  for spline in ob.data.splines:
   for p in spline.points:
    p.co.x*=.88;p.co.z=1.44+(p.co.z-1.47)*.92;p.co.y=face_y(p.co.x,p.co.z,.012)
 if ob.name.startswith('Ear_'):
  ob.location.x*=.87;ob.location.y=-.12;ob.location.z=1.44+(ob.location.z-1.47)*.92
  for v in ob.data.vertices:v.co*=.9
# Crown covers the scalp; separate locks grow from overlapping roots.
def crown(t,q):
 a=2*math.pi*q;back=max(0,math.sin(a));front=max(0,-math.sin(a));theta=.002+t*(1.40-.12*math.sqrt(front)-.002)
 x=.48*sp(math.sin(theta)*math.cos(a),.82)
 y=.025+.325*sp(math.sin(theta)*math.sin(a),.52)
 z=1.46+.41*sp(math.cos(theta),.82)
 return x,y,z
surface('Hair_Crown_SoftAsymmetric',crown,40,96,.012)
# Nine independent curved back locks: shared roots, separated flowing ends.
angles=[.10,.45,.80,1.15,1.50,1.85,2.20,2.55,2.95]
ends=[.81,.77,.84,.79,.83,.765,.82,.78,.85]
for idx,(angle,end) in enumerate(zip(angles,ends)):
 vs=[];fs=[];N=36;K=16
 for i in range(N+1):
  t=i/N;z=1.71+(end-1.71)*t
  base=math.sqrt(max(.1,1-abs((max(z,1.30)-1.46)/.41)**(2/.82)))
  grow=ss(min(1,t/.18));flare=ss(max(0,(t-.40)/.60))
  rx=.48*base**.82-.025*(1-grow)+.012*grow+.025*flare
  ry=.325*base**.52-.025*(1-grow)+.012*grow+.14*flare-.035*ss(max(0,(t-.85)/.15))
  # Ends curl, instead of forming a straight cut curtain.
  a=angle+.045*math.sin(t*math.pi)*(1 if idx%2 else -1)+(.14 if idx%2 else -.10)*t**4
  width=.23*(.86+.14*math.sin(math.pi*t))
  if t>.72:width*=max(.015,(1-ss((t-.72)/.28)))
  thickness=.019*(.5+.5*math.sin(math.pi*t))*(1-.92*t**5)
  for j in range(K):
   beta=j/K*2*math.pi;aa=a+width*math.sin(beta)
   d=thickness*math.cos(beta)+(.005 if idx==1 else 0)
   # A broad convex section provides volume without inflated tube-like locks.
   blend=ss(min(1,t/.65))
   xx=sp(math.cos(aa),.82)*(1-blend)+math.cos(aa)*blend
   yy=sp(math.sin(aa),.52)*(1-blend)+math.sin(aa)*blend
   vs.append(((rx+d)*xx,.025+(ry+d)*yy,z+.008*math.sin(beta)*t*t))
 for i in range(N):
  for j in range(K):a=i*K+j;b=i*K+(j+1)%K;fs.append((a,b,b+K,a+K))
 fs.extend([tuple(range(K-1,-1,-1)),tuple(N*K+j for j in range(K))])
 mesh('Hair_Back_Lock_%02d'%(idx+1),vs,fs,1)
# Irregular swept fringe, with slanted cuts and unequal lengths.
# Each panel's width grows from a hidden root, rather than a tiled rectangular strip.
for idx,(root,lo,hi,ze,lean) in enumerate([
 (-.13,-.365,-.217,1.565,-.014),(-.055,-.229,-.098,1.555,.008),
 (.035,-.111,.034,1.56,-.011),(.095,.024,.112,1.58,.024)]):
 def bang(t,q,root=root,lo=lo,hi=hi,ze=ze,lean=lean,idx=idx):
  e=ss(t);x=(root+(q-.5)*.09)*(1-e)+(lo+(hi-lo)*q)*e
  x+=lean*math.sin(math.pi*t)
  z=1.849+(ze-1.849)*t+.015*(q-.5)*t**6
  norm=abs(x/.48)**(2/.82)+abs((z-1.46)/.41)**(2/.82)
  y=.025-.325*max(.012,1-norm)**.26-.010-.006*math.sin(math.pi*q)*e-.004*idx
  return x,y,z
 surface('Hair_Fringe_Swept_%02d'%(idx+1),bang,30,12,.007)
# Long cheek-framing locks with organic curvature and a tapered curl.
for sign,label in [(-1,'L'),(1,'R')]:
 def lock(t,q,sign=sign):
  z=1.83-.86*t
  center=.19+.225*math.sin(t*math.pi*.72)-.07*t**5
  width=(.022+.095*math.sin(min(1,t/.5)*math.pi/2))*(1-.98*t**5)
  x=sign*(center+(q-.5)*width)
  norm=abs(x/.48)**(2/.82)+abs((z-1.46)/.41)**(2/.82)
  rooty=.025-.325*max(.012,1-norm)**.26-.010
  target=-.20-.12*math.sin(t*math.pi*.75)-.018*math.sin(q*math.pi)
  blend=ss(min(1,t/.36));y=rooty*(1-blend)+target*blend
  if sign<0:y-=.009*(1-t)
  return x,y,z
 surface('Hair_FaceFraming_'+label,lock,44,16,.006)
# Gentle variation between hair masses, all within the same sage palette.
for idx,ob in enumerate(HC.objects):
 if ob.name.startswith('Hair_Back_Lock'):
  mat=hair.copy();mat.name=ob.name+'_Sage';p=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
  rgb=(.62+idx%3*.009,.70+idx%3*.009,.57+idx%3*.009)
  p.inputs['Base Color'].default_value=(*rgb,1);mat.diffuse_color=(*rgb,1)
  ob.data.materials[0]=mat
for ob in C.all_objects:
 if ob.type=='MESH':
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
for area in [a for screen in bpy.data.screens for a in screen.areas if a.type=='VIEW_3D']:
 area.spaces.active.shading.type='MATERIAL';area.spaces.active.region_3d.view_location=(0,0,.96);area.spaces.active.region_3d.view_distance=3.0
s['revision']='V3: smaller squared-round face; independently editable swept fringe and nine flowing rear locks.'
s['inferred_design']='Back view arrangement of locks is inferred from front and side artwork.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'chibi_character_v3.blend'))
if '--build-only' in sys.argv:sys.exit(0)
for view in ['front','side','back','three_quarter']:
 bpy.data.objects['Studio_Ground'].hide_render=view!='three_quarter';s.camera=bpy.data.objects['Camera_'+view];s.render.filepath=str(R/(view+'.png'));bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['Camera_three_quarter'];bpy.data.objects['Studio_Ground'].hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=str(R/'chibi_character_v3.blend'))
