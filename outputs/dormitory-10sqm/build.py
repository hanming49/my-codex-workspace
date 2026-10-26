import bpy,math,json,sys
from mathutils import Vector
from pathlib import Path
R=Path(__file__).parent
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.name='Dormitory_10sqm';s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
root=bpy.data.collections.new('Dormitory_Editable');s.collection.children.link(root)
def col(n):
 c=bpy.data.collections.new(n);root.children.link(c);return c
arch=col('01_Architecture');furn=col('02_Furniture');doorcol=col('03_Door_Operable');decor=col('04_Details');pres=col('05_Presentation')
def mat(n,c,rough=.6,metal=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
wall=mat('M_WarmWhite',(.84,.83,.78));oak=mat('M_Oak',(.57,.36,.19));floor=mat('M_Floor',(.65,.59,.47));white=mat('M_Ivory',(.92,.91,.86));navy=mat('M_Teal',(.09,.32,.36));rust=mat('M_Terracotta',(.55,.26,.15));dark=mat('M_DarkMetal',(.08,.095,.10),.3,.6);glass=mat('M_Window_PaleBlue',(.46,.72,.83),.2);paper=mat('M_Paper',(.96,.94,.85))
def box(n,loc,size,m,c=furn,bev=.01):
 x,y,z=[v/2 for v in size];vs=[(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)];fs=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],[tuple(reversed(f)) for f in fs]);me.update();o=bpy.data.objects.new(n,me);c.objects.link(o);o.location=loc;me.materials.append(m)
 if bev:
  b=o.modifiers.new('Edge_softening','BEVEL');b.width=min(bev,min(size)/4);b.segments=3
  w=o.modifiers.new('Weighted_normals','WEIGHTED_NORMAL')
 return o
floorob=box('Floor_4x2_5',(2,1.25,-.09),(4.24,2.74,.18),floor,arch,.005)
west=[];south=[]
south.append(box('Wall_South',(2,-.06,1.4),(4,.12,2.8),wall,arch,.002))
box('Wall_North',(2,2.56,1.4),(4,.12,2.8),wall,arch,.002)
west.append(box('Wall_West_South',(-.06,.375,1.4),(.12,.75,2.8),wall,arch,.002))
west.append(box('Wall_West_North',(-.06,2.125,1.4),(.12,.75,2.8),wall,arch,.002))
west.append(box('Wall_West_OverDoor',(-.06,1.25,2.475),(.12,1.0,.65),wall,arch,.002))
# East window: 1.20 m overall frame width, sill 1.10 m, head 2.30 m.
box('Wall_East_Lower',(4.06,1.25,.55),(.12,2.5,1.1),wall,arch,.002)
box('Wall_East_Upper',(4.06,1.25,2.55),(.12,2.5,.5),wall,arch,.002)
for y in [.325,2.175]:box('Wall_East_Pier_'+str(y),(4.06,y,1.7),(.12,.65,1.2),wall,arch,.002)
for y in [.675,1.825]:box('Window_Frame_V_'+str(y),(4.025,y,1.7),(.06,.05,1.2),white,arch,.003)
for z in [1.125,2.275]:box('Window_Frame_H_'+str(z),(4.025,1.25,z),(.06,1.1,.05),white,arch,.003)
box('Window_Mullion',(4.025,1.25,1.7),(.06,.035,1.1),white,arch,.003)
box('Window_Glass',(4.055,1.25,1.7),(.008,1.10,1.10),glass,arch,.001)
box('Window_Sill',(3.94,1.25,1.085),(.12,1.25,.03),white,arch,.004)
ceiling=box('Ceiling_Hidden_For_Inspection',(2,1.25,2.86),(4,.0+2.5,.12),wall,arch,.001);ceiling.hide_render=True;ceiling.hide_set(True)
# Door leaf is 0.90 wide. Extra frame allowance ensures >0.90 clear at 90 degrees.
for y in [.7625,1.7375]:box('Door_Jamb_'+str(y),(-.04,y,1.0625),(.12,.025,2.125),oak,doorcol,.003)
box('Door_Header',(-.04,1.25,2.1375),(.12,1.0,.025),oak,doorcol,.003)
hinge=bpy.data.objects.new('Door_Hinge_Rotate_Z_0_to_minus90',None);doorcol.objects.link(hinge);hinge.location=(0,.8,.02)
hinge['closed_angle_deg']=0.;hinge['open_angle_deg']=-90.;hinge['leaf_width_m']=.9
leaf=box('Door_Leaf_0_90m',(0,0,0),(.036,.9,2.1),oak,doorcol,.005);leaf.parent=hinge;leaf.location=(0,.45,1.05)
for side in [-1,1]:
 handle=box('Door_Handle_'+str(side),(0,0,0),(.07,.12,.025),dark,doorcol,.006);handle.parent=hinge;handle.location=(side*.042,.78,1.0)
