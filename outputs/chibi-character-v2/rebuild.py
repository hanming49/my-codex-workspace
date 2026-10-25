import bpy,math,bmesh
from mathutils import Vector
from pathlib import Path
R=Path(__file__).parent;s=bpy.data.scenes['Chibi_Reference_Character'];bpy.context.window.scene=s;C=bpy.data.collections['Character_Editable'];HC=bpy.data.collections['02_Hair'];FC=bpy.data.collections['01_Head_Face'];OC=bpy.data.collections['03_Outfit']
hair=bpy.data.materials['Hair_SageGrey'];skin=bpy.data.materials['Skin_WarmCream'];white=bpy.data.materials['Ivory_CollarAndSocks'];ink=bpy.data.materials['Ink_SoftCharcoal']
for o in list(HC.objects):bpy.data.objects.remove(o,do_unlink=True)
def mesh(n,v,f,mat,col=HC,thick=0):
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);col.objects.link(o);me.materials.append(mat)
 for p in me.polygons:p.use_smooth=True
 if thick:
  m=o.modifiers.new('Editable thickness','SOLIDIFY');m.thickness=thick;m.offset=-1
 return o
def grid(n,fn,nu,nv,mat=hair,col=HC,thick=.012):
 vs=[fn(i/nu,j/nv) for i in range(nu+1) for j in range(nv+1)];fs=[]
 for i in range(nu):
  for j in range(nv):
   a=i*(nv+1)+j;fs.append((a,a+1,a+nv+2,a+nv+1))
 return mesh(n,vs,fs,mat,col,thick)
# Flatten the front plane and broaden the cheek silhouette.
head=bpy.data.objects['Head_Editable']
for v in head.data.vertices:
 x,y,z=v.co;v.co.x=x*1.05;v.co.y=math.copysign((abs(y)/.345)**.52*.29,y);v.co.z=math.copysign((abs(z)/.435)**.80*.40,z)
head.location.z=1.47

def fy(x,z,off):
 zz=math.copysign(abs((z-1.47)/.40)**1.25,z-1.47)
 return -.29*max(.015,1-(x/.5145)**2-zz*zz)**.26-off
for o in FC.objects:
 if o.name.startswith('Eye_') and o.type=='MESH':
  off=next(v for k,v in {'Outline':.004,'Ivory':.006,'Iris':.008,'Pupil':.010,'Glint':.012}.items() if k in o.name)
  for v in o.data.vertices:
   # Move eyes a little lower and apart, keeping the relaxed upper eyelid.
   v.co.x*=1.12;v.co.z-=.018;v.co.y=fy(v.co.x,v.co.z,off)
 if o.type=='CURVE' and o.name.startswith(('UpperLid','Brow','Mouth')):
  for sp in o.data.splines:
   for p in sp.points:
    p.co.x*=1.12
    if not o.name.startswith('Mouth'):p.co.z-=.018
    p.co.y=fy(p.co.x,p.co.z,.012)
for o in FC.objects:
 if o.name.startswith('Ear_'):o.location.x*=1.04;o.location.y=-.01
# Crown: broad smooth dome, ending behind the fringe at the front.
def crown(t,q):
 a=q*2*math.pi;front=max(0,-math.sin(a));limit=math.pi/2-.23*math.sqrt(front);theta=.008+t*(limit-.008)
 return (.54*math.sin(theta)*math.cos(a),.025+.37*math.sin(theta)*math.sin(a),1.51+.465*math.cos(theta))
cap=grid('Hair_ContinuousCrown',crown,40,96,thick=0)
# Continuous back curtain. Only the lower edge is cut into large groups.
def curtain(t,q):
 a=q*math.pi
 rx=.54+.025*math.sin(math.pi*t/2)**2;ry=.37+.025*math.sin(math.pi*t/2)**2
 z=1.51-t*.69
 if t>.75:z-=.085*((t-.75)/.25)**2*(.5+.5*math.cos(q*math.pi*12))
 x=rx*math.cos(a)
 y=.025+ry*math.sin(a)
 return (x,y,z)
