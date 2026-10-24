import bpy,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).parent;s=bpy.data.scenes['Chibi_Reference_Character'];bpy.context.window.scene=s;C=bpy.data.collections['Character_Editable'];T=bpy.data.collections['Presentation']
src=(R/'build.py').read_text();exec(src[src.index('def mat'):src.index('# Face is')])
def fy(x,z,offset=.004):return -.345*math.sqrt(max(.03,1-(x/.49)**2-((z-1.49)/.435)**2))-offset
# Conforming face patches: rounded rectangles with small matte highlights.
def patch(n,cx,cz,wx,hz,m,off=.005):
 pts=[]
 for i in range(64):
  a=2*math.pi*i/64;x=cx+wx*math.copysign(abs(math.cos(a))**.55,math.cos(a));z=cz+hz*math.copysign(abs(math.sin(a))**.55,math.sin(a));pts.append((x,fy(x,z,off),z))
 v=[(cx,fy(cx,cz,off),cz)]+pts;ob=mesh(n,v,[(0,i+1,(i+1)%64+1) for i in range(64)],m);return pts
for sign,label in [(-1,'L'),(1,'R')]:
 x=sign*.185
 pts=patch('Eye_Outline_'+label,x,1.435,.061,.090,dark,.005)
 patch('Eye_Ivory_'+label,x,1.432,.051,.079,white,.007)
 patch('Eye_Iris_'+label,x,1.448,.036,.064,iris,.009)
 patch('Eye_Pupil_'+label,x,1.451,.012,.042,dark,.010)
 patch('Eye_Glint_'+label,x-.013,1.476,.014,.021,glint,.012)
 pts=[(xx,fy(xx,1.510,.016),1.510) for xx in [x-.075+i*.15/20 for i in range(21)]];line('UpperLid_'+label,pts,dark,.009)
 pts=[(xx,fy(xx,1.558,.007),1.558+.005*math.sin(i/20*math.pi)) for i,xx in enumerate([x-.06+i*.12/20 for i in range(21)])];line('Brow_'+label,pts,dark,.004)
line('Mouth',[(x,fy(x,1.277,.007),1.277) for x in [-.012,0,.012]],dark,.003)
# Broad, blunt fringe panels, ending above the eyes.
for i,(x,tip) in enumerate([(-.31,1.62),(-.205,1.62),(-.095,1.61),(.018,1.61),(.125,1.615),(.235,1.60)]):
 v=[];f=[];K=12;N=16
 for j in range(N+1):
  t=j/N;z=1.90+(tip-1.90)*t;xx=x*(.70+.30*t);yy=-.11-.24*math.sin(t*math.pi/2);w=.063*(.75+.25*t);depth=.027
  for k in range(K):
   a=2*math.pi*k/K;v.append((xx+w*math.cos(a),yy+depth*math.sin(a),z+.008*math.cos(a)*t))
 for j in range(N):
  for k in range(K):
   a=j*K+k;b=j*K+(k+1)%K;f.append((a,b,b+K,a+K))
 f.extend([tuple(reversed(range(K))),tuple(N*K+k for k in range(K))]);mesh('Hair_BluntFringe_%02d'%i,v,f,hair)
# Collar: scalloped bib surface, split into two white leaves.
for sign,label in [(-1,'L'),(1,'R')]:
 v=[];f=[]
 for j in range(9):
  t=j/8
  for k in range(25):
   a=-math.pi/2+k*math.pi/24
   x=sign*(.035+t*(.15+.008*math.cos(8*a))*math.cos(a));z=.995+t*.075*math.sin(a)-.045*t;y=-.105-.080*t
   v.append((x,y,z))
 for j in range(8):
  for k in range(24):
   a=j*25+k;f.append((a,a+1,a+26,a+25))
 o=mesh('Collar_Scalloped_'+label,v,f,white);m=o.modifiers.new('Cloth thickness','SOLIDIFY');m.thickness=.008
uv('Placket',(0,-.151,.91),(.055,.018,.09),white)
line('Placket_Seam',[(0,-.172,.84),(0,-.173,.96)],dark,.003)
for z in [.87,.90,.93]:uv('Placket_Button',(0,-.176,z),(.008,.006,.008),shoe)
for sign in [-1,1]:
 o=uv('Ribbon_Loop_'+str(sign),(sign*.047,-.194,.976),(.046,.020,.025),navy);o.rotation_euler[1]=sign*.28
 line('Ribbon_Tail_'+str(sign),[(sign*.015,-.198,.964),(sign*.03,-.195,.92)],dark,.008)
uv('Ribbon_Knot',(0,-.211,.976),(.016,.014,.016),dark)
line('Choker',[(.099*math.cos(2*math.pi*i/64),.091*math.sin(2*math.pi*i/64),1.074) for i in range(64)],dark,.011,True)
for sign in [-1,1]:
 for z in [.093,.128]:line('Sock_CuffStripe',[(sign*.145+.075*math.cos(2*math.pi*i/48),-.008+.079*math.sin(2*math.pi*i/48),z) for i in range(48)],dark,.003,True)
 line('Shoe_Strap',[(sign*.145-.055+i*.11/24,-.083,.080+.016*math.sin(i/24*math.pi)) for i in range(25)],white,.008)
# Shared spatial scale across dress and sleeves. Two narrow stripes per repeat.
n=navy.node_tree.nodes;l=navy.node_tree.links;p=n.get('Principled BSDF');coord=n.new('ShaderNodeTexCoord');empty=bpy.data.objects.new('Plaid_CoordinateOrigin',None);C.objects.link(empty);coord.object=empty
sep=n.new('ShaderNodeSeparateXYZ');l.new(coord.outputs['Object'],sep.inputs[0]);masks=[]
for axis in ['X','Y','Z']:
 mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=10;l.new(sep.outputs[axis],mul.inputs[0]);fract=n.new('ShaderNodeMath');fract.operation='FRACT';l.new(mul.outputs[0],fract.inputs[0]);less=n.new('ShaderNodeMath');less.operation='LESS_THAN';less.inputs[1].default_value=.045;l.new(fract.outputs[0],less.inputs[0]);masks.append(less)
add=n.new('ShaderNodeMath');add.operation='MAXIMUM';l.new(masks[0].outputs[0],add.inputs[0]);l.new(masks[1].outputs[0],add.inputs[1]);add2=n.new('ShaderNodeMath');add2.operation='MAXIMUM';l.new(add.outputs[0],add2.inputs[0]);l.new(masks[2].outputs[0],add2.inputs[1]);mix=n.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(.055,.065,.105,1);mix.inputs[2].default_value=(.29,.31,.34,1);l.new(add2.outputs[0],mix.inputs[0]);l.new(mix.outputs[0],p.inputs['Base Color'])
# Ground and final cameras.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.002));link(bpy.context.object,'Studio_Ground',mat('Ground',(.68,.72,.73)),T)
s['inferred_design']='Rear collar and belt closure, rear skirt plaid and seven broad rear hair locks inferred from front and side; no rig supplied.'
s['proportions']='Approximate 2-head chibi; height 1.98 units. Scale is illustrative, not measured.'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'chibi_character_editable.blend'))
for name in ['front','side','back','three_quarter']:
 s.camera=bpy.data.objects['Camera_'+name];s.render.filepath=str(R/(name+'.png'));bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['Camera_three_quarter'];bpy.ops.wm.save_as_mainfile(filepath=str(R/'chibi_character_editable.blend'))