hinge.rotation_euler.z=-math.pi/2
# Bounding-box ledger, in interior coordinates (x=0..4, y=0..2.5).
ledger=[]
def record(n,rect,h,kind):ledger.append(dict(name=n,bounds_xy=rect,height_m=h,kind=kind))
for i,y in enumerate([.5,2.0],1):
 tag='Bed_%d'%i;blanket=navy if i==1 else rust
 record(tag,[1.95,y-.45,3.95,y+.45],.85,'bed')
 box(tag+'_Frame',(2.925,y,.27),(1.95,.9,.18),oak)
 for x in [2.03,3.87]:
  for yy in [y-.37,y+.37]:box(tag+'_Leg',(x,yy,.09),(.07,.07,.18),oak,bev=.006)
 box(tag+'_Mattress',(2.925,y,.44),(1.95,.86,.16),white,bev=.035)
 box(tag+'_Headboard',(3.925,y,.535),(.05,.9,.63),oak)
 box(tag+'_Duvet',(2.72,y,.545),(1.48,.84,.05),blanket,bev=.02)
 box(tag+'_Fold',(2.10,y,.58),(.22,.85,.035),white,bev=.012)
 box(tag+'_Pillow',(3.59,y,.565),(.36,.62,.10),white,bev=.045)
for i,sign in [(1,1),(2,-1)]:
 y=.3 if sign==1 else 2.2
 record('Desk_%d'%i,[.95,y-.25,1.85,y+.25],.75,'desk')
 box('Desk_%d_Top'%i,(1.4,y,.725),(.9,.5,.05),oak)
 for x in [1.0,1.80]:
  for yy in [y-.20,y+.20]:box('Desk_%d_Leg'%i,(x,yy,.35),(.035,.035,.70),dark,bev=.004)
 box('Desk_%d_Drawer'%i,(1.65,y,.64),(.29,.42,.12),white)
 # Stools fit beneath the desk edge; no chair back intrudes into the main aisle.
 cy=.68 if sign==1 else 1.82
 record('Seat_%d'%i,[1.20,cy-.20,1.60,cy+.20],.46,'seat')
 box('Seat_%d_Cushion'%i,(1.4,cy,.435),(.4,.4,.05),navy if i==1 else rust,bev=.018)
 for x in [1.25,1.55]:
  for yy in [cy-.15,cy+.15]:box('Seat_%d_Leg'%i,(x,yy,.205),(.03,.03,.41),oak,bev=.004)
 for k in range(3):box('Book_%d_%d'%(i,k),(1.10+.025*k,y-sign*.06,.778+k*.022),(.23,.16,.02),[navy,paper,rust][k],decor,.003)
 box('Desk_%d_WritingPad'%i,(1.48,y,.754),(.27,.24,.006),paper,decor,.001)
 wy=.35 if sign==1 else 2.15
 record('Wardrobe_%d'%i,[.05,wy-.30,.70,wy+.30],2.10,'wardrobe')
 box('Wardrobe_%d_Case'%i,(.375,wy-sign*.025,1.05),(.65,.55,2.10),white)
 # Sliding fronts face the room centre, not the narrow gap beside the desks.
 fy=wy+sign*.265
 for k in range(2):
  box('Wardrobe_%d_SlidingPanel_%d'%(i,k),(.215+.32*k,fy,1.07),(.31,.028,2.02),oak if k==0 else white,bev=.004)
  box('Wardrobe_%d_Handle_%d'%(i,k),(.33+.1*k,fy+sign*.02,1.10),(.018,.018,.19),dark,bev=.004)