back=grid('Hair_Back_ContinuousWithSplitHem',curtain,40,48,thick=0)
bm=bmesh.new();bm.from_mesh(cap.data);bm.from_mesh(back.data)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cap.data);bm.free()
bpy.data.objects.remove(back,do_unlink=True)
cap.name='Hair_CrownAndBack_Continuous'
m=cap.modifiers.new('Editable hair thickness','SOLIDIFY');m.thickness=.018;m.offset=-1
# Five broad flush fringe panels; roots follow the crown instead of sitting on top of it.
for idx,(lo,hi,end) in enumerate([(-.37,-.242,1.60),(-.240,-.117,1.61),(-.115,.023,1.595),(.025,.162,1.60),(.164,.315,1.57)]):
 def bang(t,q,lo=lo,hi=hi,end=end):
  x=(lo+(hi-lo)*q)*(.55+.45*t);z=1.93+(end-1.93)*t
  z+=.009*math.sin(q*math.pi)*t**8
  y=.025-.37*math.sqrt(max(.015,1-(x/.54)**2-((z-1.51)/.465)**2))-.004-.003*t*t
  return (x,y,z)
 grid('Hair_Fringe_%02d'%idx,bang,32,12,thick=.010)
# Slim side locks hug the temples; taper only below the cheek.
for sign,label in [(-1,'L'),(1,'R')]:
 def sidelock(t,q,sign=sign):
  z=1.91-t*.83
  center=.22+.24*math.sin(t*math.pi*.8)+.015*t
  width=.105*(1-.90*t**3)*(.12+.88*min(1,t/.23))
  x=sign*(center+(q-.5)*width)
  y=-.13-.18*math.sin(t*math.pi*.65)-.023*math.sin(q*math.pi)
  blend=min(1,t/.3)
  surface=.025-.37*math.sqrt(max(.015,1-(x/.54)**2-((z-1.51)/.465)**2))-.007
  y=surface*(1-blend)+y*blend
  if t>.80:x-=sign*.020*((t-.8)/.2)**2
  return (x,y,z)
 o=grid('Hair_ThinTempleLock_'+label,sidelock,44,14,thick=.004)
# White collar spreads over the shoulders; remove the previous flower-like bib.
for o in list(OC.objects):
 if o.name.startswith('Collar_'):bpy.data.objects.remove(o,do_unlink=True)
for sign,label in [(-1,'L'),(1,'R')]:
 def collar(t,q,sign=sign):
  x=sign*(.015+.19*q)
  y=(-.09-.055*q)*(1-t)+(-.185+.020*q)*t
  z=(1.04-.020*q)*(1-t)+(.93+.055*q)*t+.006*math.sin(q*math.pi*6)*t**5
  return (x,y,z)
 grid('Collar_ShoulderLeaf_'+label,collar,12,30,white,OC,.006)
# Slightly broaden the lower dress, preserving the short silhouette.
for o in OC.objects:
 if o.name.startswith('Skirt_'):
  for v in o.data.vertices:v.co.x*=1.06
for node in bpy.data.materials['Dress_NavyPlaid'].node_tree.nodes:
 if node.type=='MATH' and node.operation=='MULTIPLY':node.inputs[1].default_value=13.3
 if node.type=='MATH' and node.operation=='LESS_THAN':node.inputs[1].default_value=.027
# Softer colours and restrained shadow contrast.
for name,rgb in [('Skin_WarmCream',(.97,.84,.71)),('Hair_SageGrey',(.66,.73,.60))]:
 m=bpy.data.materials[name];m.diffuse_color=(*rgb,1);m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*rgb,1)
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(*rgb,1);p.inputs['Emission Strength'].default_value=.12
# Consistent outward normals, weld poles before checking.
for o in C.all_objects:
 if o.type=='MESH':
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
# A useful default view: character framed, no giant ground selection.
for o in bpy.context.selected_objects:o.select_set(False)
head.select_set(True);bpy.context.view_layer.objects.active=head
bpy.data.objects['Studio_Ground'].hide_set(True)
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':
   a.spaces.active.region_3d.view_location=(0,0,1);a.spaces.active.region_3d.view_distance=3.2;a.spaces.active.region_3d.view_rotation=bpy.data.objects['Camera_front'].rotation_euler.to_quaternion();a.spaces.active.overlay.show_extras=False;a.spaces.active.shading.type='MATERIAL'
s['revision']='V2: continuous hair crown and curtain, flush fringe, flattened broad face, shoulder collar.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'chibi_character_v2.blend'))
for view in ['front','side','back','three_quarter']:
 bpy.data.objects['Studio_Ground'].hide_render=view!='three_quarter';s.camera=bpy.data.objects['Camera_'+view];s.render.filepath=str(R/(view+'.png'));bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['Camera_three_quarter'];bpy.data.objects['Studio_Ground'].hide_render=False;bpy.ops.wm.save_as_mainfile(filepath=str(R/'chibi_character_v2.blend'))