# Lighting and cameras.
s.world=bpy.data.worlds.new('Studio_World');s.world.color=(.35,.35,.35);s.world.use_nodes=True
next(n for n in s.world.node_tree.nodes if n.type=='BACKGROUND').inputs[0].default_value=(.70,.79,.86,1)
next(n for n in s.world.node_tree.nodes if n.type=='BACKGROUND').inputs[1].default_value=.65
for name,loc,power,size in [('Key', (1,-1,5),450,4),('WindowFill',(3,2,3.5),280,3),('EntryFill',(-1,2,3),200,3)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);pres.objects.link(o);o.location=loc;o.rotation_euler=(Vector((2,1.25,.5))-o.location).to_track_quat('-Z','Y').to_euler()
def cam(n,loc,target,ortho=None):
 d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);pres.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=42
 if ortho:d.type='ORTHO';d.ortho_scale=ortho
 return o
cams=[cam('Camera_Top',(2,1.25,8),(2,1.25,0),4.9),cam('Camera_Perspective_A',(-3.4,-4.7,5.3),(2,1.25,.9)),cam('Camera_Perspective_B',(1.6,-5.6,4.1),(2,1.3,.95))]
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=1050;s.render.resolution_percentage=100
s.view_settings.view_transform='AgX';s.render.image_settings.file_format='PNG'
s['interior_dimensions_m']='4.0 x 2.5 x 2.8';s['clear_aisle_m']=.6;s['cutaway_note']='South and west walls hidden only in presentation. Ceiling retained as hidden object.'
(R/'layout.json').write_text(json.dumps({'room':[4,2.5,2.8],'door_leaf_width':.9,'window_width':1.2,'aisle':[.0,.95,3.95,1.55],'door_sweep_conservative_aabb':[0,.72,.91,1.71],'furniture':ledger},indent=2))
# Dimension measurements taken from evaluated scene geometry, not only input constants.
bpy.context.view_layer.update();bounds={}
for item in ledger:
 prefix=item['name']+'_';obs=[o for o in furn.objects if o.name.startswith(prefix)]
 pts=[o.matrix_world@Vector(p) for o in obs for p in o.bound_box]
 bounds[item['name']]=[min(p.x for p in pts),min(p.y for p in pts),max(p.x for p in pts),max(p.y for p in pts)]
(R/'measured_bounds.json').write_text(json.dumps(bounds,indent=2))
# Save complete geometry; presentation cutaway uses visibility only.
for o in south+west:o.hide_render=True;o.hide_set(True)
s.camera=cams[1]
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':a.spaces.active.region_3d.view_location=(2,1.25,1);a.spaces.active.region_3d.view_distance=7;a.spaces.active.region_3d.view_rotation=cams[1].rotation_euler.to_quaternion();a.spaces.active.shading.type='MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'dormitory_10sqm.blend'))
if '--build-only' not in sys.argv:
 for camera,name in zip(cams,['top_view','perspective_a','perspective_b']):
  s.camera=camera
  for o in arch.objects:
   if o.name.startswith('Wall_'):o.hide_render=(camera==cams[0] or o in south+west)
  s.render.filepath=str(R/(name+'.png'));bpy.ops.render.render(write_still=True)
 for o in arch.objects:
  if o.name.startswith('Wall_'):o.hide_render=o in south+west
 s.camera=cams[1];bpy.ops.wm.save_as_mainfile(filepath=str(R/'dormitory_10sqm.blend'))
